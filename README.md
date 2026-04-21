# Scientific Dashboard – Chemistry & Mechanical Engineering

This project is a browser-based scientific dashboard featuring interactive 3D-style visual models, centered on Carbon-12 and related scientific systems.

## Included models

- Carbon-12 atom (6 protons, 6 neutrons, 6 electrons)
- Carbon-13 atom (6 protons, 7 neutrons, 6 electrons)
- Methane molecule (CH4 tetrahedral bonding)
- Planetary gear train model
- Axial turbine stage model

## Prerequisites

- Node.js ≥ 20

## Install dependencies

```bash
npm install
```

## Develop

```bash
npm run dev
```

Opens a local dev server at `http://localhost:5173/rag7/` with hot-module replacement.

## Build

```bash
npm run build
```

Produces an optimised, hashed bundle in `dist/`. Serve `dist/` for production or
deploy it to GitHub Pages at `https://<username>.github.io/rag7/`.

## Preview production build locally

```bash
npm run preview
```

Serves `dist/` at `http://localhost:4173/rag7/`.

## Project structure

```
rag7/
├── index.html           # Dashboard HTML (Vite entry point)
├── src/
│   ├── app.js           # Model rendering + interaction (ES module)
│   └── style.css        # Dashboard styles with dark/light themes
├── public/
│   ├── manifest.json    # PWA manifest
│   └── sw.js            # Service worker (lazy-cache strategy)
├── dist/                # Production build output (git-ignored)
├── vite.config.js       # Vite configuration (base: /rag7/)
└── package.json
```

