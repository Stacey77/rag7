"""Safe rollback mechanism with health checks for trading platform deployments."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Callable, Awaitable

from loguru import logger


class RollbackStatus(Enum):
    """Status of a rollback operation."""

    SUCCESS = auto()
    FAILED = auto()
    PARTIAL = auto()
    IN_PROGRESS = auto()


@dataclass
class DeploymentSnapshot:
    """Snapshot of a deployment that can be rolled back to.

    Attributes:
        snapshot_id: Unique identifier.
        service_name: Service this snapshot belongs to.
        version: Deployment version string.
        config: Service configuration at the time of snapshot.
        health_check_url: URL for health verification.
        created_at: UTC creation timestamp.
    """

    snapshot_id: str
    service_name: str
    version: str
    config: dict[str, Any]
    health_check_url: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RollbackResult:
    """Result of a rollback operation.

    Attributes:
        rollback_id: Unique identifier.
        service_name: Service that was rolled back.
        from_version: Version rolled back from.
        to_version: Version rolled back to.
        status: Rollback outcome.
        health_verified: Whether health check passed post-rollback.
        steps_completed: Number of rollback steps completed.
        error: Error message if failed.
        duration_ms: Total operation duration.
        completed_at: UTC timestamp.
    """

    rollback_id: str
    service_name: str
    from_version: str
    to_version: str
    status: RollbackStatus
    health_verified: bool
    steps_completed: int
    error: str = ""
    duration_ms: float = 0.0
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RollbackMechanism:
    """Safe rollback with health checks for trading platform deployments.

    Manages deployment snapshots and orchestrates rollback procedures
    with mandatory health verification at each step.

    Attributes:
        snapshots: Deployment snapshots keyed by snapshot_id.
        rollback_history: All completed rollback results.
        _health_checker: Optional async health check callable.
    """

    def __init__(
        self,
        health_checker: Callable[[str], Awaitable[bool]] | None = None,
    ) -> None:
        """Initialise the rollback mechanism.

        Args:
            health_checker: Async callable ``(url) → bool`` for health
                verification.  Uses a simulated checker when ``None``.
        """
        self.snapshots: dict[str, DeploymentSnapshot] = {}
        self.rollback_history: list[RollbackResult] = []
        self._health_checker = health_checker or self._default_health_check
        self._rollback_counter = 0
        logger.info("RollbackMechanism initialised")

    def capture_snapshot(
        self,
        service_name: str,
        version: str,
        config: dict[str, Any],
        health_check_url: str = "",
    ) -> DeploymentSnapshot:
        """Capture a deployment snapshot for future rollback.

        Args:
            service_name: Service identifier.
            version: Current deployment version.
            config: Current service configuration.
            health_check_url: Health check endpoint URL.

        Returns:
            The created :class:`DeploymentSnapshot`.
        """
        snapshot_id = f"snap_{service_name}_{version}_{int(time.time())}"
        snapshot = DeploymentSnapshot(
            snapshot_id=snapshot_id,
            service_name=service_name,
            version=version,
            config=dict(config),
            health_check_url=health_check_url,
        )
        self.snapshots[snapshot_id] = snapshot
        logger.info("Snapshot captured: {} v{} (id={})", service_name, version, snapshot_id)
        return snapshot

    def get_latest_snapshot(self, service_name: str) -> DeploymentSnapshot | None:
        """Get the most recent snapshot for a service.

        Args:
            service_name: Service identifier.

        Returns:
            Most recent :class:`DeploymentSnapshot` or ``None``.
        """
        service_snaps = [
            s for s in self.snapshots.values()
            if s.service_name == service_name
        ]
        if not service_snaps:
            return None
        return max(service_snaps, key=lambda s: s.created_at)

    async def rollback(
        self,
        service_name: str,
        current_version: str,
        target_snapshot_id: str | None = None,
        max_health_retries: int = 3,
    ) -> RollbackResult:
        """Execute a rollback for a service.

        Args:
            service_name: Service to roll back.
            current_version: Currently deployed version.
            target_snapshot_id: Snapshot to roll back to; uses the most
                recent snapshot if ``None``.
            max_health_retries: Health check retry count after rollback.

        Returns:
            :class:`RollbackResult` with outcome.

        Raises:
            RuntimeError: If no snapshot is available for the service.
        """
        self._rollback_counter += 1
        rollback_id = f"rollback_{self._rollback_counter:06d}"
        start = time.monotonic()

        if target_snapshot_id:
            snapshot = self.snapshots.get(target_snapshot_id)
        else:
            snapshot = self.get_latest_snapshot(service_name)

        if snapshot is None:
            raise RuntimeError(
                f"No snapshot available for service '{service_name}'. "
                "Capture a snapshot before attempting rollback."
            )

        logger.warning(
            "Rollback {}: '{}' {} → {}",
            rollback_id,
            service_name,
            current_version,
            snapshot.version,
        )

        steps = 0
        try:
            # Step 1: Stop traffic to the current version
            await self._stop_traffic(service_name, current_version)
            steps += 1

            # Step 2: Deploy the previous version
            await self._deploy_version(service_name, snapshot)
            steps += 1

            # Step 3: Verify health
            health_ok = False
            for attempt in range(1, max_health_retries + 1):
                health_ok = await self._health_checker(snapshot.health_check_url)
                if health_ok:
                    logger.info("Health check passed after rollback (attempt {})", attempt)
                    break
                logger.warning("Health check attempt {}/{} failed", attempt, max_health_retries)
                await asyncio.sleep(0)

            steps += 1
            status = RollbackStatus.SUCCESS if health_ok else RollbackStatus.PARTIAL

        except Exception as exc:
            logger.error("Rollback {} failed at step {}: {}", rollback_id, steps + 1, exc)
            status = RollbackStatus.FAILED
            health_ok = False

        duration_ms = (time.monotonic() - start) * 1000
        result = RollbackResult(
            rollback_id=rollback_id,
            service_name=service_name,
            from_version=current_version,
            to_version=snapshot.version,
            status=status,
            health_verified=health_ok,
            steps_completed=steps,
            duration_ms=round(duration_ms, 2),
        )
        self.rollback_history.append(result)
        log = logger.info if status == RollbackStatus.SUCCESS else logger.error
        log(
            "Rollback {} {}: {} → {} (health={})",
            rollback_id,
            status.name,
            current_version,
            snapshot.version,
            health_ok,
        )
        return result

    async def _stop_traffic(self, service_name: str, version: str) -> None:
        """Simulate stopping traffic to a service version.

        Args:
            service_name: Service identifier.
            version: Version to stop.
        """
        await asyncio.sleep(0)
        logger.debug("Traffic stopped for '{}' v{}", service_name, version)

    async def _deploy_version(self, service_name: str, snapshot: DeploymentSnapshot) -> None:
        """Simulate deploying a snapshot version.

        Args:
            service_name: Service identifier.
            snapshot: Snapshot to restore.
        """
        await asyncio.sleep(0)
        logger.debug("Deploying '{}' v{} from snapshot {}", service_name, snapshot.version, snapshot.snapshot_id)

    async def _default_health_check(self, url: str) -> bool:
        """Simulated health check.

        Args:
            url: Health check URL (unused in simulation).

        Returns:
            Always ``True`` in simulation.
        """
        await asyncio.sleep(0)
        return True
