"""Export a RobotDesign to URDF — the standard robot-description XML format."""
import math
import xml.etree.ElementTree as ET

from .spec import RobotDesign


def _cyl_inertia(mass: float, radius: float, length: float) -> dict:
    """Inertia tensor of a solid cylinder about its centre (z along length)."""
    ixx = (1.0 / 12.0) * mass * (3 * radius ** 2 + length ** 2)
    izz = 0.5 * mass * radius ** 2
    return {"ixx": ixx, "iyy": ixx, "izz": izz}


def to_urdf(design: RobotDesign) -> str:
    """Render a design as a URDF XML document.

    Args:
        design: The RobotDesign to serialize.

    Returns:
        A URDF XML string (parseable by ROS / simulators).
    """
    robot = ET.Element("robot", {"name": design.name})

    for link in design.links:
        el = ET.SubElement(robot, "link", {"name": link.name})
        # visual: a cylinder along z, offset so it starts at the joint origin
        visual = ET.SubElement(el, "visual")
        origin = ET.SubElement(visual, "origin", {"xyz": f"0 0 {link.length_m / 2:.4f}", "rpy": "0 0 0"})
        geometry = ET.SubElement(visual, "geometry")
        ET.SubElement(geometry, "cylinder", {"radius": f"{link.radius_m:.4f}", "length": f"{link.length_m:.4f}"})
        if link.material:
            mat = ET.SubElement(visual, "material", {"name": link.material})
            ET.SubElement(mat, "color", {"rgba": _material_rgba(link.material)})
        # inertial
        inertial = ET.SubElement(el, "inertial")
        ET.SubElement(inertial, "mass", {"value": f"{link.mass_kg:.4f}"})
        ET.SubElement(inertial, "origin", {"xyz": f"0 0 {link.length_m / 2:.4f}", "rpy": "0 0 0"})
        i = _cyl_inertia(max(link.mass_kg, 1e-6), link.radius_m, link.length_m)
        ET.SubElement(inertial, "inertia", {
            "ixx": f"{i['ixx']:.6f}", "ixy": "0", "ixz": "0",
            "iyy": f"{i['iyy']:.6f}", "iyz": "0", "izz": f"{i['izz']:.6f}",
        })

    # joints connect parent -> child; child link is placed at end of parent link
    parent_length = {l.name: l.length_m for l in design.links}
    for joint in design.joints:
        el = ET.SubElement(robot, "joint", {"name": joint.name, "type": joint.joint_type})
        ET.SubElement(el, "parent", {"link": joint.parent})
        ET.SubElement(el, "child", {"link": joint.child})
        ET.SubElement(el, "origin", {"xyz": f"0 0 {parent_length.get(joint.parent, 0.0):.4f}", "rpy": "0 0 0"})
        if joint.joint_type == "revolute":
            ax = joint.axis
            ET.SubElement(el, "axis", {"xyz": f"{ax[0]:g} {ax[1]:g} {ax[2]:g}"})
            ET.SubElement(el, "limit", {
                "lower": f"{joint.lower:.4f}", "upper": f"{joint.upper:.4f}",
                "effort": "50", "velocity": "2.0",
            })

    ET.indent(robot, space="  ")
    return '<?xml version="1.0"?>\n' + ET.tostring(robot, encoding="unicode")


def _material_rgba(material: str) -> str:
    return {
        "steel": "0.55 0.57 0.60 1",
        "aluminium": "0.80 0.82 0.85 1",
        "carbon-fibre": "0.15 0.15 0.18 1",
    }.get(material, "0.6 0.6 0.6 1")
