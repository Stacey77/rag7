"""Automated build pipeline orchestration with stages and security gates."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Callable, Awaitable

from loguru import logger


class StageStatus(Enum):
    """Status of a pipeline stage."""

    PENDING = auto()
    RUNNING = auto()
    PASSED = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class PipelineStage:
    """A single build pipeline stage.

    Attributes:
        name: Stage name.
        handler: Async callable that executes the stage.
        required: If ``True``, failure blocks subsequent stages.
        timeout_s: Maximum execution time in seconds.
    """

    name: str
    handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]
    required: bool = True
    timeout_s: float = 300.0


@dataclass
class StageResult:
    """Result of a single pipeline stage execution.

    Attributes:
        stage_name: Name of the executed stage.
        status: Execution outcome.
        output: Stage output data.
        duration_ms: Execution time.
        error: Error message if failed.
        started_at: UTC start timestamp.
    """

    stage_name: str
    status: StageStatus
    output: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0
    error: str = ""
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BuildResult:
    """Aggregated result of a full build pipeline run.

    Attributes:
        build_id: Unique build identifier.
        pipeline_name: Name of the pipeline.
        overall_status: Aggregate pass/fail status.
        stage_results: Ordered stage results.
        total_duration_ms: Total pipeline duration.
        completed_at: UTC completion timestamp.
    """

    build_id: str
    pipeline_name: str
    overall_status: StageStatus
    stage_results: list[StageResult]
    total_duration_ms: float
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BuildPipeline:
    """Automated build orchestration with ordered stages and security gates.

    Stages are executed sequentially; a required stage failure halts
    subsequent stages.

    Attributes:
        stages: Ordered list of pipeline stages.
        build_history: Log of completed build results.
    """

    def __init__(self, name: str = "trading-platform") -> None:
        """Initialise the build pipeline.

        Args:
            name: Pipeline name for identification.
        """
        self.name = name
        self.stages: list[PipelineStage] = []
        self.build_history: list[BuildResult] = []
        self._build_counter = 0
        logger.info("BuildPipeline '{}' initialised", name)

    def add_stage(
        self,
        name: str,
        handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]],
        required: bool = True,
        timeout_s: float = 300.0,
    ) -> None:
        """Add a stage to the pipeline.

        Args:
            name: Stage name.
            handler: Async callable receiving context dict, returning result dict.
            required: Whether failure should halt the pipeline.
            timeout_s: Stage execution timeout.
        """
        self.stages.append(PipelineStage(name=name, handler=handler, required=required, timeout_s=timeout_s))
        logger.debug("Stage '{}' added to pipeline '{}'", name, self.name)

    async def run(self, context: dict[str, Any] | None = None) -> BuildResult:
        """Execute the pipeline.

        Args:
            context: Initial context data passed to all stages.

        Returns:
            :class:`BuildResult` with all stage outcomes.
        """
        self._build_counter += 1
        build_id = f"build_{self._build_counter:06d}"
        context = dict(context or {})
        pipeline_start = time.monotonic()
        stage_results: list[StageResult] = []
        overall_status = StageStatus.PASSED
        halted = False

        logger.info("Build {} starting: '{}' ({} stages)", build_id, self.name, len(self.stages))

        for stage in self.stages:
            if halted:
                stage_results.append(StageResult(
                    stage_name=stage.name,
                    status=StageStatus.SKIPPED,
                ))
                continue

            result = await self._execute_stage(stage, context)
            stage_results.append(result)
            context.update(result.output)

            if result.status == StageStatus.FAILED:
                if stage.required:
                    overall_status = StageStatus.FAILED
                    halted = True
                    logger.error("Required stage '{}' failed — pipeline halted", stage.name)

        total_ms = (time.monotonic() - pipeline_start) * 1000
        build = BuildResult(
            build_id=build_id,
            pipeline_name=self.name,
            overall_status=overall_status,
            stage_results=stage_results,
            total_duration_ms=round(total_ms, 2),
        )
        self.build_history.append(build)
        log = logger.info if overall_status == StageStatus.PASSED else logger.error
        log("Build {} {}: {} stages, {:.0f}ms", build_id, overall_status.name, len(stage_results), total_ms)
        return build

    async def _execute_stage(
        self,
        stage: PipelineStage,
        context: dict[str, Any],
    ) -> StageResult:
        """Execute a single pipeline stage with timeout handling.

        Args:
            stage: Stage specification.
            context: Current pipeline context.

        Returns:
            :class:`StageResult`.
        """
        start = time.monotonic()
        started_at = datetime.now(timezone.utc)
        logger.info("Stage '{}' starting", stage.name)

        try:
            output = await asyncio.wait_for(stage.handler(context), timeout=stage.timeout_s)
            duration_ms = (time.monotonic() - start) * 1000
            return StageResult(
                stage_name=stage.name,
                status=StageStatus.PASSED,
                output=output or {},
                duration_ms=round(duration_ms, 2),
                started_at=started_at,
            )
        except asyncio.TimeoutError:
            duration_ms = (time.monotonic() - start) * 1000
            logger.error("Stage '{}' timed out after {}s", stage.name, stage.timeout_s)
            return StageResult(
                stage_name=stage.name,
                status=StageStatus.FAILED,
                duration_ms=round(duration_ms, 2),
                error=f"Timeout after {stage.timeout_s}s",
                started_at=started_at,
            )
        except Exception as exc:
            duration_ms = (time.monotonic() - start) * 1000
            logger.error("Stage '{}' failed: {}", stage.name, exc)
            return StageResult(
                stage_name=stage.name,
                status=StageStatus.FAILED,
                duration_ms=round(duration_ms, 2),
                error=str(exc),
                started_at=started_at,
            )

    @staticmethod
    def make_simulated_stage(name: str, should_fail: bool = False) -> Callable:
        """Factory for a simulated stage handler.

        Args:
            name: Stage name for labelling.
            should_fail: Whether to simulate a failure.

        Returns:
            Async stage handler callable.
        """
        async def _handler(context: dict[str, Any]) -> dict[str, Any]:
            await asyncio.sleep(0)
            if should_fail:
                raise RuntimeError(f"Simulated failure in stage '{name}'")
            return {f"{name}_passed": True}

        return _handler
