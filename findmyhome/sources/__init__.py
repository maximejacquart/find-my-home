"""Source registry. Each source exposes fetch(filters, global_cfg) -> list[Listing]."""
from __future__ import annotations

from typing import Callable

from ..models import Listing
from . import bienici

SOURCES: dict[str, Callable[[dict, dict], list[Listing]]] = {
    "bienici": bienici.fetch,
}


def fetch_all(source_names: list[str], filters: dict, global_cfg: dict) -> list[Listing]:
    listings: list[Listing] = []
    for name in source_names:
        fn = SOURCES.get(name)
        if fn is None:
            print(f"  ! source inconnue: {name} (disponibles: {', '.join(SOURCES)})")
            continue
        try:
            found = fn(filters, global_cfg)
            print(f"  {name}: {len(found)} annonces")
            listings.extend(found)
        except Exception as e:  # a broken source must not kill the weekly run
            print(f"  ! {name} en erreur: {e}")
    return listings
