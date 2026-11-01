"""Tests for Ingenium: both hemispheres, the integration hub, and the full loop."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ingenium import Ingenium
from ingenium.company_intelligence import CompanyIntelligence
from ingenium.core.integration_hub import IntegrationHub


class TestCompanyIntelligence(unittest.TestCase):
    def test_snapshot_shape(self):
        ci = CompanyIntelligence()
        ci.strategy.set_positioning("The AI ops partner for local service businesses")
        ci.strategy.add_priority("expand enterprise", rank=1)
        ci.customer_data.upsert_record("cust-1", {"email": "lead@example.com", "stage": "new"})
        ci.goals.set_goal("Q3 new clients", target=10, current=3)
        ci.knowledge.add("pricing", "Starter tier is $499/mo")
        ci.brand.set_voice("direct, confident, no fluff", ["clear", "bold"])

        snapshot = ci.snapshot()
        self.assertEqual(
            set(snapshot.keys()),
            {"strategy", "customer_data", "goals", "knowledge", "brand"},
        )
        self.assertEqual(snapshot["customer_data"]["total"], 1)
        self.assertAlmostEqual(snapshot["goals"]["Q3 new clients"]["completion_ratio"], 0.3)


class TestIntegrationHub(unittest.TestCase):
    def test_connect_all_and_requires_connection(self):
        hub = IntegrationHub()
        crm = hub.get("crm")
        with self.assertRaises(RuntimeError):
            crm.log_activity("cust-1", "called")

        statuses = hub.connect_all()
        self.assertTrue(all(s["connected"] for s in statuses.values()))
        self.assertEqual(set(statuses.keys()), set(hub.adapters.keys()))
        self.assertTrue(hub.status()["crm"])


class TestIngeniumPipeline(unittest.TestCase):
    def setUp(self):
        self.brain = Ingenium()
        ci = self.brain.company_intelligence
        ci.strategy.set_positioning("AI ops partner for local service businesses")
        ci.strategy.add_priority("book more jobs", rank=1)
        ci.customer_data.upsert_record("cust-1", {"email": "a@example.com", "stage": "new"})
        ci.customer_data.upsert_record("cust-2", {"email": "b@example.com", "stage": "new"})
        ci.brand.set_voice("direct, confident", ["clear", "bold"])
        ci.knowledge.add("offers", "Fall tune-up special: $99")

    def test_think_returns_edge(self):
        thought = self.brain.think("Launch fall tune-up campaign")
        self.assertEqual(thought["objective"], "Launch fall tune-up campaign")
        self.assertIn("customer_data", thought["edge"])

    def test_connect_returns_all_six_integrations(self):
        connections = self.brain.connect()
        expected = {"crm", "web_builder", "email", "finance", "analytics", "calendar"}
        self.assertEqual(set(connections.keys()), expected)

    def test_execute_runs_full_pipeline(self):
        report = self.brain.execute("Launch fall tune-up campaign")

        self.assertEqual(report["objective"], "Launch fall tune-up campaign")
        self.assertIn("edge", report)
        self.assertIn("integrations", report)

        pipeline = report["pipeline"]
        self.assertEqual(
            set(pipeline.keys()),
            {"research", "create", "outreach", "follow_up", "optimize"},
        )

        # Research saw the customer segment and prior strategy priorities.
        self.assertEqual(pipeline["research"]["findings"]["target_segment"], 2)

        # Create published a page through the web builder.
        self.assertEqual(pipeline["create"]["asset"]["status"], "published")

        # Outreach emailed both customer records.
        self.assertEqual(len(pipeline["outreach"]["sent"]), 2)

        # Follow-up scheduled one calendar event per outreach message.
        self.assertEqual(len(pipeline["follow_up"]["scheduled"]), 2)

        # Optimize saw the outreach event tracked in analytics.
        self.assertEqual(pipeline["optimize"]["report"]["outreach_sent"], 1)
        self.assertEqual(pipeline["optimize"]["recommendation"], "scale")

    def test_execute_without_customer_records_yields_insufficient_data(self):
        empty_brain = Ingenium()
        report = empty_brain.execute("Cold launch with no customers yet")
        self.assertEqual(report["pipeline"]["optimize"]["recommendation"], "insufficient_data")


if __name__ == "__main__":
    unittest.main()
