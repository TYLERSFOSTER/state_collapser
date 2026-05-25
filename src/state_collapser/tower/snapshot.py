"""Runtime view and value-snapshot contract surfaces."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from state_collapser.core.rewards import PathRewardSummary, QuotientRewardSummary, StepReward
from state_collapser.graph.explored_graph import ExploredGraph
from state_collapser.graph.vista_graph import VistaGraph
from state_collapser.quotient.tier_view import QuotientTierView

JsonDict = dict[str, object]


def _json_safe(value: object) -> object:
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, tuple | list):
        return [_json_safe(item) for item in value]
    if isinstance(value, Mapping):
        safe_items: JsonDict = {}
        for key, item in value.items():
            safe_items[str(key)] = _json_safe(item)
        return safe_items
    return {"repr": repr(value)}


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    """Serializable value snapshot derived from a runtime view."""

    current_base_state: object | None
    current_position_at_every_tier: tuple[object | None, ...]
    current_step_reward_value: float | None
    cumulative_reward_total: float
    cumulative_reward_count: int
    quotient_tier_count: int
    quotient_tier_reward_summary_count: int = 0
    active_control_tier: int | None = None
    last_control_action: str | None = None
    partition_tower_present: bool = False
    tower_update_changed: bool | None = None
    diagnostics: Mapping[str, object] = field(default_factory=dict)

    def to_dict(self) -> JsonDict:
        """Return a JSON-safe dictionary for controlled snapshot serialization."""

        data: JsonDict = {
            "current_position_at_every_tier": _json_safe(
                self.current_position_at_every_tier
            ),
            "current_step_reward_value": self.current_step_reward_value,
            "cumulative_reward_total": self.cumulative_reward_total,
            "cumulative_reward_count": self.cumulative_reward_count,
            "quotient_tier_count": self.quotient_tier_count,
            "quotient_tier_reward_summary_count": self.quotient_tier_reward_summary_count,
            "active_control_tier": self.active_control_tier,
            "last_control_action": self.last_control_action,
            "partition_tower_present": self.partition_tower_present,
            "tower_update_changed": self.tower_update_changed,
            "diagnostics": _json_safe(self.diagnostics),
        }
        safe_state = _json_safe(self.current_base_state)
        if isinstance(safe_state, dict) and set(safe_state) == {"repr"}:
            data["current_base_state_repr"] = safe_state["repr"]
        else:
            data["current_base_state"] = safe_state
        return data


@dataclass(frozen=True, slots=True)
class LiveRuntimeView:
    """Live runtime handoff object carrying graph and tower references."""

    current_base_state: object | None
    explored_graph: ExploredGraph
    vista_graph: VistaGraph
    ordered_quotient_tiers: tuple[QuotientTierView, ...]
    current_position_at_every_tier: tuple[object | None, ...]
    current_step_reward: StepReward | None
    cumulative_path_reward: PathRewardSummary
    quotient_tier_reward_summaries: tuple[QuotientRewardSummary, ...]
    active_control_tier: int | None = None
    last_control_action: str | None = None
    partition_tower_view: object | None = None
    tower_update_result: object | None = None

    def to_snapshot(self) -> RuntimeSnapshot:
        """Freeze the live handoff into a small value snapshot."""

        return RuntimeSnapshot(
            current_base_state=self.current_base_state,
            current_position_at_every_tier=self.current_position_at_every_tier,
            current_step_reward_value=(
                None if self.current_step_reward is None else self.current_step_reward.value
            ),
            cumulative_reward_total=self.cumulative_path_reward.total,
            cumulative_reward_count=len(self.cumulative_path_reward.step_rewards),
            quotient_tier_count=len(self.current_position_at_every_tier),
            quotient_tier_reward_summary_count=len(self.quotient_tier_reward_summaries),
            active_control_tier=self.active_control_tier,
            last_control_action=self.last_control_action,
            partition_tower_present=self.partition_tower_view is not None,
            tower_update_changed=(
                None
                if self.tower_update_result is None
                else bool(getattr(self.tower_update_result, "changed", False))
            ),
        )


__all__ = ["LiveRuntimeView", "RuntimeSnapshot"]
