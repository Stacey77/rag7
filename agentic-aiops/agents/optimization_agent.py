"""Resource optimisation agent for trading infrastructure."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class ResourceProfile:
    """Current resource usage profile for a component.

    Attributes:
        component: Component identifier.
        cpu_percent: CPU utilisation percentage.
        memory_mb: Memory used in MB.
        memory_limit_mb: Configured memory limit.
        disk_io_mbps: Disk I/O throughput in MB/s.
        network_mbps: Network throughput in MB/s.
        thread_count: Number of active threads.
        profiled_at: UTC timestamp.
    """

    component: str
    cpu_percent: float
    memory_mb: float
    memory_limit_mb: float
    disk_io_mbps: float
    network_mbps: float
    thread_count: int
    profiled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def memory_utilisation(self) -> float:
        """Memory utilisation fraction (0–1)."""
        return self.memory_mb / (self.memory_limit_mb + 1e-6)


@dataclass
class Bottleneck:
    """A detected resource bottleneck.

    Attributes:
        component: Affected component.
        resource: Resource type (``"cpu"``, ``"memory"``, ``"disk"``, ``"network"``).
        severity: Severity score 0–1.
        description: Human-readable bottleneck description.
        detected_at: UTC timestamp.
    """

    component: str
    resource: str
    severity: float
    description: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class OptimizationAction:
    """A recommended optimisation action.

    Attributes:
        component: Target component.
        action_type: Category (``"scale_up"``, ``"rebalance"``, ``"tune"``, etc.).
        description: Specific action description.
        expected_improvement_pct: Estimated percentage improvement.
        risk_level: ``"low"``, ``"medium"``, or ``"high"``.
        applied: Whether the action has been applied.
    """

    component: str
    action_type: str
    description: str
    expected_improvement_pct: float
    risk_level: str = "low"
    applied: bool = False


class OptimizationAgent:
    """Resource optimisation agent for trading platform components.

    Profiles resource usage, identifies bottlenecks, and recommends or
    executes optimisation actions.

    Attributes:
        profiles: Latest resource profiles per component.
        bottleneck_history: Historical bottleneck detections.
        optimization_history: Applied optimisation actions.
    """

    _CPU_BOTTLENECK_THRESHOLD: float = 80.0
    _MEMORY_BOTTLENECK_THRESHOLD: float = 0.85
    _DISK_IO_BOTTLENECK_THRESHOLD: float = 500.0  # MB/s
    _NETWORK_BOTTLENECK_THRESHOLD: float = 1000.0  # MB/s

    def __init__(self) -> None:
        """Initialise the optimisation agent."""
        self.profiles: dict[str, ResourceProfile] = {}
        self.bottleneck_history: list[Bottleneck] = []
        self.optimization_history: list[OptimizationAction] = []
        logger.info("OptimizationAgent initialised")

    async def profile_usage(self, components: list[str]) -> dict[str, ResourceProfile]:
        """Profile resource usage for the given components.

        Args:
            components: List of component names to profile.

        Returns:
            Mapping of component name to :class:`ResourceProfile`.
        """
        tasks = {c: asyncio.create_task(self._profile_component(c)) for c in components}
        results: dict[str, ResourceProfile] = {}

        for component, task in tasks.items():
            profile = await task
            self.profiles[component] = profile
            results[component] = profile

        logger.debug("Profiled {} components", len(results))
        return results

    async def _profile_component(self, component: str) -> ResourceProfile:
        """Simulate profiling for a single component.

        Args:
            component: Component identifier.

        Returns:
            Simulated :class:`ResourceProfile`.
        """
        await asyncio.sleep(0)
        rng = np.random.default_rng(seed=hash(component) % (2**32))
        return ResourceProfile(
            component=component,
            cpu_percent=round(float(rng.uniform(10, 90)), 2),
            memory_mb=round(float(rng.uniform(256, 4096)), 1),
            memory_limit_mb=4096.0,
            disk_io_mbps=round(float(rng.exponential(100)), 2),
            network_mbps=round(float(rng.exponential(200)), 2),
            thread_count=int(rng.integers(4, 128)),
        )

    async def identify_bottlenecks(
        self,
        profiles: dict[str, ResourceProfile] | None = None,
    ) -> list[Bottleneck]:
        """Identify resource bottlenecks from profiles.

        Args:
            profiles: Profiles to analyse; defaults to ``self.profiles``.

        Returns:
            List of detected :class:`Bottleneck` objects.
        """
        profiles = profiles or self.profiles
        bottlenecks: list[Bottleneck] = []
        await asyncio.sleep(0)

        for component, profile in profiles.items():
            if profile.cpu_percent >= self._CPU_BOTTLENECK_THRESHOLD:
                severity = profile.cpu_percent / 100.0
                bottlenecks.append(Bottleneck(
                    component=component,
                    resource="cpu",
                    severity=round(severity, 2),
                    description=f"CPU at {profile.cpu_percent:.1f}%",
                ))
            if profile.memory_utilisation >= self._MEMORY_BOTTLENECK_THRESHOLD:
                severity = profile.memory_utilisation
                bottlenecks.append(Bottleneck(
                    component=component,
                    resource="memory",
                    severity=round(severity, 2),
                    description=f"Memory at {profile.memory_utilisation:.1%}",
                ))
            if profile.disk_io_mbps >= self._DISK_IO_BOTTLENECK_THRESHOLD:
                severity = min(1.0, profile.disk_io_mbps / 1000.0)
                bottlenecks.append(Bottleneck(
                    component=component,
                    resource="disk",
                    severity=round(severity, 2),
                    description=f"Disk I/O at {profile.disk_io_mbps:.0f} MB/s",
                ))
            if profile.network_mbps >= self._NETWORK_BOTTLENECK_THRESHOLD:
                severity = min(1.0, profile.network_mbps / 10000.0)
                bottlenecks.append(Bottleneck(
                    component=component,
                    resource="network",
                    severity=round(severity, 2),
                    description=f"Network at {profile.network_mbps:.0f} MB/s",
                ))

        self.bottleneck_history.extend(bottlenecks)
        if bottlenecks:
            logger.warning("Identified {} bottleneck(s)", len(bottlenecks))
        else:
            logger.debug("No bottlenecks detected")
        return bottlenecks

    async def optimize(
        self,
        bottlenecks: list[Bottleneck],
        *,
        auto_apply: bool = False,
    ) -> list[OptimizationAction]:
        """Generate and optionally apply optimisation actions.

        Args:
            bottlenecks: Detected bottlenecks to address.
            auto_apply: If ``True``, mark actions as applied immediately.

        Returns:
            List of :class:`OptimizationAction` recommendations.
        """
        actions: list[OptimizationAction] = []

        _action_map: dict[str, tuple[str, str, float]] = {
            "cpu": ("scale_up", "Add CPU cores or horizontal scale-out", 30.0),
            "memory": ("tune", "Increase memory limit or fix memory leak", 40.0),
            "disk": ("rebalance", "Enable read cache or offload to object storage", 25.0),
            "network": ("tune", "Enable network bonding or upgrade NIC", 20.0),
        }

        for bottleneck in bottlenecks:
            action_type, description, improvement = _action_map.get(
                bottleneck.resource, ("investigate", "Manual investigation required", 10.0)
            )
            risk = "high" if bottleneck.severity > 0.9 else "medium" if bottleneck.severity > 0.7 else "low"
            action = OptimizationAction(
                component=bottleneck.component,
                action_type=action_type,
                description=f"{bottleneck.component}: {description}",
                expected_improvement_pct=improvement * bottleneck.severity,
                risk_level=risk,
                applied=auto_apply,
            )
            actions.append(action)

        if auto_apply:
            await asyncio.sleep(0)  # Simulate application
            logger.info("Auto-applied {} optimisation action(s)", len(actions))
        else:
            logger.info("Generated {} optimisation recommendation(s)", len(actions))

        self.optimization_history.extend(actions)
        return actions
