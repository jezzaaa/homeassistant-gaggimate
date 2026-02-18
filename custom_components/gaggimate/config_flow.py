"""Config flow for GaggiMate integration."""
from __future__ import annotations

import asyncio
import logging
import socket
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, DEFAULT_NAME, MDNS_HOSTNAME, CONF_MODEL, CONF_HW_VERSION

_LOGGER = logging.getLogger(__name__)


def parse_hardware(hardware_str: str) -> tuple[str, str]:
    """Parse hardware string to extract model and hardware version.
    
    Example: "GaggiMate Pro Rev 1.x" → ("GaggiMate Pro", "Rev 1.x")
    """
    parts = hardware_str.split(" Rev ")
    model = parts[0]
    hw_version = f"Rev {parts[1]}" if len(parts) > 1 else ""
    return model, hw_version


async def query_ota_settings(hass: HomeAssistant, host: str) -> dict[str, Any]:
    """Query OTA settings from device via WebSocket."""
    session = async_get_clientsession(hass)
    ws_url = f"ws://{host}/ws"
    
    try:
        async with session.ws_connect(ws_url, timeout=10) as ws:
            # Send OTA settings request
            await ws.send_json({"tp": "req:ota-settings"})
            
            # Wait for response
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = msg.json()
                    if data.get("tp") == "res:ota-settings":
                        return data
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
            
            raise CannotConnect("No OTA settings response received")
    except Exception as err:
        _LOGGER.error("Error querying OTA settings from %s: %s", host, err)
        raise CannotConnect from err


async def validate_connection(hass: HomeAssistant, host: str) -> dict[str, Any]:
    """Validate the connection to GaggiMate device and get device info."""
    try:
        # Query OTA settings to get device information
        ota_data = await query_ota_settings(hass, host)
        
        # Parse hardware field
        hardware = ota_data.get("hardware", DEFAULT_NAME)
        model, hw_version = parse_hardware(hardware)
        
        return {
            "title": model,
            "host": host,
            "model": model,
            "hw_version": hw_version,
            "display_version": ota_data.get("displayVersion"),
            "controller_version": ota_data.get("controllerVersion"),
        }
    except Exception as err:
        _LOGGER.error("Error connecting to GaggiMate at %s: %s", host, err)
        raise CannotConnect from err


class GaggiMateConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GaggiMate."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.discovered_host: str | None = None
        self.discovered_info: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            
            # Check if already configured
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()
            
            try:
                info = await validate_connection(self.hass, host)
                self.discovered_info = info
                return await self.async_step_confirm()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Try to discover device via mDNS
        if self.discovered_host is None:
            try:
                self.discovered_host = socket.gethostbyname(MDNS_HOSTNAME)
                _LOGGER.info("Discovered GaggiMate at %s", self.discovered_host)
            except socket.gaierror:
                _LOGGER.debug("Could not resolve %s via mDNS", MDNS_HOSTNAME)

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_HOST, 
                    default=self.discovered_host or MDNS_HOSTNAME
                ): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm setup with device information."""
        if user_input is not None:
            # Use edited model name if provided
            model = user_input.get(CONF_MODEL, self.discovered_info.get("model"))
            
            return self.async_create_entry(
                title=model,
                data={
                    CONF_HOST: self.discovered_info["host"],
                    CONF_MODEL: model,
                    CONF_HW_VERSION: self.discovered_info.get("hw_version", ""),
                },
            )

        # Show form with device information
        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_MODEL,
                    default=self.discovered_info.get("model", DEFAULT_NAME)
                ): str,
            }
        )

        return self.async_show_form(
            step_id="confirm",
            data_schema=data_schema,
            description_placeholders={
                "model": self.discovered_info.get("model", DEFAULT_NAME),
                "hw_version": self.discovered_info.get("hw_version", "Unknown"),
                "display_version": self.discovered_info.get("display_version", "Unknown"),
                "controller_version": self.discovered_info.get("controller_version", "Unknown"),
            },
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""
