# Synthetic Blow Review Revision Implementation Log

Date: 2026-05-24

Source blueprint:

- `docs/design/synthetic_blow_revisions_01/01_001_synthetic_blow_review_revision_blueprint.md`

Source gameplan:

- `docs/design/synthetic_blow_revisions_01/01_002_synthetic_blow_review_revision_implementation_gameplan.md`

## Initial State

- Project Owner approved execution by saying `continue` after branch creation.
- Active branch: `codex/synthetic-blow-revisions-01`
- Starting commit: `529e462`
- Starting status:

```text
## codex/synthetic-blow-revisions-01
```

- No source-code or test implementation edits occurred before this log was created.

## Phase Progress

### Phase 0: Execution Setup And Reality Binding

- Action 0.1.1: completed. Execution approval is explicit.
- Action 0.1.2: completed. Branch `codex/synthetic-blow-revisions-01` exists and is active.
- Action 0.2.1: completed. This implementation log was created before source/test edits.
- Action 0.3.1: completed. Training files still match the gameplan's current-state claims:
  transitions lack continuation fields, collectors do not auto-extract masks, and
  `TabularQLearner.update(...)` still derives bootstrap from raw `terminated`/`truncated`.
- Action 0.3.2: completed. Runtime/adapter/example files still match the gameplan's
  current-state claims: snapshots are live object carriers, runtime eagerly rebuilds
  quotient readouts, partition updates always capture morphism domains, action-layer
  carry-forward hard-codes `LoopPolicy.drop_internal()`, the toy `GymnasiumAdapter`
  remains present, and four example envs coerce actions before validation.

### Phase 1: Strict Example Environment Action Boundaries

- Action 1.1.1: completed. Added
  `tests/examples/test_env_action_boundaries.py` with shared invalid-action
  checks for all current example Gymnasium environments.
- Actions 1.2.1, 1.2.2, 1.2.3, and 1.2.4: completed. Updated the
  articulated-loop, cable-parallel, dual-arm manipulation, and parallelogram
  singularity environments to reject invalid raw actions before coercion.
- Additional Phase 1 alignment: updated `PlateSupportEnv` and `RlCounterpointEnv`
  to reject bool actions and to coerce only after `action_space.contains(...)`
  succeeds, preserving NumPy integer scalar compatibility while forbidding
  float/string/bool boundary leaks.
- Action 1.3.1: completed. Focused validation passed:

```text
uv run pytest tests/examples/test_env_action_boundaries.py tests/examples/test_articulated_loop_env_validity.py tests/examples/test_cable_parallel_env_validity.py tests/examples/test_dual_arm_manipulation_env_validity.py tests/examples/test_parallelogram_singularity_env_validity.py tests/examples/test_plate_support_env_gymnasium.py tests/examples/test_rl_counterpoint_v3_gymnasium.py
52 passed in 0.43s
```

### Phase 2: First-Class Action Masks

- Action 2.1.1: completed. Added
  `src/state_collapser/training/masks.py` with `mask_from_info(...)`,
  `legal_actions(...)`, and `action_is_legal(...)`, and exported the helpers
  from `state_collapser.training`.
- Action 2.2.1: completed. `StepCollector.reset_episode(...)` now extracts a
  normalized mask from `info["action_mask"]` when no factory override is
  supplied.
- Action 2.2.2: completed. `StepCollector.collect_step(...)` rejects
  masked-off selected actions before mutating the runtime.
- Action 2.2.3: completed. `StepCollector.collect_step(...)` attaches target
  masks from step-result info, with factory override precedence preserved.
- Action 2.3.1: completed. Focused training validation passed:

```text
uv run pytest tests/training
19 passed in 0.66s
```

### Phase 3: Continuation-Aware And Masked Learner Semantics

- Action 3.1.1: completed. `TrainingTransition` now exposes explicit
  `bootstrap_allowed`, `bootstrap_input`, and `bootstrap_reason` fields.
- Action 3.1.2: completed. Added
  `src/state_collapser/training/continuation.py` with `BootstrapSemantics`,
  `default_bootstrap_allowed(...)`, and `default_bootstrap_reason(...)`.
- Action 3.2.1: completed. `StepCollector` now computes transition
  continuation fields with the required reason strings and configurable
  truncation semantics.
- Action 3.2.2: completed. Learner tests now include a manual
  `bootstrap_input` override with a distinct key.
- Action 3.3.1: completed. `TabularQLearner.act(...)` now raises on all-false
  source masks and never falls back to all actions when a mask exists.
- Action 3.3.2: completed. `TabularQLearner.update(...)` now obeys explicit
  continuation fields, uses `bootstrap_input` when supplied, masks bootstrap
  candidate actions, and reports bootstrap diagnostics.
- Action 3.4.1: completed. Focused training validation passed:

```text
uv run pytest tests/training
36 passed in 0.79s

uv run mypy src/state_collapser/training
Success: no issues found in 10 source files
```

### Phase 4: Reference Training Loop Consolidation

- Action 4.1.1: completed. Added
  `src/state_collapser/examples/_shared_training.py` and
  `tests/examples/test_training_semantics_shared.py`. The shared test proves
  the helper uses the package continuation semantics by checking truncation
  bootstrap behavior through `TabularQLearner`.
- Actions 4.2.1, 4.2.2, 4.2.3, and 4.2.4: completed. The ordinary
  articulated-loop, cable-parallel, dual-arm manipulation, and parallelogram
  tower-training paths now delegate to the shared helper instead of carrying
  local Q-target formulas.
- Action 4.2.5: completed. The ordinary `PlateSupportEnv` tower-training path
  now delegates to the shared helper. The experimental exploit/explore path
  remains intentionally unmigrated and isolated, per gameplan.
- Action 4.3.1: completed. Focused example training validation passed:

```text
uv run pytest tests/examples/test_training_semantics_shared.py tests/examples/test_articulated_loop_env_tower_training.py tests/examples/test_cable_parallel_env_tower_training.py tests/examples/test_dual_arm_manipulation_env_tower_training.py tests/examples/test_parallelogram_singularity_env_tower_training.py tests/examples/test_plate_support_env_tower_training.py tests/examples/test_plate_support_env_exploit_explore_training.py tests/examples/test_rl_counterpoint_v3_tower_training.py
17 passed in 0.81s
```

### Phase 5: Runtime View And Serializable Snapshot Split

- Action 5.1.1: completed. `src/state_collapser/tower/snapshot.py` now defines
  `LiveRuntimeView` for live graph/tower handoff and `RuntimeSnapshot` for the
  value snapshot shape. The value snapshot has no live graph, vista graph,
  partition tower, or quotient-tier-view fields.
- Action 5.1.2: completed. `RuntimeSnapshot.to_dict()` produces a JSON-safe
  dictionary for controlled serialization cases, using documented repr fields
  for non-JSON-safe objects.
- Action 5.2.1: completed. `TowerRuntime.reset(...)` and
  `TowerRuntime.step(...)` now return `LiveRuntimeView`; the live view exposes
  `to_snapshot()` for value-snapshot production.
- Action 5.2.2: completed. Training protocols and summaries now type against
  `LiveRuntimeView` for live runtime handoff, while `RuntimeSnapshotSummary`
  remains a small value summary.
- Action 5.3.1: completed. Added value-snapshot stability coverage proving an
  old value snapshot dict remains unchanged after the runtime advances.
- Action 5.4.1: completed. Focused runtime/training integration validation
  passed:

```text
uv run pytest tests/tower tests/training tests/examples/test_articulated_loop_env_runtime_integration.py tests/examples/test_cable_parallel_env_runtime_integration.py tests/examples/test_dual_arm_manipulation_env_runtime_integration.py tests/examples/test_parallelogram_singularity_env_runtime_integration.py tests/examples/test_plate_support_env_runtime_integration.py tests/examples/test_rl_counterpoint_v3_runtime_integration.py
202 passed in 1.38s
```

### Phase 6: Lazy Compatibility Readouts And Optional Morphisms

- Action 6.1.1: completed. `PartitionTower.update_with_delta(...)` now accepts
  `build_morphism: bool = False`. The default path returns an empty/default
  morphism and avoids `_capture_morphism_domain()`. Explicit
  `build_morphism=True` preserves previous morphism behavior.
- Action 6.2.1: completed. `TowerRuntime._apply_partition_update_result(...)`
  now stores update results, current positions, selected edges, and stopping
  reason without calling `PartitionTower.to_quotient_tier_views()` on the
  default partition-runtime path.
- Action 6.2.2: completed. Added
  `TowerRuntime.compatibility_quotient_tiers()` as the explicit lazy readout
  API. The legacy `quotient_tiers` property delegates to this compatibility
  call for backward-facing callers.
- Action 6.3.1: completed. `tower_depth_probe` now derives default depth from
  live runtime positions rather than forcing quotient-tier readouts.
- Action 6.4.1: completed. Focused tower/probe validation passed:

```text
uv run pytest tests/tower tests/quotient tests/examples/test_tower_depth_probe.py
141 passed in 0.47s
```

### Phase 7: Loop Policy Carry-Forward And Internal Aggregation

- Action 7.1.1: completed. `ActionPartitionLayer.carry_forward_from(...)` now
  accepts `loop_policy`, and partition-tower carry-forward paths pass the
  configured tower policy instead of hard-coding `LoopPolicy.drop_internal()`.
- Action 7.2.1: completed. Added
  `src/state_collapser/tower/partition/internal_aggregation.py` with
  `InternalAggregationName`, `InternalAggregationResult`,
  `InternalEdgeAggregator`, and `aggregate_internal_values(...)`, supporting
  `sum`, `mean`, and `max`.
- Action 7.2.2: completed. `PartitionTower` now stores
  `internal_edge_aggregator`, and update diagnostics expose the configured
  internal aggregation name without inventing reward semantics for absent
  internal values.
- Action 7.3.1: completed. Partition validation passed:

```text
uv run pytest tests/tower/partition
74 passed in 0.08s
```

### Phase 8: Real Gymnasium Bridge With Explicit Hooks

- Action 8.1.1: completed. Renamed the toy adapter surface to
  `RobotConstraintRuntimeAdapter` so it no longer appears to be the serious
  Gymnasium bridge.
- Action 8.2.1: completed. Added `StateCollapserGymHooks`, with explicit
  `state_key`, `action_key`, optional `action_mask`, and `edge_labeler` hooks.
- Action 8.3.1: completed. Added `StateCollapserGymWrapper`, which delegates to
  a wrapped Gymnasium-style env and records only realized transitions in an
  `ExploredGraph` opaque-mode structural layer.
- Action 8.3.2: completed. The wrapper propagates hook-provided action masks
  into returned info and records hook-provided edge labels on realized edges.
- Actions 8.4.1 and 8.4.2: completed. README and CONTRIBUTING now document the
  hook-based bridge and identify observation-vs-state inference as future work.
- Action 8.5.1: completed. Adapter/package validation passed:

```text
uv run pytest tests/adapters tests/test_package.py
10 passed in 0.23s
```

### Phase 9: Benchmark And Performance Regression Surface

- Action 9.1.1: completed. Added
  `src/state_collapser/benchmarks/` with `tower_runtime_bench.py` and a
  structured `TowerRuntimeBenchResult`.
- Action 9.2.1: completed. Benchmark supports `none` and `default` schema
  modes with configurable step count and seed.
- Action 9.2.2: completed. Benchmark distinguishes readout-disabled and
  readout-enabled modes and records `readout_requested`.
- Action 9.3.1: completed. Benchmark is executable via `python -m` and exposes
  `--steps`, `--seed`, `--mode`, `--summary-only`, `--readout`, and
  `--morphism`.
- Action 9.4.1: completed. Benchmark validation passed:

```text
uv run pytest tests/benchmarks/test_tower_runtime_bench.py
5 passed in 0.33s

uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
tower_runtime_bench mode=default steps=10 elapsed_seconds=0.005536 operations_per_second=1806.21 readout_requested=False morphism_requested=False tower_depth=2 discovered_states=22 discovered_edges=60
```

### Phase 10: Documentation And Public Surface Cleanup

- Action 10.1.1: completed. README TODOs now mention explicit masks and
  continuation/bootstrap semantics, live-view/value-snapshot hardening, lazy
  compatibility readouts, benchmark smoke tooling, hook-based Gymnasium, and
  observation-vs-state inference as future work.
- Action 10.1.2: completed. README package map now mentions
  `LiveRuntimeView`, serializable `RuntimeSnapshot`, action masks,
  continuation-aware transitions, `StateCollapserGymWrapper`, and
  `state_collapser.benchmarks`.
- Action 10.2.1: completed. CONTRIBUTING now documents Gymnasium integration
  expectations around explicit state/action hooks, masks, and transition
  labels.
- Action 10.2.2: completed. CONTRIBUTING now documents benchmark and hot-path
  discipline, including readout-disabled/readout-enabled benchmark smoke
  guidance.
- Action 10.3.1: completed. Deferred items explicitly retained:
  compiled-core/language rewrites are not part of this implementation;
  automatic observation-to-state inference remains future work; tensor/device,
  vectorized rollout, batch/sequence, and checkpoint hardening remain later
  training-surface work.

### Phase 11: Whole-Repo Validation And Consistency Sweep

- Action 11.1.1: completed. Focused training validation passed after masks,
  continuation semantics, collector changes, and reference-loop consolidation:

```text
uv run pytest tests/training
36 passed in 0.84s
```

- Action 11.1.2: completed. Focused tower and quotient validation passed after
  lazy readouts, optional morphism construction, live-view/value-snapshot split,
  and loop-policy/internal-aggregation changes:

```text
uv run pytest tests/tower tests/quotient
140 passed in 0.10s
```

- Action 11.1.3: completed. Focused adapter validation passed after replacing
  the old toy-facing adapter name with the explicit hook-based Gymnasium bridge:

```text
uv run pytest tests/adapters
7 passed in 0.08s
```

- Action 11.1.4: completed. Focused benchmark validation passed:

```text
uv run pytest tests/benchmarks
5 passed in 0.33s
```

- Action 11.1.5: completed. Focused example-environment validation passed after
  action-boundary fixes and shared ordinary training-loop consolidation:

```text
uv run pytest tests/examples
200 passed in 1.28s
```

- Action 11.2.1: completed. Final lint validation passed:

```text
uv run ruff check .
All checks passed!
```

- Action 11.2.2: completed. Final type validation passed:

```text
uv run mypy src
Success: no issues found in 85 source files
```

- Action 11.2.3: completed. Final full test validation passed:

```text
uv run pytest
437 passed in 2.01s
```

- Action 11.3.1: completed. Benchmark smoke validation passed:

```text
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
tower_runtime_bench mode=default steps=10 elapsed_seconds=0.005364 operations_per_second=1864.15 readout_requested=False morphism_requested=False tower_depth=2 discovered_states=22 discovered_edges=60
```

- Action 11.4.1: completed. Consistency search was run for:
  `GymnasiumAdapter`, `Serializable runtime handoff`, `terminated or truncated`,
  `to_quotient_tier_views()`, and `LoopPolicy.drop_internal()`.
- Action 11.4.2: completed. Runtime/source consistency findings:
  `GymnasiumAdapter` remains only in historical design/gameplan text; no
  public source export keeps the misleading old name. `Serializable runtime
  handoff` remains only as a search item in the implementation gameplan.
  `terminated or truncated` remains only in an example Gymnasium episode-break
  test and historical design text, not as learner bootstrap policy.
  `to_quotient_tier_views()` remains in explicit readout methods/tests and
  historical design text, not in the default runtime update hot path.
  `LoopPolicy.drop_internal()` remains as a default constructor/factory and in
  tests, but not as a hard-coded action-layer carry-forward policy.

### Phase 12: Handoff State

- Action 12.1.1: completed. Current branch is still
  `codex/synthetic-blow-revisions-01`.
- Action 12.1.2: completed. The working tree has implementation edits and new
  files pending review/stage/commit; no commit was made by Codex during this
  implementation pass.
- Action 12.1.3: completed. Tracked diff summary at handoff:

```text
47 files changed, 1364 insertions(+), 509 deletions(-)
```

- Action 12.1.4: completed. New untracked implementation artifacts pending add
  include the implementation log, benchmark package/tests, shared example
  training helper, internal aggregation module, training continuation/mask
  helpers, Gymnasium wrapper tests, action-boundary tests, shared-training
  semantics tests, runtime value-snapshot tests, and continuation/mask tests.
