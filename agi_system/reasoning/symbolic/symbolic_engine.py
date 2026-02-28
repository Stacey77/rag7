"""
AGI System - Symbolic Reasoning Engine
Implements logic inference, knowledge graphs, and rule-based reasoning
"""
from typing import List, Dict, Any, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import sympy
from sympy.logic.boolalg import And, Or, Not, Implies, Equivalent
from sympy import symbols
import networkx as nx
from loguru import logger


class LogicType(Enum):
    """Types of logic systems"""
    PROPOSITIONAL = "propositional"
    FIRST_ORDER = "first_order"
    MODAL = "modal"


@dataclass
class Fact:
    """Represents a fact in the knowledge base"""
    id: str
    statement: str
    confidence: float = 1.0
    source: str = "user"
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Rule:
    """Represents a logical rule"""
    id: str
    name: str
    premises: List[str]  # List of fact IDs or conditions
    conclusion: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class LogicInferenceSystem:
    """Handles logical inference and deduction"""
    
    def __init__(self, logic_type: LogicType = LogicType.PROPOSITIONAL):
        self.logic_type = logic_type
        self.facts: Dict[str, Fact] = {}
        self.rules: Dict[str, Rule] = {}
        self.symbols_cache: Dict[str, Any] = {}
        logger.info(f"Logic Inference System initialized with {logic_type.value}")
    
    def add_fact(self, statement: str, confidence: float = 1.0, source: str = "user") -> Fact:
        """Add a fact to the knowledge base"""
        fact_id = f"fact_{len(self.facts)}"
        fact = Fact(
            id=fact_id,
            statement=statement,
            confidence=confidence,
            source=source
        )
        self.facts[fact_id] = fact
        logger.debug(f"Added fact: {fact_id} - {statement}")
        return fact
    
    def add_rule(self, name: str, premises: List[str], conclusion: str, confidence: float = 1.0) -> Rule:
        """Add a logical rule"""
        rule_id = f"rule_{len(self.rules)}"
        rule = Rule(
            id=rule_id,
            name=name,
            premises=premises,
            conclusion=conclusion,
            confidence=confidence
        )
        self.rules[rule_id] = rule
        logger.debug(f"Added rule: {rule_id} - {name}")
        return rule
    
    def get_symbol(self, name: str):
        """Get or create a symbolic variable"""
        if name not in self.symbols_cache:
            self.symbols_cache[name] = symbols(name)
        return self.symbols_cache[name]
    
    def forward_chaining(self) -> List[Fact]:
        """Perform forward chaining inference"""
        new_facts = []
        
        for rule_id, rule in self.rules.items():
            # Check if all premises are satisfied
            premises_satisfied = all(
                any(fact.statement == premise for fact in self.facts.values())
                for premise in rule.premises
            )
            
            if premises_satisfied:
                # Check if conclusion already exists
                conclusion_exists = any(
                    fact.statement == rule.conclusion
                    for fact in self.facts.values()
                )
                
                if not conclusion_exists:
                    # Derive new fact
                    confidence = rule.confidence * min(
                        self.facts[fid].confidence
                        for fid in self.facts
                        if self.facts[fid].statement in rule.premises
                    )
                    
                    new_fact = self.add_fact(
                        rule.conclusion,
                        confidence=confidence,
                        source=f"inferred_from_{rule_id}"
                    )
                    new_facts.append(new_fact)
                    logger.info(f"Inferred new fact: {new_fact.statement}")
        
        return new_facts
    
    def backward_chaining(self, goal: str) -> bool:
        """Perform backward chaining to prove a goal"""
        # Check if goal is already a fact
        if any(fact.statement == goal for fact in self.facts.values()):
            logger.info(f"Goal '{goal}' is already a fact")
            return True
        
        # Find rules that can prove the goal
        for rule in self.rules.values():
            if rule.conclusion == goal:
                # Try to prove all premises
                if all(self.backward_chaining(premise) for premise in rule.premises):
                    logger.info(f"Goal '{goal}' proven via rule {rule.id}")
                    return True
        
        logger.info(f"Goal '{goal}' cannot be proven")
        return False
    
    def evaluate_propositional(self, expression: str, assignments: Dict[str, bool]) -> bool:
        """Evaluate a propositional logic expression"""
        try:
            # Parse the expression
            expr = sympy.sympify(expression)
            
            # Substitute assignments
            for var, value in assignments.items():
                sym = self.get_symbol(var)
                expr = expr.subs(sym, value)
            
            # Evaluate
            result = bool(expr)
            logger.debug(f"Evaluated '{expression}' with {assignments} = {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating expression: {e}")
            return False
    
    def derive_implications(self, fact_a: str, fact_b: str) -> Optional[str]:
        """Derive logical implications between facts"""
        # Create symbolic representations
        A = self.get_symbol('A')
        B = self.get_symbol('B')
        
        # Check various logical relationships
        implications = []
        
        # A implies B
        if self.backward_chaining(fact_a) and self.backward_chaining(fact_b):
            implications.append(f"{fact_a} → {fact_b}")
        
        return " AND ".join(implications) if implications else None


class KnowledgeGraphReasoner:
    """Manages and reasons over knowledge graphs"""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.entity_types: Dict[str, str] = {}
        self.relation_types: Set[str] = set()
        logger.info("Knowledge Graph Reasoner initialized")
    
    def add_entity(self, entity_id: str, entity_type: str, properties: Optional[Dict[str, Any]] = None):
        """Add an entity to the knowledge graph"""
        self.graph.add_node(entity_id, type=entity_type, **(properties or {}))
        self.entity_types[entity_id] = entity_type
        logger.debug(f"Added entity: {entity_id} (type: {entity_type})")
    
    def add_relation(self, source: str, relation: str, target: str, properties: Optional[Dict[str, Any]] = None):
        """Add a relation between entities"""
        self.graph.add_edge(source, target, relation=relation, **(properties or {}))
        self.relation_types.add(relation)
        logger.debug(f"Added relation: {source} --[{relation}]--> {target}")
    
    def query_relations(self, entity_id: str, relation_type: Optional[str] = None) -> List[Tuple[str, str, str]]:
        """Query relations for an entity"""
        results = []
        
        # Outgoing relations
        for target in self.graph.successors(entity_id):
            for key, edge_data in self.graph[entity_id][target].items():
                rel = edge_data.get('relation')
                if relation_type is None or rel == relation_type:
                    results.append((entity_id, rel, target))
        
        # Incoming relations
        for source in self.graph.predecessors(entity_id):
            for key, edge_data in self.graph[source][entity_id].items():
                rel = edge_data.get('relation')
                if relation_type is None or rel == relation_type:
                    results.append((source, rel, entity_id))
        
        return results
    
    def find_path(self, start: str, end: str, max_depth: int = 5) -> Optional[List[str]]:
        """Find a path between two entities"""
        try:
            path = nx.shortest_path(self.graph, start, end)
            if len(path) <= max_depth + 1:
                logger.debug(f"Found path from {start} to {end}: {path}")
                return path
        except nx.NetworkXNoPath:
            logger.debug(f"No path found from {start} to {end}")
        return None
    
    def get_neighbors(self, entity_id: str, depth: int = 1) -> Set[str]:
        """Get all neighbors within a certain depth"""
        neighbors = set()
        current_level = {entity_id}
        
        for _ in range(depth):
            next_level = set()
            for node in current_level:
                next_level.update(self.graph.successors(node))
                next_level.update(self.graph.predecessors(node))
            neighbors.update(next_level)
            current_level = next_level
        
        neighbors.discard(entity_id)
        return neighbors
    
    def infer_transitive_relations(self, relation_type: str) -> List[Tuple[str, str, str]]:
        """Infer transitive relations (if A->B and B->C, then A->C)"""
        new_relations = []
        
        edges = [(u, v) for u, v, d in self.graph.edges(data=True) if d.get('relation') == relation_type]
        
        for u, v in edges:
            for v2, w in edges:
                if v == v2 and u != w:
                    # Check if relation doesn't already exist
                    if not self.graph.has_edge(u, w):
                        new_relations.append((u, relation_type, w))
                        logger.debug(f"Inferred transitive: {u} --[{relation_type}]--> {w}")
        
        return new_relations
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        return {
            "num_entities": self.graph.number_of_nodes(),
            "num_relations": self.graph.number_of_edges(),
            "entity_types": len(set(self.entity_types.values())),
            "relation_types": len(self.relation_types),
            "avg_degree": sum(dict(self.graph.degree()).values()) / max(self.graph.number_of_nodes(), 1)
        }


class RuleEngine:
    """Rule-based reasoning engine"""
    
    def __init__(self):
        self.rules: List[Rule] = []
        self.working_memory: Dict[str, Any] = {}
        logger.info("Rule Engine initialized")
    
    def add_rule(self, rule: Rule):
        """Add a rule to the engine"""
        self.rules.append(rule)
        logger.debug(f"Added rule: {rule.name}")
    
    def set_fact(self, key: str, value: Any):
        """Set a fact in working memory"""
        self.working_memory[key] = value
        logger.debug(f"Set fact: {key} = {value}")
    
    def get_fact(self, key: str) -> Optional[Any]:
        """Get a fact from working memory"""
        return self.working_memory.get(key)
    
    def evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition using working memory"""
        try:
            # Simple evaluation using working memory as namespace
            return eval(condition, {"__builtins__": {}}, self.working_memory)
        except Exception as e:
            logger.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    def fire_rules(self) -> List[str]:
        """Fire all applicable rules"""
        fired_rules = []
        
        for rule in self.rules:
            # Check if all premises are satisfied
            if all(self.evaluate_condition(premise) for premise in rule.premises):
                # Execute conclusion
                fired_rules.append(rule.id)
                logger.info(f"Fired rule: {rule.name}")
                
                # Update working memory with conclusion
                self.set_fact(f"rule_{rule.id}_fired", True)
                self.set_fact(f"conclusion_{rule.id}", rule.conclusion)
        
        return fired_rules


class SymbolicReasoningEngine:
    """Main symbolic reasoning engine integrating all components"""
    
    def __init__(self):
        self.logic_system = LogicInferenceSystem()
        self.knowledge_graph = KnowledgeGraphReasoner()
        self.rule_engine = RuleEngine()
        logger.info("Symbolic Reasoning Engine initialized")
    
    def add_knowledge(self, statement: str, confidence: float = 1.0) -> Fact:
        """Add knowledge to the system"""
        return self.logic_system.add_fact(statement, confidence)
    
    def add_relation(self, subject: str, predicate: str, object: str):
        """Add a relation to the knowledge graph"""
        self.knowledge_graph.add_relation(subject, predicate, object)
    
    def reason(self, query: str, method: str = "forward_chaining") -> Dict[str, Any]:
        """Perform reasoning on a query"""
        logger.info(f"Reasoning about: {query} using {method}")
        
        result = {
            "query": query,
            "method": method,
            "result": None,
            "explanation": []
        }
        
        if method == "forward_chaining":
            new_facts = self.logic_system.forward_chaining()
            result["result"] = new_facts
            result["explanation"] = [f.statement for f in new_facts]
            
        elif method == "backward_chaining":
            proven = self.logic_system.backward_chaining(query)
            result["result"] = proven
            result["explanation"] = [f"Query {'proven' if proven else 'not proven'}"]
            
        elif method == "graph_query":
            # Parse query for entity
            entity = query.split()[-1] if query.split() else query
            relations = self.knowledge_graph.query_relations(entity)
            result["result"] = relations
            result["explanation"] = [f"{s} --[{r}]--> {t}" for s, r, t in relations]
        
        return result
    
    def explain_reasoning(self, conclusion: str) -> List[str]:
        """Explain how a conclusion was reached"""
        explanation = []
        
        # Find facts that support the conclusion
        for fact in self.logic_system.facts.values():
            if conclusion in fact.statement:
                explanation.append(f"Fact: {fact.statement} (confidence: {fact.confidence})")
        
        # Find rules that lead to the conclusion
        for rule in self.logic_system.rules.values():
            if rule.conclusion == conclusion:
                explanation.append(f"Rule: {rule.name}")
                explanation.extend([f"  Premise: {p}" for p in rule.premises])
        
        return explanation
    
    def get_system_state(self) -> Dict[str, Any]:
        """Get current state of the reasoning system"""
        return {
            "num_facts": len(self.logic_system.facts),
            "num_rules": len(self.logic_system.rules),
            "knowledge_graph": self.knowledge_graph.get_statistics(),
            "rule_engine_facts": len(self.rule_engine.working_memory)
        }
