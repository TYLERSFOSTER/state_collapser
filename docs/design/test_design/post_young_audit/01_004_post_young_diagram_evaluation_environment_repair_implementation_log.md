# Post-Young-Diagram Evaluation Environment Repair Implementation Log

## Status

Date: 2026-05-24

Gameplan:

```text
docs/design/test_design/post_young_audit/01_003_post_young_diagram_evaluation_environment_repair_implementation_gameplan.md
```

Branch:

```text
codex/post-young-eval-env-schema-repair
```

Starting commit:

```text
17b8fad env test fix planning
```

Starting status:

```text
## codex/post-young-eval-env-schema-repair
```

## Execution Contract

This log records execution of the Phase.Stage.Action gameplan.

If implementation reality conflicts with the gameplan, execution must stop and
return to the Project Owner. Silent simplification, silent reordering, and
silent reinterpretation are forbidden.

## Validation Command Set

Focused validation:

```text
uv run pytest tests/examples/test_tower_depth_probe.py
uv run pytest tests/examples/test_plate_support_env_runtime_integration.py
uv run pytest tests/examples/test_parallelogram_singularity_env_runtime_integration.py
uv run pytest tests/examples/test_articulated_loop_env_runtime_integration.py
uv run pytest tests/examples/test_cable_parallel_env_runtime_integration.py
uv run pytest tests/examples/test_dual_arm_manipulation_env_runtime_integration.py
uv run pytest tests/examples/test_rl_counterpoint_v3_runtime_integration.py
```

Broad validation:

```text
uv run pytest tests/examples
uv run pytest
```

Probe validation:

```text
uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --summary-only
uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --schema-mode none --summary-only
```

## Completed Actions

### Phase 0.Stage 0.1.Action 0.1.1

Confirmed execution authority from Project Owner instruction:

```text
Perfect. Implement this: docs/design/test_design/post_young_audit/01_003_post_young_diagram_evaluation_environment_repair_implementation_gameplan.md following prime_directive, in step-by-step Phase.Stage.Action form, makeing new branch first
```

### Phase 0.Stage 0.1.Action 0.1.2

Created dedicated implementation branch:

```text
codex/post-young-eval-env-schema-repair
```

### Phase 0.Stage 0.2.Action 0.2.1

Created this implementation log before source-code or test edits.

### Phase 0.Stage 0.3.Action 0.3.1

Verified current runtime reality:

```text
TowerRuntime accepts contraction_schema
TowerRuntime stores last_tower_update_result
BaseEdge accepts labels
PrimitiveAction accepts labels
ContractionSchema exists
NoContractionSchema exists
DimensionwiseSchema exists
```

Files inspected:

```text
src/state_collapser/tower/runtime.py
src/state_collapser/tower/partition/schema.py
src/state_collapser/core/edges.py
src/state_collapser/core/action.py
```

## In Progress

### Phase 0.Stage 0.3.Action 0.3.2

Capturing pre-repair baseline.

## Test Results

### Phase 0.Stage 0.3.Action 0.3.2

Command:

```text
uv run pytest tests/examples
```

Result:

```text
138 passed in 0.81s
```

Command:

```text
uv run python -m state_collapser.examples.tower_depth_probe plate_support_env articulated_loop_env dual_arm_manipulation_env cable_parallel_env parallelogram_singularity_env rl_counterpoint_v3 --steps 20 --seed 7 --summary-only
```

Result:

```text
plate_support_env                    max_depth: 2
articulated_loop_env                 max_depth: 1
dual_arm_manipulation_env            max_depth: 1
cable_parallel_env                   max_depth: 1
parallelogram_singularity_env        max_depth: 1
rl_counterpoint_v3                   max_depth: 1
```

Interpretation:

```text
The pre-repair baseline matches the audit: examples are API/test healthy, but
all target environments except plate_support_env are tower-flat.
```

## In Progress

### Phase 1.Stage 1.1.Action 1.1.1

Creating shared schema-depth test helpers.

## Completed Actions

### Phase 1.Stage 1.1.Action 1.1.1

Created shared example schema assertion helpers:

```text
tests/examples/schema_assertions.py
```

Helpers added:

```text
scheduled_assignment_count
latest_schema_assignment_count
snapshot_has_nontrivial_tower
assert_runtime_scheduled_schema_assignments
assert_snapshot_has_nontrivial_tower
```

### Phase 1.Stage 1.1.Action 1.1.2

Recorded deterministic environment-local action sequences as the test convention.
No global sequence was introduced because action semantics differ per
environment.

### Phase 1.Stage 1.2.Action 1.2.1

Updated `tower_depth_probe` parser so empty positional environment selection is
accepted and environment validation is handled after parsing.

### Phase 1.Stage 1.2.Action 1.2.2

Added schema-mode probe plumbing:

```text
--schema-mode default
--schema-mode none
```

Also updated legacy policy help text so it no longer implies policy controls
partition coarsening.

### Phase 1.Stage 1.2.Action 1.2.3

Extended `DepthProbeResult` with:

```text
schema_mode
scheduled_assignment_count
unscheduled_assignment_count
```

Probe now accumulates schema assignment counts across reset and step updates.

## Test Results

### Phase 1

Command:

```text
uv run pytest tests/examples/test_tower_depth_probe.py
```

Result:

```text
5 passed in 0.41s
```

## In Progress

### Phase 2.Stage 2.1.Action 2.1.1

Normalizing plate-support default schema helper.

## Completed Actions

### Phase 2.Stage 2.1.Action 2.1.1

Added and exported:

```text
default_plate_support_schema
```

Updated `PlateSupportEnvRuntime` to use the helper instead of inline
`DimensionwiseSchema` construction.

### Phase 2.Stage 2.2.Action 2.2.1

Added plate-support tests for:

```text
default schema produces a nontrivial tower
default schema schedules assignments
explicit NoContractionSchema stays flat
```

## Test Results

### Phase 2

Command:

```text
uv run pytest tests/examples/test_plate_support_env_runtime_integration.py
```

Initial result:

```text
ImportError: No module named 'tests'
```

Reality correction:

```text
tests/examples is not importable as tests.examples in this context. The helper
import was corrected to use the local test-module import path.
```

Final result:

```text
14 passed in 0.12s
```

## In Progress

### Phase 3.Stage 3.1.Action 3.1.1

Adding parallelogram edge labels.

## Completed Actions

### Phase 3.Stage 3.1.Action 3.1.1

Added `parallelogram_edge_labels(...)` and wired labels into
`ParallelogramHiddenGraph.out_edges(...)`.

Label families added:

```text
parallelogram-transition
parallelogram-left-angle
parallelogram-right-angle
parallelogram-span
parallelogram-alignment-mode
parallelogram-singular-source
parallelogram-singular-target
parallelogram-enters-singular-regime
parallelogram-leaves-singular-regime
```

### Phase 3.Stage 3.1.Action 3.1.2

Added and exported:

```text
default_parallelogram_schema
semantic_parallelogram_schema
```

### Phase 3.Stage 3.2.Action 3.2.1

Added `contraction_schema` to `ParallelogramSingularityEnvRuntime` and defaulted
to `default_parallelogram_schema()` when no schema override is supplied.

### Phase 3.Stage 3.2.Action 3.2.2

Validated parallelogram migration.

## Test Results

### Phase 3

Command:

```text
uv run pytest tests/examples/test_parallelogram_singularity_env_runtime_integration.py tests/examples/test_tower_depth_probe.py
```

Result:

```text
11 passed in 0.34s
```

Command:

```text
uv run python -m state_collapser.examples.tower_depth_probe parallelogram_singularity_env --steps 20 --seed 7 --summary-only
```

Result:

```text
parallelogram_singularity_env
max_depth: 2
scheduled_assignments: 35
unscheduled_assignments: 0
```

## In Progress

### Phase 4.Stage 4.1.Action 4.1.1

Adding articulated-loop edge labels.

## Completed Actions

### Phase 4.Stage 4.1.Action 4.1.1

Added `articulated_loop_edge_labels(...)` and wired labels into
`ArticulatedLoopHiddenGraph.out_edges(...)`.

Label families added:

```text
articulated-loop-transition
articulated-loop-link-1
articulated-loop-link-2
articulated-loop-link-3
articulated-loop-brace-mode
articulated-loop-coupler-slack
```

### Phase 4.Stage 4.1.Action 4.1.2

Added and exported:

```text
default_articulated_loop_schema
semantic_articulated_loop_schema
```

### Phase 4.Stage 4.2.Action 4.2.1

Added `contraction_schema` to `ArticulatedLoopEnvRuntime` and defaulted to
`default_articulated_loop_schema()` when no schema override is supplied.

### Phase 4.Stage 4.2.Action 4.2.2

Validated articulated-loop migration.

## Test Results

### Phase 4

Command:

```text
uv run pytest tests/examples/test_articulated_loop_env_runtime_integration.py tests/examples/test_tower_depth_probe.py
```

Result:

```text
11 passed in 0.33s
```

Command:

```text
uv run python -m state_collapser.examples.tower_depth_probe articulated_loop_env --steps 20 --seed 7 --summary-only
```

Result:

```text
articulated_loop_env
max_depth: 2
scheduled_assignments: 117
unscheduled_assignments: 0
```

## In Progress

### Phase 5.Stage 5.1.Action 5.1.1

Adding cable-parallel edge labels.

## Completed Actions

### Phase 5.Stage 5.1.Action 5.1.1

Added `cable_parallel_edge_labels(...)` and wired labels into
`CableParallelHiddenGraph.out_edges(...)`.

Label families added:

```text
cable-parallel-transition
cable-parallel-x-motion
cable-parallel-y-motion
cable-parallel-orientation-motion
cable-parallel-cable-1-tension
cable-parallel-cable-2-tension
cable-parallel-cable-3-tension
cable-parallel-platform-motion
cable-parallel-tension-motion
```

### Phase 5.Stage 5.1.Action 5.1.2

Added and exported:

```text
default_cable_parallel_schema
semantic_cable_parallel_schema
```

### Phase 5.Stage 5.2.Action 5.2.1

Added `contraction_schema` to `CableParallelEnvRuntime` and defaulted to
`default_cable_parallel_schema()` when no schema override is supplied.

### Phase 5.Stage 5.2.Action 5.2.2

Validated cable-parallel migration.

## Test Results

### Phase 5

Command:

```text
uv run pytest tests/examples/test_cable_parallel_env_runtime_integration.py tests/examples/test_tower_depth_probe.py
```

Result:

```text
11 passed in 0.43s
```

Command:

```text
uv run python -m state_collapser.examples.tower_depth_probe cable_parallel_env --steps 20 --seed 7 --summary-only
```

Result:

```text
cable_parallel_env
max_depth: 2
scheduled_assignments: 88
unscheduled_assignments: 0
```

## In Progress

### Phase 6.Stage 6.1.Action 6.1.1

Adding dual-arm edge labels.

## Completed Actions

### Phase 6.Stage 6.1.Action 6.1.1

Added `dual_arm_edge_labels(...)` and wired labels into
`DualArmManipulationHiddenGraph.out_edges(...)`.

Label families added:

```text
dual-arm-transition
dual-arm-object-x-motion
dual-arm-object-y-motion
dual-arm-object-orientation-motion
dual-arm-left-mode-motion
dual-arm-right-mode-motion
dual-arm-left-reach-motion
dual-arm-right-reach-motion
dual-arm-object-motion
dual-arm-left-arm-motion
dual-arm-right-arm-motion
dual-arm-coordination-motion
```

### Phase 6.Stage 6.1.Action 6.1.2

Added and exported:

```text
default_dual_arm_schema
semantic_dual_arm_schema
```

### Phase 6.Stage 6.2.Action 6.2.1

Added `contraction_schema` to `DualArmManipulationEnvRuntime` and defaulted to
`default_dual_arm_schema()` when no schema override is supplied.

### Phase 6.Stage 6.2.Action 6.2.2

Validated dual-arm migration.

## Test Results

### Phase 6

Command:

```text
uv run pytest tests/examples/test_dual_arm_manipulation_env_runtime_integration.py tests/examples/test_tower_depth_probe.py
```

Result:

```text
11 passed in 0.34s
```

Command:

```text
uv run python -m state_collapser.examples.tower_depth_probe dual_arm_manipulation_env --steps 20 --seed 7 --summary-only
```

Result:

```text
dual_arm_manipulation_env
max_depth: 2
scheduled_assignments: 121
unscheduled_assignments: 0
```

## In Progress

### Phase 7.Stage 7.1.Action 7.1.1

Adding neutral motion-family counterpoint edge labels.

## Completed Actions

### Phase 7.Stage 7.1.Action 7.1.1

Added `rl_counterpoint_edge_labels(...)` and wired labels into
`RlCounterpointHiddenGraph.out_edges(...)`.

Label families added:

```text
rl-counterpoint-v3-transition
rl-counterpoint-v3-bass-motion
rl-counterpoint-v3-inner-motion
rl-counterpoint-v3-upper-motion
rl-counterpoint-v3-any-voice-motion
rl-counterpoint-v3-stepwise-motion
rl-counterpoint-v3-leap-motion
rl-counterpoint-v3-oblique-motion
rl-counterpoint-v3-parallel-direction-motion
rl-counterpoint-v3-contrary-direction-motion
rl-counterpoint-v3-beat-advance
```

### Phase 7.Stage 7.2.Action 7.2.1

Added and exported:

```text
default_rl_counterpoint_v3_schema
semantic_rl_counterpoint_v3_schema
```

### Phase 7.Stage 7.3.Action 7.3.1

Added `contraction_schema` to `RlCounterpointEnvRuntime` and defaulted to
`default_rl_counterpoint_v3_schema()` when no schema override is supplied.

### Phase 7.Stage 7.3.Action 7.3.2

Restored post-refactor nontrivial counterpoint depth check without asserting the
historical legacy `max_depth = 15`.

## Test Results

### Phase 7

Command:

```text
uv run pytest tests/examples/test_rl_counterpoint_v3_runtime_integration.py tests/examples/test_tower_depth_probe.py
```

Result:

```text
12 passed in 0.61s
```

Command:

```text
uv run python -m state_collapser.examples.tower_depth_probe rl_counterpoint_v3 --steps 40 --seed 0 --summary-only
```

Result:

```text
rl_counterpoint_v3
max_depth: 2
scheduled_assignments: 1116
unscheduled_assignments: 0
```

## In Progress

### Phase 8.Stage 8.1.Action 8.1.1

Adding schema pass-through to example training entrypoints.

## Completed Actions

### Phase 8.Stage 8.1.Action 8.1.1

Added `contraction_schema` pass-through to mechanical example
`run_tower_training(...)` entrypoints:

```text
articulated_loop_env
cable_parallel_env
dual_arm_manipulation_env
parallelogram_singularity_env
plate_support_env
```

Plate support was included because it is already a schema-enabled evaluation
environment and the final acceptance criteria require migrated training loops to
accept schema overrides.

### Phase 8.Stage 8.1.Action 8.1.2

Added shared training schema pass-through tests:

```text
tests/examples/test_training_schema_pass_through.py
```

These tests verify default schema training keys have length `2` and explicit
`NoContractionSchema()` training keys have length `1`.

### Phase 8.Stage 8.2.Action 8.2.1

Added `contraction_schema` pass-through to `rl_counterpoint_v3`
`run_tower_training(...)`.

### Phase 8.Stage 8.3.Action 8.3.1

Validated example suite after training pass-through migration.

## Test Results

### Phase 8

Command:

```text
uv run pytest tests/examples/test_training_schema_pass_through.py
```

Result:

```text
2 passed in 0.37s
```

Command:

```text
uv run pytest tests/examples
```

Result:

```text
167 passed in 1.06s
```

## In Progress

### Phase 9.Stage 9.1.Action 9.1.1

Updating probe registry to pass schema arguments to all schema-enabled runtimes.

## Completed Actions

### Phase 9.Stage 9.1.Action 9.1.1

Updated `SUPPORTED_ENVIRONMENTS` runtime factories so all schema-enabled
environment runtimes receive the probe schema argument.

### Phase 9.Stage 9.2.Action 9.2.1

Added cross-environment probe tests for:

```text
default schema mode reaches nontrivial depth
default schema mode schedules assignments
none schema mode schedules zero assignments
```

### Phase 9.Stage 9.3.Action 9.3.1

Validated CLI probe output in default and none schema modes.

## Test Results

### Phase 9

Command:

```text
uv run pytest tests/examples/test_tower_depth_probe.py
```

Result:

```text
7 passed in 0.50s
```

Command:

```text
uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --summary-only
```

Result:

```text
plate_support_env                    max_depth: 2 scheduled_assignments: 84  unscheduled_assignments: 0
articulated_loop_env                 max_depth: 2 scheduled_assignments: 117 unscheduled_assignments: 0
dual_arm_manipulation_env            max_depth: 2 scheduled_assignments: 121 unscheduled_assignments: 0
cable_parallel_env                   max_depth: 2 scheduled_assignments: 88  unscheduled_assignments: 0
parallelogram_singularity_env        max_depth: 2 scheduled_assignments: 35  unscheduled_assignments: 0
rl_counterpoint_v3                   max_depth: 2 scheduled_assignments: 248 unscheduled_assignments: 0
```

Command:

```text
uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --schema-mode none --summary-only
```

Result:

```text
plate_support_env                    max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 84
articulated_loop_env                 max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 117
dual_arm_manipulation_env            max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 121
cable_parallel_env                   max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 88
parallelogram_singularity_env        max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 35
rl_counterpoint_v3                   max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 248
```

## In Progress

### Phase 10.Stage 10.1.Action 10.1.1

Updating README environment/tower language.

## Completed Actions

### Phase 10.Stage 10.1.Action 10.1.1

Updated `README.md` to clarify:

```text
ContractionSchema is the partition-tower contraction schedule.
ContractionPolicy remains a legacy/local-star/vista compatibility surface.
--schema-mode default uses environment schemas.
--schema-mode none is the explicit flat probe baseline.
NoContractionSchema is the explicit Python flat baseline.
```

### Phase 10.Stage 10.2.Action 10.2.1

Kept this implementation log current through the documentation phase.

### Phase 10.Stage 10.3.Action 10.3.1

Probe help text was updated during Phase 1 to describe schema mode and legacy
policy behavior accurately.

## Test Results

### Phase 10

Command:

```text
uv run pytest tests/examples/test_tower_depth_probe.py
```

Result:

```text
7 passed in 0.40s
```

## Completed Actions

### Phase 11.Stage 11.1.Action 11.1.1

Ran full example validation after all environment schema migrations, training
pass-through updates, probe updates, and README updates.

### Phase 11.Stage 11.1.Action 11.1.2

Ran full repository validation after the focused example suite was green.

### Phase 11.Stage 11.2.Action 11.2.1

Ran Ruff across the repository. Ruff initially reported import-order fixes in
new tests and one long line in the probe. Applied Ruff's safe fixes and wrapped
the remaining long line manually.

### Phase 11.Stage 11.2.Action 11.2.2

Re-ran focused and full validation after Ruff's import sorting and the manual
line-wrap correction.

### Phase 11.Stage 11.3.Action 11.3.1

Ran the final default-schema and flat-schema probe comparison.

### Phase 11.Stage 11.4.Action 11.4.1

Ran final diff hygiene.

## Test Results

### Phase 11

Command:

```text
uv run pytest tests/examples
```

Result:

```text
169 passed in 1.14s
```

Command:

```text
uv run pytest
```

Result:

```text
354 passed in 1.43s
```

Command:

```text
uv run ruff check .
```

Final result:

```text
All checks passed!
```

Command:

```text
uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --summary-only
```

Result:

```text
plate_support_env                    max_depth: 2 scheduled_assignments: 84  unscheduled_assignments: 0
articulated_loop_env                 max_depth: 2 scheduled_assignments: 117 unscheduled_assignments: 0
dual_arm_manipulation_env            max_depth: 2 scheduled_assignments: 121 unscheduled_assignments: 0
cable_parallel_env                   max_depth: 2 scheduled_assignments: 88  unscheduled_assignments: 0
parallelogram_singularity_env        max_depth: 2 scheduled_assignments: 35  unscheduled_assignments: 0
rl_counterpoint_v3                   max_depth: 2 scheduled_assignments: 248 unscheduled_assignments: 0
```

Command:

```text
uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --schema-mode none --summary-only
```

Result:

```text
plate_support_env                    max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 84
articulated_loop_env                 max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 117
dual_arm_manipulation_env            max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 121
cable_parallel_env                   max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 88
parallelogram_singularity_env        max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 35
rl_counterpoint_v3                   max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 248
```

Command:

```text
git diff --check
```

Result:

```text
no output
```

## Final Implementation State

The repair restores schema-driven, nontrivial partition towers across all six
evaluation environments while preserving an explicit flat baseline through
`NoContractionSchema` and `--schema-mode none`.

Changed tracked files:

```text
README.md
src/state_collapser/examples/*/runtime.py
src/state_collapser/examples/*/training.py
src/state_collapser/examples/*/__init__.py
src/state_collapser/examples/tower_depth_probe.py
tests/examples/test_*_runtime_integration.py
tests/examples/test_tower_depth_probe.py
```

New files:

```text
docs/design/test_design/post_young_audit/01_004_post_young_diagram_evaluation_environment_repair_implementation_log.md
tests/examples/schema_assertions.py
tests/examples/test_training_schema_pass_through.py
```

Final diff size:

```text
27 tracked files changed, 919 insertions(+), 29 deletions(-)
```

## Surprises And Stop Conditions

No stop condition was encountered.
