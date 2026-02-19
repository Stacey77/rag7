"""Distributed tracing system."""
from __future__ import annotations
import logging
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class Span:
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:16])
    trace_id: str = ""
    parent_span_id: Optional[str] = None
    operation_name: str = ""
    service: str = ""
    start_time: float = field(default_factory=time.perf_counter)
    end_time: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "ok"   # ok | error
    error_message: Optional[str] = None

    @property
    def duration_ms(self) -> float:
        if self.end_time is None:
            return (time.perf_counter() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000

    def finish(self) -> None:
        self.end_time = time.perf_counter()

    def set_tag(self, key: str, value: Any) -> "Span":
        self.tags[key] = value
        return self

    def log(self, event: str, **fields: Any) -> "Span":
        self.logs.append({"event": event, "timestamp": time.perf_counter(), **fields})
        return self

    def set_error(self, message: str) -> "Span":
        self.status = "error"
        self.error_message = message
        self.tags["error"] = True
        return self


@dataclass
class Trace:
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    root_span: Optional[Span] = None
    spans: List[Span] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_duration_ms(self) -> float:
        if not self.spans:
            return 0.0
        start = min(s.start_time for s in self.spans)
        end = max(s.end_time or time.perf_counter() for s in self.spans)
        return (end - start) * 1000

    @property
    def has_errors(self) -> bool:
        return any(s.status == "error" for s in self.spans)

    def critical_path(self) -> List[Span]:
        """Return spans in chronological order (simplified critical path)."""
        return sorted(self.spans, key=lambda s: s.start_time)


class SpanContext:
    """Thread-local span context for implicit propagation."""
    _current: Optional[Span] = None

    @classmethod
    def current(cls) -> Optional[Span]:
        return cls._current

    @classmethod
    def set(cls, span: Optional[Span]) -> None:
        cls._current = span


class Tracer:
    """Distributed tracer with span management and trace collection."""

    def __init__(self, service: str) -> None:
        self.service = service
        self._traces: Dict[str, Trace] = {}
        self._completed: List[Trace] = []
        logger.info("Tracer initialized for service '%s'", service)

    def start_trace(self, operation: str) -> Trace:
        trace = Trace()
        span = Span(trace_id=trace.trace_id, operation_name=operation, service=self.service)
        trace.root_span = span
        trace.spans.append(span)
        self._traces[trace.trace_id] = trace
        SpanContext.set(span)
        return trace

    def start_span(self, operation: str, trace_id: Optional[str] = None,
                    parent_span_id: Optional[str] = None) -> Span:
        parent = SpanContext.current()
        if trace_id is None and parent:
            trace_id = parent.trace_id
        if trace_id is None:
            trace = self.start_trace(operation)
            return trace.root_span  # type: ignore[return-value]
        tid = trace_id
        pid = parent_span_id or (parent.span_id if parent else None)
        span = Span(trace_id=tid, parent_span_id=pid,
                    operation_name=operation, service=self.service)
        if tid in self._traces:
            self._traces[tid].spans.append(span)
        SpanContext.set(span)
        return span

    def finish_span(self, span: Span) -> None:
        span.finish()
        if span == SpanContext.current():
            SpanContext.set(None)

    @contextmanager
    def span(self, operation: str, **tags: Any) -> Generator[Span, None, None]:
        s = self.start_span(operation)
        for k, v in tags.items():
            s.set_tag(k, v)
        try:
            yield s
        except Exception as exc:
            s.set_error(str(exc))
            raise
        finally:
            self.finish_span(s)

    def finish_trace(self, trace: Trace) -> None:
        for span in trace.spans:
            if span.end_time is None:
                span.finish()
        self._traces.pop(trace.trace_id, None)
        self._completed.append(trace)
        logger.debug("Trace %s finished: %d spans, %.1fms",
                     trace.trace_id[:8], len(trace.spans), trace.total_duration_ms)

    def get_trace(self, trace_id: str) -> Optional[Trace]:
        return self._traces.get(trace_id) or next(
            (t for t in self._completed if t.trace_id == trace_id), None)

    def recent_traces(self, n: int = 10) -> List[Trace]:
        return self._completed[-n:]

    def error_rate(self, window: int = 100) -> float:
        recent = self._completed[-window:]
        if not recent:
            return 0.0
        return sum(1 for t in recent if t.has_errors) / len(recent)

    def p95_latency(self, window: int = 100) -> float:
        recent = self._completed[-window:]
        if not recent:
            return 0.0
        durations = sorted(t.total_duration_ms for t in recent)
        idx = max(0, int(len(durations) * 0.95) - 1)
        return durations[idx]


class TracingMiddleware:
    """Wraps callable with automatic tracing."""

    def __init__(self, tracer: Tracer) -> None:
        self._tracer = tracer

    def trace(self, operation: str) -> Any:
        def decorator(func: Any) -> Any:
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                with self._tracer.span(operation, func=func.__name__) as s:
                    result = func(*args, **kwargs)
                    s.set_tag("success", True)
                    return result
            return wrapper
        return decorator
