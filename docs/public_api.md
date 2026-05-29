# Public API Policy

This document states the package's public API policy. It is intentionally not a
complete inventory of importable modules. Many modules are importable because
they are tested, useful, and needed by current examples, but importability is not
the same thing as long-term API stability.

## Current Stable Contract

The only stable top-level public API currently exposed by the package is:

- `state_collapser.__version__`

Everything else should be treated as provisional unless a later release promotes
it deliberately.

## Provisional Engineer-Facing Surfaces

For the current documented provisional surfaces, use the API notes:

- [PartitionTower](./api_notes/partition_tower.md)
- [training inputs and transitions](./api_notes/training_inputs_and_transitions.md)
- [FrozenQuotientBehavior](./api_notes/frozen_quotient_behavior.md)
- [PathFiber](./api_notes/path_fiber.md)
- [FiberConditionedStage](./api_notes/fiber_conditioned_stage.md)
- [tensorization boundary](./api_notes/tensorization_boundary.md)

These notes are the right place to look for exact current names and usage
patterns. This file should not duplicate that inventory.

## Compatibility Targets

The repository's current external compatibility targets are design commitments,
not blanket stable runtime APIs:

- `gymnasium` for environment interoperability
- `torch` for model-backend interoperability
- `ROS 2` for robotics-stack interoperability
- `HGraphML` as a downstream graph-ML package that consumes partition-tower
  construction and fiber/readout information

Adapters or bridge modules for those systems should not be treated as stable
public API until they are deliberately documented, tested, and exported.

## Known Downstream Consumer: HGraphML

`HGraphML` is now a real downstream consumer of `state_collapser`. It uses the
partition-tower runtime to turn a known graph into a quotient tower for trainable
graph message passing.

The current HGraphML-facing dependency surface includes:

- core state/action/edge wrappers
- contraction schemas, especially label-block schemas
- `PartitionTower`
- `build_partition_tower_full`
- state-cell and edge/source/target queries needed to recover node and edge
  fibers

These names are still pre-alpha and should not be read as permanently stable
API. However, they are no longer merely private implementation details. Changes
that alter them should either preserve HGraphML behavior or include an explicit
migration path.

## Promotion Rule

Before making a module or symbol public:

1. Define its intended users.
2. Define its stability expectations.
3. Add tests that describe the public behavior.
4. Document the surface in the appropriate usage or API note.
5. Export it intentionally from `state_collapser.__init__` or from a documented
   public submodule.

Until that happens, an import path may be useful and tested without being a
promised public API.
