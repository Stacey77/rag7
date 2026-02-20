"""Resource Allocator – dynamic resource budget management.

Tracks named resource pools (CPU, memory, API quota, …) and provides
allocation/release semantics with utilisation reporting.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shared.common.logger import get_logger

log = get_logger(__name__, service="agi-orchestrator")


@dataclass
class ResourcePool:
    """A named resource bucket with a fixed capacity.

    Attributes:
        name: Human-readable resource name (e.g. ``"cpu"``, ``"memory_gb"``).
        capacity: Total available units.
        allocated: Currently committed units.
        metadata: Arbitrary tags.
    """

    name: str
    capacity: float
    allocated: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def available(self) -> float:
        """Remaining unallocated units."""
        return max(0.0, self.capacity - self.allocated)

    @property
    def utilisation(self) -> float:
        """Fraction of capacity currently in use, in ``[0.0, 1.0]``."""
        return self.allocated / self.capacity if self.capacity else 0.0


@dataclass
class Allocation:
    """A recorded allocation ticket.

    Attributes:
        allocation_id: Unique ticket identifier.
        resource_name: Name of the pool allocated from.
        units: Number of units reserved.
        owner: Agent or component that owns this allocation.
    """

    allocation_id: str
    resource_name: str
    units: float
    owner: str = "unknown"


class ResourceAllocator:
    """Dynamic resource manager that tracks pools and outstanding allocations.

    Attributes:
        _pools: Registered resource pools keyed by name.
        _allocations: Outstanding allocation tickets keyed by ``allocation_id``.
    """

    def __init__(self) -> None:
        """Initialise with no pools and no outstanding allocations."""
        self._pools: dict[str, ResourcePool] = {}
        self._allocations: dict[str, Allocation] = {}
        log.info("ResourceAllocator initialised")

    def register_pool(self, name: str, capacity: float, metadata: dict[str, Any] | None = None) -> None:
        """Register a new named resource pool.

        Args:
            name: Unique pool name.
            capacity: Total available units.
            metadata: Optional tags.

        Raises:
            ValueError: If *name* is already registered or *capacity* ≤ 0.
        """
        if name in self._pools:
            raise ValueError(f"Pool '{name}' already registered")
        if capacity <= 0:
            raise ValueError(f"capacity must be positive, got {capacity}")
        self._pools[name] = ResourcePool(name=name, capacity=capacity, metadata=metadata or {})
        log.info("Resource pool registered", name=name, capacity=capacity)

    def allocate(
        self,
        allocation_id: str,
        resource_name: str,
        units: float,
        owner: str = "unknown",
    ) -> Allocation:
        """Reserve *units* from the named pool.

        Args:
            allocation_id: Unique ticket identifier chosen by the caller.
            resource_name: Name of the pool to allocate from.
            units: Number of units to reserve.
            owner: Identifier of the requesting component.

        Returns:
            The created :class:`Allocation` ticket.

        Raises:
            KeyError: If *resource_name* is not registered.
            ValueError: If insufficient capacity is available or *units* ≤ 0.
        """
        if resource_name not in self._pools:
            raise KeyError(f"Resource pool '{resource_name}' not found")
        if units <= 0:
            raise ValueError(f"units must be positive, got {units}")

        pool = self._pools[resource_name]
        if units > pool.available:
            raise ValueError(
                f"Insufficient capacity: requested {units}, available {pool.available}"
            )

        pool.allocated += units
        ticket = Allocation(
            allocation_id=allocation_id,
            resource_name=resource_name,
            units=units,
            owner=owner,
        )
        self._allocations[allocation_id] = ticket
        log.info(
            "Resources allocated",
            allocation_id=allocation_id,
            resource=resource_name,
            units=units,
            utilisation=f"{pool.utilisation:.1%}",
        )
        return ticket

    def release(self, allocation_id: str) -> None:
        """Return previously reserved units back to the pool.

        Args:
            allocation_id: Ticket identifier returned by :meth:`allocate`.

        Raises:
            KeyError: If *allocation_id* is not found.
        """
        if allocation_id not in self._allocations:
            raise KeyError(f"Allocation '{allocation_id}' not found")

        ticket = self._allocations.pop(allocation_id)
        pool = self._pools[ticket.resource_name]
        pool.allocated = max(0.0, pool.allocated - ticket.units)
        log.info(
            "Resources released",
            allocation_id=allocation_id,
            resource=ticket.resource_name,
            units=ticket.units,
        )

    def get_utilization(self) -> dict[str, dict[str, float]]:
        """Return a utilisation snapshot for every registered pool.

        Returns:
            Mapping of pool name → dict with ``capacity``, ``allocated``,
            ``available``, and ``utilisation`` keys.
        """
        report = {
            name: {
                "capacity": pool.capacity,
                "allocated": pool.allocated,
                "available": pool.available,
                "utilisation": pool.utilisation,
            }
            for name, pool in self._pools.items()
        }
        log.debug("Utilisation report generated", pools=list(report.keys()))
        return report
