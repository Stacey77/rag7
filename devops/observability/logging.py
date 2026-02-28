"""Centralized structured logging system."""
from __future__ import annotations
import json
import logging
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

_BASE_LOGGER = logging.getLogger(__name__)

@dataclass
class LogRecord:
    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    level: str = "INFO"
    message: str = ""
    service: str = ""
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    fields: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class LogSink:
    name: str = ""
    level: str = "INFO"
    format: str = "json"   # json | text
    destination: str = "stdout"

class JSONFormatter(logging.Formatter):
    def __init__(self, service: str = "platform", extra_fields: Optional[Dict[str, Any]] = None) -> None:
        super().__init__()
        self.service = service
        self.extra_fields = extra_fields or {}

    def format(self, record: logging.LogRecord) -> str:
        log_dict = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": self.service,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            **self.extra_fields,
        }
        if hasattr(record, "trace_id"):
            log_dict["trace_id"] = record.trace_id
        if hasattr(record, "fields"):
            log_dict.update(record.fields)
        if record.exc_info:
            log_dict["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_dict)


class InMemoryLogSink:
    """Stores log records in memory for querying."""

    def __init__(self, max_records: int = 10000) -> None:
        from collections import deque
        self._records: "deque[LogRecord]" = __import__("collections").deque(maxlen=max_records)

    def write(self, record: LogRecord) -> None:
        self._records.append(record)

    def query(self, level: Optional[str] = None, service: Optional[str] = None,
              trace_id: Optional[str] = None, limit: int = 100) -> List[LogRecord]:
        records = list(self._records)
        if level:
            records = [r for r in records if r.level == level.upper()]
        if service:
            records = [r for r in records if r.service == service]
        if trace_id:
            records = [r for r in records if r.trace_id == trace_id]
        return records[-limit:]

    def search(self, query: str, limit: int = 50) -> List[LogRecord]:
        q = query.lower()
        return [r for r in self._records if q in r.message.lower()][-limit:]

    @property
    def count(self) -> int:
        return len(self._records)


class StructuredLogger:
    """Structured logger with context propagation and multiple sinks."""

    def __init__(self, service: str, level: str = "INFO") -> None:
        self.service = service
        self._log = logging.getLogger(service)
        self._log.setLevel(getattr(logging, level.upper(), logging.INFO))
        self._in_memory = InMemoryLogSink()
        self._context: Dict[str, Any] = {}
        self._processors: List[Callable[[LogRecord], LogRecord]] = []

    def add_json_handler(self, stream: Any = None) -> None:
        handler = logging.StreamHandler(stream or sys.stdout)
        handler.setFormatter(JSONFormatter(service=self.service))
        self._log.addHandler(handler)

    def set_context(self, **kwargs: Any) -> None:
        self._context.update(kwargs)

    def clear_context(self) -> None:
        self._context.clear()

    def add_processor(self, processor: Callable[[LogRecord], LogRecord]) -> None:
        self._processors.append(processor)

    def _emit(self, level: str, message: str, trace_id: Optional[str] = None,
               **fields: Any) -> LogRecord:
        record = LogRecord(
            level=level.upper(),
            message=message,
            service=self.service,
            trace_id=trace_id or self._context.get("trace_id"),
            fields={**self._context, **fields},
        )
        for processor in self._processors:
            record = processor(record)
        self._in_memory.write(record)
        log_fn = getattr(self._log, level.lower(), self._log.info)
        extra = {"trace_id": record.trace_id, "fields": record.fields}
        log_fn(message, extra=extra)
        return record

    def debug(self, msg: str, **fields: Any) -> LogRecord:
        return self._emit("DEBUG", msg, **fields)

    def info(self, msg: str, **fields: Any) -> LogRecord:
        return self._emit("INFO", msg, **fields)

    def warning(self, msg: str, **fields: Any) -> LogRecord:
        return self._emit("WARNING", msg, **fields)

    def error(self, msg: str, **fields: Any) -> LogRecord:
        return self._emit("ERROR", msg, **fields)

    def critical(self, msg: str, **fields: Any) -> LogRecord:
        return self._emit("CRITICAL", msg, **fields)

    def query(self, level: Optional[str] = None, limit: int = 100) -> List[LogRecord]:
        return self._in_memory.query(level=level, service=self.service, limit=limit)

    def error_rate(self, window: int = 100) -> float:
        records = list(self._in_memory._records)[-window:]
        if not records:
            return 0.0
        errors = sum(1 for r in records if r.level in ("ERROR", "CRITICAL"))
        return errors / len(records)


class CentralizedLogManager:
    """Manages multiple service loggers with aggregated querying."""

    def __init__(self) -> None:
        self._loggers: Dict[str, StructuredLogger] = {}
        _BASE_LOGGER.info("CentralizedLogManager initialized")

    def get_logger(self, service: str, level: str = "INFO") -> StructuredLogger:
        if service not in self._loggers:
            self._loggers[service] = StructuredLogger(service, level)
        return self._loggers[service]

    def aggregate_query(self, level: Optional[str] = None, limit: int = 100) -> List[LogRecord]:
        all_records: List[LogRecord] = []
        for logger in self._loggers.values():
            all_records.extend(logger.query(level=level, limit=limit))
        return sorted(all_records, key=lambda r: r.timestamp)[-limit:]

    def list_services(self) -> List[str]:
        return list(self._loggers.keys())
