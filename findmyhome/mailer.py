"""Gmail sending — REST API (HTTPS) si les vars OAuth sont définies, SMTP sinon."""
from __future__ import annotations

import base64
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests


def _access_token(client_id: str, client_secret: str, refresh_token: str) -> str:
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _send_via_api(user: str, to_addr: str, msg) -> None:
    client_id = os.environ.get("GMAIL_OAUTH_CLIENT_ID", "")
    client_secret = os.environ.get("GMAIL_OAUTH_CLIENT_SECRET", "")
    refresh_token = os.environ.get("GMAIL_OAUTH_REFRESH_TOKEN", "")
    token = _access_token(client_id, client_secret, refresh_token)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    resp = requests.post(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
        headers={"Authorization": f"Bearer {token}"},
        json={"raw": raw},
        timeout=30,
    )
    resp.raise_for_status()


def send_html(smtp_cfg: dict, to_addr: str, subject: str, html: str):
    user, password = smtp_cfg.get("user"), smtp_cfg.get("password")
    if not user or not password:
        raise RuntimeError(
            "SMTP non configuré: définir GMAIL_USER et GMAIL_APP_PASSWORD dans .env"
        )
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Find My Home <{user}>"
    msg["To"] = to_addr
    msg.attach(MIMEText(html, "html", "utf-8"))

    if all(os.environ.get(v) for v in ("GMAIL_OAUTH_CLIENT_ID", "GMAIL_OAUTH_CLIENT_SECRET", "GMAIL_OAUTH_REFRESH_TOKEN")):
        _send_via_api(user, to_addr, msg)
    else:
        with smtplib.SMTP_SSL(smtp_cfg["host"], int(smtp_cfg["port"]), timeout=30) as server:
            server.login(user, password)
            server.sendmail(user, [to_addr], msg.as_string())
