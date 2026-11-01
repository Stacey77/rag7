"""Comprehensive tests for advanced robotics AGI system."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMetaLearning(unittest.TestCase):
    def test_maml(self):
        from advanced.meta_learning import MetaLearner
        ml = MetaLearner()
        result = ml.meta_train([{"task": "pick", "data": []}])
        self.assertIsInstance(result, dict)
        result = ml.few_shot_adapt({"task": "place"}, [{"obs": 1, "action": 2}])
        self.assertIsInstance(result, dict)
        result = ml.zero_shot_transfer("grasp unknown object")
        self.assertIsInstance(result, dict)

    def test_reptile(self):
        from advanced.meta_learning import ReptileMetaLearner
        rl = ReptileMetaLearner()
        result = rl.meta_update([{"task": "pick"}])
        self.assertIsInstance(result, dict)
        result = rl.meta_update([{"task": "place"}, {"task": "push"}], step_size=0.05)
        self.assertIsInstance(result, dict)

    def test_few_shot(self):
        from advanced.meta_learning import FewShotLearner
        fs = FewShotLearner()
        result = fs.adapt({"name": "pick"}, [{"obs": 1, "label": "A"}], [{"obs": 2}])
        self.assertIsInstance(result, dict)
        result = fs.predict({"obs": 3})
        self.assertIsInstance(result, dict)

    def test_zero_shot(self):
        from advanced.meta_learning import ZeroShotLearner
        zs = ZeroShotLearner()
        result = zs.transfer("grasp a heavy fragile object")
        self.assertIsInstance(result, dict)
        result = zs.transfer("navigate to goal", context={"env": "indoor"})
        self.assertIsInstance(result, dict)


class TestMultimodal(unittest.TestCase):
    def test_fusion(self):
        from advanced.multimodal import MultimodalFusion
        mf = MultimodalFusion()
        modalities = {"vision": [1, 2, 3], "audio": [4, 5, 6], "tactile": [7]}
        result = mf.early_fusion(modalities)
        self.assertIsInstance(result, dict)
        result = mf.late_fusion(modalities)
        self.assertIsInstance(result, dict)
        result = mf.attention_fusion(modalities)
        self.assertIsInstance(result, dict)
        result = mf.transformer_fusion(modalities)
        self.assertIsInstance(result, dict)

    def test_vlm(self):
        from advanced.multimodal import VisionLanguageModel
        vlm = VisionLanguageModel()
        image = {"id": "img_1", "features": ["red", "round"]}
        result = vlm.visual_reasoning(image, "What color is the object?")
        self.assertIsInstance(result, dict)
        result = vlm.generate_detailed_caption(image)
        self.assertIsInstance(result, dict)
        result = vlm.ground_language_to_vision("the red ball", image)
        self.assertIsInstance(result, dict)

    def test_active_perception(self):
        from advanced.multimodal import ActivePerception
        ap = ActivePerception()
        result = ap.plan_next_view({"uncertainty": 0.7})
        self.assertIsInstance(result, dict)
        result = ap.focus_attention({"objects": ["cup", "table"]})
        self.assertIsInstance(result, dict)
        result = ap.minimize_uncertainty({"uncertainty": 0.5})
        self.assertIsInstance(result, dict)

    def test_sensor_fusion(self):
        from advanced.multimodal import SensorFusion
        sf = SensorFusion()
        result = sf.fuse({"lidar": 1.5, "camera": 1.6, "imu": 0.1})
        self.assertIsInstance(result, dict)
        result = sf.calibrate("lidar", {"bias": 0.01, "scale": 1.0})
        self.assertIsInstance(result, dict)


class TestHierarchicalPlanning(unittest.TestCase):
    def test_mission_planner(self):
        from advanced.hierarchical_planning import MissionPlanner
        mp = MissionPlanner()
        result = mp.plan_mission({"type": "pick", "target": "cup"})
        self.assertIsInstance(result, dict)
        result = mp.update_mission({"status": "in_progress", "progress_pct": 50})
        self.assertIsInstance(result, dict)

    def test_task_planner(self):
        from advanced.hierarchical_planning import TaskPlanner
        tp = TaskPlanner()
        result = tp.decompose_into_tasks({"goal": {"type": "pick"}})
        self.assertIsInstance(result, list)
        result = tp.replan({"failed_task": "plan_grasp"})
        self.assertIsInstance(result, list)

    def test_motion_planner(self):
        from advanced.hierarchical_planning import MotionPlanner
        mp = MotionPlanner()
        result = mp.plan_motion({"action": "move", "start": [0, 0, 0], "goal": [1, 0, 0]})
        self.assertIsInstance(result, dict)
        result = mp.replan_online({"reason": "obstacle", "current_position": [0.5, 0, 0], "goal": [1, 1, 0]})
        self.assertIsInstance(result, dict)

    def test_neural_planner(self):
        from advanced.hierarchical_planning import NeuralPlanner
        np_ = NeuralPlanner()
        result = np_.train_planner([{"state": {}, "goal": {}, "solution": []}])
        self.assertIsInstance(result, dict)
        result = np_.plan_with_neural_net({"pos": [0, 0]}, {"goal": [1, 1]})
        self.assertIsInstance(result, dict)
        result = np_.continuous_planning({"name": "test_env"})
        self.assertIsInstance(result, dict)

    def test_hierarchical_planner(self):
        from advanced.hierarchical_planning import HierarchicalPlanner
        hp = HierarchicalPlanner()
        result = hp.plan({"type": "pick", "target": "cup"})
        self.assertIsInstance(result, dict)


class TestManipulation(unittest.TestCase):
    def test_dexterous(self):
        from advanced.manipulation import DexterousManipulation
        dm = DexterousManipulation()
        result = dm.in_hand_reorientation({"name": "screwdriver"})
        self.assertIsInstance(result, dict)
        result = dm.use_tool({"name": "wrench"}, {"type": "fasten"})
        self.assertIsInstance(result, dict)
        result = dm.precision_grasp({"name": "fragile_cup"}, "pinch")
        self.assertIsInstance(result, dict)

    def test_contact_rich(self):
        from advanced.manipulation import ContactRichManipulation
        cr = ContactRichManipulation()
        result = cr.push_to_goal({"name": "box"}, {"x": 1.0, "y": 0.5})
        self.assertIsInstance(result, dict)
        result = cr.assemble_parts([{"name": "base"}, {"name": "top"}])
        self.assertIsInstance(result, dict)
        result = cr.manipulate_deformable({"name": "cloth"})
        self.assertIsInstance(result, dict)

    def test_force_controller(self):
        from advanced.manipulation import ForceController
        fc = ForceController()
        result = fc.compliant_insertion({"id": "peg_1", "diameter_mm": 9.9}, {"id": "hole_1", "diameter_mm": 10.0})
        self.assertIsInstance(result, dict)
        result = fc.polishing_with_force({"material": "aluminum", "target_force_N": 10.0})
        self.assertIsInstance(result, dict)
        result = fc.set_impedance(100.0, 10.0)
        self.assertIsInstance(result, dict)

    def test_tool_user(self):
        from advanced.manipulation import ToolUser
        tu = ToolUser()
        result = tu.select_tool({"type": "screw"})
        self.assertIsInstance(result, dict)
        result = tu.use_tool({"name": "screwdriver"}, {"type": "screw"})
        self.assertIsInstance(result, dict)


class TestReasoning(unittest.TestCase):
    def test_knowledge_graph(self):
        from advanced.reasoning import KnowledgeGraph
        kg = KnowledgeGraph()
        result = kg.add_knowledge("cup", "is_a", "container")
        self.assertIsInstance(result, dict)
        result = kg.query_knowledge("cup")
        self.assertIsInstance(result, list)
        result = kg.reason_over_graph("What is a cup?")
        self.assertIsInstance(result, dict)
        result = kg.learn_from_experience([{"subject": "robot", "predicate": "grasped", "object": "cup"}])
        self.assertIsInstance(result, dict)

    def test_causal(self):
        from advanced.reasoning import CausalReasoner
        cr = CausalReasoner()
        result = cr.learn_causal_model([{"force": 1.0, "displacement": 0.1}, {"force": 2.0, "displacement": 0.2}])
        self.assertIsInstance(result, dict)
        result = cr.predict_intervention({"variable": "force", "value": 5.0}, "displacement")
        self.assertIsInstance(result, dict)
        result = cr.counterfactual_reasoning({"changed_variable": "force", "factual_outcome": 0.5})
        self.assertIsInstance(result, dict)

    def test_commonsense(self):
        from advanced.reasoning import CommonSenseReasoner
        cs = CommonSenseReasoner()
        result = cs.physical_reasoning({"name": "table_scene", "objects": ["cup", "plate"]})
        self.assertIsInstance(result, dict)
        result = cs.temporal_reasoning([{"type": "grasp", "timestamp": 1.0}, {"type": "place", "timestamp": 2.0}])
        self.assertIsInstance(result, dict)
        result = cs.social_reasoning({"agents": ["human_1"], "context": "handshake"})
        self.assertIsInstance(result, dict)

    def test_symbolic(self):
        from advanced.reasoning import SymbolicReasoner
        sr = SymbolicReasoner()
        result = sr.add_rule("IF object_is_heavy THEN use_two_hands")
        self.assertIsInstance(result, dict)
        result = sr.reason("object_is_heavy")
        self.assertIsInstance(result, dict)


class TestSocial(unittest.TestCase):
    def test_emotion_recognizer(self):
        from advanced.social import EmotionRecognizer
        er = EmotionRecognizer()
        result = er.recognize_facial_emotion({"landmarks": 68})
        self.assertIsInstance(result, dict)
        result = er.recognize_vocal_emotion({"pitch": 200, "energy": 0.5})
        self.assertIsInstance(result, dict)
        result = er.recognize_body_emotion({"num_joints": 17})
        self.assertIsInstance(result, dict)
        face = er.recognize_facial_emotion({"landmarks": 68})
        voice = er.recognize_vocal_emotion({"pitch": 150})
        body = er.recognize_body_emotion({"num_joints": 17})
        result = er.fuse_emotional_cues(face, voice, body)
        self.assertIsInstance(result, dict)

    def test_social_navigator(self):
        from advanced.social import SocialNavigator
        sn = SocialNavigator()
        result = sn.respect_personal_space([{"id": "h1", "position": [0.5, 0.5]}])
        self.assertIsInstance(result, dict)
        result = sn.predict_human_trajectories([{"id": "h1", "position": [0, 0], "velocity": [0.5, 0]}])
        self.assertIsInstance(result, list)
        result = sn.communicate_intent({"type": "move_right", "direction": "right"})
        self.assertIsInstance(result, dict)

    def test_theory_of_mind(self):
        from advanced.social import TheoryOfMind
        tom = TheoryOfMind()
        result = tom.infer_beliefs("person_1", [{"saw": "cup_on_table"}, {"saw": "robot_approaching"}])
        self.assertIsInstance(result, dict)
        result = tom.infer_intentions("person_1", [{"action": "reach"}, {"action": "grasp"}])
        self.assertIsInstance(result, dict)
        result = tom.perspective_taking({"position": [1, 0, 1.7], "fov_deg": 120})
        self.assertIsInstance(result, dict)

    def test_intent_predictor_social(self):
        from advanced.social import IntentPredictor
        ip = IntentPredictor()
        result = ip.predict_next_action([{"pos": [0, 0]}, {"pos": [0.1, 0]}])
        self.assertIsInstance(result, dict)
        result = ip.infer_goal(["reach", "grasp"])
        self.assertIsInstance(result, dict)


class TestSwarm(unittest.TestCase):
    def test_coordinator(self):
        from advanced.swarm import SwarmCoordinator
        sc = SwarmCoordinator()
        result = sc.decentralized_task_allocation(
            [{"id": "t1"}, {"id": "t2"}],
            [{"id": "r1"}, {"id": "r2"}]
        )
        self.assertIsInstance(result, dict)
        result = sc.maintain_formation("circle")
        self.assertIsInstance(result, dict)
        result = sc.consensus_protocol([{"value": 0.3}, {"value": 0.7}])
        self.assertIsInstance(result, dict)

    def test_collective(self):
        from advanced.swarm import CollectiveIntelligence
        ci = CollectiveIntelligence()
        result = ci.stigmergic_coordination({"marker_1": 0.8, "marker_2": 0.3})
        self.assertIsInstance(result, dict)
        result = ci.quorum_decision([{"choice": "A"}, {"choice": "A"}, {"choice": "B"}])
        self.assertIsInstance(result, dict)

    def test_consensus(self):
        from advanced.swarm import ConsensusAlgorithm
        ca = ConsensusAlgorithm()
        result = ca.run([{"value": 0.0}, {"value": 1.0}, {"value": 0.5}])
        self.assertIsInstance(result, dict)
        self.assertIn("consensus_value", result)

    def test_formation(self):
        from advanced.swarm import FormationController
        fc = FormationController()
        result = fc.set_formation("circle", 4)
        self.assertIsInstance(result, dict)
        result = fc.compute_targets([[0, 0], [1, 0], [0, 1], [1, 1]])
        self.assertIsInstance(result, list)


class TestDiagnosis(unittest.TestCase):
    def test_self_diagnostics(self):
        from advanced.diagnosis import SelfDiagnostics
        sd = SelfDiagnostics()
        result = sd.detect_anomaly({"motor_temp": 80, "voltage": 24}, {"speed": 1.0})
        self.assertIsInstance(result, dict)
        result = sd.isolate_fault(["high_temp", "reduced_speed"])
        self.assertIsInstance(result, dict)
        result = sd.predict_failure({"motor": 0.7, "joint": 0.2})
        self.assertIsInstance(result, dict)
        result = sd.generate_diagnostic_report()
        self.assertIsInstance(result, dict)

    def test_self_repair(self):
        from advanced.diagnosis import SelfRepair
        sr = SelfRepair()
        result = sr.software_repair({"type": "null_pointer", "module": "perception"})
        self.assertIsInstance(result, dict)
        result = sr.recalibrate("imu_sensor")
        self.assertIsInstance(result, dict)
        result = sr.find_workaround("motor")
        self.assertIsInstance(result, dict)

    def test_anomaly_detector(self):
        from advanced.diagnosis import AnomalyDetector
        ad = AnomalyDetector()
        result = ad.fit([1.0, 2.0, 1.5, 1.8, 2.1, 1.9])
        self.assertIsInstance(result, dict)
        result = ad.detect([1.5, 10.0, 2.0])
        self.assertIsInstance(result, dict)
        self.assertIn("anomalies", result)

    def test_predictive_maintenance(self):
        from advanced.diagnosis import PredictiveMaintenance
        pm = PredictiveMaintenance()
        result = pm.update("motor_1", {"vibration": 0.05, "temperature": 45})
        self.assertIsInstance(result, dict)
        result = pm.get_health_status()
        self.assertIsInstance(result, dict)


class TestExplainability(unittest.TestCase):
    def test_xai(self):
        from advanced.explainability import ExplainableAI
        xai = ExplainableAI()
        result = xai.explain_action({"type": "move"}, {"goal": "reach_target", "obstacle": "chair"})
        self.assertIsInstance(result, dict)
        result = xai.explain_perception({"class": "cup", "confidence": 0.95})
        self.assertIsInstance(result, dict)
        result = xai.explain_plan({"goal": "pick_cup", "steps": ["approach", "grasp", "lift"]})
        self.assertIsInstance(result, dict)
        result = xai.visualize_attention({"id": "img_1"}, {"weights": [[0.1, 0.9]]})
        self.assertIsInstance(result, dict)

    def test_interpretable(self):
        from advanced.explainability import InterpretableModels
        im = InterpretableModels()
        result = im.extract_decision_tree({"layers": 4, "hidden_size": 128})
        self.assertIsInstance(result, dict)
        result = im.feature_importance({"features": ["pos_x", "pos_y", "velocity", "goal_dist"]})
        self.assertIsInstance(result, dict)

    def test_attention_visualizer(self):
        from advanced.explainability import AttentionVisualizer
        av = AttentionVisualizer()
        result = av.create_heatmap({"id": "img_1", "width": 224, "height": 224}, [0.1, 0.5, 0.9, 0.3])
        self.assertIsInstance(result, dict)
        result = av.overlay_attention({"id": "img_1"}, {"weights": [[0.1, 0.9]]})
        self.assertIsInstance(result, dict)

    def test_nl_explainer(self):
        from advanced.explainability import NaturalLanguageExplainer
        nle = NaturalLanguageExplainer()
        result = nle.explain({"type": "move", "direction": "forward"})
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        result = nle.generate_summary(["I moved forward.", "I grasped the cup."])
        self.assertIsInstance(result, str)


class TestSim2Real(unittest.TestCase):
    def test_domain_randomizer(self):
        from advanced.sim2real import DomainRandomizer
        dr = DomainRandomizer()
        result = dr.randomize_physics({"gravity": -9.8, "friction": 0.5})
        self.assertIsInstance(result, dict)
        result = dr.randomize_visuals({"objects": ["cup", "table"]})
        self.assertIsInstance(result, dict)
        result = dr.randomize_sensors({"lidar": 1.5, "camera": 1.6})
        self.assertIsInstance(result, dict)

    def test_gap_bridging(self):
        from advanced.sim2real import RealityGapBridge
        rgb = RealityGapBridge()
        result = rgb.system_identification({"num_samples": 500, "trajectories": []})
        self.assertIsInstance(result, dict)
        result = rgb.finetune_on_real({"performance": 0.85}, [{"state": {}, "action": {}}])
        self.assertIsInstance(result, dict)

    def test_system_identifier(self):
        from advanced.sim2real import SystemIdentifier
        si = SystemIdentifier()
        result = si.identify([0.1, 0.2, 0.3], [0.09, 0.19, 0.29])
        self.assertIsInstance(result, dict)
        result = si.get_parameters()
        self.assertIsInstance(result, dict)

    def test_transfer_learner(self):
        from advanced.sim2real import TransferLearner
        tl = TransferLearner()
        result = tl.transfer({"performance": 0.9}, [{"state": {}, "action": {}} for _ in range(10)])
        self.assertIsInstance(result, dict)


class TestMemory(unittest.TestCase):
    def test_episodic(self):
        from advanced.memory import EpisodicMemory
        em = EpisodicMemory(capacity=100)
        result = em.store_episode({"state": "s1", "action": "a1", "reward": 1.0})
        self.assertIsInstance(result, dict)
        result = em.recall_similar({"state": "s1"})
        self.assertIsInstance(result, list)
        result = em.replay_for_learning()
        self.assertIsInstance(result, list)

    def test_semantic(self):
        from advanced.memory import SemanticMemory
        sm = SemanticMemory()
        result = sm.store_fact({"concept": "cup", "property": "material", "value": "ceramic"})
        self.assertIsInstance(result, dict)
        result = sm.retrieve_knowledge("cup")
        self.assertIsInstance(result, list)

    def test_working_memory(self):
        from advanced.memory import WorkingMemory
        wm = WorkingMemory()
        result = wm.update_goals({"name": "pick_cup", "priority": 1})
        self.assertIsInstance(result, dict)
        result = wm.maintain_context({"location": "kitchen", "task": "pick"})
        self.assertIsInstance(result, dict)
        result = wm.get_current_goals()
        self.assertIsInstance(result, list)

    def test_consolidator(self):
        from advanced.memory import EpisodicMemory, SemanticMemory, MemoryConsolidator
        em = EpisodicMemory(capacity=50)
        sm = SemanticMemory()
        mc = MemoryConsolidator()
        for i in range(5):
            em.store_episode({"state": f"s{i}", "action": f"a{i}", "reward": float(i)})
        result = mc.consolidate(em, sm)
        self.assertIsInstance(result, dict)
        result = mc.get_stats()
        self.assertIsInstance(result, dict)


class TestLearning(unittest.TestCase):
    def test_offline_rl(self):
        from advanced.learning import OfflineRL
        orl = OfflineRL()
        dataset = [{"state": {}, "action": {}, "reward": 1.0, "next_state": {}} for _ in range(10)]
        result = orl.train_from_dataset(dataset)
        self.assertIsInstance(result, dict)
        result = orl.evaluate_dataset_quality(dataset)
        self.assertIsInstance(result, dict)

    def test_marl(self):
        from advanced.learning import MultiAgentRL
        marl = MultiAgentRL()
        agents = [{"id": "r1"}, {"id": "r2"}]
        env = {"name": "collaborative_env"}
        result = marl.train_cooperative(agents, env)
        self.assertIsInstance(result, dict)
        result = marl.train_competitive(agents, {"name": "competitive_env"})
        self.assertIsInstance(result, dict)

    def test_inverse_rl(self):
        from advanced.learning import InverseRL
        irl = InverseRL()
        demos = [{"trajectory": [{"state": {}, "action": {}}]}]
        result = irl.learn_reward(demos)
        self.assertIsInstance(result, dict)
        result = irl.infer_preferences([{"preferred": "A", "rejected": "B"}])
        self.assertIsInstance(result, dict)

    def test_curriculum(self):
        from advanced.learning import CurriculumGenerator
        cg = CurriculumGenerator()
        result = cg.generate_curriculum({"name": "complex_assembly", "difficulty": 0.9})
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        result = cg.adapt_difficulty({"success_rate": 0.85})
        self.assertIsInstance(result, dict)

    def test_self_supervised(self):
        from advanced.learning import SelfSupervisedLearner
        ssl = SelfSupervisedLearner()
        result = ssl.learn_from_exploration({"name": "kitchen", "objects": ["cup", "plate"]})
        self.assertIsInstance(result, dict)
        result = ssl.predict_future_states([{"pos": 0.0}, {"pos": 0.1}])
        self.assertIsInstance(result, list)


class TestOptimization(unittest.TestCase):
    def test_compressor(self):
        from advanced.optimization import ModelCompressor
        mc = ModelCompressor()
        model = {"size_mb": 100, "accuracy": 0.95, "num_params": 1000000}
        result = mc.quantize_model(model, "int8")
        self.assertIsInstance(result, dict)
        result = mc.prune_model(model, 0.5)
        self.assertIsInstance(result, dict)
        result = mc.distill_knowledge({"accuracy": 0.95, "size_mb": 100}, {"accuracy": 0.8, "size_mb": 10})
        self.assertIsInstance(result, dict)

    def test_accelerator(self):
        from advanced.optimization import HardwareAccelerator
        ha = HardwareAccelerator()
        model = {"size_mb": 50, "latency_ms": 100}
        result = ha.convert_to_tensorrt(model)
        self.assertIsInstance(result, dict)
        result = ha.export_to_onnx(model)
        self.assertIsInstance(result, dict)
        result = ha.compile_for_edge_tpu(model)
        self.assertIsInstance(result, dict)

    def test_quantizer(self):
        from advanced.optimization import Quantizer
        q = Quantizer()
        model = {"size_mb": 80, "num_layers": 12}
        result = q.quantize(model, "int8")
        self.assertIsInstance(result, dict)
        result = q.calibrate(model, [{"data": [1.0, 2.0]} for _ in range(100)])
        self.assertIsInstance(result, dict)

    def test_pruner(self):
        from advanced.optimization import Pruner
        p = Pruner()
        model = {"num_params": 5000000, "num_channels": 256}
        result = p.prune(model, 0.5)
        self.assertIsInstance(result, dict)
        result = p.structured_prune(model, 0.3)
        self.assertIsInstance(result, dict)


class TestSafety(unittest.TestCase):
    def test_adversarial_defense(self):
        from advanced.safety import AdversarialDefense
        ad = AdversarialDefense()
        model = {"accuracy": 0.95}
        attack = {"method": "PGD", "epsilon": 0.03}
        result = ad.adversarial_training(model, attack)
        self.assertIsInstance(result, dict)
        result = ad.detect_adversarial({"image": "data"})
        self.assertIsInstance(result, dict)

    def test_safe_explorer(self):
        from advanced.safety import SafeExplorer
        se = SafeExplorer()
        result = se.constrained_exploration({"max_force_N": 50.0, "max_velocity_ms": 2.0})
        self.assertIsInstance(result, dict)
        result = se.risk_sensitive_policy(0.2)
        self.assertIsInstance(result, dict)

    def test_formal_verifier(self):
        from advanced.safety import FormalVerifier
        fv = FormalVerifier()
        system = {"name": "robot_controller", "states": ["idle", "moving", "stopped"]}
        spec = {"properties": ["safety", "liveness"]}
        result = fv.verify(system, spec)
        self.assertIsInstance(result, dict)
        result = fv.check_invariants({"position_in_bounds": True, "velocity_safe": 1.5})
        self.assertIsInstance(result, dict)

    def test_runtime_monitor(self):
        from advanced.safety import RuntimeMonitor
        rm = RuntimeMonitor()
        result = rm.monitor({"velocity_ms": 1.0, "human_distance_m": 2.0}, {"force_N": 10.0})
        self.assertIsInstance(result, dict)
        result = rm.get_violations()
        self.assertIsInstance(result, list)


class TestCollaboration(unittest.TestCase):
    def test_intent_predictor(self):
        from advanced.collaboration import IntentPredictor
        ip = IntentPredictor()
        result = ip.predict_next_action([{"pos": [0, 0]}, {"pos": [0.1, 0.1]}])
        self.assertIsInstance(result, dict)
        result = ip.infer_goal(["reach", "grasp", "lift"])
        self.assertIsInstance(result, dict)

    def test_proactive_assistant(self):
        from advanced.collaboration import ProactiveAssistant
        pa = ProactiveAssistant()
        result = pa.anticipate_needs({"type": "cooking", "step": "chopping"})
        self.assertIsInstance(result, dict)
        result = pa.prepare_assistance({"type": "fetch_item", "priority": 0.9})
        self.assertIsInstance(result, dict)

    def test_handover(self):
        from advanced.collaboration import HandoverController
        hc = HandoverController()
        result = hc.predict_handover({"right_hand_position": [0.5, 0.0, 1.0], "gaze_target": "cup"})
        self.assertIsInstance(result, dict)
        result = hc.execute_handover({"name": "cup"}, {"id": "human_1", "mode": "give"})
        self.assertIsInstance(result, dict)

    def test_shared_autonomy(self):
        from advanced.collaboration import SharedAutonomy
        sa = SharedAutonomy()
        result = sa.blend_control(
            {"command": [0.5, 0.0, 0.0]},
            {"command": [0.3, 0.2, 0.0]}
        )
        self.assertIsInstance(result, dict)
        result = sa.adjust_autonomy_level({"human_error_rate": 0.25, "task_difficulty": 0.7})
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)
