# Ingenium

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![Dependencies: stdlib only](https://img.shields.io/badge/dependencies-stdlib--only-brightgreen)

**A two-hemisphere engine that turns what a company knows into what it does.**

Ingenium pairs a company's knowledge (strategy, customers, goals, knowledge,
brand) with an agent pipeline (research → create → outreach → follow-up →
optimize) and runs the second against the first to execute a business
objective end to end.

> **Scope.** Ingenium is a standalone Python package (`ingenium/`). It is
> completely independent of the two other layers in this repo — the PWA
> digital business card at the repo root and the `robot_agi/` package — and
> shares no code with them.

## Current state

- **Prototype, not production.** The architecture and control flow are
  complete and tested; the external integrations are not yet real.
- **Stubbed integrations, real deliverables.** The CRM/email/calendar
  adapters are in-memory (nothing is sent to a live service), but a run can
  export **real, usable files** — a landing page, outreach email copy, an
  importable `.ics` calendar, and an outreach CSV — via `ingenium campaign`.
- **State persists to disk.** The company edge and run history serialize to
  JSON via `save()` / `load()`; only the integration adapters are ephemeral
  (they reconnect fresh each run).
- **Stdlib-only.** No third-party dependencies. Runs on a plain Python 3.10+
  install (uses `str | None` union syntax and `Path.is_relative_to`).
- **Multi-workspace platform.** A web app (`ingenium platform`) that manages
  several companies at once, each with its own editable edge, persisted run
  history, and one-click campaign-kit download — all saved to disk.
- **Dashboards included.** A zero-setup single HTML file, a single-workspace
  served dashboard, and the multi-workspace platform.
- **Tests included.** 53 unit tests covering both hemispheres, the
  integration hub, the web layer, state persistence, the CLI, campaign asset
  generation, and the platform (store + full REST API).

## Quick start

From the repo root (no install step — it's stdlib-only):

```bash
# 1. Run the tests (expected to pass on a clean clone)
python3 -m unittest discover -s ingenium/tests -v

# 2. Run an objective and export a real, usable campaign kit to ./campaign
python3 -m ingenium campaign "Launch fall tune-up campaign" --demo --out ./campaign

# 3. Or launch the multi-workspace platform web app
python3 -m ingenium platform

# 4. Or run a one-shot sample cycle that prints a JSON report
python3 -m ingenium demo
```

Prefer no terminal at all? Open `ingenium/standalone.html` in any browser —
the whole loop runs client-side (see [HTML dashboard](#html-dashboard)).

### Prerequisites and setup

- **Python:** 3.10 or newer (the provided container uses `python:3.12-slim`).
- **Dependencies:** none beyond the Python standard library.
- **Packaging:** Ingenium is stdlib-only and structured as a package, but this
  repo ships no packaging metadata (`pyproject.toml` / `setup.py`) — run
  commands from the repo root, or otherwise put the repo root on `PYTHONPATH`.

## Command-line interface

`python3 -m ingenium <command>` drives the whole loop without writing Python:

```bash
# Run an objective against the built-in sample edge, printing a summary
python3 -m ingenium run "Launch fall tune-up campaign" --demo

# Persist across runs: loads the state file if it exists, saves back after.
# History accumulates, so the edge and past runs carry forward.
python3 -m ingenium run "Kickoff"     --demo --state state.json
python3 -m ingenium run "Follow-up"          --state state.json

# Export a real campaign kit (see "Campaign export" below)
python3 -m ingenium campaign "Launch fall tune-up campaign" --demo --out ./campaign

# Inspect a saved state (company edge + run history)
python3 -m ingenium show --state state.json

# Full JSON report instead of the summary
python3 -m ingenium run "Launch fall tune-up campaign" --demo --json

# Start a dashboard / the platform / print one sample cycle
python3 -m ingenium serve --port 8000                  # single-workspace dashboard
python3 -m ingenium platform --data-dir ./ingenium_data  # multi-workspace app
python3 -m ingenium demo
```

A bare `run` with no `--demo` and no existing `--state` runs against an empty
edge, which yields the `insufficient_data` recommendation — the CLI's way of
showing there's nothing to act on yet.

## Campaign export (the working MVP)

`ingenium campaign` runs an objective and writes a folder of **real,
ready-to-use marketing assets** generated locally from the company edge — no
API keys, no external calls, nothing sent on your behalf:

```bash
python3 -m ingenium campaign "Launch fall tune-up campaign" --demo --out ./campaign
```

produces:

```
campaign/
├── landing.html        # a real landing page (headline, positioning, offer, CTA)
├── emails/
│   └── 01-...txt       # outreach email copy (subject + body) per customer
├── followups.ics       # importable calendar file — one event per follow-up
├── outreach.csv        # every recipient, ready for a mail-merge or CRM import
└── report.json         # the full execute() report
```

Open `landing.html` in a browser, double-click `followups.ics` to add the
follow-ups to any calendar, and paste the email copy straight into your mail
client. `--state` works here too, so the edge and history carry across runs.
The content is templated from your strategy, brand voice, and knowledge —
swap a stubbed adapter for a real API (see [Extending](#extending-swapping-a-stub-for-a-real-api))
when you want Ingenium to send these itself instead of handing you the files.

## Platform (multi-workspace web app)

`ingenium platform` runs a web application that manages **several companies at
once** — each a separate workspace with its own company edge, run history, and
campaign kits, all persisted to disk under a data directory:

```bash
python3 -m ingenium platform --data-dir ./ingenium_data
# -> open http://localhost:8000
```

In the browser you can:

- **Create, rename, and delete workspaces** (optionally seeded with sample
  data) from the sidebar, and switch between them — each keeps its own state.
- **Edit the company edge** (positioning, customers, goal, offer, brand voice)
  and save it per workspace.
- **Run objectives** and watch the Agent stages execute; the run history
  accumulates per workspace.
- **Download a campaign kit** (the same landing page / emails / `.ics` / CSV
  as `ingenium campaign`) as a zip, straight from the browser.

Everything is stored as one JSON file per workspace in the data directory, so
it survives restarts. The REST API underneath (used by the UI, but callable
directly) is:

| Method & path | Purpose |
|---|---|
| `GET /api/workspaces` | list workspaces |
| `POST /api/workspaces` `{name, seed}` | create a workspace |
| `GET /api/workspaces/<slug>` | edge + run history for one workspace |
| `PUT /api/workspaces/<slug>/edge` `{edge}` | replace the company edge |
| `POST /api/workspaces/<slug>/execute` `{objective}` | run and persist |
| `POST /api/workspaces/<slug>/rename` `{name}` | rename (slug id unchanged) |
| `DELETE /api/workspaces/<slug>` | delete a workspace |
| `GET /api/workspaces/<slug>/campaign.zip?objective=…` | download a kit (does not alter stored history) |

## Concept

Ingenium has two hemispheres joined by a shared integration layer:

- **Company Intelligence** (the company's *edge*) — strategy, customer data,
  goals, knowledge, and brand. What the company knows about itself and its
  market.
- **Agent** (the *doing* side) — research, create, outreach, follow-up, and
  optimize. What acts on that knowledge.

Both read and write through one **integration layer** — CRM, web builder,
email, finance, analytics, and calendar — which is what lets the engine
**think** (build context from the edge), **connect** (wire up the
integrations), and **execute** (run the agent pipeline against both).

Take the objective **"Launch fall tune-up campaign."** The five agent stages
run in order, each acting through the integration layer:

| Stage | What it does for this objective |
|-------|----------------------------------|
| **Research** | Reads the CRM pipeline, analytics history, and strategic priorities to size up the segment and context. |
| **Create** | Drafts an on-brand asset (voice/tone from Brand, facts from Knowledge) and publishes it via the web builder. |
| **Outreach** | Emails the relevant customer segment and logs each touch in the CRM. |
| **Follow-up** | Schedules a calendar touchpoint for everyone reached. |
| **Optimize** | Reads analytics + finance results back and recommends whether to *scale* or gather more data — feeding the next cycle. |

```mermaid
flowchart LR
    subgraph CI["Company Intelligence (edge)"]
        strategy[Strategy]
        customers[Customer Data]
        goals[Goals]
        knowledge[Knowledge]
        brand[Brand]
    end

    subgraph Agent["Agent"]
        research[Research]
        create[Create]
        outreach[Outreach]
        followup[Follow-up]
        optimize[Optimize]
        research --> create --> outreach --> followup --> optimize
    end

    subgraph Hub["Integration Hub"]
        crm[CRM]
        web[Web Builder]
        email[Email]
        finance[Finance]
        analytics[Analytics]
        calendar[Calendar]
    end

    CI -- snapshot / edge --> Agent
    Agent -- reads + acts --> Hub
    Hub -- results feed back --> optimize
    optimize -. informs next cycle .-> CI
```

Under the hood, `Ingenium.execute()` is just those three verbs in sequence:
`think()` builds the edge snapshot, `connect()` wires the integrations, and
`AgentSide.execute_pipeline()` runs the five stages against them.

## Structure

```
ingenium/
├── core/                     # orchestration
│   ├── brain.py              #   Ingenium: think() / connect() / execute()
│   └── integration_hub.py    #   owns + connects the six integrations
├── company_intelligence/     # source-of-truth state — the company edge
├── agent/                    # the pipeline stages that act on the edge
├── integrations/             # adapters to external systems (stubbed today)
├── web/                      # single-workspace dashboard (HTTP server + static)
├── platform.py               # multi-workspace platform: store + REST server
├── platform_static/          #   platform web app (index.html, style.css, app.js)
├── standalone.html           # zero-dependency, client-side-only dashboard
├── cli.py                    # `python3 -m ingenium` command-line interface
├── __main__.py               # makes the package runnable with -m
├── campaign.py               # renders a run into real, exportable assets
├── samples.py                # the shared sample company edge
├── demo.py                   # one-shot sample cycle
└── tests/                    # test_brain, test_web, test_persistence, test_cli,
                              #   test_campaign, test_platform
```

Top-level responsibilities:

- **`company_intelligence/`** — holds and returns the company's state; each
  module (strategy, customer_data, goals, knowledge, brand) is a small store
  with a `snapshot()`.
- **`agent/`** — the five pipeline stages; each reads the edge and/or the
  previous stage's output and acts through the hub.
- **`integrations/`** — one adapter per external system, all behind a common
  `Integration` base class. This is the seam where real APIs plug in.
- **`core/`** — wires the two hemispheres to the hub and exposes the
  think/connect/execute entrypoints.

## Usage

```python
from ingenium import Ingenium

brain = Ingenium()

# Populate the company edge once.
brain.company_intelligence.strategy.set_positioning("AI ops partner for local service businesses")
brain.company_intelligence.customer_data.upsert_record("cust-1", {"email": "lead@example.com"})
brain.company_intelligence.brand.set_voice("direct, confident, no fluff", ["clear", "bold"])

# Think, connect, and execute against an objective.
report = brain.execute("Launch fall tune-up campaign")
```

`report` is a dict recording what the engine knew, connected to, and did:

```python
{
  "objective": "Launch fall tune-up campaign",
  "edge": { "strategy": {...}, "customer_data": {...}, "goals": {...},
            "knowledge": {...}, "brand": {...} },          # the snapshot used
  "integrations": { "crm": {"connected": True}, ... },     # all six
  "pipeline": {
    "research": {...}, "create": {...}, "outreach": {...},
    "follow_up": {...},
    "optimize": { "report": {"outreach_sent": 1},
                  "recommendation": "scale" },             # scale | insufficient_data
  },
}
```

Every `execute()` is also appended to `brain.history`.

### Persisting state

The company edge and run history serialize to a JSON file, so a session
survives a restart (the integration adapters are not persisted — they
reconnect fresh on the next `execute()`):

```python
brain.save("state.json")            # write edge + history to disk
brain = Ingenium.load("state.json")  # rebuild a brain from that file
report = brain.execute("Follow-up campaign")  # history continues from where it left off
```

## HTML dashboard

There are two ways to use the dashboard.

**Standalone file (no server, no Python).** `ingenium/standalone.html` is a
single self-contained file — the entire think → connect → execute loop is
ported to in-browser JavaScript. Open it in any browser (double-click it).
The Company Intelligence fields are editable, so you can change the strategy,
customers, goal, knowledge, and brand, type an objective, and watch the Agent
side run against it. Your edits and a run-history list are saved in the
browser (localStorage), so they survive a reload. Nothing is installed and
nothing leaves the page.

**Served dashboard (backed by the real Python package).** `ingenium/web/` is
a stdlib-only HTTP server that serves the same dashboard but runs the actual
`Ingenium` package server-side:

```bash
python3 -m ingenium serve
# -> open http://localhost:8000
# (python3 -m ingenium.web.server also works)
```

The underlying `Ingenium` instance is held in memory by the server process,
so state (CRM activity, sent emails, scheduled follow-ups, tracked analytics)
accumulates across runs, the same way the engine would in real use. It
exposes two JSON endpoints the dashboard's JS calls, which you can also hit
directly:

- `GET /api/edge` — the current company intelligence snapshot.
- `GET /api/history` — a summary of every run so far (objective,
  recommendation, number reached), shown as a Run history panel in the UI.
- `POST /api/execute` with `{"objective": "..."}` — runs the full pipeline
  and returns the same report shape as `Ingenium.execute()`.

## Testing

- **Prerequisites:** none beyond Python 3.10+. No packages to install; the
  tests are expected to pass on a clean clone.
- **Everything:** `python3 -m unittest discover -s ingenium/tests -v`
- **Core only (no dashboard):** `python3 -m unittest ingenium.tests.test_brain -v`
- **Persistence only:** `python3 -m unittest ingenium.tests.test_persistence -v`
- **CLI only:** `python3 -m unittest ingenium.tests.test_cli -v`
- **Campaign export only:** `python3 -m unittest ingenium.tests.test_campaign -v`
- **Platform only:** `python3 -m unittest ingenium.tests.test_platform -v` —
  binds a server on an ephemeral port and uses a temp data dir.
- **Web layer only:** `python3 -m unittest ingenium.tests.test_web -v` — this
  binds a server on an ephemeral port (`127.0.0.1:0`), so it needs local
  loopback networking.

## Running in a container (Podman / Rancher Desktop / Docker)

A `Containerfile` at the repo root packages `ingenium/` as a standalone
image with no dependencies beyond the Python standard library. Building it
also runs the full test suite — the build fails if a test fails.

```bash
# Podman (or Podman Desktop's embedded CLI, or Rancher Desktop set to the
# Podman/moby backend):
podman build -t ingenium -f Containerfile .
podman run --rm -p 8000:8000 ingenium
# -> open http://localhost:8000

# Docker works identically:
docker build -t ingenium -f Containerfile .
docker run --rm -p 8000:8000 ingenium
```

The default command runs the served dashboard (`ingenium.web.server`) on
port 8000. For the one-shot CLI report instead:

```bash
podman run --rm ingenium python3 -m ingenium demo
```

## Extending: swapping a stub for a real API

The whole point of the `integrations/` seam is to replace in-memory stubs
with real API clients without touching either hemisphere or the pipeline.
To add or wire up an integration:

1. **Implement the adapter.** Add or edit a module in `integrations/`
   subclassing `Integration` (`integrations/base.py`). Keep `connect()`'s
   contract — it must succeed before any action method runs — and preserve
   the existing method names/return shapes the pipeline stages already call
   (e.g. the CRM's `log_activity()` / `get_pipeline()`), so callers keep
   working unchanged. Swap only the internals for a real client.
2. **Register it** in `IntegrationHub` (`core/integration_hub.py`) under its
   name so `connect_all()` and `get(name)` reach it.
3. **Add tests** in `tests/` alongside `test_brain.py`. Follow the existing
   pattern: assert the adapter refuses actions before `connect()`, then that
   its methods return the shapes the pipeline expects. Prefer a fake/mock
   over live network calls so the suite stays hermetic and passes offline.

Because every stage talks to adapters only through that common interface,
a faithful replacement is a drop-in — the rest of Ingenium never has to know
whether it's talking to memory or a live service.
