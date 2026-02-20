// --- IMPORT LIT FROM HOME ASSISTANT ---
// Import Lit from the Home Assistant frontend
import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit@3.1.2/index.js?module";

// --- HELPERS ---
const getGaggiMateDevices = (hass) => {
  if (!hass) return [];
  return Object.keys(hass.states)
    .filter(id => id.startsWith("select.") && id.includes("gaggimate") && id.endsWith("_mode"))
    .map(id => ({
      slug: id.split(".")[1].replace("_mode", ""),
      name: hass.states[id].attributes.friendly_name?.replace(/\s*mode$/i, "") || id
    }));
};

// --- VISUAL EDITOR ---
class GaggiMateCardEditor extends LitElement {
  static get properties() { return { hass: {}, _config: {} }; }
  setConfig(config) { this._config = config; }

  _valueChanged(ev) {
    const target = ev.target;
    const config = { ...this._config };
    const value = target.tagName === "HA-SWITCH" ? target.checked : target.value;

    config[target.configValue] = value;

    if (target.configValue === "device_name") {
      const selected = getGaggiMateDevices(this.hass).find(d => d.slug === value);
      if (selected) config.name = selected.name;
    }

    this.dispatchEvent(new CustomEvent("config-changed", { detail: { config }, bubbles: true, composed: true }));
  }

  render() {
    if (!this.hass || !this._config) return html``;
    return html`
      <div class="card-config">
        <label class="label">Machine</label>
        <select class="std-input" .value="${this._config.device_name || ""}" .configValue="${"device_name"}" @change="${this._valueChanged}">
          <option value="" disabled>Select machine...</option>
          ${getGaggiMateDevices(this.hass).map(d => html`<option value="${d.slug}">${d.name}</option>`)}
        </select>

        <label class="label">Title</label>
        <input class="std-input" type="text" .value="${this._config.name || ""}" .configValue="${"name"}" @input="${this._valueChanged}" />

        <div class="sw-row"><span>Show Grinder</span><ha-switch .checked="${this._config.show_grinder !== false}" .configValue="${"show_grinder"}" @change="${this._valueChanged}"></ha-switch></div>
        <div class="sw-row"><span>Show Weight</span><ha-switch .checked="${this._config.show_weight !== false}" .configValue="${"show_weight"}" @change="${this._valueChanged}"></ha-switch></div>
      </div>`;
  }

  static get styles() {
    return css`
      .card-config { display: flex; flex-direction: column; gap: 12px; padding: 10px; }
      .label { font-weight: 500; font-size: 14px; color: var(--primary-text-color); }
      .std-input { width: 100%; padding: 10px; border: 1px solid var(--divider-color); border-radius: 4px; background: var(--card-background-color); color: var(--primary-text-color); }
      .sw-row { display: flex; justify-content: space-between; align-items: center; color: var(--primary-text-color); }
    `;
  }
}
customElements.define("gaggimate-card-editor", GaggiMateCardEditor);

// --- MAIN CARD ---
class GaggiMateCard extends LitElement {
  static get properties() { return { hass: {}, config: {} }; }
  static getConfigElement() { return document.createElement("gaggimate-card-editor"); }

  static getStubConfig(hass) {
    const dev = getGaggiMateDevices(hass)[0];
    return { device_name: dev?.slug || "", name: dev?.name || "GaggiMate", show_grinder: true, show_weight: true };
  }

  setConfig(config) { this.config = config; }

  _getVal(suffix, domain = "sensor") {
    if (!this.hass || !this.config) return 0;
    const stateObj = this.hass.states[`${domain}.${this.config.device_name}_${suffix}`];
    return stateObj ? parseFloat(stateObj.state) || 0 : 0;
  }

  _renderDial(label, curSuffix, tgtSuffix, max, unit, showButtons = false) {
    const cur = this._getVal(curSuffix);
    const tgt = this._getVal(tgtSuffix);
    const angle = (val) => (Math.min(val, max) / max) * 270 - 135;
    const rad = (deg) => (deg - 90) * Math.PI / 180.0;
    const pt = (deg) => ({ x: 50 + 40 * Math.cos(rad(deg)), y: 50 + 40 * Math.sin(rad(deg)) });

    const aTgt = angle(tgt);
    const start = pt(aTgt);
    const end = pt(-135);
    const path = `M ${start.x} ${start.y} A 40 40 0 ${aTgt + 135 <= 180 ? 0 : 1} 0 ${end.x} ${end.y}`;

    // Check if we're in Brew mode for temperature buttons
    const slug = this.config.device_name;
    const mode = this.hass.states[`select.${slug}_mode`]?.state || "Standby";
    const buttonsEnabled = showButtons && mode === "Brew";

    return html`
      <div class="dial">
        <div class="d-label">${label}</div>
        <div class="d-rel">
          <svg viewBox="0 0 100 100">
            <path class="track" d="M 22 78 A 40 40 0 1 1 78 78" />
            <path class="fill ${cur < tgt - 0.5 ? 'active' : ''}" d="${path}" />
            <circle class="handle" cx="50" cy="10" r="4.5" transform="rotate(${aTgt} 50 50)" />
            <circle class="dot" cx="50" cy="10" r="2.5" transform="rotate(${angle(cur)} 50 50)" />
          </svg>
          ${showButtons ? html`
            <button 
              class="temp-btn temp-minus ${!buttonsEnabled ? 'disabled' : ''}" 
              @click="${() => buttonsEnabled && this.hass.callService('gaggimate', 'lower_temperature', {device_id: slug})}"
              ?disabled="${!buttonsEnabled}">
              <ha-icon icon="mdi:minus"></ha-icon>
            </button>
            <button 
              class="temp-btn temp-plus ${!buttonsEnabled ? 'disabled' : ''}" 
              @click="${() => buttonsEnabled && this.hass.callService('gaggimate', 'raise_temperature', {device_id: slug})}"
              ?disabled="${!buttonsEnabled}">
              <ha-icon icon="mdi:plus"></ha-icon>
            </button>
          ` : ''}
          <div class="d-data">
            <div class="v-main">${cur.toFixed(label === "PRESSURE" ? 2 : 1)}</div>
            <div class="v-tgt">${tgt.toFixed(1)}${unit}</div>
          </div>
        </div>
      </div>`;
  }

  render() {
    if (!this.hass || !this.config?.device_name) return html`<ha-card style="padding:16px">Check configuration.</ha-card>`;
    const slug = this.config.device_name;
    const mode = this.hass.states[`select.${slug}_mode`]?.state || "Standby";
    const profile = this.hass.states[`select.${slug}_profile`];
    const modes = ["Standby", "Brew", "Steam", "Water", ...(this.config.show_grinder !== false ? ["Grind"] : [])];

    return html`
      <ha-card>
        <div class="card-header">${this.config.name}</div>
        ${profile ? html`<div class="pad"><ha-select label="Profile" .value="${profile.state}" @selected="${(e) => this.hass.callService('select', 'select_option', {entity_id: profile.entity_id, option: e.target.value})}">${profile.attributes.options.map(opt => html`<mwc-list-item .value="${opt}">${opt}</mwc-list-item>`)}</ha-select></div>` : ''}
        <div class="modes">${modes.map(m => html`<div class="m-btn ${mode === m ? 'active' : ''}" @click="${() => this.hass.callService('select', 'select_option', {entity_id: `select.${slug}_mode`, option: m})}">${m.toUpperCase()}</div>`)}</div>
        <div class="dials">${this._renderDial("TEMPERATURE", "current_temperature", "target_temperature", 110, "°C", true)}${this._renderDial("PRESSURE", "current_pressure", "target_pressure", 15, " Bar")}</div>
        ${this.config.show_weight !== false ? html`<div class="weight"><div class="w-sec"><div class="w-l">CURRENT</div><div>${this._getVal("current_weight").toFixed(1)}g</div></div><div class="divider"></div><div class="w-sec"><div class="w-l">TARGET</div><div>${this._getVal("target_weight").toFixed(1)}g</div></div></div>` : ''}
      </ha-card>`;
  }

  static get styles() {
    return css`
      :host { --brand: var(--accent-color, #ff9800); }
      .card-header { padding: 24px 16px 16px; font-size: var(--ha-card-header-font-size, 24px); line-height: var(--ha-card-header-line-height, 32px); color: var(--ha-card-header-color, var(--primary-text-color)); }
      .pad { padding: 0 16px 16px; }
      ha-select { width: 100%; }
      .modes { display: grid; grid-template-columns: repeat(auto-fit, minmax(65px, 1fr)); gap: 8px; padding: 0 16px 16px; }
      .m-btn { background: var(--secondary-background-color); padding: 10px; border-radius: 8px; text-align: center; cursor: pointer; font-size: 10px; font-weight: bold; color: var(--primary-text-color); }
      .m-btn.active { background: var(--brand); color: white; }
      .dials { display: flex; justify-content: space-around; padding-bottom: 16px; }
      .dial { width: 42%; text-align: center; }
      .d-label { font-size: 10px; font-weight: bold; opacity: 0.6; margin-bottom: 4px; color: var(--primary-text-color); }
      .d-rel { position: relative; }
      svg { width: 100%; overflow: visible; }
      .track { fill: none; stroke: var(--divider-color); stroke-width: 8; stroke-linecap: round; }
      .fill { fill: none; stroke: var(--disabled-text-color); stroke-width: 8; stroke-linecap: round; }
      .fill.active { stroke: var(--brand); }
      .handle { fill: var(--card-background-color); stroke: var(--divider-color); stroke-width: 1; }
      .dot { fill: var(--primary-text-color); }
      .d-data { position: absolute; top: 55%; width: 100%; transform: translateY(-50%); pointer-events: none; }
      .v-main { font-size: 22px; font-weight: bold; color: var(--primary-text-color); }
      .v-tgt { font-size: 11px; color: var(--error-color, #e91e63); font-weight: bold; }
      .temp-btn { position: absolute; width: 32px; height: 32px; border-radius: 50%; background: var(--card-background-color); border: 2px solid var(--brand); color: var(--brand); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; pointer-events: auto; }
      .temp-btn:hover:not(.disabled) { background: var(--brand); color: white; transform: scale(1.1); }
      .temp-btn.disabled { opacity: 0.3; cursor: not-allowed; border-color: var(--disabled-text-color); color: var(--disabled-text-color); }
      .temp-minus { left: -5%; top: 50%; transform: translateY(-50%); }
      .temp-plus { right: -5%; top: 50%; transform: translateY(-50%); }
      .temp-btn ha-icon { --mdc-icon-size: 20px; }
      .weight { margin: 0 16px 16px; padding: 12px; background: var(--secondary-background-color); border-radius: 12px; display: flex; justify-content: space-around; text-align: center; color: var(--primary-text-color); }
      .w-l { font-size: 9px; opacity: 0.5; font-weight: bold; }
      .divider { width: 1px; background: var(--divider-color); }
    `;
  }
}
customElements.define("gaggimate-card", GaggiMateCard);

window.customCards = window.customCards || [];
window.customCards.push({ type: "gaggimate-card", name: "GaggiMate", description: "Universal Gaggia Control", preview: true });
