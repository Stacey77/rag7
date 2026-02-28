"""
Policy Enforcement Module
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .policy_engine import PolicyEngine, LocalPolicyEngine
from .blast_radius import BlastRadiusPredictor, ApprovalDecision

logger = logging.getLogger(__name__)


class PolicyEnforcement:
    """Enforces governance policies across all automation"""
    
    def __init__(self, use_opa: bool = False, opa_url: str = "http://localhost:8181"):
        self.use_opa = use_opa
        if use_opa:
            self.policy_engine = PolicyEngine(opa_url)
        else:
            self.policy_engine = LocalPolicyEngine()
        
        self.blast_predictor = BlastRadiusPredictor()
        self.logger = logging.getLogger("policy_enforcement")
        self.enforcement_history: List[Dict[str, Any]] = []
    
    async def enforce_policies(
        self,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enforce all applicable policies for an action"""
        
        self.logger.info(f"Enforcing policies for action: {action}")
        
        enforcement_result = {
            "action": action,
            "timestamp": datetime.utcnow().isoformat(),
            "allowed": True,
            "policy_checks": [],
            "blast_radius": None,
            "final_decision": None
        }
        
        # Step 1: Policy validation
        policy_result = await self.policy_engine.evaluate_policy(
            f"{action}/policy",
            context
        )
        enforcement_result["policy_checks"].append(policy_result)
        
        if not policy_result.get("allowed", False):
            enforcement_result["allowed"] = False
            enforcement_result["final_decision"] = "denied_by_policy"
            self.logger.warning(f"Action denied by policy: {action}")
            self._record_enforcement(enforcement_result)
            return enforcement_result
        
        # Step 2: Blast radius prediction
        if context.get("change_spec"):
            blast_result = await self.blast_predictor.predict_impact(
                context["change_spec"]
            )
            enforcement_result["blast_radius"] = blast_result
            
            # Check approval decision
            approval_decision = blast_result.get("approval_decision")
            if approval_decision == ApprovalDecision.DENY.value:
                enforcement_result["allowed"] = False
                enforcement_result["final_decision"] = "denied_by_blast_radius"
                self.logger.warning(
                    f"Action denied due to critical blast radius: {action}"
                )
            elif approval_decision == ApprovalDecision.REQUIRE_APPROVAL.value:
                enforcement_result["final_decision"] = "requires_approval"
                enforcement_result["approval_required"] = True
                self.logger.info(f"Action requires approval: {action}")
            else:
                enforcement_result["final_decision"] = "auto_approved"
                self.logger.info(f"Action auto-approved: {action}")
        else:
            enforcement_result["final_decision"] = "approved"
        
        # Record enforcement decision
        self._record_enforcement(enforcement_result)
        
        return enforcement_result
    
    async def validate_before_execution(
        self,
        script: str,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate script before execution"""
        
        validation_result = {
            "script_hash": hash(script),
            "validated": False,
            "issues": []
        }
        
        # Policy validation
        policy_check = await self.policy_engine.validate_script(
            script,
            execution_context
        )
        
        if not policy_check.get("allowed", False):
            validation_result["issues"].extend(
                policy_check.get("violations", [])
            )
        else:
            validation_result["validated"] = True
        
        return validation_result
    
    def _record_enforcement(self, enforcement_result: Dict[str, Any]):
        """Record enforcement decision for audit"""
        self.enforcement_history.append(enforcement_result)
        
        # Keep only last 1000 records
        if len(self.enforcement_history) > 1000:
            self.enforcement_history = self.enforcement_history[-1000:]
    
    def get_enforcement_history(
        self,
        limit: int = 100,
        action_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get enforcement history"""
        history = self.enforcement_history
        
        if action_filter:
            history = [
                h for h in history
                if h.get("action") == action_filter
            ]
        
        return history[-limit:]
    
    async def simulate_policy(
        self,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate policy enforcement without executing"""
        
        simulation = await self.enforce_policies(action, context)
        simulation["simulated"] = True
        
        return simulation
