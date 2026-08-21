"""Tests for the multi-workspace platform: WorkspaceStore and the REST API."""
import io
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ingenium.core.brain import Ingenium
from ingenium.platform import WorkspaceStore, _history_summary, make_server, slugify


class TestSlugify(unittest.TestCase):
    def test_slugify_normalizes(self):
        self.assertEqual(slugify("Fortis Auto!"), "fortis-auto")
        self.assertEqual(slugify("  A/B  Co  "), "a-b-co")
        self.assertEqual(slugify("---"), "")


class TestWorkspaceStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = WorkspaceStore(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_and_load(self):
        meta = self.store.create("Fortis Auto", seed=True)
        self.assertEqual(meta["slug"], "fortis-auto")
        self.assertEqual(meta["name"], "Fortis Auto")
        brain = self.store.load("fortis-auto")
        self.assertEqual(
            brain.company_intelligence.strategy.snapshot()["positioning"],
            "AI ops partner for local service businesses",
        )

    def test_create_rejects_duplicate(self):
        self.store.create("Fortis Auto")
        with self.assertRaises(ValueError):
            self.store.create("fortis auto")  # same slug

    def test_create_rejects_empty_name(self):
        with self.assertRaises(ValueError):
            self.store.create("!!!")

    def test_save_persists_history_and_keeps_name(self):
        self.store.create("Fortis Auto", seed=True)
        brain = self.store.load("fortis-auto")
        brain.execute("Launch fall tune-up campaign")
        self.store.save("fortis-auto", brain)
        self.assertEqual(self.store.meta("fortis-auto")["runs"], 1)
        self.assertEqual(self.store.meta("fortis-auto")["name"], "Fortis Auto")

    def test_list_sorted_by_name(self):
        self.store.create("Zeta Co")
        self.store.create("Alpha Co")
        self.assertEqual([m["name"] for m in self.store.list()], ["Alpha Co", "Zeta Co"])

    def test_delete_removes_workspace(self):
        self.store.create("Fortis Auto")
        self.store.delete("fortis-auto")
        self.assertFalse(self.store.exists("fortis-auto"))
        with self.assertRaises(KeyError):
            self.store.delete("fortis-auto")

    def test_rename_keeps_slug_changes_name(self):
        self.store.create("Fortis Auto", seed=True)
        meta = self.store.rename("fortis-auto", "Fortis Automotive")
        self.assertEqual(meta["slug"], "fortis-auto")
        self.assertEqual(meta["name"], "Fortis Automotive")
        # renaming preserves the underlying state
        self.assertEqual(
            self.store.load("fortis-auto").company_intelligence.strategy.snapshot()["positioning"],
            "AI ops partner for local service businesses",
        )

    def test_rename_rejects_empty(self):
        self.store.create("Fortis Auto")
        with self.assertRaises(ValueError):
            self.store.rename("fortis-auto", "   ")

    def test_load_rejects_corrupt_workspace_file(self):
        self.store.create("Fortis Auto")
        workspace_file = os.path.join(self.tmp.name, "fortis-auto.json")
        with open(workspace_file, "w", encoding="utf-8") as handle:
            handle.write("{")
        with self.assertRaisesRegex(ValueError, "corrupt"):
            self.store.load("fortis-auto")

    def test_save_uses_atomic_replace_without_tmp_leftovers(self):
        self.store.create("Fortis Auto")
        brain = self.store.load("fortis-auto")
        brain.execute("Launch campaign")
        self.store.save("fortis-auto", brain)
        self.assertFalse(any(p.endswith(".tmp") for p in os.listdir(self.tmp.name)))


class TestHistorySummary(unittest.TestCase):
    def test_history_summary_handles_partial_records(self):
        brain = Ingenium()
        brain.history = [
            {"objective": "A"},
            {"pipeline": {"optimize": {}, "outreach": {}}},
            "invalid",
        ]
        self.assertEqual(
            _history_summary(brain),
            [
                {"objective": "A", "recommendation": "", "reached": 0},
                {"objective": "", "recommendation": "", "reached": 0},
                {"objective": "", "recommendation": "", "reached": 0},
            ],
        )


class TestPlatformAPI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.server = make_server(host="127.0.0.1", port=0, data_dir=self.tmp.name)
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()
        self.tmp.cleanup()

    def _req(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Content-Type": "application/json"} if body is not None else {}
        req = urllib.request.Request(self.base + path, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read())

    def test_index_page_served(self):
        with urllib.request.urlopen(self.base + "/") as res:
            self.assertIn("Ingenium", res.read().decode())

    def test_create_list_execute_flow(self):
        status, meta = self._req("POST", "/api/workspaces", {"name": "Fortis Auto", "seed": True})
        self.assertEqual(status, 201)
        slug = meta["slug"]

        _, listing = self._req("GET", "/api/workspaces")
        self.assertEqual([w["slug"] for w in listing["workspaces"]], [slug])

        status, report = self._req("POST", f"/api/workspaces/{slug}/execute", {"objective": "Launch campaign"})
        self.assertEqual(status, 200)
        self.assertEqual(report["objective"], "Launch campaign")

        _, ws = self._req("GET", f"/api/workspaces/{slug}")
        self.assertEqual(ws["runs"], 1)
        self.assertEqual(ws["history"][0]["objective"], "Launch campaign")

    def test_edit_edge_persists(self):
        _, meta = self._req("POST", "/api/workspaces", {"name": "Blank Co"})
        slug = meta["slug"]
        edge = {
            "strategy": {"positioning": "edited positioning", "priorities": []},
            "customer_data": {"records": [{"id": "cust-1", "email": "x@y.com"}]},
            "goals": {}, "knowledge": {}, "brand": {"voice": "", "tone_words": [], "taboo_words": []},
        }
        status, _ = self._req("PUT", f"/api/workspaces/{slug}/edge", {"edge": edge})
        self.assertEqual(status, 200)
        _, ws = self._req("GET", f"/api/workspaces/{slug}")
        self.assertEqual(ws["edge"]["strategy"]["positioning"], "edited positioning")
        self.assertEqual(ws["edge"]["customer_data"]["total"], 1)

    def test_campaign_zip_download_does_not_touch_history(self):
        _, meta = self._req("POST", "/api/workspaces", {"name": "Fortis Auto", "seed": True})
        slug = meta["slug"]
        url = f"{self.base}/api/workspaces/{slug}/campaign.zip?objective=Launch%20campaign"
        with urllib.request.urlopen(url) as res:
            self.assertEqual(res.headers["Content-Type"], "application/zip")
            payload = res.read()
        with zipfile.ZipFile(io.BytesIO(payload)) as zf:
            names = zf.namelist()
        self.assertIn("landing.html", names)
        self.assertTrue(any(n.startswith("emails/") for n in names))
        # transient export must not have added to stored history
        _, ws = self._req("GET", f"/api/workspaces/{slug}")
        self.assertEqual(ws["runs"], 0)

    def test_rename_then_delete_via_api(self):
        _, meta = self._req("POST", "/api/workspaces", {"name": "Fortis Auto", "seed": True})
        slug = meta["slug"]

        status, renamed = self._req("POST", f"/api/workspaces/{slug}/rename", {"name": "Fortis Automotive"})
        self.assertEqual(status, 200)
        self.assertEqual(renamed["name"], "Fortis Automotive")
        self.assertEqual(renamed["slug"], slug)  # slug unchanged

        status, deleted = self._req("DELETE", f"/api/workspaces/{slug}")
        self.assertEqual(status, 200)
        self.assertEqual(deleted["deleted"], slug)

        _, listing = self._req("GET", "/api/workspaces")
        self.assertEqual(listing["workspaces"], [])

    def test_delete_unknown_is_404(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._req("DELETE", "/api/workspaces/nope")
        self.assertEqual(ctx.exception.code, 404)

    def test_unknown_workspace_is_404(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._req("GET", "/api/workspaces/nope")
        self.assertEqual(ctx.exception.code, 404)

    def test_duplicate_create_is_400(self):
        self._req("POST", "/api/workspaces", {"name": "Fortis Auto"})
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._req("POST", "/api/workspaces", {"name": "Fortis Auto"})
        self.assertEqual(ctx.exception.code, 400)

    def test_corrupt_workspace_returns_400(self):
        _, meta = self._req("POST", "/api/workspaces", {"name": "Fortis Auto"})
        slug = meta["slug"]
        workspace_file = os.path.join(self.tmp.name, f"{slug}.json")
        with open(workspace_file, "w", encoding="utf-8") as handle:
            handle.write("{")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._req("GET", f"/api/workspaces/{slug}")
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
