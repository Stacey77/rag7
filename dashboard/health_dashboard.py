"""
Web-based health monitoring dashboard for the Resolver Agent.

Provides a real-time view of all agent statuses, active alerts,
and system health metrics via a simple Flask web server.

Dependencies: flask (optional; falls back to a stub when unavailable)
"""

import json
import logging
import threading
import time
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from agents.resolver_agent import ResolverAgent

logger = logging.getLogger(__name__)

try:
    from flask import Flask, Response, jsonify, render_template

    _FLASK_AVAILABLE = True
except ImportError:
    _FLASK_AVAILABLE = False
    logger.warning("Flask not available; HealthDashboard will run in stub mode")


class HealthDashboard:
    """
    Real-time health monitoring dashboard.

    When Flask is available the dashboard serves:
      GET /             → HTML dashboard
      GET /api/health   → JSON health data
      GET /api/agents   → JSON per-agent data
      GET /api/alerts   → JSON active alerts

    When Flask is not installed the dashboard logs health data to the console.
    """

    def __init__(self, resolver_agent: "ResolverAgent", port: int = 8080):
        self.resolver = resolver_agent
        self.port = port
        self._app: Optional[Any] = None
        self._server_thread: Optional[threading.Thread] = None

        if _FLASK_AVAILABLE:
            self._app = self._create_flask_app()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def run(self, debug: bool = False) -> None:
        """Start the dashboard server (blocking when Flask is available)."""
        if _FLASK_AVAILABLE and self._app is not None:
            logger.info("Launching HealthDashboard on http://localhost:%d", self.port)
            self._app.run(host="0.0.0.0", port=self.port, debug=debug)
        else:
            logger.info("Flask unavailable – printing health data every 5 s")
            self._console_loop()

    def run_async(self) -> threading.Thread:
        """Start the dashboard server in a background daemon thread."""
        self._server_thread = threading.Thread(
            target=self.run, daemon=True, name="health-dashboard"
        )
        self._server_thread.start()
        return self._server_thread

    def get_health_data(self) -> Dict[str, Any]:
        """Return the current health data as a plain dict."""
        return self.resolver.assess_system_health()

    # ------------------------------------------------------------------ #
    # Flask application
    # ------------------------------------------------------------------ #

    def _create_flask_app(self) -> Any:
        """Create and configure the Flask application."""
        app = Flask(__name__, template_folder="templates", static_folder="static")

        @app.route("/")
        def index():
            health = self.get_health_data()
            return render_template("dashboard.html", health=health)

        @app.route("/api/health")
        def api_health():
            return jsonify(self.get_health_data())

        @app.route("/api/agents")
        def api_agents():
            health = self.get_health_data()
            return jsonify(health.get("agents", {}))

        @app.route("/api/alerts")
        def api_alerts():
            health = self.get_health_data()
            return jsonify(health.get("alerts", []))

        @app.route("/api/stream")
        def api_stream():
            """Server-Sent Events endpoint for real-time updates."""
            def generate():
                while True:
                    data = json.dumps(self.get_health_data())
                    yield f"data: {data}\n\n"
                    time.sleep(2)

            return Response(generate(), mimetype="text/event-stream")

        return app

    # ------------------------------------------------------------------ #
    # Console fallback
    # ------------------------------------------------------------------ #

    def _console_loop(self) -> None:
        """Print health data to the console when Flask is unavailable."""
        while True:
            health = self.get_health_data()
            logger.info("System health: %s", health.get("overall_status", "unknown"))
            for name, data in health.get("agents", {}).items():
                logger.info("  Agent '%s': %s", name, data.get("status", "unknown"))
            for alert in health.get("alerts", []):
                logger.warning("  ALERT: %s", alert.get("message", ""))
            time.sleep(5)
