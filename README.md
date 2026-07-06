# Find My Home 🏠

Veille locative automatisée sur Bordeaux. Collecte les annonces de Bien'ici, les score selon tes critères grâce à l'IA, et envoie un rapport hebdomadaire par email — sans jamais renvoyer une annonce déjà vue.

---

## Tu veux juste recevoir les annonces ?

La façon la plus simple : envoie-moi tes critères (budget, surface, quartiers, ce que tu cherches) et ton email — je m'occupe du reste. Tu recevras ton rapport chaque semaine sans rien installer.

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
ANTHROPIC_API_KEY=...
```

> La config Gmail OAuth est un peu technique. Colle le fichier [SETUP.md](SETUP.md) dans ChatGPT, Claude ou n'importe quel assistant IA — il te guidera pas à pas.

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
