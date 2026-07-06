"""Hard filters: cheap structural elimination before LLM scoring."""
from __future__ import annotations

from .models import Listing


def passes(listing: Listing, filters: dict) -> bool:
    if filters.get("max_price") and listing.price and listing.price > filters["max_price"]:
        return False
    if filters.get("min_price") and listing.price and listing.price < filters["min_price"]:
        return False
    if filters.get("min_surface") and listing.surface and listing.surface < filters["min_surface"]:
        return False
    if filters.get("max_surface") and listing.surface and listing.surface > filters["max_surface"]:
        return False
    if filters.get("min_rooms") and listing.rooms and listing.rooms < filters["min_rooms"]:
        return False
    if filters.get("furnished") is not None and listing.furnished is not None:
        if listing.furnished != filters["furnished"]:
            return False
    cities = filters.get("cities")
    if cities and listing.city:
        wanted = {c.strip().lower() for c in cities}
        if listing.city.strip().lower() not in wanted:
            return False
    return True


def apply(listings: list[Listing], filters: dict) -> list[Listing]:
    return [l for l in listings if passes(l, filters)]
