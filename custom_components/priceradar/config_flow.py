from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import aiohttp

from .const import (
    DOMAIN,
    CONF_POSTAL_CODE,
    CONF_PRODUCTS,
    CONF_MAX_OFFERS,
    CONF_UPDATE_INTERVAL,
    DEFAULT_MAX_OFFERS,
    DEFAULT_UPDATE_INTERVAL,
    MARKTGURU_API_URL,
    MARKTGURU_HEADERS,
)


def _products_from_string(value: str) -> list[str]:
    return [p.strip() for p in value.split(",") if p.strip()]


class PriceRadarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PriceRadar."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            postal_code = user_input[CONF_POSTAL_CODE].strip()
            products_raw = user_input.get(CONF_PRODUCTS, "")
            products = _products_from_string(products_raw)

            if not postal_code.isdigit() or len(postal_code) != 5:
                errors[CONF_POSTAL_CODE] = "invalid_postal_code"
            elif not products:
                errors[CONF_PRODUCTS] = "no_products"
            else:
                ok = await self._test_connection(postal_code, products[0])
                if not ok:
                    errors["base"] = "cannot_connect"
                else:
                    await self.async_set_unique_id(f"priceradar_{postal_code}")
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"PriceRadar {postal_code}",
                        data={
                            CONF_POSTAL_CODE: postal_code,
                            CONF_PRODUCTS: products,
                            CONF_MAX_OFFERS: user_input.get(CONF_MAX_OFFERS, DEFAULT_MAX_OFFERS),
                            CONF_UPDATE_INTERVAL: user_input.get(
                                CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                            ),
                        },
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_POSTAL_CODE): str,
                vol.Required(CONF_PRODUCTS): str,
                vol.Optional(CONF_MAX_OFFERS, default=DEFAULT_MAX_OFFERS): vol.All(
                    int, vol.Range(min=1, max=50)
                ),
                vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
                    int, vol.Range(min=1, max=24)
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def _test_connection(self, postal_code: str, product: str) -> bool:
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                MARKTGURU_API_URL,
                params={"as": "web", "limit": 1, "zipCode": postal_code, "q": product},
                headers=MARKTGURU_HEADERS,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                return resp.status in (200, 204)
        except Exception:
            return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PriceRadarOptionsFlow(config_entry)


class PriceRadarOptionsFlow(config_entries.OptionsFlow):
    """Handle options for PriceRadar."""

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}

        if user_input is not None:
            products_raw = user_input.get(CONF_PRODUCTS, "")
            products = _products_from_string(products_raw)
            if not products:
                errors[CONF_PRODUCTS] = "no_products"
            else:
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_PRODUCTS: products,
                        CONF_MAX_OFFERS: user_input.get(CONF_MAX_OFFERS, DEFAULT_MAX_OFFERS),
                        CONF_UPDATE_INTERVAL: user_input.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    },
                )

        current_products = self.config_entry.options.get(
            CONF_PRODUCTS, self.config_entry.data.get(CONF_PRODUCTS, [])
        )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_PRODUCTS, default=", ".join(current_products)
                ): str,
                vol.Optional(
                    CONF_MAX_OFFERS,
                    default=self.config_entry.options.get(CONF_MAX_OFFERS, DEFAULT_MAX_OFFERS),
                ): vol.All(int, vol.Range(min=1, max=50)),
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                    ),
                ): vol.All(int, vol.Range(min=1, max=24)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
        )
