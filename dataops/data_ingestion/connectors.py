"""Multi-source data connectors."""
from __future__ import annotations

import csv
import io
import json
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Generator, Iterable, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ConnectorConfig:
    name: str
    connector_type: str
    connection_params: Dict[str, Any] = field(default_factory=dict)
    batch_size: int = 1000
    timeout_seconds: int = 30
    retry_count: int = 3


@dataclass
class DataRecord:
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    schema: Dict[str, str] = field(default_factory=dict)
    ingested_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionResult:
    records_read: int = 0
    records_failed: int = 0
    source: str = ""
    elapsed_seconds: float = 0.0
    errors: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)


class BaseConnector(ABC):
    def __init__(self, config: ConnectorConfig) -> None:
        self.config = config
        self._connected = False

    @abstractmethod
    def connect(self) -> bool: ...

    @abstractmethod
    def read(self) -> Generator[DataRecord, None, None]: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    def __enter__(self) -> "BaseConnector":
        self.connect()
        return self

    def __exit__(self, *_: Any) -> None:
        self.disconnect()


class CSVConnector(BaseConnector):
    """Reads records from CSV text or file path."""

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def read(self) -> Generator[DataRecord, None, None]:
        content = self.config.connection_params.get("content", "")
        path = self.config.connection_params.get("path", "")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except OSError as e:
                logger.error("CSV read error: %s", e)
                return
        reader = csv.DictReader(io.StringIO(content))
        for row in reader:
            yield DataRecord(source=self.config.name, data=dict(row),
                             schema={k: "str" for k in row})


class JSONConnector(BaseConnector):
    """Reads records from JSON array or newline-delimited JSON."""

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def read(self) -> Generator[DataRecord, None, None]:
        content = self.config.connection_params.get("content", "[]")
        try:
            data = json.loads(content)
            if isinstance(data, list):
                for item in data:
                    yield DataRecord(source=self.config.name, data=item if isinstance(item, dict) else {"value": item})
            elif isinstance(data, dict):
                yield DataRecord(source=self.config.name, data=data)
        except json.JSONDecodeError as e:
            logger.error("JSON parse error: %s", e)


class InMemoryConnector(BaseConnector):
    """Reads records from an in-memory list."""

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def read(self) -> Generator[DataRecord, None, None]:
        records = self.config.connection_params.get("records", [])
        for item in records:
            yield DataRecord(source=self.config.name,
                             data=item if isinstance(item, dict) else {"value": item})


class APIConnector(BaseConnector):
    """Simulated REST API connector."""

    def connect(self) -> bool:
        base_url = self.config.connection_params.get("base_url", "")
        logger.info("Simulating connection to API: %s", base_url)
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def read(self) -> Generator[DataRecord, None, None]:
        endpoint = self.config.connection_params.get("endpoint", "/data")
        mock_data = self.config.connection_params.get("mock_data", [{"id": 1, "value": "sample"}])
        logger.info("Fetching from API endpoint %s", endpoint)
        for item in mock_data:
            yield DataRecord(source=self.config.name, data=item,
                             metadata={"endpoint": endpoint})


_CONNECTOR_REGISTRY: Dict[str, type] = {
    "csv": CSVConnector,
    "json": JSONConnector,
    "memory": InMemoryConnector,
    "api": APIConnector,
}


class ConnectorFactory:
    @staticmethod
    def create(config: ConnectorConfig) -> BaseConnector:
        cls = _CONNECTOR_REGISTRY.get(config.connector_type)
        if not cls:
            raise ValueError(f"Unknown connector type: {config.connector_type}")
        return cls(config)

    @staticmethod
    def register(connector_type: str, cls: type) -> None:
        _CONNECTOR_REGISTRY[connector_type] = cls


class DataIngestionManager:
    def __init__(self) -> None:
        self._connectors: List[ConnectorConfig] = []
        logger.info("DataIngestionManager initialized")

    def add_source(self, config: ConnectorConfig) -> None:
        self._connectors.append(config)

    def ingest_all(self) -> Dict[str, IngestionResult]:
        import time
        results: Dict[str, IngestionResult] = {}
        for cfg in self._connectors:
            connector = ConnectorFactory.create(cfg)
            result = IngestionResult(source=cfg.name)
            start = time.perf_counter()
            try:
                with connector:
                    for _ in connector.read():
                        result.records_read += 1
            except Exception as exc:
                result.errors.append(str(exc))
                result.records_failed += 1
                logger.error("Ingestion failed for '%s': %s", cfg.name, exc)
            result.elapsed_seconds = time.perf_counter() - start
            results[cfg.name] = result
            logger.info("Ingested %d records from '%s'", result.records_read, cfg.name)
        return results
