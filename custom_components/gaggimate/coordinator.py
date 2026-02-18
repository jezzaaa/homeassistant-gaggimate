"""DataUpdateCoordinator for GaggiMate."""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    WS_PATH,
    WS_TIMEOUT,
    RECONNECT_INTERVAL,
    OTA_REFRESH_INTERVAL,
    WS_REQ_OTA_SETTINGS,
    WS_RES_OTA_SETTINGS,
    WS_EVT_STATUS,
    WS_RES_PROFILES_LIST,
    API_SCALES_SCAN,
)

_LOGGER = logging.getLogger(__name__)


class GaggiMateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching GaggiMate data via WebSocket."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize."""
        self.host = host
        self.ws_url = f"ws://{host}{WS_PATH}"
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._session: aiohttp.ClientSession | None = None
        self._reconnect_task: asyncio.Task | None = None
        self._ota_refresh_task: asyncio.Task | None = None
        self._profiles: list[dict[str, Any]] = []
        self._ota_data: dict[str, Any] = {}
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None,  # We use WebSocket push updates
        )

    @property
    def profiles(self) -> list[dict[str, Any]]:
        """Return cached profiles list."""
        return self._profiles

    @property
    def ota_data(self) -> dict[str, Any]:
        """Return OTA settings data."""
        return self._ota_data

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from WebSocket."""
        if self._ws is None or self._ws.closed:
            await self._connect_websocket()
        
        # Merge status data with OTA data
        merged_data = {**(self.data or {}), **self._ota_data}
        return merged_data

    async def _connect_websocket(self) -> None:
        """Connect to the WebSocket."""
        if self._session is None:
            self._session = async_get_clientsession(self.hass)
        
        try:
            _LOGGER.debug("Connecting to WebSocket at %s", self.ws_url)
            self._ws = await self._session.ws_connect(
                self.ws_url,
                timeout=WS_TIMEOUT,
                heartbeat=30,
            )
            
            # Start listening for messages
            self.hass.async_create_task(self._listen_websocket())
            
            # Request initial OTA settings
            await self._request_ota_settings()
            
            # Start periodic OTA refresh
            self._start_ota_refresh()
            
            _LOGGER.info("Connected to GaggiMate WebSocket at %s", self.host)
        except Exception as err:
            _LOGGER.error("Error connecting to WebSocket: %s", err)
            raise UpdateFailed(f"Error connecting to WebSocket: {err}") from err

    async def _listen_websocket(self) -> None:
        """Listen for WebSocket messages."""
        if self._ws is None:
            return
        
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = msg.json()
                        msg_type = data.get("tp")
                        _LOGGER.debug("Received WebSocket message type %s: %s", msg_type, data)
                        
                        if msg_type == WS_EVT_STATUS:
                            # Status update - merge with existing data
                            current_data = self.data or {}
                            updated_data = {**current_data, **data}
                            self.async_set_updated_data(updated_data)
                        
                        elif msg_type == WS_RES_OTA_SETTINGS:
                            # OTA settings response
                            self._ota_data = data
                            # Merge with current data
                            current_data = self.data or {}
                            updated_data = {**current_data, **data}
                            self.async_set_updated_data(updated_data)
                        
                        elif msg_type == WS_RES_PROFILES_LIST:
                            # Profiles list response
                            self._profiles = data.get("profiles", [])
                            _LOGGER.info("Updated profiles list: %d profiles available", len(self._profiles))
                            _LOGGER.debug("Profile details: %s", self._profiles)
                        
                    except Exception as err:
                        _LOGGER.error("Error parsing WebSocket message: %s", err)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    _LOGGER.error("WebSocket error: %s", self._ws.exception())
                    break
        except Exception as err:
            _LOGGER.error("WebSocket connection lost: %s", err)
        finally:
            # Stop OTA refresh task
            if self._ota_refresh_task is not None:
                self._ota_refresh_task.cancel()
            
            # Schedule reconnection
            if not self._ws.closed:
                await self._ws.close()
            self._schedule_reconnect()

    def _schedule_reconnect(self) -> None:
        """Schedule a reconnection attempt."""
        if self._reconnect_task is not None and not self._reconnect_task.done():
            return
        
        async def reconnect() -> None:
            _LOGGER.info("Attempting to reconnect to GaggiMate at %s", self.host)
            await asyncio.sleep(RECONNECT_INTERVAL)
            try:
                await self._connect_websocket()
                _LOGGER.info("Successfully reconnected to GaggiMate at %s", self.host)
            except Exception as err:
                _LOGGER.error("Reconnection failed: %s", err)
                self._schedule_reconnect()
        
        self._reconnect_task = self.hass.async_create_task(reconnect())

    def _start_ota_refresh(self) -> None:
        """Start periodic OTA settings refresh."""
        if self._ota_refresh_task is not None and not self._ota_refresh_task.done():
            return
        
        async def refresh_ota() -> None:
            while True:
                await asyncio.sleep(OTA_REFRESH_INTERVAL)
                try:
                    await self._request_ota_settings()
                except Exception as err:
                    _LOGGER.error("Error refreshing OTA settings: %s", err)
        
        self._ota_refresh_task = self.hass.async_create_task(refresh_ota())

    async def _request_ota_settings(self) -> None:
        """Request OTA settings from device."""
        await self.send_command({"tp": WS_REQ_OTA_SETTINGS})

    async def send_command(self, command: dict[str, Any]) -> None:
        """Send a command to the device via WebSocket."""
        if self._ws is None or self._ws.closed:
            await self._connect_websocket()
        
        if self._ws is not None and not self._ws.closed:
            try:
                await asyncio.wait_for(
                    self._ws.send_json(command),
                    timeout=WS_TIMEOUT
                )
                _LOGGER.debug("Sent command: %s", command)
            except Exception as err:
                _LOGGER.error("Error sending command: %s", err)
                raise UpdateFailed(f"Error sending command: {err}") from err

    async def request_profiles_list(self) -> None:
        """Request profiles list from device."""
        rid = str(uuid.uuid4())
        await self.send_command({"tp": "req:profiles:list", "rid": rid})

    async def select_profile(self, profile_id: str) -> None:
        """Select a profile by ID."""
        rid = str(uuid.uuid4())
        await self.send_command({"tp": "req:profiles:select", "id": profile_id, "rid": rid})

    async def change_mode(self, mode: int) -> None:
        """Change device mode."""
        await self.send_command({"tp": "req:change-mode", "mode": mode})

    async def start_ota_update(self) -> None:
        """Start OTA update."""
        rid = str(uuid.uuid4())
        await self.send_command({"tp": "req:ota-start", "rid": rid})

    async def scan_scales(self) -> bool:
        """Trigger Bluetooth scale scan via HTTP."""
        try:
            url = f"http://{self.host}{API_SCALES_SCAN}"
            async with self._session.post(url, timeout=10) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("success", False)
                return False
        except Exception as err:
            _LOGGER.error("Error scanning scales: %s", err)
            return False

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self._reconnect_task is not None:
            self._reconnect_task.cancel()
        
        if self._ota_refresh_task is not None:
            self._ota_refresh_task.cancel()
        
        if self._ws is not None and not self._ws.closed:
            await self._ws.close()
