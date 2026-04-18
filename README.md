# Scientific Dashboard – Chemistry & Mechanical Engineering

This project is a browser-based scientific dashboard featuring interactive 3D-style visual models, centered on Carbon-12 and related scientific systems.

## Included models

- Carbon-12 atom (6 protons, 6 neutrons, 6 electrons)
- Carbon-13 atom (6 protons, 7 neutrons, 6 electrons)
- Methane molecule (CH4 tetrahedral bonding)
- Planetary gear train model
- Axial turbine stage model

## Run locally

No build step is required.

```bash
cd /home/runner/work/rag7/rag7
python3 -m http.server 8080
```

Open:

- `http://localhost:8080/` (local)
- `https://<username>.github.io/rag7/` (GitHub Pages project path)

## Files

- `/home/runner/work/rag7/rag7/index.html` – dashboard layout
- `/home/runner/work/rag7/rag7/style.css` – visual design and themes
- `/home/runner/work/rag7/rag7/app.js` – model rendering and interaction logic
