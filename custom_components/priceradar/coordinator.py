from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    MARKTGURU_API_URL,
    MARKTGURU_HEADERS,
    CONF_POSTAL_CODE,
    CONF_PRODUCTS,
    CONF_MAX_OFFERS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_MAX_OFFERS,
    DEFAULT_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class PriceRadarCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch product offers from Marktguru."""

    def __init__(self, hass: HomeAssistant, session: aiohttp.ClientSession, entry) -> None:
        self.session = session
        self.postal_code: str = entry.data[CONF_POSTAL_CODE]
        self.products: list[str] = entry.data[CONF_PRODUCTS]
        self.max_offers: int = entry.options.get(
            CONF_MAX_OFFERS, entry.data.get(CONF_MAX_OFFERS, DEFAULT_MAX_OFFERS)
        )
        update_hours: int = entry.options.get(
            CONF_UPDATE_INTERVAL, entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=update_hours),
        )

    async def _async_update_data(self) -> dict:
        results: dict[str, list[dict]] = {}
        tasks = [self._fetch_offers(product) for product in self.products]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for product, response in zip(self.products, responses):
            if isinstance(response, Exception):
                _LOGGER.warning("Fehler beim Abrufen von Angeboten für '%s': %s", product, response)
                results[product] = []
            else:
                results[product] = response

        return results

    async def _fetch_offers(self, product: str) -> list[dict]:
        params = {
            "as": "web",
            "limit": self.max_offers,
            "postal_code": self.postal_code,
            "q": product,
        }
        timeout = aiohttp.ClientTimeout(total=30)

        try:
            async with self.session.get(
                MARKTGURU_API_URL,
                params=params,
                headers=MARKTGURU_HEADERS,
                timeout=timeout,
            ) as response:
                if response.status == 429:
                    raise UpdateFailed("Rate-Limit erreicht – bitte Abrufintervall erhöhen")
                if response.status != 200:
                    raise UpdateFailed(f"HTTP {response.status} für '{product}'")

                data = await response.json(content_type=None)
                offers = data.get("offers", [])
                return [self._parse_offer(o) for o in offers if o.get("price") is not None]

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Verbindungsfehler: {err}") from err

    @staticmethod
    def _parse_offer(offer: dict) -> dict:
        retailer = offer.get("retailer") or {}
        price = offer.get("price")
        regular_price = offer.get("regular_price")

        discount_percent = None
        if price is not None and regular_price and regular_price > price:
            discount_percent = round((1 - price / regular_price) * 100)

        return {
            "id": offer.get("id", ""),
            "name": offer.get("name", "Unbekannt"),
            "description": offer.get("description", ""),
            "price": price,
            "regular_price": regular_price,
            "discount_percent": discount_percent,
            "unit": offer.get("unit", ""),
            "quantity": offer.get("quantity", ""),
            "retailer": retailer.get("name", "Unbekannt"),
            "retailer_logo": retailer.get("logo_url", ""),
            "retailer_color": retailer.get("color", ""),
            "valid_from": offer.get("valid_from", ""),
            "valid_to": offer.get("valid_to", ""),
            "image_url": offer.get("image_url", ""),
            "category": offer.get("category", {}).get("name", "") if offer.get("category") else "",
        }
