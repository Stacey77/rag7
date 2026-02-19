"""
Unit tests for Symbolic Reasoning Engine
"""
import pytest
from agi_system.reasoning.symbolic.symbolic_engine import (
    SymbolicReasoningEngine,
    LogicInferenceSystem,
    KnowledgeGraphReasoner,
    RuleEngine,
    Fact,
    Rule
)


class TestLogicInferenceSystem:
    """Test logic inference capabilities"""
    
    def test_add_fact(self):
        """Test adding facts to the system"""
        logic = LogicInferenceSystem()
        fact = logic.add_fact("Socrates is a man", confidence=0.9)
        
        assert fact.statement == "Socrates is a man"
        assert fact.confidence == 0.9
        assert fact.id in logic.facts
    
    def test_add_rule(self):
        """Test adding rules"""
        logic = LogicInferenceSystem()
        rule = logic.add_rule(
            name="mortality_rule",
            premises=["Socrates is a man", "All men are mortal"],
            conclusion="Socrates is mortal"
        )
        
        assert rule.name == "mortality_rule"
        assert len(rule.premises) == 2
        assert rule.conclusion == "Socrates is mortal"
    
    def test_forward_chaining(self):
        """Test forward chaining inference"""
        logic = LogicInferenceSystem()
        
        # Add facts
        logic.add_fact("Socrates is a man")
        logic.add_fact("All men are mortal")
        
        # Add rule
        logic.add_rule(
            name="mortality",
            premises=["Socrates is a man", "All men are mortal"],
            conclusion="Socrates is mortal"
        )
        
        # Perform forward chaining
        new_facts = logic.forward_chaining()
        
        assert len(new_facts) > 0
        assert any("Socrates is mortal" in f.statement for f in new_facts)
    
    def test_backward_chaining(self):
        """Test backward chaining to prove goals"""
        logic = LogicInferenceSystem()
        
        # Add facts
        logic.add_fact("All birds can fly")
        logic.add_fact("Eagle is a bird")
        
        # Add rule
        logic.add_rule(
            name="flight_rule",
            premises=["All birds can fly", "Eagle is a bird"],
            conclusion="Eagle can fly"
        )
        
        # Try to prove the goal
        proven = logic.backward_chaining("Eagle can fly")
        assert proven is True


class TestKnowledgeGraphReasoner:
    """Test knowledge graph reasoning"""
    
    def test_add_entity(self):
        """Test adding entities"""
        kg = KnowledgeGraphReasoner()
        kg.add_entity("Python", "programming_language", {"year": 1991})
        
        assert "Python" in kg.entities
        assert kg.entity_types["Python"] == "programming_language"
    
    def test_add_relation(self):
        """Test adding relations"""
        kg = KnowledgeGraphReasoner()
        kg.add_entity("Python", "language")
        kg.add_entity("TensorFlow", "framework")
        kg.add_relation("TensorFlow", "written_in", "Python")
        
        relations = kg.query_relations("TensorFlow")
        assert len(relations) > 0
        assert any(r[1] == "written_in" for r in relations)
    
    def test_find_path(self):
        """Test finding paths between entities"""
        kg = KnowledgeGraphReasoner()
        
        # Create a path: A -> B -> C
        kg.add_entity("A", "node")
        kg.add_entity("B", "node")
        kg.add_entity("C", "node")
        kg.add_relation("A", "connects_to", "B")
        kg.add_relation("B", "connects_to", "C")
        
        path = kg.find_path("A", "C")
        assert path is not None
        assert len(path) == 3
        assert path == ["A", "B", "C"]
    
    def test_get_neighbors(self):
        """Test getting neighboring entities"""
        kg = KnowledgeGraphReasoner()
        
        kg.add_entity("Center", "node")
        kg.add_entity("Node1", "node")
        kg.add_entity("Node2", "node")
        kg.add_relation("Center", "links", "Node1")
        kg.add_relation("Center", "links", "Node2")
        
        neighbors = kg.get_neighbors("Center")
        assert len(neighbors) == 2
        assert "Node1" in neighbors
        assert "Node2" in neighbors
    
    def test_statistics(self):
        """Test graph statistics"""
        kg = KnowledgeGraphReasoner()
        
        kg.add_entity("A", "type1")
        kg.add_entity("B", "type2")
        kg.add_relation("A", "relates", "B")
        
        stats = kg.get_statistics()
        assert stats["num_entities"] == 2
        assert stats["num_relations"] == 1


class TestRuleEngine:
    """Test rule-based reasoning"""
    
    def test_add_rule(self):
        """Test adding rules to engine"""
        engine = RuleEngine()
        rule = Rule(
            id="test_rule",
            name="Test Rule",
            premises=["condition1"],
            conclusion="result1"
        )
        
        engine.add_rule(rule)
        assert len(engine.rules) == 1
    
    def test_set_get_fact(self):
        """Test setting and getting facts"""
        engine = RuleEngine()
        
        engine.set_fact("temperature", 25)
        assert engine.get_fact("temperature") == 25
    
    def test_fire_rules(self):
        """Test firing rules"""
        engine = RuleEngine()
        
        # Set up working memory
        engine.set_fact("temperature", 35)
        
        # Add a rule
        rule = Rule(
            id="hot_rule",
            name="Hot Weather",
            premises=["temperature > 30"],
            conclusion="weather is hot"
        )
        engine.add_rule(rule)
        
        # Fire rules
        result = engine.fire_rules()
        assert "rule_hot_rule_fired" in engine.working_memory


class TestSymbolicReasoningEngine:
    """Test integrated symbolic reasoning engine"""
    
    def test_initialization(self):
        """Test engine initialization"""
        engine = SymbolicReasoningEngine()
        
        assert engine.logic_system is not None
        assert engine.knowledge_graph is not None
        assert engine.rule_engine is not None
    
    def test_add_knowledge(self):
        """Test adding knowledge"""
        engine = SymbolicReasoningEngine()
        fact = engine.add_knowledge("AI is intelligent")
        
        assert fact.statement == "AI is intelligent"
        assert fact.id in engine.logic_system.facts
    
    def test_add_relation(self):
        """Test adding relations"""
        engine = SymbolicReasoningEngine()
        engine.add_relation("AI", "is_a", "Technology")
        
        relations = engine.knowledge_graph.query_relations("AI")
        assert len(relations) > 0
    
    def test_reason_forward_chaining(self):
        """Test reasoning with forward chaining"""
        engine = SymbolicReasoningEngine()
        
        engine.add_knowledge("All humans are mortal")
        engine.add_knowledge("Socrates is a human")
        engine.logic_system.add_rule(
            name="mortality",
            premises=["All humans are mortal", "Socrates is a human"],
            conclusion="Socrates is mortal"
        )
        
        result = engine.reason("test", method="forward_chaining")
        assert result["method"] == "forward_chaining"
        assert "result" in result
    
    def test_get_system_state(self):
        """Test getting system state"""
        engine = SymbolicReasoningEngine()
        
        engine.add_knowledge("Test fact")
        engine.add_relation("A", "relates", "B")
        
        state = engine.get_system_state()
        assert state["num_facts"] > 0
        assert "knowledge_graph" in state


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
