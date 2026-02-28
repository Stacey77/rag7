"""
Example: Symbolic Reasoning Demo
Demonstrates symbolic AI, logic inference, and knowledge graph reasoning
"""
from agi_system import create_agi_system


def test_logic_inference():
    """Test logical inference capabilities"""
    print("\n" + "=" * 80)
    print("Logic Inference Demo")
    print("=" * 80 + "\n")
    
    agi = create_agi_system()
    logic_system = agi.symbolic_engine.logic_system
    
    # Add facts
    print("Adding facts to the knowledge base:")
    logic_system.add_fact("Socrates is a man")
    logic_system.add_fact("All men are mortal")
    print("  ✓ Socrates is a man")
    print("  ✓ All men are mortal")
    print()
    
    # Add inference rule
    print("Adding inference rule:")
    logic_system.add_rule(
        name="mortality_rule",
        premises=["Socrates is a man", "All men are mortal"],
        conclusion="Socrates is mortal"
    )
    print("  ✓ IF (Socrates is a man AND All men are mortal) THEN Socrates is mortal")
    print()
    
    # Forward chaining
    print("Performing forward chaining inference:")
    new_facts = logic_system.forward_chaining()
    for fact in new_facts:
        print(f"  → Inferred: {fact.statement} (confidence: {fact.confidence:.2f})")
    print()
    
    # Backward chaining
    print("Performing backward chaining to prove goal:")
    goal = "Socrates is mortal"
    proven = logic_system.backward_chaining(goal)
    print(f"  Goal: {goal}")
    print(f"  Result: {'✓ PROVEN' if proven else '✗ NOT PROVEN'}")
    print()


def test_knowledge_graph_reasoning():
    """Test knowledge graph reasoning"""
    print("\n" + "=" * 80)
    print("Knowledge Graph Reasoning Demo")
    print("=" * 80 + "\n")
    
    agi = create_agi_system()
    kg = agi.symbolic_engine.knowledge_graph
    
    # Build a knowledge graph
    print("Building knowledge graph:")
    
    # Add entities
    entities = [
        ("Python", "programming_language", {"created": 1991}),
        ("Java", "programming_language", {"created": 1995}),
        ("TensorFlow", "ml_framework", {"domain": "deep_learning"}),
        ("PyTorch", "ml_framework", {"domain": "deep_learning"}),
    ]
    
    for entity_id, entity_type, props in entities:
        kg.add_entity(entity_id, entity_type, props)
        print(f"  ✓ Added entity: {entity_id} (type: {entity_type})")
    
    print()
    
    # Add relations
    print("Adding relations:")
    relations = [
        ("TensorFlow", "written_in", "Python"),
        ("PyTorch", "written_in", "Python"),
        ("TensorFlow", "competes_with", "PyTorch"),
        ("Python", "used_for", "AI"),
        ("Java", "used_for", "Enterprise"),
    ]
    
    for subject, predicate, obj in relations:
        kg.add_relation(subject, predicate, obj)
        print(f"  ✓ {subject} --[{predicate}]--> {obj}")
    
    print()
    
    # Query relations
    print("Querying knowledge graph:")
    
    print("\n  1. What is Python used for?")
    python_relations = kg.query_relations("Python")
    for s, p, o in python_relations:
        print(f"     → {s} --[{p}]--> {o}")
    
    print("\n  2. What frameworks are written in Python?")
    python_frameworks = kg.query_relations(predicate="written_in", obj="Python")
    for s, p, o in python_frameworks:
        print(f"     → {s}")
    
    print("\n  3. Find path between Python and AI:")
    path = kg.find_path("Python", "AI")
    if path:
        print(f"     → Path found: {' → '.join(path)}")
    else:
        print(f"     → No path found")
    
    print("\n  4. Get neighbors of TensorFlow:")
    neighbors = kg.get_neighbors("TensorFlow")
    print(f"     → Neighbors: {', '.join(neighbors)}")
    
    print()
    
    # Infer transitive relations
    print("Inferring transitive relations:")
    kg.add_relation("Python", "influences", "TensorFlow")
    kg.add_relation("TensorFlow", "influences", "AI_Development")
    
    new_relations = kg.infer_transitive_relations("influences")
    for s, p, o in new_relations:
        print(f"  → Inferred: {s} --[{p}]--> {o}")
    
    print()
    
    # Statistics
    stats = kg.get_statistics()
    print("Knowledge Graph Statistics:")
    for key, value in stats.items():
        print(f"  • {key}: {value}")
    print()


def test_rule_engine():
    """Test rule-based reasoning"""
    print("\n" + "=" * 80)
    print("Rule Engine Demo")
    print("=" * 80 + "\n")
    
    agi = create_agi_system()
    rule_engine = agi.symbolic_engine.rule_engine
    
    # Set up working memory
    print("Setting up working memory:")
    rule_engine.set_fact("temperature", 35)
    rule_engine.set_fact("humidity", 80)
    rule_engine.set_fact("time_of_day", "afternoon")
    print("  ✓ temperature = 35")
    print("  ✓ humidity = 80")
    print("  ✓ time_of_day = 'afternoon'")
    print()
    
    # Add rules
    print("Adding rules:")
    from agi_system.reasoning.symbolic.symbolic_engine import Rule
    
    rule1 = Rule(
        id="hot_weather_rule",
        name="Hot Weather Alert",
        premises=["temperature > 30"],
        conclusion="weather is hot"
    )
    rule_engine.add_rule(rule1)
    print("  ✓ IF temperature > 30 THEN weather is hot")
    
    rule2 = Rule(
        id="humid_weather_rule",
        name="Humid Weather Alert",
        premises=["humidity > 70"],
        conclusion="weather is humid"
    )
    rule_engine.add_rule(rule2)
    print("  ✓ IF humidity > 70 THEN weather is humid")
    print()
    
    # Fire rules
    print("Firing rules:")
    fired = rule_engine.fire_rules()
    print(f"  → Fired rules: {fired}")
    print()
    
    # Check conclusions
    print("Conclusions in working memory:")
    for key in rule_engine.working_memory:
        if key.startswith("conclusion_"):
            print(f"  → {key}: {rule_engine.working_memory[key]}")
    print()


def test_hybrid_reasoning():
    """Test hybrid symbolic-neural reasoning"""
    print("\n" + "=" * 80)
    print("Hybrid Reasoning Demo")
    print("=" * 80 + "\n")
    
    agi = create_agi_system()
    
    # Add both symbolic knowledge and vector knowledge
    print("Adding knowledge (both symbolic and vector):")
    
    # Symbolic
    agi.add_structured_knowledge("Einstein", "discovered", "Relativity")
    agi.add_structured_knowledge("Relativity", "is_a", "Physics_Theory")
    print("  ✓ Symbolic: Einstein → discovered → Relativity")
    
    # Vector
    agi.add_knowledge("Albert Einstein developed the theory of relativity, which revolutionized physics.")
    print("  ✓ Vector: Added document about Einstein and relativity")
    print()
    
    # Query using hybrid approach
    print("Querying with hybrid approach:")
    query = "What did Einstein discover?"
    result = agi.query_knowledge(query, method="hybrid")
    
    print(f"  Query: {query}")
    print(f"\n  Vector Results:")
    if result.get("results", {}).get("vector_results"):
        for doc in result["results"]["vector_results"][:2]:
            print(f"    → {doc['content'][:80]}...")
    
    print(f"\n  Graph Results:")
    if result.get("results", {}).get("graph_results"):
        for item in result["results"]["graph_results"][:2]:
            print(f"    → {item['id']}")
            if item.get("relations"):
                for s, p, o in item["relations"][:2]:
                    print(f"      • {s} --[{p}]--> {o}")
    print()


def main():
    """Run all symbolic reasoning demos"""
    print("\n" + "=" * 80)
    print("AGI System - Symbolic Reasoning Demonstrations")
    print("=" * 80)
    
    test_logic_inference()
    test_knowledge_graph_reasoning()
    test_rule_engine()
    test_hybrid_reasoning()
    
    print("\n" + "=" * 80)
    print("Symbolic Reasoning Demo Completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
