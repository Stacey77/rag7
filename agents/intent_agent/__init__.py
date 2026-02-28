"""
Intent Agent - Main Implementation
"""
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent, Message
from .intent_parser import IntentParser
from .script_generator import ScriptGenerator
from .validation import IntentValidator


class IntentAgent(BaseAgent):
    """Intent Agent - Processes user intents and translates to actionable scripts"""
    
    def __init__(self, agent_id: str = "intent_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.parser = None
        self.generator = None
        self.validator = None
        
    async def initialize(self) -> bool:
        """Initialize the intent agent"""
        try:
            use_ai = self.config.get("use_ai", False)
            api_key = self.config.get("api_key")
            
            self.parser = IntentParser()
            self.generator = ScriptGenerator(use_ai, api_key)
            self.validator = IntentValidator()
            
            self.logger.info("Intent Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Intent Agent: {str(e)}")
            return False
    
    async def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming intent-related messages"""
        
        message_type = message.message_type
        payload = message.payload
        
        if message_type == "parse_intent":
            # Parse user intent
            intent = await self.parser.parse_intent(payload.get("user_input", ""))
            
            # Validate intent
            validation = await self.validator.validate(intent)
            
            result = {
                "intent": intent,
                "validation": validation
            }
            
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="intent_parsed",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "generate_script":
            # Generate script from intent
            intent = payload.get("intent", {})
            script_result = await self.generator.generate_script(intent)
            
            # Validate generated script
            script_validation = await self.generator.validate_script(
                script_result["script"]
            )
            
            result = {
                "script": script_result,
                "validation": script_validation
            }
            
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="script_generated",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "modify_script":
            # Modify existing script
            modified_script = await self.generator.modify_script(
                payload.get("script", ""),
                payload.get("modifications", {})
            )
            
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="script_modified",
                payload={"script": modified_script},
                correlation_id=message.correlation_id
            )
        
        elif message_type == "process_intent_end_to_end":
            # Complete intent processing workflow
            user_input = payload.get("user_input", "")
            
            # Step 1: Parse intent
            intent = await self.parser.parse_intent(user_input)
            
            # Step 2: Validate intent
            intent_validation = await self.validator.validate(intent)
            
            if not intent_validation["valid"]:
                return Message(
                    sender=self.agent_id,
                    receiver=message.sender,
                    message_type="intent_processing_failed",
                    payload={
                        "intent": intent,
                        "validation": intent_validation,
                        "suggestions": await self.validator.suggest_corrections(
                            intent, intent_validation
                        )
                    },
                    correlation_id=message.correlation_id
                )
            
            # Step 3: Generate script
            script_result = await self.generator.generate_script(intent)
            
            # Step 4: Validate script
            script_validation = await self.generator.validate_script(
                script_result["script"]
            )
            
            result = {
                "intent": intent,
                "intent_validation": intent_validation,
                "script": script_result,
                "script_validation": script_validation,
                "ready_for_policy_check": script_validation["valid"]
            }
            
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="intent_processed",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        else:
            self.logger.warning(f"Unknown message type: {message_type}")
            return None
