"""Monitor user workload and predict burnout risk."""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from statistics import mean, stdev
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

COMPLEXITY_SCORES = {"low": 1, "medium": 3, "high": 5, "critical": 8}
TASK_WINDOW_HOURS = 8   # rolling window for workload computation


class WorkloadLevel(Enum):
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    OVERLOADED = "overloaded"


@dataclass
class WorkloadMetrics:
    """Computed workload statistics for a user."""
    user_id: str
    task_count: int
    total_complexity: float
    avg_complexity: float
    peak_complexity: float
    tasks_per_hour: float
    computed_at: datetime = field(default_factory=datetime.utcnow)


class WorkloadAnalyzer:
    """Analyse user task load and flag overload risk."""

    def __init__(self) -> None:
        # user_id -> list of (task_type, complexity_str, timestamp)
        self._tasks: Dict[str, List[Tuple[str, str, datetime]]] = defaultdict(list)
        logger.info("WorkloadAnalyzer initialised.")

    def record_task(self, user_id: str, task_type: str, complexity: str = "medium") -> None:
        """Record a new task for *user_id*."""
        complexity = complexity.lower() if complexity.lower() in COMPLEXITY_SCORES else "medium"
        self._tasks[user_id].append((task_type, complexity, datetime.utcnow()))
        logger.debug("Task recorded: user=%s type=%s complexity=%s", user_id, task_type, complexity)

    def _recent_tasks(self, user_id: str) -> List[Tuple[str, str, datetime]]:
        cutoff = datetime.utcnow() - timedelta(hours=TASK_WINDOW_HOURS)
        return [(t, c, ts) for t, c, ts in self._tasks.get(user_id, []) if ts >= cutoff]

    def compute_workload(self, user_id: str) -> WorkloadMetrics:
        """Compute workload metrics over the last *TASK_WINDOW_HOURS* hours."""
        recent = self._recent_tasks(user_id)
        if not recent:
            return WorkloadMetrics(user_id=user_id, task_count=0, total_complexity=0.0,
                                   avg_complexity=0.0, peak_complexity=0.0, tasks_per_hour=0.0)
        scores = [COMPLEXITY_SCORES[c] for _, c, _ in recent]
        total = sum(scores)
        avg = mean(scores)
        peak = max(scores)
        tasks_per_hour = len(recent) / TASK_WINDOW_HOURS
        return WorkloadMetrics(user_id=user_id, task_count=len(recent),
                               total_complexity=total, avg_complexity=round(avg, 2),
                               peak_complexity=float(peak), tasks_per_hour=round(tasks_per_hour, 2))

    def get_workload_level(self, user_id: str) -> WorkloadLevel:
        """Classify the user's current workload into a WorkloadLevel."""
        metrics = self.compute_workload(user_id)
        tph = metrics.tasks_per_hour
        avg = metrics.avg_complexity
        if tph >= 4 or avg >= 6:
            return WorkloadLevel.OVERLOADED
        if tph >= 2.5 or avg >= 4:
            return WorkloadLevel.HEAVY
        if tph >= 1 or avg >= 2:
            return WorkloadLevel.MODERATE
        return WorkloadLevel.LIGHT

    def predict_burnout_risk(self, user_id: str) -> float:
        """Return a 0-1 burnout risk score based on task load trend."""
        all_tasks = self._tasks.get(user_id, [])
        if len(all_tasks) < 5:
            return 0.0
        scores = [COMPLEXITY_SCORES[c] for _, c, _ in all_tasks[-20:]]
        avg = mean(scores)
        variability = stdev(scores) if len(scores) > 1 else 0.0
        # High average + low variability = sustained pressure = burnout risk
        risk = min((avg / 8) * 0.7 + (1 - min(variability / 4, 1)) * 0.3, 1.0)
        return round(risk, 3)

    def get_recommendations(self, user_id: str) -> List[str]:
        """Provide actionable workload-management recommendations."""
        level = self.get_workload_level(user_id)
        risk = self.predict_burnout_risk(user_id)
        recs: List[str] = []
        if level in (WorkloadLevel.HEAVY, WorkloadLevel.OVERLOADED):
            recs.append("Consider delegating or deferring lower-priority tasks.")
            recs.append("Take a 10-minute break before starting the next high-complexity item.")
        if level == WorkloadLevel.OVERLOADED:
            recs.append("Your current load is unsustainable — raise this with your team.")
        if risk >= 0.7:
            recs.append("Burnout risk is elevated. Protect time for recovery and deep rest.")
        if not recs:
            recs.append("Workload looks healthy. Keep up the good balance!")
        return recs
