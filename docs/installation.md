# Installation Guide

## Prerequisites

- Python 3.10 or higher
- pip 23+
- (Optional) CUDA 11.8+ for GPU inference
- (Optional) ROS2 Humble or later for hardware integration

---

## Quick Install

```bash
git clone https://github.com/your-org/rag7.git
cd rag7
pip install -e .
```

For full LLM and ML support:

```bash
pip install -e ".[llm]"
```

For development (includes testing tools):

```bash
pip install -e ".[llm,dev]"
```

---

## Installing All Requirements

```bash
pip install -r requirements.txt
```

> **Note:** `rclpy`, `geometry_msgs`, `sensor_msgs`, `nav_msgs`, and
> `action_msgs` are ROS2 packages installed via the ROS2 toolchain, not pip.
> All other packages install normally.

---

## ROS2 Setup (Optional)

1. Install ROS2 Humble following the [official guide](https://docs.ros.org/en/humble/Installation.html).
2. Source the ROS2 environment:

   ```bash
   source /opt/ros/humble/setup.bash
   ```

3. Build the rag7 ROS2 package:

   ```bash
   colcon build --packages-select rag7_agi
   source install/setup.bash
   ```

---

## OpenAI API Key (Optional)

Set the environment variable to enable LLM-based planning and NLP:

```bash
export OPENAI_API_KEY="sk-..."
```

Without a key the system falls back to rule-based planning and parsing.

---

## Docker

```bash
docker build -t rag7-agi .
docker run --rm rag7-agi
```

---

## Verifying the Installation

```bash
cd rag7
python -m pytest tests/ -v
```

All tests should pass without ROS2 or a GPU.
