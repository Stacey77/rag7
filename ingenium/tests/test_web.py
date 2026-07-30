"""Tests for the Ingenium web GUI: static serving and the JSON API."""
import json
import os
import sys
import threading
import unittest
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ingenium import Ingenium
from ingenium.web.server import make_server


class TestWebGUI(unittest.TestCase):
    def setUp(self):
        brain = Ingenium()
        brain.company_intelligence.customer_data.upsert_record("cust-1", {"email": "a@example.com"})
        self.server = make_server(host="127.0.0.1", port=0, brain=brain)
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def test_index_page_served(self):
        with urllib.request.urlopen(f"{self.base_url}/") as response:
            self.assertEqual(response.status, 200)
            self.assertIn("Ingenium", response.read().decode())

    def test_static_assets_served(self):
        for asset in ("/style.css", "/app.js"):
            with urllib.request.urlopen(f"{self.base_url}{asset}") as response:
                self.assertEqual(response.status, 200)

    def test_unknown_path_is_404(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(f"{self.base_url}/does-not-exist")
        self.assertEqual(ctx.exception.code, 404)

    def test_path_traversal_is_blocked(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(f"{self.base_url}/../server.py")
        self.assertEqual(ctx.exception.code, 404)

    def test_api_edge_reflects_brain_state(self):
        with urllib.request.urlopen(f"{self.base_url}/api/edge") as response:
            edge = json.loads(response.read())
        self.assertEqual(edge["customer_data"]["total"], 1)

    def test_api_execute_runs_full_pipeline(self):
        body = json.dumps({"objective": "Launch fall tune-up campaign"}).encode()
        request = urllib.request.Request(
            f"{self.base_url}/api/execute", data=body, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(request) as response:
            report = json.loads(response.read())
        self.assertEqual(report["objective"], "Launch fall tune-up campaign")
        self.assertEqual(len(report["pipeline"]["outreach"]["sent"]), 1)

    def test_api_execute_requires_objective(self):
        body = json.dumps({}).encode()
        request = urllib.request.Request(
            f"{self.base_url}/api/execute", data=body, headers={"Content-Type": "application/json"}
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(request)
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
