from __future__ import annotations

import logging
import pathlib

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, PLATFORMS, URL_BASE, CARD_URL
from .coordinator import PriceRadarCoordinator

_LOGGER = logging.getLogger(__name__)

LOVELACE_RESOURCE_URL = CARD_URL


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    hass.data.setdefault(DOMAIN, {})

    card_path = pathlib.Path(__file__).parent / "priceradar-card.js"
    if card_path.exists():
        hass.http.register_static_path(
            LOVELACE_RESOURCE_URL,
            str(card_path),
            cache_headers=False,
        )
        await _async_register_lovelace_resource(hass, LOVELACE_RESOURCE_URL)

    return True


async def _async_register_lovelace_resource(hass: HomeAssistant, url: str) -> None:
    try:
        resources = hass.data.get("lovelace", {}).get("resources")
        if resources is None:
            _LOGGER.debug("Lovelace resources not available yet, skipping registration")
            return

        existing = [r["url"] for r in resources.async_items()]
        if url in existing:
            return

        await resources.async_create_item({"res_type": "module", "url": url})
        _LOGGER.info("PriceRadar card registered as Lovelace resource: %s", url)
    except Exception as err:
        _LOGGER.warning("Could not register PriceRadar Lovelace resource: %s", err)


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
