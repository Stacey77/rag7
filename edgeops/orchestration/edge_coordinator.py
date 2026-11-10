"""Multi-edge coordination with topology management and task distribution."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Callable, Awaitable

import numpy as np
from loguru import logger


class NodeRole(Enum):
    """Role of an edge node in the topology."""

    PRIMARY = auto()
    SECONDARY = auto()
    GATEWAY = auto()
    LEAF = auto()


@dataclass
class EdgeNode:
    """An edge node in the coordinator's topology.

    Attributes:
        node_id: Unique identifier.
        address: Network address (host:port).
        role: Node role in the topology.
        capacity: Normalised capacity score (0–1).
        current_load: Normalised current load (0–1).
        tags: Classification tags.
        registered_at: UTC registration timestamp.
        last_heartbeat: UTC last heartbeat timestamp.
        online: Whether the node is reachable.
    """

    node_id: str
    address: str
    role: NodeRole
    capacity: float
    current_load: float = 0.0
    tags: list[str] = field(default_factory=list)
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_heartbeat: datetime | None = None
    online: bool = True

    @property
    def available_capacity(self) -> float:
        """Available capacity (capacity − current_load)."""
        return max(0.0, self.capacity - self.current_load)


@dataclass
class DistributedTask:
    """A task to be distributed across edge nodes.

    Attributes:
        task_id: Unique identifier.
        task_type: Category/type label.
        payload: Task input data.
        required_capacity: Minimum available capacity needed.
        affinity_tags: Preferred node tags.
        timeout_s: Task execution deadline in seconds.
    """

    task_id: str
    task_type: str
    payload: Any
    required_capacity: float = 0.1
    affinity_tags: list[str] = field(default_factory=list)
    timeout_s: float = 30.0


@dataclass
class TaskResult:
    """Result of a distributed task execution.

    Attributes:
        task_id: Corresponding task identifier.
        node_id: Node that executed the task.
        success: Whether execution succeeded.
        result: Task output.
        latency_ms: Execution time.
        executed_at: UTC timestamp.
    """

    task_id: str
    node_id: str
    success: bool
    result: Any
    latency_ms: float
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EdgeCoordinator:
    """Multi-edge node coordinator with topology and task distribution.

    Manages an overlay network of edge nodes, performs health-aware
    task routing, and provides topology views.

    Attributes:
        nodes: Registered nodes keyed by node_id.
        task_history: Completed task results.
        _routing_strategy: Task routing strategy (``"least_loaded"`` or ``"round_robin"``).
        _rr_index: Round-robin counter.
    """

    def __init__(self, routing_strategy: str = "least_loaded") -> None:
        """Initialise the edge coordinator.

        Args:
            routing_strategy: ``"least_loaded"`` or ``"round_robin"``.

        Raises:
            ValueError: If ``routing_strategy`` is unknown.
        """
        valid_strategies = {"least_loaded", "round_robin"}
        if routing_strategy not in valid_strategies:
            raise ValueError(
                f"routing_strategy must be one of {valid_strategies}, got '{routing_strategy}'"
            )

        self.nodes: dict[str, EdgeNode] = {}
        self.task_history: list[TaskResult] = []
        self._routing_strategy = routing_strategy
        self._rr_index = 0
        logger.info("EdgeCoordinator initialised (strategy='{}')", routing_strategy)

    def register_node(
        self,
        address: str,
        role: NodeRole = NodeRole.SECONDARY,
        capacity: float = 1.0,
        tags: list[str] | None = None,
    ) -> EdgeNode:
        """Register an edge node in the topology.

        Args:
            address: Network address string.
            role: Node role.
            capacity: Normalised capacity (0–1).
            tags: Classification tags.

        Returns:
            The registered :class:`EdgeNode`.

        Raises:
            ValueError: If ``capacity`` is not in (0, 1].
        """
        if not 0 < capacity <= 1.0:
            raise ValueError(f"capacity must be in (0, 1], got {capacity}")

        node_id = f"node_{uuid.uuid4().hex[:8]}"
        node = EdgeNode(
            node_id=node_id,
            address=address,
            role=role,
            capacity=capacity,
            tags=tags or [],
        )
        self.nodes[node_id] = node
        logger.info("Edge node registered: {} @ {} (role={})", node_id, address, role.name)
        return node

    def route_task(self, task: DistributedTask) -> EdgeNode | None:
        """Select the best node for a task using the routing strategy.

        Args:
            task: Task requiring routing.

        Returns:
            Selected :class:`EdgeNode`, or ``None`` if no suitable node found.
        """
        candidates = [
            n for n in self.nodes.values()
            if n.online and n.available_capacity >= task.required_capacity
        ]

        if task.affinity_tags:
            preferred = [
                n for n in candidates
                if any(tag in n.tags for tag in task.affinity_tags)
            ]
            if preferred:
                candidates = preferred

        if not candidates:
            logger.warning("No suitable nodes for task '{}' (required_capacity={})", task.task_id, task.required_capacity)
            return None

        if self._routing_strategy == "least_loaded":
            return min(candidates, key=lambda n: n.current_load)
        else:  # round_robin
            node = candidates[self._rr_index % len(candidates)]
            self._rr_index += 1
            return node

    async def distribute_task(
        self,
        task: DistributedTask,
        executor: Callable[[EdgeNode, DistributedTask], Awaitable[Any]] | None = None,
    ) -> TaskResult:
        """Distribute and execute a task on the best available node.

        Args:
            task: Task to distribute.
            executor: Async callable ``(node, task) → result``.  Uses a
                simulated executor when ``None``.

        Returns:
            :class:`TaskResult` from the executing node.

        Raises:
            RuntimeError: If no suitable node is available.
        """
        node = self.route_task(task)
        if node is None:
            raise RuntimeError(f"No suitable node for task '{task.task_id}'")

        import time
        start = time.monotonic()
        node.current_load = min(1.0, node.current_load + task.required_capacity)

        try:
            exec_fn = executor or self._default_executor
            result_data = await asyncio.wait_for(
                exec_fn(node, task), timeout=task.timeout_s
            )
            success = True
        except Exception as exc:
            result_data = str(exc)
            success = False
            logger.error("Task '{}' failed on node '{}': {}", task.task_id, node.node_id, exc)
        finally:
            node.current_load = max(0.0, node.current_load - task.required_capacity)

        latency_ms = (time.monotonic() - start) * 1000
        tr = TaskResult(
            task_id=task.task_id,
            node_id=node.node_id,
            success=success,
            result=result_data,
            latency_ms=round(latency_ms, 2),
        )
        self.task_history.append(tr)
        logger.debug("Task '{}' → node '{}': {} ({:.1f}ms)", task.task_id, node.node_id, "OK" if success else "FAIL", latency_ms)
        return tr

    async def broadcast(
        self,
        payload: Any,
        node_ids: list[str] | None = None,
    ) -> dict[str, bool]:
        """Broadcast a payload to all (or specified) online nodes.

        Args:
            payload: Data to broadcast.
            node_ids: Subset of node IDs to target; all online nodes if None.

        Returns:
            Mapping of node_id to delivery success flag.
        """
        targets = (
            [self.nodes[nid] for nid in node_ids if nid in self.nodes]
            if node_ids
            else [n for n in self.nodes.values() if n.online]
        )

        async def _send(node: EdgeNode) -> tuple[str, bool]:
            await asyncio.sleep(0)
            return node.node_id, True

        results_list = await asyncio.gather(*[_send(n) for n in targets])
        results = dict(results_list)
        logger.debug("Broadcast to {} nodes", len(results))
        return results

    async def _default_executor(self, node: EdgeNode, task: DistributedTask) -> Any:
        """Simulated task executor.

        Args:
            node: Executing node.
            task: Task to execute.

        Returns:
            Simulated result string.
        """
        await asyncio.sleep(0)
        return f"result:{task.task_id}@{node.node_id}"

    def topology_summary(self) -> dict[str, Any]:
        """Return a summary of the current topology.

        Returns:
            Dictionary with node counts, load distribution, and role counts.
        """
        online = [n for n in self.nodes.values() if n.online]
        loads = [n.current_load for n in online]
        return {
            "total_nodes": len(self.nodes),
            "online_nodes": len(online),
            "mean_load": round(float(np.mean(loads)), 4) if loads else 0.0,
            "max_load": round(float(np.max(loads)), 4) if loads else 0.0,
            "roles": {role.name: sum(1 for n in self.nodes.values() if n.role == role)
                      for role in NodeRole},
        }
