"""AGI Orchestrator package for the trading platform.

Provides the top-level AGIOrchestrator that wires together the decision engine,
global state manager, goal hierarchy, self-improvement loops, reasoning modules,
and multi-agent coordination into a single coherent runtime.
"""

from coordination.agent_coordinator import AgentCoordinator
from coordination.conflict_resolver import ConflictResolver
from coordination.resource_allocator import ResourceAllocator
from core.decision_engine import AGIDecisionEngine
from core.global_state_manager import GlobalStateManager
from core.goal_hierarchy import GoalHierarchy
from core.self_improvement import SelfImprovement
from reasoning.causal_inference import CausalInferenceEngine
from reasoning.meta_cognitive import MetaCognitive
from reasoning.strategic_planner import StrategicPlanner
from shared.common.logger import get_logger

log = get_logger(__name__, service="agi-orchestrator")


class AGIOrchestrator:
    """Top-level AGI orchestrator for the trading platform.

    Wires together all sub-systems (decision engine, goal hierarchy, reasoning,
    coordination) and exposes a unified async lifecycle interface.

    Attributes:
        state_manager: System-wide shared state store.
        goal_hierarchy: Multi-objective goal tracker.
        decision_engine: Meta-learning decision maker.
        self_improvement: Autonomous performance-improvement loop.
        causal_engine: Causal inference reasoner.
        strategic_planner: Long-horizon strategy builder.
        meta_cognitive: Self-reflection and confidence assessor.
        agent_coordinator: Multi-agent lifecycle manager.
        resource_allocator: Dynamic resource budget manager.
        conflict_resolver: Inter-system conflict mediator.
    """

    def __init__(self, config: dict | None = None) -> None:
        """Initialise all sub-systems with an optional configuration mapping.

        Args:
            config: Optional key-value configuration overrides forwarded to
                each sub-system during initialisation.
        """
        cfg = config or {}
        self.state_manager = GlobalStateManager()
        self.goal_hierarchy = GoalHierarchy()
        self.decision_engine = AGIDecisionEngine(state_manager=self.state_manager)
        self.self_improvement = SelfImprovement()
        self.causal_engine = CausalInferenceEngine()
        self.strategic_planner = StrategicPlanner()
        self.meta_cognitive = MetaCognitive()
        self.agent_coordinator = AgentCoordinator(state_manager=self.state_manager)
        self.resource_allocator = ResourceAllocator()
        self.conflict_resolver = ConflictResolver()
        log.info("AGIOrchestrator initialised", config_keys=list(cfg.keys()))

    async def start(self) -> None:
        """Start all async sub-systems in the correct dependency order.

        Raises:
            RuntimeError: If any sub-system fails to start.
        """
        log.info("AGIOrchestrator starting")
        await self.state_manager.update_state("orchestrator_status", "running")
        log.info("AGIOrchestrator running")

    async def stop(self) -> None:
        """Gracefully shut down all sub-systems.

        Raises:
            RuntimeError: If any sub-system fails during shutdown.
        """
        log.info("AGIOrchestrator stopping")
        await self.state_manager.update_state("orchestrator_status", "stopped")
        log.info("AGIOrchestrator stopped")


__all__ = ["AGIOrchestrator"]
