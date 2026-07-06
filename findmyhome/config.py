"""Config loading: global settings + per-user criteria files."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
USERS_DIR = CONFIG_DIR / "users"

load_dotenv(ROOT / ".env")


def load_global() -> dict:
    path = CONFIG_DIR / "config.yaml"
    if not path.exists():
        path = CONFIG_DIR / "config.example.yaml"
    with open(path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    smtp = cfg.setdefault("smtp", {})
    smtp.setdefault("host", "smtp.gmail.com")
    smtp.setdefault("port", 465)
    smtp["user"] = os.environ.get("GMAIL_USER", smtp.get("user", ""))
    smtp["password"] = os.environ.get("GMAIL_APP_PASSWORD", "")
    cfg["firecrawl_api_key"] = os.environ.get("FIRECRAWL_API_KEY", "")
    cfg.setdefault("db_path", str(ROOT / "data" / "findmyhome.db"))
    cfg.setdefault("top_n", 12)
    cfg.setdefault("max_listings_per_source", 100)
    return cfg


def load_user(name: str) -> dict:
    path = USERS_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"User config not found: {path}. Copy config/users/example.yaml to create one."
        )
    with open(path, encoding="utf-8") as f:
        user = yaml.safe_load(f) or {}
    user["name"] = name
    user.setdefault("filters", {})
    user.setdefault("preferences", "")
    user.setdefault("sources", ["bienici"])
    return user


def list_users() -> list[str]:
    if not USERS_DIR.exists():
        return []
    return sorted(p.stem for p in USERS_DIR.glob("*.yaml") if p.stem != "example")
