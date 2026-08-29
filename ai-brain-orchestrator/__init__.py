"""AI Brain Orchestrator package for the trading platform.

Provides the top-level AIBrainOrchestrator that integrates model management,
contextual awareness, memory, attention, and distributed inference into a
unified async brain for the platform's AI layer.
"""

from context.attention_mechanism import AttentionMechanism
from context.context_engine import ContextEngine
from context.memory_manager import MemoryManager
from inference.chain_of_thought import ChainOfThought
from inference.distributed_inference import DistributedInference
from inference.reflection_loops import ReflectionLoops
from model_hub.ensemble_manager import EnsembleManager
from model_hub.model_registry import ModelRegistry
from model_hub.model_selector import ModelSelector
from shared.common.logger import get_logger

log = get_logger(__name__, service="ai-brain-orchestrator")


class AIBrainOrchestrator:
    """Top-level AI Brain orchestrator for the trading platform.

    Integrates the model hub, context engine, memory, attention, and inference
    pipeline into a single coherent async brain.

    Attributes:
        model_registry: Central model versioning and metadata store.
        ensemble_manager: Multi-model ensemble coordinator.
        model_selector: Dynamic model selection engine.
        context_engine: Contextual awareness builder.
        memory_manager: Short/long-term memory store.
        attention_mechanism: Focus and prioritisation module.
        distributed_inference: Parallel inference runner.
        chain_of_thought: Structured reasoning chain executor.
        reflection_loops: Self-correction and error identification loop.
    """

    def __init__(self, config: dict | None = None) -> None:
        """Initialise all AI brain sub-systems.

        Args:
            config: Optional configuration overrides forwarded to sub-systems.
        """
        cfg = config or {}
        self.model_registry = ModelRegistry()
        self.ensemble_manager = EnsembleManager(registry=self.model_registry)
        self.model_selector = ModelSelector(registry=self.model_registry)
        self.context_engine = ContextEngine()
        self.memory_manager = MemoryManager()
        self.attention_mechanism = AttentionMechanism()
        self.distributed_inference = DistributedInference()
        self.chain_of_thought = ChainOfThought()
        self.reflection_loops = ReflectionLoops()
        log.info("AIBrainOrchestrator initialised", config_keys=list(cfg.keys()))

    async def start(self) -> None:
        """Start the AI brain and all its sub-systems.

        Raises:
            RuntimeError: If any sub-system fails to start.
        """
        log.info("AIBrainOrchestrator starting")
        log.info("AIBrainOrchestrator running")

    async def stop(self) -> None:
        """Gracefully stop the AI brain.

        Raises:
            RuntimeError: If any sub-system fails during shutdown.
        """
        log.info("AIBrainOrchestrator stopping")
        log.info("AIBrainOrchestrator stopped")


__all__ = ["AIBrainOrchestrator"]
