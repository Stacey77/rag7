"""
Example: Basic Platform Usage

This example demonstrates basic usage of the platform including:
- Starting the platform
- Processing user intents
- Deploying applications
- Checking policies
"""

import asyncio
import logging
from agents.core.agent_orchestrator import AgentOrchestrator
from agents.core.base_agent import Message
from agents.policy_agent import PolicyAgent
from agents.intent_agent import IntentAgent
from agents.deployment_agent import DeploymentAgent
from agents.compliance_agent import ComplianceAgent
from agents.inference_agent import InferenceAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main example function"""
    
    logger.info("=== Multi-Agent Platform Example ===")
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator.get_instance()
    
    # Register agents
    policy_agent = PolicyAgent()
    intent_agent = IntentAgent()
    deployment_agent = DeploymentAgent()
    compliance_agent = ComplianceAgent()
    inference_agent = InferenceAgent()
    
    orchestrator.register_agent(policy_agent)
    orchestrator.register_agent(intent_agent)
    orchestrator.register_agent(deployment_agent)
    orchestrator.register_agent(compliance_agent)
    orchestrator.register_agent(inference_agent)
    
    # Start agents in background
    agent_tasks = asyncio.create_task(orchestrator.start_all_agents())
    
    # Give agents time to initialize
    await asyncio.sleep(1)
    
    logger.info("\n=== Example 1: Process User Intent ===")
    user_input = "Deploy my-app to production with 3 replicas"
    logger.info(f"User input: {user_input}")
    
    # Send message to intent agent
    intent_message = Message(
        sender="example",
        receiver="intent_agent",
        message_type="parse_intent",
        payload={"user_input": user_input}
    )
    
    await intent_agent.receive_message(intent_message)
    await asyncio.sleep(0.5)  # Wait for processing
    
    logger.info("\n=== Example 2: Check Policy ===")
    policy_message = Message(
        sender="example",
        receiver="policy_agent",
        message_type="predict_blast_radius",
        payload={
            "change_spec": {
                "type": "deploy",
                "resources": ["my-app"],
                "scope": {
                    "regions": ["us-east-1"],
                    "user_impact_percent": 10
                },
                "data_sensitivity": "medium"
            }
        }
    )
    
    await policy_agent.receive_message(policy_message)
    await asyncio.sleep(0.5)
    
    logger.info("\n=== Example 3: Deploy Application ===")
    deploy_message = Message(
        sender="example",
        receiver="deployment_agent",
        message_type="deploy",
        payload={
            "spec": {
                "name": "my-app",
                "image": "my-app:v1.0.0",
                "replicas": 3,
                "environment": "production"
            }
        }
    )
    
    await deployment_agent.receive_message(deploy_message)
    await asyncio.sleep(0.5)
    
    logger.info("\n=== Example 4: Check Compliance ===")
    compliance_message = Message(
        sender="example",
        receiver="compliance_agent",
        message_type="check_compliance",
        payload={
            "resource": {
                "encrypted": True,
                "tls_enabled": True,
                "audit_enabled": True
            },
            "resource_id": "my-app",
            "frameworks": ["SOC2"]
        }
    )
    
    await compliance_agent.receive_message(compliance_message)
    await asyncio.sleep(0.5)
    
    logger.info("\n=== Example 5: Get Platform Status ===")
    status = orchestrator.get_all_agent_status()
    logger.info("Platform Status:")
    for agent_id, agent_status in status.items():
        logger.info(f"  {agent_id}: {agent_status['status']}")
    
    # Cleanup
    logger.info("\n=== Shutting Down ===")
    await orchestrator.stop_all_agents()
    
    logger.info("Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
