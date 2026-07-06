# Find My Home 🏠

Outil de veille locative automatisée. Scrape les annonces immobilières (Bien'ici), les filtre sur des critères objectifs, les score via LLM selon des préférences en texte libre, puis envoie un rapport par email — sans jamais reproposer une annonce déjà vue.

---

## Tu veux juste recevoir les annonces ?

La façon la plus simple : remplis ce formulaire → [tally.so/r/J9Y0GJ](https://tally.so/r/J9Y0GJ)

Indique ton email, ton budget, ta surface, tes critères éliminatoires et ce qui compte pour toi — je m'occupe du reste. Tu recevras ton rapport chaque semaine sans rien installer.

---

## Tu veux faire tourner ta propre instance ?

### Installation

```bash
git clone https://github.com/maximejacquart/find-my-home
cd find-my-home
pip install -r requirements.txt
```

### Configuration

**1. Crée ton profil** :

```bash
cp config/users/max.yaml config/users/prenom.yaml
```

Remplis ton email, ton budget, ta surface, et en texte libre ce que tu cherches.

**2. Configure les variables d'environnement** dans un fichier `.env` à la racine :

```
GMAIL_USER=ton@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
GMAIL_OAUTH_CLIENT_ID=...
GMAIL_OAUTH_CLIENT_SECRET=...
GMAIL_OAUTH_REFRESH_TOKEN=...
AI_API_KEY=...
```

Le scoring fonctionne avec n'importe quelle clé API de modèle IA (Anthropic, OpenAI, etc.) ou n'importe quel outil agentique CLI (Claude Code, Cursor, Codex…). Modifie `findmyhome/scoring.py` selon ton setup.

> **Besoin d'aide pour l'installation ?**
> Copiez le texte ci-dessous et collez-le dans votre assistant IA (Claude, ChatGPT…) avec le fichier [SETUP.md](SETUP.md) en pièce jointe — il vous guidera pas à pas.
>
> ```
> Je veux configurer le projet Find My Home pour envoyer des rapports d'annonces immobilières par email. Lis le fichier SETUP.md joint et guide-moi étape par étape pour : créer mon fichier de profil, configurer les variables d'environnement Gmail OAuth, et lancer mon premier rapport.
> ```

### Utilisation

```bash
python -m findmyhome run --all-users               # rapport + email pour tout le monde
python -m findmyhome run --user prenom             # juste une personne
python -m findmyhome run --user prenom --no-email  # rapport HTML sans envoyer
```

### Annonces sauvegardées

```bash
python -m findmyhome save <id> --user prenom
python -m findmyhome save <id> --user prenom --note "à visiter en priorité"
python -m findmyhome saved --user prenom
```

### Mail de candidature

```bash
python -m findmyhome apply <id> --user prenom
```

---

## Comment ça marche

```
Bien'ici API ──▶ Filtres durs ──▶ Scoring LLM ──▶ Rapport HTML ──▶ Email
 (scraping)      (prix, surface,   (Claude, lit    (top N annonces   (Gmail)
                  pièces, ville)    la description   avec verdict)
                                    vs tes critères)
```

1. **Collecte** — interroge l'API publique JSON de Bien'ici (pas de clé requise), normalise chaque annonce, stocke en SQLite pour ne rien scraper deux fois.
2. **Filtres durs** — élimine sur des critères objectifs (budget, surface, meublé/non meublé, villes) avant de payer le moindre appel LLM.
3. **Scoring** — chaque annonce restante passe devant un LLM (Claude) avec tes préférences en texte libre ("proche tram, lumineux, évite rdc..."). Renvoie un score 0-100, un verdict en une phrase, et les critères invérifiables depuis l'annonce.
4. **Rapport** — génère une page HTML avec le top N annonces triées par score, et l'envoie par email via Gmail.
5. **Suivi** — une annonce déjà envoyée n'est plus reproposée. Tu peux aussi sauvegarder une annonce (`fmh save`) ou générer un brouillon de mail de candidature personnalisé (`fmh apply`), qui relit l'annonce pour éviter un mail générique.

## Stack

- Python, argparse (CLI)
- SQLite (persistance, pas de serveur DB)
- Requêtes HTTP directes vers l'API Bien'ici
- LLM (Claude, ou n'importe quel modèle — voir `scoring.py`) pour le scoring et la génération des mails
- SMTP Gmail pour l'envoi
