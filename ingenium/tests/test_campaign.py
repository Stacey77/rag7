"""Tests for campaign asset generation and export."""
import csv
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ingenium.campaign import (
    email_copy,
    export_campaign,
    followups_ics,
    landing_page_html,
    outreach_csv,
)
from ingenium.samples import sample_brain


def _sample_report():
    return sample_brain().execute("Launch fall tune-up campaign")


class TestAssetGeneration(unittest.TestCase):
    def setUp(self):
        self.report = _sample_report()

    def test_landing_page_includes_objective_and_offer(self):
        page = landing_page_html(self.report)
        self.assertIn("<!doctype html>", page)
        self.assertIn("Launch fall tune-up campaign", page)
        self.assertIn("Fall tune-up special: $99", page)  # from knowledge
        self.assertIn("AI ops partner for local service businesses", page)  # positioning

    def test_email_copy_is_addressed_and_has_offer(self):
        email = email_copy(self.report, "lead@example.com")
        self.assertEqual(email["to"], "lead@example.com")
        self.assertEqual(email["subject"], "Launch fall tune-up campaign")
        self.assertIn("Fall tune-up special: $99", email["body"])

    def test_ics_is_wellformed_with_one_event_per_followup(self):
        ics = followups_ics(self.report)
        self.assertTrue(ics.startswith("BEGIN:VCALENDAR"))
        self.assertIn("END:VCALENDAR", ics)
        n_followups = len(self.report["pipeline"]["follow_up"]["scheduled"])
        self.assertEqual(ics.count("BEGIN:VEVENT"), n_followups)
        self.assertEqual(ics.count("END:VEVENT"), n_followups)

    def test_csv_has_header_and_row_per_recipient(self):
        text = outreach_csv(self.report)
        rows = list(csv.reader(io.StringIO(text)))
        self.assertEqual(rows[0], ["recipient", "objective", "subject", "status"])
        self.assertEqual(len(rows) - 1, len(self.report["pipeline"]["outreach"]["sent"]))
        self.assertEqual(rows[1][0], "lead@example.com")

    def test_landing_page_escapes_html(self):
        report = sample_brain().execute("Sale <script>alert(1)</script>")
        page = landing_page_html(report)
        self.assertNotIn("<script>alert(1)</script>", page)
        self.assertIn("&lt;script&gt;", page)


class TestExportCampaign(unittest.TestCase):
    def test_export_writes_all_expected_files(self):
        report = _sample_report()
        with tempfile.TemporaryDirectory() as tmp:
            written = export_campaign(report, tmp)
            out = Path(tmp)
            self.assertTrue((out / "landing.html").is_file())
            self.assertTrue((out / "followups.ics").is_file())
            self.assertTrue((out / "outreach.csv").is_file())
            self.assertTrue((out / "report.json").is_file())
            # one email file per recipient
            email_files = list((out / "emails").glob("*.txt"))
            self.assertEqual(len(email_files), len(report["pipeline"]["outreach"]["sent"]))
            # returned mapping points at real files
            for path in written.values():
                self.assertTrue(Path(path).is_file())

    def test_export_creates_missing_directory(self):
        report = _sample_report()
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "deep" / "campaign"
            export_campaign(report, nested)
            self.assertTrue((nested / "landing.html").is_file())


if __name__ == "__main__":
    unittest.main()
