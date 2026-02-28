"""
AGI System - Learning Module
Implements online learning, reinforcement learning, and transfer learning capabilities
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
from loguru import logger


class LearningMode(Enum):
    """Learning modes"""
    ONLINE = "online"
    BATCH = "batch"
    REINFORCEMENT = "reinforcement"
    TRANSFER = "transfer"
    META = "meta"


@dataclass
class Experience:
    """Represents a learning experience"""
    id: str
    state: Dict[str, Any]
    action: str
    reward: float
    next_state: Optional[Dict[str, Any]] = None
    done: bool = False
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningTask:
    """Represents a learning task"""
    id: str
    name: str
    task_type: str
    domain: str
    examples: List[Dict[str, Any]] = field(default_factory=list)
    performance_history: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class OnlineLearningSystem:
    """Implements online learning from interactions"""
    
    def __init__(self, learning_rate: float = 0.01):
        self.learning_rate = learning_rate
        self.knowledge_base: Dict[str, Any] = {}
        self.interaction_history: List[Dict[str, Any]] = []
        self.performance_metrics: Dict[str, float] = {}
        logger.info(f"Online Learning System initialized with learning_rate={learning_rate}")
    
    def learn_from_interaction(self, interaction: Dict[str, Any], feedback: Optional[float] = None) -> Dict[str, Any]:
        """Learn from a single interaction"""
        # Store interaction
        interaction_record = {
            "interaction": interaction,
            "feedback": feedback,
            "timestamp": time.time()
        }
        self.interaction_history.append(interaction_record)
        
        # Extract patterns
        pattern_key = interaction.get("type", "unknown")
        
        if pattern_key not in self.knowledge_base:
            self.knowledge_base[pattern_key] = {
                "count": 0,
                "total_feedback": 0.0,
                "examples": []
            }
        
        # Update knowledge
        self.knowledge_base[pattern_key]["count"] += 1
        if feedback is not None:
            self.knowledge_base[pattern_key]["total_feedback"] += feedback
        
        # Store example if valuable
        if feedback and feedback > 0.5:
            self.knowledge_base[pattern_key]["examples"].append(interaction)
            
            # Keep only top examples
            if len(self.knowledge_base[pattern_key]["examples"]) > 10:
                self.knowledge_base[pattern_key]["examples"].pop(0)
        
        # Calculate average performance
        avg_feedback = (
            self.knowledge_base[pattern_key]["total_feedback"] / 
            self.knowledge_base[pattern_key]["count"]
        ) if self.knowledge_base[pattern_key]["count"] > 0 else 0.0
        
        self.performance_metrics[pattern_key] = avg_feedback
        
        logger.debug(f"Learned from interaction: {pattern_key}, avg_feedback={avg_feedback:.3f}")
        
        return {
            "pattern": pattern_key,
            "knowledge_updated": True,
            "average_performance": avg_feedback,
            "total_examples": self.knowledge_base[pattern_key]["count"]
        }
    
    def get_learned_patterns(self) -> Dict[str, Any]:
        """Get all learned patterns"""
        return {
            pattern: {
                "count": data["count"],
                "performance": self.performance_metrics.get(pattern, 0.0),
                "num_examples": len(data["examples"])
            }
            for pattern, data in self.knowledge_base.items()
        }
    
    def predict_performance(self, interaction_type: str) -> float:
        """Predict performance for an interaction type"""
        return self.performance_metrics.get(interaction_type, 0.0)
    
    def adapt_learning_rate(self, performance: float):
        """Adapt learning rate based on performance"""
        if performance < 0.3:
            self.learning_rate = min(0.1, self.learning_rate * 1.5)
            logger.info(f"Increased learning rate to {self.learning_rate:.4f}")
        elif performance > 0.8:
            self.learning_rate = max(0.001, self.learning_rate * 0.8)
            logger.info(f"Decreased learning rate to {self.learning_rate:.4f}")


class ReinforcementLearningSystem:
    """Implements reinforcement learning capabilities"""
    
    def __init__(self, discount_factor: float = 0.9, exploration_rate: float = 0.1):
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.q_table: Dict[Tuple[str, str], float] = {}  # (state, action) -> Q-value
        self.experience_replay: List[Experience] = []
        self.max_replay_size = 1000
        logger.info(f"Reinforcement Learning System initialized")
    
    def add_experience(self, state: Dict[str, Any], action: str, reward: float, 
                      next_state: Optional[Dict[str, Any]] = None, done: bool = False) -> str:
        """Add an experience to the replay buffer"""
        exp_id = f"exp_{len(self.experience_replay)}_{int(time.time())}"
        experience = Experience(
            id=exp_id,
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done
        )
        
        self.experience_replay.append(experience)
        
        # Remove oldest if buffer is full
        if len(self.experience_replay) > self.max_replay_size:
            self.experience_replay.pop(0)
        
        logger.debug(f"Added experience: reward={reward}")
        return exp_id
    
    def update_q_value(self, state_key: str, action: str, reward: float, 
                      next_state_key: Optional[str] = None):
        """Update Q-value using Q-learning"""
        current_q = self.q_table.get((state_key, action), 0.0)
        
        if next_state_key and not self._is_terminal(next_state_key):
            # Get max Q-value for next state
            next_actions = [key for key in self.q_table.keys() if key[0] == next_state_key]
            max_next_q = max([self.q_table[key] for key in next_actions], default=0.0)
            
            # Q-learning update
            new_q = current_q + self.exploration_rate * (
                reward + self.discount_factor * max_next_q - current_q
            )
        else:
            # Terminal state
            new_q = current_q + self.exploration_rate * (reward - current_q)
        
        self.q_table[(state_key, action)] = new_q
        logger.debug(f"Updated Q({state_key}, {action}): {current_q:.3f} -> {new_q:.3f}")
    
    def _is_terminal(self, state_key: str) -> bool:
        """Check if state is terminal"""
        # Simplified check
        return "terminal" in state_key.lower() or "done" in state_key.lower()
    
    def select_action(self, state_key: str, available_actions: List[str], 
                     epsilon_greedy: bool = True) -> str:
        """Select action using epsilon-greedy policy"""
        import random
        
        # Exploration
        if epsilon_greedy and random.random() < self.exploration_rate:
            action = random.choice(available_actions)
            logger.debug(f"Exploration: selected {action}")
            return action
        
        # Exploitation: select best action
        action_values = {
            action: self.q_table.get((state_key, action), 0.0)
            for action in available_actions
        }
        
        best_action = max(action_values.items(), key=lambda x: x[1])[0]
        logger.debug(f"Exploitation: selected {best_action}")
        return best_action
    
    def train_from_replay(self, batch_size: int = 32) -> Dict[str, Any]:
        """Train from experience replay"""
        import random
        
        if len(self.experience_replay) < batch_size:
            batch_size = len(self.experience_replay)
        
        batch = random.sample(self.experience_replay, batch_size)
        
        updates = 0
        for exp in batch:
            state_key = str(exp.state)
            next_state_key = str(exp.next_state) if exp.next_state else None
            
            self.update_q_value(state_key, exp.action, exp.reward, next_state_key)
            updates += 1
        
        logger.info(f"Trained on {updates} experiences")
        
        return {
            "updates": updates,
            "batch_size": batch_size,
            "q_table_size": len(self.q_table)
        }


class TransferLearningSystem:
    """Implements transfer learning across domains"""
    
    def __init__(self):
        self.source_tasks: Dict[str, LearningTask] = {}
        self.target_tasks: Dict[str, LearningTask] = {}
        self.transfer_mappings: Dict[Tuple[str, str], Dict[str, Any]] = {}  # (source, target) -> mapping
        logger.info("Transfer Learning System initialized")
    
    def add_source_task(self, task: LearningTask):
        """Add a source task for transfer learning"""
        self.source_tasks[task.id] = task
        logger.debug(f"Added source task: {task.name}")
    
    def add_target_task(self, task: LearningTask):
        """Add a target task"""
        self.target_tasks[task.id] = task
        logger.debug(f"Added target task: {task.name}")
    
    def find_similar_tasks(self, target_task_id: str, k: int = 3) -> List[Tuple[str, float]]:
        """Find similar source tasks for transfer"""
        if target_task_id not in self.target_tasks:
            return []
        
        target = self.target_tasks[target_task_id]
        
        # Simple similarity based on domain and task type
        similarities = []
        for source_id, source in self.source_tasks.items():
            similarity = 0.0
            
            # Domain similarity
            if source.domain == target.domain:
                similarity += 0.5
            
            # Task type similarity
            if source.task_type == target.task_type:
                similarity += 0.5
            
            similarities.append((source_id, similarity))
        
        # Sort and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    def transfer_knowledge(self, source_task_id: str, target_task_id: str) -> Dict[str, Any]:
        """Transfer knowledge from source to target task"""
        if source_task_id not in self.source_tasks:
            raise ValueError(f"Source task {source_task_id} not found")
        if target_task_id not in self.target_tasks:
            raise ValueError(f"Target task {target_task_id} not found")
        
        source = self.source_tasks[source_task_id]
        target = self.target_tasks[target_task_id]
        
        # Create transfer mapping
        mapping = {
            "source_domain": source.domain,
            "target_domain": target.domain,
            "transferred_examples": min(len(source.examples), 10),
            "adaptation_required": source.domain != target.domain
        }
        
        self.transfer_mappings[(source_task_id, target_task_id)] = mapping
        
        # Transfer examples (simplified)
        transferred_examples = source.examples[:10]
        target.examples.extend(transferred_examples)
        
        logger.info(f"Transferred knowledge from {source.name} to {target.name}")
        
        return {
            "source_task": source.name,
            "target_task": target.name,
            "transferred_examples": len(transferred_examples),
            "mapping": mapping
        }
    
    def get_transfer_performance(self, source_task_id: str, target_task_id: str) -> Optional[float]:
        """Get performance improvement from transfer"""
        if (source_task_id, target_task_id) not in self.transfer_mappings:
            return None
        
        target = self.target_tasks.get(target_task_id)
        if not target or not target.performance_history:
            return None
        
        # Calculate improvement (simplified)
        recent_performance = sum(target.performance_history[-5:]) / min(5, len(target.performance_history))
        return recent_performance


class MetaLearningSystem:
    """Implements meta-learning (learning to learn)"""
    
    def __init__(self):
        self.learning_strategies: Dict[str, Dict[str, Any]] = {}
        self.strategy_performance: Dict[str, List[float]] = {}
        logger.info("Meta-Learning System initialized")
    
    def register_strategy(self, strategy_name: str, strategy_config: Dict[str, Any]):
        """Register a learning strategy"""
        self.learning_strategies[strategy_name] = strategy_config
        self.strategy_performance[strategy_name] = []
        logger.debug(f"Registered learning strategy: {strategy_name}")
    
    def evaluate_strategy(self, strategy_name: str, performance: float):
        """Evaluate a learning strategy's performance"""
        if strategy_name in self.strategy_performance:
            self.strategy_performance[strategy_name].append(performance)
            logger.debug(f"Strategy {strategy_name} performance: {performance:.3f}")
    
    def select_best_strategy(self, task_context: Dict[str, Any]) -> str:
        """Select the best learning strategy for a given context"""
        if not self.strategy_performance:
            return "default"
        
        # Select strategy with highest average performance
        best_strategy = max(
            self.strategy_performance.items(),
            key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0.0
        )[0]
        
        logger.info(f"Selected strategy: {best_strategy}")
        return best_strategy
    
    def adapt_strategy(self, strategy_name: str, adaptation: Dict[str, Any]):
        """Adapt a learning strategy based on feedback"""
        if strategy_name in self.learning_strategies:
            self.learning_strategies[strategy_name].update(adaptation)
            logger.info(f"Adapted strategy: {strategy_name}")


class LearningModule:
    """Main learning module integrating all learning systems"""
    
    def __init__(self):
        self.online_learning = OnlineLearningSystem()
        self.reinforcement_learning = ReinforcementLearningSystem()
        self.transfer_learning = TransferLearningSystem()
        self.meta_learning = MetaLearningSystem()
        logger.info("Learning Module initialized")
    
    def learn(self, learning_mode: LearningMode, **kwargs) -> Dict[str, Any]:
        """Learn using specified mode"""
        if learning_mode == LearningMode.ONLINE:
            interaction = kwargs.get("interaction", {})
            feedback = kwargs.get("feedback")
            return self.online_learning.learn_from_interaction(interaction, feedback)
            
        elif learning_mode == LearningMode.REINFORCEMENT:
            state = kwargs.get("state", {})
            action = kwargs.get("action", "")
            reward = kwargs.get("reward", 0.0)
            next_state = kwargs.get("next_state")
            done = kwargs.get("done", False)
            
            exp_id = self.reinforcement_learning.add_experience(state, action, reward, next_state, done)
            return {"experience_id": exp_id}
            
        elif learning_mode == LearningMode.TRANSFER:
            source_task_id = kwargs.get("source_task_id", "")
            target_task_id = kwargs.get("target_task_id", "")
            return self.transfer_learning.transfer_knowledge(source_task_id, target_task_id)
            
        else:
            raise ValueError(f"Unsupported learning mode: {learning_mode}")
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about learning systems"""
        return {
            "online_learning": {
                "patterns_learned": len(self.online_learning.knowledge_base),
                "total_interactions": len(self.online_learning.interaction_history),
                "learning_rate": self.online_learning.learning_rate
            },
            "reinforcement_learning": {
                "q_table_size": len(self.reinforcement_learning.q_table),
                "experience_replay_size": len(self.reinforcement_learning.experience_replay),
                "exploration_rate": self.reinforcement_learning.exploration_rate
            },
            "transfer_learning": {
                "source_tasks": len(self.transfer_learning.source_tasks),
                "target_tasks": len(self.transfer_learning.target_tasks),
                "transfer_mappings": len(self.transfer_learning.transfer_mappings)
            },
            "meta_learning": {
                "registered_strategies": len(self.meta_learning.learning_strategies),
                "evaluated_strategies": len(self.meta_learning.strategy_performance)
            }
        }
