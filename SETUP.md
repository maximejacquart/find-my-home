# Setup Find My Home

Ce fichier est un guide de configuration. Il peut être fourni à Claude ou à un autre assistant IA pour un accompagnement étape par étape.

---

## Ce qu'il faut configurer

1. Un fichier `.env` à la racine du projet avec les variables ci-dessous
2. Un fichier de profil dans `config/users/`

---

## Variables d'environnement (fichier `.env`)

### Envoi des emails — Gmail

```
GMAIL_USER=adresse@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
GMAIL_OAUTH_CLIENT_ID=...
GMAIL_OAUTH_CLIENT_SECRET=...
GMAIL_OAUTH_REFRESH_TOKEN=...
```

**GMAIL_APP_PASSWORD** : sur [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords), créez un mot de passe d'application pour "Mail". Nécessite la validation en 2 étapes activée.

**GMAIL_OAUTH_CLIENT_ID / CLIENT_SECRET** :
1. Rendez-vous sur [console.cloud.google.com](https://console.cloud.google.com)
2. Créez un projet (ou utilisez un existant)
3. Activez l'API Gmail : menu > APIs & Services > Library > cherchez "Gmail API" > Enable
4. Créez des identifiants : APIs & Services > Credentials > Create Credentials > OAuth client ID
5. Type : **Application de bureau** — le nom importe peu
6. Récupérez le Client ID et le Client Secret

**GMAIL_OAUTH_REFRESH_TOKEN** :
1. Dans APIs & Services > OAuth consent screen, vérifiez que votre email figure dans les "Test users"
2. Ouvrez cette URL dans un navigateur (remplacez CLIENT_ID par votre valeur) :
```
https://accounts.google.com/o/oauth2/auth?client_id=CLIENT_ID&redirect_uri=http://localhost&scope=https://www.googleapis.com/auth/gmail.send&response_type=code&access_type=offline&prompt=consent
```
3. Autorisez l'accès — le navigateur va tenter d'aller sur `http://localhost` (rien ne s'ouvrira, c'est normal)
4. Copiez l'URL complète de la barre d'adresse et donnez-la à l'assistant
5. L'assistant échange le code contre le refresh token et fournit la valeur à copier

### Scoring IA

Plusieurs backends possibles, dont des gratuits sans carte bancaire. Un seul suffit.

**Mistral (gratuit, recommandé)** — clé sur [console.mistral.ai](https://console.mistral.ai) (plan « Experiment ») :

```
FMH_LLM_BASE_URL=https://api.mistral.ai/v1
FMH_LLM_API_KEY=...
FMH_LLM_MODEL=mistral-small-latest
```

**Groq (gratuit)** — clé sur [console.groq.com/keys](https://console.groq.com/keys) :

```
FMH_LLM_BASE_URL=https://api.groq.com/openai/v1
FMH_LLM_API_KEY=...
FMH_LLM_MODEL=llama-3.3-70b-versatile
```

**Ollama (local, sans clé)** — après `ollama pull <modèle>` :

```
FMH_LLM_BASE_URL=http://localhost:11434/v1
FMH_LLM_MODEL=<modèle>
```

Tout autre endpoint compatible OpenAI (`/chat/completions`) fonctionne de la même façon.

**Claude** — soit le CLI `claude` est installé (abonnement, détecté automatiquement, rien à configurer), soit une clé API facturée à l'usage :

```
ANTHROPIC_API_KEY=sk-ant-...
```

Clé sur [console.anthropic.com](https://console.anthropic.com). Ordre de priorité : `FMH_LLM_BASE_URL` > `ANTHROPIC_API_KEY` > CLI `claude`.

---

## Profil utilisateur

Copiez `config/users/max.yaml` en `config/users/prenom.yaml` et remplissez :

- `email` : adresse de réception des rapports
- `filters` : budget max, surface min, nombre de pièces, villes
- `preferences` : en texte libre, les critères recherchés — en précisant ce qui est **éliminatoire** et ce qui est un **plus**
- `profile` : situation personnelle (utilisé pour générer les mails de candidature)

---

## Lancer

```bash
pip install -r requirements.txt
python -m findmyhome run --user prenom
```
