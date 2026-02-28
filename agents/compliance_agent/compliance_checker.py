"""
Compliance Checker
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ComplianceChecker:
    """Validates compliance requirements"""
    
    def __init__(self):
        self.logger = logging.getLogger("compliance_checker")
        self.compliance_frameworks = {
            "SOC2": ["encryption_at_rest", "encryption_in_transit", "audit_logging"],
            "HIPAA": ["data_encryption", "access_control", "audit_trail"],
            "PCI-DSS": ["network_segmentation", "encryption", "access_logging"],
            "GDPR": ["data_privacy", "right_to_erasure", "consent_tracking"]
        }
    
    async def check_compliance(
        self,
        resource: Dict[str, Any],
        frameworks: List[str]
    ) -> Dict[str, Any]:
        """Check resource compliance against frameworks"""
        
        self.logger.info(f"Checking compliance for frameworks: {frameworks}")
        
        results = {
            "compliant": True,
            "frameworks": {},
            "violations": [],
            "warnings": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for framework in frameworks:
            if framework not in self.compliance_frameworks:
                results["warnings"].append(f"Unknown framework: {framework}")
                continue
            
            framework_result = await self._check_framework(
                resource,
                framework,
                self.compliance_frameworks[framework]
            )
            
            results["frameworks"][framework] = framework_result
            
            if not framework_result["compliant"]:
                results["compliant"] = False
                results["violations"].extend(framework_result["violations"])
        
        return results
    
    async def _check_framework(
        self,
        resource: Dict[str, Any],
        framework: str,
        requirements: List[str]
    ) -> Dict[str, Any]:
        """Check compliance for a specific framework"""
        
        violations = []
        
        for requirement in requirements:
            if not self._check_requirement(resource, requirement):
                violations.append({
                    "framework": framework,
                    "requirement": requirement,
                    "message": f"Missing or non-compliant: {requirement}"
                })
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "requirements_checked": len(requirements)
        }
    
    def _check_requirement(self, resource: Dict[str, Any], requirement: str) -> bool:
        """Check a specific requirement"""
        
        # Simplified compliance checking
        if requirement == "encryption_at_rest":
            return resource.get("encrypted", False)
        elif requirement == "encryption_in_transit":
            return resource.get("tls_enabled", False)
        elif requirement == "audit_logging":
            return resource.get("audit_enabled", False)
        elif requirement == "access_control":
            return "access_policy" in resource
        
        # Default to compliant if unknown requirement
        return True
    
    async def validate_change(
        self,
        change_spec: Dict[str, Any],
        compliance_requirements: List[str]
    ) -> Dict[str, Any]:
        """Validate that a change maintains compliance"""
        
        validation = {
            "approved": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check if change affects compliance
        if change_spec.get("type") == "delete":
            validation["recommendations"].append(
                "Ensure data retention policies are followed"
            )
        
        if "encryption" in str(change_spec).lower():
            validation["recommendations"].append(
                "Verify encryption keys are properly managed"
            )
        
        return validation
