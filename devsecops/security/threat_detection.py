"""Security monitoring with rate limiting, IP blocking, and anomaly detection."""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting a resource.

    Attributes:
        resource: Resource or endpoint identifier.
        max_requests: Maximum allowed requests per window.
        window_seconds: Rolling window duration in seconds.
    """

    resource: str
    max_requests: int
    window_seconds: float = 60.0


@dataclass
class ThreatEvent:
    """A detected security threat event.

    Attributes:
        event_id: Unique identifier.
        event_type: Category (``"rate_limit"``, ``"ip_blocked"``, ``"anomaly"``).
        source_ip: Originating IP address.
        resource: Affected resource.
        details: Supplementary event data.
        severity: ``"low"``, ``"medium"``, or ``"high"``.
        detected_at: UTC timestamp.
    """

    event_id: str
    event_type: str
    source_ip: str
    resource: str
    details: dict[str, Any] = field(default_factory=dict)
    severity: str = "medium"
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ThreatDetection:
    """Security monitoring with rate limiting, IP blocking, and anomaly detection.

    Tracks per-IP request rates and flags anomalous usage patterns.

    Attributes:
        blocked_ips: Set of currently blocked IP addresses.
        rate_limits: Per-resource rate limit configurations.
        threat_log: All detected threat events.
        _request_log: Per-(ip, resource) request timestamps.
        _baseline_rates: Per-resource baseline request rate (requests/s).
    """

    def __init__(self) -> None:
        """Initialise the threat detection engine."""
        self.blocked_ips: set[str] = set()
        self.rate_limits: dict[str, RateLimitConfig] = {}
        self.threat_log: list[ThreatEvent] = []
        self._request_log: dict[str, list[float]] = defaultdict(list)
        self._baseline_rates: dict[str, float] = {}
        self._event_counter = 0
        logger.info("ThreatDetection initialised")

    def configure_rate_limit(self, config: RateLimitConfig) -> None:
        """Set or update a rate limit for a resource.

        Args:
            config: Rate limit configuration.
        """
        self.rate_limits[config.resource] = config
        logger.debug(
            "Rate limit configured: {} → {}/{:.0f}s",
            config.resource,
            config.max_requests,
            config.window_seconds,
        )

    def check_rate_limit(self, source_ip: str, resource: str) -> bool:
        """Check if a request from a given IP is within the rate limit.

        Also blocks IPs that repeatedly exceed the limit.

        Args:
            source_ip: Client IP address.
            resource: Resource or endpoint being accessed.

        Returns:
            ``True`` if the request is allowed, ``False`` if rate-limited
            or blocked.
        """
        if source_ip in self.blocked_ips:
            self._fire_event("ip_blocked", source_ip, resource, severity="high")
            return False

        config = self.rate_limits.get(resource)
        if config is None:
            return True  # No limit configured

        key = f"{source_ip}:{resource}"
        now = time.monotonic()
        window_start = now - config.window_seconds

        # Prune old timestamps
        self._request_log[key] = [
            ts for ts in self._request_log[key] if ts >= window_start
        ]
        self._request_log[key].append(now)

        count = len(self._request_log[key])
        if count > config.max_requests:
            self._fire_event(
                "rate_limit",
                source_ip,
                resource,
                details={"count": count, "limit": config.max_requests},
                severity="medium",
            )
            # Block after 3× the limit
            if count > config.max_requests * 3:
                self.blocked_ips.add(source_ip)
                logger.warning("IP {} auto-blocked after {}× rate limit", source_ip, count)
            return False

        return True

    def block_ip(self, ip: str, reason: str = "manual") -> None:
        """Manually block an IP address.

        Args:
            ip: IP address to block.
            reason: Human-readable reason for audit trail.
        """
        self.blocked_ips.add(ip)
        self._fire_event("ip_blocked", ip, "manual", details={"reason": reason}, severity="high")
        logger.warning("IP {} blocked: {}", ip, reason)

    def unblock_ip(self, ip: str) -> bool:
        """Remove an IP from the block list.

        Args:
            ip: IP address to unblock.

        Returns:
            ``True`` if the IP was blocked and is now unblocked.
        """
        if ip in self.blocked_ips:
            self.blocked_ips.discard(ip)
            logger.info("IP {} unblocked", ip)
            return True
        return False

    def set_baseline(self, resource: str, baseline_rps: float) -> None:
        """Set the expected baseline request rate for anomaly detection.

        Args:
            resource: Resource identifier.
            baseline_rps: Expected requests per second.
        """
        self._baseline_rates[resource] = baseline_rps

    def detect_anomaly(
        self,
        source_ip: str,
        resource: str,
        observed_rps: float,
    ) -> ThreatEvent | None:
        """Detect anomalous request rates using Z-score comparison.

        Args:
            source_ip: Client IP.
            resource: Resource being accessed.
            observed_rps: Current observed request rate.

        Returns:
            :class:`ThreatEvent` if anomalous, ``None`` if normal.
        """
        baseline = self._baseline_rates.get(resource)
        if baseline is None:
            return None

        # Simple ratio-based anomaly detection
        ratio = observed_rps / (baseline + 1e-6)
        if ratio > 5.0:
            event = self._fire_event(
                "anomaly",
                source_ip,
                resource,
                details={"observed_rps": observed_rps, "baseline_rps": baseline, "ratio": ratio},
                severity="high" if ratio > 10.0 else "medium",
            )
            return event
        return None

    def _fire_event(
        self,
        event_type: str,
        source_ip: str,
        resource: str,
        details: dict[str, Any] | None = None,
        severity: str = "medium",
    ) -> ThreatEvent:
        """Create and record a threat event.

        Args:
            event_type: Event category.
            source_ip: Originating IP.
            resource: Affected resource.
            details: Supplementary data.
            severity: Severity label.

        Returns:
            The recorded :class:`ThreatEvent`.
        """
        self._event_counter += 1
        event = ThreatEvent(
            event_id=f"threat_{self._event_counter:06d}",
            event_type=event_type,
            source_ip=source_ip,
            resource=resource,
            details=details or {},
            severity=severity,
        )
        self.threat_log.append(event)
        log = logger.warning if severity == "high" else logger.debug
        log("ThreatEvent [{}] {}: {} → {}", severity, event_type, source_ip, resource)
        return event
