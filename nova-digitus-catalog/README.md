# Catalog generator (not published)

- `catalog_data.py`: every app, its buyer group, its public description, and whether it's marked "Most requested". Edit this to add, move or reword apps.
- `links.py`: `PUBLIC_URLS`, the public "Try it" addresses. Only apps listed there get a Try it button.
- `build.py`: rebuilds `../nova-digitus-site/apps/`.

Rebuild: `python3 nova-digitus-catalog/build.py`, then commit. The Netlify Action publishes on push to main.

## Connected to the Obsidian vault

When `vault_apps.json` is present, it is the source of truth: the Wiki Brain on Stacey's PC exports every app whose Obsidian note (in `_Wiki/Nova Digitus HQ/Apps`) says `public: true`, with its `site_group`, `public_description`, `featured` and `try_url`, and pushes it here. Only those apps are published. `catalog_data.py` still supplies the group definitions, and it is the fallback when the file is absent.

On every push that touches this folder, the "Deploy Nova Digitus site" workflow runs `build.py`, commits the rebuilt pages to `main` (GitHub Pages) and deploys to Netlify. To show or hide an app, change `public:` in its note; nothing needs editing here.

## App Exchange apps not in the vault yet

`catalog_data.PORTFOLIO_EXTRA` holds 62 apps from the App Exchange portfolio that had no vault note yet (Oct 2026). `build.py` publishes them alongside the vault's public apps; a vault note with the same name always wins. Once each has its own vault note (`vault-app-notes.zip` contains ready-made notes for `_Wiki/Nova Digitus HQ/Apps`), they can be removed from this list. `build.py` also keeps the home page's app counts in step with the catalog.
