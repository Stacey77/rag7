"""Multi-workspace platform: manage several companies, each its own Ingenium.

A workspace is one company's Ingenium instance (edge + run history),
persisted to a JSON file on disk. The platform server exposes a REST API and
a web UI for creating workspaces, editing each one's company edge, running
objectives, and downloading a real campaign kit as a zip.

Stdlib-only. Nothing is sent to a live service; campaign kits are generated
locally (see ``campaign.py``).
"""
import io
import json
import logging
import re
import tempfile
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .campaign import export_campaign
from .core.brain import Ingenium

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "platform_static"
CONTENT_TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "application/javascript"}


def slugify(name: str) -> str:
    """Turn a display name into a filesystem-safe workspace id.

    Args:
        name: Human-entered workspace name.

    Returns:
        A lowercase hyphenated slug (alphanumerics and hyphens only).
    """
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    return slug[:60]


def _read_json_file(path: Path) -> dict:
    """Read and parse a workspace JSON file."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"workspace file '{path.name}' is corrupt") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"workspace file '{path.name}' is corrupt")
    return payload


def _write_json_file(path: Path, payload: dict) -> None:
    """Write JSON via temp file and atomically replace the target."""
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp") as tmp:
            temp_name = tmp.name
            json.dump(payload, tmp, indent=2)
            tmp.flush()
        Path(temp_name).replace(path)
    finally:
        if temp_name:
            tmp_path = Path(temp_name)
            if tmp_path.exists():
                tmp_path.unlink()


class WorkspaceStore:
    """Persists one Ingenium instance per named workspace under a data dir."""

    def __init__(self, data_dir: str | Path) -> None:
        """Initialize the store, creating the data directory if needed.

        Args:
            data_dir: Directory where per-workspace JSON files live.
        """
        self.dir = Path(data_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, slug: str) -> Path:
        # slug is already sanitized; re-sanitize defensively against traversal
        safe = slugify(slug)
        if not safe:
            raise ValueError("invalid workspace id")
        return self.dir / f"{safe}.json"

    def exists(self, slug: str) -> bool:
        """Return whether a workspace with this slug exists."""
        return self._path(slug).is_file()

    def create(self, name: str, seed: bool = False) -> dict:
        """Create a new, empty (or sample-seeded) workspace.

        Args:
            name: Display name; its slug becomes the workspace id.
            seed: If True, populate the shared sample company edge.

        Returns:
            The new workspace's metadata dict.

        Raises:
            ValueError: If the name is empty or the slug already exists.
        """
        slug = slugify(name)
        if not slug:
            raise ValueError("workspace name must contain letters or digits")
        if self.exists(slug):
            raise ValueError(f"workspace '{slug}' already exists")
        if seed:
            from .samples import sample_brain
            brain = sample_brain()
        else:
            brain = Ingenium()
        self._write(slug, name, brain)
        logger.info("Created workspace '%s'", slug)
        return self.meta(slug)

    def delete(self, slug: str) -> None:
        """Delete a workspace.

        Args:
            slug: Workspace id.

        Raises:
            KeyError: If the workspace does not exist.
        """
        path = self._path(slug)
        if not path.is_file():
            raise KeyError(slug)
        path.unlink()
        logger.info("Deleted workspace '%s'", slug)

    def rename(self, slug: str, new_name: str) -> dict:
        """Change a workspace's display name (its slug id is unchanged).

        Args:
            slug: Workspace id.
            new_name: New display name.

        Returns:
            The workspace's updated metadata.

        Raises:
            KeyError: If the workspace does not exist.
            ValueError: If the new name is empty.
        """
        if not new_name.strip():
            raise ValueError("workspace name must not be empty")
        path = self._path(slug)
        if not path.is_file():
            raise KeyError(slug)
        payload = _read_json_file(path)
        payload["name"] = new_name.strip()
        _write_json_file(path, payload)
        logger.info("Renamed workspace '%s' to '%s'", slug, new_name)
        return self.meta(slug)

    def load(self, slug: str) -> Ingenium:
        """Load the Ingenium instance for a workspace.

        Args:
            slug: Workspace id.

        Returns:
            The restored Ingenium instance.

        Raises:
            KeyError: If the workspace does not exist.
        """
        path = self._path(slug)
        if not path.is_file():
            raise KeyError(slug)
        payload = _read_json_file(path)
        state = payload.get("state")
        if not isinstance(state, dict):
            raise ValueError(f"workspace file '{path.name}' is corrupt")
        brain = Ingenium()
        brain.load_state(state)
        return brain

    def save(self, slug: str, brain: Ingenium) -> None:
        """Persist a workspace's Ingenium state, preserving its display name."""
        name = self._name_of(slug)
        self._write(slug, name, brain)

    def _write(self, slug: str, name: str, brain: Ingenium) -> None:
        _write_json_file(self._path(slug), {"name": name, "state": brain.state()})

    def _name_of(self, slug: str) -> str:
        path = self._path(slug)
        if path.is_file():
            return _read_json_file(path).get("name", slug)
        return slug

    def meta(self, slug: str) -> dict:
        """Return summary metadata for a workspace (slug, name, run count)."""
        payload = _read_json_file(self._path(slug))
        state = payload.get("state", {})
        if not isinstance(state, dict):
            state = {}
        history = state.get("history", [])
        if not isinstance(history, list):
            history = []
        return {"slug": slug, "name": payload.get("name", slug), "runs": len(history)}

    def list(self) -> list[dict]:
        """Return metadata for every workspace, sorted by name."""
        metas = [self.meta(p.stem) for p in self.dir.glob("*.json")]
        return sorted(metas, key=lambda m: m["name"].lower())


def _history_summary(brain: Ingenium) -> list[dict]:
    summary = []
    for run in brain.history:
        record = run if isinstance(run, dict) else {}
        pipeline = record.get("pipeline")
        if not isinstance(pipeline, dict):
            pipeline = {}
        optimize = pipeline.get("optimize")
        if not isinstance(optimize, dict):
            optimize = {}
        outreach = pipeline.get("outreach")
        if not isinstance(outreach, dict):
            outreach = {}
        sent = outreach.get("sent")
        if not isinstance(sent, list):
            sent = []
        summary.append({
            "objective": record.get("objective", ""),
            "recommendation": optimize.get("recommendation", ""),
            "reached": len(sent),
        })
    return summary


def make_handler(store: WorkspaceStore) -> type:
    """Bind a WorkspaceStore to a request handler class."""

    class PlatformHandler(BaseHTTPRequestHandler):
        """Serves the platform UI and its workspace REST API."""

        # -- helpers ---------------------------------------------------------
        def _json(self, status: int, payload) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _body(self) -> dict:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            return json.loads(raw or b"{}")

        def _static(self, path: str) -> None:
            relative = path.lstrip("/") or "index.html"
            file_path = (STATIC_DIR / relative).resolve()
            if not file_path.is_relative_to(STATIC_DIR) or not file_path.is_file():
                self._json(404, {"error": "not found"})
                return
            data = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPES.get(file_path.suffix, "application/octet-stream"))
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _zip(self, filename: str, files: dict) -> None:
            buffer = io.BytesIO()
            with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for arcname, content in files.items():
                    zf.writestr(arcname, content)
            data = buffer.getvalue()
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        # -- routing ---------------------------------------------------------
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            parts = [p for p in parsed.path.split("/") if p]
            if parsed.path == "/api/workspaces":
                try:
                    listing = store.list()
                except ValueError as exc:
                    self._json(400, {"error": str(exc)})
                    return
                self._json(200, {"workspaces": listing})
                return
            if len(parts) >= 3 and parts[0] == "api" and parts[1] == "workspaces":
                slug = parts[2]
                if not store.exists(slug):
                    self._json(404, {"error": "no such workspace"})
                    return
                if len(parts) == 3:
                    try:
                        brain = store.load(slug)
                        meta = store.meta(slug)
                    except ValueError as exc:
                        self._json(400, {"error": str(exc)})
                        return
                    self._json(200, {
                        **meta,
                        "edge": brain.company_intelligence.snapshot(),
                        "history": _history_summary(brain),
                    })
                    return
                if len(parts) == 4 and parts[3] == "campaign.zip":
                    objective = (parse_qs(parsed.query).get("objective", [""])[0]).strip()
                    if not objective:
                        self._json(400, {"error": "objective is required"})
                        return
                    try:
                        self._export_zip(slug, objective)
                    except ValueError as exc:
                        self._json(400, {"error": str(exc)})
                    return
            self._static(parsed.path)

        def do_POST(self) -> None:
            parts = [p for p in urlparse(self.path).path.split("/") if p]
            if self.path == "/api/workspaces":
                try:
                    body = self._body()
                    meta = store.create(str(body.get("name", "")), seed=bool(body.get("seed")))
                except (ValueError, json.JSONDecodeError) as exc:
                    self._json(400, {"error": str(exc)})
                    return
                self._json(201, meta)
                return
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "workspaces" and parts[3] == "execute":
                slug = parts[2]
                if not store.exists(slug):
                    self._json(404, {"error": "no such workspace"})
                    return
                objective = str(self._body().get("objective", "")).strip()
                if not objective:
                    self._json(400, {"error": "objective is required"})
                    return
                try:
                    brain = store.load(slug)
                    report = brain.execute(objective)
                    store.save(slug, brain)
                except ValueError as exc:
                    self._json(400, {"error": str(exc)})
                    return
                self._json(200, report)
                return
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "workspaces" and parts[3] == "rename":
                slug = parts[2]
                if not store.exists(slug):
                    self._json(404, {"error": "no such workspace"})
                    return
                try:
                    meta = store.rename(slug, str(self._body().get("name", "")))
                except ValueError as exc:
                    self._json(400, {"error": str(exc)})
                    return
                self._json(200, meta)
                return
            self._json(404, {"error": "not found"})

        def do_DELETE(self) -> None:
            parts = [p for p in urlparse(self.path).path.split("/") if p]
            if len(parts) == 3 and parts[0] == "api" and parts[1] == "workspaces":
                slug = parts[2]
                if not store.exists(slug):
                    self._json(404, {"error": "no such workspace"})
                    return
                store.delete(slug)
                self._json(200, {"deleted": slug})
                return
            self._json(404, {"error": "not found"})

        def do_PUT(self) -> None:
            parts = [p for p in urlparse(self.path).path.split("/") if p]
            if len(parts) == 4 and parts[0] == "api" and parts[1] == "workspaces" and parts[3] == "edge":
                slug = parts[2]
                if not store.exists(slug):
                    self._json(404, {"error": "no such workspace"})
                    return
                try:
                    edge = self._body().get("edge", {})
                    brain = store.load(slug)
                except (json.JSONDecodeError, ValueError) as exc:
                    self._json(400, {"error": str(exc)})
                    return
                brain.company_intelligence.restore(edge)
                store.save(slug, brain)
                self._json(200, {"edge": brain.company_intelligence.snapshot()})
                return
            self._json(404, {"error": "not found"})

        def _export_zip(self, slug: str, objective: str) -> None:
            # Export against a transient copy so the stored history is untouched.
            brain = store.load(slug)
            report = brain.execute(objective)
            with tempfile.TemporaryDirectory() as tmp:
                written = export_campaign(report, tmp)
                files = {}
                base = Path(tmp)
                for path in written.values():
                    files[str(Path(path).relative_to(base))] = Path(path).read_text(encoding="utf-8")
            self._zip(f"{slugify(objective) or 'campaign'}.zip", files)

        def log_message(self, format: str, *args) -> None:
            logger.info("%s - %s", self.address_string(), format % args)

    return PlatformHandler


def make_server(host: str = "0.0.0.0", port: int = 8000, data_dir: str | Path = "ingenium_data") -> ThreadingHTTPServer:
    """Build (but do not start) the platform server.

    Args:
        host: Interface to bind.
        port: Port to listen on (0 lets the OS choose).
        data_dir: Directory workspaces are persisted under.

    Returns:
        A ThreadingHTTPServer ready for ``serve_forever()``.
    """
    return ThreadingHTTPServer((host, port), make_handler(WorkspaceStore(data_dir)))


def run(host: str = "0.0.0.0", port: int = 8000, data_dir: str | Path = "ingenium_data") -> None:
    """Start the platform server and serve until interrupted."""
    server = make_server(host, port, data_dir)
    logger.info("Ingenium platform on http://%s:%d (data: %s)", host, port, data_dir)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
