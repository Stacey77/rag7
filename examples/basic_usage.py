"""
Example: Basic AGI System Usage
Demonstrates core functionality of the AGI system
"""
from agi_system import create_agi_system
from loguru import logger


def main():
    """Main example demonstrating AGI system capabilities"""
    
    print("=" * 80)
    print("AGI System - Basic Usage Example")
    print("=" * 80)
    print()
    
    # Initialize AGI system
    print("1. Initializing AGI System...")
    agi = create_agi_system()
    print("✓ AGI System initialized\n")
    
    # Example 1: Add knowledge to the system
    print("2. Adding knowledge to the system...")
    agi.add_knowledge(
        "Artificial Intelligence is a branch of computer science focused on creating intelligent machines.",
        metadata={"domain": "computer_science", "topic": "AI"}
    )
    agi.add_knowledge(
        "Machine learning is a subset of AI that enables systems to learn from data.",
        metadata={"domain": "computer_science", "topic": "ML"}
    )
    agi.add_knowledge(
        "Neural networks are computing systems inspired by biological neural networks.",
        metadata={"domain": "computer_science", "topic": "neural_networks"}
    )
    print("✓ Added 3 knowledge items\n")
    
    # Example 2: Add structured knowledge
    print("3. Adding structured knowledge (knowledge graph)...")
    agi.add_structured_knowledge("AI", "is_a", "Computer_Science_Field")
    agi.add_structured_knowledge("Machine_Learning", "is_subset_of", "AI")
    agi.add_structured_knowledge("Neural_Networks", "implements", "Machine_Learning")
    print("✓ Added structured knowledge triples\n")
    
    # Example 3: Process user input with emotional reasoning
    print("4. Processing user input with emotional reasoning...")
    user_input = "I'm excited to learn about artificial intelligence!"
    result = agi.process_input(user_input)
    
    print(f"User Input: {user_input}")
    print(f"Response: {result['response']}")
    print(f"Detected Emotion: {result['emotional_analysis']['affective_state']['primary_emotion']}")
    print(f"Valence: {result['emotional_analysis']['affective_state']['valence']:.2f}")
    print()
    
    # Example 4: Query knowledge base
    print("5. Querying knowledge base...")
    query_result = agi.query_knowledge("What is machine learning?", method="vector")
    
    print(f"Query: What is machine learning?")
    if query_result.get("results"):
        print(f"Found {len(query_result['results'])} relevant documents:")
        for i, doc in enumerate(query_result['results'][:2], 1):
            print(f"  {i}. {doc['content'][:100]}...")
            print(f"     Similarity: {doc['similarity']:.3f}")
    print()
    
    # Example 5: Symbolic reasoning
    print("6. Performing symbolic reasoning...")
    agi.symbolic_engine.logic_system.add_fact("AI is intelligent")
    agi.symbolic_engine.logic_system.add_fact("Machine_Learning uses AI")
    agi.symbolic_engine.logic_system.add_rule(
        name="intelligence_transfer",
        premises=["AI is intelligent", "Machine_Learning uses AI"],
        conclusion="Machine_Learning is intelligent"
    )
    
    reasoning_result = agi.reason("Machine_Learning is intelligent", reasoning_type="symbolic")
    print(f"Query: Is Machine Learning intelligent?")
    print(f"Method: {reasoning_result['method']}")
    print(f"Result: {'Proven' if reasoning_result['result'] else 'Not proven'}")
    print()
    
    # Example 6: Set and execute a goal
    print("7. Setting and executing a goal...")
    goal_id = agi.set_goal(
        "Understand the relationship between AI and Machine Learning",
        priority="high"
    )
    print(f"Goal ID: {goal_id}")
    
    execution_result = agi.execute_goal(goal_id)
    print(f"Goal Status: {execution_result['status']}")
    print(f"Completed Tasks: {execution_result['completed_tasks']}/{execution_result.get('iterations', 0)}")
    print()
    
    # Example 7: Get system status
    print("8. Getting system status...")
    status = agi.get_system_status()
    
    print("System Status:")
    print(f"  - Active Goal: {status['agent_controller']['active_goal']}")
    print(f"  - Knowledge Items: {status['knowledge_layer']['total_knowledge_items']}")
    print(f"  - Memory Stats:")
    print(f"    • Short-term: {status['langchain_layer']['memory_stats']['short_term']['count']}")
    print(f"    • Long-term: {status['langchain_layer']['memory_stats']['long_term']['count']}")
    print(f"  - Symbolic Reasoning: {status['symbolic_reasoning']['num_facts']} facts, {status['symbolic_reasoning']['num_rules']} rules")
    print()
    
    # Example 8: Consolidate memories
    print("9. Consolidating memories...")
    consolidation_result = agi.consolidate_memories()
    print(f"Consolidated {consolidation_result['short_term_consolidated']} memories")
    print(f"Short-term remaining: {consolidation_result['short_term_remaining']}")
    print(f"Long-term total: {consolidation_result['long_term_total']}")
    print()
    
    print("=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
