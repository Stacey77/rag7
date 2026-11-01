"""Robot design subsystem: agents that turn a brief into a real robot spec."""
from .agents import KinematicsAgent, MaterialAgent, StructuralAgent, parse_brief
from .pipeline import design_robot
from .spec import Joint, Link, RobotDesign
from .urdf import to_urdf

__all__ = [
    "design_robot",
    "parse_brief",
    "RobotDesign",
    "Link",
    "Joint",
    "to_urdf",
    "KinematicsAgent",
    "StructuralAgent",
    "MaterialAgent",
]
