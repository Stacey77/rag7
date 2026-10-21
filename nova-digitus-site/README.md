# Nova Digitus Designs: public site and app catalog

Static site, no build step. Everything lives in this folder and doesn't touch the WellOff platform.

```
index.html          Home page: services, pricing, booking
apps/index.html     Catalog front door: search + 9 buyer groups
apps/<group>.html   One page per group (engineering, it, ai, operations, sales, wealth, health, culture, creative)
thanks.html         Shown after the contact form is sent
netlify.toml        Netlify settings
Dockerfile          Coolify / any Docker host (nginx)
nginx.conf          nginx settings used by the Dockerfile
```

Every app's **Book a demo** button opens the Cal.com Discovery Call with the app name filled in
(`cal.com/stacey-williams-5enqex/discovery-call?app=<name>`).

## Deploy option 1: Netlify (automatic from GitHub)

Pick one:

**A. GitHub Action (already in this repo):** `.github/workflows/deploy-nova-digitus-site.yml`
1. Create a token at app.netlify.com/user/applications ("New access token").
2. In GitHub: Stacey77/WellOff > Settings > Secrets and variables > Actions > New repository secret, named `NETLIFY_AUTH_TOKEN`.
3. Every push to `main` that changes this folder publishes to **nova-digitus-designs-f0js.netlify.app**. You can also run it by hand from the Actions tab.

**Also live on GitHub Pages:** https://stacey77.github.io/rag7/nova-digitus-site/ (links are relative, so the site works at any address).

**B. Netlify's own Git connection:** in Netlify, open the project, go to Site configuration > Build & deploy > Link repository, choose `Stacey77/WellOff`, set the base directory to `nova-digitus-site` and the publish directory to `.`, and leave the build command empty.

**C. Drag and drop (no setup):** Netlify > project > Deploys, then drag this folder onto the page.

The contact form on the home page uses Netlify Forms, which is already turned on for the project.

## Deploy option 2: Coolify (self-hosted, open source)

1. In Coolify, go to Projects > New Resource > Application, then Private Repository (GitHub App) or Public Repository.
2. Repository: `Stacey77/WellOff`, branch `main`.
3. Base directory: `/nova-digitus-site`. Build pack: **Dockerfile**. Port: **80**.
4. Add your domain (for example `novadigitus.com`). Coolify issues the HTTPS certificate.
5. Turn on **Auto deploy** so each push to `main` redeploys.

Off Netlify (GitHub Pages, Coolify) the contact form opens the Discovery Call booking page with the visitor's name, email, app and message already filled in, so inquiries still arrive.
If you want the form on Coolify, point its `action` at your own form handler or an n8n webhook.

## Updating the catalog

The catalog is generated from the app list (`catalog_data.py` and `build.py` in the Nova Digitus workspace).
To give an app a **Try it** button, add its public address to `PUBLIC_URLS` in `links.py`, rebuild,
and copy the new `apps/` folder here.
