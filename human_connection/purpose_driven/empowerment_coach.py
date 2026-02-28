"""User skill development and empowerment coaching."""

import logging
import random
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

SKILL_KEYWORDS: Dict[str, List[str]] = {
    "python": ["python", "def ", "import ", "class ", "list ", "dict "],
    "data_analysis": ["dataframe", "csv", "statistics", "mean", "median", "plot"],
    "communication": ["explain", "describe", "summarise", "present", "report"],
    "problem_solving": ["debug", "fix", "solve", "error", "issue", "workaround"],
    "critical_thinking": ["why", "because", "reason", "evaluate", "compare", "pros", "cons"],
    "writing": ["paragraph", "sentence", "grammar", "punctuation", "draft", "revise"],
}

SKILL_RESOURCES: Dict[str, List[str]] = {
    "python": ["Practice Python exercises on Exercism.io", "Read the official Python tutorial",
               "Build a small project: a to-do list app"],
    "data_analysis": ["Explore a public dataset on Kaggle", "Learn pandas basics",
                      "Try a data-cleaning challenge"],
    "communication": ["Write a daily journal entry", "Summarise an article in 3 sentences",
                      "Record yourself explaining a concept"],
    "problem_solving": ["Work through a coding kata on Codewars", "Rubber-duck debug your next issue",
                        "Try the '5 Whys' root-cause technique"],
    "critical_thinking": ["Debate both sides of an argument", "Evaluate a news article for bias",
                          "Apply the Socratic method to a problem"],
    "writing": ["Edit yesterday's writing for clarity", "Write one paragraph without adverbs",
                "Read a style-guide chapter (e.g., Strunk & White)"],
}

CELEBRATION_MESSAGES = [
    "🎉 Amazing work on '{achievement}'! You're making real progress!",
    "🌟 '{achievement}' — that's a skill milestone to be proud of!",
    "🚀 You just levelled up with '{achievement}'. Keep building on this!",
    "💪 '{achievement}' is no small feat. You earned it!",
]


@dataclass
class SkillGap:
    """A skill where the user needs development."""
    skill: str
    current_score: float     # 0-1
    target_score: float = 0.8
    priority: str = "medium"  # "low", "medium", "high"


@dataclass
class LearningPath:
    """An ordered list of skill-building steps."""
    skill_gaps: List[SkillGap]
    steps: List[str]
    estimated_hours: float
    created_at: datetime = field(default_factory=datetime.utcnow)


class EmpowermentCoach:
    """Guide users toward skill growth through assessment, paths, and celebration."""

    def __init__(self) -> None:
        # user_id -> skill -> list[score float]
        self._growth: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        logger.info("EmpowermentCoach initialised.")

    def assess_skills(self, user_responses: List[str]) -> List[SkillGap]:
        """Infer skill levels from a list of user-written responses."""
        combined = " ".join(user_responses).lower()
        gaps: List[SkillGap] = []
        for skill, keywords in SKILL_KEYWORDS.items():
            hits = sum(1 for kw in keywords if kw in combined)
            score = min(hits / len(keywords), 1.0)
            if score < 0.8:
                priority = "high" if score < 0.3 else ("medium" if score < 0.6 else "low")
                gaps.append(SkillGap(skill=skill, current_score=round(score, 2),
                                     priority=priority))
        gaps.sort(key=lambda g: g.current_score)
        logger.debug("Assessed %d skill gaps.", len(gaps))
        return gaps

    def create_learning_path(self, skill_gaps: List[SkillGap]) -> LearningPath:
        """Build an ordered LearningPath from assessed SkillGaps."""
        steps: List[str] = []
        for gap in skill_gaps:
            resources = SKILL_RESOURCES.get(gap.skill, [])
            for i, resource in enumerate(resources[:2]):
                steps.append(f"[{gap.skill.upper()} step {i + 1}] {resource}")
        estimated_hours = round(len(skill_gaps) * 2.5, 1)
        return LearningPath(skill_gaps=skill_gaps, steps=steps, estimated_hours=estimated_hours)

    def suggest_next_step(self, user_id: str) -> str:
        """Suggest the single most impactful next learning action for a user."""
        growth = self._growth.get(user_id, {})
        if not growth:
            return "Start by completing a skill self-assessment to reveal your strongest opportunities."
        # Find the skill with lowest average score
        avg_scores = {skill: sum(scores) / len(scores)
                      for skill, scores in growth.items() if scores}
        if not avg_scores:
            return "Keep practising — every interaction teaches you something new."
        weakest = min(avg_scores, key=lambda s: avg_scores[s])
        resources = SKILL_RESOURCES.get(weakest, ["Explore a related tutorial or documentation."])
        return f"Focus on {weakest.replace('_', ' ')}: {resources[0]}"

    def celebrate_progress(self, achievement: str) -> str:
        """Return a celebration message for an achievement."""
        template = random.choice(CELEBRATION_MESSAGES)
        return template.format(achievement=achievement)

    def track_growth(self, user_id: str, skill: str, score: float) -> None:
        """Record a skill score observation for a user."""
        self._growth[user_id][skill].append(max(0.0, min(1.0, score)))
        logger.debug("Growth tracked: user=%s skill=%s score=%.2f", user_id, skill, score)
