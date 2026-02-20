# Conflict Resolution Guide

## Overview

The conflict resolution system detects and resolves disagreements between agents in the Agentic AGI robotics system.

## Conflict Types

| Type | Description |
|------|-------------|
| `perception_planning` | Perception sees objects that Planning doesn't know about (or vice versa) |
| `control` | Multiple agents simultaneously request robot control |
| `task` | The same task is assigned to multiple agents |
| `resource` | Multiple agents compete for the same resource (GPU, camera, etc.) |

## Resolution Strategies

### 1. Priority-Based (Default)
The agent with the highest priority wins. Uses the global priority table.

```python
from resolver.conflict_resolution import ConflictResolver, ResolutionStrategy

resolver = ConflictResolver()
result = resolver.resolve(conflict, ResolutionStrategy.PRIORITY_BASED)
```

### 2. Voting
Each agent casts a weighted vote (based on priority). The agent with the most votes wins.

### 3. Expertise
The most domain-relevant agent is selected as the decision-maker.

| Conflict Type       | Expert Agent  |
|---------------------|---------------|
| perception_planning | perception    |
| control             | control       |
| task                | coordination  |
| resource            | resolver      |

### 4. Cost-Based
The option with the lowest numerical cost (from `conflict.details.options`) is selected.

```python
conflict = {
    "type": "resource",
    "agents": ["planning", "control"],
    "details": {
        "options": [
            {"id": "opt_a", "agent": "planning", "cost": 10},
            {"id": "opt_b", "agent": "control", "cost": 5},
        ]
    },
}
result = resolver.resolve(conflict, ResolutionStrategy.COST_BASED)
# → control wins (cost 5)
```

### 5. ML-Based
A trained PyTorch model predicts the best resolution. Falls back to priority-based if PyTorch is unavailable.

## Conflict Prediction

The `ConflictPredictor` class provides rule-based and ML-based prediction:

```python
from resolver.conflict_resolution import ConflictPredictor

predictor = ConflictPredictor()
predictions = predictor.predict(agent_states)
actions = predictor.suggest_preventive_actions(agent_states)
```

## Conflict Data Format

```python
conflict = {
    "type": "control",               # ConflictType value
    "agents": ["planning", "control"], # involved agent names
    "description": "...",            # human-readable description
    "severity": 2,                   # 1-5 (1=minor, 5=critical)
    "details": { ... },              # type-specific details
}
```

## Resolution Result Format

```python
resolution = {
    "strategy": "priority_based",
    "winning_agent": "planning",
    "action": "grant_control_to_planning",
    "rationale": "Agent 'planning' has highest priority (4)",
    "success": True,
    "timestamp": 1234567890.0,
}
```
