"""Stdlib-only HTTP server exposing Ingenium as an HTML dashboard."""
import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ..core.brain import Ingenium

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css",
    ".js": "application/javascript",
}


def build_demo_brain() -> Ingenium:
    """Construct an Ingenium pre-populated with a sample company edge.

    Returns:
        An Ingenium instance ready to execute objectives against out of the box.
    """
    brain = Ingenium()
    ci = brain.company_intelligence
    ci.strategy.set_positioning("AI ops partner for local service businesses")
    ci.strategy.add_priority("book more jobs", rank=1)
    ci.customer_data.upsert_record("cust-1", {"email": "lead@example.com", "stage": "new"})
    ci.goals.set_goal("Q3 new clients", target=10, current=3)
    ci.knowledge.add("offers", "Fall tune-up special: $99")
    ci.brand.set_voice("direct, confident, no fluff", ["clear", "bold"])
    return brain


def make_handler(brain: Ingenium) -> type:
    """Bind an Ingenium instance to a request handler class.

    Args:
        brain: The Ingenium instance requests should read and act through.

    Returns:
        A BaseHTTPRequestHandler subclass wired to that instance.
    """

    class IngeniumHandler(BaseHTTPRequestHandler):
        """Serves the dashboard page and a small JSON API around `brain`."""

        def _send_json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _serve_static(self, request_path: str) -> None:
            relative = request_path.lstrip("/") or "index.html"
            file_path = (STATIC_DIR / relative).resolve()
            if not file_path.is_relative_to(STATIC_DIR) or not file_path.is_file():
                self._send_json(404, {"error": "not found"})
                return
            body = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPES.get(file_path.suffix, "application/octet-stream"))
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path == "/api/edge":
                self._send_json(200, brain.company_intelligence.snapshot())
                return
            self._serve_static(self.path)

        def do_POST(self) -> None:
            if self.path != "/api/execute":
                self._send_json(404, {"error": "not found"})
                return
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                self._send_json(400, {"error": "invalid JSON body"})
                return
            objective = str(data.get("objective", "")).strip()
            if not objective:
                self._send_json(400, {"error": "objective is required"})
                return
            logger.info("Executing objective via web GUI: %s", objective)
            self._send_json(200, brain.execute(objective))

        def log_message(self, format: str, *args) -> None:
            logger.info("%s - %s", self.address_string(), format % args)

    return IngeniumHandler


def make_server(host: str = "0.0.0.0", port: int = 8000, brain: Ingenium | None = None) -> ThreadingHTTPServer:
    """Build (but do not start) an Ingenium web GUI server.

    Args:
        host: Interface to bind to.
        port: Port to listen on. Pass 0 to let the OS assign a free port.
        brain: Ingenium instance to serve; a pre-populated demo brain if omitted.

    Returns:
        A ThreadingHTTPServer ready to have `serve_forever()` called on it.
    """
    return ThreadingHTTPServer((host, port), make_handler(brain or build_demo_brain()))


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    """Start the Ingenium web GUI and block serving requests until interrupted.

    Args:
        host: Interface to bind to.
        port: Port to listen on.
    """
    server = make_server(host, port)
    logger.info("Ingenium GUI listening on http://%s:%d", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
