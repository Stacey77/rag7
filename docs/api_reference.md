# API Reference

## agents

### `BaseAgent`

Abstract base class for all rag7 agents.

```python
class BaseAgent(ABC):
    def __init__(self, name: str, config: dict, logger=None)
    def update_state(self, key: str, value: Any) -> None
    def add_to_memory(self, item: Any) -> None
    def get_memory(self, n: int = 10) -> list
    def clear_memory(self) -> None
    def register_tool(self, tool: Any) -> None
    def get_tools(self) -> list

    # Abstract
    def perceive(self, observation: Any) -> Any
    def reason(self, context: Any) -> Any
    def act(self, action: Any) -> Any
```

### `PerceptionAgent`

```python
class PerceptionAgent(BaseAgent):
    def __init__(self, config: dict, device: str = "cpu")
    def perceive(self, observation: dict) -> dict
    # observation keys: image (ndarray), lidar (array), imu (dict)
    # returns: detections, position, orientation, nearest_obstacle
    def reason(self, context: Any) -> dict
    def act(self, action: dict) -> dict
```

### `PlanningAgent`

```python
class PlanningAgent(BaseAgent):
    def __init__(self, config: dict, llm_config: dict = None)
    def perceive(self, observation: dict) -> dict
    def reason(self, context: Any) -> dict  # returns plan dict
    def act(self, action: dict) -> dict
    def create_plan(self, goal: str) -> list[dict]
```

### `ControlAgent`

```python
class ControlAgent(BaseAgent):
    def __init__(self, config: dict, ros2_enabled: bool = False)
    def perceive(self, observation: dict) -> dict
    def reason(self, context: Any) -> dict
    def act(self, action: dict) -> dict  # type: navigate | grasp | stop
    def navigate_to(self, x: float, y: float, theta: float) -> bool
    def execute_grasp(self, object_id: str) -> bool
    def emergency_stop(self) -> None
```

### `CommunicationAgent`

```python
class CommunicationAgent(BaseAgent):
    def __init__(self, config: dict, llm_config: dict = None)
    def perceive(self, observation: dict) -> dict
    def reason(self, context: Any) -> dict
    def act(self, action: dict) -> dict  # type: send | receive
    def parse_command(self, text: str) -> dict
    def generate_response(self, context: dict) -> str
    def classify_intent(self, text: str) -> str
```

### `CoordinationAgent`

```python
class CoordinationAgent(BaseAgent):
    def __init__(self, config: dict)
    def register_agent(self, agent: BaseAgent) -> None
    def allocate_task(self, task: dict, agents: list = None) -> BaseAgent
    def coordinate(self, task_list: list) -> dict
    def get_agent_status(self) -> dict
```

### `RoboticsAGI`

```python
class RoboticsAGI:
    def __init__(
        self,
        ros2_interface=None,
        llm_provider: str = "openai",
        enable_learning: bool = False,
        config_path: str = "config",
    )
    def execute_command(self, text: str) -> dict
    def create_task(self, task_type: str, **kwargs) -> dict
    def execute_task(self, task: dict) -> dict
    def coordinate_robots(self, robots: list, task: dict) -> dict
    def get_status(self) -> dict
```

---

## perception

### `ObjectDetector`

```python
class ObjectDetector:
    def __init__(self, model_path=None, device="cpu", confidence_threshold=0.5)
    def detect(self, image: ndarray) -> list[Detection]
    def load_model(self, path: str) -> bool
```

### `Segmenter`

```python
class Segmenter:
    def __init__(self, model_path=None, device="cpu")
    def segment(self, image: ndarray) -> dict  # masks, labels, scores
```

### `ObjectTracker`

```python
class ObjectTracker:
    def __init__(self, max_age=30, min_hits=3)
    def update(self, detections: list) -> list[dict]  # id, bbox, label
```

### `SLAMMapper`

```python
class SLAMMapper:
    def __init__(self, map_resolution=0.05, map_size=100)
    def update(self, lidar_scan, pose: dict) -> None
    def get_map(self) -> ndarray
    def localize(self, scan) -> dict  # x, y, theta, confidence
```

### `SensorFusion`

```python
class SensorFusion:
    def fuse(self, camera_data, lidar_data, imu_data) -> dict
```

---

## planning

### `TaskPlanner`

```python
class TaskPlanner:
    def __init__(self, llm_config: dict = None)
    def plan(self, goal: str, context: dict = None) -> list[dict]
    def decompose(self, task: str) -> list[dict]
    def replan(self, failed_step: dict, context: dict = None) -> list[dict]
```

### `PathPlanner`

```python
class PathPlanner:
    def __init__(self, grid_resolution=0.1)
    def plan(self, start: tuple, goal: tuple, obstacles: list = None) -> list[tuple]
```

### `MotionPlanner`

```python
class MotionPlanner:
    def __init__(self, dof=6)
    def plan_trajectory(self, start_config, goal_config, duration=1.0) -> dict
    def compute_ik(self, pose: dict) -> list[float]
    def compute_fk(self, joint_angles: list) -> dict
```

### `DecisionMaker`

```python
class DecisionMaker:
    def __init__(self, config: dict = None)
    def decide(self, state: dict, options: list) -> Any
    def evaluate(self, state: dict, action: Any) -> float
```

---

## nlp

### `CommandParser`

```python
class CommandParser:
    def __init__(self, llm_config: dict = None)
    def parse(self, text: str) -> dict  # intent, action, target_object, location, confidence
    def extract_entities(self, text: str) -> dict
```

### `IntentClassifier`

```python
class IntentClassifier:
    INTENTS = ["navigate", "grasp", "place", "inspect", "stop", "query", "unknown"]
    def classify(self, text: str) -> str
    def get_confidence(self, text: str, intent: str) -> float
```

### `DialogManager`

```python
class DialogManager:
    def __init__(self, max_history=10)
    def process(self, user_input: str, robot_state: dict = None) -> str
    def add_turn(self, role: str, content: str) -> None
    def get_history(self) -> list[dict]
    def clear_history(self) -> None
```

---

## learning

### `DQNAgent`

```python
class DQNAgent:
    def __init__(self, state_dim, action_dim, lr=1e-3, gamma=0.99, ...)
    def select_action(self, state) -> int
    def update(self, batch: dict) -> float
    def save(self, path: str) -> None
    def load(self, path: str) -> None
```

### `PPOAgent`

```python
class PPOAgent:
    def __init__(self, state_dim, action_dim, lr=3e-4, gamma=0.99, ...)
    def select_action(self, state) -> tuple[int, tensor]
    def update(self, memory: dict) -> float
    def save(self, path: str) -> None
    def load(self, path: str) -> None
```

### `ReplayBuffer`

```python
class ReplayBuffer:
    def __init__(self, capacity=10000)
    def push(self, state, action, reward, next_state, done) -> None
    def sample(self, batch_size: int) -> dict
    def __len__(self) -> int
```

### `BCTrainer`

```python
class BCTrainer:
    def __init__(self, state_dim, action_dim, lr=1e-3)
    def add_demonstration(self, state, action) -> None
    def train(self, epochs=10, batch_size=32) -> list[float]
    def predict(self, state) -> ndarray
    def save(self, path: str) -> None
    def load(self, path: str) -> None
```

---

## simulation

### `GazeboEnv`

```python
class GazeboEnv:
    def __init__(self, world_name="empty", robot_name="robot", headless=True)
    def reset(self) -> dict
    def step(self, action: dict) -> tuple[dict, float, bool, dict]
    def render(self) -> ndarray | None
    def close(self) -> None
```
