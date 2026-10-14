"""Generate the public app catalog into the Nova Digitus site folder.

Run: python3 nova-digitus-catalog/build.py  -> rewrites nova-digitus-site/apps/*.html
Every "Book a demo" button opens the Discovery Call with the app name pre-filled (?app=...).
"""
import html, json, os, re
from urllib.parse import quote
from catalog_data import APPS, GROUPS
from links import public_try_url as try_url

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "nova-digitus-site")
OUT = os.path.join(SITE, "apps")
CAL = "https://cal.com/stacey-williams-5enqex/discovery-call"
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
"""

def head(title, desc):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Figtree:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/apps/catalog.css"></head><body><div class="wrap">
<header class="nav"><a class="logo" href="/">Nova Digitus Designs</a><nav><a href="/apps/">All apps</a><a href="/#pricing">Pricing</a><a class="btn" href="{CAL}" target="_blank" rel="noopener">Book a call</a></nav></header>"""

FOOT = """</div><footer><div class="wrap">© 2026 Nova Digitus Designs LLC</div></footer></body></html>"""

def try_btn(name):
    u = try_url(name)
    return f'<a class="btn sm line" href="{e(u)}" target="_blank" rel="noopener">Try it</a>' if u else ""

def app_card(a, show_group=False):
    name, gid, desc, featured = a
    g = next(x for x in GROUPS if x[0] == gid)
    tag = '<span class="tag">Most requested</span>' if featured else ""
    grp = f'<a class="grp" href="/apps/{gid}.html">{e(g[1])}</a>' if show_group else ""
    return f"""<article class="app">{tag}<h3>{e(name)}</h3><p>{e(desc)}</p>
<div class="row"><a class="btn sm" href="{e(book_url(name))}" target="_blank" rel="noopener">Book a demo</a>{try_btn(name)}{grp}</div></article>"""

def cta():
    return f"""<section><div class="cta"><div><h2>Don't see your problem here?</h2><p>Most clients come with a problem, not an app name. Bring it to a free 30-minute call and we'll tell you which app fits, or what a custom build would take.</p></div>
<a class="btn" href="{CAL}" target="_blank" rel="noopener">Book a free call</a></div></section>"""

# ---------- group pages
for gid, gname, who, blurb in GROUPS:
    apps = [a for a in APPS if a[1] == gid]
    apps.sort(key=lambda a: (not a[3], a[0].lower()))
    others = "".join(f'<a href="/apps/{g[0]}.html">{e(g[1])}</a>' for g in GROUPS if g[0] != gid)
    note = f'<p class="note">{e(DISCLAIMER[gid])}</p>' if gid in DISCLAIMER else ""
    page = head(f"{gname} | Nova Digitus Designs", f"{blurb} {len(apps)} AI apps from Nova Digitus Designs.") + f"""
<div class="crumb"><a href="/apps/">All apps</a> / {e(gname)}</div>
<div class="hero"><h1>{e(gname)}</h1><p class="lede">{e(who)} {e(blurb)} Pick an app and book a demo; the call is free and the app you chose comes with you.</p></div>
<section><h2>{len(apps)} apps</h2><p class="lede" style="font-size:1rem">Every demo is a live 30-minute call on your own use case.</p>
<div class="apps">{''.join(app_card(a) for a in apps)}</div>{note}</section>
{cta()}
<section><h2>Other groups</h2><div class="others" style="margin-top:12px">{others}</div></section>
""" + FOOT
    open(os.path.join(OUT, f"{gid}.html"), "w").write(page)

# ---------- catalog front door
doors = "".join(
    f'<a class="door" href="/apps/{gid}.html"><h3>{e(gname)}</h3><p>{e(who)}</p><span class="count">{sum(1 for a in APPS if a[1]==gid)} apps</span></a>'
    for gid, gname, who, blurb in GROUPS)
data = json.dumps([{"n": a[0], "g": a[1], "d": a[2], "f": a[3], "t": try_url(a[0])} for a in APPS]).replace("</", "<\\/")
groups_js = json.dumps({g[0]: g[1] for g in GROUPS})
total = len(APPS)
from links import PUBLIC_URLS
INTRO_TAIL = "Try an app yourself where you see a Try it button, or book a free 30-minute demo of any app." if PUBLIC_URLS else "Every app has its own demo button that books a free 30-minute call."
index = head("AI apps for every team | Nova Digitus Designs", f"Browse {total} AI apps by who they're for and book a free demo of any of them.") + f"""
<div class="hero"><h1>Find the AI app built for your team.</h1>
<p class="lede">{total} working apps, sorted by who they're for. Pick your group, or search by what you need done. {INTRO_TAIL}</p>
<form class="search" role="search" onsubmit="return false"><input id="q" type="search" placeholder="Try: network, credit, outreach, sound, robot" aria-label="Search apps"></form>
<div id="results" aria-live="polite"></div></div>
<section><h2>Browse by who it's for</h2><p class="lede" style="font-size:1rem">Send people straight to their group: each one has its own link.</p><div class="doors">{doors}</div></section>
{cta()}
<script>
const APPS={data}, GROUPS={groups_js}, CAL={json.dumps(CAL)};
const esc=s=>s.replace(/[&<>"']/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c]));
const box=document.getElementById('results');
document.getElementById('q').addEventListener('input',ev=>{{
  const q=ev.target.value.trim().toLowerCase();
  if(q.length<2){{box.innerHTML='';return;}}
  const words=q.split(/\\s+/);
  const hits=APPS.filter(a=>words.every(w=>(a.n+' '+a.d+' '+GROUPS[a.g]).toLowerCase().includes(w))).sort((x,y)=>(y.f-x.f)).slice(0,12);
  box.innerHTML=hits.length?'<div class="apps">'+hits.map(a=>`<article class="app"><h3>${{esc(a.n)}}</h3><p>${{esc(a.d)}}</p><div class="row"><a class="btn sm" target="_blank" rel="noopener" href="${{CAL}}?app=${{encodeURIComponent(a.n)}}">Book a demo</a>${{a.t?`<a class="btn sm line" target="_blank" rel="noopener" href="${{a.t}}">Try it</a>`:''}}<a class="grp" href="/apps/${{a.g}}.html">${{esc(GROUPS[a.g])}}</a></div></article>`).join('')+'</div>'
    :'<p class="empty">No app matches that yet. <a href="'+CAL+'" target="_blank" rel="noopener">Book a call</a> and describe the problem; it may be a quick custom build.</p>';
}});
</script>
""" + FOOT
open(os.path.join(OUT, "index.html"), "w").write(index)
open(os.path.join(OUT, "catalog.css"), "w").write(CSS)
print(f"built {len(GROUPS)} group pages + index, {total} apps")
