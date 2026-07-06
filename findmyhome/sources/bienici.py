"""Bien'ici source — public JSON endpoint, no API key needed."""
from __future__ import annotations

import json
import re
import time
import unicodedata

import requests

from ..models import Listing

API = "https://www.bienici.com/realEstateAds.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Bien'ici internal zone ids. -105270 = Bordeaux. Overridable via filters.bienici_zone_ids,
# or resolved automatically from filters.cities via the suggest endpoint.
DEFAULT_ZONE_IDS = ["-105270"]
SUGGEST_API = "https://res.bienici.com/suggest.json"
_zone_cache: dict[str, list[str]] = {}


def _resolve_zone_ids(filters: dict) -> list[str]:
    if filters.get("bienici_zone_ids"):
        return filters["bienici_zone_ids"]
    cities = filters.get("cities")
    if not cities:
        return DEFAULT_ZONE_IDS
    zone_ids: list[str] = []
    for city in cities:
        key = city.strip().lower()
        if key not in _zone_cache:
            try:
                resp = requests.get(SUGGEST_API, params={"q": city}, headers=HEADERS, timeout=15)
                resp.raise_for_status()
                hits = [h for h in resp.json() if h.get("type") == "city"]
                _zone_cache[key] = hits[0]["zoneIds"] if hits else []
            except Exception:
                _zone_cache[key] = []
        zone_ids.extend(_zone_cache[key])
    return zone_ids or DEFAULT_ZONE_IDS

PROPERTY_TYPES = {
    "appartement": "flat",
    "maison": "house",
    "flat": "flat",
    "house": "house",
}


def _slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "ville"


FILTER_TYPE = {"location": "rent", "achat": "buy"}


def _build_filters(filters: dict, size: int, offset: int, page: int) -> dict:
    mode = filters.get("mode", "location")
    f: dict = {
        "size": size,
        "from": offset,
        "page": page,
        "filterType": FILTER_TYPE.get(mode, "rent"),
        "onTheMarket": [True],
        "sortBy": "publicationDate",
        "sortOrder": "desc",
        "zoneIdsByTypes": {"zoneIds": _resolve_zone_ids(filters)},
    }
    types = filters.get("property_types", ["appartement"])
    f["propertyType"] = sorted({PROPERTY_TYPES.get(t, t) for t in types})
    if filters.get("max_price"):
        f["maxPrice"] = filters["max_price"]
    if filters.get("min_price"):
        f["minPrice"] = filters["min_price"]
    if filters.get("min_surface"):
        f["minArea"] = filters["min_surface"]
    if filters.get("min_rooms"):
        f["minRooms"] = filters["min_rooms"]
    return f


def _to_listing(ad: dict) -> Listing:
    city = ad.get("city", "")
    rooms = ad.get("roomsQuantity")
    ptype = "maison" if ad.get("propertyType") == "house" else "appartement"
    room_slug = f"{rooms}pieces" if rooms and rooms > 1 else "1piece"
    ad_type = "vente" if ad.get("adType") == "buy" else "location"
    url = f"https://www.bienici.com/annonce/{ad_type}/{_slug(city)}/{ptype}/{room_slug}/{ad['id']}"
    photos = [p.get("url_photo") or p.get("url", "") for p in ad.get("photos", [])]
    return Listing(
        id=f"bienici:{ad['id']}",
        source="bienici",
        url=url,
        title=ad.get("title") or f"{ptype.capitalize()} {rooms or '?'}p {city}",
        price=ad.get("price"),
        charges_included=("inclus" in (ad.get("chargesMethod") or "")) or None,
        rooms=rooms,
        bedrooms=ad.get("bedroomsQuantity"),
        surface=ad.get("surfaceArea"),
        city=city,
        postal_code=ad.get("postalCode", ""),
        district=(ad.get("district") or {}).get("name", "") if isinstance(ad.get("district"), dict) else "",
        furnished=ad.get("isFurnished"),
        floor=ad.get("floor"),
        energy_grade=(ad.get("energyClassification") or ""),
        description=ad.get("description", ""),
        photos=[p for p in photos if p][:3],
        published_at=(ad.get("publicationDate") or "")[:10],
        raw={"reference": ad.get("reference", ""), "adType": ad.get("adType", "")},
    )


def fetch(filters: dict, global_cfg: dict) -> list[Listing]:
    max_total = int(global_cfg.get("max_listings_per_source", 100))
    size = min(60, max_total)
    out: list[Listing] = []
    page = 1
    while len(out) < max_total:
        params = {"filters": json.dumps(_build_filters(filters, size, len(out), page))}
        resp = requests.get(API, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        ads = resp.json().get("realEstateAds", [])
        if not ads:
            break
        for ad in ads:
            try:
                out.append(_to_listing(ad))
            except Exception:
                continue
        if len(ads) < size:
            break
        page += 1
        time.sleep(1.0)  # courtesy throttle between pages to avoid abuse/ban
    return out[:max_total]
