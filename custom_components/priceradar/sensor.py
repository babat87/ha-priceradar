from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ICON,
    ATTR_OFFERS,
    ATTR_BEST_PRICE,
    ATTR_BEST_STORE,
    ATTR_VALID_UNTIL,
    ATTR_OFFER_COUNT,
    ATTR_POSTAL_CODE,
)
from .coordinator import PriceRadarCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: PriceRadarCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        PriceRadarSensor(coordinator, product, entry.entry_id)
        for product in coordinator.products
    ]
    async_add_entities(entities, True)


class PriceRadarSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity representing the best current offer for a product."""

    def __init__(
        self, coordinator: PriceRadarCoordinator, product: str, entry_id: str
    ) -> None:
        super().__init__(coordinator)
        self._product = product
        self._attr_unique_id = f"{entry_id}_{product.lower().replace(' ', '_')}"
        self._attr_name = f"PriceRadar {product}"
        self._attr_icon = ICON
        self._attr_native_unit_of_measurement = "€"

    @property
    def offers(self) -> list[dict]:
        if self.coordinator.data is None:
            return []
        return self.coordinator.data.get(self._product, [])

    @property
    def best_offer(self) -> dict | None:
        offers = self.offers
        if not offers:
            return None
        return min(offers, key=lambda o: o.get("price") or float("inf"))

    @property
    def native_value(self):
        offer = self.best_offer
        if offer is None:
            return None
        return offer.get("price")

    @property
    def extra_state_attributes(self) -> dict:
        offer = self.best_offer
        offers = self.offers
        attrs: dict = {
            ATTR_POSTAL_CODE: self.coordinator.postal_code,
            ATTR_OFFER_COUNT: len(offers),
            ATTR_OFFERS: offers,
        }
        if offer:
            attrs[ATTR_BEST_PRICE] = offer.get("price")
            attrs[ATTR_BEST_STORE] = offer.get("retailer")
            attrs[ATTR_VALID_UNTIL] = offer.get("valid_to")
        return attrs

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success
