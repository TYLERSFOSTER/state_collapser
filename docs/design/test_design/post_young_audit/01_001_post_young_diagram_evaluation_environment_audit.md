# Post-Young-Diagram Refactor Evaluation Environment Audit

## Status

Date: 2026-05-24

Branch inspected:

```text
codex/young-tableaux-runtime-refactor
```

This report audits the example/evaluation environments after the Young
diagram / nested partition runtime refactor.

The core question is:

> Do the evaluation environments still exercise meaningful tower behavior after
> `TowerRuntime` changed from the legacy full-rebuild contraction path to the
> partition-backed runtime?

## Executive Conclusion

The environments are not broadly broken at the basic API, transition, reward, or
smoke-training level. The full example suite passes.

However, the evaluation story is materially degraded for most environments.
After the Young diagram refactor, contraction is schema-driven. Most evaluation
environment runtimes still expose only the old `contraction_policy` parameter and
do not provide a `contraction_schema`. As a result, they run on the partition
backend with `NoContractionSchema`, produce only tier `0`, and do not test
nontrivial quotient-tower behavior.

In short:

- **API/runtime smoke health:** mostly good.
- **Environment physics/reward validity:** good under current tests.
- **Tower-evaluation validity:** compromised for every evaluation environment
  except `plate_support_env`.
- **Most serious regression:** `rl_counterpoint_v3` previously documented a
  tower-depth reality check of `max_depth = 15`; after the refactor, the same
  probe now reports `max_depth = 1`.

This is exactly the kind of post-refactor semantic failure that tests can miss:
the examples still run, but most are no longer evaluating induced hierarchy.

## What Changed Architecturally

Before the refactor, tower construction was driven by the legacy dynamic builder
and local-star contraction policies. The old `SeededRandomContractionPolicy`
could induce nontrivial depth in the tower-depth probe.

After the refactor:

- `TowerRuntime` defaults to the partition backend.
- The partition backend contracts edges only through `ContractionSchema`
  assignments.
- `ContractionPolicy` still exists, but it is no longer the authoritative
  contraction schedule for the partition tower.
- If no schema is supplied, `TowerRuntime` uses `NoContractionSchema`.
- A runtime can therefore accept a `contraction_policy`, run successfully, and
  still never build any nontrivial quotient tiers.

That is the central compatibility break for the evaluation environments.

## Investigation Scope

Environment families inspected:

- `plate_support_env`
- `articulated_loop_env`
- `parallelogram_singularity_env`
- `cable_parallel_env`
- `dual_arm_manipulation_env`
- `rl_counterpoint_v3`
- `robot_constraint_toy` as a smaller schema smoke reference

Files inspected included:

- `src/state_collapser/examples/*/runtime.py`
- `src/state_collapser/examples/*/training.py`
- `src/state_collapser/examples/*/env.py`
- `src/state_collapser/examples/tower_depth_probe.py`
- `tests/examples/test_*`
- `docs/design/test_design/env_*/*`
- `docs/design/test_design/rl_counterpoint_v3/*`

## Validation Commands Run

### Example Suite

Command:

```text
uv run pytest tests/examples
```

Result:

```text
138 passed
```

Interpretation:

- The environment APIs, transition logic, reward surfaces, Gymnasium wrappers,
  runtime smoke tests, and tower-training smoke tests all pass.
- This does **not** prove the environments still exercise nontrivial quotient
  structure.

### Tower-Depth Probe With Explicit Environment Names

Command:

```text
uv run python -m state_collapser.examples.tower_depth_probe \
  plate_support_env articulated_loop_env dual_arm_manipulation_env \
  cable_parallel_env parallelogram_singularity_env rl_counterpoint_v3 \
  --steps 20 --seed 7 --summary-only
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

The same command with `--no-contraction-policy` produced the same depths.

Interpretation:

- The old contraction-policy switch is no longer materially affecting tower
  depth.
- Only `plate_support_env` currently has a schema-driven nontrivial tower.

### Counterpoint Regression Reality Check

Historical evidence from
`docs/design/test_design/rl_counterpoint_v3/01_004_rl_counterpoint_v3_implementation_log.md`:

```text
continuous_probe(env_name='rl_counterpoint_v3', steps=40, seed=0, sample_size=1, use_contraction_policy=True, reset_on_terminal=True)
max_depth = 15
```

Current check:

```text
continuous_probe(env_name='rl_counterpoint_v3', steps=40, seed=0, sample_size=1, use_contraction_policy=True, reset_on_terminal=True)
max_depth = 1
```

Interpretation:

- This is a real semantic regression in the evaluation surface.
- It does not mean `rl_counterpoint_v3` is invalid as an environment.
- It does mean it is no longer currently validating induced tower behavior.

### Runtime Diagnostics Probe

A direct runtime inspection produced:

| Environment | Backend | Schema | Max Depth | Scheduled Schema Assignments |
| --- | --- | --- | ---: | ---: |
| `plate_support_env` | partition | `DimensionwiseSchema` | 2 | nonzero |
| `articulated_loop_env` | partition | `NoContractionSchema` | 1 | 0 |
| `dual_arm_manipulation_env` | partition | `NoContractionSchema` | 1 | 0 |
| `cable_parallel_env` | partition | `NoContractionSchema` | 1 | 0 |
| `parallelogram_singularity_env` | partition | `NoContractionSchema` | 1 | 0 |
| `rl_counterpoint_v3` | partition | `NoContractionSchema` | 1 | 0 |

Interpretation:

- The runtimes are using the new backend.
- Most of them are not using the new contraction surface.
- Many discover edges, but schedule none of them for contraction.

## Findings

### Finding 1: Most Evaluation Environments Are Now Tower-Flat

Severity: High.

Affected:

- `articulated_loop_env`
- `parallelogram_singularity_env`
- `cable_parallel_env`
- `dual_arm_manipulation_env`
- `rl_counterpoint_v3`

These runtimes still construct `TowerRuntime(...)` with `contraction_policy`, but
without `contraction_schema`.

Because the partition backend defaults to `NoContractionSchema`, the result is
a depth-1 tower:

```text
G^0 only
```

The smoke-training loops still run because their state key is
`snapshot.current_position_at_every_tier`, and a one-tier tower still provides a
nonempty key. But from an evaluation standpoint, this is no longer a quotient
tower experiment. It is a tower-shaped wrapper around a flat runtime.

### Finding 2: `contraction_policy` Is Now Misleading In Example Runtimes

Severity: High.

Most runtime constructors still expose:

```python
contraction_policy: ContractionPolicy | None = None
```

But in the partition backend, this no longer schedules contractions. It can
still affect vista annotation/message behavior, but it does not determine tower
coarsening.

This matters because:

- `run_tower_training(..., contraction_policy=...)` appears to configure tower
  construction.
- `tower_depth_probe` appears to compare contraction-policy versus no-policy
  behavior.
- Under the partition backend, those policy knobs do not produce nontrivial
  tower depth unless a schema is also supplied.

The current public/example API therefore creates a false sense that evaluation
experiments are still varying tower construction when they are not.

### Finding 3: `rl_counterpoint_v3` Lost Its Nontrivial Tower-Depth Reality Check

Severity: High.

`rl_counterpoint_v3` was explicitly documented as not being a flat dead surface
under the old package-owned dynamic tower path. The implementation log recorded:

```text
max_depth = 15
```

The same continuous probe now reports:

```text
max_depth = 1
```

This is the clearest concrete evidence that the post-refactor environment suite
still passes while losing a major intended evaluation property.

The root cause is not the counterpoint transition system. The root cause is that
the runtime no longer receives a schema capable of scheduling any contractions.

### Finding 4: `plate_support_env` Is The Only Evaluation Env Currently Migrated To Schema-Driven Tower Construction

Severity: Medium.

`plate_support_env` was adjusted during the Young diagram refactor:

- hidden graph edges receive the label `"plate-support-transition"`
- `PlateSupportEnvRuntime` supplies
  `DimensionwiseSchema(("plate-support-transition",))`
- reset/step probes report max depth `2`
- exploit/explore tests expecting at least two tiers pass

This environment is therefore the only one currently exercising nontrivial
partition-tower construction by default.

This does not prove its schema is the final scientifically best schema. It does
mean it has crossed the minimum compatibility threshold.

### Finding 5: Existing Example Tests Are Too Weak For Post-Refactor Tower Semantics

Severity: Medium.

The tests generally assert:

- env transitions are valid
- rewards work
- runtime snapshots exist
- `current_position_at_every_tier` is nonempty
- training loops produce nonempty Q-tables

They usually do **not** assert:

- max tower depth is greater than `1`
- schema assignments are scheduled
- a labeled or structured edge family actually contracts
- the tower-depth probe changes under schema/policy settings
- training is keyed by a nontrivial coarse tier rather than only tier `0`

That is why `tests/examples` can pass while most evaluation environments are
tower-flat.

### Finding 6: `tower_depth_probe` Has A CLI Default-Env Bug

Severity: Low to Medium.

The parser says env names are optional and should default to all supported
environments. But this command fails:

```text
uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --summary-only
```

Observed failure:

```text
argument envs: invalid choice: [] (...)
```

The probe works when env names are supplied explicitly.

This is not caused by the Young diagram refactor directly, but it matters now
because tower-depth probing is one of the most useful diagnostic tools for this
exact post-refactor audit.

### Finding 7: The Probe's Policy Flag Is Now Semantically Outdated

Severity: Medium.

`tower_depth_probe` still has:

```text
--no-contraction-policy
--sample-size
```

Those controls made sense when local-star contraction policy drove the old
dynamic builder. Under the partition backend, the important control is a
contraction schema.

The probe should now expose either:

- a schema option,
- per-environment default schemas,
- or a clearly named legacy-policy mode.

Otherwise the probe is testing a knob that no longer controls tower coarsening.

## Environment-By-Environment Assessment

### `plate_support_env`

Status: Healthy enough after migration.

Evidence:

- Uses partition backend.
- Supplies `DimensionwiseSchema(("plate-support-transition",))`.
- Reaches depth `2`.
- Example tests pass.
- Exploit/explore runtime tests expecting at least two tiers pass.

Risk:

- The current schema is broad: every visible plate-support transition is in the
  same contraction block. This is sufficient as a compatibility schema, but may
  be too blunt for serious benchmark claims.

Recommendation:

- Keep current schema as the smoke/default schema.
- Later benchmark work should test more structured schemas, likely based on
  support extension mode, plate pose change, or constraint family.

### `articulated_loop_env`

Status: Functional but tower-flat.

Evidence:

- Uses partition backend.
- Uses `NoContractionSchema`.
- Reaches max depth `1`.
- Tests pass because they do not require nontrivial quotient tiers.

Why this matters:

- The environment was designed around loop-closure constraints, which should
  plausibly provide quotientable structure.
- It currently does not test that structure through the new partition runtime.

Recommendation:

- Add edge labels and a default schema aligned with action/geometry families.
- Add a depth or scheduled-assignment test.

### `parallelogram_singularity_env`

Status: Functional but tower-flat.

Evidence:

- Uses partition backend.
- Uses `NoContractionSchema`.
- Reaches max depth `1`.

Why this matters:

- The environment was intended to test hidden structural bottlenecks.
- A depth-1 tower cannot test bottleneck quotient behavior.

Recommendation:

- Add labels/schemas for singularity-relevant motion families or bottleneck
  transitions.
- Add a probe test that asserts at least one nontrivial tier appears under the
  default schema.

### `cable_parallel_env`

Status: Functional but tower-flat.

Evidence:

- Uses partition backend.
- Uses `NoContractionSchema`.
- Reaches max depth `1`.
- Discovers edges during probes, but schedules zero contractions.

Why this matters:

- The environment is supposed to test a hidden feasible region inside a product
  state space.
- With no schema, it is currently only a flat runtime/training smoke surface.

Recommendation:

- Add cable-mode or tension/slack-family labels.
- Add schema-aware runtime constructor support.

### `dual_arm_manipulation_env`

Status: Functional but tower-flat.

Evidence:

- Uses partition backend.
- Uses `NoContractionSchema`.
- Reaches max depth `1`.

Why this matters:

- The design docs identify hidden coordination geometry and likely repeated
  quotientable local structure.
- Current runtime does not exercise those structures.

Recommendation:

- Add action/coordination labels and a schema that contracts one meaningful
  coordination family first.
- Add tests for nonzero scheduled assignments.

### `rl_counterpoint_v3`

Status: Functional but semantically regressed as a tower-evaluation example.

Evidence:

- Uses partition backend.
- Uses `NoContractionSchema`.
- Reaches max depth `1`.
- Historical implementation log recorded `max_depth = 15`.

Why this matters:

- The whole point of this example is that the flat counterpoint problem has
  hidden hierarchy pressure without importing the old hand-authored rank tower.
- A no-schema partition runtime does not induce that hierarchy.

Recommendation:

- Do **not** reintroduce the old explicit rank tower.
- Instead, add a package-facing schema derived from neutral edge/action facts:
  for example voice-motion family, interval-class change family, contrary/oblique
  motion family, or legality/reward-feature labels.
- Add a post-refactor version of the old tower-depth reality check. It does not
  need to require `max_depth = 15`, because the new semantics are different, but
  it should require nontrivial depth under an approved schema.

### `robot_constraint_toy`

Status: Healthy as a small schema smoke reference.

Evidence:

- A test now explicitly constructs `TowerRuntime` with
  `DimensionwiseSchema(("hinge",))`.
- The labeled hinge vista edge contracts at tier `1`.

Risk:

- This is not one of the big evaluation environments, but it is useful as a
  minimal template for how the larger envs should be migrated.

## Recommended Fix Plan

### Phase 1: Repair The Public Evaluation Runtime Surface

For each evaluation runtime:

- add an optional `contraction_schema` constructor parameter
- preserve `contraction_policy` only for annotation/vista policy compatibility
- choose a default schema only when there is a clear first-scope environment
  schema
- otherwise make flat/no-schema behavior explicit in docs/tests

Target files:

- `src/state_collapser/examples/articulated_loop_env/runtime.py`
- `src/state_collapser/examples/parallelogram_singularity_env/runtime.py`
- `src/state_collapser/examples/cable_parallel_env/runtime.py`
- `src/state_collapser/examples/dual_arm_manipulation_env/runtime.py`
- `src/state_collapser/examples/rl_counterpoint_v3/runtime.py`

### Phase 2: Add Edge Labels Or Schema Inputs

Most hidden graph bindings currently create unlabeled `BaseEdge` objects. That
means label/dimension schemas have nothing environment-specific to inspect.

Each environment needs either:

- edge labels attached in `HiddenGraph.out_edges(...)`, or
- a schema that assigns edges based on source/target/action identities and state
  payloads.

For readability and auditability, labels are probably the better first repair.

### Phase 3: Update `tower_depth_probe`

The probe should be updated so it is no longer policy-centric.

Recommended changes:

- fix the no-env CLI default bug
- add schema-aware probe configuration
- report schema name, backend, max depth, and scheduled assignment count
- preserve legacy policy controls only as annotation/legacy controls

### Phase 4: Strengthen Tests

Add tests that fail if environments silently become tower-flat again.

For each schema-enabled evaluation environment, add assertions such as:

```python
assert len(snapshot.current_position_at_every_tier) >= 2
assert runtime.tower_runtime.last_tower_update_result is not None
assert any(
    assignment.block_id is not None
    for assignment in runtime.tower_runtime.last_tower_update_result.schema_assignments
)
```

For `tower_depth_probe`, add an explicit test that an approved schema-enabled
environment reaches nontrivial depth.

For `rl_counterpoint_v3`, restore a reality check similar to the old one, but
with a new threshold appropriate to the partition schema.

### Phase 5: Reclassify Any Intentionally Flat Examples

If any environments are intentionally meant to remain flat baselines, say so
explicitly. Do not let a flat runtime masquerade as quotient-tower evaluation.

Possible categories:

- flat environment validity example
- tower-runtime smoke example
- schema-enabled quotient evaluation environment
- benchmark candidate

Right now the categories are blurred.

## Bottom Line

The environments are not "fucked" in the sense of failing tests or broken
transition/reward mechanics.

They are "fucked" in the more important evaluation sense for this project:
most of them no longer exercise meaningful quotient-tower behavior after the
Young diagram refactor.

This is fixable. The repair is not to undo the Young diagram refactor. The
repair is to migrate the evaluation environments from policy-driven contraction
assumptions to explicit schema-driven partition-tower construction.

