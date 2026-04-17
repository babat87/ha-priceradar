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
            "zipCode": self.postal_code,
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
                offers = data.get("results", [])
                return [self._parse_offer(o) for o in offers if o.get("price") is not None]

        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Verbindungsfehler: {err}") from err

    @staticmethod
    def _parse_offer(offer: dict) -> dict:
        advertisers = offer.get("advertisers") or []
        retailer_name = advertisers[0].get("name", "Unbekannt") if advertisers else "Unbekannt"

        price = offer.get("price")
        old_price = offer.get("oldPrice")

        discount_percent = None
        if price is not None and old_price and old_price > price:
            discount_percent = round((1 - price / old_price) * 100)

        validity = (offer.get("validityDates") or [{}])[0]
        brand = offer.get("brand") or {}
        unit = offer.get("unit") or {}
        categories = offer.get("categories") or []

        # Brand name (e.g. "Philadelphia") is more useful than generic product.name
        name = brand.get("name") or (offer.get("product") or {}).get("name", "Unbekannt")

        return {
            "id": offer.get("id", ""),
            "name": name,
            "description": offer.get("description", ""),
            "price": price,
            "regular_price": old_price,
            "discount_percent": discount_percent,
            "unit": unit.get("shortName", ""),
            "quantity": offer.get("quantity", ""),
            "retailer": retailer_name,
            "retailer_logo": "",
            "retailer_color": "",
            "valid_from": validity.get("from", ""),
            "valid_to": validity.get("to", ""),
            "image_url": "",
            "category": categories[0].get("name", "") if categories else "",
        }
