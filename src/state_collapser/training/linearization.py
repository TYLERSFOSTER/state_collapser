"""Backend-independent semantic-to-numeric conversion boundary.

This module deliberately does not import Torch at module import time. It keeps
the object-native runtime as the source of truth and exposes explicit conversion
helpers for learner and benchmark boundaries.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import time
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from state_collapser.core.edges import BaseEdge
from state_collapser.core.state import State
from state_collapser.tower.partition.ids import (
    ActionCellId,
    ActionCollectionId,
    ActionId,
    EdgeId,
    StateCellId,
    StateId,
)
from state_collapser.tower.partition.tower import PartitionTower

from .fibers import FiberDeparture, FiberDepartureReason, FiberStageContext
from .inputs import ActionSelectionInput
from .transitions import TrainingTransition

JsonDict = dict[str, object]


class LinearizationState(StrEnum):
    """Whether a tensor-capable conversion boundary is present and active."""

    ABSENT = "ABSENT"
    PRESENT_DISABLED = "PRESENT_DISABLED"
    PRESENT_ENABLED = "PRESENT_ENABLED"


class NumericBackend(StrEnum):
    """Numeric backend used by the conversion boundary."""

    NONE = "NONE"
    NUMPY = "NUMPY"
    TORCH = "TORCH"


class TensorDeviceKind(StrEnum):
    """Tensor device family requested by the conversion boundary."""

    NONE = "NONE"
    CPU = "CPU"
    CUDA = "CUDA"


@dataclass(frozen=True, slots=True)
class BackendAvailability:
    """Local optional-backend availability report."""

    available: bool
    version: str | None = None
    cuda_available: bool = False

    def to_dict(self) -> JsonDict:
        """Return a JSON-safe dictionary."""

        return {
            "available": self.available,
            "version": self.version,
            "cuda_available": self.cuda_available,
        }


@dataclass(frozen=True, slots=True)
class LinearizationConfig:
    """Configuration for semantic-to-numeric conversion."""

    linearization_state: LinearizationState
    numeric_backend: NumericBackend
    device_kind: TensorDeviceKind
    dtype: str | None = None
    mask_dtype: str = "bool"
    max_tower_depth: int | None = None
    max_action_count: int | None = None
    sequence_length: int | None = None
    include_diagnostics: bool = False
    encoder_registry_id: str | None = None
    strict: bool = True
    debug_export_records: bool = False

    def __post_init__(self) -> None:
        _validate_config(self)

    @property
    def enabled(self) -> bool:
        """Return whether conversion is meant to produce records."""

        return self.linearization_state == LinearizationState.PRESENT_ENABLED

    @property
    def derived_benchmark_label(self) -> str:
        """Return the benchmark label derived from orthogonal mode fields."""

        if (
            self.linearization_state == LinearizationState.ABSENT
            and self.numeric_backend == NumericBackend.NONE
            and self.device_kind == TensorDeviceKind.NONE
        ):
            return "none_control_flow"
        if self.linearization_state == LinearizationState.PRESENT_DISABLED:
            return "tensor_available_disabled"
        if (
            self.linearization_state == LinearizationState.PRESENT_ENABLED
            and self.numeric_backend == NumericBackend.TORCH
            and self.device_kind == TensorDeviceKind.CPU
        ):
            return "tensor_enabled_cpu"
        if (
            self.linearization_state == LinearizationState.PRESENT_ENABLED
            and self.numeric_backend == NumericBackend.TORCH
            and self.device_kind == TensorDeviceKind.CUDA
        ):
            return "tensor_enabled_cuda"
        raise ValueError("No benchmark label is defined for this linearization config.")

    def to_dict(self) -> JsonDict:
        """Return a JSON-safe dictionary."""

        return {
            "linearization_state": self.linearization_state.value,
            "numeric_backend": self.numeric_backend.value,
            "device_kind": self.device_kind.value,
            "dtype": self.dtype,
            "mask_dtype": self.mask_dtype,
            "max_tower_depth": self.max_tower_depth,
            "max_action_count": self.max_action_count,
            "sequence_length": self.sequence_length,
            "include_diagnostics": self.include_diagnostics,
            "encoder_registry_id": self.encoder_registry_id,
            "strict": self.strict,
            "debug_export_records": self.debug_export_records,
            "derived_benchmark_label": self.derived_benchmark_label,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> LinearizationConfig:
        """Build a config from a dictionary produced by `to_dict`."""

        return cls(
            linearization_state=LinearizationState(str(data["linearization_state"])),
            numeric_backend=NumericBackend(str(data["numeric_backend"])),
            device_kind=TensorDeviceKind(str(data["device_kind"])),
            dtype=_optional_str(data.get("dtype")),
            mask_dtype=str(data.get("mask_dtype", "bool")),
            max_tower_depth=_optional_int(data.get("max_tower_depth")),
            max_action_count=_optional_int(data.get("max_action_count")),
            sequence_length=_optional_int(data.get("sequence_length")),
            include_diagnostics=bool(data.get("include_diagnostics", False)),
            encoder_registry_id=_optional_str(data.get("encoder_registry_id")),
            strict=bool(data.get("strict", True)),
            debug_export_records=bool(data.get("debug_export_records", False)),
        )


@dataclass(frozen=True, slots=True)
class LinearizationReport:
    """Benchmark-visible report for the tensorization boundary."""

    linearization_state: LinearizationState
    numeric_backend: NumericBackend
    device_kind: TensorDeviceKind
    benchmark_label: str
    backend_available: bool
    enabled: bool
    dtype: str | None
    mask_dtype: str
    numpy_available: bool
    numpy_version: str | None
    torch_available: bool
    torch_version: str | None
    cuda_available: bool
    encoder_registry_id: str | None
    schema_fingerprint: str | None
    tower_fingerprint: str | None
    max_tower_depth: int | None
    max_action_count: int | None
    conversion_count: int = 0
    conversion_elapsed_seconds: float = 0.0
    debug_record_exported: bool = False
    metadata: Mapping[str, object] = field(default_factory=dict)

    def to_dict(self) -> JsonDict:
        """Return a JSON-safe dictionary."""

        return {
            "linearization_state": self.linearization_state.value,
            "numeric_backend": self.numeric_backend.value,
            "device_kind": self.device_kind.value,
            "benchmark_label": self.benchmark_label,
            "backend_available": self.backend_available,
            "enabled": self.enabled,
            "dtype": self.dtype,
            "mask_dtype": self.mask_dtype,
            "numpy_available": self.numpy_available,
            "numpy_version": self.numpy_version,
            "torch_available": self.torch_available,
            "torch_version": self.torch_version,
            "cuda_available": self.cuda_available,
            "encoder_registry_id": self.encoder_registry_id,
            "schema_fingerprint": self.schema_fingerprint,
            "tower_fingerprint": self.tower_fingerprint,
            "max_tower_depth": self.max_tower_depth,
            "max_action_count": self.max_action_count,
            "conversion_count": self.conversion_count,
            "conversion_elapsed_seconds": self.conversion_elapsed_seconds,
            "debug_record_exported": self.debug_record_exported,
            "metadata": _json_safe(self.metadata),
        }


@dataclass(slots=True)
class EncodingRegistry:
    """Stable numeric vocabulary for tower, fiber, and training identities."""

    state_id_by_state: dict[State, int] = field(default_factory=dict)
    edge_id_by_edge: dict[BaseEdge, int] = field(default_factory=dict)
    action_id_by_identity: dict[object, int] = field(default_factory=dict)
    state_cell_id_by_cell: dict[StateCellId, int] = field(default_factory=dict)
    action_collection_id_by_collection: dict[ActionCollectionId, int] = field(
        default_factory=dict
    )
    action_cell_id_by_cell: dict[ActionCellId, int] = field(default_factory=dict)
    tier_id_by_tier: dict[int, int] = field(default_factory=dict)
    stage_id_by_identity: dict[str, int] = field(default_factory=dict)
    fiber_id_by_identity: dict[str, int] = field(default_factory=dict)
    frozen_behavior_id_by_identity: dict[str, int] = field(default_factory=dict)
    departure_reason_id_by_reason: dict[FiberDepartureReason, int] = field(
        default_factory=dict
    )
    label_id_by_namespace_and_value: dict[tuple[str, str], int] = field(
        default_factory=dict
    )

    @classmethod
    def from_tower(cls, tower: PartitionTower) -> EncodingRegistry:
        """Build a registry from a partition tower without RL-specific objects."""

        registry = cls()
        for state, state_id in tower.registry.state_id_by_state.items():
            registry.state_id_by_state[state] = state_id.value
        for edge, edge_id in tower.registry.edge_id_by_edge.items():
            registry.edge_id_by_edge[edge] = edge_id.value
        for identity, action_id in tower.registry.action_id_by_identity.items():
            registry.action_id_by_identity[identity] = action_id.value
        for tier in range(len(tower.state_layers)):
            registry.tier_id_by_tier[tier] = tier
        for state_layer in tower.state_layers:
            for state_cell_id in state_layer.all_cell_ids():
                registry.state_cell_id_by_cell[state_cell_id] = _cell_numeric_id(
                    state_cell_id
                )
        for action_layer in tower.action_layers:
            for collection_id in action_layer.edge_ids_by_collection:
                registry.action_collection_id_by_collection[collection_id] = (
                    _cell_numeric_id(collection_id)
                )
            for action_cell_id in action_layer.edge_ids_by_action_cell:
                registry.action_cell_id_by_cell[action_cell_id] = _cell_numeric_id(
                    action_cell_id
                )
        for reason in FiberDepartureReason:
            registry.departure_reason_id_by_reason[reason] = len(
                registry.departure_reason_id_by_reason
            )
        return registry

    @property
    def registry_id(self) -> str:
        """Return a deterministic fingerprint for the current vocabulary."""

        return _fingerprint(self.summary())

    def encode_state(self, state: object | None) -> int | None:
        """Return the numeric id for a base state if known."""

        if state is None:
            return None
        if isinstance(state, State):
            return self.state_id_by_state.get(state)
        return None

    def encode_edge(self, edge: object | None) -> int | None:
        """Return the numeric id for a base edge if known."""

        if edge is None:
            return None
        if isinstance(edge, BaseEdge):
            return self.edge_id_by_edge.get(edge)
        return None

    def encode_state_cell(self, cell: object | None) -> int | None:
        """Return the numeric id for a state cell if known."""

        if cell is None:
            return None
        if isinstance(cell, StateCellId):
            return self.state_cell_id_by_cell.get(cell, _cell_numeric_id(cell))
        return None

    def encode_action_collection(self, collection: object | None) -> int | None:
        """Return the numeric id for an action collection if known."""

        if collection is None:
            return None
        if isinstance(collection, ActionCollectionId):
            return self.action_collection_id_by_collection.get(
                collection,
                _cell_numeric_id(collection),
            )
        return None

    def encode_action_cell(self, cell: object | None) -> int | None:
        """Return the numeric id for an action cell if known."""

        if cell is None:
            return None
        if isinstance(cell, ActionCellId):
            return self.action_cell_id_by_cell.get(cell, _cell_numeric_id(cell))
        return None

    def encode_tier(self, tier: int | None) -> int | None:
        """Return a stable id for a tower tier."""

        if tier is None:
            return None
        existing = self.tier_id_by_tier.get(tier)
        if existing is not None:
            return existing
        self.tier_id_by_tier[tier] = tier
        return tier

    def encode_stage_context(
        self,
        stage_context: FiberStageContext | None,
    ) -> tuple[int | None, int | None, int | None]:
        """Encode stage, fiber, and frozen-behavior identities."""

        if stage_context is None:
            return None, None, None
        stage_id = self._encode_text(
            self.stage_id_by_identity,
            stage_context.stage_id,
        )
        fiber_id = self._encode_text(
            self.fiber_id_by_identity,
            stage_context.fiber_id,
        )
        frozen_behavior_id = self._encode_text(
            self.frozen_behavior_id_by_identity,
            stage_context.frozen_behavior_id,
        )
        self.encode_tier(stage_context.fine_tier)
        self.encode_tier(stage_context.coarse_tier)
        return stage_id, fiber_id, frozen_behavior_id

    def encode_departure_reason(
        self,
        departure: FiberDeparture | None,
    ) -> int | None:
        """Encode a fiber-departure reason."""

        if departure is None:
            return None
        existing = self.departure_reason_id_by_reason.get(departure.reason)
        if existing is not None:
            return existing
        next_id = len(self.departure_reason_id_by_reason)
        self.departure_reason_id_by_reason[departure.reason] = next_id
        return next_id

    def encode_label(self, namespace: str, value: object | None) -> int | None:
        """Encode a small metadata label in a caller-provided namespace."""

        if value is None:
            return None
        key = (namespace, str(value))
        existing = self.label_id_by_namespace_and_value.get(key)
        if existing is not None:
            return existing
        next_id = len(self.label_id_by_namespace_and_value)
        self.label_id_by_namespace_and_value[key] = next_id
        return next_id

    def summary(self) -> JsonDict:
        """Return a serializable vocabulary summary."""

        return {
            "state_ids": sorted(self.state_id_by_state.values()),
            "edge_ids": sorted(self.edge_id_by_edge.values()),
            "action_ids": sorted(self.action_id_by_identity.values()),
            "state_cell_ids": sorted(
                _cell_key(cell) for cell in self.state_cell_id_by_cell
            ),
            "action_collection_ids": sorted(
                _cell_key(collection)
                for collection in self.action_collection_id_by_collection
            ),
            "action_cell_ids": sorted(
                _cell_key(cell) for cell in self.action_cell_id_by_cell
            ),
            "tier_ids": sorted(self.tier_id_by_tier.values()),
            "stage_ids": dict(sorted(self.stage_id_by_identity.items())),
            "fiber_ids": dict(sorted(self.fiber_id_by_identity.items())),
            "frozen_behavior_ids": dict(
                sorted(self.frozen_behavior_id_by_identity.items())
            ),
            "departure_reason_ids": {
                reason.value: reason_id
                for reason, reason_id in sorted(
                    self.departure_reason_id_by_reason.items(),
                    key=lambda item: item[0].value,
                )
            },
            "label_ids": {
                f"{namespace}:{value}": label_id
                for (namespace, value), label_id in sorted(
                    self.label_id_by_namespace_and_value.items()
                )
            },
        }

    def to_dict(self) -> JsonDict:
        """Return a JSON-safe dictionary."""

        return {
            "registry_id": self.registry_id,
            "summary": self.summary(),
        }

    def _encode_text(self, table: dict[str, int], value: str) -> int:
        existing = table.get(value)
        if existing is not None:
            return existing
        next_id = len(table)
        table[value] = next_id
        return next_id


@dataclass(frozen=True, slots=True)
class LinearizedActionSelectionInput:
    """Backend-independent numeric record for action selection."""

    observation_features: tuple[float, ...]
    current_base_state_id: int | None
    tower_position_ids: tuple[int | None, ...]
    tower_depth: int
    active_tier: int | None
    fine_tier: int | None
    coarse_tier: int | None
    action_mask: tuple[bool, ...]
    action_count: int
    stage_id: int | None
    fiber_id: int | None
    frozen_behavior_id: int | None
    frozen_behavior_version: int | str | None
    fiber_departure_reason_id: int | None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def to_dict(self) -> JsonDict:
        """Return a JSON-safe dictionary."""

        return {
            "observation_features": list(self.observation_features),
            "current_base_state_id": self.current_base_state_id,
            "tower_position_ids": list(self.tower_position_ids),
            "tower_depth": self.tower_depth,
            "active_tier": self.active_tier,
            "fine_tier": self.fine_tier,
            "coarse_tier": self.coarse_tier,
            "action_mask": list(self.action_mask),
            "action_count": self.action_count,
            "stage_id": self.stage_id,
            "fiber_id": self.fiber_id,
            "frozen_behavior_id": self.frozen_behavior_id,
            "frozen_behavior_version": self.frozen_behavior_version,
            "fiber_departure_reason_id": self.fiber_departure_reason_id,
            "metadata": _json_safe(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class LinearizedTrainingTransition:
    """Backend-independent numeric record for one training transition."""

    source: LinearizedActionSelectionInput
    target: LinearizedActionSelectionInput
    chosen_action: int
    reward: float
    terminated: bool
    truncated: bool
    bootstrap_allowed: bool
    bootstrap_reason_id: int | None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def to_dict(self) -> JsonDict:
        """Return a JSON-safe dictionary."""

        return {
            "source": self.source.to_dict(),
            "target": self.target.to_dict(),
            "chosen_action": self.chosen_action,
            "reward": self.reward,
            "terminated": self.terminated,
            "truncated": self.truncated,
            "bootstrap_allowed": self.bootstrap_allowed,
            "bootstrap_reason_id": self.bootstrap_reason_id,
            "metadata": _json_safe(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class ConversionTiming:
    """Small explicit conversion timing payload."""

    conversion_count: int
    conversion_elapsed_seconds: float

    def to_dict(self) -> JsonDict:
        """Return a JSON-safe dictionary."""

        return {
            "conversion_count": self.conversion_count,
            "conversion_elapsed_seconds": self.conversion_elapsed_seconds,
        }


def numpy_availability() -> BackendAvailability:
    """Return NumPy availability without requiring NumPy at module import time."""

    if importlib.util.find_spec("numpy") is None:
        return BackendAvailability(available=False)
    return BackendAvailability(
        available=True,
        version=_optional_package_version("numpy"),
    )


def torch_availability(*, check_cuda: bool = False) -> BackendAvailability:
    """Return Torch availability without requiring Torch at module import time."""

    if importlib.util.find_spec("torch") is None:
        return BackendAvailability(available=False)
    cuda_available = False
    if check_cuda:
        try:
            torch_module = importlib.import_module("torch")
        except Exception:
            cuda_available = False
        else:
            cuda_available = bool(torch_module.cuda.is_available())
    return BackendAvailability(
        available=True,
        version=_optional_package_version("torch"),
        cuda_available=cuda_available,
    )


def build_linearization_report(
    *,
    config: LinearizationConfig,
    registry: EncodingRegistry | None = None,
    tower: PartitionTower | None = None,
    conversion_count: int = 0,
    conversion_elapsed_seconds: float = 0.0,
    debug_record_exported: bool = False,
    metadata: Mapping[str, object] | None = None,
) -> LinearizationReport:
    """Build the manifest/report fragment for one tensorization boundary."""

    numpy_status = numpy_availability()
    torch_status = torch_availability(
        check_cuda=config.device_kind == TensorDeviceKind.CUDA
    )
    backend_available = _backend_available(config, numpy_status, torch_status)
    effective_registry = registry
    if effective_registry is None and tower is not None:
        effective_registry = EncodingRegistry.from_tower(tower)
    tower_fingerprint = None
    schema_fingerprint = None
    if tower is not None:
        tower_fingerprint = (
            effective_registry.registry_id if effective_registry is not None else None
        )
        schema_fingerprint = _fingerprint({"schema": repr(tower.schema)})
    return LinearizationReport(
        linearization_state=config.linearization_state,
        numeric_backend=config.numeric_backend,
        device_kind=config.device_kind,
        benchmark_label=config.derived_benchmark_label,
        backend_available=backend_available,
        enabled=config.enabled and backend_available,
        dtype=config.dtype,
        mask_dtype=config.mask_dtype,
        numpy_available=numpy_status.available,
        numpy_version=numpy_status.version,
        torch_available=torch_status.available,
        torch_version=torch_status.version,
        cuda_available=torch_status.cuda_available,
        encoder_registry_id=(
            config.encoder_registry_id
            if config.encoder_registry_id is not None
            else None
            if effective_registry is None
            else effective_registry.registry_id
        ),
        schema_fingerprint=schema_fingerprint,
        tower_fingerprint=tower_fingerprint,
        max_tower_depth=config.max_tower_depth,
        max_action_count=config.max_action_count,
        conversion_count=conversion_count,
        conversion_elapsed_seconds=conversion_elapsed_seconds,
        debug_record_exported=debug_record_exported,
        metadata={} if metadata is None else dict(metadata),
    )


def time_conversions(
    conversions: Iterable[object],
) -> tuple[tuple[object, ...], ConversionTiming]:
    """Materialize explicit conversions and return count/timing metadata."""

    started = time.perf_counter()
    materialized = tuple(conversions)
    elapsed = time.perf_counter() - started
    return materialized, ConversionTiming(
        conversion_count=len(materialized),
        conversion_elapsed_seconds=elapsed,
    )


def linearize_action_selection_input(
    action_input: ActionSelectionInput,
    *,
    config: LinearizationConfig,
    registry: EncodingRegistry,
) -> LinearizedActionSelectionInput:
    """Convert one semantic action-selection input into a numeric record."""

    if config.linearization_state == LinearizationState.ABSENT:
        raise ValueError("Cannot linearize with LinearizationState.ABSENT.")

    observation_features, observation_metadata = _linearize_observation(
        action_input.observation,
        strict=config.strict,
    )
    action_vocabulary = _action_vocabulary_from_input(action_input)
    action_mask, action_count = _normalize_action_mask(
        action_input.action_mask,
        max_action_count=config.max_action_count,
        inferred_action_count=len(action_vocabulary) if action_vocabulary else None,
        strict=config.strict,
    )
    current_base_state_id = registry.encode_state(action_input.current_base_state)
    if (
        config.strict
        and action_input.current_base_state is not None
        and current_base_state_id is None
    ):
        raise ValueError("Current base state is not present in the encoding registry.")

    tower_position_ids = tuple(
        _require_encoded(
            registry.encode_state_cell(position),
            value_name="tower position",
            value=position,
            strict=config.strict,
        )
        for position in action_input.runtime_snapshot.current_position_at_every_tier
    )
    tower_position_ids = _pad_tower_positions(
        tower_position_ids,
        max_tower_depth=config.max_tower_depth,
        strict=config.strict,
    )
    stage_id, fiber_id, frozen_behavior_id = registry.encode_stage_context(
        action_input.stage_context
    )
    fiber_departure_reason_id = registry.encode_departure_reason(
        action_input.fiber_departure
    )
    metadata = _linearized_input_metadata(
        action_input=action_input,
        action_vocabulary=action_vocabulary,
        registry=registry,
        observation_metadata=observation_metadata,
        include_diagnostics=config.include_diagnostics,
    )
    stage_context = action_input.stage_context
    return LinearizedActionSelectionInput(
        observation_features=observation_features,
        current_base_state_id=current_base_state_id,
        tower_position_ids=tower_position_ids,
        tower_depth=len(action_input.runtime_snapshot.current_position_at_every_tier),
        active_tier=action_input.runtime_snapshot.active_control_tier,
        fine_tier=None if stage_context is None else stage_context.fine_tier,
        coarse_tier=None if stage_context is None else stage_context.coarse_tier,
        action_mask=action_mask,
        action_count=action_count,
        stage_id=stage_id,
        fiber_id=fiber_id,
        frozen_behavior_id=frozen_behavior_id,
        frozen_behavior_version=(
            None if stage_context is None else stage_context.frozen_behavior_version
        ),
        fiber_departure_reason_id=fiber_departure_reason_id,
        metadata=metadata,
    )


def linearize_training_transition(
    transition: TrainingTransition,
    *,
    config: LinearizationConfig,
    registry: EncodingRegistry,
) -> LinearizedTrainingTransition:
    """Convert one semantic training transition into a numeric record."""

    source = linearize_action_selection_input(
        transition.source_input,
        config=config,
        registry=registry,
    )
    target = linearize_action_selection_input(
        transition.target_input,
        config=config,
        registry=registry,
    )
    chosen_action = _resolve_chosen_action_index(
        transition.chosen_action,
        transition.source_input,
        strict=config.strict,
    )
    metadata: dict[str, object] = {}
    if config.include_diagnostics:
        metadata["diagnostics"] = _json_safe(transition.diagnostics)
    if transition.stage_context is not None:
        metadata["stage_context"] = _json_safe(
            {
                "stage_id": transition.stage_context.stage_id,
                "fiber_id": transition.stage_context.fiber_id,
                "fine_tier": transition.stage_context.fine_tier,
                "coarse_tier": transition.stage_context.coarse_tier,
                "frozen_behavior_id": transition.stage_context.frozen_behavior_id,
                "frozen_behavior_version": (
                    transition.stage_context.frozen_behavior_version
                ),
            }
        )
    return LinearizedTrainingTransition(
        source=source,
        target=target,
        chosen_action=chosen_action,
        reward=float(transition.reward),
        terminated=transition.terminated,
        truncated=transition.truncated,
        bootstrap_allowed=transition.bootstrap_allowed,
        bootstrap_reason_id=registry.encode_label(
            "bootstrap_reason",
            transition.bootstrap_reason,
        ),
        metadata=metadata,
    )


def export_linearized_record(record: object) -> JsonDict:
    """Return a JSON-safe debug payload for an explicitly selected record."""

    if hasattr(record, "to_dict"):
        value = record.to_dict()
        if isinstance(value, dict):
            return {"record": _json_safe(value)}
    return {"record": _json_safe(record)}


def _validate_config(config: LinearizationConfig) -> None:
    if config.linearization_state == LinearizationState.ABSENT:
        if config.numeric_backend != NumericBackend.NONE:
            raise ValueError("ABSENT linearization requires NumericBackend.NONE.")
        if config.device_kind != TensorDeviceKind.NONE:
            raise ValueError("ABSENT linearization requires TensorDeviceKind.NONE.")
    if (
        config.numeric_backend == NumericBackend.NONE
        and config.device_kind != TensorDeviceKind.NONE
    ):
        raise ValueError("NumericBackend.NONE requires TensorDeviceKind.NONE.")
    if (
        config.device_kind == TensorDeviceKind.CUDA
        and config.numeric_backend != NumericBackend.TORCH
    ):
        raise ValueError("CUDA device kind requires NumericBackend.TORCH.")
    if (
        config.linearization_state == LinearizationState.PRESENT_ENABLED
        and config.numeric_backend == NumericBackend.NONE
    ):
        raise ValueError("PRESENT_ENABLED requires a numeric backend.")
    if config.max_tower_depth is not None and config.max_tower_depth < 0:
        raise ValueError("max_tower_depth must be nonnegative.")
    if config.max_action_count is not None and config.max_action_count < 0:
        raise ValueError("max_action_count must be nonnegative.")
    if config.sequence_length is not None and config.sequence_length < 0:
        raise ValueError("sequence_length must be nonnegative.")


def _backend_available(
    config: LinearizationConfig,
    numpy_status: BackendAvailability,
    torch_status: BackendAvailability,
) -> bool:
    if config.numeric_backend == NumericBackend.NONE:
        return True
    if config.numeric_backend == NumericBackend.NUMPY:
        return numpy_status.available
    if config.numeric_backend == NumericBackend.TORCH:
        if not torch_status.available:
            return False
        if config.device_kind == TensorDeviceKind.CUDA:
            return torch_status.cuda_available
        return True
    return False


def _normalize_action_mask(
    action_mask: tuple[bool, ...] | None,
    *,
    max_action_count: int | None,
    inferred_action_count: int | None,
    strict: bool,
) -> tuple[tuple[bool, ...], int]:
    if action_mask is None:
        action_count = (
            max_action_count
            if max_action_count is not None
            else inferred_action_count
        )
        if action_count is None:
            if strict:
                raise ValueError("Cannot infer action count for missing action mask.")
            return (), 0
        return tuple(True for _ in range(action_count)), action_count

    raw_mask = tuple(bool(item) for item in action_mask)
    target_count = max_action_count if max_action_count is not None else len(raw_mask)
    if len(raw_mask) > target_count:
        if strict:
            raise ValueError("Action mask is longer than max_action_count.")
        return raw_mask[:target_count], target_count
    if len(raw_mask) < target_count:
        raw_mask = raw_mask + tuple(False for _ in range(target_count - len(raw_mask)))
    return raw_mask, target_count


def _pad_tower_positions(
    tower_position_ids: tuple[int | None, ...],
    *,
    max_tower_depth: int | None,
    strict: bool,
) -> tuple[int | None, ...]:
    if max_tower_depth is None:
        return tower_position_ids
    if len(tower_position_ids) > max_tower_depth:
        if strict:
            raise ValueError("Tower position is deeper than max_tower_depth.")
        return tower_position_ids[:max_tower_depth]
    if len(tower_position_ids) < max_tower_depth:
        return tower_position_ids + tuple(
            None for _ in range(max_tower_depth - len(tower_position_ids))
        )
    return tower_position_ids


def _linearize_observation(
    observation: object,
    *,
    strict: bool,
) -> tuple[tuple[float, ...], JsonDict]:
    if isinstance(observation, bool):
        return (1.0 if observation else 0.0,), {}
    if isinstance(observation, int | float):
        return (float(observation),), {}
    if isinstance(observation, tuple | list):
        features: list[float] = []
        for item in observation:
            if isinstance(item, bool):
                features.append(1.0 if item else 0.0)
            elif isinstance(item, int | float):
                features.append(float(item))
            else:
                if strict:
                    raise ValueError("Observation sequence contains non-numeric data.")
                return (), {"unsupported_observation_repr": repr(observation)}
        return tuple(features), {}
    if strict:
        raise ValueError("Unsupported observation type for first-scope linearization.")
    return (), {"unsupported_observation_repr": repr(observation)}


def _action_vocabulary_from_input(
    action_input: ActionSelectionInput,
) -> tuple[object, ...]:
    vocabulary = action_input.diagnostics.get("fiber_action_vocabulary")
    if isinstance(vocabulary, tuple):
        return vocabulary
    if isinstance(vocabulary, list):
        return tuple(vocabulary)
    return ()


def _linearized_input_metadata(
    *,
    action_input: ActionSelectionInput,
    action_vocabulary: tuple[object, ...],
    registry: EncodingRegistry,
    observation_metadata: Mapping[str, object],
    include_diagnostics: bool,
) -> JsonDict:
    metadata: JsonDict = {}
    if observation_metadata:
        metadata["observation"] = _json_safe(observation_metadata)
    if action_vocabulary:
        metadata["action_vocabulary_ids"] = [
            registry.encode_action_cell(action_cell)
            for action_cell in action_vocabulary
        ]
        metadata["action_vocabulary"] = _json_safe(action_vocabulary)
    if include_diagnostics:
        metadata["diagnostics"] = _json_safe(action_input.diagnostics)
    return metadata


def _resolve_chosen_action_index(
    chosen_action: object,
    source_input: ActionSelectionInput,
    *,
    strict: bool,
) -> int:
    if type(chosen_action) is int:
        return chosen_action
    action_vocabulary = _action_vocabulary_from_input(source_input)
    for index, action_cell in enumerate(action_vocabulary):
        if chosen_action == action_cell:
            return index
    if strict:
        raise ValueError("Chosen action is not a first-scope integer action index.")
    return -1


def _require_encoded(
    encoded: int | None,
    *,
    value_name: str,
    value: object,
    strict: bool,
) -> int | None:
    if encoded is None and value is not None and strict:
        raise ValueError(f"Could not encode {value_name}.")
    return encoded


def _optional_package_version(package_name: str) -> str | None:
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value)
    raise TypeError("Expected an int-compatible value.")


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _cell_key(cell: StateCellId | ActionCollectionId | ActionCellId) -> tuple[int, int]:
    return (cell.tier, cell.ordinal)


def _cell_numeric_id(cell: StateCellId | ActionCollectionId | ActionCellId) -> int:
    return cell.tier * 1_000_000 + cell.ordinal


def _fingerprint(value: object) -> str:
    encoded = json.dumps(_json_safe(value), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _json_safe(value: object) -> object:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, StateId | EdgeId | ActionId):
        return value.value
    if isinstance(value, StateCellId | ActionCollectionId | ActionCellId):
        return {"tier": value.tier, "ordinal": value.ordinal}
    if isinstance(value, tuple | list):
        return [_json_safe(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    return {"repr": repr(value)}


__all__ = [
    "BackendAvailability",
    "ConversionTiming",
    "EncodingRegistry",
    "LinearizationConfig",
    "LinearizationReport",
    "LinearizationState",
    "LinearizedActionSelectionInput",
    "LinearizedTrainingTransition",
    "NumericBackend",
    "TensorDeviceKind",
    "build_linearization_report",
    "export_linearized_record",
    "linearize_action_selection_input",
    "linearize_training_transition",
    "numpy_availability",
    "time_conversions",
    "torch_availability",
]
