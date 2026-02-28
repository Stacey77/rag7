"""
Intent Parser - NLP-based intent understanding
"""
import logging
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class IntentParser:
    """Parse and understand user intents for automation"""
    
    def __init__(self):
        self.logger = logging.getLogger("intent_parser")
        self.intent_patterns = self._load_intent_patterns()
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent detection patterns"""
        return {
            "deploy": [
                r"deploy\s+(\w+)",
                r"roll\s?out\s+(\w+)",
                r"release\s+(\w+)",
                r"push\s+(\w+)\s+to\s+production"
            ],
            "scale": [
                r"scale\s+(\w+)\s+to\s+(\d+)",
                r"increase\s+(\w+)\s+replicas",
                r"reduce\s+(\w+)\s+instances"
            ],
            "migrate": [
                r"migrate\s+(\w+)\s+to\s+(\w+)",
                r"move\s+(\w+)\s+from\s+(\w+)\s+to\s+(\w+)"
            ],
            "backup": [
                r"backup\s+(\w+)",
                r"create\s+snapshot\s+of\s+(\w+)"
            ],
            "rollback": [
                r"rollback\s+(\w+)",
                r"revert\s+(\w+)",
                r"undo\s+deployment\s+of\s+(\w+)"
            ],
            "configure": [
                r"configure\s+(\w+)",
                r"update\s+(\w+)\s+config",
                r"set\s+(\w+)\s+to\s+(.+)"
            ]
        }
    
    async def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """Parse user intent from natural language"""
        
        user_input = user_input.lower().strip()
        
        # Detect intent type
        intent_type = self._detect_intent_type(user_input)
        
        # Extract entities
        entities = self._extract_entities(user_input, intent_type)
        
        # Determine scope
        scope = self._determine_scope(user_input)
        
        result = {
            "original_input": user_input,
            "intent_type": intent_type,
            "entities": entities,
            "scope": scope,
            "confidence": self._calculate_confidence(intent_type, entities)
        }
        
        self.logger.info(f"Parsed intent: {intent_type} (confidence: {result['confidence']:.2f})")
        
        return result
    
    def _detect_intent_type(self, text: str) -> str:
        """Detect the type of intent"""
        
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent_type
        
        return "unknown"
    
    def _extract_entities(self, text: str, intent_type: str) -> Dict[str, Any]:
        """Extract entities from text based on intent type"""
        
        entities = {}
        
        if intent_type in self.intent_patterns:
            for pattern in self.intent_patterns[intent_type]:
                match = re.search(pattern, text)
                if match:
                    groups = match.groups()
                    if len(groups) >= 1:
                        entities["target"] = groups[0]
                    if len(groups) >= 2:
                        entities["parameter"] = groups[1]
                    if len(groups) >= 3:
                        entities["additional"] = groups[2:]
                    break
        
        # Extract environment mentions
        env_pattern = r"(production|staging|development|dev|prod|test)"
        env_match = re.search(env_pattern, text)
        if env_match:
            entities["environment"] = env_match.group(1)
        
        # Extract region mentions
        region_pattern = r"(us-east|us-west|eu-west|eu-central|ap-south|ap-northeast)-(\d)"
        region_match = re.search(region_pattern, text)
        if region_match:
            entities["region"] = region_match.group(0)
        
        return entities
    
    def _determine_scope(self, text: str) -> Dict[str, Any]:
        """Determine the scope of the operation"""
        
        scope = {
            "global": False,
            "multi_region": False,
            "regions": [],
            "services": []
        }
        
        # Check for global keywords
        if any(word in text for word in ["all", "global", "everywhere"]):
            scope["global"] = True
        
        # Check for multi-region
        if any(word in text for word in ["multi-region", "all regions", "cross-region"]):
            scope["multi_region"] = True
        
        return scope
    
    def _calculate_confidence(self, intent_type: str, entities: Dict[str, Any]) -> float:
        """Calculate confidence score for the parsed intent"""
        
        confidence = 0.0
        
        # Base confidence from intent detection
        if intent_type != "unknown":
            confidence += 0.5
        
        # Boost from entity extraction
        if "target" in entities:
            confidence += 0.3
        if "environment" in entities:
            confidence += 0.1
        if "parameter" in entities:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    async def validate_intent(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parsed intent"""
        
        validation = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check confidence threshold
        if intent.get("confidence", 0) < 0.5:
            validation["valid"] = False
            validation["errors"].append("Low confidence in intent parsing")
        
        # Check for required entities
        if intent.get("intent_type") != "unknown":
            if not intent.get("entities", {}).get("target"):
                validation["warnings"].append("No target specified")
        
        return validation
