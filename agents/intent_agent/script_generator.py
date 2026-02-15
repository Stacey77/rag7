"""
AI Script Generator
"""
import logging
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)


class ScriptGenerator:
    """AI-powered script generation from intents"""
    
    def __init__(self, use_ai: bool = False, api_key: Optional[str] = None):
        self.use_ai = use_ai
        self.api_key = api_key
        self.logger = logging.getLogger("script_generator")
        self.script_templates = self._load_script_templates()
    
    def _load_script_templates(self) -> Dict[str, str]:
        """Load script templates for different intent types"""
        return {
            "deploy": """#!/bin/bash
# Deploy {target} to {environment}
echo "Deploying {target}..."
kubectl apply -f {target}-deployment.yaml
kubectl rollout status deployment/{target}
echo "Deployment complete"
""",
            "scale": """#!/bin/bash
# Scale {target} to {replicas} replicas
echo "Scaling {target}..."
kubectl scale deployment/{target} --replicas={replicas}
kubectl rollout status deployment/{target}
echo "Scaling complete"
""",
            "backup": """#!/bin/bash
# Backup {target}
echo "Creating backup of {target}..."
kubectl exec -it {target} -- pg_dump -U postgres > backup_{target}_$(date +%Y%m%d_%H%M%S).sql
echo "Backup complete"
""",
            "rollback": """#!/bin/bash
# Rollback {target}
echo "Rolling back {target}..."
kubectl rollout undo deployment/{target}
kubectl rollout status deployment/{target}
echo "Rollback complete"
""",
            "configure": """#!/bin/bash
# Configure {target}
echo "Configuring {target}..."
kubectl create configmap {target}-config --from-literal={parameter}
kubectl rollout restart deployment/{target}
echo "Configuration complete"
"""
        }
    
    async def generate_script(
        self,
        intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate automation script from intent"""
        
        intent_type = intent.get("intent_type", "unknown")
        entities = intent.get("entities", {})
        
        if self.use_ai and self.api_key:
            # Use AI model for script generation
            script = await self._generate_with_ai(intent)
        else:
            # Use template-based generation
            script = self._generate_from_template(intent_type, entities)
        
        result = {
            "script": script,
            "intent_type": intent_type,
            "language": "bash",
            "metadata": {
                "generated_from": "ai" if self.use_ai else "template",
                "entities": entities
            }
        }
        
        self.logger.info(f"Generated script for intent: {intent_type}")
        
        return result
    
    def _generate_from_template(
        self,
        intent_type: str,
        entities: Dict[str, Any]
    ) -> str:
        """Generate script from template"""
        
        if intent_type not in self.script_templates:
            return f"# No template available for intent: {intent_type}\necho 'Manual implementation required'"
        
        template = self.script_templates[intent_type]
        
        # Replace placeholders
        script = template.format(
            target=entities.get("target", "UNKNOWN"),
            environment=entities.get("environment", "production"),
            replicas=entities.get("parameter", "3"),
            parameter=entities.get("parameter", "config=value")
        )
        
        return script
    
    async def _generate_with_ai(self, intent: Dict[str, Any]) -> str:
        """Generate script using AI model (placeholder for actual implementation)"""
        
        # This would integrate with OpenAI or another LLM
        # For now, fallback to template
        self.logger.info("AI generation requested but using template fallback")
        return self._generate_from_template(
            intent.get("intent_type"),
            intent.get("entities", {})
        )
    
    async def modify_script(
        self,
        original_script: str,
        modifications: Dict[str, Any]
    ) -> str:
        """Modify existing script based on requirements"""
        
        modified = original_script
        
        # Apply modifications
        if "add_logging" in modifications:
            modified = self._add_logging(modified)
        
        if "add_error_handling" in modifications:
            modified = self._add_error_handling(modified)
        
        if "add_rollback" in modifications:
            modified = self._add_rollback_logic(modified)
        
        return modified
    
    def _add_logging(self, script: str) -> str:
        """Add logging to script"""
        lines = script.split("\n")
        logged_lines = []
        
        for line in lines:
            logged_lines.append(line)
            if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("echo"):
                logged_lines.append(f'echo "Executing: {line.strip()}"')
        
        return "\n".join(logged_lines)
    
    def _add_error_handling(self, script: str) -> str:
        """Add error handling to script"""
        error_handler = """
set -e
trap 'echo "Error occurred at line $LINENO"; exit 1' ERR
"""
        return error_handler + script
    
    def _add_rollback_logic(self, script: str) -> str:
        """Add rollback logic to script"""
        rollback = """
# Rollback function
rollback() {
    echo "Rolling back changes..."
    # Add rollback steps here
}
trap rollback EXIT
"""
        return rollback + script
    
    async def validate_script(self, script: str) -> Dict[str, Any]:
        """Validate generated script"""
        
        validation = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "security_checks": []
        }
        
        # Check for dangerous commands
        dangerous_patterns = [
            r"rm\s+-rf\s+/",
            r"dd\s+if=",
            r":\(\)\{\s*:\|:&\s*\};:",  # Fork bomb
            r"mkfs\.",
        ]
        
        for pattern in dangerous_patterns:
            import re
            if re.search(pattern, script):
                validation["valid"] = False
                validation["issues"].append(f"Dangerous pattern detected: {pattern}")
        
        # Check for best practices
        if "set -e" not in script:
            validation["warnings"].append("Script does not exit on error")
        
        if not script.strip().startswith("#!/bin/bash"):
            validation["warnings"].append("Missing shebang")
        
        return validation
