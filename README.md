# Stacey Williams – Digital Business Card PWA

A Progressive Web App (PWA) digital business card for **Stacey Williams**, Certified Service Technician at Mercedes-Benz of Collierville.

## Features

- 📇 One-tap phone, email, maps, and website links
- 📋 Clipboard copy for phone & email
- 📥 Download vCard (`.vcf`) contact file
- 🔗 Web Share API (native share sheet on mobile)
- 🌗 Light / dark theme toggle (persisted to `localStorage`)
- 📱 Installable PWA with offline shell support
- 🤖 AI assistant with local FAQ fallback (optional server for live LLM)

---

## Running locally

No build step required. Serve the repo root over HTTPS (required for Service Worker and Clipboard API):

```bash
# Using the built-in Python server (HTTP only – SW won't register)
python3 -m http.server 8080

# Recommended: use a tool that supports HTTPS / proper headers
npx serve .
# or
npx http-server . -p 8080 --cors
```

Then open `http://localhost:8080/rag7/` (note the `/rag7/` base path which matches the GitHub Pages project-site URL).

---

## Deploying to GitHub Pages

1. Push to the `main` branch (or configure your GitHub Pages source branch).
2. In **Settings → Pages**, set the source to the branch root.
3. The site will be available at `https://<username>.github.io/rag7/`.

The service worker and manifest are already configured for the `/rag7/` base path.

---

## Enabling the AI assistant (optional)

The chat panel works in **local FAQ mode** by default – no server or API key needed.

To enable a live LLM (OpenAI-powered), deploy the included Netlify function:

### Deploy to Netlify

1. Import the repo into Netlify (or use the CLI).
2. In **Site settings → Environment variables**, add:
   - `OPENAI_API_KEY` – your OpenAI secret key (never commit this!)
   - `OPENAI_MODEL` – optional, defaults to `gpt-4o-mini`
3. Netlify will auto-deploy the function from `server/netlify/functions/chat.js`.
4. Your function endpoint will be:
   ```
   https://<your-site>.netlify.app/.netlify/functions/chat
   ```
5. Add a `<meta>` tag inside `<head>` in `index.html` to point the front end at it:
   ```html
   <meta name="chat-endpoint" content="https://<your-site>.netlify.app/.netlify/functions/chat">
   ```

> **Security note**: The API key is only used server-side inside the Netlify function. It is **never** exposed to the browser or committed to the repository. See [SECURITY.md](SECURITY.md) for the full policy.

### Local development of the server

```bash
cd server
cp ../.env.example .env   # fill in your OPENAI_API_KEY
npm install -g netlify-cli
netlify dev               # starts the function on http://localhost:8888
```

---

## Environment variables reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | ✅ (server only) | – | OpenAI secret key |
| `OPENAI_MODEL` | ❌ | `gpt-4o-mini` | OpenAI chat model |

See `.env.example` for a template.

---

## Project structure

This repository contains **three independent layers**:

### 1 · PWA digital business card (repo root)

```
rag7/
├── index.html          # Main PWA page
├── style.css           # All styles (dark + light theme)
├── app.js              # Core interactivity (clipboard, share, theme, install)
├── vcard.js            # vCard download helper
├── chat-ui.js          # AI assistant chat panel
├── sw.js               # Service worker (cache + offline fallback)
├── manifest.json       # PWA manifest
├── .env.example        # Server env-var template
├── .gitignore
├── README.md
├── SECURITY.md
└── server/
    └── netlify/
        └── functions/
            └── chat.js # Serverless AI proxy (Netlify)
```

### 2 · Advanced Python robotics / AGI package (`robot_agi/`)

```
robot_agi/
├── advanced/           # Core Python library (14 capability sub-packages)
├── config/             # Feature flags & hyperparameter defaults (YAML)
└── tests/              # Full unittest suite – run with:
                        #   python3 -m unittest discover -s robot_agi/tests -v
```

See [`robot_agi/README.md`](robot_agi/README.md) for a full breakdown of every sub-package.

### 3 · Ingenium business intelligence system (`ingenium/`)

A two-hemisphere system — **Company Intelligence** (strategy, customer data,
goals, knowledge, brand) and **Agent** (research, create, outreach,
follow-up, optimize) — connected through one integration layer (CRM, web
builder, email, finance, analytics, calendar) so the brain can think,
connect, and execute. Run its tests with:

```bash
python3 -m unittest discover -s ingenium/tests -v
```

See [`ingenium/README.md`](ingenium/README.md) for the full architecture.
