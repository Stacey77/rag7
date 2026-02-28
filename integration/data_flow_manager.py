"""Orchestrate DataOps data flows with lineage tracking."""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class DataFlow:
    """Definition of a named data flow pipeline."""
    name: str
    sources: List[str]
    transformations: List[Callable]
    sinks: List[str]
    flow_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    enabled: bool = True


class DataFlowManager:
    """Register, execute, monitor, and trace DataOps flows."""

    def __init__(self) -> None:
        self._flows: Dict[str, DataFlow] = {}
        # name -> list of execution records
        self._exec_history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        # name -> lineage graph {step -> [upstream_steps]}
        self._lineage: Dict[str, Dict[str, List[str]]] = {}
        logger.info("DataFlowManager initialised.")

    def register_flow(self, name: str, sources: List[str],
                      transformations: List[Callable], sinks: List[str]) -> DataFlow:
        """Register a new data flow pipeline."""
        flow = DataFlow(name=name, sources=sources,
                        transformations=transformations, sinks=sinks)
        self._flows[name] = flow
        # Build static lineage graph
        lineage: Dict[str, List[str]] = {}
        prev = list(sources)
        for i, transform in enumerate(transformations):
            step = getattr(transform, "__name__", f"transform_{i}")
            lineage[step] = list(prev)
            prev = [step]
        for sink in sinks:
            lineage[sink] = list(prev)
        self._lineage[name] = lineage
        logger.info("Flow registered: %s (%d transforms, %d sinks)", name, len(transformations), len(sinks))
        return flow

    def execute_flow(self, name: str) -> Dict[str, Any]:
        """Run a registered flow and return an execution report."""
        flow = self._flows.get(name)
        if not flow:
            return {"success": False, "error": f"Flow '{name}' not found."}
        if not flow.enabled:
            return {"success": False, "error": f"Flow '{name}' is paused."}

        t0 = time.monotonic()
        rows_processed = 0
        errors: List[str] = []
        data: Any = None

        # Simulate ingestion
        for source in flow.sources:
            logger.debug("Ingesting from source: %s", source)
            data = {"source": source, "rows": 100}  # stub
            rows_processed += 100

        # Apply transformations
        for transform in flow.transformations:
            try:
                data = transform(data) if data is not None else data
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{getattr(transform, '__name__', 'transform')}: {exc}")
                logger.warning("Transform error: %s", exc)

        # Simulate sink writing
        for sink in flow.sinks:
            logger.debug("Writing to sink: %s", sink)

        latency_ms = round((time.monotonic() - t0) * 1000, 2)
        record = {"run_id": str(uuid4()), "flow": name, "success": not errors,
                  "rows_processed": rows_processed, "errors": errors,
                  "latency_ms": latency_ms, "executed_at": datetime.utcnow().isoformat()}
        self._exec_history[name].append(record)
        logger.info("Flow '%s' executed in %.1f ms, rows=%d, errors=%d",
                    name, latency_ms, rows_processed, len(errors))
        return record

    def monitor_flow(self, name: str) -> Dict[str, Any]:
        """Return execution statistics for *name*."""
        history = self._exec_history.get(name, [])
        if not history:
            return {"flow": name, "executions": 0, "status": "never_run"}
        latencies = [h["latency_ms"] for h in history]
        success_count = sum(1 for h in history if h["success"])
        return {
            "flow": name,
            "executions": len(history),
            "success_rate": round(success_count / len(history), 3),
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
            "last_run": history[-1]["executed_at"],
            "enabled": self._flows[name].enabled if name in self._flows else None,
        }

    def get_lineage(self, name: str) -> Dict[str, Any]:
        """Return the lineage graph for flow *name*."""
        if name not in self._lineage:
            return {"error": f"No lineage recorded for flow '{name}'."}
        return {"flow": name, "lineage": self._lineage[name]}

    def pause_flow(self, name: str) -> None:
        """Disable a flow so it cannot be executed."""
        if name in self._flows:
            self._flows[name].enabled = False
            logger.info("Flow paused: %s", name)

    def resume_flow(self, name: str) -> None:
        """Re-enable a previously paused flow."""
        if name in self._flows:
            self._flows[name].enabled = True
            logger.info("Flow resumed: %s", name)
