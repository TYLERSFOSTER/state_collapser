"""Loop/internal-edge policy for partition-tower navigation.

Loop policy is explicit because contracted internal edges are not lost; they are
recorded as internal action data and can later support aggregation or stutter
semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from state_collapser.tower.partition.ids import EdgeId, StateCellId


class LoopPolicyName(StrEnum):
    """Supported conventions for edges that become internal to a state cell."""

    DROP_INTERNAL = "drop_internal"
    AGGREGATE_INTERNAL = "aggregate_internal"
    FORMAL_STUTTER = "formal_stutter"


@dataclass(frozen=True, slots=True)
class LoopPolicy:
    """Configuration for handling edges that become internal after contraction."""

    name: LoopPolicyName = LoopPolicyName.DROP_INTERNAL

    @classmethod
    def drop_internal(cls) -> LoopPolicy:
        """Use internal edges only as diagnostics, not as live actions."""

        return cls(LoopPolicyName.DROP_INTERNAL)

    @classmethod
    def aggregate_internal(cls) -> LoopPolicy:
        """Record internal edges so residual reward/value aggregation can use them."""

        return cls(LoopPolicyName.AGGREGATE_INTERNAL)

    @classmethod
    def formal_stutter(cls) -> LoopPolicy:
        """Record internal edges as formal stutter/self-loop structure."""

        return cls(LoopPolicyName.FORMAL_STUTTER)


@dataclass(frozen=True, slots=True)
class InternalEdgeRecord:
    """Record that a base edge became internal to a state cell at a tier."""

    edge_id: EdgeId
    tier: int
    state_cell_id: StateCellId
    policy_name: LoopPolicyName
    reward_contributor: float | None = None


def record_internal_edge(
    *,
    edge_id: EdgeId,
    tier: int,
    state_cell_id: StateCellId,
    loop_policy: LoopPolicy,
    reward_contributor: float | None = None,
) -> InternalEdgeRecord:
    """Create an internal-edge record under the selected loop policy."""

    return InternalEdgeRecord(
        edge_id=edge_id,
        tier=tier,
        state_cell_id=state_cell_id,
        policy_name=loop_policy.name,
        reward_contributor=reward_contributor,
    )


__all__ = [
    "InternalEdgeRecord",
    "LoopPolicy",
    "LoopPolicyName",
    "record_internal_edge",
]
