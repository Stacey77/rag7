"""Resource allocation using Q-learning reinforcement learning."""
from __future__ import annotations
import math
import random
import logging
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)


@dataclass
class ResourceState:
    cpu_available: float      # 0.0 – 1.0
    memory_available: float   # 0.0 – 1.0
    queue_depth: int          # pending jobs
    active_tasks: int = 0

    def discretize(self) -> Tuple[int, int, int]:
        cpu_bin = min(9, int(self.cpu_available * 10))
        mem_bin = min(9, int(self.memory_available * 10))
        q_bin = min(9, min(self.queue_depth, 9))
        return (cpu_bin, mem_bin, q_bin)


@dataclass
class ResourceAction:
    cpu_alloc: float     # fraction to allocate (0.0 – 1.0)
    memory_alloc: float  # fraction to allocate (0.0 – 1.0)
    action_id: int = 0


_ACTION_SPACE: List[Tuple[float, float]] = [
    (0.1, 0.1), (0.1, 0.3), (0.3, 0.1), (0.3, 0.3),
    (0.5, 0.3), (0.3, 0.5), (0.5, 0.5), (0.7, 0.5),
    (0.5, 0.7), (0.7, 0.7),
]


class QTable:
    def __init__(self, n_actions: int, lr: float, gamma: float) -> None:
        self.n_actions = n_actions
        self.lr = lr
        self.gamma = gamma
        self._q: Dict[Tuple, List[float]] = {}

    def _get(self, key: Tuple) -> List[float]:
        if key not in self._q:
            self._q[key] = [0.0] * self.n_actions
        return self._q[key]

    def update(self, state_key: Tuple, action_id: int, reward: float,
               next_key: Tuple, done: bool = False) -> None:
        q = self._get(state_key)
        next_q = self._get(next_key)
        target = reward + (0.0 if done else self.gamma * max(next_q))
        q[action_id] += self.lr * (target - q[action_id])

    def best_action(self, key: Tuple) -> int:
        q = self._get(key)
        return int(max(range(self.n_actions), key=lambda a: q[a]))

    def q_values(self, key: Tuple) -> List[float]:
        return self._get(key)


class ResourceAllocator:
    def __init__(self, learning_rate: float = 0.1, gamma: float = 0.95,
                 epsilon: float = 0.2, epsilon_decay: float = 0.995,
                 min_epsilon: float = 0.01) -> None:
        self.n_actions = len(_ACTION_SPACE)
        self.q_table = QTable(self.n_actions, learning_rate, gamma)
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        self._reward_history: List[float] = []
        self._step = 0
        logger.info("ResourceAllocator initialised (n_actions=%d, lr=%.3f)",
                    self.n_actions, learning_rate)

    def compute_reward(self, state: ResourceState, action: ResourceAction,
                       next_state: ResourceState) -> float:
        utilisation = (1.0 - action.cpu_alloc) * 0.4 + (1.0 - action.memory_alloc) * 0.4
        queue_penalty = -0.05 * next_state.queue_depth
        overalloc_penalty = 0.0
        if action.cpu_alloc > state.cpu_available:
            overalloc_penalty -= 0.5
        if action.memory_alloc > state.memory_available:
            overalloc_penalty -= 0.5
        throughput = min(1.0, (state.queue_depth - next_state.queue_depth) * 0.1)
        reward = utilisation + queue_penalty + overalloc_penalty + throughput
        logger.debug("Reward: %.4f (util=%.4f queue=%.4f overalloc=%.4f tp=%.4f)",
                     reward, utilisation, queue_penalty, overalloc_penalty, throughput)
        return reward

    def observe_and_learn(self, state: ResourceState, action: ResourceAction,
                           reward: float, next_state: ResourceState,
                           done: bool = False) -> None:
        s_key = state.discretize()
        ns_key = next_state.discretize()
        self.q_table.update(s_key, action.action_id, reward, ns_key, done)
        self._reward_history.append(reward)
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        self._step += 1
        logger.debug("Step %d: epsilon=%.4f", self._step, self.epsilon)

    def allocate(self, state: ResourceState) -> ResourceAction:
        key = state.discretize()
        if random.random() < self.epsilon:
            action_id = random.randrange(self.n_actions)
            logger.debug("Exploring: random action %d", action_id)
        else:
            action_id = self.q_table.best_action(key)
            logger.debug("Exploiting: action %d", action_id)
        cpu_alloc, mem_alloc = _ACTION_SPACE[action_id]
        cpu_alloc = min(cpu_alloc, state.cpu_available)
        mem_alloc = min(mem_alloc, state.memory_available)
        return ResourceAction(cpu_alloc=cpu_alloc, memory_alloc=mem_alloc,
                               action_id=action_id)

    def get_efficiency_metrics(self) -> Dict[str, float]:
        if not self._reward_history:
            return {"avg_reward": 0.0, "steps": 0, "epsilon": self.epsilon}
        window = self._reward_history[-100:]
        avg = statistics.mean(window)
        std = statistics.stdev(window) if len(window) > 1 else 0.0
        trend = (window[-1] - window[0]) / (len(window) + 1e-9) if len(window) > 1 else 0.0
        return {
            "avg_reward": round(avg, 4),
            "reward_std": round(std, 4),
            "reward_trend": round(trend, 6),
            "epsilon": round(self.epsilon, 4),
            "steps": self._step,
            "q_states": len(self.q_table._q),
        }
