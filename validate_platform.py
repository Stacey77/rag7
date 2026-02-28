#!/usr/bin/env python3
"""
Platform Validation Script

This script validates that all core components are working correctly.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from agents.core.base_agent import BaseAgent, Message, AgentStatus
        print("  ✓ Core agent framework")
    except Exception as e:
        print(f"  ✗ Core agent framework: {e}")
        return False
    
    try:
        from agents.core.agent_orchestrator import AgentOrchestrator
        print("  ✓ Agent orchestrator")
    except Exception as e:
        print(f"  ✗ Agent orchestrator: {e}")
        return False
    
    try:
        from agents.policy_agent import PolicyAgent
        print("  ✓ Policy agent")
    except Exception as e:
        print(f"  ✗ Policy agent: {e}")
        return False
    
    try:
        from agents.intent_agent import IntentAgent
        print("  ✓ Intent agent")
    except Exception as e:
        print(f"  ✗ Intent agent: {e}")
        return False
    
    try:
        from agents.deployment_agent import DeploymentAgent
        print("  ✓ Deployment agent")
    except Exception as e:
        print(f"  ✗ Deployment agent: {e}")
        return False
    
    try:
        from agents.compliance_agent import ComplianceAgent
        print("  ✓ Compliance agent")
    except Exception as e:
        print(f"  ✗ Compliance agent: {e}")
        return False
    
    try:
        from agents.inference_agent import InferenceAgent
        print("  ✓ Inference agent")
    except Exception as e:
        print(f"  ✗ Inference agent: {e}")
        return False
    
    try:
        from agents.config.settings import settings
        print("  ✓ Configuration")
    except Exception as e:
        print(f"  ✗ Configuration: {e}")
        return False
    
    return True


def test_policy_enforcement():
    """Test policy enforcement and blast radius"""
    print("\nTesting policy enforcement...")
    
    try:
        from agents.policy_agent.blast_radius import BlastRadiusPredictor
        import asyncio
        
        predictor = BlastRadiusPredictor()
        
        change_spec = {
            "type": "deploy",
            "resources": ["test-app"],
            "scope": {
                "regions": ["us-east-1"],
                "user_impact_percent": 10
            },
            "data_sensitivity": "low"
        }
        
        result = asyncio.run(predictor.predict_impact(change_spec))
        
        print(f"  ✓ Blast radius prediction: {result['blast_level']}")
        print(f"  ✓ Approval decision: {result['approval_decision']}")
        return True
        
    except Exception as e:
        print(f"  ✗ Policy enforcement test failed: {e}")
        return False


def test_intent_parsing():
    """Test intent parsing"""
    print("\nTesting intent parsing...")
    
    try:
        from agents.intent_agent.intent_parser import IntentParser
        import asyncio
        
        parser = IntentParser()
        
        user_input = "deploy my-app to production with 5 replicas"
        result = asyncio.run(parser.parse_intent(user_input))
        
        print(f"  ✓ Intent type: {result['intent_type']}")
        print(f"  ✓ Confidence: {result['confidence']:.2f}")
        return True
        
    except Exception as e:
        print(f"  ✗ Intent parsing test failed: {e}")
        return False


def test_script_generation():
    """Test script generation"""
    print("\nTesting script generation...")
    
    try:
        from agents.intent_agent.script_generator import ScriptGenerator
        import asyncio
        
        generator = ScriptGenerator(use_ai=False)
        
        intent = {
            "intent_type": "deploy",
            "entities": {
                "target": "my-app",
                "environment": "production",
                "parameter": "5"
            }
        }
        
        result = asyncio.run(generator.generate_script(intent))
        
        print(f"  ✓ Script generated ({len(result['script'])} chars)")
        return True
        
    except Exception as e:
        print(f"  ✗ Script generation test failed: {e}")
        return False


def test_compliance():
    """Test compliance checking"""
    print("\nTesting compliance checking...")
    
    try:
        from agents.compliance_agent.compliance_checker import ComplianceChecker
        import asyncio
        
        checker = ComplianceChecker()
        
        resource = {
            "encrypted": True,
            "tls_enabled": True,
            "audit_enabled": True
        }
        
        result = asyncio.run(checker.check_compliance(resource, ["SOC2"]))
        
        print(f"  ✓ Compliance check: {'Compliant' if result['compliant'] else 'Non-compliant'}")
        return True
        
    except Exception as e:
        print(f"  ✗ Compliance test failed: {e}")
        return False


def main():
    """Main validation function"""
    print("=" * 60)
    print("Multi-Agent Agentic Infrastructure Platform")
    print("Validation Script")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Policy Enforcement", test_policy_enforcement()))
    results.append(("Intent Parsing", test_intent_parsing()))
    results.append(("Script Generation", test_script_generation()))
    results.append(("Compliance", test_compliance()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:30} {status}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All validation tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
