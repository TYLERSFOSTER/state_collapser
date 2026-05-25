# Post-Young-Diagram Evaluation Environment Repair Blueprint

## Status

Date: 2026-05-24

Branch inspected:

```text
codex/young-tableaux-runtime-refactor
```

Design status:

```text
Blueprint, not implementation gameplan
```

This blueprint turns
`docs/design/test_design/post_young_audit/01_001_post_young_diagram_evaluation_environment_audit.md`
into a concrete repair design for the evaluation/environment test surface after
the Young diagram / nested partition runtime refactor.

The audit conclusion was:

> The environments are not broadly broken at the transition/reward/API level,
> but most of them are now tower-flat because they still expose the old
> `contraction_policy` surface while the partition backend is driven by
> `contraction_schema`.

The goal of this blueprint is to repair that semantic break without undoing the
Young diagram refactor.

## Executive Blueprint

The repair should make `ContractionSchema` the explicit environment-facing
surface for quotient-tower construction.

Every evaluation environment that is meant to exercise nontrivial hierarchy
should provide:

1. environment-specific edge labels or a schema that can inspect edge/state/action
   data,
2. an optional `contraction_schema` runtime constructor parameter,
3. a documented default schema when nontrivial tower behavior is intended by
   default,
4. training pass-through for the same schema,
5. probe support that reports schema behavior rather than only legacy policy
   behavior,
6. tests that fail if the environment silently collapses back to a depth-1 tower.

This is a semantic migration, not a broad rewrite. The environment dynamics,
reward functions, Gymnasium wrappers, and reference training loops are largely
sound. The missing piece is the schema-facing quotient construction layer.

The core implementation target is:

```text
legacy policy-driven assumption
    -> explicit schema-driven partition-tower evaluation surface
```

## Non-Goals

This repair should not:

- revert to the legacy dynamic tower backend as the default runtime path;
- reintroduce the old hand-authored counterpoint rank tower;
- claim that first-pass schemas are final benchmark-quality scientific schemas;
- convert every example into a benchmark environment;
- redesign the reward functions;
- redesign the collector/learner/reference-loop architecture;
- harden vectorization, batching, checkpointing, or model-training surfaces.

Those are separate design surfaces. This blueprint is specifically about
post-Young-diagram evaluation environment validity.

## Ground Truth From The Current Repo

The current runtime stack has these relevant facts:

- `TowerRuntime` defaults to `tower_backend="partition"`.
- `TowerRuntime(..., contraction_schema=None)` becomes `NoContractionSchema()`.
- `NoContractionSchema` schedules no discovered base edges for contraction.
- `ContractionPolicy` remains accepted by `TowerRuntime`, but under the partition
  backend it is not the authoritative contraction schedule.
- `BaseEdge` already supports `labels: tuple[Hashable, ...]`.
- `BaseGraphRegistry` stores combined edge/action labels and exposes them through
  `labels_for_edge_id(...)`.
- `LabelBlockSchema` and `DimensionwiseSchema` already assign edges by labels.
- `PlateSupportEnvRuntime` is the only large evaluation runtime already migrated
  to accept a `contraction_schema`.
- `plate_support_env` labels edges with `"plate-support-transition"` and supplies
  `DimensionwiseSchema(("plate-support-transition",))` by default.
- `articulated_loop_env`, `cable_parallel_env`,
  `dual_arm_manipulation_env`, `parallelogram_singularity_env`, and
  `rl_counterpoint_v3` still build unlabeled `BaseEdge(...)` objects and pass no
  schema to `TowerRuntime`.
- The current `tower_depth_probe` is still policy-centered and has a CLI no-env
  default bug.

The immediate repair can therefore use the existing schema machinery. We do not
need a new tower backend.

## Design Principle 1: Schema Is The Quotient Schedule

The runtime contract should be made clear:

```text
ContractionPolicy:
    local-star/vista annotation and legacy policy surface

ContractionSchema:
    partition-tower contraction schedule
```

The example runtimes should stop giving users the impression that
`contraction_policy` alone controls tower coarsening under the partition backend.
The parameter can stay for compatibility, but schema must become visible wherever
nontrivial quotient behavior is expected.

Target public constructor shape:

```python
class SomeEnvRuntime:
    def __init__(
        self,
        env: SomeEnv,
        contraction_policy: ContractionPolicy | None = None,
        contraction_schema: ContractionSchema | None = None,
    ) -> None:
        ...
```

Target `TowerRuntime` construction shape:

```python
self._tower_runtime = TowerRuntime(
    hidden_graph=self.hidden_graph,
    contraction_policy=contraction_policy,
    contraction_schema=(
        default_some_env_schema()
        if contraction_schema is None
        else contraction_schema
    ),
    reward_function=self._reward_from_edge,
)
```

If an environment is intentionally flat, it should explicitly pass
`NoContractionSchema()` or document that `contraction_schema=None` means a flat
baseline. It should not accidentally become flat because the runtime forgot to
provide a schema.

## Design Principle 2: Labels Should Be Auditable

For the first repair, labels are preferable to opaque schema logic.

The existing package already has the right machinery:

```python
BaseEdge(
    source=state,
    action=action,
    target=target,
    labels=(...),
)
```

Then:

```python
DimensionwiseSchema(("some-label", "another-label"))
```

or:

```python
LabelBlockSchema.from_mapping(
    {
        "fine-label-a": "coarse-block-a",
        "fine-label-b": "coarse-block-a",
        "fine-label-c": "coarse-block-b",
    }
)
```

This keeps the quotient schedule inspectable:

- a developer can print edge labels;
- a test can assert that labels are present;
- a probe can report scheduled assignment counts;
- a design document can explain why a block exists;
- a future benchmark can compare schemas.

An opaque schema that only inspects payloads internally may eventually be useful,
but it is a weaker first repair because it is harder to audit.

## Design Principle 3: Separate Smoke Schemas From Semantic Schemas

The repair should distinguish two schema levels.

### Smoke Schema

A smoke schema is a minimal compatibility schema that proves:

- labels are present,
- schema assignments are nonzero,
- the partition backend creates at least one nontrivial tier,
- training keys can include coarse tower positions.

Example:

```python
DimensionwiseSchema(("articulated-loop-transition",))
```

Smoke schemas are useful for regression tests, but they are not necessarily good
scientific benchmark schemas. A broad "all transitions" label can over-collapse
structure.

### Semantic Schema

A semantic schema is an environment-specific quotient hypothesis.

It groups edges according to the latent geometry of the task:

- joint-family motion,
- span/singularity motion,
- cable tension family,
- arm/object coordination family,
- counterpoint voice-motion family.

Semantic schemas are what should eventually support serious evaluation claims.

The first implementation may ship with smoke defaults plus semantic helper
functions where they are easy and safe. The tests should clearly identify which
mode they are checking.

## Target Runtime API

Each schema-enabled environment runtime should expose:

```python
runtime = SomeEnvRuntime(
    env=SomeEnv(),
    contraction_policy=None,
    contraction_schema=None,
)
```

The meaning should be:

- `contraction_schema=None` uses that environment's documented default schema if
  the environment is a quotient-evaluation environment.
- `contraction_schema=NoContractionSchema()` explicitly requests a flat baseline.
- `contraction_schema=DimensionwiseSchema(...)` or another schema object overrides
  the default.
- `contraction_policy` is preserved as a legacy/annotation compatibility input,
  but tests and docs should not describe it as the quotient schedule under the
  partition backend.

Recommended helper naming:

```python
def default_articulated_loop_schema() -> ContractionSchema: ...
def default_cable_parallel_schema() -> ContractionSchema: ...
def default_dual_arm_schema() -> ContractionSchema: ...
def default_parallelogram_schema() -> ContractionSchema: ...
def default_rl_counterpoint_v3_schema() -> ContractionSchema: ...
```

The helpers should be exported in each example package `__init__.py` only if the
package already exports runtime surfaces there. Otherwise they can remain local
until the public API is reviewed.

## Target Training API

Every `run_tower_training(...)` entrypoint for schema-enabled environments should
accept schema pass-through:

```python
def run_tower_training(
    *,
    env: SomeEnv | None = None,
    contraction_policy: ContractionPolicy | None = None,
    contraction_schema: ContractionSchema | None = None,
    config: TowerTrainingConfig | None = None,
) -> TowerTrainingResult:
    ...
```

The runtime call should pass both:

```python
runtime = SomeEnvRuntime(
    env=SomeEnv() if env is None else env,
    contraction_policy=contraction_policy,
    contraction_schema=contraction_schema,
)
```

This keeps training honest:

- default training exercises the default quotient schema;
- flat-baseline training can explicitly pass `NoContractionSchema()`;
- future benchmark scripts can sweep schemas without constructing runtimes
  manually.

## Environment Repair Blueprint

### `plate_support_env`

Current status:

- already schema-enabled;
- already labels hidden-graph edges with `"plate-support-transition"`;
- already defaults to `DimensionwiseSchema(("plate-support-transition",))`;
- already reaches nontrivial depth in the probe.

Blueprint:

- keep the current default schema as the smoke/default schema;
- add explicit tests that the default schema schedules at least one assignment;
- add an explicit flat-baseline test using `NoContractionSchema()`;
- optionally add named helper `default_plate_support_schema()` for consistency;
- do not broaden this repair unless tests reveal a mismatch.

Potential future semantic labels:

- `"plate-support-pose-motion"` for actions that change `x_idx`, `y_idx`, or
  `theta_idx`;
- `"plate-support-extension-motion"` for actuator/support extension actions;
- `"plate-support-support-pattern"` for transitions changing support pattern.

Risk:

- the current broad label is good enough as a compatibility schema, but may be
  too blunt for benchmark-quality claims.

### `articulated_loop_env`

Current status:

- transition/reward tests pass;
- runtime is partition-backed;
- runtime has no schema parameter;
- hidden graph creates unlabeled `BaseEdge` objects;
- depth probe is flat.

Action semantics from current code:

- actions `0` and `1` rotate `d1`;
- actions `2` and `3` rotate `d2`;
- actions `4` and `5` rotate `d3`;
- action `6` flips `brace_mode`;
- actions `7` and `8` change `coupler_slack`.

First repair labels:

```text
"articulated-loop-transition"
"articulated-loop-link-1"
"articulated-loop-link-2"
"articulated-loop-link-3"
"articulated-loop-brace-mode"
"articulated-loop-coupler-slack"
```

Recommended smoke schema:

```python
DimensionwiseSchema(("articulated-loop-transition",))
```

Recommended semantic schema:

```python
DimensionwiseSchema(
    (
        "articulated-loop-coupler-slack",
        "articulated-loop-brace-mode",
        "articulated-loop-link-1",
        "articulated-loop-link-2",
        "articulated-loop-link-3",
    )
)
```

Rationale:

- slack and brace mode encode feasibility/closure slack;
- link rotations encode the articulated geometry;
- the schema order gives a coarse feasibility-support tier before refining by
  individual link coordinates.

Implementation surface:

- add `edge_labels_for_action(index: int) -> tuple[Hashable, ...]`;
- use those labels in `ArticulatedLoopHiddenGraph.out_edges(...)`;
- add `contraction_schema` to `ArticulatedLoopEnvRuntime`;
- add `default_articulated_loop_schema()`.

Test targets:

- at least one outgoing edge from the start state has labels;
- the default runtime reaches `len(snapshot.current_position_at_every_tier) >= 2`
  after a short deterministic action sequence;
- `NoContractionSchema()` keeps the same runtime flat;
- `runtime.last_tower_update_result.schema_assignments` includes at least one
  non-`None` block.

### `parallelogram_singularity_env`

Current status:

- transition/reward tests pass;
- runtime is partition-backed;
- runtime has no schema parameter;
- hidden graph creates unlabeled edges;
- depth probe is flat.

Action semantics from current code:

- actions `0` and `1` rotate `left_angle`;
- actions `2` and `3` rotate `right_angle`;
- actions `4` and `5` change `span`;
- action `6` flips `alignment_mode`.

First repair labels:

```text
"parallelogram-transition"
"parallelogram-left-angle"
"parallelogram-right-angle"
"parallelogram-span"
"parallelogram-alignment-mode"
"parallelogram-singular-source"
"parallelogram-singular-target"
"parallelogram-enters-singular-regime"
"parallelogram-leaves-singular-regime"
```

Recommended smoke schema:

```python
DimensionwiseSchema(("parallelogram-transition",))
```

Recommended semantic schema:

```python
DimensionwiseSchema(
    (
        "parallelogram-enters-singular-regime",
        "parallelogram-leaves-singular-regime",
        "parallelogram-span",
        "parallelogram-alignment-mode",
        "parallelogram-left-angle",
        "parallelogram-right-angle",
    )
)
```

Rationale:

- this environment is specifically about a singularity/bottleneck regime;
- transitions that enter or leave singular span regimes should be visible to the
  quotient schedule;
- span and alignment are more structurally central than raw angle rotations.

Implementation surface:

- import or locally use `is_singular_state(...)` from the env module;
- add labels based on action index and source/target singularity status;
- add `contraction_schema` to `ParallelogramSingularityEnvRuntime`;
- add `default_parallelogram_schema()`.

Test targets:

- labels include singularity labels on transitions crossing the singular boundary;
- default schema reaches depth at least `2`;
- schema assignment diagnostics are nonzero;
- flat baseline remains possible with `NoContractionSchema()`.

### `cable_parallel_env`

Current status:

- transition/reward tests pass;
- runtime is partition-backed;
- runtime has no schema parameter;
- hidden graph creates unlabeled edges;
- depth probe is flat.

Action semantics from current code:

- actions `0` and `1` change `x_idx`;
- actions `2` and `3` change `y_idx`;
- action `4` flips `theta_idx`;
- actions `5` and `6` change `c1`;
- actions `7` and `8` change `c2`;
- actions `9` and `10` change `c3`.

First repair labels:

```text
"cable-parallel-transition"
"cable-parallel-x-motion"
"cable-parallel-y-motion"
"cable-parallel-orientation-motion"
"cable-parallel-cable-1-tension"
"cable-parallel-cable-2-tension"
"cable-parallel-cable-3-tension"
"cable-parallel-platform-motion"
"cable-parallel-tension-motion"
```

Recommended smoke schema:

```python
DimensionwiseSchema(("cable-parallel-transition",))
```

Recommended semantic schema:

```python
DimensionwiseSchema(
    (
        "cable-parallel-tension-motion",
        "cable-parallel-platform-motion",
        "cable-parallel-orientation-motion",
        "cable-parallel-cable-1-tension",
        "cable-parallel-cable-2-tension",
        "cable-parallel-cable-3-tension",
    )
)
```

Rationale:

- the hidden structure is a feasible region inside pose/tension product space;
- tension feasibility is a natural coarse quotient family;
- platform motion and cable-specific tension motion can then refine it.

Implementation surface:

- add label helper keyed by action index;
- add `contraction_schema` to `CableParallelEnvRuntime`;
- add `default_cable_parallel_schema()`;
- optionally add a semantic label based on support count changes later, but do
  not require this in the first implementation.

Test targets:

- start-state outgoing edges include platform and tension labels;
- default schema reaches depth at least `2` after a short deterministic sequence;
- flat schema remains depth `1`;
- tower-training Q-table keys include at least one key with more than one tier
  position under the default schema.

### `dual_arm_manipulation_env`

Current status:

- transition/reward tests pass;
- runtime is partition-backed;
- runtime has no schema parameter;
- hidden graph creates unlabeled edges;
- depth probe is flat.

Action semantics from current code:

- actions `0` and `1` change object `obj_x`;
- actions `2` and `3` change object `obj_y`;
- action `4` flips object `obj_theta`;
- action `5` changes `left_mode`;
- action `6` changes `right_mode`;
- actions `7` and `8` change `left_reach`;
- actions `9` and `10` change `right_reach`.

First repair labels:

```text
"dual-arm-transition"
"dual-arm-object-x-motion"
"dual-arm-object-y-motion"
"dual-arm-object-orientation-motion"
"dual-arm-left-mode-motion"
"dual-arm-right-mode-motion"
"dual-arm-left-reach-motion"
"dual-arm-right-reach-motion"
"dual-arm-object-motion"
"dual-arm-left-arm-motion"
"dual-arm-right-arm-motion"
"dual-arm-coordination-motion"
```

Recommended smoke schema:

```python
DimensionwiseSchema(("dual-arm-transition",))
```

Recommended semantic schema:

```python
DimensionwiseSchema(
    (
        "dual-arm-coordination-motion",
        "dual-arm-object-motion",
        "dual-arm-left-arm-motion",
        "dual-arm-right-arm-motion",
    )
)
```

Rationale:

- this environment is about hidden coordination geometry;
- object movement, left-arm state, and right-arm state are the obvious quotient
  dimensions;
- a coarse coordination label can group arm-mode/reach changes before finer
  object and arm families.

Implementation surface:

- add label helper keyed by action index;
- add `contraction_schema` to `DualArmManipulationEnvRuntime`;
- add `default_dual_arm_schema()`;
- avoid adding complicated support-count labels in the first pass unless needed
  for stable depth.

Test targets:

- outgoing edges expose object/arm labels;
- default schema reaches nontrivial depth;
- schema diagnostics show scheduled assignments;
- `run_tower_training(..., contraction_schema=NoContractionSchema())` remains
  valid as a flat baseline.

### `rl_counterpoint_v3`

Current status:

- environment and training smoke tests pass;
- runtime is partition-backed;
- runtime has no schema parameter;
- hidden graph creates unlabeled edges;
- current probe reports `max_depth = 1`;
- historical implementation log recorded `max_depth = 15` under the old
  dynamic path.

Important design constraint:

The repair should not restore the old explicit rank tower. The point is not to
hand-author "rank 1, rank 2, rank 3" as the tower. The point is to let the
package-facing schema induce quotient structure from neutral edge/action facts.

Action semantics from current code:

- actions are bounded nonzero three-voice step deltas;
- `action_index_to_step_delta(index, spec=...)` decodes an action to
  `(bass_delta, inner_delta, upper_delta)`;
- each valid primitive transition advances `beat_index`;
- state validity enforces voice order, pitch range, allowed interval classes,
  allowed bass/root families, and forbidden parallel classes.

First repair labels:

```text
"rl-counterpoint-v3-transition"
"rl-counterpoint-v3-bass-motion"
"rl-counterpoint-v3-inner-motion"
"rl-counterpoint-v3-upper-motion"
"rl-counterpoint-v3-any-voice-motion"
"rl-counterpoint-v3-stepwise-motion"
"rl-counterpoint-v3-leap-motion"
"rl-counterpoint-v3-oblique-motion"
"rl-counterpoint-v3-parallel-direction-motion"
"rl-counterpoint-v3-contrary-direction-motion"
"rl-counterpoint-v3-beat-advance"
```

Optional later labels:

```text
"rl-counterpoint-v3-adjacent-interval-change"
"rl-counterpoint-v3-outer-interval-change"
"rl-counterpoint-v3-root-family-change"
"rl-counterpoint-v3-terminal-beat-target"
"rl-counterpoint-v3-valid-cadential-motion"
```

Recommended smoke schema:

```python
DimensionwiseSchema(("rl-counterpoint-v3-transition",))
```

Recommended first semantic schema:

```python
DimensionwiseSchema(
    (
        "rl-counterpoint-v3-bass-motion",
        "rl-counterpoint-v3-inner-motion",
        "rl-counterpoint-v3-upper-motion",
        "rl-counterpoint-v3-contrary-direction-motion",
        "rl-counterpoint-v3-oblique-motion",
        "rl-counterpoint-v3-parallel-direction-motion",
    )
)
```

Rationale:

- voice-motion labels are neutral action facts, not an explicit old rank tower;
- they make the hidden hierarchy pressure visible to the partition backend;
- motion-family labels are musically interpretable and testable;
- this preserves the conceptual claim that counterpoint has latent hierarchical
  quotient structure while avoiding a hand-authored training tower.

Implementation surface:

- import `action_index_to_step_delta`;
- add helper `rl_counterpoint_edge_labels(state, action_index, target, spec)`;
- label edges in `RlCounterpointHiddenGraph.out_edges(...)`;
- add `contraction_schema` to `RlCounterpointEnvRuntime`;
- add `default_rl_counterpoint_v3_schema()`;
- add tests that assert nontrivial depth but do not require the old `max_depth = 15`.

Test targets:

- decoded edge labels match action deltas;
- default schema schedules nonzero assignments;
- deterministic continuous probe reaches `max_depth >= 2`;
- flat baseline with `NoContractionSchema()` reaches only depth `1` under the same
  probe;
- training keys under default schema include multi-tier tower positions.

## Probe Repair Blueprint

The probe should change from a policy-centered diagnostic to a schema-aware
diagnostic.

Current problem:

```text
--no-contraction-policy
--sample-size
```

These flags still exercise a legacy/annotation knob, but they do not control
partition-tower coarsening.

### Required Probe Fixes

Fix the no-env default CLI bug.

The parser currently combines:

```python
nargs="*"
choices=tuple(SUPPORTED_ENVIRONMENTS)
```

Observed behavior:

```text
argument envs: invalid choice: [] (...)
```

The probe should allow no positional envs and then default to all supported
environments in `main(...)`.

Recommended parser design:

```python
parser.add_argument(
    "envs",
    nargs="*",
    help="Environment names to probe. Defaults to all supported environments.",
)
```

Then validate manually:

```python
env_names = tuple(args.envs) if args.envs else tuple(SUPPORTED_ENVIRONMENTS)
for env_name in env_names:
    if env_name not in SUPPORTED_ENVIRONMENTS:
        parser.error(...)
```

### Required Probe Schema Surface

Add a schema mode.

Recommended initial CLI:

```text
--schema-mode default
--schema-mode none
```

Optional later CLI:

```text
--schema-mode smoke
--schema-mode semantic
--schema-mode random-rate
```

First-scope semantics:

- `default`: use each environment runtime's default schema;
- `none`: pass `NoContractionSchema()` explicitly;
- legacy `--no-contraction-policy` can remain, but help text should clarify that
  it disables only the legacy/annotation policy, not schema scheduling.

The `ProbeEnvironment.runtime_factory` should accept both policy and schema:

```python
runtime_factory: Callable[
    [ContractionPolicy | None, ContractionSchema | None],
    ProbeRuntime,
]
```

### Required Probe Diagnostics

Extend `DepthProbeResult` to report at least:

```python
schema_mode: str
scheduled_assignment_count: int
unscheduled_assignment_count: int
max_depth: int
depth_curve: tuple[int, ...]
reset_events: tuple[tuple[int, bool, bool], ...]
```

Optional later diagnostics:

```python
nontrivial_merge_count: int
affected_tier_count: int
created_tier_count: int
backend: str
schema_name: str
```

The scheduled assignment count can be computed from:

```python
runtime.tower_runtime.last_tower_update_result.schema_assignments
```

where scheduled means:

```python
assignment.block_id is not None
```

Because the probe loops over steps, it should accumulate counts across updates,
not only inspect the final update.

### Probe Acceptance Behavior

After repair, this should be true:

```text
uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --summary-only
```

Expected:

- command succeeds with no positional env names;
- all supported environments are probed;
- schema-enabled envs report `max_depth >= 2` in default mode;
- flat mode reports depth `1` for environments whose only source of hierarchy is
  schema contraction.

## Test Repair Blueprint

The current tests mostly prove that runtimes run. The repaired tests must also
prove that quotient structure is being exercised where expected.

### Shared Test Helpers

Introduce small helpers in tests or in an example test utility module:

```python
def scheduled_assignment_count(runtime: object) -> int:
    result = runtime.tower_runtime.last_tower_update_result
    if result is None:
        return 0
    return sum(1 for assignment in result.schema_assignments if assignment.block_id is not None)
```

```python
def has_nontrivial_tower(snapshot: RuntimeSnapshot) -> bool:
    return len(snapshot.current_position_at_every_tier) >= 2
```

Avoid overfitting tests to exact tower depth. Exact depth can vary when schema
semantics improve.

### Per-Environment Runtime Tests

For every schema-enabled environment:

- test reset returns a snapshot;
- test step returns a snapshot;
- test at least one outgoing edge has labels;
- test default schema schedules nonzero assignments after a deterministic action
  sequence;
- test default schema reaches at least two tiers;
- test explicit `NoContractionSchema()` remains flat.

The deterministic action sequence should be local to each environment and should
use known valid or at least non-crashing actions. It does not need to solve the
task.

### Training Tests

For every repaired training entrypoint:

- test `run_tower_training(...)` still returns nonempty episodes and Q-table;
- test passing `contraction_schema=NoContractionSchema()` does not crash;
- for at least one representative environment, assert that default training
  produces at least one Q-table key with length greater than `1`.

This catches the current failure mode directly: flat runtime keys are still
nonempty, but their tuple length is only `1`.

### Probe Tests

Add or update tests around `tower_depth_probe`:

- no positional envs defaults to all environments;
- unsupported env names produce a clean parser error or `ValueError`;
- `schema_mode="default"` reaches nontrivial depth for at least
  `plate_support_env` and one newly migrated environment;
- `schema_mode="none"` reports flat depth for the same deterministic probe;
- result diagnostics include scheduled assignment counts.

### Counterpoint Regression Test

Add a post-refactor equivalent of the old reality check.

Do not assert the historical value:

```text
max_depth == 15
```

Instead assert:

```text
max_depth >= 2
scheduled_assignment_count > 0
```

The old `15` belonged to the legacy dynamic policy path. The new partition
schema path has different semantics and should not be forced to match that exact
number.

## Documentation Repair Blueprint

Update documentation so users do not misread the environment examples.

Required doc clarifications:

- `ContractionSchema` is the partition-tower schedule.
- `ContractionPolicy` is retained for legacy/local-star/vista compatibility.
- Most evaluation environments now have default schemas.
- Flat baselines require explicit `NoContractionSchema()`.
- Broad smoke schemas are not final benchmark schemas.
- `tower_depth_probe` should be interpreted in schema terms.

Candidate docs:

- `README.md`
- environment test design docs under `docs/design/test_design/*`
- relevant implementation log once the repair is executed
- any example docstring or CLI help text for `tower_depth_probe`

## Compatibility Requirements

The repair should preserve these existing surfaces:

- constructing runtimes with only `env=...`;
- constructing runtimes with `contraction_policy=...`;
- running all existing example training loops;
- existing return dataclasses for reset/step;
- `tower_runtime` property;
- `quotient_tiers` property;
- `RuntimeSnapshot.current_position_at_every_tier`;
- `TowerRuntime.last_tower_update_result`.

The repair may add optional parameters and helper functions, but it should not
break existing imports.

## Backward Compatibility Strategy

The safest migration is additive:

1. add labels to hidden graph edges;
2. add `contraction_schema` optional constructor parameters;
3. default to environment schema where the environment is intended to be
   schema-enabled;
4. preserve `contraction_policy` parameters;
5. add tests for explicit flat baselines;
6. update probe semantics.

This gives users three modes:

```python
# new default quotient-evaluation mode
runtime = SomeEnvRuntime(env=SomeEnv())

# explicit flat baseline
runtime = SomeEnvRuntime(env=SomeEnv(), contraction_schema=NoContractionSchema())

# custom schema experiment
runtime = SomeEnvRuntime(env=SomeEnv(), contraction_schema=DimensionwiseSchema(...))
```

## Risks

### Risk: Broad Smoke Schemas Over-Collapse

A one-label schema like:

```python
DimensionwiseSchema(("some-env-transition",))
```

can prove the machinery works but may collapse too much structure. This is fine
for smoke tests, but benchmark docs should not oversell it.

Mitigation:

- name broad schemas as smoke/default compatibility schemas;
- add semantic schema helpers where the geometry is clear;
- keep flat baselines available.

### Risk: Tests Become Too Brittle

Exact tower depth can change as schemas improve.

Mitigation:

- assert lower bounds like `>= 2`;
- assert scheduled assignments and nonempty labels;
- avoid exact cell ids or exact depth values except in tiny unit tests.

### Risk: Counterpoint Schema Looks Like The Old Rank Tower

Voice-motion labels could be mistaken for reintroducing the old explicit rank
tower.

Mitigation:

- document that the schema is derived from edge/action facts;
- avoid naming labels `"rank-1"`, `"rank-2"`, or `"rank-3"`;
- include motion-family labels beyond voice identity when useful;
- preserve custom schema override.

### Risk: `contraction_policy` Confusion Persists

Users may continue to pass `contraction_policy` expecting tower depth changes.

Mitigation:

- update CLI help and docs;
- add schema-mode probe controls;
- consider deprecating policy-centered probe language later.

## Acceptance Criteria

The repair is successful when:

- all example tests still pass;
- every schema-enabled evaluation runtime accepts `contraction_schema`;
- every schema-enabled hidden graph emits inspectable edge labels;
- `tower_depth_probe` runs with no positional env names;
- `tower_depth_probe --schema-mode default` reports nontrivial depth for
  schema-enabled environments;
- `tower_depth_probe --schema-mode none` can demonstrate flat baselines;
- `rl_counterpoint_v3` regains a nontrivial post-refactor tower-depth reality
  check;
- tests fail if a schema-enabled environment silently returns to depth `1`;
- docs clarify that schema, not policy, is the partition contraction schedule.

## Expected Implementation Footprint

Likely source files:

```text
src/state_collapser/examples/articulated_loop_env/runtime.py
src/state_collapser/examples/articulated_loop_env/training.py
src/state_collapser/examples/cable_parallel_env/runtime.py
src/state_collapser/examples/cable_parallel_env/training.py
src/state_collapser/examples/dual_arm_manipulation_env/runtime.py
src/state_collapser/examples/dual_arm_manipulation_env/training.py
src/state_collapser/examples/parallelogram_singularity_env/runtime.py
src/state_collapser/examples/parallelogram_singularity_env/training.py
src/state_collapser/examples/rl_counterpoint_v3/runtime.py
src/state_collapser/examples/rl_counterpoint_v3/training.py
src/state_collapser/examples/tower_depth_probe.py
```

Likely test files:

```text
tests/examples/test_articulated_loop_env_runtime_integration.py
tests/examples/test_cable_parallel_env_runtime_integration.py
tests/examples/test_dual_arm_manipulation_env_runtime_integration.py
tests/examples/test_parallelogram_singularity_env_runtime_integration.py
tests/examples/test_rl_counterpoint_v3_runtime_integration.py
tests/examples/test_tower_depth_probe.py
```

Likely optional test additions:

```text
tests/examples/test_evaluation_env_schema_surfaces.py
tests/examples/test_rl_counterpoint_v3_schema_depth.py
```

Likely documentation files:

```text
README.md
docs/design/test_design/post_young_audit/01_003_*.md
```

## Recommended Implementation Order

This is not yet a Phase.Stage.Action gameplan, but the implementation should
probably proceed in this order:

1. fix `tower_depth_probe` no-env parser behavior;
2. add schema-mode plumbing to `tower_depth_probe`;
3. migrate one small environment after `plate_support_env`, preferably
   `parallelogram_singularity_env`;
4. add shared test helpers for scheduled assignments and nontrivial depth;
5. migrate `articulated_loop_env`;
6. migrate `cable_parallel_env`;
7. migrate `dual_arm_manipulation_env`;
8. migrate `rl_counterpoint_v3`;
9. update training pass-through;
10. strengthen probe and training tests;
11. update docs.

The reason to start with `parallelogram_singularity_env` is that its action
families are small and the singularity labels are conceptually sharp. It is a
good second reference implementation after `plate_support_env`.

## Open PO Decisions

### PO Answer: Should broad smoke schemas be default for every repaired environment?

Recommendation: yes for the first repair, but call them smoke/default
compatibility schemas and keep `NoContractionSchema()` as the explicit flat
baseline.

### PO Answer: Should semantic schemas ship in the first implementation?

Recommendation: ship simple semantic label helpers where they are obvious, but
do not block the repair on benchmark-grade schemas.

### PO Answer: Should `rl_counterpoint_v3` default to voice-motion labels?

Recommendation: yes. Voice-motion labels are neutral edge/action facts and are
the clearest first post-refactor schema for restoring nontrivial hierarchy
without reviving the old explicit rank tower.

### PO Answer: Should `contraction_policy` be deprecated?

Recommendation: not yet. Keep it for compatibility, but update docs/probes so
it is no longer described as the partition-tower contraction schedule.

### PO Answer: What threshold should tests require for tower depth?

Recommendation: require `>= 2` for schema-enabled environments and avoid exact
depth assertions except in tiny controlled unit tests.

## Blueprint Conclusion

The audit does not point to a broken Young diagram refactor. It points to an
unfinished migration of the evaluation environments onto the new schema-driven
runtime surface.

The right repair is to make the partition schedule explicit at the environment
boundary:

```text
edge labels + contraction schema + schema-aware probes + tests that require
nontrivial quotient behavior
```

Once this is in place, the environment suite will again test what the project
actually claims to provide: not just a flat RL environment wrapper, but a runtime
architecture where discovered graph structure is maintained through nested
state/action coset partitions.
