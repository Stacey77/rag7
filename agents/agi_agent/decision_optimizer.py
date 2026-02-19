"""Multi-objective optimization for decision making."""
from __future__ import annotations

import logging
import math
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Objective:
    """A single optimization objective."""
    name: str
    weight: float = 1.0
    minimize: bool = True          # True = minimize, False = maximize
    constraint_min: Optional[float] = None
    constraint_max: Optional[float] = None


@dataclass
class Decision:
    """A candidate decision with evaluated objectives."""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    variables: Dict[str, float] = field(default_factory=dict)
    objective_values: Dict[str, float] = field(default_factory=dict)
    aggregate_score: float = 0.0
    rank: int = 0
    feasible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationProblem:
    """Definition of a multi-objective optimization problem."""
    problem_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    objectives: List[Objective] = field(default_factory=list)
    variable_bounds: Dict[str, Tuple[float, float]] = field(default_factory=dict)
    description: str = ""


@dataclass
class OptimizationResult:
    """Result of an optimization run."""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    problem_id: str = ""
    pareto_front: List[Decision] = field(default_factory=list)
    best_decision: Optional[Decision] = None
    iterations: int = 0
    converged: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


def _weighted_sum(decision: Decision, objectives: List[Objective]) -> float:
    total_weight = sum(o.weight for o in objectives) or 1.0
    score = 0.0
    for obj in objectives:
        val = decision.objective_values.get(obj.name, 0.0)
        normalized = val / (abs(val) + 1e-9)
        contribution = obj.weight / total_weight * (normalized if obj.minimize else -normalized)
        score += contribution
    return score


def _dominates(a: Decision, b: Decision, objectives: List[Objective]) -> bool:
    """Return True if decision a Pareto-dominates b."""
    at_least_one_better = False
    for obj in objectives:
        av = a.objective_values.get(obj.name, float("inf"))
        bv = b.objective_values.get(obj.name, float("inf"))
        if obj.minimize:
            if av > bv:
                return False
            if av < bv:
                at_least_one_better = True
        else:
            if av < bv:
                return False
            if av > bv:
                at_least_one_better = True
    return at_least_one_better


def _pareto_front(decisions: List[Decision], objectives: List[Objective]) -> List[Decision]:
    """Extract non-dominated (Pareto-optimal) decisions."""
    front: List[Decision] = []
    for candidate in decisions:
        dominated = False
        for other in decisions:
            if other.decision_id != candidate.decision_id and _dominates(other, candidate, objectives):
                dominated = True
                break
        if not dominated:
            front.append(candidate)
    return front


class RandomSearchOptimizer:
    """Baseline optimizer: random search with constraint checking."""

    def __init__(self, n_samples: int = 200, seed: Optional[int] = None) -> None:
        self.n_samples = n_samples
        self._rng = random.Random(seed)

    def optimize(self, problem: OptimizationProblem,
                 evaluator: Callable[[Dict[str, float]], Dict[str, float]]) -> List[Decision]:
        decisions: List[Decision] = []
        for _ in range(self.n_samples):
            variables = {
                name: self._rng.uniform(lo, hi)
                for name, (lo, hi) in problem.variable_bounds.items()
            }
            obj_values = evaluator(variables)
            feasible = self._check_feasibility(obj_values, problem.objectives)
            d = Decision(variables=variables, objective_values=obj_values, feasible=feasible)
            d.aggregate_score = _weighted_sum(d, problem.objectives)
            decisions.append(d)
        return decisions

    def _check_feasibility(self, obj_values: Dict[str, float], objectives: List[Objective]) -> bool:
        for obj in objectives:
            val = obj_values.get(obj.name, 0.0)
            if obj.constraint_min is not None and val < obj.constraint_min:
                return False
            if obj.constraint_max is not None and val > obj.constraint_max:
                return False
        return True


class GeneticOptimizer:
    """Simple genetic algorithm for multi-objective optimization."""

    def __init__(self, population_size: int = 50, generations: int = 20,
                 mutation_rate: float = 0.1, seed: Optional[int] = None) -> None:
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self._rng = random.Random(seed)

    def optimize(self, problem: OptimizationProblem,
                 evaluator: Callable[[Dict[str, float]], Dict[str, float]]) -> Tuple[List[Decision], int]:
        population = self._init_population(problem, evaluator)
        converged = False
        prev_best = float("inf")

        for gen in range(self.generations):
            population = sorted(population, key=lambda d: d.aggregate_score)
            best = population[0].aggregate_score
            if abs(best - prev_best) < 1e-5:
                converged = True
                break
            prev_best = best

            elites = population[: self.population_size // 4]
            offspring = self._crossover_mutate(elites, problem, evaluator)
            population = elites + offspring
            logger.debug("GA gen %d, best score: %.4f", gen, best)

        return population, self.generations if not converged else gen + 1

    def _init_population(self, problem: OptimizationProblem,
                          evaluator: Callable) -> List[Decision]:
        pop = []
        for _ in range(self.population_size):
            variables = {
                name: self._rng.uniform(lo, hi)
                for name, (lo, hi) in problem.variable_bounds.items()
            }
            obj_values = evaluator(variables)
            d = Decision(variables=variables, objective_values=obj_values)
            d.aggregate_score = _weighted_sum(d, problem.objectives)
            pop.append(d)
        return pop

    def _crossover_mutate(self, elites: List[Decision], problem: OptimizationProblem,
                           evaluator: Callable) -> List[Decision]:
        offspring: List[Decision] = []
        n = self.population_size - len(elites)
        for _ in range(n):
            p1, p2 = self._rng.sample(elites, min(2, len(elites)))
            child_vars: Dict[str, float] = {}
            for name, (lo, hi) in problem.variable_bounds.items():
                gene = p1.variables.get(name, lo) if self._rng.random() > 0.5 else p2.variables.get(name, lo)
                if self._rng.random() < self.mutation_rate:
                    gene = self._rng.uniform(lo, hi)
                child_vars[name] = gene
            obj_values = evaluator(child_vars)
            d = Decision(variables=child_vars, objective_values=obj_values)
            d.aggregate_score = _weighted_sum(d, problem.objectives)
            offspring.append(d)
        return offspring


class DecisionOptimizer:
    """
    High-level multi-objective decision optimizer combining random search,
    genetic algorithms, and Pareto-front analysis.
    """

    def __init__(self) -> None:
        self._random_optimizer = RandomSearchOptimizer(n_samples=200)
        self._ga_optimizer = GeneticOptimizer(population_size=50, generations=20)
        self._history: List[OptimizationResult] = []
        logger.info("DecisionOptimizer initialized")

    def optimize(self, problem: OptimizationProblem,
                 evaluator: Callable[[Dict[str, float]], Dict[str, float]],
                 method: str = "genetic") -> OptimizationResult:
        """Run optimization and return Pareto front + best decision."""
        logger.info("Optimizing problem '%s' using method '%s'", problem.problem_id, method)

        if method == "random":
            decisions = self._random_optimizer.optimize(problem, evaluator)
            iterations = self._random_optimizer.n_samples
            converged = True
        else:
            decisions, iterations = self._ga_optimizer.optimize(problem, evaluator)
            converged = iterations < self._ga_optimizer.generations

        feasible = [d for d in decisions if d.feasible]
        if not feasible:
            feasible = decisions  # relax feasibility if nothing found

        pareto = _pareto_front(feasible, problem.objectives)
        for rank, d in enumerate(sorted(pareto, key=lambda d: d.aggregate_score)):
            d.rank = rank + 1

        best = min(pareto, key=lambda d: d.aggregate_score) if pareto else None

        result = OptimizationResult(
            problem_id=problem.problem_id,
            pareto_front=pareto,
            best_decision=best,
            iterations=iterations,
            converged=converged,
            metadata={"total_evaluated": len(decisions), "pareto_size": len(pareto), "method": method},
        )
        self._history.append(result)
        logger.info("Optimization done: pareto_size=%d, converged=%s", len(pareto), converged)
        return result

    def recommend(self, problem: OptimizationProblem,
                  evaluator: Callable[[Dict[str, float]], Dict[str, float]],
                  n: int = 3) -> List[Decision]:
        """Return top-n recommended decisions."""
        result = self.optimize(problem, evaluator)
        return sorted(result.pareto_front, key=lambda d: d.aggregate_score)[:n]

    def sensitivity_analysis(self, problem: OptimizationProblem,
                              evaluator: Callable[[Dict[str, float]], Dict[str, float]],
                              n_perturbations: int = 50) -> Dict[str, float]:
        """Estimate sensitivity of each variable by random perturbation."""
        base_vars = {name: (lo + hi) / 2 for name, (lo, hi) in problem.variable_bounds.items()}
        base_obj = evaluator(base_vars)
        base_score = sum(base_obj.values())

        sensitivities: Dict[str, List[float]] = {name: [] for name in problem.variable_bounds}
        rng = random.Random(42)
        for _ in range(n_perturbations):
            for name, (lo, hi) in problem.variable_bounds.items():
                perturbed = dict(base_vars)
                perturbed[name] = rng.uniform(lo, hi)
                obj = evaluator(perturbed)
                delta = abs(sum(obj.values()) - base_score)
                sensitivities[name].append(delta)

        return {
            name: sum(deltas) / len(deltas) if deltas else 0.0
            for name, deltas in sensitivities.items()
        }
