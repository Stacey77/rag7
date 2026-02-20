"""
Conflict Resolution Demo

Demonstrates the Resolver Agent's conflict detection and resolution
capabilities with multiple resolution strategies.
"""

import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from agents.base_agent import AgentState, AgentStatus
from agents.resolver_agent import ResolverAgent
from resolver.conflict_resolution import ConflictDetector, ConflictResolver, ResolutionStrategy


def demo_perception_planning_conflict():
    print("\n=== Perception vs Planning Conflict ===")
    detector = ConflictDetector()
    state_p = AgentState(name="perception")
    state_p.metadata["detected_objects"] = ["chair", "table", "robot"]
    state_pl = AgentState(name="planning")
    state_pl.metadata["known_objects"] = ["chair"]

    conflicts = detector.detect_perception_planning_conflict(
        {"perception": state_p, "planning": state_pl}
    )
    print(f"Detected {len(conflicts)} conflict(s):")
    for c in conflicts:
        print(f"  Type: {c['type']}, Severity: {c['severity']}")
        print(f"  Missing objects: {c['details']['disagreements']}")
    return conflicts


def demo_resource_conflict():
    print("\n=== Resource Conflict (Multiple Agents Need GPU) ===")
    detector = ConflictDetector()
    states = {}
    for name in ["perception", "planning", "control"]:
        state = AgentState(name=name)
        state.metadata["requested_resources"] = ["GPU"]
        states[name] = state

    conflicts = detector.detect_resource_conflict(states)
    print(f"Detected {len(conflicts)} resource conflict(s):")
    for c in conflicts:
        print(f"  Resource: {c['details']['resource']}")
        print(f"  Requesters: {c['details']['requesting_agents']}")
    return conflicts


def demo_resolution_strategies():
    print("\n=== Resolution Strategies Demo ===")
    resolver = ConflictResolver()
    conflict = {
        "type": "control",
        "agents": ["planning", "control", "coordination"],
        "description": "Multiple agents requesting robot control",
    }

    strategies = [
        ResolutionStrategy.PRIORITY_BASED,
        ResolutionStrategy.VOTING,
        ResolutionStrategy.EXPERTISE,
    ]

    for strategy in strategies:
        result = resolver.resolve(conflict, strategy)
        print(f"  {strategy.value:20s} → winner: {result['winning_agent']}")


def demo_full_resolver():
    print("\n=== Full Resolver Agent Demo ===")
    from agents.base_agent import BaseAgent

    class _DummyAgent(BaseAgent):
        def __init__(self, name, priority=0):
            super().__init__(name, priority)
        def on_start(self): pass
        def on_stop(self): pass
        def execute(self, task): return {}

    resolver = ResolverAgent()
    agents = [
        _DummyAgent("perception", 5),
        _DummyAgent("planning", 4),
        _DummyAgent("control", 3),
        _DummyAgent("communication", 2),
        _DummyAgent("coordination", 1),
    ]
    resolver.integrate_with_agents(agents)
    resolver.start()

    # Simulate a control conflict
    conflict = {
        "type": "control",
        "agents": ["planning", "control"],
        "description": "Path disagreement",
    }
    print(f"\nResolving conflict: {conflict['description']}")
    resolution = resolver.resolve_conflict(conflict)
    print(f"  Resolution: {resolution['winning_agent']} granted control "
          f"({resolution['strategy']})")

    # Check system health
    health = resolver.generate_health_report()
    print(f"\nSystem health: {health['overall_status']}")

    resolver.stop()
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    demo_perception_planning_conflict()
    demo_resource_conflict()
    demo_resolution_strategies()
    demo_full_resolver()
