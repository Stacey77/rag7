"""Data cleaning and normalization."""
from __future__ import annotations

import logging
import re
import statistics
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CleansingResult:
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    records_in: int = 0
    records_out: int = 0
    records_dropped: int = 0
    fields_modified: Dict[str, int] = field(default_factory=dict)
    operations_applied: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


def _strip_whitespace(value: Any) -> Any:
    return value.strip() if isinstance(value, str) else value


def _to_lowercase(value: Any) -> Any:
    return value.lower() if isinstance(value, str) else value


def _remove_special_chars(value: Any, keep: str = r"a-zA-Z0-9 ._-") -> Any:
    if isinstance(value, str):
        return re.sub(f"[^{keep}]", "", value)
    return value


def _normalize_whitespace(value: Any) -> Any:
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return value


def _coerce_numeric(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return float(value.replace(",", ""))
        except ValueError:
            return value
    return value


def _truncate(value: Any, max_len: int = 255) -> Any:
    return value[:max_len] if isinstance(value, str) and len(value) > max_len else value


class ImputationStrategy:
    """Handles missing value imputation."""

    def __init__(self, strategy: str = "mean", fill_value: Any = None) -> None:
        self.strategy = strategy
        self.fill_value = fill_value
        self._computed_fills: Dict[str, Any] = {}

    def fit(self, records: List[Dict[str, Any]], fields: List[str]) -> None:
        for field_name in fields:
            values = [r[field_name] for r in records
                      if r.get(field_name) is not None and isinstance(r[field_name], (int, float))]
            if not values:
                continue
            if self.strategy == "mean":
                self._computed_fills[field_name] = statistics.mean(values)
            elif self.strategy == "median":
                self._computed_fills[field_name] = statistics.median(values)
            elif self.strategy == "mode":
                from collections import Counter
                self._computed_fills[field_name] = Counter(values).most_common(1)[0][0]
            elif self.strategy == "constant":
                self._computed_fills[field_name] = self.fill_value

    def impute(self, record: Dict[str, Any]) -> Dict[str, Any]:
        result = dict(record)
        for field_name, fill in self._computed_fills.items():
            if result.get(field_name) is None:
                result[field_name] = fill
        return result


class OutlierHandler:
    """Detects and handles numeric outliers using IQR method."""

    def __init__(self, method: str = "clip", iqr_multiplier: float = 1.5) -> None:
        self.method = method    # "clip" | "remove" | "impute"
        self.iqr_multiplier = iqr_multiplier
        self._bounds: Dict[str, tuple] = {}

    def fit(self, records: List[Dict[str, Any]], fields: List[str]) -> None:
        for field_name in fields:
            values = sorted(r[field_name] for r in records
                            if isinstance(r.get(field_name), (int, float)))
            if len(values) < 4:
                continue
            q1 = values[len(values) // 4]
            q3 = values[3 * len(values) // 4]
            iqr = q3 - q1
            self._bounds[field_name] = (q1 - self.iqr_multiplier * iqr,
                                         q3 + self.iqr_multiplier * iqr)

    def handle(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        result = dict(record)
        for field_name, (low, high) in self._bounds.items():
            val = result.get(field_name)
            if not isinstance(val, (int, float)):
                continue
            if val < low or val > high:
                if self.method == "clip":
                    result[field_name] = max(low, min(high, val))
                elif self.method == "remove":
                    return None
                elif self.method == "impute":
                    result[field_name] = (low + high) / 2
        return result


class DataCleanser:
    """
    Comprehensive data cleaning pipeline supporting field-level transforms,
    imputation, outlier handling, deduplication, and custom rules.
    """

    def __init__(self) -> None:
        self._field_transforms: Dict[str, List[Callable]] = {}
        self._drop_conditions: List[Callable[[Dict[str, Any]], bool]] = []
        self._imputer: Optional[ImputationStrategy] = None
        self._outlier_handler: Optional[OutlierHandler] = None
        self._dedup_key: Optional[str] = None
        logger.info("DataCleanser initialized")

    def add_transform(self, field: str, func: Callable) -> "DataCleanser":
        self._field_transforms.setdefault(field, []).append(func)
        return self

    def strip_whitespace(self, *fields: str) -> "DataCleanser":
        for f in fields:
            self.add_transform(f, _strip_whitespace)
        return self

    def lowercase(self, *fields: str) -> "DataCleanser":
        for f in fields:
            self.add_transform(f, _to_lowercase)
        return self

    def coerce_numeric(self, *fields: str) -> "DataCleanser":
        for f in fields:
            self.add_transform(f, _coerce_numeric)
        return self

    def truncate(self, field: str, max_len: int = 255) -> "DataCleanser":
        return self.add_transform(field, lambda v: _truncate(v, max_len))

    def drop_if(self, condition: Callable[[Dict[str, Any]], bool]) -> "DataCleanser":
        self._drop_conditions.append(condition)
        return self

    def drop_nulls(self, *fields: str) -> "DataCleanser":
        for f in fields:
            self._drop_conditions.append(lambda r, field=f: r.get(field) is None)
        return self

    def enable_imputation(self, strategy: str = "mean",
                           fill_value: Any = None) -> "DataCleanser":
        self._imputer = ImputationStrategy(strategy, fill_value)
        return self

    def enable_outlier_handling(self, method: str = "clip") -> "DataCleanser":
        self._outlier_handler = OutlierHandler(method)
        return self

    def deduplicate(self, key_field: str) -> "DataCleanser":
        self._dedup_key = key_field
        return self

    def fit(self, records: List[Dict[str, Any]]) -> "DataCleanser":
        numeric_fields = [f for f in (records[0].keys() if records else [])
                          if any(isinstance(r.get(f), (int, float)) for r in records[:10])]
        if self._imputer:
            self._imputer.fit(records, numeric_fields)
        if self._outlier_handler:
            self._outlier_handler.fit(records, numeric_fields)
        return self

    def clean_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        result = dict(record)
        for condition in self._drop_conditions:
            if condition(result):
                return None
        for field_name, transforms in self._field_transforms.items():
            if field_name in result:
                for func in transforms:
                    result[field_name] = func(result[field_name])
        if self._imputer:
            result = self._imputer.impute(result)
        if self._outlier_handler:
            result = self._outlier_handler.handle(result)
            if result is None:
                return None
        return result

    def clean(self, records: List[Dict[str, Any]]) -> tuple:
        self.fit(records)
        cleaned: List[Dict[str, Any]] = []
        seen_keys: set = set()
        dropped = 0
        for record in records:
            result = self.clean_record(record)
            if result is None:
                dropped += 1
                continue
            if self._dedup_key:
                key = result.get(self._dedup_key)
                if key in seen_keys:
                    dropped += 1
                    continue
                if key is not None:
                    seen_keys.add(key)
            cleaned.append(result)
        result_obj = CleansingResult(
            records_in=len(records),
            records_out=len(cleaned),
            records_dropped=dropped,
            operations_applied=list(self._field_transforms.keys()),
        )
        logger.info("Cleansed: %d in, %d out, %d dropped", len(records), len(cleaned), dropped)
        return cleaned, result_obj
