DOMAIN = "priceradar"
PLATFORMS = ["sensor"]

MARKTGURU_API_URL = "https://www.marktguru.de/api/v1/offers"
MARKTGURU_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    "Referer": "https://www.marktguru.de/",
    "Origin": "https://www.marktguru.de",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}

CONF_POSTAL_CODE = "postal_code"
CONF_PRODUCTS = "products"
CONF_MAX_OFFERS = "max_offers"
CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_MAX_OFFERS = 10
DEFAULT_UPDATE_INTERVAL = 6

URL_BASE = "/priceradar"
CARD_URL = f"{URL_BASE}/priceradar-card.js"

ATTR_OFFERS = "offers"
ATTR_BEST_PRICE = "best_price"
ATTR_BEST_STORE = "best_store"
ATTR_VALID_UNTIL = "valid_until"
ATTR_OFFER_COUNT = "offer_count"
ATTR_POSTAL_CODE = "postal_code"

ICON = "mdi:tag-multiple"
