"""
Policy Engine - OPA Integration
"""
import logging
import requests
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)


class PolicyEngine:
    """OPA (Open Policy Agent) Integration"""
    
    def __init__(self, opa_url: str = "http://localhost:8181"):
        self.opa_url = opa_url
        self.logger = logging.getLogger("policy_engine")
    
    async def evaluate_policy(
        self,
        policy_name: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate input against OPA policy"""
        try:
            url = f"{self.opa_url}/v1/data/{policy_name}"
            response = requests.post(
                url,
                json={"input": input_data},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"Policy evaluation successful: {policy_name}")
                return {
                    "allowed": result.get("result", {}).get("allow", False),
                    "violations": result.get("result", {}).get("violations", []),
                    "decision": result.get("result", {}),
                    "policy": policy_name
                }
            else:
                self.logger.error(f"Policy evaluation failed: {response.status_code}")
                return {
                    "allowed": False,
                    "error": f"HTTP {response.status_code}",
                    "policy": policy_name
                }
                
        except Exception as e:
            self.logger.error(f"Error evaluating policy: {str(e)}", exc_info=True)
            return {
                "allowed": False,
                "error": str(e),
                "policy": policy_name
            }
    
    async def validate_deployment(
        self,
        deployment_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate deployment against policies"""
        return await self.evaluate_policy("deployment/validate", deployment_spec)
    
    async def validate_script(
        self,
        script: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate script execution against policies"""
        input_data = {
            "script": script,
            "context": context
        }
        return await self.evaluate_policy("script/validate", input_data)
    
    async def check_compliance(
        self,
        resource: Dict[str, Any],
        compliance_rules: List[str]
    ) -> Dict[str, Any]:
        """Check resource compliance"""
        input_data = {
            "resource": resource,
            "rules": compliance_rules
        }
        return await self.evaluate_policy("compliance/check", input_data)


class LocalPolicyEngine:
    """Local policy engine for when OPA is not available"""
    
    def __init__(self):
        self.policies: Dict[str, Any] = {}
        self.logger = logging.getLogger("local_policy_engine")
    
    def load_policy(self, policy_name: str, policy_rules: Dict[str, Any]):
        """Load a policy definition"""
        self.policies[policy_name] = policy_rules
        self.logger.info(f"Loaded policy: {policy_name}")
    
    async def evaluate_policy(
        self,
        policy_name: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate input against local policy"""
        if policy_name not in self.policies:
            return {
                "allowed": False,
                "error": f"Policy not found: {policy_name}",
                "policy": policy_name
            }
        
        policy = self.policies[policy_name]
        violations = []
        
        # Simple rule evaluation
        for rule_name, rule_config in policy.items():
            if not self._evaluate_rule(rule_config, input_data):
                violations.append({
                    "rule": rule_name,
                    "message": rule_config.get("message", "Rule violated")
                })
        
        return {
            "allowed": len(violations) == 0,
            "violations": violations,
            "policy": policy_name
        }
    
    def _evaluate_rule(self, rule: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """Evaluate a single rule"""
        # Simple evaluation logic
        rule_type = rule.get("type", "allow")
        
        if rule_type == "allow":
            return True
        elif rule_type == "deny":
            return False
        elif rule_type == "require":
            required_field = rule.get("field")
            return required_field in data
        
        return True
