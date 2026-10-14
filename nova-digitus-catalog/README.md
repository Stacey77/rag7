# Catalog generator (not published)

- `catalog_data.py`: every app, its buyer group, its public description, and whether it's marked "Most requested". Edit this to add, move or reword apps.
- `links.py`: `PUBLIC_URLS`, the public "Try it" addresses. Only apps listed there get a Try it button.
- `build.py`: rebuilds `../nova-digitus-site/apps/`.

Rebuild: `python3 nova-digitus-catalog/build.py`, then commit. The Netlify Action publishes on push to main.
