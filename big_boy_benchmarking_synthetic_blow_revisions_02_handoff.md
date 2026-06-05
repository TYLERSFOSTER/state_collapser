# big_boy_benchmarking Handoff: Synthetic Blow Revisions 02

Date: 2026-06-04

Status: downstream handoff note after upstream implementation

Upstream authority:

```text
docs/design/synthetic_blow_revisions_02/01_001_synthetic_blow_revisions_02_blueprint.md
docs/design/synthetic_blow_revisions_02/01_002_synthetic_blow_revisions_02_implementation_gameplan.md
docs/code_review/03_001_synthetic_blow_full_repo_review_current_state.md
```

## Purpose

This note tells `big_boy_benchmarking` engineers what the Synthetic Blow
Revisions 02 hardening pass changed in `state_collapser`, what downstream
benchmark code may safely use, and what should not be assumed.

The implementation is intentionally narrow. It is not a benchmark-harness
rewrite and it is not a new learner stack. It is a trust-and-correctness pass
around existing upstream surfaces that `big_boy_benchmarking` may reasonably
depend on.

## Upstream Changes

### 1. NumPy Observation Linearization

`state_collapser` now supports numeric NumPy observations at the
backend-independent linearization boundary.

Implemented behavior:

- numeric `np.ndarray` observations linearize to tuple-like float feature data;
- metadata records observation kind, shape, and dtype;
- NumPy is imported lazily, not as a mandatory base-package import;
- unsupported arrays fail in strict mode;
- unsupported arrays become non-feature sidecar metadata in non-strict mode.

Observation metadata keys:

```text
kind
shape
dtype
dtype_kind
unsupported_observation_repr
```

`dtype_kind` and `unsupported_observation_repr` appear for unsupported NumPy
arrays. Supported numeric arrays record `kind`, `shape`, and `dtype`.

Downstream meaning:

- `big_boy_benchmarking` may use real NumPy observations from RL-like
  environments when testing linearization;
- benchmark code should not expect the linearized observation to remain a NumPy
  array;
- benchmark code should not assume Torch is involved.

### 2. Partition Source-Support Invariant Checking

`state_collapser` now exposes explicit invariant-reporting/assertion surfaces
for partition/action source-support tables.

Implemented APIs:

```python
PartitionTower.invariant_report(allow_dirty=False)
PartitionTower.assert_consistent(allow_dirty=False)
ActionPartitionLayer.invariant_report(
    state_layer=...,
    registry=...,
    lower_state_layer=...,
    lower_action_layer=...,
    allow_dirty=False,
)
ActionPartitionLayer.assert_consistent(
    state_layer=...,
    registry=...,
    lower_state_layer=...,
    lower_action_layer=...,
    allow_dirty=False,
)
```

Report types exported from `state_collapser.tower.partition`:

```python
PartitionInvariantIssue
PartitionInvariantReport
action_layer_invariant_report
```

Implemented invariant coverage:

- state cells point to live outgoing action collections;
- action collections point to live action cells;
- action cells map back consistently through edge indexes;
- source and target state-cell indexes match current partition layers;
- internal loops are excluded from live quotient action cells;
- adjacent-tier source-support maps are consistent;
- flattened base-source caches are consistent with recursive support;
- dirty collections are detected unless explicitly allowed.

Important runtime-history detail:

`state_collapser` retains some historical collection and internal-edge records
after merges. The invariant checker treats historical unattached collections
without live action cells as allowed, and checks internal-edge geometry only for
active state cells while still checking record/key consistency.

Downstream meaning:

- use invariant checks as debug/preflight validation around suspicious tower
  construction or update failures;
- do not run invariant checks inside timed benchmark hot loops unless the
  benchmark is explicitly measuring validation overhead;
- if an invariant failure appears after normal construction/update, treat it as
  an upstream correctness issue, not benchmark noise.

### 3. Explicit Concrete Lift Selection

`FiberConditionedStage` now exposes a concrete lift-selection hook.

Current behavior remains deterministic first-candidate selection. The difference
is that the policy is now explicit and replaceable.

Implemented API:

```python
LiftSelector
deterministic_first_lift_selector(...)
FiberConditionedStage(..., lift_selector=...)
```

Selector signature:

```python
Callable[[tuple[BaseEdge, ...], ActionSelectionInput, ActionCellId], BaseEdge]
```

Implemented behavior:

- default selector chooses the first executable lift candidate;
- custom selector can choose another candidate from the available tuple;
- invalid selector output raises a clear error;
- transition diagnostics include lift-selection information.

Transition diagnostics keys:

```text
lift_candidate_count
selected_lift_index
lift_selector
fiber_action_cell
realized_edge
```

Downstream meaning:

- if benchmark code is happy with deterministic first-candidate behavior, no
  selector change should be needed;
- if a benchmark needs a specific concrete lift policy, pass a custom selector
  rather than depending on tuple order implicitly;
- if benchmark log parsers inspect transition diagnostics, account for the new
  lift-selection keys in current upstream transitions.

### 4. Mandatory Dependency Cleanup

The review identified `pillow` as an unused mandatory dependency.

Implemented behavior:

- `pillow` was removed from base dependencies;
- `uv.lock` was updated;
- the package still validates with the current `dev` and `rl` extras.

Downstream meaning:

- if `big_boy_benchmarking` uses Pillow directly, it should declare its own
  dependency;
- do not rely on `state_collapser` to transitively install visualization
  libraries unless the package explicitly exposes that dependency through an
  optional extra.

### 5. Small Front-Door Documentation Cleanup

Upstream docs now align release/version and current artifact language.

Downstream meaning:

- no benchmark behavior should change from this alone;
- if downstream documentation quotes upstream install instructions, refresh
  those references to the current `v0.7.2` tag language.

## Explicit Non-Changes

The following are not part of this upstream pass:

- no serious benchmark artifact system;
- no JSON/CSV benchmark table contract;
- no replay buffer;
- no checkpoint/resume surface;
- no vectorized rollout framework;
- no experiment manifest system;
- no Torch CI expansion;
- no package-owned neural policy model family;
- no full tower-augmented Gymnasium wrapper;
- no direct implementation inside `big_boy_benchmarking`.

If downstream work needs any of those, treat it as separate design work.

## Recommended Downstream Response

1. Update the `state_collapser` dependency to the `v0.7.2` release tag.
2. Run existing `big_boy_benchmarking` smoke and regression checks.
3. Add optional preflight calls to `tower.assert_consistent(...)` around tower
   construction/update diagnostics, but keep them out of timed hot loops.
4. Add one focused NumPy-observation linearization check if benchmark fixtures
   currently emit NumPy arrays.
5. If benchmark code uses `FiberConditionedStage`, decide whether deterministic
   first lift is acceptable or whether a benchmark-specific selector should be
   passed explicitly.
6. If downstream code relied on transitive Pillow installation, add a direct
   downstream dependency.

## Watchpoints

- If invariant checks report stale flattened base-source caches, that should be
  escalated as an upstream source-support bug.
- If a custom lift selector is introduced downstream, its output must be one of
  the executable lift candidates supplied by upstream.
- NumPy linearization is not tensor batching. It is backend-independent numeric
  record construction.
- This pass hardens existing benchmark-adjacent surfaces; it does not replace
  the future serious benchmark artifact contract.

## Attribution

The Project Owner scoped this pass by striking through larger framework and
benchmark-harness work, preserving only the correctness/hardening items that
matter immediately.

The earlier `big_boy_benchmarking` diagnostic stream helped expose why
pointwise liftability and source-support invariants matter downstream.

Codex generated this handoff to keep downstream benchmark engineers aligned
with the upstream `state_collapser` implementation plan without expanding the
upstream scope.
