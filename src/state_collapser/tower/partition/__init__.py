"""Partition-tower runtime model.

This package contains the nested state/action partition implementation that
backs the Young-tableaux-style tower runtime. The partition tower is the runtime
model; `QuotientTierView` objects are compatibility readouts derived from it.
"""

from state_collapser.tower.partition.diagnostics import TowerUpdateDiagnostics
from state_collapser.tower.partition.ids import (
    ActionCellId,
    ActionCollectionId,
    ActionId,
    EdgeId,
    SchemaBlockId,
    StateCellId,
    StateId,
    TierIndex,
)
from state_collapser.tower.partition.internal_aggregation import (
    InternalAggregationName,
    InternalAggregationResult,
    InternalEdgeAggregator,
    aggregate_internal_values,
)
from state_collapser.tower.partition.loop_policy import (
    InternalEdgeRecord,
    LoopPolicy,
    LoopPolicyName,
)
from state_collapser.tower.partition.reward_aggregation import (
    RewardAggregationName,
    RewardAggregationResult,
    RewardAggregator,
    aggregate_rewards,
)
from state_collapser.tower.partition.schema import (
    ContractionSchema,
    DimensionwiseSchema,
    DiscoveryOrderChunkSchema,
    LabelBlockSchema,
    NoContractionSchema,
    SchemaAssignment,
    SchemaAssignmentStore,
    SeededRandomRateSchema,
)
from state_collapser.tower.partition.tower import PartitionTower, build_partition_tower_full
from state_collapser.tower.partition.update import (
    ActionCollectionMergeRecord,
    StateCellMergeRecord,
    TowerMorphism,
    TowerUpdateResult,
)

__all__ = [
    "ActionCellId",
    "ActionCollectionMergeRecord",
    "ActionCollectionId",
    "ActionId",
    "ContractionSchema",
    "DimensionwiseSchema",
    "DiscoveryOrderChunkSchema",
    "EdgeId",
    "InternalAggregationName",
    "InternalAggregationResult",
    "InternalEdgeAggregator",
    "InternalEdgeRecord",
    "LabelBlockSchema",
    "LoopPolicy",
    "LoopPolicyName",
    "NoContractionSchema",
    "PartitionTower",
    "RewardAggregationName",
    "RewardAggregationResult",
    "RewardAggregator",
    "SchemaBlockId",
    "SchemaAssignment",
    "SchemaAssignmentStore",
    "SeededRandomRateSchema",
    "StateCellMergeRecord",
    "StateCellId",
    "StateId",
    "TierIndex",
    "TowerMorphism",
    "TowerUpdateDiagnostics",
    "TowerUpdateResult",
    "aggregate_internal_values",
    "aggregate_rewards",
    "build_partition_tower_full",
]
