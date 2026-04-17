from __future__ import annotations

import logging
import pathlib

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant, Event
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, PLATFORMS, CARD_URL
from .coordinator import PriceRadarCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})

    card_path = pathlib.Path(__file__).parent / "priceradar-card.js"
    if not card_path.exists():
        _LOGGER.error("PriceRadar card JS not found at %s", card_path)
        return True

    await hass.http.async_register_static_paths([
        StaticPathConfig(CARD_URL, str(card_path), False)
    ])
    _LOGGER.info("PriceRadar card served at %s", CARD_URL)

    async def _on_started(event: Event) -> None:
        registered = await _async_register_lovelace_resource(hass, CARD_URL)
        if not registered:
            hass.components.persistent_notification.async_create(
                "Die **PriceRadar Lovelace-Karte** konnte nicht automatisch registriert werden.\n\n"
                "Bitte manuell hinzufügen:\n"
                "1. **Einstellungen → Dashboards → Ressourcen** (⋮ Menü oben rechts)\n"
                f"2. **Ressource hinzufügen** → URL: `{CARD_URL}`\n"
                "3. Typ: **JavaScript-Modul**\n"
                "4. Speichern und Browser neu laden\n\n"
                "Danach erscheint **PriceRadar** in der Kartenauswahl.",
                title="PriceRadar: Karte manuell registrieren",
                notification_id="priceradar_resource",
            )

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _on_started)
    return True


async def _async_register_lovelace_resource(hass: HomeAssistant, url: str) -> bool:
    lovelace = hass.data.get("lovelace")
    _LOGGER.debug("Lovelace data keys: %s", list(lovelace.keys()) if lovelace else "None")

    if not lovelace:
        _LOGGER.warning("PriceRadar: hass.data['lovelace'] is None — cannot auto-register card")
        return False

    resources = lovelace.get("resources")
    if resources is None:
        _LOGGER.warning("PriceRadar: lovelace['resources'] is None (YAML mode?) — cannot auto-register card")
        return False

    try:
        existing_urls = {r["url"] for r in resources.async_items()}
        if url in existing_urls:
            _LOGGER.debug("PriceRadar resource already registered: %s", url)
            return True

        await resources.async_create_item({"res_type": "module", "url": url})
        _LOGGER.info("PriceRadar card registered as Lovelace resource: %s", url)
        return True
    except Exception as err:
        _LOGGER.warning("PriceRadar: failed to register Lovelace resource: %s", err)
        return False


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    session = async_get_clientsession(hass)
    coordinator = PriceRadarCoordinator(hass, session, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
