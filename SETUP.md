# Setup Find My Home

Ce fichier est un guide de configuration. Tu peux le donner à Claude ou un autre assistant pour qu'il te guide étape par étape.

---

## Ce qu'il faut configurer

1. Un fichier `.env` à la racine du projet avec les variables ci-dessous
2. Un fichier de profil dans `config/users/`

---

## Variables d'environnement (fichier `.env`)

### Envoi des emails — Gmail

```
GMAIL_USER=ton@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
GMAIL_OAUTH_CLIENT_ID=...
GMAIL_OAUTH_CLIENT_SECRET=...
GMAIL_OAUTH_REFRESH_TOKEN=...
```

**GMAIL_APP_PASSWORD** : va sur [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords), crée un mot de passe d'application pour "Mail". Nécessite la validation en 2 étapes activée.

**GMAIL_OAUTH_CLIENT_ID / CLIENT_SECRET** :
1. Va sur [console.cloud.google.com](https://console.cloud.google.com)
2. Crée un projet (ou utilise un existant)
3. Active l'API Gmail : menu > APIs & Services > Library > cherche "Gmail API" > Enable
4. Crée des identifiants : APIs & Services > Credentials > Create Credentials > OAuth client ID
5. Type : **Application de bureau** — donne un nom quelconque
6. Tu récupères le Client ID et le Client Secret

**GMAIL_OAUTH_REFRESH_TOKEN** :
1. Dans APIs & Services > OAuth consent screen, vérifie que ton email est dans les "Test users"
2. Ouvre cette URL dans ton navigateur (remplace CLIENT_ID par ta valeur) :
```
https://accounts.google.com/o/oauth2/auth?client_id=CLIENT_ID&redirect_uri=http://localhost&scope=https://www.googleapis.com/auth/gmail.send&response_type=code&access_type=offline&prompt=consent
```
3. Autorise l'accès — ton navigateur va tenter d'aller sur `http://localhost` (ça n'ouvrira rien, c'est normal)
4. Copie l'URL complète de la barre d'adresse et donne-la à Claude
5. Claude échange le code contre le refresh token et te donne la valeur à copier

### Scoring IA

```
ANTHROPIC_API_KEY=sk-ant-...
```

Crée une clé sur [console.anthropic.com](https://console.anthropic.com). Sans cette clé, le scoring utilise l'application Claude si elle est installée.

---

## Profil utilisateur

Copie `config/users/max.yaml` en `config/users/tonprenom.yaml` et remplis :

- `email` : ton adresse email
- `filters` : budget max, surface min, nombre de pièces, villes
- `preferences` : en texte libre, ce que tu cherches — précise ce qui est **éliminatoire** et ce qui est un **plus**
- `profile` : ta situation (utilisé pour générer les mails de candidature)

---

## Lancer

```bash
pip install -r requirements.txt
python -m findmyhome run --user tonprenom
```
