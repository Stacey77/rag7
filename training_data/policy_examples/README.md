# Policy Examples Training Data

Example policies and outcomes for reinforcement learning policy optimization.

## Policy Types

### Infrastructure Policies
- Auto-scaling policies with CPU/memory thresholds
- Load balancing strategies (round-robin, least-connections, weighted)
- Resource allocation decisions under capacity constraints

### Deployment Policies
- Canary deployment traffic shifting strategies
- Rollback trigger conditions and thresholds
- Blue-green promotion criteria

### Cost Optimization Policies
- Spot instance bidding strategies
- Reserved capacity allocation rules
- Storage tiering decision trees

### Security Policies
- Access control rule templates
- Network policy configurations
- Secret rotation schedules

## Data Format

```json
{
  "policy_id": "scale-policy-001",
  "policy_type": "auto_scaling",
  "state": {
    "cpu_utilization": 0.85,
    "memory_utilization": 0.72,
    "request_rate": 1500,
    "current_replicas": 3
  },
  "action": {
    "scale_to_replicas": 5,
    "reasoning": "CPU above 80% threshold with growing request rate"
  },
  "outcome": {
    "reward": 0.92,
    "latency_improvement_ms": 45,
    "cost_impact_usd": 2.50
  }
}
```

## Quality Criteria

- Include state-action-reward triples for RL training
- Cover edge cases (scale-down during traffic spikes, etc.)
- Label sub-optimal decisions for contrastive learning
- Minimum 500 examples per policy type
