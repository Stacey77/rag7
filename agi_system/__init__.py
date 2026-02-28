"""
AGI System - Main Integration Module
Integrates all AGI components into a unified system
"""
from typing import Dict, Any, Optional, List
from loguru import logger
import sys

from .config import AGIConfig, get_config
from .core.agent_controller import AGIAgentController, GoalPriority
from .reasoning.symbolic.symbolic_engine import SymbolicReasoningEngine
from .reasoning.emotional.emotional_engine import EmotionalReasoningEngine
from .langchain_layer.integration import LangChainIntegrationLayer
from .knowledge.rag_integration import KnowledgeLayerRAG
from .learning.learning_module import LearningModule, LearningMode


class AGISystem:
    """
    Main AGI System integrating all components:
    - Agent Controller (AutoGPT-inspired)
    - Symbolic Reasoning Engine
    - Emotional Reasoning Engine  
    - LangChain Integration Layer
    - Knowledge Layer with RAG
    - Learning Module
    """
    
    def __init__(self, config: Optional[AGIConfig] = None):
        """Initialize the AGI system"""
        self.config = config or get_config()
        
        # Setup logging
        logger.remove()
        logger.add(
            sys.stderr,
            level=self.config.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
        )
        
        logger.info("Initializing AGI System...")
        
        # Initialize core components
        self.agent_controller = AGIAgentController()
        self.symbolic_engine = SymbolicReasoningEngine()
        self.emotional_engine = EmotionalReasoningEngine()
        self.langchain_layer = LangChainIntegrationLayer()
        self.knowledge_layer = KnowledgeLayerRAG()
        self.learning_module = LearningModule()
        
        logger.info("AGI System initialized successfully")
    
    def process_input(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user input through the AGI system
        
        Args:
            user_input: User's input text
            context: Optional context dictionary
            
        Returns:
            Dict containing the system's response and metadata
        """
        logger.info(f"Processing input: {user_input[:100]}...")
        
        try:
            # 1. Emotional processing
            emotional_analysis = self.emotional_engine.process_input(user_input, context)
            logger.debug(f"Emotional analysis: {emotional_analysis['affective_state']['primary_emotion']}")
            
            # 2. Store in memory
            self.langchain_layer.memory_manager.add_to_memory(
                content=user_input,
                memory_type="short_term",
                importance=0.7
            )
            
            # 3. Retrieve relevant knowledge (RAG)
            knowledge_results = self.knowledge_layer.query(user_input, k=3, method="vector")
            logger.debug(f"Retrieved {len(knowledge_results['results'])} knowledge items")
            
            # 4. Symbolic reasoning (if needed)
            reasoning_result = None
            if self._requires_symbolic_reasoning(user_input):
                reasoning_result = self.symbolic_engine.reason(user_input, method="forward_chaining")
                logger.debug("Applied symbolic reasoning")
            
            # 5. Generate response using chain
            chain_result = self.langchain_layer.process_with_chain(user_input, chain_type="reasoning")
            
            # 6. Learn from interaction
            self.learning_module.learn(
                learning_mode=LearningMode.ONLINE,
                interaction={"input": user_input, "type": "user_query"},
                feedback=0.8  # Default positive feedback
            )
            
            # Construct response
            response = {
                "response": emotional_analysis["empathetic_response"],
                "emotional_analysis": emotional_analysis,
                "knowledge_context": knowledge_results["results"][:2] if knowledge_results["results"] else [],
                "reasoning": reasoning_result,
                "chain_execution": chain_result,
                "status": "success"
            }
            
            logger.info("Input processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your request.",
                "error": str(e),
                "status": "error"
            }
    
    def set_goal(self, goal_description: str, priority: str = "medium") -> str:
        """
        Set a high-level goal for the AGI agent
        
        Args:
            goal_description: Description of the goal
            priority: Priority level (low, medium, high, critical)
            
        Returns:
            Goal ID
        """
        priority_map = {
            "low": GoalPriority.LOW,
            "medium": GoalPriority.MEDIUM,
            "high": GoalPriority.HIGH,
            "critical": GoalPriority.CRITICAL
        }
        
        priority_enum = priority_map.get(priority.lower(), GoalPriority.MEDIUM)
        goal_id = self.agent_controller.set_goal(goal_description, priority_enum)
        
        logger.info(f"Set goal: {goal_description} (Priority: {priority})")
        return goal_id
    
    def execute_goal(self, goal_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a goal autonomously
        
        Args:
            goal_id: Optional goal ID (uses active goal if not provided)
            
        Returns:
            Dict containing execution results
        """
        logger.info(f"Executing goal: {goal_id or 'active'}")
        
        try:
            result = self.agent_controller.execute_goal(goal_id)
            
            # Learn from goal execution
            self.learning_module.learn(
                learning_mode=LearningMode.REINFORCEMENT,
                state={"goal": goal_id or "active"},
                action="execute_goal",
                reward=1.0 if result["status"] == "completed" else 0.3,
                done=result["status"] == "completed"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing goal: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def add_knowledge(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add knowledge to the system
        
        Args:
            content: Knowledge content
            metadata: Optional metadata
            
        Returns:
            Document ID
        """
        doc_id = self.knowledge_layer.ingest_document(content, metadata)
        logger.info(f"Added knowledge: {doc_id}")
        return doc_id
    
    def add_structured_knowledge(self, subject: str, predicate: str, object: str) -> None:
        """
        Add structured knowledge (triple) to knowledge graph
        
        Args:
            subject: Subject entity
            predicate: Relation/predicate
            object: Object entity
        """
        self.knowledge_layer.add_structured_knowledge(subject, predicate, object)
        self.symbolic_engine.add_relation(subject, predicate, object)
        logger.info(f"Added structured knowledge: {subject} --[{predicate}]--> {object}")
    
    def query_knowledge(self, query: str, method: str = "hybrid") -> Dict[str, Any]:
        """
        Query the knowledge base
        
        Args:
            query: Query string
            method: Query method (vector, graph, hybrid)
            
        Returns:
            Query results
        """
        logger.info(f"Querying knowledge: {query} (method: {method})")
        return self.knowledge_layer.query(query, k=5, method=method)
    
    def reason(self, query: str, reasoning_type: str = "symbolic") -> Dict[str, Any]:
        """
        Perform reasoning on a query
        
        Args:
            query: Query to reason about
            reasoning_type: Type of reasoning (symbolic, emotional, hybrid)
            
        Returns:
            Reasoning results
        """
        logger.info(f"Reasoning about: {query} (type: {reasoning_type})")
        
        if reasoning_type == "symbolic":
            return self.symbolic_engine.reason(query, method="forward_chaining")
        elif reasoning_type == "emotional":
            return self.emotional_engine.process_input(query)
        elif reasoning_type == "hybrid":
            symbolic_result = self.symbolic_engine.reason(query, method="forward_chaining")
            emotional_result = self.emotional_engine.process_input(query)
            return {
                "symbolic": symbolic_result,
                "emotional": emotional_result,
                "type": "hybrid"
            }
        else:
            raise ValueError(f"Unknown reasoning type: {reasoning_type}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status
        
        Returns:
            Dict containing status of all subsystems
        """
        return {
            "agent_controller": self.agent_controller.get_status(),
            "symbolic_reasoning": self.symbolic_engine.get_system_state(),
            "emotional_intelligence": self.emotional_engine.get_emotional_intelligence_metrics(),
            "langchain_layer": self.langchain_layer.get_system_state(),
            "knowledge_layer": self.knowledge_layer.get_system_stats(),
            "learning_module": self.learning_module.get_learning_stats()
        }
    
    def _requires_symbolic_reasoning(self, text: str) -> bool:
        """Determine if input requires symbolic reasoning"""
        reasoning_keywords = [
            "why", "how", "because", "therefore", "if", "then",
            "implies", "prove", "logic", "reason", "deduce", "infer"
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in reasoning_keywords)
    
    def consolidate_memories(self) -> Dict[str, Any]:
        """Consolidate memories from short-term to long-term"""
        return self.langchain_layer.memory_manager.consolidate_memories()
    
    def export_knowledge_graph(self) -> Dict[str, Any]:
        """Export the knowledge graph"""
        return {
            "entities": list(self.knowledge_layer.knowledge_graph.entities.keys()),
            "relations": self.knowledge_layer.knowledge_graph.relations,
            "stats": self.knowledge_layer.knowledge_graph.get_stats()
        }


def create_agi_system(config: Optional[AGIConfig] = None) -> AGISystem:
    """
    Factory function to create an AGI system instance
    
    Args:
        config: Optional configuration
        
    Returns:
        Initialized AGI system
    """
    return AGISystem(config)


__all__ = [
    'AGISystem',
    'create_agi_system',
    'AGIConfig',
    'get_config',
]
