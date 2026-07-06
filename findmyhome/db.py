"""SQLite persistence: listings, per-user scores, saved ads, report history."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import Listing

SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    price REAL,
    charges_included INTEGER,
    rooms INTEGER,
    bedrooms INTEGER,
    surface REAL,
    city TEXT,
    postal_code TEXT,
    district TEXT,
    furnished INTEGER,
    floor INTEGER,
    energy_grade TEXT,
    description TEXT,
    photos TEXT,
    published_at TEXT,
    raw TEXT,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS scores (
    listing_id TEXT NOT NULL,
    user TEXT NOT NULL,
    score INTEGER,
    verdict TEXT,
    reasons TEXT,
    scored_at TEXT NOT NULL,
    PRIMARY KEY (listing_id, user)
);
CREATE TABLE IF NOT EXISTS saved (
    listing_id TEXT NOT NULL,
    user TEXT NOT NULL,
    saved_at TEXT NOT NULL,
    note TEXT,
    PRIMARY KEY (listing_id, user)
);
CREATE TABLE IF NOT EXISTS reported (
    listing_id TEXT NOT NULL,
    user TEXT NOT NULL,
    reported_at TEXT NOT NULL,
    PRIMARY KEY (listing_id, user)
);
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Database:
    def __init__(self, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    # --- listings -----------------------------------------------------
    def upsert_listing(self, listing: Listing) -> bool:
        """Insert or refresh a listing. Returns True if it was new."""
        row = listing.to_row()
        cur = self.conn.execute("SELECT id FROM listings WHERE id = ?", (listing.id,))
        is_new = cur.fetchone() is None
        ts = now_iso()
        if is_new:
            row["first_seen"] = ts
            row["last_seen"] = ts
            cols = ", ".join(row)
            marks = ", ".join(":" + k for k in row)
            self.conn.execute(f"INSERT INTO listings ({cols}) VALUES ({marks})", row)
        else:
            row["last_seen"] = ts
            sets = ", ".join(f"{k} = :{k}" for k in row if k not in ("id",))
            self.conn.execute(f"UPDATE listings SET {sets} WHERE id = :id", row)
        self.conn.commit()
        return is_new

    def get_listing(self, listing_id: str) -> Listing | None:
        cur = self.conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,))
        row = cur.fetchone()
        return Listing.from_row(dict(row)) if row else None

    def find_listing(self, prefix: str) -> Listing | None:
        """Exact id match, else unique prefix/substring match."""
        exact = self.get_listing(prefix)
        if exact:
            return exact
        cur = self.conn.execute(
            "SELECT * FROM listings WHERE id LIKE ?", (f"%{prefix}%",)
        )
        rows = cur.fetchall()
        return Listing.from_row(dict(rows[0])) if len(rows) == 1 else None

    # --- scores -------------------------------------------------------
    def set_score(self, listing_id: str, user: str, score: int, verdict: str, reasons: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO scores (listing_id, user, score, verdict, reasons, scored_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (listing_id, user, score, verdict, reasons, now_iso()),
        )
        self.conn.commit()

    def get_score(self, listing_id: str, user: str):
        cur = self.conn.execute(
            "SELECT * FROM scores WHERE listing_id = ? AND user = ?", (listing_id, user)
        )
        row = cur.fetchone()
        return dict(row) if row else None

    # --- saved --------------------------------------------------------
    def save_listing(self, listing_id: str, user: str, note: str = ""):
        self.conn.execute(
            "INSERT OR REPLACE INTO saved (listing_id, user, saved_at, note) VALUES (?, ?, ?, ?)",
            (listing_id, user, now_iso(), note),
        )
        self.conn.commit()

    def unsave_listing(self, listing_id: str, user: str):
        self.conn.execute(
            "DELETE FROM saved WHERE listing_id = ? AND user = ?", (listing_id, user)
        )
        self.conn.commit()

    def saved_listings(self, user: str) -> list[tuple[Listing, dict]]:
        cur = self.conn.execute(
            "SELECT l.*, s.saved_at, s.note FROM saved s JOIN listings l ON l.id = s.listing_id"
            " WHERE s.user = ? ORDER BY s.saved_at DESC",
            (user,),
        )
        out = []
        for row in cur.fetchall():
            d = dict(row)
            meta = {"saved_at": d.pop("saved_at"), "note": d.pop("note")}
            out.append((Listing.from_row(d), meta))
        return out

    # --- report history -------------------------------------------------
    def mark_reported(self, listing_ids: list[str], user: str):
        ts = now_iso()
        self.conn.executemany(
            "INSERT OR REPLACE INTO reported (listing_id, user, reported_at) VALUES (?, ?, ?)",
            [(lid, user, ts) for lid in listing_ids],
        )
        self.conn.commit()

    def already_reported(self, user: str) -> set[str]:
        cur = self.conn.execute("SELECT listing_id FROM reported WHERE user = ?", (user,))
        return {r["listing_id"] for r in cur.fetchall()}
