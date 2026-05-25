"""Internal reusable training surfaces for state_collapser."""

from .collectors import CollectedEpisode, CollectedStep, EpisodeCollector, StepCollector
from .continuation import (
    BootstrapSemantics,
    default_bootstrap_allowed,
    default_bootstrap_reason,
)
from .decisions import ActionDecision
from .fibers import FiberDeparture, FiberDepartureReason, FiberStageContext, PathFiber
from .frozen import FrozenQuotientBehavior, FrozenQuotientStep
from .inputs import ActionSelectionInput, build_action_selection_input, tower_position_key
from .learners import Learner, LearnerUpdateSummary, TabularQLearner
from .masks import action_is_legal, legal_actions, mask_from_info
from .metrics import EpisodeMetrics, MetricsHook, TrainingMetrics
from .reference_loops import (
    ReferenceLoopResult,
    run_reference_episode_loop,
    run_reference_online_loop,
)
from .stages import FiberConditionedStage
from .transitions import RuntimeSnapshotSummary, TrainingTransition, summarize_runtime_snapshot

__all__ = [
    "ActionDecision",
    "ActionSelectionInput",
    "BootstrapSemantics",
    "CollectedEpisode",
    "CollectedStep",
    "EpisodeCollector",
    "EpisodeMetrics",
    "FiberConditionedStage",
    "FiberDeparture",
    "FiberDepartureReason",
    "FiberStageContext",
    "FrozenQuotientBehavior",
    "FrozenQuotientStep",
    "Learner",
    "LearnerUpdateSummary",
    "MetricsHook",
    "PathFiber",
    "ReferenceLoopResult",
    "RuntimeSnapshotSummary",
    "StepCollector",
    "TabularQLearner",
    "TrainingMetrics",
    "TrainingTransition",
    "action_is_legal",
    "build_action_selection_input",
    "default_bootstrap_allowed",
    "default_bootstrap_reason",
    "legal_actions",
    "mask_from_info",
    "run_reference_episode_loop",
    "run_reference_online_loop",
    "summarize_runtime_snapshot",
    "tower_position_key",
]
