"""HTML weekly report rendering."""
from __future__ import annotations

from datetime import date

from jinja2 import Template

from .models import Listing

TEMPLATE = Template("""\
<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f2ee;font-family:Georgia,'Times New Roman',serif;color:#2b2b2b;">
<div style="max-width:640px;margin:0 auto;padding:24px 16px;">

  <div style="border-bottom:3px solid #2b2b2b;padding-bottom:12px;margin-bottom:8px;">
    <div style="font-size:13px;letter-spacing:2px;text-transform:uppercase;color:#8a6d3b;">Find My Home · Bordeaux</div>
    <h1 style="margin:4px 0 0;font-size:26px;font-weight:normal;">Rapport hebdo — {{ date_str }}</h1>
  </div>

  <p style="font-size:14px;color:#555;margin:12px 0 24px;">
    {{ total_scanned }} annonces analysées cette semaine · {{ total_new }} nouvelles ·
    voici les {{ listings|length }} plus pertinentes pour <strong>{{ user_name }}</strong>.
  </p>

  {% for item in listings %}
  <div style="background:#fff;border:1px solid #ddd;border-radius:6px;margin-bottom:18px;overflow:hidden;">
    {% if item.listing.photos %}
    <img src="{{ item.listing.photos[0] }}" alt="" style="width:100%;max-height:260px;object-fit:cover;display:block;">
    {% endif %}
    <div style="padding:14px 18px;">
      <table width="100%" cellpadding="0" cellspacing="0"><tr>
        <td style="font-size:18px;font-weight:bold;">
          <a href="{{ item.listing.url }}" style="color:#2b2b2b;text-decoration:none;">{{ item.listing.title }}</a>
        </td>
        <td align="right" style="white-space:nowrap;">
          <span style="display:inline-block;background:{{ item.color }};color:#fff;border-radius:12px;padding:3px 10px;font-size:13px;font-family:Arial,sans-serif;font-weight:bold;">{{ item.score }}/100</span>
        </td>
      </tr></table>
      <div style="font-size:15px;margin:6px 0;color:#8a6d3b;font-weight:bold;">
        {{ item.listing.price|int if item.listing.price else '?' }} €/mois
        · {{ item.listing.rooms or '?' }} pièce(s)
        · {{ item.listing.surface|int if item.listing.surface else '?' }} m²
        · {{ item.listing.city }}{% if item.listing.district %} ({{ item.listing.district }}){% endif %}
      </div>
      <div style="font-size:14px;font-style:italic;color:#444;margin:8px 0;">« {{ item.verdict }} »</div>
      {% if item.flags %}
      <div style="font-size:12px;color:#a05a00;margin:6px 0;">⚠ À vérifier : {{ item.flags|join(' · ') }}</div>
      {% endif %}
      <div style="margin-top:10px;font-size:13px;font-family:Arial,sans-serif;">
        <a href="{{ item.listing.url }}" style="color:#8a6d3b;">Voir l'annonce ({{ item.listing.source }})</a>
        <span style="color:#bbb;"> | </span>
        <span style="color:#999;">Sauvegarder : <code style="background:#f0ede6;padding:1px 5px;border-radius:3px;">fmh save {{ item.short_id }}</code></span>
      </div>
    </div>
  </div>
  {% endfor %}

  {% if not listings %}
  <p style="text-align:center;color:#777;padding:40px 0;">Aucune annonce ne passe tes filtres cette semaine. Élargis peut-être les critères ?</p>
  {% endif %}

  <div style="border-top:1px solid #ccc;margin-top:24px;padding-top:12px;font-size:12px;color:#999;text-align:center;">
    Généré automatiquement par find-my-home · sources : {{ sources|join(', ') }}
  </div>
</div>
</body>
</html>
""")


def score_color(score: int) -> str:
    if score >= 85:
        return "#2e7d32"
    if score >= 70:
        return "#558b2f"
    if score >= 50:
        return "#b8860b"
    return "#a04040"


def render(user: dict, scored: list[tuple[Listing, dict]], total_scanned: int,
           total_new: int, sources: list[str]) -> str:
    items = [
        {
            "listing": listing,
            "score": s["score"],
            "verdict": s["verdict"],
            "flags": s.get("flags", []),
            "color": score_color(s["score"]),
            "short_id": listing.id.split(":", 1)[1][:18],
        }
        for listing, s in scored
    ]
    return TEMPLATE.render(
        date_str=date.today().strftime("%d/%m/%Y"),
        user_name=user.get("display_name", user["name"]),
        listings=items,
        total_scanned=total_scanned,
        total_new=total_new,
        sources=sources,
    )
