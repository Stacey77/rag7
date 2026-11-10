"""Security agent for threat detection and automated response."""

from __future__ import annotations

import asyncio
import hashlib
import ipaddress
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

import numpy as np
from loguru import logger


class ThreatLevel(Enum):
    """Categorical threat severity levels."""

    NONE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class SecurityEvent:
    """A raw security event for analysis.

    Attributes:
        event_id: Unique identifier.
        source_ip: Origin IP address.
        event_type: Category (e.g. ``"login_attempt"``, ``"api_call"``).
        endpoint: Target API endpoint or resource.
        user_id: Authenticated user (if known).
        payload_size_bytes: Request payload size.
        metadata: Additional event attributes.
        occurred_at: UTC timestamp.
    """

    event_id: str
    source_ip: str
    event_type: str
    endpoint: str
    user_id: str = "anonymous"
    payload_size_bytes: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ThreatIndicator:
    """A detected threat indicator.

    Attributes:
        threat_id: Unique identifier.
        threat_level: Severity level.
        threat_type: Category (e.g. ``"brute_force"``, ``"injection"``).
        source_ip: Originating IP.
        description: Human-readable description.
        evidence: Supporting evidence key-value pairs.
        detected_at: UTC timestamp.
        mitigated: Whether the threat has been mitigated.
    """

    threat_id: str
    threat_level: ThreatLevel
    threat_type: str
    source_ip: str
    description: str
    evidence: dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    mitigated: bool = False


@dataclass
class ThreatResponse:
    """Result of an automated threat response action.

    Attributes:
        threat_id: Identifier of the mitigated threat.
        action: Description of the action taken.
        success: Whether the action succeeded.
        details: Additional response metadata.
        responded_at: UTC timestamp.
    """

    threat_id: str
    action: str
    success: bool
    details: dict[str, Any] = field(default_factory=dict)
    responded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityAgent:
    """Autonomous security monitoring and response agent.

    Detects threats through pattern analysis and anomaly detection,
    and executes automated response playbooks.

    Attributes:
        blocked_ips: Currently blocked IP addresses.
        threat_log: All detected threats.
        response_log: All executed response actions.
        _rate_limit_counters: Request counts per IP for rate limiting.
        _rate_limit_threshold: Requests per window before blocking.
    """

    def __init__(self, rate_limit_threshold: int = 100) -> None:
        """Initialise the security agent.

        Args:
            rate_limit_threshold: Requests per monitoring window to trigger
                rate limiting.
        """
        self.blocked_ips: set[str] = set()
        self.threat_log: list[ThreatIndicator] = []
        self.response_log: list[ThreatResponse] = []
        self._rate_limit_counters: dict[str, int] = {}
        self._rate_limit_threshold = rate_limit_threshold
        self._threat_counter = 0
        logger.info("SecurityAgent initialised (rate_limit={})", rate_limit_threshold)

    async def scan(self, events: list[SecurityEvent]) -> list[ThreatIndicator]:
        """Scan a batch of security events for threats.

        Args:
            events: Security events to analyse.

        Returns:
            List of detected :class:`ThreatIndicator` objects.
        """
        threats: list[ThreatIndicator] = []
        await asyncio.sleep(0)

        for event in events:
            detected = self._analyse_event(event)
            threats.extend(detected)

        self.threat_log.extend(threats)
        if threats:
            logger.warning("Scan complete: {} threat(s) detected in {} events", len(threats), len(events))
        else:
            logger.debug("Scan clean: {} events analysed", len(events))
        return threats

    def _analyse_event(self, event: SecurityEvent) -> list[ThreatIndicator]:
        """Apply detection heuristics to a single event.

        Args:
            event: The security event to evaluate.

        Returns:
            List of threats detected (may be empty).
        """
        threats: list[ThreatIndicator] = []

        # Rate limiting check
        if event.source_ip in self.blocked_ips:
            self._threat_counter += 1
            threats.append(ThreatIndicator(
                threat_id=f"threat_{self._threat_counter:06d}",
                threat_level=ThreatLevel.HIGH,
                threat_type="blocked_ip_access",
                source_ip=event.source_ip,
                description=f"Request from blocked IP {event.source_ip}",
                evidence={"event_id": event.event_id},
            ))

        # Increment rate limit counter
        self._rate_limit_counters[event.source_ip] = (
            self._rate_limit_counters.get(event.source_ip, 0) + 1
        )
        if self._rate_limit_counters[event.source_ip] > self._rate_limit_threshold:
            self._threat_counter += 1
            threats.append(ThreatIndicator(
                threat_id=f"threat_{self._threat_counter:06d}",
                threat_level=ThreatLevel.MEDIUM,
                threat_type="rate_limit_exceeded",
                source_ip=event.source_ip,
                description=f"IP {event.source_ip} exceeded rate limit",
                evidence={"count": self._rate_limit_counters[event.source_ip]},
            ))

        # SQL/command injection detection
        injection_keywords = ["' OR ", "UNION SELECT", "DROP TABLE", "; rm -", "$(", "${IFS}"]
        endpoint_lower = event.endpoint.lower()
        for keyword in injection_keywords:
            if keyword.lower() in endpoint_lower:
                self._threat_counter += 1
                threats.append(ThreatIndicator(
                    threat_id=f"threat_{self._threat_counter:06d}",
                    threat_level=ThreatLevel.CRITICAL,
                    threat_type="injection_attempt",
                    source_ip=event.source_ip,
                    description=f"Injection pattern detected in endpoint",
                    evidence={"keyword": keyword, "endpoint": event.endpoint[:100]},
                ))
                break  # One alert per event for injection

        return threats

    async def detect_anomaly(
        self,
        events: list[SecurityEvent],
        baseline_request_rate: float = 10.0,
    ) -> list[ThreatIndicator]:
        """Detect statistical anomalies in event patterns.

        Args:
            events: Recent security events to analyse.
            baseline_request_rate: Expected average requests per second.

        Returns:
            List of anomaly-based :class:`ThreatIndicator` objects.
        """
        await asyncio.sleep(0)
        threats: list[ThreatIndicator] = []

        if not events:
            return threats

        # Group by source IP and check for abnormal volume
        ip_counts: dict[str, int] = {}
        for event in events:
            ip_counts[event.source_ip] = ip_counts.get(event.source_ip, 0) + 1

        counts = np.array(list(ip_counts.values()), dtype=float)
        if len(counts) < 2:
            return threats

        mean_count = float(np.mean(counts))
        std_count = float(np.std(counts, ddof=1)) + 1e-6
        z_scores = (counts - mean_count) / std_count

        for ip, z_score in zip(ip_counts.keys(), z_scores):
            if abs(z_score) > 3.0:
                self._threat_counter += 1
                threats.append(ThreatIndicator(
                    threat_id=f"threat_{self._threat_counter:06d}",
                    threat_level=ThreatLevel.MEDIUM,
                    threat_type="volume_anomaly",
                    source_ip=ip,
                    description=f"Anomalous request volume from {ip} (z={z_score:.2f})",
                    evidence={"z_score": round(z_score, 2), "count": ip_counts[ip]},
                ))

        self.threat_log.extend(threats)
        return threats

    async def respond_to_threat(
        self,
        threat: ThreatIndicator,
    ) -> ThreatResponse:
        """Execute an automated response to a detected threat.

        Args:
            threat: The threat to respond to.

        Returns:
            :class:`ThreatResponse` documenting the action taken.

        Raises:
            ValueError: If ``threat`` has already been mitigated.
        """
        if threat.mitigated:
            raise ValueError(f"Threat '{threat.threat_id}' is already mitigated")

        await asyncio.sleep(0)
        action, success = self._select_response(threat)
        threat.mitigated = success

        response = ThreatResponse(
            threat_id=threat.threat_id,
            action=action,
            success=success,
            details={
                "threat_type": threat.threat_type,
                "threat_level": threat.threat_level.name,
                "source_ip": threat.source_ip,
            },
        )
        self.response_log.append(response)
        log = logger.warning if success else logger.error
        log(
            "Threat '{}' response: {} → {}",
            threat.threat_id,
            action,
            "SUCCESS" if success else "FAILED",
        )
        return response

    def _select_response(self, threat: ThreatIndicator) -> tuple[str, bool]:
        """Choose and simulate a response action for a threat.

        Args:
            threat: Threat to respond to.

        Returns:
            Tuple of ``(action_description, success_flag)``.
        """
        if threat.threat_level in (ThreatLevel.HIGH, ThreatLevel.CRITICAL):
            self.blocked_ips.add(threat.source_ip)
            return f"IP {threat.source_ip} blocked permanently", True
        if threat.threat_level == ThreatLevel.MEDIUM:
            self._rate_limit_counters[threat.source_ip] = 0
            return f"Rate limit reset for {threat.source_ip}", True
        return "Event logged for review", True
