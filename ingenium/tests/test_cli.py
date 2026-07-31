"""Tests for the Ingenium CLI (run / show / demo)."""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ingenium.cli import main


def _run(argv):
    """Invoke the CLI, capturing stdout/stderr and the exit code."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class TestRunCommand(unittest.TestCase):
    def test_run_demo_summary(self):
        code, out, _ = _run(["run", "Launch fall tune-up campaign", "--demo"])
        self.assertEqual(code, 0)
        self.assertIn("recommendation: scale", out)
        self.assertIn("reached:        1 customer(s)", out)

    def test_run_demo_json(self):
        code, out, _ = _run(["run", "Launch fall tune-up campaign", "--demo", "--json"])
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertEqual(report["objective"], "Launch fall tune-up campaign")

    def test_run_without_customers_recommends_insufficient(self):
        code, out, _ = _run(["run", "Cold launch"])
        self.assertEqual(code, 0)
        self.assertIn("recommendation: insufficient_data", out)

    def test_run_persists_and_accumulates_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = str(Path(tmp) / "state.json")
            code, _, _ = _run(["run", "Campaign one", "--demo", "--state", state])
            self.assertEqual(code, 0)
            self.assertTrue(Path(state).is_file())

            # second run loads the saved state; --demo is ignored, history grows
            code, _, err = _run(["run", "Campaign two", "--demo", "--state", state])
            self.assertEqual(code, 0)
            self.assertIn("--demo ignored", err)

            saved = json.loads(Path(state).read_text())
            self.assertEqual([r["objective"] for r in saved["history"]],
                             ["Campaign one", "Campaign two"])


class TestShowCommand(unittest.TestCase):
    def test_show_missing_state_errors(self):
        code, _, err = _run(["show", "--state", "/nonexistent/state.json"])
        self.assertEqual(code, 1)
        self.assertIn("no state file", err)

    def test_show_lists_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = str(Path(tmp) / "state.json")
            _run(["run", "Launch fall tune-up campaign", "--demo", "--state", state])
            code, out, _ = _run(["show", "--state", state])
        self.assertEqual(code, 0)
        self.assertIn("run history: 1 run(s)", out)
        self.assertIn("Launch fall tune-up campaign -> scale", out)


class TestDemoCommand(unittest.TestCase):
    def test_demo_prints_report(self):
        code, out, _ = _run(["demo"])
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertEqual(report["objective"], "Launch fall tune-up campaign")


if __name__ == "__main__":
    unittest.main()
