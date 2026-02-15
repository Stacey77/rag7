"""
Blast Radius Prediction System
"""
import logging
from typing import Dict, Any, List
from enum import Enum

logger = logging.getLogger(__name__)


class BlastRadiusLevel(Enum):
    """Blast radius severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalDecision(Enum):
    """Approval workflow decisions"""
    AUTO_APPROVE = "auto_approve"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"


class BlastRadiusPredictor:
    """Predicts the impact radius of infrastructure changes"""
    
    def __init__(self):
        self.logger = logging.getLogger("blast_radius")
        self.impact_weights = {
            "affected_services": 0.3,
            "affected_regions": 0.25,
            "affected_users": 0.25,
            "data_impact": 0.2
        }
    
    async def predict_impact(
        self,
        change_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict the blast radius of a change"""
        
        # Extract change details
        change_type = change_spec.get("type", "unknown")
        affected_resources = change_spec.get("resources", [])
        scope = change_spec.get("scope", {})
        
        # Calculate impact scores
        impact_score = self._calculate_impact_score(change_spec)
        blast_level = self._determine_blast_level(impact_score)
        approval_decision = self._determine_approval(blast_level)
        
        # Predict affected components
        affected_components = self._predict_affected_components(
            affected_resources,
            scope
        )
        
        result = {
            "impact_score": impact_score,
            "blast_level": blast_level.value,
            "approval_decision": approval_decision.value,
            "affected_components": affected_components,
            "estimated_affected_services": len(affected_components.get("services", [])),
            "estimated_affected_regions": len(affected_components.get("regions", [])),
            "estimated_downtime_minutes": self._estimate_downtime(change_spec),
            "rollback_complexity": self._assess_rollback_complexity(change_spec),
            "recommendations": self._generate_recommendations(blast_level)
        }
        
        self.logger.info(
            f"Blast radius prediction: {blast_level.value} "
            f"(score: {impact_score:.2f})"
        )
        
        return result
    
    def _calculate_impact_score(self, change_spec: Dict[str, Any]) -> float:
        """Calculate overall impact score (0-1)"""
        score = 0.0
        
        # Number of affected services
        services = change_spec.get("resources", [])
        service_impact = min(len(services) / 10, 1.0)  # Normalize to 0-1
        score += service_impact * self.impact_weights["affected_services"]
        
        # Number of affected regions
        regions = change_spec.get("scope", {}).get("regions", [])
        region_impact = min(len(regions) / 5, 1.0)  # Normalize to 0-1
        score += region_impact * self.impact_weights["affected_regions"]
        
        # Estimated user impact
        user_impact = change_spec.get("scope", {}).get("user_impact_percent", 0) / 100
        score += user_impact * self.impact_weights["affected_users"]
        
        # Data sensitivity
        data_sensitivity = change_spec.get("data_sensitivity", "low")
        data_impact = {"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 1.0}.get(
            data_sensitivity, 0.2
        )
        score += data_impact * self.impact_weights["data_impact"]
        
        return score
    
    def _determine_blast_level(self, impact_score: float) -> BlastRadiusLevel:
        """Determine blast radius level from impact score"""
        if impact_score >= 0.75:
            return BlastRadiusLevel.CRITICAL
        elif impact_score >= 0.5:
            return BlastRadiusLevel.HIGH
        elif impact_score >= 0.25:
            return BlastRadiusLevel.MEDIUM
        else:
            return BlastRadiusLevel.LOW
    
    def _determine_approval(self, blast_level: BlastRadiusLevel) -> ApprovalDecision:
        """Determine approval decision based on blast level"""
        if blast_level == BlastRadiusLevel.CRITICAL:
            return ApprovalDecision.DENY
        elif blast_level == BlastRadiusLevel.HIGH:
            return ApprovalDecision.REQUIRE_APPROVAL
        elif blast_level == BlastRadiusLevel.MEDIUM:
            return ApprovalDecision.REQUIRE_APPROVAL
        else:
            return ApprovalDecision.AUTO_APPROVE
    
    def _predict_affected_components(
        self,
        resources: List[str],
        scope: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Predict which components will be affected"""
        
        affected = {
            "services": resources,
            "regions": scope.get("regions", []),
            "dependencies": self._find_dependencies(resources),
            "databases": scope.get("databases", []),
            "networks": scope.get("networks", [])
        }
        
        return affected
    
    def _find_dependencies(self, resources: List[str]) -> List[str]:
        """Find dependent resources (simplified)"""
        # In a real implementation, this would query a dependency graph
        dependencies = []
        for resource in resources:
            # Simplified dependency detection
            if "api" in resource.lower():
                dependencies.append(f"{resource}-database")
                dependencies.append(f"{resource}-cache")
        return dependencies
    
    def _estimate_downtime(self, change_spec: Dict[str, Any]) -> int:
        """Estimate potential downtime in minutes"""
        change_type = change_spec.get("type", "update")
        complexity = change_spec.get("complexity", "medium")
        
        base_downtime = {
            "create": 5,
            "update": 2,
            "delete": 10,
            "migrate": 30
        }.get(change_type, 5)
        
        complexity_multiplier = {
            "low": 0.5,
            "medium": 1.0,
            "high": 2.0
        }.get(complexity, 1.0)
        
        return int(base_downtime * complexity_multiplier)
    
    def _assess_rollback_complexity(self, change_spec: Dict[str, Any]) -> str:
        """Assess how complex rollback would be"""
        change_type = change_spec.get("type", "update")
        has_data_migration = change_spec.get("data_migration", False)
        
        if has_data_migration or change_type == "migrate":
            return "high"
        elif change_type == "delete":
            return "high"
        elif change_type == "create":
            return "low"
        else:
            return "medium"
    
    def _generate_recommendations(
        self,
        blast_level: BlastRadiusLevel
    ) -> List[str]:
        """Generate recommendations based on blast level"""
        recommendations = []
        
        if blast_level in [BlastRadiusLevel.HIGH, BlastRadiusLevel.CRITICAL]:
            recommendations.extend([
                "Schedule change during maintenance window",
                "Notify stakeholders before execution",
                "Prepare rollback plan",
                "Enable enhanced monitoring",
                "Consider canary deployment"
            ])
        elif blast_level == BlastRadiusLevel.MEDIUM:
            recommendations.extend([
                "Review with team before execution",
                "Have rollback plan ready",
                "Monitor metrics closely"
            ])
        else:
            recommendations.append("Safe to proceed with standard monitoring")
        
        return recommendations
