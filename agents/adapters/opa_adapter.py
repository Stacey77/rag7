"""
OPA (Open Policy Agent) Adapter
"""
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)


class OPAAdapter:
    """Adapter for Open Policy Agent integration"""
    
    def __init__(self, opa_url: str = "http://localhost:8181"):
        self.opa_url = opa_url
        self.logger = logging.getLogger("opa_adapter")
    
    async def evaluate_policy(
        self,
        policy_path: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate policy via OPA"""
        
        try:
            url = f"{self.opa_url}/v1/data/{policy_path}"
            
            response = requests.post(
                url,
                json={"input": input_data},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"OPA request failed: {response.status_code}")
                return {"error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.ConnectionError:
            self.logger.warning("OPA not available, using fallback")
            return self._fallback_evaluation(input_data)
        except Exception as e:
            self.logger.error(f"OPA evaluation error: {str(e)}")
            return {"error": str(e)}
    
    def _fallback_evaluation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback evaluation when OPA is unavailable"""
        return {
            "result": {
                "allow": True,
                "message": "Fallback evaluation - OPA unavailable"
            }
        }
    
    async def upload_policy(
        self,
        policy_name: str,
        policy_rego: str
    ) -> Dict[str, Any]:
        """Upload policy to OPA"""
        
        try:
            url = f"{self.opa_url}/v1/policies/{policy_name}"
            
            response = requests.put(
                url,
                data=policy_rego,
                headers={"Content-Type": "text/plain"},
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                self.logger.info(f"Policy uploaded: {policy_name}")
                return {"status": "success"}
            else:
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            self.logger.error(f"Policy upload error: {str(e)}")
            return {"status": "failed", "error": str(e)}
