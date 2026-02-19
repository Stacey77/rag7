"""Data validation rules and schema enforcement."""
from __future__ import annotations

import logging
import re
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    field: str
    rule: str
    message: str
    value: Any = None


@dataclass
class ValidationResult:
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    record: Dict[str, Any] = field(default_factory=dict)
    is_valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationReport:
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    error_counts: Dict[str, int] = field(default_factory=dict)
    sample_errors: List[ValidationError] = field(default_factory=list)
    pass_rate: float = 0.0
    generated_at: datetime = field(default_factory=datetime.utcnow)


class Rule(ABC):
    def __init__(self, name: str, field: str, is_warning: bool = False) -> None:
        self.name = name
        self.field = field
        self.is_warning = is_warning

    @abstractmethod
    def validate(self, record: Dict[str, Any]) -> Optional[ValidationError]: ...


class NotNullRule(Rule):
    def validate(self, record: Dict[str, Any]) -> Optional[ValidationError]:
        val = record.get(self.field)
        if val is None or val == "":
            return ValidationError(self.field, self.name, f"'{self.field}' must not be null/empty", val)
        return None


class TypeRule(Rule):
    def __init__(self, name: str, field: str, expected_type: type, **kwargs: Any) -> None:
        super().__init__(name, field, **kwargs)
        self.expected_type = expected_type

    def validate(self, record: Dict[str, Any]) -> Optional[ValidationError]:
        val = record.get(self.field)
        if val is not None and not isinstance(val, self.expected_type):
            try:
                self.expected_type(val)
            except (ValueError, TypeError):
                return ValidationError(self.field, self.name,
                    f"'{self.field}' expected {self.expected_type.__name__}, got {type(val).__name__}", val)
        return None


class RangeRule(Rule):
    def __init__(self, name: str, field: str, min_val: Optional[float] = None,
                 max_val: Optional[float] = None, **kwargs: Any) -> None:
        super().__init__(name, field, **kwargs)
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, record: Dict[str, Any]) -> Optional[ValidationError]:
        val = record.get(self.field)
        if val is None:
            return None
        try:
            num = float(val)
        except (TypeError, ValueError):
            return None
        if self.min_val is not None and num < self.min_val:
            return ValidationError(self.field, self.name,
                f"'{self.field}' value {num} < min {self.min_val}", val)
        if self.max_val is not None and num > self.max_val:
            return ValidationError(self.field, self.name,
                f"'{self.field}' value {num} > max {self.max_val}", val)
        return None


class RegexRule(Rule):
    def __init__(self, name: str, field: str, pattern: str, **kwargs: Any) -> None:
        super().__init__(name, field, **kwargs)
        self._pattern = re.compile(pattern)

    def validate(self, record: Dict[str, Any]) -> Optional[ValidationError]:
        val = record.get(self.field)
        if val is not None and not self._pattern.match(str(val)):
            return ValidationError(self.field, self.name,
                f"'{self.field}' does not match pattern {self._pattern.pattern}", val)
        return None


class UniqueRule(Rule):
    def __init__(self, name: str, field: str, **kwargs: Any) -> None:
        super().__init__(name, field, **kwargs)
        self._seen: set = set()

    def validate(self, record: Dict[str, Any]) -> Optional[ValidationError]:
        val = record.get(self.field)
        if val is not None:
            if val in self._seen:
                return ValidationError(self.field, self.name,
                    f"Duplicate value for '{self.field}': {val}", val)
            self._seen.add(val)
        return None

    def reset(self) -> None:
        self._seen.clear()


class CustomRule(Rule):
    def __init__(self, name: str, field: str, func: Callable[[Any], bool],
                 message: str = "", **kwargs: Any) -> None:
        super().__init__(name, field, **kwargs)
        self._func = func
        self._message = message or f"Custom rule '{name}' failed"

    def validate(self, record: Dict[str, Any]) -> Optional[ValidationError]:
        val = record.get(self.field)
        try:
            if not self._func(val):
                return ValidationError(self.field, self.name, self._message, val)
        except Exception as exc:
            return ValidationError(self.field, self.name, f"Rule error: {exc}", val)
        return None


class DataValidator:
    """Validates records against a set of rules and produces reports."""

    def __init__(self) -> None:
        self._rules: List[Rule] = []
        logger.info("DataValidator initialized")

    def add_rule(self, rule: Rule) -> "DataValidator":
        self._rules.append(rule)
        return self

    def not_null(self, field: str) -> "DataValidator":
        return self.add_rule(NotNullRule(f"{field}_not_null", field))

    def type_check(self, field: str, expected_type: type) -> "DataValidator":
        return self.add_rule(TypeRule(f"{field}_type", field, expected_type))

    def range_check(self, field: str, min_val: Optional[float] = None,
                     max_val: Optional[float] = None) -> "DataValidator":
        return self.add_rule(RangeRule(f"{field}_range", field, min_val, max_val))

    def regex_check(self, field: str, pattern: str) -> "DataValidator":
        return self.add_rule(RegexRule(f"{field}_pattern", field, pattern))

    def unique(self, field: str) -> "DataValidator":
        return self.add_rule(UniqueRule(f"{field}_unique", field))

    def validate(self, record: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult(record=record)
        for rule in self._rules:
            error = rule.validate(record)
            if error:
                if rule.is_warning:
                    result.warnings.append(error)
                else:
                    result.errors.append(error)
        result.is_valid = len(result.errors) == 0
        return result

    def validate_batch(self, records: List[Dict[str, Any]]) -> ValidationReport:
        report = ValidationReport(total_records=len(records))
        sample_errors: List[ValidationError] = []
        for record in records:
            result = self.validate(record)
            if result.is_valid:
                report.valid_records += 1
            else:
                report.invalid_records += 1
                for err in result.errors:
                    report.error_counts[err.rule] = report.error_counts.get(err.rule, 0) + 1
                    if len(sample_errors) < 10:
                        sample_errors.append(err)
        report.sample_errors = sample_errors
        report.pass_rate = report.valid_records / max(report.total_records, 1)
        logger.info("Validation: %d/%d records passed (%.1f%%)",
                    report.valid_records, report.total_records, report.pass_rate * 100)
        return report
