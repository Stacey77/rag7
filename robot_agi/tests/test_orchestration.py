"""Tests for the agentic orchestration framework and the robot-design pipeline."""
import os
import sys
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from robot_agi.design import design_robot, parse_brief, to_urdf
from robot_agi.orchestration import Agent, InMemoryKnowledge, MessageBus, Orchestrator


class _EchoAgent(Agent):
    name = "echo"
    role = "test"

    def run(self, brief, context):
        self.tell("orchestrator", "done", {"echo": brief.get("goal")})
        return {"echoed": brief.get("goal")}


class TestOrchestration(unittest.TestCase):
    def test_orchestrator_runs_pipeline_and_logs_messages(self):
        orch = Orchestrator()
        orch.register(_EchoAgent(orch.bus))
        result = orch.run({"goal": "hello"}, pipeline=["echo"])
        self.assertEqual(result["context"]["echo"], {"echoed": "hello"})
        # orchestrator plan + assign + agent's own message all recorded
        intents = [m["intent"] for m in result["conversation"]]
        self.assertIn("assign", intents)
        self.assertIn("done", intents)

    def test_unknown_agent_raises(self):
        orch = Orchestrator()
        with self.assertRaises(KeyError):
            orch.run({"goal": "x"}, pipeline=["missing"])

    def test_message_bus_between(self):
        bus = MessageBus()
        from robot_agi.orchestration import Message
        bus.send(Message("a", "b", "hi"))
        bus.send(Message("b", "a", "yo"))
        bus.send(Message("a", "c", "hey"))
        self.assertEqual(len(bus.between("a", "b")), 2)

    def test_knowledge_retrieval_keyword_match(self):
        kb = InMemoryKnowledge()
        hits = kb.retrieve("which material for a distal link")
        self.assertTrue(hits)
        self.assertTrue(any("carbon" in h["text"].lower() or "material" in h["topic"] for h in hits))


class TestBriefParsing(unittest.TestCase):
    def test_parses_dof_and_limb(self):
        self.assertEqual(parse_brief("6-DOF service robot arm"), {"goal": "6-DOF service robot arm", "limb": "arm", "dof": 6})
        self.assertEqual(parse_brief("exoskeleton leg")["limb"], "leg")

    def test_defaults_and_clamping(self):
        self.assertEqual(parse_brief("gripper")["dof"], 2)
        self.assertLessEqual(parse_brief("99-DOF arm")["dof"], 12)


class TestDesignPipeline(unittest.TestCase):
    def setUp(self):
        self.result = design_robot("6-DOF humanoid service robot arm")
        self.design = self.result["design"]

    def test_chain_shape(self):
        self.assertEqual(self.design.dof(), 6)
        self.assertEqual(len(self.design.links), 7)  # base + 6
        self.assertEqual(len(self.design.joints), 6)

    def test_structural_then_material_collaboration(self):
        # every link got a radius (structural) and a material + mass (material)
        for link in self.design.links:
            self.assertGreater(link.radius_m, 0)
            self.assertIn(link.material, {"steel", "aluminium", "carbon-fibre"})
            self.assertGreater(link.mass_kg, 0)
        # base link is heavier material than the tip
        self.assertEqual(self.design.links[0].material, "steel")
        self.assertEqual(self.design.links[-1].material, "carbon-fibre")

    def test_a2a_messages_recorded(self):
        senders = {m["sender"] for m in self.result["conversation"]}
        self.assertIn("structural", senders)
        self.assertIn("material", senders)

    def test_reports_present(self):
        self.assertIn("kinematics", self.result["reports"])
        self.assertIn("material", self.result["reports"])
        self.assertGreater(self.result["reports"]["material"]["total_mass_kg"], 0)


class TestUrdfExport(unittest.TestCase):
    def test_urdf_is_valid_xml_with_expected_counts(self):
        design = design_robot("4-DOF gripper arm")["design"]
        urdf = to_urdf(design)
        root = ET.fromstring(urdf.split("?>", 1)[1])  # strip xml declaration
        self.assertEqual(root.tag, "robot")
        self.assertEqual(len(root.findall("link")), len(design.links))
        self.assertEqual(len(root.findall("joint")), len(design.joints))
        # every revolute joint has an axis and limit
        for joint in root.findall("joint"):
            if joint.get("type") == "revolute":
                self.assertIsNotNone(joint.find("axis"))
                self.assertIsNotNone(joint.find("limit"))


if __name__ == "__main__":
    unittest.main()
