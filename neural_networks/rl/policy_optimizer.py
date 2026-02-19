"""Reinforcement learning policy optimisation using tabular Q-learning."""
from __future__ import annotations
import math
import json
import random
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class State:
    features: Tuple
    def __hash__(self) -> int:
        return hash(self.features)
    def __eq__(self, other: object) -> bool:
        return isinstance(other, State) and self.features == other.features


@dataclass
class Action:
    action_id: int
    params: Dict[str, Any] = field(default_factory=dict)
    def __hash__(self) -> int:
        return hash(self.action_id)
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Action) and self.action_id == other.action_id


@dataclass
class Transition:
    state: State
    action: Action
    reward: float
    next_state: State
    done: bool = False


class ReplayBuffer:
    def __init__(self, capacity: int = 10000) -> None:
        self._buffer: deque = deque(maxlen=capacity)

    def push(self, transition: Transition) -> None:
        self._buffer.append(transition)

    def sample(self, batch_size: int) -> List[Transition]:
        return random.sample(list(self._buffer), min(batch_size, len(self._buffer)))

    def __len__(self) -> int:
        return len(self._buffer)


class PolicyNetwork:
    """Tabular Q-function stored as a nested dict."""

    def __init__(self, n_actions: int, learning_rate: float = 0.1,
                 gamma: float = 0.99) -> None:
        self.n_actions = n_actions
        self.lr = learning_rate
        self.gamma = gamma
        self._q: Dict[Any, List[float]] = {}

    def _get_q(self, state: State) -> List[float]:
        key = state.features
        if key not in self._q:
            self._q[key] = [0.0] * self.n_actions
        return self._q[key]

    def update(self, transition: Transition) -> float:
        q_vals = self._get_q(transition.state)
        next_q = self._get_q(transition.next_state)
        target = transition.reward + (0.0 if transition.done
                                       else self.gamma * max(next_q))
        td_error = target - q_vals[transition.action.action_id]
        q_vals[transition.action.action_id] += self.lr * td_error
        return abs(td_error)

    def best_action(self, state: State) -> int:
        return int(max(range(self.n_actions), key=lambda a: self._get_q(state)[a]))

    def serialize(self) -> Dict:
        return {str(k): v for k, v in self._q.items()}

    def deserialize(self, data: Dict) -> None:
        import ast
        self._q = {ast.literal_eval(k): v for k, v in data.items()}


class PolicyOptimizer:
    def __init__(self, n_actions: int = 4, learning_rate: float = 0.1,
                 gamma: float = 0.99, batch_size: int = 32) -> None:
        self.n_actions = n_actions
        self.batch_size = batch_size
        self.policy = PolicyNetwork(n_actions, learning_rate, gamma)
        self.buffer = ReplayBuffer()
        self._step_count = 0
        self._total_reward = 0.0
        logger.info("PolicyOptimizer initialised (n_actions=%d)", n_actions)

    def observe(self, state: State, action: Action, reward: float,
                next_state: State, done: bool = False) -> None:
        self._total_reward += reward
        self._step_count += 1
        self.buffer.push(Transition(state, action, reward, next_state, done))
        logger.debug("Step %d: reward=%.4f", self._step_count, reward)

    def optimize_step(self) -> Optional[float]:
        if len(self.buffer) < self.batch_size:
            return None
        batch = self.buffer.sample(self.batch_size)
        td_errors = [self.policy.update(t) for t in batch]
        avg_td = sum(td_errors) / len(td_errors)
        logger.debug("Optimize step: avg_td_error=%.4f", avg_td)
        return avg_td

    def get_action(self, state: State, epsilon: float = 0.1) -> Action:
        if random.random() < epsilon:
            action_id = random.randrange(self.n_actions)
            logger.debug("Exploring: random action %d", action_id)
        else:
            action_id = self.policy.best_action(state)
            logger.debug("Exploiting: best action %d", action_id)
        return Action(action_id=action_id)

    def evaluate_policy(self, eval_states: List[State]) -> Dict[str, float]:
        logger.info("Evaluating policy on %d states", len(eval_states))
        q_means = []
        for s in eval_states:
            q_vals = self.policy._get_q(s)
            q_means.append(max(q_vals))
        return {
            "mean_q": round(sum(q_means) / (len(q_means) + 1e-9), 4),
            "max_q": round(max(q_means) if q_means else 0.0, 4),
            "steps": self._step_count,
            "total_reward": round(self._total_reward, 4),
        }

    def save_policy(self, path: str) -> None:
        data = {"q_table": self.policy.serialize(), "n_actions": self.n_actions}
        with open(path, "w") as f:
            json.dump(data, f)
        logger.info("Policy saved to '%s'", path)

    def load_policy(self, path: str) -> None:
        with open(path, "r") as f:
            data = json.load(f)
        self.policy.deserialize(data["q_table"])
        logger.info("Policy loaded from '%s'", path)
