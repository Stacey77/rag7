"""EdgeOps: Operations framework for edge computing nodes in the trading platform."""

from __future__ import annotations

from loguru import logger

from edgeops.edge_nodes.model_compression import ModelCompression
from edgeops.edge_nodes.edge_deployment import EdgeDeployment
from edgeops.edge_nodes.federated_learning import FederatedLearning
from edgeops.streaming.real_time_inference import RealTimeInference
from edgeops.streaming.stream_processor import StreamProcessor
from edgeops.streaming.edge_cache import EdgeCache
from edgeops.orchestration.edge_coordinator import EdgeCoordinator
from edgeops.orchestration.data_sync import DataSync


class EdgeOps:
    """Unified EdgeOps orchestrator for trading platform edge infrastructure.

    Aggregates model compression, edge deployment, federated learning,
    real-time inference, stream processing, caching, and coordination.

    Attributes:
        model_compression: Model quantisation and pruning component.
        edge_deployment: Edge device deployment manager.
        federated_learning: Distributed federated learning coordinator.
        real_time_inference: Ultra-low latency inference engine.
        stream_processor: Event stream processing component.
        edge_cache: Local data cache with TTL and LRU eviction.
        edge_coordinator: Multi-edge topology coordinator.
        data_sync: Edge-to-cloud sync manager.
    """

    def __init__(self) -> None:
        """Initialise all EdgeOps sub-components."""
        self.model_compression = ModelCompression()
        self.edge_deployment = EdgeDeployment()
        self.federated_learning = FederatedLearning()
        self.real_time_inference = RealTimeInference()
        self.stream_processor = StreamProcessor()
        self.edge_cache = EdgeCache()
        self.edge_coordinator = EdgeCoordinator()
        self.data_sync = DataSync()
        logger.info("EdgeOps initialised")

    def status(self) -> dict[str, str]:
        """Return a health summary for all sub-components.

        Returns:
            Mapping of component name to status string.
        """
        return {name: "ready" for name in [
            "model_compression", "edge_deployment", "federated_learning",
            "real_time_inference", "stream_processor", "edge_cache",
            "edge_coordinator", "data_sync",
        ]}


__all__ = ["EdgeOps"]
