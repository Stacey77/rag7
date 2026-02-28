"""Data profiling - statistical summaries of datasets."""
from __future__ import annotations

import logging
import math
import re
import statistics
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class FieldProfile:
    field_name: str = ""
    dtype: str = "unknown"
    count: int = 0
    null_count: int = 0
    null_rate: float = 0.0
    unique_count: int = 0
    unique_rate: float = 0.0
    # Numeric stats
    mean: Optional[float] = None
    std: Optional[float] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    median: Optional[float] = None
    p25: Optional[float] = None
    p75: Optional[float] = None
    skewness: Optional[float] = None
    # String stats
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    avg_length: Optional[float] = None
    patterns: List[str] = field(default_factory=list)
    # Top values
    top_values: List[Tuple[Any, int]] = field(default_factory=list)


@dataclass
class DatasetProfile:
    profile_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dataset_name: str = ""
    record_count: int = 0
    field_count: int = 0
    field_profiles: Dict[str, FieldProfile] = field(default_factory=dict)
    overall_null_rate: float = 0.0
    duplicate_rate: float = 0.0
    quality_score: float = 0.0
    generated_at: datetime = field(default_factory=datetime.utcnow)


def _percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    idx = max(0, int(len(sorted_values) * p) - 1)
    return sorted_values[idx]


def _skewness(values: List[float]) -> float:
    n = len(values)
    if n < 3:
        return 0.0
    mean = statistics.mean(values)
    std = statistics.stdev(values)
    if std == 0:
        return 0.0
    return sum(((v - mean) / std) ** 3 for v in values) * n / ((n - 1) * (n - 2))


def _infer_dtype(values: List[Any]) -> str:
    non_null = [v for v in values if v is not None]
    if not non_null:
        return "null"
    sample = non_null[:20]
    if all(isinstance(v, bool) for v in sample):
        return "boolean"
    if all(isinstance(v, int) for v in sample):
        return "integer"
    if all(isinstance(v, float) for v in sample):
        return "float"
    if all(isinstance(v, (int, float)) for v in sample):
        return "numeric"
    if all(isinstance(v, str) for v in sample):
        # Check if numeric strings
        try:
            [float(v) for v in sample[:5]]
            return "numeric_string"
        except (ValueError, TypeError):
            pass
        return "string"
    return "mixed"


def _detect_patterns(values: List[str]) -> List[str]:
    patterns: List[str] = []
    sample = [v for v in values if isinstance(v, str)][:100]
    if not sample:
        return patterns

    email_like = sum(1 for v in sample if re.match(r".+@.+\..+", v))
    if email_like / len(sample) > 0.5:
        patterns.append("email")

    url_like = sum(1 for v in sample if v.startswith(("http://", "https://")))
    if url_like / len(sample) > 0.3:
        patterns.append("url")

    numeric_like = sum(1 for v in sample if re.match(r"^-?\d+\.?\d*$", v.strip()))
    if numeric_like / len(sample) > 0.7:
        patterns.append("numeric_string")

    date_like = sum(1 for v in sample if re.match(r"\d{4}-\d{2}-\d{2}", v))
    if date_like / len(sample) > 0.5:
        patterns.append("date_iso")

    return patterns


class FieldProfiler:
    """Profiles a single field across all records."""

    def profile(self, field_name: str, values: List[Any]) -> FieldProfile:
        profile = FieldProfile(field_name=field_name)
        profile.count = len(values)
        null_values = [v for v in values if v is None or v == ""]
        profile.null_count = len(null_values)
        profile.null_rate = profile.null_count / max(profile.count, 1)

        non_null = [v for v in values if v is not None and v != ""]
        profile.unique_count = len(set(str(v) for v in non_null))
        profile.unique_rate = profile.unique_count / max(len(non_null), 1)
        profile.dtype = _infer_dtype(values)

        # Numeric stats
        numeric_values: List[float] = []
        for v in non_null:
            try:
                numeric_values.append(float(v))
            except (TypeError, ValueError):
                pass

        if numeric_values:
            sorted_nums = sorted(numeric_values)
            profile.mean = statistics.mean(numeric_values)
            profile.std = statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0.0
            profile.min_val = sorted_nums[0]
            profile.max_val = sorted_nums[-1]
            profile.median = statistics.median(numeric_values)
            profile.p25 = _percentile(sorted_nums, 0.25)
            profile.p75 = _percentile(sorted_nums, 0.75)
            profile.skewness = _skewness(numeric_values)

        # String stats
        str_values = [str(v) for v in non_null if isinstance(v, str)]
        if str_values:
            lengths = [len(v) for v in str_values]
            profile.min_length = min(lengths)
            profile.max_length = max(lengths)
            profile.avg_length = sum(lengths) / len(lengths)
            profile.patterns = _detect_patterns(str_values)

        # Top values
        counts = Counter(str(v) for v in non_null)
        profile.top_values = counts.most_common(10)
        return profile


class DataProfiler:
    """
    Generates comprehensive statistical profiles of datasets
    including field-level statistics, quality scoring, and anomaly hints.
    """

    def __init__(self) -> None:
        self._field_profiler = FieldProfiler()
        logger.info("DataProfiler initialized")

    def profile(self, records: List[Dict[str, Any]],
                dataset_name: str = "dataset") -> DatasetProfile:
        if not records:
            return DatasetProfile(dataset_name=dataset_name)

        fields = list(records[0].keys())
        dp = DatasetProfile(
            dataset_name=dataset_name,
            record_count=len(records),
            field_count=len(fields),
        )

        for field_name in fields:
            values = [r.get(field_name) for r in records]
            fp = self._field_profiler.profile(field_name, values)
            dp.field_profiles[field_name] = fp

        # Overall stats
        total_cells = len(records) * len(fields)
        null_cells = sum(fp.null_count for fp in dp.field_profiles.values())
        dp.overall_null_rate = null_cells / max(total_cells, 1)

        seen = set()
        dups = 0
        for r in records:
            key = str(sorted(r.items()))
            if key in seen:
                dups += 1
            seen.add(key)
        dp.duplicate_rate = dups / max(len(records), 1)

        dp.quality_score = max(0.0, 1.0 - dp.overall_null_rate - dp.duplicate_rate * 0.5)
        logger.info("Profiled '%s': %d records, %d fields, quality=%.2f",
                    dataset_name, len(records), len(fields), dp.quality_score)
        return dp

    def summarize(self, profile: DatasetProfile) -> str:
        lines = [
            f"Dataset: {profile.dataset_name}",
            f"Records: {profile.record_count}, Fields: {profile.field_count}",
            f"Null rate: {profile.overall_null_rate:.1%}, Duplicate rate: {profile.duplicate_rate:.1%}",
            f"Quality score: {profile.quality_score:.2f}",
            "\nField summaries:",
        ]
        for name, fp in profile.field_profiles.items():
            line = f"  {name}: dtype={fp.dtype}, nulls={fp.null_rate:.1%}, unique={fp.unique_rate:.1%}"
            if fp.mean is not None:
                line += f", mean={fp.mean:.2f}, std={fp.std:.2f}"
            lines.append(line)
        return "\n".join(lines)
