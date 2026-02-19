"""Coordinate multiple AGI agents for complex multi-step reasoning."""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class AgentTask:
    """A unit of work dispatched to one or more agents."""
    text: str
    context: Dict[str, Any] = field(default_factory=dict)
    task_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    priority: int = 5   # 1 (highest) to 10 (lowest)


@dataclass
class AgentResult:
    """The output produced by an agent or aggregated from multiple agents."""
    task_id: str
    agent_name: str
    output: str
    confidence: float          # 0-1
    latency_ms: float
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AGIOrchestrator:
    """Register agents and dispatch tasks for single-agent or multi-agent reasoning."""

    def __init__(self) -> None:
        # name -> callable(task: AgentTask) -> AgentResult
        self._agents: Dict[str, Callable[[AgentTask], AgentResult]] = {}
        self._agent_stats: Dict[str, Dict[str, Any]] = {}
        logger.info("AGIOrchestrator initialised.")

    def register_agent(self, name: str, agent: Callable[[AgentTask], AgentResult]) -> None:
        """Register an agent callable under *name*."""
        self._agents[name] = agent
        self._agent_stats[name] = {"calls": 0, "errors": 0, "total_latency_ms": 0.0}
        logger.info("Agent registered: %s", name)

    def dispatch(self, task_text: str, context: Optional[Dict] = None) -> AgentResult:
        """Dispatch a task to the best available agent."""
        context = context or {}
        task = AgentTask(text=task_text, context=context)

        if not self._agents:
            return AgentResult(task_id=task.task_id, agent_name="none",
                               output="No agents registered.", confidence=0.0,
                               latency_ms=0.0, success=False, error="No agents available.")

        # Simple strategy: choose the agent with the fewest calls (load balancing)
        chosen = min(self._agents, key=lambda n: self._agent_stats[n]["calls"])
        return self._call_agent(chosen, task)

    def _call_agent(self, name: str, task: AgentTask) -> AgentResult:
        t0 = time.monotonic()
        stats = self._agent_stats[name]
        stats["calls"] += 1
        try:
            result = self._agents[name](task)
        except Exception as exc:  # noqa: BLE001
            stats["errors"] += 1
            latency = (time.monotonic() - t0) * 1000
            logger.exception("Agent %s raised an error.", name)
            return AgentResult(task_id=task.task_id, agent_name=name, output="",
                               confidence=0.0, latency_ms=round(latency, 2),
                               success=False, error=str(exc))
        latency = (time.monotonic() - t0) * 1000
        stats["total_latency_ms"] += latency
        result.latency_ms = round(latency, 2)
        logger.debug("Agent %s completed in %.1f ms", name, latency)
        return result

    def multi_agent_reasoning(self, problem: str, agents: List[str]) -> AgentResult:
        """Run *problem* through each listed agent and synthesise the results."""
        task = AgentTask(text=problem)
        results: List[AgentResult] = []
        for name in agents:
            if name in self._agents:
                results.append(self._call_agent(name, task))
            else:
                logger.warning("Agent %s not registered — skipping.", name)

        if not results:
            return AgentResult(task_id=task.task_id, agent_name="orchestrator",
                               output="No valid agents provided.", confidence=0.0, latency_ms=0.0,
                               success=False)

        synthesised = self.synthesize_results(results)
        avg_confidence = sum(r.confidence for r in results) / len(results)
        total_latency = sum(r.latency_ms for r in results)
        return AgentResult(task_id=task.task_id, agent_name="orchestrator",
                           output=synthesised, confidence=round(avg_confidence, 3),
                           latency_ms=round(total_latency, 2),
                           metadata={"contributing_agents": agents, "result_count": len(results)})

    def synthesize_results(self, results: List[AgentResult]) -> str:
        """Merge multiple agent outputs into a single coherent response."""
        successful = [r for r in results if r.success and r.output]
        if not successful:
            return "No successful results to synthesise."
        if len(successful) == 1:
            return successful[0].output
        parts = [f"[{r.agent_name}]: {r.output}" for r in successful]
        return "Combined reasoning:\n" + "\n".join(parts)

    def get_agent_status(self) -> Dict:
        """Return live stats for all registered agents."""
        status = {}
        for name, stats in self._agent_stats.items():
            calls = stats["calls"]
            avg_lat = (stats["total_latency_ms"] / calls) if calls else 0.0
            status[name] = {
                "calls": calls, "errors": stats["errors"],
                "avg_latency_ms": round(avg_lat, 2),
                "error_rate": round(stats["errors"] / max(calls, 1), 3),
            }
        return status
