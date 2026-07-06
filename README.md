# Find My Home 🏠

Veille locative automatisée sur Bordeaux. Collecte les annonces de Bien'ici, les score selon tes critères grâce à l'IA, et envoie un rapport hebdomadaire par email — sans jamais renvoyer une annonce déjà vue.

## Installation

```bash
git clone https://github.com/maximejacquart/find-my-home
cd find-my-home
pip install -r requirements.txt
```

## Configuration

**1. Crée ton profil** en copiant le fichier d'un utilisateur existant :

```bash
cp config/users/max.yaml config/users/prenom.yaml
```

Remplis ton email, ton budget, ta surface, et en texte libre ce que tu cherches (quartiers, critères éliminatoires, ce qui compte pour toi).

**2. Configure les variables d'environnement** dans un fichier `.env` à la racine :

```
GMAIL_USER=ton@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
GMAIL_OAUTH_CLIENT_ID=...
GMAIL_OAUTH_CLIENT_SECRET=...
GMAIL_OAUTH_REFRESH_TOKEN=...
ANTHROPIC_API_KEY=...
```

Pour `GMAIL_APP_PASSWORD` : [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (nécessite la validation en 2 étapes).

Pour les variables `GMAIL_OAUTH_*` : crée un projet sur [console.cloud.google.com](https://console.cloud.google.com), active l'API Gmail, crée des identifiants OAuth "Application de bureau", puis lance le flow d'autorisation pour obtenir le refresh token.

Pour `ANTHROPIC_API_KEY` : [console.anthropic.com](https://console.anthropic.com).

## Utilisation

```bash
python -m findmyhome run --all-users               # rapport + email pour tout le monde
python -m findmyhome run --user prenom             # juste une personne
python -m findmyhome run --user prenom --no-email  # rapport HTML sans envoyer
```

Le rapport est aussi écrit dans `out/report-prenom.html`.

## Annonces sauvegardées

```bash
python -m findmyhome save <id> --user prenom
python -m findmyhome save <id> --user prenom --note "à visiter en priorité"
python -m findmyhome saved --user prenom
```

## Mail de candidature

```bash
python -m findmyhome apply <id> --user prenom
```

Génère un mail de candidature personnalisé à partir de ton profil et de l'annonce.
