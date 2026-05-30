"""Contraction schema surfaces for persistent edge-block assignment.

`ContractionSchema` is the partition-tower contraction schedule. It is distinct
from local-star `ContractionPolicy`, which remains an annotation/message-passing
policy used by legacy and vista-facing code.
"""

from __future__ import annotations

import random
from collections.abc import Hashable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Protocol

from state_collapser.tower.partition.base_registry import BaseGraphRegistry
from state_collapser.tower.partition.ids import EdgeId, SchemaBlockId


class ContractionSchema(Protocol):
    """Assign discovered base edges to ordered contraction blocks.

    A schema is the runtime form of the ordered edge partition
    `Sigma_0^1, ..., Sigma_0^d`. Edges assigned to earlier blocks create coarser
    tiers earlier; returning `None` leaves an edge unscheduled for contraction.
    """

    def assign_edge(
        self,
        edge_id: EdgeId,
        registry: BaseGraphRegistry,
    ) -> SchemaBlockId | None:
        """Return the schema block for an edge, or ``None`` if unscheduled."""

    def ordered_blocks(self) -> tuple[SchemaBlockId, ...]:
        """Return schema blocks in contraction order."""


@dataclass(frozen=True, slots=True)
class SchemaAssignment:
    """Persistent assignment of one edge to one contraction-schema block."""

    edge_id: EdgeId
    block_id: SchemaBlockId | None


@dataclass(slots=True)
class SchemaAssignmentStore:
    """Persistent edge-to-block assignment cache for one schema.

    The store ensures a discovered edge is assigned once, then reused during
    incremental updates. This makes schema behavior stable even when later graph
    discovery adds more edges.
    """

    schema: ContractionSchema
    assignment_by_edge_id: dict[EdgeId, SchemaBlockId | None] = field(default_factory=dict)
    edge_ids_by_block: dict[SchemaBlockId, dict[EdgeId, None]] = field(default_factory=dict)
    unscheduled_edge_ids: dict[EdgeId, None] = field(default_factory=dict)

    def assign_edge(
        self,
        edge_id: EdgeId,
        registry: BaseGraphRegistry,
    ) -> SchemaAssignment:
        """Assign an edge once and return its persistent assignment record."""

        if edge_id in self.assignment_by_edge_id:
            return SchemaAssignment(edge_id, self.assignment_by_edge_id[edge_id])

        block_id = self.schema.assign_edge(edge_id, registry)
        self.assignment_by_edge_id[edge_id] = block_id
        if block_id is None:
            self.unscheduled_edge_ids[edge_id] = None
        else:
            self.edge_ids_by_block.setdefault(block_id, {})[edge_id] = None
        return SchemaAssignment(edge_id=edge_id, block_id=block_id)

    def assign_edges(
        self,
        edge_ids: Iterable[EdgeId],
        registry: BaseGraphRegistry,
    ) -> tuple[SchemaAssignment, ...]:
        """Assign multiple edges in input order."""

        return tuple(self.assign_edge(edge_id, registry) for edge_id in edge_ids)

    def edges_in_block(self, block_id: SchemaBlockId) -> tuple[EdgeId, ...]:
        """Return edge ids assigned to a block in assignment order."""

        return tuple(self.edge_ids_by_block.get(block_id, {}).keys())

    def ordered_blocks(self) -> tuple[SchemaBlockId, ...]:
        """Return contraction blocks in schema-declared order."""

        return self.schema.ordered_blocks()

    def scheduled_edge_ids(self) -> tuple[EdgeId, ...]:
        """Return assigned, scheduled edge ids in assignment order."""

        return tuple(
            edge_id
            for edge_id, block_id in self.assignment_by_edge_id.items()
            if block_id is not None
        )


@dataclass(frozen=True, slots=True)
class NoContractionSchema:
    """Schema that keeps the tower at the base tier by scheduling no edges."""

    def assign_edge(
        self,
        edge_id: EdgeId,
        registry: BaseGraphRegistry,
    ) -> SchemaBlockId | None:
        """Leave every edge unscheduled."""

        return None

    def ordered_blocks(self) -> tuple[SchemaBlockId, ...]:
        """Return no contraction blocks."""

        return ()


@dataclass(frozen=True, slots=True)
class LabelBlockSchema:
    """Assign edges to contraction blocks by matching labels in declared order."""

    ordered_label_blocks: tuple[tuple[Hashable, SchemaBlockId], ...]

    @classmethod
    def from_labels(cls, labels: Iterable[Hashable]) -> LabelBlockSchema:
        """Build a schema whose block ids are the labels themselves."""

        return cls(tuple((label, SchemaBlockId(label)) for label in labels))

    @classmethod
    def from_mapping(cls, mapping: Mapping[Hashable, Hashable]) -> LabelBlockSchema:
        """Build a schema from an ordered label-to-block mapping."""

        return cls(
            tuple((label, SchemaBlockId(block_value)) for label, block_value in mapping.items())
        )

    def assign_edge(
        self,
        edge_id: EdgeId,
        registry: BaseGraphRegistry,
    ) -> SchemaBlockId | None:
        """Return the first declared block whose label appears on the edge."""

        labels = set(registry.labels_for_edge_id(edge_id))
        for label, block_id in self.ordered_label_blocks:
            if label in labels:
                return block_id
        return None

    def ordered_blocks(self) -> tuple[SchemaBlockId, ...]:
        """Return unique block ids in first-declared label order."""

        ordered: dict[SchemaBlockId, None] = {}
        for _, block_id in self.ordered_label_blocks:
            ordered.setdefault(block_id, None)
        return tuple(ordered.keys())


@dataclass(frozen=True, slots=True)
class DimensionwiseSchema:
    """Convenience schema for contracting labeled dimensions in order."""

    dimensions: tuple[Hashable, ...]

    def assign_edge(
        self,
        edge_id: EdgeId,
        registry: BaseGraphRegistry,
    ) -> SchemaBlockId | None:
        """Assign by matching one of the configured dimension labels."""

        return LabelBlockSchema.from_labels(self.dimensions).assign_edge(edge_id, registry)

    def ordered_blocks(self) -> tuple[SchemaBlockId, ...]:
        """Return one block per configured dimension in dimension order."""

        return tuple(SchemaBlockId(dimension) for dimension in self.dimensions)


@dataclass(frozen=True, slots=True)
class SeededRandomRateSchema:
    """Assign each edge to a deterministic pseudo-random contraction block."""

    seed: int
    block_count: int = 3

    def __post_init__(self) -> None:
        """Validate that at least one random contraction block exists."""

        if self.block_count <= 0:
            raise ValueError("SeededRandomRateSchema.block_count must be positive.")

    def assign_edge(
        self,
        edge_id: EdgeId,
        registry: BaseGraphRegistry,
    ) -> SchemaBlockId:
        """Assign an edge using a seed and the edge's stable registry id."""

        rng = random.Random(f"{self.seed}:{edge_id.value}")
        return SchemaBlockId(("random", rng.randrange(self.block_count)))

    def ordered_blocks(self) -> tuple[SchemaBlockId, ...]:
        """Return all random-rate blocks in numeric order."""

        return tuple(SchemaBlockId(("random", index)) for index in range(self.block_count))


@dataclass(frozen=True, slots=True)
class DiscoveryOrderChunkSchema:
    """Assign edges to deterministic blocks by discovery-order chunks."""

    chunk_size: int

    def __post_init__(self) -> None:
        """Validate that discovery-order chunks are nonempty."""

        if self.chunk_size <= 0:
            raise ValueError("DiscoveryOrderChunkSchema.chunk_size must be positive.")

    def assign_edge(
        self,
        edge_id: EdgeId,
        registry: BaseGraphRegistry,
    ) -> SchemaBlockId:
        """Assign an edge to the chunk containing its registry allocation id."""

        return SchemaBlockId(("chunk", edge_id.value // self.chunk_size))

    def ordered_blocks(self) -> tuple[SchemaBlockId, ...]:
        """Return no fixed block list because chunks appear as edges are discovered."""

        return ()


__all__ = [
    "ContractionSchema",
    "DimensionwiseSchema",
    "DiscoveryOrderChunkSchema",
    "LabelBlockSchema",
    "NoContractionSchema",
    "SchemaAssignment",
    "SchemaAssignmentStore",
    "SeededRandomRateSchema",
]
