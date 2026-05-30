"""Optional Torch conversion boundary for linearized training records.

This module is intentionally downstream of `training.linearization`: it accepts
backend-independent numeric records and turns them into Torch tensors only when
the optional `ml` dependency is installed. Importing the package's training
surfaces should not require Torch.
"""

from __future__ import annotations

import importlib
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any, cast

from .decisions import ActionDecision
from .linearization import (
    LinearizationConfig,
    LinearizedActionSelectionInput,
    LinearizedTrainingTransition,
    TensorDeviceKind,
)


@dataclass(frozen=True, slots=True)
class TorchDecisionBatch:
    """Torch tensor batch for action-selection records.

    The batch owns tensor layout only, not model policy semantics. Ragged fields
    are padded at this boundary, with `-1` used for absent ids and `False` used
    for padded action-mask positions.
    """

    observations: object
    tower_positions: object
    tower_depth: object
    active_tier: object
    action_mask: object
    stage_features: object
    metadata: tuple[object, ...] = field(default_factory=tuple)

    @classmethod
    def from_linearized(
        cls,
        records: Sequence[LinearizedActionSelectionInput],
        *,
        config: LinearizationConfig,
    ) -> TorchDecisionBatch:
        """Convert backend-independent decision records into Torch tensors.

        The conversion uses the device and dtype described by
        `LinearizationConfig`; it does not inspect or mutate the semantic tower
        runtime. Empty batches produce width-zero tensors for fields whose width
        is inferred from records.
        """

        torch_module = _require_torch()
        device = _torch_device(torch_module, config)
        float_dtype = _torch_dtype(torch_module, config.dtype)

        observation_width = max((len(record.observation_features) for record in records), default=0)
        tower_width = max((len(record.tower_position_ids) for record in records), default=0)
        action_width = max((len(record.action_mask) for record in records), default=0)

        observations = torch_module.tensor(
            [
                _pad_float_tuple(record.observation_features, observation_width)
                for record in records
            ],
            dtype=float_dtype,
            device=device,
        )
        tower_positions = torch_module.tensor(
            [
                _pad_optional_int_tuple(record.tower_position_ids, tower_width)
                for record in records
            ],
            dtype=torch_module.long,
            device=device,
        )
        tower_depth = torch_module.tensor(
            [record.tower_depth for record in records],
            dtype=torch_module.long,
            device=device,
        )
        active_tier = torch_module.tensor(
            [_optional_int_value(record.active_tier) for record in records],
            dtype=torch_module.long,
            device=device,
        )
        action_mask = torch_module.tensor(
            [_pad_bool_tuple(record.action_mask, action_width) for record in records],
            dtype=torch_module.bool,
            device=device,
        )
        stage_features = torch_module.tensor(
            [
                (
                    _optional_int_value(record.stage_id),
                    _optional_int_value(record.fiber_id),
                    _optional_int_value(record.frozen_behavior_id),
                    _optional_int_value(record.fiber_departure_reason_id),
                    _optional_int_value(record.fine_tier),
                    _optional_int_value(record.coarse_tier),
                )
                for record in records
            ],
            dtype=torch_module.long,
            device=device,
        )
        return cls(
            observations=observations,
            tower_positions=tower_positions,
            tower_depth=tower_depth,
            active_tier=active_tier,
            action_mask=action_mask,
            stage_features=stage_features,
            metadata=tuple(record.metadata for record in records),
        )


@dataclass(frozen=True, slots=True)
class TorchTransitionBatch:
    """Torch tensor batch for source-target transition records.

    This is the first neural-learner-facing container in the package. It keeps
    source and target decision batches explicit so actor-critic, Q-learning, and
    supervised smoke models can choose their own update logic without changing
    the package-owned transition schema.
    """

    source: TorchDecisionBatch
    target: TorchDecisionBatch
    actions: object
    rewards: object
    terminated: object
    truncated: object
    bootstrap_allowed: object
    metadata: tuple[object, ...] = field(default_factory=tuple)

    @classmethod
    def from_linearized(
        cls,
        records: Sequence[LinearizedTrainingTransition],
        *,
        config: LinearizationConfig,
    ) -> TorchTransitionBatch:
        """Convert backend-independent transitions into Torch tensor batches."""

        torch_module = _require_torch()
        device = _torch_device(torch_module, config)
        float_dtype = _torch_dtype(torch_module, config.dtype)
        source = TorchDecisionBatch.from_linearized(
            [record.source for record in records],
            config=config,
        )
        target = TorchDecisionBatch.from_linearized(
            [record.target for record in records],
            config=config,
        )
        return cls(
            source=source,
            target=target,
            actions=torch_module.tensor(
                [record.chosen_action for record in records],
                dtype=torch_module.long,
                device=device,
            ),
            rewards=torch_module.tensor(
                [record.reward for record in records],
                dtype=float_dtype,
                device=device,
            ),
            terminated=torch_module.tensor(
                [record.terminated for record in records],
                dtype=torch_module.bool,
                device=device,
            ),
            truncated=torch_module.tensor(
                [record.truncated for record in records],
                dtype=torch_module.bool,
                device=device,
            ),
            bootstrap_allowed=torch_module.tensor(
                [record.bootstrap_allowed for record in records],
                dtype=torch_module.bool,
                device=device,
            ),
            metadata=tuple(record.metadata for record in records),
        )


def action_decision_from_logits(
    logits: object,
    batch: TorchDecisionBatch,
    *,
    row: int = 0,
) -> ActionDecision:
    """Build an `ActionDecision` from one row of masked Torch logits.

    Invalid actions are masked to negative infinity before argmax selection.
    The returned decision remains package-native so callers can plug a toy Torch
    model into existing collector/reference-loop surfaces without adopting a
    package-owned policy architecture.
    """

    torch_module = _require_torch()
    tensor_logits = cast(Any, logits)
    batch_action_mask = cast(Any, batch.action_mask)
    if not hasattr(tensor_logits, "dim"):
        raise TypeError("logits must be a Torch tensor-like object.")
    row_logits = tensor_logits[row] if tensor_logits.dim() == 2 else tensor_logits
    row_mask = (
        batch_action_mask[row]
        if batch_action_mask.dim() == 2
        else batch_action_mask
    )
    if row_logits.numel() != row_mask.numel():
        raise ValueError("Logit count must match action-mask width.")
    if not bool(row_mask.any().item()):
        raise ValueError("Cannot choose an action from an all-false mask.")
    masked_logits = row_logits.masked_fill(~row_mask, float("-inf"))
    chosen_action = int(torch_module.argmax(masked_logits).item())
    return ActionDecision(
        chosen_action=chosen_action,
        action_logits={
            index: float(value)
            for index, value in enumerate(row_logits.detach().cpu().tolist())
        },
        diagnostics={"tensor_action_mask": row_mask.detach().cpu().tolist()},
    )


def _require_torch() -> Any:
    try:
        return importlib.import_module("torch")
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Torch conversion requires the 'ml' extra, for example: "
            "pip install -e '.[ml]'."
        ) from exc


def _torch_device(torch_module: Any, config: LinearizationConfig) -> object:
    if config.device_kind == TensorDeviceKind.CUDA:
        if not bool(torch_module.cuda.is_available()):
            raise RuntimeError("CUDA device requested but torch.cuda.is_available() is false.")
        return torch_module.device("cuda")
    return torch_module.device("cpu")


def _torch_dtype(torch_module: Any, dtype: str | None) -> object:
    if dtype is None:
        return torch_module.float32
    if not hasattr(torch_module, dtype):
        raise ValueError(f"Unsupported Torch dtype: {dtype}")
    return getattr(torch_module, dtype)


def _pad_float_tuple(values: tuple[float, ...], width: int) -> tuple[float, ...]:
    if len(values) >= width:
        return values
    return values + tuple(0.0 for _ in range(width - len(values)))


def _pad_optional_int_tuple(
    values: tuple[int | None, ...],
    width: int,
) -> tuple[int, ...]:
    encoded = tuple(_optional_int_value(value) for value in values)
    if len(encoded) >= width:
        return encoded
    return encoded + tuple(-1 for _ in range(width - len(encoded)))


def _pad_bool_tuple(values: tuple[bool, ...], width: int) -> tuple[bool, ...]:
    if len(values) >= width:
        return values
    return values + tuple(False for _ in range(width - len(values)))


def _optional_int_value(value: int | None) -> int:
    return -1 if value is None else value


__all__ = [
    "TorchDecisionBatch",
    "TorchTransitionBatch",
    "action_decision_from_logits",
]
