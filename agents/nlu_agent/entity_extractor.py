"""Named entity recognition for NLU."""
from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Pattern, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents an extracted named entity."""
    entity_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    entity_type: str = ""
    start: int = 0
    end: int = 0
    confidence: float = 1.0
    normalized_value: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """Result of named entity extraction."""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    entities: List[Entity] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def get_by_type(self, entity_type: str) -> List[Entity]:
        return [e for e in self.entities if e.entity_type == entity_type]


# --- Regex-based extraction rules ---

_PATTERNS: List[Tuple[str, re.Pattern, float]] = [
    ("EMAIL",     re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b"), 0.99),
    ("URL",       re.compile(r"https?://[^\s]+"), 0.99),
    ("IP_ADDRESS",re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), 0.95),
    ("DATE",      re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b"), 0.92),
    ("TIME",      re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AP]M)?\b"), 0.90),
    ("DURATION",  re.compile(r"\b\d+\s*(?:second|minute|hour|day|week|month|year)s?\b", re.IGNORECASE), 0.88),
    ("NUMBER",    re.compile(r"\b\d+(?:\.\d+)?\b"), 0.85),
    ("PERCENTAGE",re.compile(r"\b\d+(?:\.\d+)?\s*%"), 0.90),
    ("VERSION",   re.compile(r"\bv?\d+\.\d+(?:\.\d+)*\b"), 0.88),
    ("PORT",      re.compile(r"\bport\s+(\d{1,5})\b", re.IGNORECASE), 0.87),
    ("FILE_PATH", re.compile(r"(?:/[\w.\-]+)+|[A-Za-z]:\\(?:[\w.\-\\]+)+"), 0.85),
    ("ENV_VAR",   re.compile(r"\b[A-Z_]{2,}(?:_[A-Z0-9]+)+\b"), 0.80),
    ("UUID",      re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.IGNORECASE), 0.99),
    ("CLOUD_REGION", re.compile(r"\b(?:us|eu|ap|sa|ca|me|af)-(?:east|west|north|south|central)-\d\b", re.IGNORECASE), 0.93),
    ("KUBERNETES_RESOURCE", re.compile(r"\b(?:pod|deployment|service|ingress|namespace|node|configmap|secret)\b", re.IGNORECASE), 0.82),
]

# Named entity word lists (gazetteer-based)
_GAZETTEERS: Dict[str, List[str]] = {
    "CLOUD_PROVIDER": ["AWS", "Azure", "GCP", "Google Cloud", "Amazon", "Microsoft Azure", "DigitalOcean", "Heroku"],
    "PROGRAMMING_LANGUAGE": ["Python", "Java", "Go", "Rust", "JavaScript", "TypeScript", "Ruby", "C++", "Scala"],
    "DATABASE": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra", "DynamoDB", "SQLite", "Elasticsearch"],
    "FRAMEWORK": ["Django", "Flask", "FastAPI", "Spring", "Rails", "Express", "React", "Vue", "Angular"],
    "PROTOCOL": ["HTTP", "HTTPS", "TCP", "UDP", "gRPC", "WebSocket", "AMQP", "MQTT", "REST", "GraphQL"],
    "SEVERITY": ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "FATAL", "NOTICE"],
}


def _extract_regex_entities(text: str) -> List[Entity]:
    entities: List[Entity] = []
    for entity_type, pattern, confidence in _PATTERNS:
        for match in pattern.finditer(text):
            entities.append(Entity(
                text=match.group(),
                entity_type=entity_type,
                start=match.start(),
                end=match.end(),
                confidence=confidence,
            ))
    return entities


def _extract_gazetteer_entities(text: str) -> List[Entity]:
    entities: List[Entity] = []
    for entity_type, terms in _GAZETTEERS.items():
        for term in terms:
            pattern = re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
            for match in pattern.finditer(text):
                entities.append(Entity(
                    text=match.group(),
                    entity_type=entity_type,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.90,
                    normalized_value=term,
                ))
    return entities


def _resolve_overlaps(entities: List[Entity]) -> List[Entity]:
    """Remove overlapping entities, preferring longer and higher-confidence spans."""
    if not entities:
        return []
    sorted_entities = sorted(entities, key=lambda e: (-(e.end - e.start), -e.confidence))
    result: List[Entity] = []
    used_positions: set = set()
    for entity in sorted_entities:
        span = set(range(entity.start, entity.end))
        if not span & used_positions:
            result.append(entity)
            used_positions.update(span)
    return sorted(result, key=lambda e: e.start)


class CustomRule:
    """User-defined extraction rule."""

    def __init__(self, entity_type: str, pattern: str, confidence: float = 0.85) -> None:
        self.entity_type = entity_type
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.confidence = confidence

    def extract(self, text: str) -> List[Entity]:
        return [
            Entity(text=m.group(), entity_type=self.entity_type,
                   start=m.start(), end=m.end(), confidence=self.confidence)
            for m in self.pattern.finditer(text)
        ]


class EntityExtractor:
    """
    Multi-strategy named entity extractor combining regex rules,
    gazetteer lookups, and user-defined custom rules.
    """

    def __init__(self) -> None:
        self._custom_rules: List[CustomRule] = []
        self._entity_normalizers: Dict[str, Any] = {
            "NUMBER": lambda v: float(v.replace(",", "")),
            "PERCENTAGE": lambda v: float(v.rstrip("%")) / 100.0,
            "VERSION": lambda v: v.lstrip("v"),
        }
        logger.info("EntityExtractor initialized")

    def add_rule(self, entity_type: str, pattern: str, confidence: float = 0.85) -> None:
        self._custom_rules.append(CustomRule(entity_type, pattern, confidence))

    def add_gazetteer(self, entity_type: str, terms: List[str]) -> None:
        existing = _GAZETTEERS.get(entity_type, [])
        _GAZETTEERS[entity_type] = list(set(existing + terms))

    def extract(self, text: str) -> ExtractionResult:
        entities = _extract_regex_entities(text)
        entities += _extract_gazetteer_entities(text)
        for rule in self._custom_rules:
            entities += rule.extract(text)

        entities = _resolve_overlaps(entities)
        self._normalize(entities)

        result = ExtractionResult(text=text, entities=entities)
        logger.debug("Extracted %d entities from text (len=%d)", len(entities), len(text))
        return result

    def _normalize(self, entities: List[Entity]) -> None:
        for entity in entities:
            normalizer = self._entity_normalizers.get(entity.entity_type)
            if normalizer:
                try:
                    entity.normalized_value = normalizer(entity.text)
                except (ValueError, TypeError):
                    pass

    def extract_typed(self, text: str, entity_types: List[str]) -> ExtractionResult:
        result = self.extract(text)
        result.entities = [e for e in result.entities if e.entity_type in entity_types]
        return result

    def batch_extract(self, texts: List[str]) -> List[ExtractionResult]:
        return [self.extract(t) for t in texts]

    def entity_summary(self, result: ExtractionResult) -> Dict[str, List[str]]:
        summary: Dict[str, List[str]] = {}
        for entity in result.entities:
            summary.setdefault(entity.entity_type, []).append(entity.text)
        return summary

    def get_supported_types(self) -> List[str]:
        regex_types = [et for et, _, _ in _PATTERNS]
        gazetteer_types = list(_GAZETTEERS.keys())
        custom_types = [r.entity_type for r in self._custom_rules]
        return sorted(set(regex_types + gazetteer_types + custom_types))
