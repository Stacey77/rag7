"""Tests for Ingenium state persistence: snapshot/restore and save/load round-trips."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ingenium import Ingenium
from ingenium.company_intelligence import CompanyIntelligence


def _populated_brain() -> Ingenium:
    brain = Ingenium()
    ci = brain.company_intelligence
    ci.strategy.set_positioning("AI ops partner for local service businesses")
    ci.strategy.add_priority("book more jobs", rank=1)
    ci.strategy.add_priority("raise retention", rank=2)
    ci.customer_data.upsert_record("cust-1", {"email": "a@example.com", "stage": "new"})
    ci.customer_data.upsert_record("cust-2", {"email": "b@example.com", "stage": "won"})
    ci.goals.set_goal("Q3 new clients", target=10, current=3)
    ci.knowledge.add("offers", "Fall tune-up special: $99")
    ci.knowledge.add("offers", "Referral bonus: $25")
    ci.brand.set_voice("direct, confident, no fluff", ["clear", "bold"])
    ci.brand.add_taboo_word("synergy")
    return brain


class TestCompanyIntelligenceRestore(unittest.TestCase):
    def test_snapshot_restore_round_trip(self):
        original = _populated_brain().company_intelligence
        snapshot = original.snapshot()

        restored = CompanyIntelligence()
        restored.restore(snapshot)

        self.assertEqual(restored.snapshot(), snapshot)

    def test_restore_tolerates_missing_keys(self):
        ci = CompanyIntelligence()
        ci.restore({})  # nothing blows up; modules stay at defaults
        self.assertEqual(ci.strategy.positioning, "")
        self.assertEqual(ci.customer_data.records, {})
        self.assertEqual(ci.goals.goals, {})

    def test_restored_goals_stay_editable(self):
        snapshot = _populated_brain().company_intelligence.snapshot()
        ci = CompanyIntelligence()
        ci.restore(snapshot)
        # record_progress requires the goal to have been rebuilt correctly
        result = ci.goals.record_progress("Q3 new clients", 7)
        self.assertEqual(result["goal"]["current"], 7)
        self.assertAlmostEqual(result["completion_ratio"], 0.7)


class TestIngeniumStatePersistence(unittest.TestCase):
    def test_state_load_state_round_trip(self):
        brain = _populated_brain()
        brain.execute("Launch fall tune-up campaign")
        state = brain.state()

        restored = Ingenium()
        restored.load_state(state)

        self.assertEqual(restored.company_intelligence.snapshot(), brain.company_intelligence.snapshot())
        self.assertEqual(len(restored.history), 1)
        self.assertEqual(restored.history[0]["objective"], "Launch fall tune-up campaign")

    def test_history_accumulates_across_executes(self):
        brain = _populated_brain()
        brain.execute("Campaign one")
        brain.execute("Campaign two")
        self.assertEqual([r["objective"] for r in brain.history], ["Campaign one", "Campaign two"])

    def test_save_and_load_from_disk(self):
        brain = _populated_brain()
        brain.execute("Launch fall tune-up campaign")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ingenium_state.json"
            brain.save(path)
            self.assertTrue(path.is_file())

            reloaded = Ingenium.load(path)

        self.assertEqual(reloaded.company_intelligence.snapshot(), brain.company_intelligence.snapshot())
        self.assertEqual(len(reloaded.history), 1)
        # a reloaded brain keeps working
        report = reloaded.execute("Follow-up campaign")
        self.assertEqual(report["objective"], "Follow-up campaign")
        self.assertEqual(len(reloaded.history), 2)

    def test_load_state_rejects_unknown_version(self):
        with self.assertRaises(ValueError):
            Ingenium().load_state({"version": 999, "edge": {}, "history": []})


if __name__ == "__main__":
    unittest.main()
