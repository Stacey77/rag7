"""Advanced learning module for robotics AGI."""
from .offline_rl import OfflineRL
from .marl import MultiAgentRL
from .inverse_rl import InverseRL
from .curriculum import CurriculumGenerator
from .self_supervised import SelfSupervisedLearner

__all__ = ["OfflineRL", "MultiAgentRL", "InverseRL", "CurriculumGenerator", "SelfSupervisedLearner"]
