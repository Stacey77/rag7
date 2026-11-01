"""Robot design data model: links, joints, and the assembled design."""
from dataclasses import asdict, dataclass, field


@dataclass
class Link:
    """A rigid body in the kinematic chain.

    Attributes:
        name: Unique link name.
        length_m: Length along its primary axis, metres.
        mass_kg: Mass, kilograms (filled by the structural/material stages).
        material: Material name (filled by the material stage).
        radius_m: Nominal cross-section radius, metres (structural stage).
    """

    name: str
    length_m: float
    mass_kg: float = 0.0
    material: str = ""
    radius_m: float = 0.02


@dataclass
class Joint:
    """A connection between two links.

    Attributes:
        name: Unique joint name.
        joint_type: URDF joint type (e.g. "revolute", "fixed").
        parent: Parent link name.
        child: Child link name.
        axis: Rotation/translation axis as (x, y, z).
        lower: Lower limit, radians.
        upper: Upper limit, radians.
    """

    name: str
    joint_type: str
    parent: str
    child: str
    axis: tuple = (0.0, 0.0, 1.0)
    lower: float = -3.1416
    upper: float = 3.1416


@dataclass
class RobotDesign:
    """A complete robot design: an ordered chain of links and joints."""

    name: str
    links: list = field(default_factory=list)
    joints: list = field(default_factory=list)

    def dof(self) -> int:
        """Return the number of movable (non-fixed) joints."""
        return sum(1 for j in self.joints if j.joint_type != "fixed")

    def total_mass_kg(self) -> float:
        """Return the summed mass of every link."""
        return round(sum(l.mass_kg for l in self.links), 4)

    def reach_m(self) -> float:
        """Return the summed link length (fully-extended reach)."""
        return round(sum(l.length_m for l in self.links), 4)

    def to_dict(self) -> dict:
        """Return a JSON-serializable view of the design."""
        return {
            "name": self.name,
            "dof": self.dof(),
            "total_mass_kg": self.total_mass_kg(),
            "reach_m": self.reach_m(),
            "links": [asdict(l) for l in self.links],
            "joints": [asdict(j) for j in self.joints],
        }
