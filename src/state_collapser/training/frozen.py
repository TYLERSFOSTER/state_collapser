"""Frozen coarse-quotient behavior surfaces for fiber-conditioned training."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class FrozenQuotientStep:
    """One concrete coarse-tier decision treated as frozen while training upstairs."""

    coarse_tier: int
    source_cell: object
    action_cell: object | None = None
    target_cell: object | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", dict(self.metadata))


@dataclass(frozen=True, slots=True)
class FrozenQuotientBehavior:
    """Coarse quotient behavior held fixed while a finer stage is trained."""

    behavior_id: str
    coarse_tier: int
    supported_fine_tier: int
    tower_fingerprint: str | None = None
    schema_fingerprint: str | None = None
    decision_surface: object | None = None
    current_step: FrozenQuotientStep | None = None
    path_prefix: tuple[object, ...] = ()
    action_prefix: tuple[object, ...] = ()
    version: int | str = 0
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.coarse_tier != self.supported_fine_tier + 1:
            raise ValueError(
                "FrozenQuotientBehavior first-scope use requires "
                "coarse_tier == supported_fine_tier + 1."
            )
        if self.current_step is not None and self.current_step.coarse_tier != self.coarse_tier:
            raise ValueError(
                "FrozenQuotientBehavior.current_step.coarse_tier must match "
                "FrozenQuotientBehavior.coarse_tier."
            )
        object.__setattr__(self, "path_prefix", tuple(self.path_prefix))
        object.__setattr__(self, "action_prefix", tuple(self.action_prefix))
        object.__setattr__(self, "metadata", dict(self.metadata))

    @classmethod
    def from_step(
        cls,
        *,
        behavior_id: str,
        coarse_tier: int,
        supported_fine_tier: int,
        source_cell: object,
        action_cell: object | None = None,
        target_cell: object | None = None,
        tower_fingerprint: str | None = None,
        schema_fingerprint: str | None = None,
        version: int | str = 0,
        metadata: Mapping[str, object] | None = None,
        step_metadata: Mapping[str, object] | None = None,
    ) -> FrozenQuotientBehavior:
        """Build a frozen behavior from one explicit coarse quotient step."""

        step = FrozenQuotientStep(
            coarse_tier=coarse_tier,
            source_cell=source_cell,
            action_cell=action_cell,
            target_cell=target_cell,
            metadata={} if step_metadata is None else step_metadata,
        )
        return cls(
            behavior_id=behavior_id,
            coarse_tier=coarse_tier,
            supported_fine_tier=supported_fine_tier,
            tower_fingerprint=tower_fingerprint,
            schema_fingerprint=schema_fingerprint,
            current_step=step,
            path_prefix=(source_cell, target_cell) if target_cell is not None else (source_cell,),
            action_prefix=() if action_cell is None else (action_cell,),
            version=version,
            metadata={} if metadata is None else metadata,
        )


__all__ = [
    "FrozenQuotientBehavior",
    "FrozenQuotientStep",
]
