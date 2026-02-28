"""
AGI System - LangChain Integration Layer
Implements chain orchestration, memory systems, and tool integration
"""
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import time
import json
from loguru import logger

try:
    from langchain.schema import BaseMemory, Document
    from langchain.prompts import PromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available, using fallback implementations")


class MemoryType(str):
    """Memory type constants"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


@dataclass
class MemoryItem:
    """Represents a single memory item"""
    id: str
    content: Any
    memory_type: str
    importance: float = 0.5  # 0.0 to 1.0
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def access(self):
        """Record memory access"""
        self.access_count += 1
        self.last_accessed = time.time()


class BaseMemorySystem(ABC):
    """Base class for memory systems"""
    
    @abstractmethod
    def add(self, content: Any, importance: float = 0.5, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add item to memory"""
        pass
    
    @abstractmethod
    def retrieve(self, query: str, k: int = 5) -> List[MemoryItem]:
        """Retrieve relevant memories"""
        pass
    
    @abstractmethod
    def forget(self, memory_id: str) -> bool:
        """Remove item from memory"""
        pass
    
    @abstractmethod
    def consolidate(self) -> int:
        """Consolidate memories (e.g., move from short-term to long-term)"""
        pass


class ShortTermMemory(BaseMemorySystem):
    """Short-term memory with limited capacity"""
    
    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.memories: List[MemoryItem] = []
        self.memory_index: Dict[str, MemoryItem] = {}
        logger.info(f"Short-term memory initialized with max_size={max_size}")
    
    def add(self, content: Any, importance: float = 0.5, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add item to short-term memory"""
        memory_id = f"stm_{len(self.memories)}_{int(time.time())}"
        memory = MemoryItem(
            id=memory_id,
            content=content,
            memory_type=MemoryType.SHORT_TERM,
            importance=importance,
            metadata=metadata or {}
        )
        
        self.memories.append(memory)
        self.memory_index[memory_id] = memory
        
        # Remove oldest if capacity exceeded
        if len(self.memories) > self.max_size:
            removed = self.memories.pop(0)
            del self.memory_index[removed.id]
            logger.debug(f"Removed old memory from short-term: {removed.id}")
        
        logger.debug(f"Added to short-term memory: {memory_id}")
        return memory_id
    
    def retrieve(self, query: str = "", k: int = 5) -> List[MemoryItem]:
        """Retrieve recent memories"""
        # Return most recent k memories
        recent = self.memories[-k:] if len(self.memories) > k else self.memories
        for memory in recent:
            memory.access()
        return recent
    
    def forget(self, memory_id: str) -> bool:
        """Remove specific memory"""
        if memory_id in self.memory_index:
            memory = self.memory_index[memory_id]
            self.memories.remove(memory)
            del self.memory_index[memory_id]
            logger.debug(f"Removed memory: {memory_id}")
            return True
        return False
    
    def consolidate(self) -> int:
        """Identify memories for long-term storage"""
        # Return high-importance or frequently accessed memories
        candidates = [
            m for m in self.memories
            if m.importance > 0.7 or m.access_count > 3
        ]
        logger.info(f"Identified {len(candidates)} memories for consolidation")
        return len(candidates)
    
    def get_all(self) -> List[MemoryItem]:
        """Get all memories"""
        return self.memories.copy()


class LongTermMemory(BaseMemorySystem):
    """Long-term memory with larger capacity"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.memories: Dict[str, MemoryItem] = {}
        self.semantic_index: Dict[str, List[str]] = {}  # keyword -> memory_ids
        logger.info(f"Long-term memory initialized with max_size={max_size}")
    
    def add(self, content: Any, importance: float = 0.5, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add item to long-term memory"""
        memory_id = f"ltm_{len(self.memories)}_{int(time.time())}"
        memory = MemoryItem(
            id=memory_id,
            content=content,
            memory_type=MemoryType.LONG_TERM,
            importance=importance,
            metadata=metadata or {}
        )
        
        self.memories[memory_id] = memory
        
        # Simple keyword indexing
        if isinstance(content, str):
            keywords = content.lower().split()[:5]  # First 5 words as keywords
            for keyword in keywords:
                if keyword not in self.semantic_index:
                    self.semantic_index[keyword] = []
                self.semantic_index[keyword].append(memory_id)
        
        # Remove least important if capacity exceeded
        if len(self.memories) > self.max_size:
            least_important = min(self.memories.values(), key=lambda m: m.importance * (1 + m.access_count))
            self.forget(least_important.id)
        
        logger.debug(f"Added to long-term memory: {memory_id}")
        return memory_id
    
    def retrieve(self, query: str, k: int = 5) -> List[MemoryItem]:
        """Retrieve relevant memories by keyword matching"""
        if not query:
            # Return most important memories
            sorted_memories = sorted(
                self.memories.values(),
                key=lambda m: m.importance * (1 + m.access_count),
                reverse=True
            )
            result = sorted_memories[:k]
        else:
            # Keyword-based retrieval
            query_keywords = query.lower().split()
            matching_ids = set()
            
            for keyword in query_keywords:
                if keyword in self.semantic_index:
                    matching_ids.update(self.semantic_index[keyword])
            
            matching_memories = [self.memories[mid] for mid in matching_ids if mid in self.memories]
            result = sorted(
                matching_memories,
                key=lambda m: m.importance * (1 + m.access_count),
                reverse=True
            )[:k]
        
        for memory in result:
            memory.access()
        
        return result
    
    def forget(self, memory_id: str) -> bool:
        """Remove specific memory"""
        if memory_id in self.memories:
            memory = self.memories[memory_id]
            
            # Remove from semantic index
            if isinstance(memory.content, str):
                keywords = memory.content.lower().split()[:5]
                for keyword in keywords:
                    if keyword in self.semantic_index and memory_id in self.semantic_index[keyword]:
                        self.semantic_index[keyword].remove(memory_id)
            
            del self.memories[memory_id]
            logger.debug(f"Removed from long-term memory: {memory_id}")
            return True
        return False
    
    def consolidate(self) -> int:
        """Strengthen important memories"""
        for memory in self.memories.values():
            if memory.access_count > 5:
                memory.importance = min(1.0, memory.importance * 1.1)
        return len(self.memories)


class EpisodicMemory(BaseMemorySystem):
    """Episodic memory for experiences and events"""
    
    def __init__(self, max_episodes: int = 100):
        self.max_episodes = max_episodes
        self.episodes: List[MemoryItem] = []
        self.episode_index: Dict[str, MemoryItem] = {}
        logger.info(f"Episodic memory initialized with max_episodes={max_episodes}")
    
    def add(self, content: Any, importance: float = 0.5, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add episode to memory"""
        episode_id = f"epi_{len(self.episodes)}_{int(time.time())}"
        episode = MemoryItem(
            id=episode_id,
            content=content,
            memory_type=MemoryType.EPISODIC,
            importance=importance,
            metadata=metadata or {}
        )
        
        self.episodes.append(episode)
        self.episode_index[episode_id] = episode
        
        # Remove oldest episodes if capacity exceeded
        if len(self.episodes) > self.max_episodes:
            removed = self.episodes.pop(0)
            del self.episode_index[removed.id]
        
        logger.debug(f"Added episode: {episode_id}")
        return episode_id
    
    def retrieve(self, query: str = "", k: int = 5) -> List[MemoryItem]:
        """Retrieve recent episodes"""
        recent = self.episodes[-k:] if len(self.episodes) > k else self.episodes
        for episode in recent:
            episode.access()
        return recent
    
    def forget(self, memory_id: str) -> bool:
        """Remove specific episode"""
        if memory_id in self.episode_index:
            episode = self.episode_index[memory_id]
            self.episodes.remove(episode)
            del self.episode_index[memory_id]
            return True
        return False
    
    def consolidate(self) -> int:
        """No consolidation for episodic memory"""
        return 0
    
    def get_timeline(self, start_time: Optional[float] = None, end_time: Optional[float] = None) -> List[MemoryItem]:
        """Get episodes within a time range"""
        filtered = []
        for episode in self.episodes:
            if start_time and episode.timestamp < start_time:
                continue
            if end_time and episode.timestamp > end_time:
                continue
            filtered.append(episode)
        return filtered


class MemoryManager:
    """Manages all memory systems"""
    
    def __init__(self):
        self.short_term = ShortTermMemory(max_size=10)
        self.long_term = LongTermMemory(max_size=1000)
        self.episodic = EpisodicMemory(max_episodes=100)
        logger.info("Memory Manager initialized")
    
    def add_to_memory(self, content: Any, memory_type: str = MemoryType.SHORT_TERM, 
                     importance: float = 0.5, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add content to appropriate memory system"""
        if memory_type == MemoryType.SHORT_TERM:
            return self.short_term.add(content, importance, metadata)
        elif memory_type == MemoryType.LONG_TERM:
            return self.long_term.add(content, importance, metadata)
        elif memory_type == MemoryType.EPISODIC:
            return self.episodic.add(content, importance, metadata)
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")
    
    def retrieve_from_memory(self, query: str, memory_type: Optional[str] = None, k: int = 5) -> List[MemoryItem]:
        """Retrieve memories from one or all systems"""
        if memory_type == MemoryType.SHORT_TERM:
            return self.short_term.retrieve(query, k)
        elif memory_type == MemoryType.LONG_TERM:
            return self.long_term.retrieve(query, k)
        elif memory_type == MemoryType.EPISODIC:
            return self.episodic.retrieve(query, k)
        else:
            # Retrieve from all systems
            results = []
            results.extend(self.short_term.retrieve(query, k))
            results.extend(self.long_term.retrieve(query, k))
            results.extend(self.episodic.retrieve(query, k))
            
            # Sort by importance and recency
            results.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)
            return results[:k]
    
    def consolidate_memories(self) -> Dict[str, int]:
        """Consolidate memories from short-term to long-term"""
        # Get high-value short-term memories
        candidates = [m for m in self.short_term.get_all() if m.importance > 0.7 or m.access_count > 3]
        
        consolidated_count = 0
        for memory in candidates:
            # Add to long-term memory
            self.long_term.add(memory.content, memory.importance, memory.metadata)
            consolidated_count += 1
        
        logger.info(f"Consolidated {consolidated_count} memories from short-term to long-term")
        
        return {
            "short_term_consolidated": consolidated_count,
            "short_term_remaining": len(self.short_term.memories),
            "long_term_total": len(self.long_term.memories)
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about all memory systems"""
        return {
            "short_term": {
                "count": len(self.short_term.memories),
                "max_size": self.short_term.max_size
            },
            "long_term": {
                "count": len(self.long_term.memories),
                "max_size": self.long_term.max_size
            },
            "episodic": {
                "count": len(self.episodic.episodes),
                "max_size": self.episodic.max_episodes
            }
        }


@dataclass
class ChainStep:
    """Represents a step in a reasoning chain"""
    id: str
    description: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, in_progress, completed, failed
    error: Optional[str] = None
    
    def execute(self, executor: Callable[[Dict[str, Any]], Dict[str, Any]]) -> bool:
        """Execute this chain step"""
        try:
            self.status = "in_progress"
            self.output_data = executor(self.input_data)
            self.status = "completed"
            return True
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            logger.error(f"Chain step {self.id} failed: {e}")
            return False


class ChainOrchestrator:
    """Orchestrates chain-of-thought reasoning chains"""
    
    def __init__(self, memory_manager: MemoryManager):
        self.memory_manager = memory_manager
        self.chains: Dict[str, List[ChainStep]] = {}
        self.executors: Dict[str, Callable] = {}
        logger.info("Chain Orchestrator initialized")
    
    def register_executor(self, step_type: str, executor: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """Register an executor for a step type"""
        self.executors[step_type] = executor
        logger.debug(f"Registered executor for step type: {step_type}")
    
    def create_chain(self, chain_id: str, steps: List[Dict[str, Any]]) -> str:
        """Create a new reasoning chain"""
        chain_steps = []
        for i, step_config in enumerate(steps):
            step = ChainStep(
                id=f"{chain_id}_step_{i}",
                description=step_config.get("description", f"Step {i}"),
                input_data=step_config.get("input", {})
            )
            chain_steps.append(step)
        
        self.chains[chain_id] = chain_steps
        logger.info(f"Created chain: {chain_id} with {len(chain_steps)} steps")
        return chain_id
    
    def execute_chain(self, chain_id: str) -> Dict[str, Any]:
        """Execute a reasoning chain"""
        if chain_id not in self.chains:
            raise ValueError(f"Chain {chain_id} not found")
        
        chain_steps = self.chains[chain_id]
        results = []
        
        logger.info(f"Executing chain: {chain_id}")
        
        for step in chain_steps:
            # Get executor for step type
            step_type = step.input_data.get("type", "default")
            executor = self.executors.get(step_type, self._default_executor)
            
            # Execute step
            success = step.execute(executor)
            
            if not success:
                logger.error(f"Chain execution stopped at step: {step.id}")
                break
            
            results.append(step.output_data)
            
            # Store in episodic memory
            self.memory_manager.add_to_memory(
                content={"step": step.description, "output": step.output_data},
                memory_type=MemoryType.EPISODIC,
                importance=0.6
            )
        
        return {
            "chain_id": chain_id,
            "completed_steps": len([s for s in chain_steps if s.status == "completed"]),
            "total_steps": len(chain_steps),
            "results": results
        }
    
    def _default_executor(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Default executor for chain steps"""
        return {"status": "executed", "input": input_data}


class PromptManager:
    """Manages prompts and prompt templates"""
    
    def __init__(self):
        self.templates: Dict[str, str] = {}
        self._initialize_default_templates()
        logger.info("Prompt Manager initialized")
    
    def _initialize_default_templates(self):
        """Initialize default prompt templates"""
        self.templates["reasoning"] = """
Given the following context and question, provide a reasoned answer:

Context: {context}
Question: {question}

Think step by step:
1. What information is relevant?
2. What logical inferences can be made?
3. What is the conclusion?

Answer:
"""
        
        self.templates["analysis"] = """
Analyze the following information:

Input: {input}

Provide:
1. Key observations
2. Patterns identified
3. Insights derived

Analysis:
"""
        
        self.templates["decision"] = """
Make a decision based on the following:

Options: {options}
Criteria: {criteria}
Context: {context}

Consider:
1. Pros and cons of each option
2. Alignment with criteria
3. Risk assessment

Decision:
"""
    
    def add_template(self, name: str, template: str):
        """Add a new prompt template"""
        self.templates[name] = template
        logger.debug(f"Added prompt template: {name}")
    
    def get_template(self, name: str) -> Optional[str]:
        """Get a prompt template"""
        return self.templates.get(name)
    
    def format_prompt(self, template_name: str, **kwargs) -> str:
        """Format a prompt template with provided arguments"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing required parameter for template: {e}")
            raise


class LangChainIntegrationLayer:
    """Main LangChain integration layer"""
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.chain_orchestrator = ChainOrchestrator(self.memory_manager)
        self.prompt_manager = PromptManager()
        logger.info("LangChain Integration Layer initialized")
    
    def process_with_chain(self, input_text: str, chain_type: str = "reasoning") -> Dict[str, Any]:
        """Process input using a reasoning chain"""
        # Store input in short-term memory
        self.memory_manager.add_to_memory(
            content=input_text,
            memory_type=MemoryType.SHORT_TERM,
            importance=0.5
        )
        
        # Retrieve relevant context from memory
        context_memories = self.memory_manager.retrieve_from_memory(input_text, k=3)
        context = " ".join([str(m.content) for m in context_memories])
        
        # Create and execute chain
        chain_id = f"chain_{int(time.time())}"
        steps = [
            {"description": "Analyze input", "input": {"type": "analyze", "text": input_text}},
            {"description": "Retrieve context", "input": {"type": "retrieve", "query": input_text}},
            {"description": "Reason", "input": {"type": "reason", "text": input_text, "context": context}},
        ]
        
        self.chain_orchestrator.create_chain(chain_id, steps)
        result = self.chain_orchestrator.execute_chain(chain_id)
        
        return result
    
    def get_system_state(self) -> Dict[str, Any]:
        """Get current system state"""
        return {
            "memory_stats": self.memory_manager.get_memory_stats(),
            "active_chains": len(self.chain_orchestrator.chains),
            "available_templates": len(self.prompt_manager.templates)
        }
