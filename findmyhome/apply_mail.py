"""Generate a personalized application email for a listing, via LLM."""
from __future__ import annotations

from .models import Listing
from .scoring import _complete

PROMPT = """Rédige un email de candidature pour une location immobilière, en français, prêt à envoyer.

PROFIL DU CANDIDAT :
{profile}

ANNONCE :
{listing}

Consignes :
- Ton poli, direct, humain — pas pompeux, pas de flagornerie.
- Mentionne 1-2 détails PRÉCIS de l'annonce pour montrer que la candidature n'est pas générique.
- Mets en avant les éléments rassurants du profil (situation, revenus, garant) sans en inventer.
- Propose des disponibilités pour une visite.
- Termine par une formule de politesse simple.
- 120-180 mots maximum.

Réponds avec EXACTEMENT ce format :
OBJET: <objet du mail>
---
<corps du mail>"""


def generate(listing: Listing, user: dict) -> tuple[str, str]:
    """Returns (subject, body)."""
    profile = user.get("profile", "").strip() or "(profil non renseigné — reste générique mais sérieux)"
    raw = _complete(PROMPT.format(profile=profile, listing=listing.summary_for_llm()))
    subject, body = "Candidature location", raw.strip()
    if "---" in raw:
        head, _, tail = raw.partition("---")
        if "OBJET:" in head:
            subject = head.split("OBJET:", 1)[1].strip()
            body = tail.strip()
    return subject, body
