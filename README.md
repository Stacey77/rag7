# BudgetAI – Smart Budgeting App

A React + TypeScript budgeting and bill-paying app with resilient Gemini AI features.

---

## Features

- **Dashboard** with spending stats, bills due soon, and AI-generated insights
- **AI Financial Advisor** – ask questions about your finances
- **Chat Widget** – floating chat assistant
- **Fallback Mode** – fully usable when AI is unavailable
- **Response Caching** – saves API calls and quota

---

## Quota Errors (429 / RESOURCE_EXHAUSTED)

When you see this error:

```
{"error":{"code":429,"message":"You exceeded your current quota...","status":"RESOURCE_EXHAUSTED"}}
```

It means your Gemini API key has hit its free-tier limit. The app will:

1. Show a friendly message explaining what happened
2. Display local (non-AI) insights computed directly from your data
3. Offer a **"Connect / Select API Key"** button if running in AI Studio

**How to fix it:**
- Wait for your quota to reset (usually 24 h for free tier)
- Upgrade your Gemini plan at [aistudio.google.com](https://aistudio.google.com/apikey)
- Use a different API key

---

## Response Caching

To reduce API calls and quota consumption, the app caches AI responses in `localStorage`:

| Cache key | TTL | Invalidated when |
|-----------|-----|-----------------|
| `dashboard-insights` | 12 hours | Transactions / bills / goals change |
| `advisor-{hash}` | 12 hours | Question + financial snapshot changes |

- Cache entries are keyed by a **fingerprint** of the input data. If your transactions or bills change materially, a fresh API call is made automatically.
- You can **clear the cache manually** via the "Clear AI Cache" button in the AI Advisor.

---

## Connecting / Selecting an API Key

1. Obtain a free Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).
2. Paste the key into the banner at the top of the app and click **Save Key**.
3. If running inside Google AI Studio, use the **Connect / Select API Key** button that appears on quota errors.

Your key is stored only in your browser's `localStorage` and never sent anywhere except to the Gemini API endpoint.

---

## Fallback Mode (No-AI Mode)

When AI is unavailable (quota exhausted, missing key, or offline) the app:

- Continues to load all pages without errors
- Replaces AI insight cards with **local insights** computed from your data:
  - Top spending categories (last 30 days)
  - Largest single expense
  - Bills due within the next 7 days
  - Savings rate
- Clearly indicates _why_ AI is unavailable and what to do
- Lets you **Disable AI features** permanently via the toggle in the header; this preference is persisted in `localStorage`

---

## Development

```bash
npm install
npm run dev        # start dev server
npm run build      # production build
npm test           # run unit tests
```

### Project structure

```
src/
├── services/
│   ├── aiErrors.ts       # Typed error classification
│   ├── aiCache.ts        # localStorage cache with TTL + fingerprinting
│   ├── geminiService.ts  # Gemini API client with retry + caching
│   └── localInsights.ts  # Local non-AI insight computation
├── components/
│   ├── Dashboard.tsx     # Dashboard with AI card + fallback
│   ├── AIAdvisor.tsx     # AI advisor + cache controls
│   ├── ChatWidget.tsx    # Floating chat widget
│   └── FallbackInsights.tsx  # No-AI fallback UI
├── types/
│   └── budget.ts         # Core data types
├── data/
│   └── mockBudget.ts     # Sample budget data
└── test/
    ├── aiErrors.test.ts  # Error classification tests
    └── aiCache.test.ts   # Cache + fingerprint tests
```
