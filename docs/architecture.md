# rag7 AGI Robotics Framework – Architecture

## Overview

The rag7 framework is a modular, multi-agent AGI robotics platform built
around the **perceive → reason → act** loop.  Each subsystem is an
independent Python package that can be used standalone or composed into
the full `RoboticsAGI` orchestrator.

---

## System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         RoboticsAGI                                  │
│  ┌────────────┐ ┌──────────────┐ ┌─────────────┐ ┌───────────────┐  │
│  │ Perception │ │   Planning   │ │   Control   │ │ Communication │  │
│  │   Agent    │ │    Agent     │ │    Agent    │ │    Agent      │  │
│  └─────┬──────┘ └──────┬───────┘ └──────┬──────┘ └───────┬───────┘  │
│        │               │                │                │           │
│  ┌─────▼───────────────▼────────────────▼────────────────▼───────┐  │
│  │                   CoordinationAgent                            │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
        │               │                │                │
   ┌────▼────┐    ┌──────▼──────┐  ┌─────▼─────┐   ┌─────▼─────┐
   │Perception│   │  Planning   │  │   NLP     │   │ Learning  │
   │ Module  │   │  Module     │  │  Module   │   │  Module   │
   └─────────┘   └─────────────┘  └───────────┘   └───────────┘
        │               │
   ┌────▼────┐    ┌──────▼──────┐
   │  SLAM   │   │  Path/Motion │
   │ Mapping │   │  Planner     │
   └─────────┘   └─────────────┘
        │
   ┌────▼────────────┐
   │  ROS2 Interface │
   │  (optional)     │
   └─────────────────┘
```

---

## Agent Layer

### BaseAgent
Abstract class that all agents inherit from.  Enforces the
perceive/reason/act interface and provides shared memory and tool
registration.

### PerceptionAgent
Processes raw sensor data (RGB-D camera, 2-D LiDAR, IMU) into
structured scene representations.

### PlanningAgent
Decomposes high-level goals into ordered action sequences.  Uses
LangChain + GPT-4 when available; falls back to rule-based planning.

### ControlAgent
Translates planned actions into robot actuator commands.  Publishes
navigation goals and arm trajectories to ROS2 topics when available.

### CommunicationAgent
Handles natural language I/O.  Parses operator commands and generates
contextual responses using the NLP module.

### CoordinationAgent
Manages multi-robot task allocation using capability-based matching.

---

## Perception Module

| Component | Description |
|-----------|-------------|
| `ObjectDetector` | PyTorch-based 2-D bounding-box detector |
| `Segmenter` | Semantic segmentation |
| `ObjectTracker` | IoU-based multi-object tracker |
| `SLAMMapper` | Occupancy-grid SLAM with ray-casting |
| `SensorFusion` | Complementary-filter fusion of camera/LiDAR/IMU |

---

## Planning Module

| Component | Description |
|-----------|-------------|
| `TaskPlanner` | LLM / rule-based goal decomposition |
| `PathPlanner` | A* grid-based path planning |
| `MotionPlanner` | Joint-space trajectory interpolation + simplified IK/FK |
| `DecisionMaker` | Rule-based action selection with safety gating |

---

## NLP Module

| Component | Description |
|-----------|-------------|
| `CommandParser` | Maps utterances to structured command dicts |
| `IntentClassifier` | Weighted keyword intent classification |
| `DialogManager` | Multi-turn conversation management |

---

## Learning Module

| Component | Description |
|-----------|-------------|
| `DQNAgent` | Deep Q-Network with experience replay |
| `PPOAgent` | Proximal Policy Optimisation actor-critic |
| `ReplayBuffer` | Circular experience replay buffer |
| `BCTrainer` | Behavioural cloning from expert demos |

---

## ROS2 Interface

Optional bridge layer that wraps each agent in a `rclpy` node.
When `rclpy` is not installed all nodes degrade to mock mode.

---

## Data Flow

```
Operator text ──► CommunicationAgent ──► CommandParser ──► intent/action
                                                              │
                                                              ▼
Sensor data ──► PerceptionAgent ──► SensorFusion ──► scene state
                                                              │
                                                              ▼
                                        PlanningAgent ──► task plan
                                                              │
                                                              ▼
                                        ControlAgent ──► actuator cmds
                                                              │
                                                              ▼
                                        ROS2Interface ──► robot hardware
```
