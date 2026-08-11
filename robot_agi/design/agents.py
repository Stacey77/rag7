"""Specialized robot-design agents: kinematics, structural, material.

They collaborate through the orchestrator's shared context (a blackboard):
kinematics builds the chain, structural sizes each link from downstream load,
and material assigns materials and computes mass — each reading the prior
agents' work and recording its A2A messages on the bus.
"""
import logging
import math

from ..orchestration.agent import Agent
from .spec import Joint, Link, RobotDesign

logger = logging.getLogger(__name__)

DENSITY = {"steel": 7850.0, "aluminium": 2700.0, "carbon-fibre": 1600.0}


def parse_brief(goal: str) -> dict:
    """Extract a structured brief from a free-text goal.

    Args:
        goal: e.g. "6-DOF humanoid service robot arm".

    Returns:
        Dict with the goal, detected limb, and degrees of freedom.
    """
    text = goal.lower()
    limb = "arm"
    for candidate in ("arm", "leg", "gripper", "torso", "neck"):
        if candidate in text:
            limb = candidate
            break
    dof = None
    for token in text.replace("-", " ").split():
        if token.isdigit():
            dof = int(token)
            break
    if dof is None:
        dof = {"arm": 6, "leg": 6, "gripper": 2, "torso": 3, "neck": 2}[limb]
    return {"goal": goal, "limb": limb, "dof": max(1, min(dof, 12))}


class KinematicsAgent(Agent):
    """Builds the kinematic chain: links and movable joints for the limb."""

    name = "kinematics"
    role = "kinematics"

    def run(self, brief: dict, context: dict) -> dict:
        dof = brief["dof"]
        limb = brief["limb"]
        design = RobotDesign(name=f"{limb}_{dof}dof")
        design.links.append(Link(name="base", length_m=0.08))
        prev = "base"
        # Links taper from base to tip; alternate joint axes for a real chain.
        for i in range(dof):
            length = round(0.30 * (0.82 ** i), 4)
            link = Link(name=f"link_{i+1}", length_m=length)
            design.links.append(link)
            axis = (0.0, 0.0, 1.0) if i % 2 == 0 else (0.0, 1.0, 0.0)
            design.joints.append(Joint(name=f"joint_{i+1}", joint_type="revolute",
                                       parent=prev, child=link.name, axis=axis))
            prev = link.name
        context["design"] = design
        logger.info("Kinematics built a %d-DOF %s (%d links)", dof, limb, len(design.links))
        return {"dof": design.dof(), "links": len(design.links), "reach_m": design.reach_m()}


class StructuralAgent(Agent):
    """Sizes each link's cross-section from the load it must carry downstream."""

    name = "structural"
    role = "structural analysis"

    def run(self, brief: dict, context: dict) -> dict:
        design: RobotDesign = context["design"]
        self.tell("kinematics", "request", {"need": "link lengths + order"})
        n = len(design.links)
        # Links nearer the base carry more downstream load -> larger radius.
        for depth, link in enumerate(design.links):
            downstream = n - depth
            link.radius_m = round(0.012 + 0.004 * downstream, 4)
        self.tell("material", "deliver", {"radii": {l.name: l.radius_m for l in design.links}})
        logger.info("Structural sized %d links (base radius %.3fm)", n, design.links[0].radius_m)
        return {"sized_links": n, "base_radius_m": design.links[0].radius_m}


class MaterialAgent(Agent):
    """Assigns a material per link by position and computes link mass."""

    name = "material"
    role = "material selection"

    def run(self, brief: dict, context: dict) -> dict:
        design: RobotDesign = context["design"]
        self.tell("structural", "request", {"need": "cross-section radii"})
        hints = self.ask_knowledge("material link load")
        n = len(design.links)
        chosen = []
        for depth, link in enumerate(design.links):
            frac = depth / max(1, n - 1)
            if frac < 0.34:
                material = "steel"
            elif frac < 0.67:
                material = "aluminium"
            else:
                material = "carbon-fibre"
            link.material = material
            volume = math.pi * (link.radius_m ** 2) * link.length_m
            link.mass_kg = round(DENSITY[material] * volume, 4)
            chosen.append(material)
        logger.info("Material assigned across chain; total mass %.3fkg", design.total_mass_kg())
        return {
            "materials": chosen,
            "total_mass_kg": design.total_mass_kg(),
            "knowledge_used": [h["text"] for h in hints],
        }
