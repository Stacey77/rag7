# rag7 – Agentic AGI Robotics Framework

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-pytest-orange)
![ROS2 Optional](https://img.shields.io/badge/ROS2-optional-lightgrey)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-red)

A production-quality, multi-agent AGI robotics framework that integrates
perception, planning, natural language control, reinforcement learning, and
ROS2 communication into a unified, extensible system.

---

## Features

- **Multi-agent architecture** – PerceptionAgent, PlanningAgent, ControlAgent,
  CommunicationAgent, CoordinationAgent, all built on a common `BaseAgent`
  abstract class with perceive → reason → act loops.
- **Natural language control** – Parse free-text operator commands into
  structured robot actions via intent classification and LLM integration
  (LangChain / GPT-4, with a rule-based fallback).
- **Modular perception** – RGB-D object detection, semantic segmentation,
  IoU multi-object tracking, occupancy-grid SLAM, and sensor fusion.
- **Intelligent planning** – A* path planning, joint-space motion planning
  with IK/FK, LLM-powered task decomposition, and safety-aware decision making.
- **Reinforcement learning** – DQN, PPO, experience replay, and behavioural
  cloning trainers built on PyTorch.
- **ROS2 integration** – Optional rclpy node wrappers for every agent;
  graceful fallback to mock mode when ROS2 is not installed.
- **Simulation** – Gazebo-compatible mock environment for policy development.

---

## Quick Start

```python
from agents.robotics_agi import RoboticsAGI

agi = RoboticsAGI(config_path="config")

# Natural language control
result = agi.execute_command("navigate to the charging station")
print(result["response"])  # "Understood. I will navigate to the specified location."

# Task API
task = agi.create_task("grasp", target_object="red_cube")
result = agi.execute_task(task)
print(result)  # {"success": True, "details": "Grasped 'red_cube'"}

# System status
print(agi.get_status()["system"])  # "online"
```

---

## Installation

```bash
git clone https://github.com/your-org/rag7.git
cd rag7
pip install -e .                   # core only
pip install -e ".[llm,dev]"        # + LangChain + testing tools
```

See [docs/installation.md](docs/installation.md) for full instructions
including ROS2 setup and Docker.

---

## Project Structure

```
rag7/
├── agents/                  # Core agent classes
│   ├── base_agent.py
│   ├── perception_agent.py
│   ├── planning_agent.py
│   ├── control_agent.py
│   ├── communication_agent.py
│   ├── coordination_agent.py
│   └── robotics_agi.py      # Top-level orchestrator
├── perception/              # Sensor processing
│   ├── vision/              # Detection, segmentation, tracking
│   ├── slam/                # Mapping & localisation
│   └── sensor_fusion.py
├── planning/                # Task, path, motion planning
├── nlp/                     # NLP pipeline
├── learning/                # RL & imitation learning
│   ├── rl/                  # DQN, PPO, ReplayBuffer
│   └── imitation/           # Behavioural cloning
├── ros2_interface/          # ROS2 node wrappers
│   ├── ros2_nodes/
│   └── launch/
├── simulation/              # Gazebo environment
├── config/                  # YAML configuration files
├── examples/                # Runnable example scripts
├── tests/                   # pytest test suite
├── docs/                    # Documentation
├── Dockerfile
├── requirements.txt
└── setup.py
```

---

## Architecture Overview

The system follows a hierarchical multi-agent architecture:

```
Operator NL input
       │
       ▼
CommunicationAgent ──► parse intent & entities
       │
       ▼
PlanningAgent ──► decompose goal into steps
       │
       ▼
ControlAgent ──► execute steps (navigate / grasp / stop)
       │
       ▼
ROS2Interface (optional) ──► robot hardware
```

See [docs/architecture.md](docs/architecture.md) for the full diagram.

---

## Usage Examples

### Navigation

```python
agi = RoboticsAGI(config_path="config")
agi.execute_command("go to the storage room")
```

### Object Manipulation

```python
agi.execute_command("pick up the blue box and place it on shelf B")
```

### Multi-Robot Coordination

```python
from agents.control_agent import ControlAgent

robot_a = ControlAgent(config={})
robot_b = ControlAgent(config={})
task = agi.create_task("navigate", location={"x": 5.0, "y": 5.0})
agi.coordinate_robots([robot_a, robot_b], task)
```

### Reinforcement Learning

```python
from learning.rl.dqn_agent import DQNAgent
from learning.rl.replay_buffer import ReplayBuffer

agent = DQNAgent(state_dim=8, action_dim=4)
buffer = ReplayBuffer(capacity=10000)
buffer.push(state, action, reward, next_state, done)
batch = buffer.sample(32)
loss = agent.update(batch)
```

---

## Configuration

All runtime parameters live in `config/`:

| File | Description |
|------|-------------|
| `robot_config.yaml` | Sensor topics, dimensions, safety thresholds |
| `agent_config.yaml` | Per-agent update rates, tolerances, memory |
| `llm_config.yaml` | LLM provider, model, temperature, API key env var |

---

## Running Tests

```bash
python -m pytest tests/ -v
python -m pytest tests/ -v --cov=. --cov-report=html
```

---

## Contributing

1. Fork the repository and create a feature branch.
2. Follow PEP 8 and add docstrings to all public classes and functions.
3. Add or update tests for any changed behaviour.
4. Open a pull request with a clear description.

---

## License

MIT License – see [LICENSE](LICENSE) for details.

© 2024 Stacey Williams