/**
 * PriceRadar Lovelace Card
 * Zeigt lokale Produktangebote aus Marktguru geordnet nach Preis.
 */

const CARD_VERSION = "1.0.0";

const styles = `
  :host {
    --pr-primary: var(--primary-color, #03a9f4);
    --pr-bg: var(--card-background-color, #fff);
    --pr-text: var(--primary-text-color, #212121);
    --pr-secondary: var(--secondary-text-color, #727272);
    --pr-divider: var(--divider-color, #e0e0e0);
    --pr-green: #4caf50;
    --pr-orange: #ff9800;
    --pr-red: #f44336;
    --pr-radius: 12px;
    --pr-shadow: 0 2px 8px rgba(0,0,0,0.12);
  }

  .card-container {
    padding: 16px;
    background: var(--pr-bg);
    border-radius: var(--pr-radius);
    font-family: var(--paper-font-body1_-_font-family, sans-serif);
    color: var(--pr-text);
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .card-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.2em;
    font-weight: 600;
  }

  .card-title ha-icon {
    color: var(--pr-primary);
  }

  .search-box {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--pr-divider);
    border-radius: 20px;
    padding: 4px 12px;
    flex: 1;
    min-width: 150px;
    max-width: 280px;
  }

  .search-box input {
    border: none;
    background: transparent;
    color: var(--pr-text);
    font-size: 0.9em;
    outline: none;
    width: 100%;
  }

  .controls {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
  }

  .sort-select {
    border: 1px solid var(--pr-divider);
    border-radius: 8px;
    padding: 4px 8px;
    background: var(--pr-bg);
    color: var(--pr-text);
    font-size: 0.85em;
    cursor: pointer;
  }

  .product-section {
    margin-bottom: 16px;
  }

  .product-title {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: var(--pr-primary);
    color: #fff;
    border-radius: 8px 8px 0 0;
    font-weight: 600;
    font-size: 1em;
    cursor: pointer;
    user-select: none;
  }

  .product-title .badge {
    margin-left: auto;
    background: rgba(255,255,255,0.25);
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 0.8em;
  }

  .product-title .toggle-icon {
    transition: transform 0.2s;
  }

  .product-title.collapsed .toggle-icon {
    transform: rotate(-90deg);
  }

  .offers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
    padding: 10px;
    border: 1px solid var(--pr-divider);
    border-top: none;
    border-radius: 0 0 8px 8px;
    background: var(--ha-card-background, var(--pr-bg));
  }

  .offers-grid.collapsed {
    display: none;
  }

  .offer-card {
    border-radius: 8px;
    overflow: hidden;
    box-shadow: var(--pr-shadow);
    display: flex;
    flex-direction: column;
    background: var(--pr-bg);
    border: 1px solid var(--pr-divider);
    transition: transform 0.15s, box-shadow 0.15s;
    cursor: default;
  }

  .offer-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(0,0,0,0.18);
  }

  .offer-image-wrap {
    position: relative;
    height: 100px;
    background: #f5f5f5;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  .offer-image-wrap img {
    max-height: 90px;
    max-width: 100%;
    object-fit: contain;
  }

  .offer-image-wrap .no-image {
    font-size: 2.5em;
    opacity: 0.3;
  }

  .discount-badge {
    position: absolute;
    top: 6px;
    right: 6px;
    background: var(--pr-red);
    color: #fff;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75em;
    font-weight: bold;
    line-height: 1.1;
    text-align: center;
  }

  .offer-body {
    padding: 8px 10px;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .offer-name {
    font-weight: 600;
    font-size: 0.9em;
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .offer-retailer {
    font-size: 0.78em;
    color: var(--pr-secondary);
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .retailer-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--pr-primary);
    display: inline-block;
    flex-shrink: 0;
  }

  .offer-price-row {
    display: flex;
    align-items: baseline;
    gap: 6px;
    margin-top: auto;
    padding-top: 4px;
  }

  .offer-price {
    font-size: 1.2em;
    font-weight: bold;
    color: var(--pr-green);
  }

  .offer-regular-price {
    font-size: 0.82em;
    color: var(--pr-secondary);
    text-decoration: line-through;
  }

  .offer-validity {
    font-size: 0.72em;
    color: var(--pr-secondary);
    display: flex;
    align-items: center;
    gap: 3px;
    margin-top: 2px;
  }

  .validity-urgent {
    color: var(--pr-orange);
    font-weight: 600;
  }

  .validity-expired {
    color: var(--pr-red);
  }

  .no-offers {
    padding: 16px;
    text-align: center;
    color: var(--pr-secondary);
    font-style: italic;
    border: 1px solid var(--pr-divider);
    border-top: none;
    border-radius: 0 0 8px 8px;
  }

  .loading {
    text-align: center;
    padding: 24px;
    color: var(--pr-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }

  .spinner {
    width: 20px;
    height: 20px;
    border: 3px solid var(--pr-divider);
    border-top-color: var(--pr-primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .last-updated {
    font-size: 0.72em;
    color: var(--pr-secondary);
    text-align: right;
    margin-top: 12px;
    padding-top: 8px;
    border-top: 1px solid var(--pr-divider);
  }

  .error-msg {
    background: rgba(244, 67, 54, 0.1);
    border: 1px solid var(--pr-red);
    border-radius: 8px;
    padding: 12px;
    color: var(--pr-red);
    font-size: 0.9em;
    margin-bottom: 12px;
  }
`;

class PriceRadarCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._collapsedSections = new Set();
    this._filterText = "";
    this._sortMode = "price";
    this._initialized = false;
  }

  static getStubConfig() {
    return {
      title: "PriceRadar",
      entities: [],
      show_images: true,
      columns: 3,
    };
  }

  setConfig(config) {
    if (!config.entities || !Array.isArray(config.entities)) {
      throw new Error("PriceRadar: 'entities' muss eine Liste von Sensor-Entities sein.");
    }
    this._config = {
      title: "PriceRadar",
      show_images: true,
      columns: 3,
      ...config,
    };
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  _render() {
    if (!this._config || !this._hass) return;

    const root = this.shadowRoot;
    root.innerHTML = "";

    const style = document.createElement("style");
    style.textContent = styles;
    root.appendChild(style);

    const container = document.createElement("div");
    container.className = "card-container";
    container.innerHTML = this._buildHTML();
    root.appendChild(container);

    this._attachEvents(container);
  }

  _buildHTML() {
    const entities = this._config.entities || [];
    const sections = entities.map((entityId) => this._buildSection(entityId)).join("");
    const hasAny = entities.length > 0;

    return `
      <div class="card-header">
        <div class="card-title">
          <ha-icon icon="mdi:tag-multiple"></ha-icon>
          ${this._config.title || "PriceRadar"}
        </div>
        ${hasAny ? `
        <div class="controls">
          <div class="search-box">
            <ha-icon icon="mdi:magnify" style="font-size:16px;color:var(--pr-secondary)"></ha-icon>
            <input type="text" placeholder="Filtern..." value="${this._escapeHtml(this._filterText)}" id="pr-filter" />
          </div>
          <select class="sort-select" id="pr-sort">
            <option value="price" ${this._sortMode === "price" ? "selected" : ""}>↑ Preis</option>
            <option value="discount" ${this._sortMode === "discount" ? "selected" : ""}>% Rabatt</option>
            <option value="validity" ${this._sortMode === "validity" ? "selected" : ""}>⏱ Gültigkeit</option>
          </select>
        </div>` : ""}
      </div>
      ${hasAny ? sections : '<div class="loading"><div class="spinner"></div> Keine Entities konfiguriert.</div>'}
      <div class="last-updated" id="pr-last-updated">${this._getLastUpdated()}</div>
    `;
  }

  _buildSection(entityId) {
    const stateObj = this._hass.states[entityId];
    if (!stateObj) {
      return `<div class="error-msg">Entity nicht gefunden: <b>${this._escapeHtml(entityId)}</b></div>`;
    }

    const productName = stateObj.attributes.friendly_name || entityId;
    const offers = (stateObj.attributes.offers || []);
    const filtered = this._filterOffers(offers);
    const sorted = this._sortOffers(filtered);

    const collapsed = this._collapsedSections.has(entityId);
    const offerCount = sorted.length;

    const offersHTML = offerCount === 0
      ? `<div class="no-offers">Keine Angebote gefunden für "${this._escapeHtml(productName)}".</div>`
      : `<div class="offers-grid ${collapsed ? "collapsed" : ""}" id="grid-${this._safeId(entityId)}" style="grid-template-columns: repeat(${this._config.columns || 3}, 1fr)">
          ${sorted.map((o) => this._buildOfferCard(o)).join("")}
        </div>`;

    return `
      <div class="product-section" data-entity="${this._escapeHtml(entityId)}">
        <div class="product-title ${collapsed ? "collapsed" : ""}" data-entity="${this._escapeHtml(entityId)}">
          <ha-icon icon="mdi:cart-outline"></ha-icon>
          ${this._escapeHtml(productName.replace(/^PriceRadar\s+/i, ""))}
          <span class="badge">${offerCount} Angebote</span>
          <ha-icon icon="mdi:chevron-down" class="toggle-icon"></ha-icon>
        </div>
        ${offersHTML}
      </div>
    `;
  }

  _buildOfferCard(offer) {
    const price = offer.price != null ? `${offer.price.toFixed(2)} €` : "–";
    const regularPrice = offer.regular_price && offer.regular_price > offer.price
      ? `${offer.regular_price.toFixed(2)} €`
      : null;
    const discount = offer.discount_percent ? `-${offer.discount_percent}%` : null;
    const validTo = offer.valid_to ? new Date(offer.valid_to) : null;
    const validityHTML = this._buildValidityHTML(validTo);
    const imageHTML = this._buildImageHTML(offer);

    return `
      <div class="offer-card">
        ${imageHTML}
        <div class="offer-body">
          <div class="offer-name">${this._escapeHtml(offer.name || "Unbekannt")}</div>
          <div class="offer-retailer">
            <span class="retailer-dot" style="${offer.retailer_color ? `background:${offer.retailer_color}` : ""}"></span>
            ${this._escapeHtml(offer.retailer || "Unbekannt")}
          </div>
          <div class="offer-price-row">
            <span class="offer-price">${price}</span>
            ${regularPrice ? `<span class="offer-regular-price">${regularPrice}</span>` : ""}
          </div>
          ${validityHTML}
        </div>
      </div>
    `;
  }

  _buildImageHTML(offer) {
    const discount = offer.discount_percent;
    const badgeHTML = discount
      ? `<div class="discount-badge">-${discount}%</div>`
      : "";

    if (this._config.show_images !== false && offer.image_url) {
      return `
        <div class="offer-image-wrap">
          <img src="${this._escapeHtml(offer.image_url)}" alt="${this._escapeHtml(offer.name || "")}" loading="lazy"
            onerror="this.parentElement.innerHTML='<span class=\\'no-image\\'>🏷️</span>${badgeHTML}'" />
          ${badgeHTML}
        </div>
      `;
    }
    return `
      <div class="offer-image-wrap">
        <span class="no-image">🏷️</span>
        ${badgeHTML}
      </div>
    `;
  }

  _buildValidityHTML(validTo) {
    if (!validTo || isNaN(validTo.getTime())) return "";
    const now = new Date();
    const diffDays = Math.ceil((validTo - now) / 86400000);

    if (diffDays < 0) {
      return `<div class="offer-validity validity-expired">⚠ Abgelaufen</div>`;
    }
    if (diffDays === 0) {
      return `<div class="offer-validity validity-urgent">⏰ Heute letzter Tag!</div>`;
    }
    if (diffDays <= 2) {
      return `<div class="offer-validity validity-urgent">⏰ Noch ${diffDays} Tag${diffDays > 1 ? "e" : ""}</div>`;
    }
    return `<div class="offer-validity">📅 bis ${validTo.toLocaleDateString("de-DE")}</div>`;
  }

  _filterOffers(offers) {
    if (!this._filterText) return offers;
    const q = this._filterText.toLowerCase();
    return offers.filter(
      (o) =>
        (o.name || "").toLowerCase().includes(q) ||
        (o.retailer || "").toLowerCase().includes(q)
    );
  }

  _sortOffers(offers) {
    const clone = [...offers];
    if (this._sortMode === "price") {
      return clone.sort((a, b) => (a.price ?? Infinity) - (b.price ?? Infinity));
    }
    if (this._sortMode === "discount") {
      return clone.sort((a, b) => (b.discount_percent ?? 0) - (a.discount_percent ?? 0));
    }
    if (this._sortMode === "validity") {
      return clone.sort((a, b) => {
        const da = a.valid_to ? new Date(a.valid_to) : new Date(9999, 0);
        const db = b.valid_to ? new Date(b.valid_to) : new Date(9999, 0);
        return da - db;
      });
    }
    return clone;
  }

  _getLastUpdated() {
    const entities = this._config.entities || [];
    const times = entities
      .map((id) => this._hass?.states[id]?.last_updated)
      .filter(Boolean)
      .map((t) => new Date(t).getTime());
    if (!times.length) return "";
    const latest = new Date(Math.max(...times));
    return `Zuletzt aktualisiert: ${latest.toLocaleString("de-DE")}`;
  }

  _attachEvents(container) {
    const filterInput = container.querySelector("#pr-filter");
    if (filterInput) {
      filterInput.addEventListener("input", (e) => {
        this._filterText = e.target.value;
        this._render();
      });
    }

    const sortSelect = container.querySelector("#pr-sort");
    if (sortSelect) {
      sortSelect.addEventListener("change", (e) => {
        this._sortMode = e.target.value;
        this._render();
      });
    }

    container.querySelectorAll(".product-title").forEach((el) => {
      el.addEventListener("click", () => {
        const entityId = el.dataset.entity;
        if (this._collapsedSections.has(entityId)) {
          this._collapsedSections.delete(entityId);
        } else {
          this._collapsedSections.add(entityId);
        }
        this._render();
      });
    });
  }

  _safeId(str) {
    return str.replace(/[^a-z0-9]/gi, "_");
  }

  _escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  getCardSize() {
    return (this._config.entities || []).length * 3 + 1;
  }
}

customElements.define("priceradar-card", PriceRadarCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "priceradar-card",
  name: "PriceRadar",
  description: "Zeigt lokale Produktangebote aus Marktguru",
  preview: false,
  documentationURL: "https://github.com/user/ha-priceradar",
});

console.info(
  `%c PRICERADAR-CARD %c v${CARD_VERSION} `,
  "background:#03a9f4;color:#fff;font-weight:bold;border-radius:4px 0 0 4px",
  "background:#222;color:#fff;font-weight:bold;border-radius:0 4px 4px 0"
);
