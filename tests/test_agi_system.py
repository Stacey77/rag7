"""
Unit tests for AGI System integration
"""
import pytest
from agi_system import AGISystem, create_agi_system


class TestAGISystem:
    """Test integrated AGI system"""
    
    def test_create_system(self):
        """Test creating AGI system"""
        agi = create_agi_system()
        assert agi is not None
        assert agi.agent_controller is not None
        assert agi.symbolic_engine is not None
        assert agi.emotional_engine is not None
        assert agi.knowledge_layer is not None
    
    def test_process_input(self):
        """Test processing user input"""
        agi = create_agi_system()
        
        result = agi.process_input("I'm excited to learn about AI!")
        
        assert result is not None
        assert "response" in result
        assert "emotional_analysis" in result
        assert "status" in result
        assert result["status"] == "success"
    
    def test_add_knowledge(self):
        """Test adding knowledge"""
        agi = create_agi_system()
        
        doc_id = agi.add_knowledge("AI is transforming the world")
        assert doc_id is not None
        assert isinstance(doc_id, str)
    
    def test_add_structured_knowledge(self):
        """Test adding structured knowledge"""
        agi = create_agi_system()
        
        # Should not raise an exception
        agi.add_structured_knowledge("AI", "is_a", "Technology")
    
    def test_query_knowledge(self):
        """Test querying knowledge"""
        agi = create_agi_system()
        
        # Add some knowledge first
        agi.add_knowledge("Machine learning is a subset of AI")
        
        # Query it
        result = agi.query_knowledge("machine learning", method="vector")
        
        assert result is not None
        assert "method" in result
        assert "results" in result
    
    def test_set_and_execute_goal(self):
        """Test setting and executing goals"""
        agi = create_agi_system()
        
        # Set a goal
        goal_id = agi.set_goal("Test goal", priority="medium")
        assert goal_id is not None
        
        # Execute the goal
        result = agi.execute_goal(goal_id)
        assert result is not None
        assert "status" in result
    
    def test_symbolic_reasoning(self):
        """Test symbolic reasoning"""
        agi = create_agi_system()
        
        # Add some facts
        agi.symbolic_engine.logic_system.add_fact("A is true")
        agi.symbolic_engine.logic_system.add_fact("B is true")
        
        # Reason about it
        result = agi.reason("test query", reasoning_type="symbolic")
        
        assert result is not None
        assert "method" in result
    
    def test_emotional_reasoning(self):
        """Test emotional reasoning"""
        agi = create_agi_system()
        
        result = agi.reason("I'm so happy!", reasoning_type="emotional")
        
        assert result is not None
        assert "detected_emotions" in result
    
    def test_hybrid_reasoning(self):
        """Test hybrid reasoning"""
        agi = create_agi_system()
        
        result = agi.reason("Test query", reasoning_type="hybrid")
        
        assert result is not None
        assert "symbolic" in result
        assert "emotional" in result
    
    def test_get_system_status(self):
        """Test getting system status"""
        agi = create_agi_system()
        
        status = agi.get_system_status()
        
        assert status is not None
        assert "agent_controller" in status
        assert "symbolic_reasoning" in status
        assert "emotional_intelligence" in status
        assert "knowledge_layer" in status
        assert "learning_module" in status
    
    def test_consolidate_memories(self):
        """Test memory consolidation"""
        agi = create_agi_system()
        
        # Add some memories
        agi.process_input("Test input 1")
        agi.process_input("Test input 2")
        
        # Consolidate
        result = agi.consolidate_memories()
        
        assert result is not None
        assert "short_term_consolidated" in result
    
    def test_export_knowledge_graph(self):
        """Test exporting knowledge graph"""
        agi = create_agi_system()
        
        # Add some knowledge
        agi.add_structured_knowledge("A", "relates", "B")
        
        # Export
        graph = agi.export_knowledge_graph()
        
        assert graph is not None
        assert "entities" in graph
        assert "relations" in graph
        assert "stats" in graph


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
