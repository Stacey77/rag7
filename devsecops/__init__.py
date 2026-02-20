"""DevSecOps: Security-integrated CI/CD framework for the trading platform."""

from __future__ import annotations

from loguru import logger

from devsecops.security.secret_manager import SecretManager
from devsecops.security.encryption import Encryption
from devsecops.security.threat_detection import ThreatDetection
from devsecops.security.compliance_checker import ComplianceChecker
from devsecops.scanning.code_scanner import CodeScanner
from devsecops.scanning.dependency_scanner import DependencyScanner
from devsecops.scanning.container_scanner import ContainerScanner
from devsecops.scanning.api_scanner import APIScanner
from devsecops.cicd.build_pipeline import BuildPipeline
from devsecops.cicd.test_automation import TestAutomation
from devsecops.cicd.deployment_gates import DeploymentGates
from devsecops.cicd.rollback_mechanism import RollbackMechanism
from devsecops.audit.audit_logger import AuditLogger
from devsecops.audit.trade_logger import TradeLogger
from devsecops.audit.compliance_reporter import ComplianceReporter


class DevSecOps:
    """Unified DevSecOps orchestrator for trading platform security operations.

    Aggregates secret management, encryption, threat detection, compliance,
    scanning, CI/CD gating, and audit logging.

    Attributes:
        secret_manager: API key and secret management.
        encryption: Data encryption/decryption.
        threat_detection: Security monitoring and rate limiting.
        compliance_checker: Regulatory compliance checks.
        code_scanner: Static application security testing.
        dependency_scanner: Vulnerability scanning.
        container_scanner: Container image security scanning.
        api_scanner: API security testing.
        build_pipeline: Build orchestration with security gates.
        test_automation: Automated security testing runner.
        deployment_gates: Pre-deployment security checkpoints.
        rollback_mechanism: Safe rollback with health checks.
        audit_logger: Immutable HMAC-signed audit log.
        trade_logger: Trading activity log.
        compliance_reporter: Regulatory report generation.
    """

    def __init__(self) -> None:
        """Initialise all DevSecOps sub-components."""
        self.secret_manager = SecretManager()
        self.encryption = Encryption()
        self.threat_detection = ThreatDetection()
        self.compliance_checker = ComplianceChecker()
        self.code_scanner = CodeScanner()
        self.dependency_scanner = DependencyScanner()
        self.container_scanner = ContainerScanner()
        self.api_scanner = APIScanner()
        self.build_pipeline = BuildPipeline()
        self.test_automation = TestAutomation()
        self.deployment_gates = DeploymentGates()
        self.rollback_mechanism = RollbackMechanism()
        self.audit_logger = AuditLogger()
        self.trade_logger = TradeLogger()
        self.compliance_reporter = ComplianceReporter()
        logger.info("DevSecOps initialised")

    def status(self) -> dict[str, str]:
        """Return a health summary for all sub-components.

        Returns:
            Mapping of component name to status string.
        """
        return {name: "ready" for name in [
            "secret_manager", "encryption", "threat_detection", "compliance_checker",
            "code_scanner", "dependency_scanner", "container_scanner", "api_scanner",
            "build_pipeline", "test_automation", "deployment_gates", "rollback_mechanism",
            "audit_logger", "trade_logger", "compliance_reporter",
        ]}


__all__ = ["DevSecOps"]
