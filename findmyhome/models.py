"""Core data model: a rental listing, normalized across sources."""
from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Listing:
    id: str                      # globally unique: "<source>:<source_id>"
    source: str                  # "bienici", "leboncoin", ...
    url: str
    title: str
    price: Optional[float] = None          # monthly rent, charges included when known
    charges_included: Optional[bool] = None
    rooms: Optional[int] = None
    bedrooms: Optional[int] = None
    surface: Optional[float] = None        # m2
    city: str = ""
    postal_code: str = ""
    district: str = ""
    furnished: Optional[bool] = None
    floor: Optional[int] = None
    energy_grade: str = ""
    description: str = ""
    photos: list[str] = field(default_factory=list)
    published_at: str = ""       # ISO date string when available
    raw: dict[str, Any] = field(default_factory=dict)

    def to_row(self) -> dict[str, Any]:
        d = dataclasses.asdict(self)
        d["photos"] = json.dumps(self.photos, ensure_ascii=False)
        d["raw"] = json.dumps(self.raw, ensure_ascii=False)
        d["charges_included"] = _bool_int(self.charges_included)
        d["furnished"] = _bool_int(self.furnished)
        return d

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "Listing":
        row = dict(row)
        row["photos"] = json.loads(row.get("photos") or "[]")
        row["raw"] = json.loads(row.get("raw") or "{}")
        row["charges_included"] = _int_bool(row.get("charges_included"))
        row["furnished"] = _int_bool(row.get("furnished"))
        known = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in row.items() if k in known})

    def summary_for_llm(self) -> str:
        parts = [
            f"ID: {self.id}",
            f"Titre: {self.title}",
            f"Prix: {self.price}€/mois" + (" CC" if self.charges_included else ""),
            f"Pièces: {self.rooms or '?'} | Chambres: {self.bedrooms or '?'} | Surface: {self.surface or '?'}m2",
            f"Ville: {self.city} {self.postal_code} {self.district}".strip(),
        ]
        if self.furnished is not None:
            parts.append("Meublé: " + ("oui" if self.furnished else "non"))
        if self.floor is not None:
            parts.append(f"Étage: {self.floor}")
        if self.energy_grade:
            parts.append(f"DPE: {self.energy_grade}")
        desc = (self.description or "").strip()
        if len(desc) > 1200:
            desc = desc[:1200] + "…"
        if desc:
            parts.append("Description: " + desc)
        return "\n".join(parts)


def _bool_int(v: Optional[bool]) -> Optional[int]:
    return None if v is None else int(v)


def _int_bool(v: Any) -> Optional[bool]:
    return None if v is None else bool(v)
