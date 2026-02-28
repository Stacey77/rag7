"""
Intent Validation
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class IntentValidator:
    """Validates intents before processing"""
    
    def __init__(self):
        self.logger = logging.getLogger("intent_validator")
        self.validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load validation rules for different intent types"""
        return {
            "deploy": {
                "required_entities": ["target"],
                "optional_entities": ["environment", "region"],
                "allowed_environments": ["development", "staging", "production"]
            },
            "scale": {
                "required_entities": ["target", "parameter"],
                "optional_entities": ["environment"],
                "validation": {
                    "parameter": lambda x: x.isdigit() and 0 < int(x) < 100
                }
            },
            "migrate": {
                "required_entities": ["target"],
                "optional_entities": ["parameter"],
                "requires_approval": True
            },
            "backup": {
                "required_entities": ["target"],
                "optional_entities": []
            },
            "rollback": {
                "required_entities": ["target"],
                "optional_entities": ["environment"]
            }
        }
    
    async def validate(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an intent"""
        
        intent_type = intent.get("intent_type", "unknown")
        entities = intent.get("entities", {})
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "requires_approval": False
        }
        
        # Check if intent type is recognized
        if intent_type == "unknown":
            validation_result["valid"] = False
            validation_result["errors"].append("Unknown intent type")
            return validation_result
        
        # Get validation rules for this intent type
        rules = self.validation_rules.get(intent_type, {})
        
        # Check required entities
        required = rules.get("required_entities", [])
        for entity in required:
            if entity not in entities:
                validation_result["valid"] = False
                validation_result["errors"].append(
                    f"Missing required entity: {entity}"
                )
        
        # Validate entity values
        validators = rules.get("validation", {})
        for entity, validator in validators.items():
            if entity in entities:
                if not validator(entities[entity]):
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Invalid value for {entity}: {entities[entity]}"
                    )
        
        # Check if approval is required
        if rules.get("requires_approval", False):
            validation_result["requires_approval"] = True
        
        # Environment validation
        allowed_envs = rules.get("allowed_environments", [])
        if allowed_envs and "environment" in entities:
            if entities["environment"] not in allowed_envs:
                validation_result["warnings"].append(
                    f"Unusual environment: {entities['environment']}"
                )
        
        self.logger.info(
            f"Validated intent {intent_type}: "
            f"{'valid' if validation_result['valid'] else 'invalid'}"
        )
        
        return validation_result
    
    async def suggest_corrections(
        self,
        intent: Dict[str, Any],
        validation_result: Dict[str, Any]
    ) -> List[str]:
        """Suggest corrections for invalid intents"""
        
        suggestions = []
        
        for error in validation_result.get("errors", []):
            if "Missing required entity" in error:
                entity = error.split(":")[-1].strip()
                suggestions.append(
                    f"Please specify the {entity} for this operation"
                )
            elif "Invalid value" in error:
                suggestions.append(
                    f"Please provide a valid value. {error}"
                )
        
        return suggestions
