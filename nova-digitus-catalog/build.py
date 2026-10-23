"""Generate the public app catalog into the Nova Digitus site folder.

Run: python3 nova-digitus-catalog/build.py  -> rewrites nova-digitus-site/apps/*.html
Every "Book a demo" button opens the Discovery Call with the app name pre-filled (?app=...).
"""
import html, json, os, re
from urllib.parse import quote
from catalog_data import APPS, GROUPS, PORTFOLIO_EXTRA
from links import public_try_url as links_try_url

# 60-second teaser demos (demos.json) and the player that runs them, bundled into the site as demos.js
HERE = os.path.dirname(os.path.abspath(__file__))

# The Obsidian vault is the source of truth when vault_apps.json is present: the Wiki Brain on Stacey's PC
# exports every app whose note says `public: true`, and only those apps are published. Without the file,
# catalog_data.py is used as before.
VAULT_FILE = os.path.join(HERE, "vault_apps.json")
VAULT_URLS = {}
if os.path.exists(VAULT_FILE):
    _gids = {g[0] for g in GROUPS}
    _vault = json.load(open(VAULT_FILE, encoding="utf-8")).get("apps", [])
    APPS = [(a["name"], a["group"] if a.get("group") in _gids else "ai", a.get("description", ""), bool(a.get("featured")))
            for a in _vault if a.get("name")]
    VAULT_URLS = {a["name"]: a["try_url"] for a in _vault if str(a.get("try_url", "")).startswith("https://")}
    print(f"catalog source: Obsidian vault ({len(APPS)} public apps)")
# Portfolio apps not yet in the vault (see catalog_data.PORTFOLIO_EXTRA); a vault entry with the same name wins.
_have = {a[0].lower() for a in APPS}
_extra = [a for a in PORTFOLIO_EXTRA if a[0].lower() not in _have]
APPS = list(APPS) + _extra
if _extra:
    print(f"plus {len(_extra)} App Exchange portfolio apps not in the vault yet")


def try_url(name):
    return VAULT_URLS.get(name) or links_try_url(name)
DEMOS = json.load(open(os.path.join(HERE, "demos.json")))

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "nova-digitus-site")
OUT = os.path.join(SITE, "apps")
CAL = "https://cal.com/stacey-williams-5enqex/discovery-call"
# Canonical public URL (GitHub Pages serves the site from a subfolder). Used for canonical links + sitemap.xml only;
# every internal link stays relative so the site also works at domain root (Netlify/Coolify).
BASE = "https://stacey77.github.io/rag7/nova-digitus-site/"
FAVICON = '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 64 64%27%3E%3Crect width=%2764%27 height=%2764%27 rx=%2714%27 fill=%27%232F5BEA%27/%3E%3Cpath d=%27M19 47V17h6l14 19V17h6v30h-6L25 28v19z%27 fill=%27%23fff%27/%3E%3C/svg%3E">'
os.makedirs(OUT, exist_ok=True)
e = html.escape

def book_url(name):
    return f"{CAL}?app={quote(name)}"

DISCLAIMER = {
    "wealth": "These are planning, research and simulation tools. They are not financial, tax, legal or investment advice, and results depend on your own situation.",
    "health": "These are education and wellness tools. They are not medical advice and don't diagnose, treat or replace care from a licensed provider.",
}

CSS = """
:root{--bg:#F5F7FB;--panel:#fff;--ink:#13213D;--muted:#56627A;--line:#D8DEE8;--cobalt:#2F5BEA;--cobalt-deep:#1A3AAE;--soft:#E4EAFD;--amber:#E0A23A;
--display:"Bricolage Grotesque",system-ui,sans-serif;--body:"Figtree",system-ui,sans-serif}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 var(--body);-webkit-font-smoothing:antialiased}
a{color:var(--cobalt)}
:focus-visible{outline:3px solid var(--amber);outline-offset:2px}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
.nav{display:flex;justify-content:space-between;align-items:center;padding:20px 0;gap:16px}
.logo{font-family:var(--display);font-weight:800;font-size:1.15rem;text-decoration:none;color:var(--ink)}
.nav nav{display:flex;gap:22px;align-items:center}
.nav nav a{color:var(--muted);text-decoration:none;font-weight:500}
.btn{display:inline-block;background:var(--cobalt);color:#fff;border:0;padding:11px 18px;border-radius:9px;text-decoration:none;cursor:pointer;font:600 .98rem var(--body);white-space:nowrap}
.nav nav a.btn{color:#fff}
.btn:hover{background:var(--cobalt-deep)}
.btn.line{background:transparent;color:var(--ink);border:1.5px solid var(--ink)}
.btn.line:hover{background:var(--ink);color:#fff}
.btn.sm{padding:8px 14px;font-size:.9rem}
@media (max-width:720px){.nav nav a:not(.btn){display:none}}
.crumb{font-size:.9rem;color:var(--muted);margin-top:8px}
.crumb a{color:var(--muted)}
h1{font-family:var(--display);font-weight:800;font-size:clamp(2.3rem,5.6vw,4.2rem);line-height:.98;letter-spacing:-.035em;margin:14px 0 16px}
h2{font-family:var(--display);font-weight:700;font-size:clamp(1.5rem,3vw,2rem);letter-spacing:-.02em;margin:0 0 6px}
.lede{font-size:1.15rem;color:var(--muted);max-width:60ch;margin:0 0 26px}
section{padding:40px 0;border-top:1px solid var(--line)}
.hero{padding:36px 0 44px}
.search{display:flex;gap:10px;max-width:620px}
.search input{flex:1;font:inherit;padding:13px 14px;border:1.5px solid var(--line);border-radius:10px;background:var(--panel);color:var(--ink)}
.search input:focus{border-color:var(--cobalt);outline:none}
#results{margin-top:18px}
.doors{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.door{display:flex;flex-direction:column;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:22px;text-decoration:none;color:var(--ink);transition:border-color .15s}
.door:hover{border-color:var(--cobalt)}
.door h3{font-family:var(--display);font-size:1.3rem;margin:0 0 6px;letter-spacing:-.01em}
.door p{margin:0 0 14px;color:var(--muted);font-size:.95rem}
.door .count{margin-top:auto;font-weight:600;color:var(--cobalt-deep)}
@media (max-width:900px){.doors{grid-template-columns:repeat(2,1fr)}}
@media (max-width:600px){.doors{grid-template-columns:1fr}}
.apps{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:var(--line);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.app{background:var(--panel);padding:22px 24px;display:flex;flex-direction:column;gap:6px}
.app h3{font-family:var(--display);font-size:1.2rem;margin:0;letter-spacing:-.01em}
.app p{margin:0 0 10px;color:var(--muted)}
.app .row{margin-top:auto;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.tag{font-size:.78rem;font-weight:600;color:var(--cobalt-deep);background:var(--soft);padding:2px 9px;border-radius:999px;align-self:flex-start}
.grp{font-size:.85rem;color:var(--muted)}
.apps .app:last-child:nth-child(odd){grid-column:1/-1}
@media (max-width:720px){.apps{grid-template-columns:1fr}}
.note{font-size:.88rem;color:var(--muted);border-left:3px solid var(--line);padding-left:12px;margin:26px 0 0;max-width:70ch}
.cta{background:var(--ink);color:#fff;border-radius:16px;padding:34px;display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap}
.cta h2{color:#fff}
.cta p{margin:0;color:#C9D2E3;max-width:52ch}
.cta .btn{background:#fff;color:var(--ink)}
.others{display:flex;flex-wrap:wrap;gap:10px}
.others a{background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:7px 14px;text-decoration:none;color:var(--ink);font-size:.95rem}
.others a:hover{border-color:var(--cobalt)}
footer{padding:30px 0 44px;color:var(--muted);font-size:.9rem;border-top:1px solid var(--line);margin-top:30px}
.empty{color:var(--muted)}
.lede-sm{font-size:1rem}
.others.mt{margin-top:12px}
.vh{position:absolute!important;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
"""

def head(title, desc, path):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE}{path}">{FAVICON}
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Figtree:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="catalog.css"></head><body><div class="wrap">
<header class="nav"><a class="logo" href="../">Nova Digitus Designs</a><nav><a href="./">All apps</a><a href="../#pricing">Pricing</a><a class="btn" href="{CAL}" target="_blank" rel="noopener">Book a call</a></nav></header>
<main>"""

FOOT = """</main></div><script src="../demos.js" defer></script><footer><div class="wrap">© 2026 Nova Digitus Designs LLC</div></footer></body></html>"""

def try_btn(name):
    u = try_url(name)
    return f'<a class="btn sm line" href="{e(u)}" target="_blank" rel="noopener">Try it</a>' if u else ""

def demo_btn(name):
    return f'<button type="button" class="btn sm line" data-demo="{e(name)}">60-second demo</button>' if name in DEMOS else ""

def app_card(a, show_group=False):
    name, gid, desc, featured = a
    g = next(x for x in GROUPS if x[0] == gid)
    tag = '<span class="tag">Live: try it now</span>' if try_url(name) else ('<span class="tag">Most requested</span>' if featured else "")
    grp = f'<a class="grp" href="{gid}.html">{e(g[1])}</a>' if show_group else ""
    return f"""<article class="app">{tag}<h3>{e(name)}</h3><p>{e(desc)}</p>
<div class="row"><a class="btn sm" href="{e(book_url(name))}" target="_blank" rel="noopener">Book a demo</a>{demo_btn(name)}{try_btn(name)}{grp}</div></article>"""

def cta():
    return f"""<section><div class="cta"><div><h2>Don't see your problem here?</h2><p>Most clients come with a problem, not an app name. Bring it to a free 30-minute call and we'll tell you which app fits, or what a custom build would take.</p></div>
<a class="btn" href="{CAL}" target="_blank" rel="noopener">Book a free call</a></div></section>"""

# ---------- group pages
for gid, gname, who, blurb in GROUPS:
    apps = [a for a in APPS if a[1] == gid]
    apps.sort(key=lambda a: (not try_url(a[0]), not a[3], a[0].lower()))
    others = "".join(f'<a href="{g[0]}.html">{e(g[1])}</a>' for g in GROUPS if g[0] != gid)
    note = f'<p class="note">{e(DISCLAIMER[gid])}</p>' if gid in DISCLAIMER else ""
    page = head(f"{gname} | Nova Digitus Designs", f"{blurb} {len(apps)} AI apps from Nova Digitus Designs.", f"apps/{gid}.html") + f"""
<div class="crumb"><a href="./">All apps</a> / {e(gname)}</div>
<div class="hero"><h1>{e(gname)}</h1><p class="lede">{e(who)} {e(blurb)} Pick an app and book a demo; the call is free and the app you chose comes with you.</p></div>
<section><h2>{len(apps)} apps</h2><p class="lede lede-sm">Watch a 60-second demo where you see one, then book a free 30-minute call to see the app on your own use case.</p>
<div class="apps">{''.join(app_card(a) for a in apps)}</div>{note}</section>
{cta()}
<section><h2>Other groups</h2><div class="others mt">{others}</div></section>
""" + FOOT
    open(os.path.join(OUT, f"{gid}.html"), "w").write(page)

# ---------- catalog front door
doors = "".join(
    f'<a class="door" href="{gid}.html"><h3>{e(gname)}</h3><p>{e(who)}</p><span class="count">{sum(1 for a in APPS if a[1]==gid)} apps</span></a>'
    for gid, gname, who, blurb in GROUPS)
data = json.dumps([{"n": a[0], "g": a[1], "d": a[2], "f": a[3], "t": try_url(a[0]), "v": a[0] in DEMOS} for a in APPS]).replace("</", "<\\/")
groups_js = json.dumps({g[0]: g[1] for g in GROUPS})
total = len(APPS)
from links import PUBLIC_URLS
live = [a for a in APPS if try_url(a[0])]
spotlight = (f'<section><h2>Try it live</h2><p class="lede lede-sm">Open these in your browser right now, no call needed.</p><div class="apps">'
             + "".join(app_card(a, show_group=True) for a in live) + '</div></section>') if live else ""

INTRO_TAIL = "Try an app yourself where you see a Try it button, or book a free 30-minute demo of any app." if (PUBLIC_URLS or VAULT_URLS) else "Every app has its own demo button that books a free 30-minute call."
index = head("AI apps for every team | Nova Digitus Designs", f"Browse {total} AI apps by who they're for and book a free demo of any of them.", "apps/") + f"""
<div class="hero"><h1>Find the AI app built for your team.</h1>
<p class="lede">{total} working apps, sorted by who they're for. Pick your group, or search by what you need done. {INTRO_TAIL}</p>
<form class="search" role="search" onsubmit="return false"><input id="q" type="search" placeholder="Try: network, credit, outreach, sound, robot" aria-label="Search apps"><button type="submit" class="vh">Search</button></form>
<div id="results" aria-live="polite"></div></div>
{spotlight}
<section><h2>Browse by who it's for</h2><p class="lede lede-sm">Send people straight to their group: each one has its own link.</p><div class="doors">{doors}</div></section>
{cta()}
<script>
const APPS={data}, GROUPS={groups_js}, CAL={json.dumps(CAL)};
const esc=s=>s.replace(/[&<>"']/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c]));
const box=document.getElementById('results');
document.getElementById('q').addEventListener('input',ev=>{{
  const q=ev.target.value.trim().toLowerCase();
  if(q.length<2){{box.innerHTML='';return;}}
  const words=q.split(/\\s+/);
  const hits=APPS.filter(a=>words.every(w=>(a.n+' '+a.d+' '+GROUPS[a.g]).toLowerCase().includes(w))).sort((x,y)=>(!!y.t-!!x.t)||(y.f-x.f)).slice(0,12);
  box.innerHTML=hits.length?'<div class="apps">'+hits.map(a=>`<article class="app"><h3>${{esc(a.n)}}</h3><p>${{esc(a.d)}}</p><div class="row"><a class="btn sm" target="_blank" rel="noopener" href="${{CAL}}?app=${{encodeURIComponent(a.n)}}">Book a demo</a>${{a.v?`<button type="button" class="btn sm line" data-demo="${{esc(a.n)}}">60-second demo</button>`:''}}${{a.t?`<a class="btn sm line" target="_blank" rel="noopener" href="${{a.t}}">Try it</a>`:''}}<a class="grp" href="${{a.g}}.html">${{esc(GROUPS[a.g])}}</a></div></article>`).join('')+'</div>'
    :'<p class="empty">No app matches that yet. <a href="'+CAL+'" target="_blank" rel="noopener">Book a call</a> and describe the problem; it may be a quick custom build.</p>';
}});
</script>
""" + FOOT
open(os.path.join(OUT, "index.html"), "w").write(index)
open(os.path.join(OUT, "catalog.css"), "w").write(CSS)
# ---------- sitemap.xml (thanks.html and 404.html are intentionally left out)
urls = ["", "apps/"] + [f"apps/{g[0]}.html" for g in GROUPS]
with open(os.path.join(SITE, "sitemap.xml"), "w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    f.write("".join(f"  <url><loc>{BASE}{u}</loc></url>\n" for u in urls))
    f.write("</urlset>\n")
print(f"built {len(GROUPS)} group pages + index, {total} apps")

# ---------- demos.js for the whole site
missing = [n for n in DEMOS if n not in {a[0] for a in APPS}]
demo_data = {n: dict(d, url=try_url(n) or "") for n, d in DEMOS.items()}
with open(os.path.join(SITE, "demos.js"), "w") as f:
    f.write("window.ND_DEMOS=" + json.dumps(demo_data, ensure_ascii=False).replace("</", "<\\/") + ";\n")
    f.write(open(os.path.join(HERE, "demo_player.js")).read())
print(f"demos.js: {len(DEMOS)} demos" + (f" ({len(missing)} for apps outside the catalog: {', '.join(missing)})" if missing else ""))

# ---------- keep the home page's app counts in step with the catalog
_home = os.path.join(SITE, "index.html")
if os.path.exists(_home):
    _h = open(_home, encoding="utf-8").read()
    _h = re.sub(r'(<div class="count"><b>)\d+(</b>)', rf"\g<1>{total}\g<2>", _h)
    _h = re.sub(r"\b\d+ apps in nine groups", f"{total} apps in nine groups", _h)
    _h = re.sub(r"Search all \d+ apps", f"Search all {total} apps", _h)
    for _gid, *_ in GROUPS:
        _n = sum(1 for a in APPS if a[1] == _gid)
        _h = re.sub(rf'(href="apps/{_gid}\.html">[^<]*<span class="more">)\d+', rf"\g<1>{_n}", _h)
    open(_home, "w", encoding="utf-8").write(_h)
