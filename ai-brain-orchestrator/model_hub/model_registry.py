"""Model Registry – central model versioning and lifecycle management.

Provides a versioned catalogue of AI model descriptors.  Actual model weights
are referenced by URI so the registry itself carries no ML framework dependency.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from shared.common.logger import get_logger

log = get_logger(__name__, service="ai-brain-orchestrator")


class ModelStatus(Enum):
    """Lifecycle status of a registered model."""

    REGISTERED = auto()
    ACTIVE = auto()
    DEPRECATED = auto()
    ARCHIVED = auto()


@dataclass
class ModelDescriptor:
    """Metadata record for a single model version.

    Attributes:
        model_id: Unique identifier, auto-generated when omitted.
        name: Human-readable model name.
        version: Semantic version string (e.g. ``"1.2.0"``).
        model_type: Category tag (e.g. ``"classifier"``, ``"regressor"``).
        uri: Location of the model artefact (path or remote URI).
        status: Current lifecycle status.
        performance_metrics: Dict of evaluation metrics (e.g. RMSE, accuracy).
        tags: Arbitrary keyword labels for filtering.
        metadata: Additional structured data.
    """

    name: str
    version: str
    model_type: str = "generic"
    uri: str = ""
    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ModelStatus = ModelStatus.REGISTERED
    performance_metrics: dict[str, float] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelRegistry:
    """Versioned model catalogue with register, retrieval, and deprecation.

    Attributes:
        _models: Primary store keyed by ``model_id``.
        _name_index: Secondary index mapping ``(name, version)`` → ``model_id``.
    """

    def __init__(self) -> None:
        """Initialise an empty model registry."""
        self._models: dict[str, ModelDescriptor] = {}
        self._name_index: dict[tuple[str, str], str] = {}
        log.info("ModelRegistry initialised")

    def register(self, descriptor: ModelDescriptor) -> str:
        """Add a new model version to the registry.

        Args:
            descriptor: :class:`ModelDescriptor` to register.

        Returns:
            The ``model_id`` of the registered model.

        Raises:
            ValueError: If a model with the same ``(name, version)`` already exists.
        """
        key = (descriptor.name, descriptor.version)
        if key in self._name_index:
            raise ValueError(
                f"Model '{descriptor.name}' v{descriptor.version} already registered"
            )
        descriptor.status = ModelStatus.ACTIVE
        self._models[descriptor.model_id] = descriptor
        self._name_index[key] = descriptor.model_id
        log.info(
            "Model registered",
            model_id=descriptor.model_id,
            name=descriptor.name,
            version=descriptor.version,
        )
        return descriptor.model_id

    def get(self, model_id: str) -> ModelDescriptor:
        """Retrieve a model by its unique ID.

        Args:
            model_id: The ``model_id`` to look up.

        Returns:
            The corresponding :class:`ModelDescriptor`.

        Raises:
            KeyError: If *model_id* is not found.
        """
        if model_id not in self._models:
            raise KeyError(f"Model '{model_id}' not found in registry")
        return self._models[model_id]

    def get_by_name(self, name: str, version: str) -> ModelDescriptor:
        """Retrieve a model by name and version.

        Args:
            name: Model name.
            version: Semantic version string.

        Returns:
            The corresponding :class:`ModelDescriptor`.

        Raises:
            KeyError: If the ``(name, version)`` pair is not found.
        """
        key = (name, version)
        if key not in self._name_index:
            raise KeyError(f"Model '{name}' v{version} not found")
        return self._models[self._name_index[key]]

    def list_models(
        self,
        model_type: str | None = None,
        status: ModelStatus | None = None,
        tag: str | None = None,
    ) -> list[ModelDescriptor]:
        """Return models optionally filtered by type, status, or tag.

        Args:
            model_type: Filter to a specific model category.
            status: Filter to a specific lifecycle status.
            tag: Filter to models carrying this tag label.

        Returns:
            List of matching :class:`ModelDescriptor` instances.
        """
        results = list(self._models.values())
        if model_type is not None:
            results = [m for m in results if m.model_type == model_type]
        if status is not None:
            results = [m for m in results if m.status == status]
        if tag is not None:
            results = [m for m in results if tag in m.tags]
        log.debug("Models listed", count=len(results), filters={"type": model_type, "status": status, "tag": tag})
        return results

    def deprecate(self, model_id: str) -> None:
        """Mark a model as deprecated so it is excluded from active selection.

        Args:
            model_id: The ``model_id`` to deprecate.

        Raises:
            KeyError: If *model_id* is not found.
        """
        model = self.get(model_id)
        model.status = ModelStatus.DEPRECATED
        log.info("Model deprecated", model_id=model_id, name=model.name, version=model.version)
