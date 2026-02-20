"""Edge device deployment management."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

import numpy as np
from loguru import logger


class DeviceStatus(Enum):
    """Edge device lifecycle status."""

    REGISTERED = auto()
    ONLINE = auto()
    OFFLINE = auto()
    DEPLOYING = auto()
    DEGRADED = auto()
    DECOMMISSIONED = auto()


@dataclass
class EdgeDevice:
    """Registered edge device metadata.

    Attributes:
        device_id: Unique identifier.
        name: Human-readable device name.
        location: Physical or logical location tag.
        hardware_spec: CPU/memory/disk specification dictionary.
        status: Current lifecycle status.
        registered_at: UTC registration timestamp.
        last_seen_at: UTC timestamp of last heartbeat.
        deployed_models: Mapping of model_id to deployment version.
        tags: Arbitrary classification tags.
    """

    device_id: str
    name: str
    location: str
    hardware_spec: dict[str, Any]
    status: DeviceStatus = DeviceStatus.REGISTERED
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen_at: datetime | None = None
    deployed_models: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class Deployment:
    """A model deployment to an edge device.

    Attributes:
        deployment_id: Unique identifier.
        device_id: Target device.
        model_id: Model being deployed.
        model_version: Semantic version string.
        status: Current deployment status (``"pending"``, ``"deployed"``, ``"failed"``).
        deployed_at: UTC deployment timestamp.
        artefact_uri: Location of the model artefact.
    """

    deployment_id: str
    device_id: str
    model_id: str
    model_version: str
    status: str = "pending"
    deployed_at: datetime | None = None
    artefact_uri: str = ""


class EdgeDeployment:
    """Edge device deployment management.

    Manages the lifecycle of edge devices and model deployments,
    including registration, deployment, synchronisation, and health tracking.

    Attributes:
        devices: Registered edge devices keyed by device_id.
        deployments: All deployments keyed by deployment_id.
    """

    def __init__(self) -> None:
        """Initialise the edge deployment manager."""
        self.devices: dict[str, EdgeDevice] = {}
        self.deployments: dict[str, Deployment] = {}
        logger.info("EdgeDeployment manager initialised")

    def register_device(
        self,
        name: str,
        location: str,
        hardware_spec: dict[str, Any],
        tags: list[str] | None = None,
    ) -> EdgeDevice:
        """Register a new edge device.

        Args:
            name: Human-readable device name.
            location: Physical or logical location identifier.
            hardware_spec: Device capability specification dict.
            tags: Optional classification tags.

        Returns:
            The registered :class:`EdgeDevice`.

        Raises:
            ValueError: If ``hardware_spec`` is empty.
        """
        if not hardware_spec:
            raise ValueError("hardware_spec must not be empty")

        device_id = f"edge_{uuid.uuid4().hex[:8]}"
        device = EdgeDevice(
            device_id=device_id,
            name=name,
            location=location,
            hardware_spec=hardware_spec,
            tags=tags or [],
        )
        self.devices[device_id] = device
        logger.info(
            "Edge device registered: name='{}', id={}, location='{}'",
            name,
            device_id,
            location,
        )
        return device

    async def deploy(
        self,
        device_id: str,
        model_id: str,
        model_version: str,
        artefact_uri: str = "",
    ) -> Deployment:
        """Deploy a model to an edge device.

        Args:
            device_id: Target device identifier.
            model_id: Model identifier to deploy.
            model_version: Version string.
            artefact_uri: URI to the model artefact.

        Returns:
            The completed :class:`Deployment`.

        Raises:
            KeyError: If ``device_id`` is not found.
            RuntimeError: If the device is not in a deployable state.
        """
        device = self._get_device(device_id)
        if device.status not in (DeviceStatus.REGISTERED, DeviceStatus.ONLINE):
            raise RuntimeError(
                f"Device '{device_id}' is in state {device.status.name}, cannot deploy"
            )

        deployment_id = f"dep_{uuid.uuid4().hex[:8]}"
        deployment = Deployment(
            deployment_id=deployment_id,
            device_id=device_id,
            model_id=model_id,
            model_version=model_version,
            artefact_uri=artefact_uri,
        )
        device.status = DeviceStatus.DEPLOYING
        self.deployments[deployment_id] = deployment

        logger.info(
            "Deploying '{}' v{} to device '{}'",
            model_id,
            model_version,
            device_id,
        )
        await asyncio.sleep(0)  # Simulate transfer

        deployment.status = "deployed"
        deployment.deployed_at = datetime.now(timezone.utc)
        device.deployed_models[model_id] = model_version
        device.status = DeviceStatus.ONLINE
        device.last_seen_at = deployment.deployed_at

        logger.info(
            "Deployment {} complete: '{}' v{} on '{}'",
            deployment_id,
            model_id,
            model_version,
            device_id,
        )
        return deployment

    async def sync(
        self,
        device_id: str,
        config_updates: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Synchronise device configuration and state.

        Args:
            device_id: Device to sync.
            config_updates: Optional configuration values to push.

        Returns:
            Sync result dictionary with status and applied changes.

        Raises:
            KeyError: If ``device_id`` is not found.
        """
        device = self._get_device(device_id)
        await asyncio.sleep(0)

        device.last_seen_at = datetime.now(timezone.utc)
        if device.status == DeviceStatus.OFFLINE:
            device.status = DeviceStatus.ONLINE

        result: dict[str, Any] = {
            "device_id": device_id,
            "synced_at": device.last_seen_at.isoformat(),
            "config_applied": bool(config_updates),
            "deployed_models": dict(device.deployed_models),
        }
        logger.debug("Synced device '{}'", device_id)
        return result

    def get_online_devices(self) -> list[EdgeDevice]:
        """Return all currently online devices.

        Returns:
            List of online :class:`EdgeDevice` objects.
        """
        return [d for d in self.devices.values() if d.status == DeviceStatus.ONLINE]

    def _get_device(self, device_id: str) -> EdgeDevice:
        """Retrieve a device by ID.

        Args:
            device_id: Device identifier.

        Returns:
            The :class:`EdgeDevice`.

        Raises:
            KeyError: If not found.
        """
        if device_id not in self.devices:
            raise KeyError(f"Device '{device_id}' not found")
        return self.devices[device_id]
