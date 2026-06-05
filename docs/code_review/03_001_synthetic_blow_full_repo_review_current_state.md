# synthetic_blow review

Generated: 2026-06-04

Scope: full repository review of the current `state_collapser` checkout, using
`docs/code_review/synthetic_blow_review_kit/synthetic_blow.md` as the review
rubric.

Review identity rule: this is a Jonathan-Blow-inspired engineering lens, not an
impersonation. The standard here is direct, performance-aware, skeptical of
unnecessary abstraction, and focused on concrete data flow.

Local validation performed during this review:

- `uv run ruff check .`: passed.
- `uv run mypy src`: passed, with no issues in 90 source files.
- `uv run pytest`: passed, with `503 passed, 4 skipped`.
- `uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only`: passed.

Important validation caveat:

- The four skipped pytest cases were all Torch optional-boundary tests:
  `tests/examples/test_torch_tensor_boundary_smoke_model.py` and
  `tests/training/test_torch_batches.py`.
- CI currently installs `dev` and `rl`, not `ml`, so the optional Torch boundary
  is not exercised by the default GitHub Actions job either
  (`.github/workflows/ci.yml:27` through `.github/workflows/ci.yml:37`).

Working-tree caveat:

- At review start, the branch was `main...origin/main [ahead 5]`.
- Two unrelated untracked files were present and were not reviewed as source:
  `logHRL_bin.bib` and `tropicalization_and_binary_coset_towers_comments.tex`.

## Verdict

This repository has moved out of the "toy scaffold" category. The core package
now has a real partition-backed tower runtime, pointwise executable lift
queries, lazy compatibility readouts, Gymnasium hook surfaces, training inputs,
collectors, continuation-aware transitions, fiber-conditioned stages,
backend-independent linearization, optional Torch batch conversion, HGraphML
compatibility tests, and a smoke benchmark surface. The local quality gates are
green.

But it is still not a mature RL framework, and the code should not pretend
otherwise. The real risk is not that the package is empty. The real risk is that
it has just enough serious-looking infrastructure to let a reader assume things
that are not yet true: Torch is advertised but not CI-exercised, linearization is
present but does not yet accept the NumPy observations emitted by the package's
own Gymnasium examples, benchmarking is runnable but not artifacted, and the
training surfaces are correct reference surfaces rather than replay/checkpointed
neural learner infrastructure.

The good news is that the repo is honest in many places. `CONTRIBUTING.md:30`
through `CONTRIBUTING.md:70` says the next work is benchmark/artifact
integration, manifests, replay design, vectorized rollout, checkpoint/resume,
and downstream harnesses. `EVALUATION.md:19` through `EVALUATION.md:23` admits
that polished benchmarking and broad empirical claims are not yet in place. The
root README calls the repo pre-alpha at `README.md:278` through `README.md:302`.
That honesty matters.

The current standard should be:

- Do not add more framework surface until the current data path is measured.
- Do not claim optional Torch support is validated until CI installs `ml`.
- Do not let tensorization become a pile of Python-object conversion overhead in
  the hot path.
- Do not let quotient actions drift away from pointwise executable lifts again.
- Do not call smoke benchmarks evidence.

Compared to the previous full synthetic review, several important old complaints
have been fixed or materially improved:

- Gymnasium hook support now exists in `src/state_collapser/adapters/gymnasium.py`.
- `terminated` and `truncated` semantics are explicit in collectors and
  transitions.
- The runtime now has strict pointwise executable-lift queries rather than only
  quotient representative fallback.
- Compatibility quotient readouts are lazy instead of being built in the default
  partition hot path.
- HGraphML is now protected by an upstream compatibility test.

That is real progress. The remaining hard parts are now much more concrete.

## Program map

The source tree currently breaks down as follows.

`src/state_collapser/core` is the basic value layer: states, primitive actions,
base edges, rewards, labels, and annotations. This layer is small and mostly
uncontroversial.

`src/state_collapser/graph` contains hidden graphs, explored graphs, local-star
data, and vista graphs. This is the environment/discovery side of the package.
It gives the runtime a way to distinguish the hidden transition system from the
currently discovered graph.

`src/state_collapser/contract` is the older contraction-policy and action
selection area. It still matters for legacy/runtime compatibility, but it is no
longer the package's central construction mechanism.

`src/state_collapser/quotient` is the quotient-view layer: cosets, projections,
and `QuotientTierView`. In the current architecture, these are compatibility and
readout surfaces, not the main mutable runtime representation.

`src/state_collapser/tower/partition` is the real center of the repo. It contains
the state and action partition tables, base graph registry, schema machinery,
loop/internal-edge policy, reward aggregation, partition-tower update logic,
readout conversion, and source-support/executable-lift queries.

`src/state_collapser/tower/runtime.py` is the exploration runtime. It owns the
mutable explored graph, vista graph, partition tower, optional morphism capture,
lazy quotient readout cache, and current runtime view. It also contains the
active-tier exploit/explore runtime.

`src/state_collapser/tower/control` is the first active-tier controller stack:
active-tier state, config, signals, executor, learner protocol, metrics, and
transition objects. It is a reference control stack, not a mature RL training
framework.

`src/state_collapser/training` is the reusable training-facing surface:
`ActionSelectionInput`, `ActionDecision`, masks, continuation/bootstrap
semantics, training transitions, collectors, reference loops, a tabular learner,
fiber-conditioned training, linearization, and optional Torch conversion.

`src/state_collapser/adapters/gymnasium.py` provides a hook-based wrapper around
Gymnasium-like environments. It records realized transitions into an
`ExploredGraph`; it does not yet turn arbitrary Gymnasium environments into full
tower-augmented training surfaces by itself.

`src/state_collapser/benchmarks/tower_runtime_bench.py` is a small CLI smoke
benchmark. It can check that runtime/readout flags and basic timing machinery
work, but it is not yet an empirical benchmarking harness.

`src/state_collapser/examples` contains the testbed environments. The examples
are now a serious part of the package because they test tower runtime behavior,
schema behavior, training surfaces, and action boundary semantics.

`docs/usage`, `docs/api_notes`, `README.md`, `CONTRIBUTING.md`, and
`EVALUATION.md` have become the front-door documentation. The design-doc tree is
large and useful, but it also contains stale design-era artifacts and generated
PDFs.

## The real data path

The real runtime path is not "train an RL algorithm." It is:

1. A hidden or Gymnasium-like environment produces states, observations, actions,
   rewards, and episode flags.
2. The package records discovered state/action graph structure through
   `ExploredGraph` and `VistaGraph`.
3. `TowerRuntime` maintains a partition-backed tower over the discovered graph.
4. `PartitionTower` updates state-cell and action-cell partitions incrementally
   as new states and edges arrive.
5. Training code reads `LiveRuntimeView`, not a globally reconstructed quotient
   graph.
6. `ActionSelectionInput` packages observation, runtime snapshot, masks, tower
   position, stage/fiber context, and diagnostics for a learner.
7. A learner returns an `ActionDecision`.
8. A collector or `FiberConditionedStage` resolves that decision to a primitive
   executable action, steps the runtime, and records a `TrainingTransition`.
9. Optional linearization converts semantic records into backend-independent
   numeric records.
10. Optional Torch conversion converts linearized records into `TorchDecisionBatch`
    or `TorchTransitionBatch`.

The most important split is between quotient availability and executable
availability.

`PartitionTower.lift_candidates(...)` at `src/state_collapser/tower/partition/tower.py:284`
through `src/state_collapser/tower/partition/tower.py:302` preserves the older
representative fallback semantics for readout/reasoning. That is useful, but it
is not safe as an execution rule.

The strict execution surface is
`PartitionTower.executable_lift_candidates(...)` at
`src/state_collapser/tower/partition/tower.py:304` through
`src/state_collapser/tower/partition/tower.py:324`, plus
`executable_action_cells(...)` and `tier_is_executable_from_state(...)` at
`src/state_collapser/tower/partition/tower.py:326` through
`src/state_collapser/tower/partition/tower.py:365`.

That distinction is essential. A quotient action may exist because some member
of a coset has an outgoing edge. It is only executable from the current base
state if the current base state is one of the source supports for that action
cell. The code now understands this.

The second important split is between runtime maintenance and compatibility
readout.

`TowerRuntime.compatibility_quotient_tiers(...)` at
`src/state_collapser/tower/runtime.py:218` through
`src/state_collapser/tower/runtime.py:229` builds quotient views lazily. The
default runtime path keeps the partition tower as the source of truth and avoids
eager quotient materialization. That is the right direction.

The third important split is between semantic records and tensors.

`state_collapser.training.linearization` does not import Torch and defines
`LinearizationConfig`, `LinearizationReport`, `EncodingRegistry`, and linearized
records. `state_collapser.training.torch` is downstream of that and imports
Torch only when used. This is the right architecture. The problem is that this
boundary is not yet fully integrated into CI, NumPy observations, or benchmark
artifacts.

## Highest-severity issues

### ~~1. High: The optional Torch boundary is not exercised by default CI~~

The repo has an optional model-backend surface under
`src/state_collapser/training/torch.py`, and `pyproject.toml:54` through
`pyproject.toml:56` define the `ml` extra with `torch>=2.4.0`.

The tests exist:

- `tests/training/test_torch_batches.py:51` through
  `tests/training/test_torch_batches.py:111`.
- `tests/examples/test_torch_tensor_boundary_smoke_model.py:17` through
  `tests/examples/test_torch_tensor_boundary_smoke_model.py:66`.

But every one of those tests uses `pytest.importorskip("torch")`. Local pytest
completed with `503 passed, 4 skipped`, and the skipped cases are exactly these
Torch tests.

CI currently installs only `dev` and `rl`:

- `.github/workflows/ci.yml:27` through `.github/workflows/ci.yml:28`.
- The test command at `.github/workflows/ci.yml:36` through
  `.github/workflows/ci.yml:37` therefore also skips Torch tests.

This creates a bad release posture. The README and changelog can honestly say
"optional Torch conversion exists," but the default public CI badge does not
prove that surface. It proves only that the optional Torch tests skip cleanly
when Torch is absent.

The fix is not complicated:

- Add a second CI job or matrix axis that runs `uv sync --extra dev --extra rl --extra ml`.
- In that job, run at least `uv run pytest tests/training/test_torch_batches.py tests/examples/test_torch_tensor_boundary_smoke_model.py`.
- Keep the non-ML job too, because it proves Torch is not accidentally required
  by base or RL users.

Until that exists, any Torch wording should be read as "implemented and locally
testable when the optional extra is installed," not "continuously verified."

### 2. High: First-scope linearization does not accept the package's own NumPy observations

The backend-independent linearization boundary is currently too narrow for the
example environments it is supposed to support.

`_linearize_observation(...)` handles bools, ints, floats, lists, and tuples:

- `src/state_collapser/training/linearization.py:973` through
  `src/state_collapser/training/linearization.py:996`.

It does not handle `np.ndarray`.

The package's own Gymnasium examples emit NumPy arrays. For example,
`PlateSupportEnv` encodes observations with `np.asarray(..., dtype=np.int64)` at
`src/state_collapser/examples/plate_support_env/env.py:46` through
`src/state_collapser/examples/plate_support_env/env.py:52`, and `reset`/`step`
return that encoded NumPy observation at
`src/state_collapser/examples/plate_support_env/env.py:396` through
`src/state_collapser/examples/plate_support_env/env.py:441`.

Other example envs follow the same pattern:

- `src/state_collapser/examples/articulated_loop_env/env.py:44`.
- `src/state_collapser/examples/cable_parallel_env/env.py:50`.
- `src/state_collapser/examples/dual_arm_manipulation_env/env.py:51`.
- `src/state_collapser/examples/parallelogram_singularity_env/env.py:44`.
- `src/state_collapser/examples/rl_counterpoint_v3/env.py:159`.

The tests for linearization avoid the issue by using tuple observations, for
example `tests/training/test_linearized_records.py:123` through
`tests/training/test_linearized_records.py:125`.

This is a real boundary bug. The PO explicitly wanted NumPy to be the
backend-independent numeric layer, while Torch stays optional behind the `ml`
extra. But the current implementation treats actual NumPy arrays from the
package's own RL examples as unsupported observation objects.

The fix should be local and conservative:

- Add an optional NumPy import check inside `linearization.py`, not at package
  import time.
- If the observation is a numeric `np.ndarray`, flatten it to a tuple of floats.
- Record at least shape and dtype in observation metadata.
- Reject object/string arrays in strict mode.
- Add a test that builds a real `PlateSupportEnv` reset observation and
  linearizes it.
- Keep non-strict sidecar behavior for unsupported observation types.

Do not solve ragged tensorization here. This is not a request for a whole tensor
framework. It is a request to support the obvious fixed-discrete NumPy array
path that the package already emits.

### ~~3. High: The benchmark surface is smoke tooling, not serious benchmarking~~

`src/state_collapser/benchmarks/tower_runtime_bench.py` is useful, but tiny.

It runs a deterministic small `plate_support_env` loop, records elapsed time,
state/edge counts, tower depth, and flags. That is good as a smoke test:

- `src/state_collapser/benchmarks/tower_runtime_bench.py:50` through
  `src/state_collapser/benchmarks/tower_runtime_bench.py:108`.

But it is not a benchmark harness:

- It does not emit JSON/CSV artifacts.
- It does not persist package version, git commit, schema config, seed sets, or
  linearization reports.
- It does not run scaling curves.
- It does not compare readout-disabled/readout-enabled across repeated seeds.
- It does not compare morphism-disabled/morphism-enabled across repeated seeds.
- It does not attach `LinearizationConfig` or `LinearizationReport`.
- It uses one tiny environment by default.
- It mutates a private runtime field at
  `src/state_collapser/benchmarks/tower_runtime_bench.py:73`:
  `tower_runtime._build_morphism = morphism_requested`.

The docs are honest about this. `EVALUATION.md:19` through `EVALUATION.md:23`
and `EVALUATION.md:466` through `EVALUATION.md:483` say the benchmark platform
is not finished. `CONTRIBUTING.md:62` through `CONTRIBUTING.md:70` says the next
benchmarking stage should persist configs, reports, labels, seeds, and versions.

So this is not a documentation contradiction. It is a release-readiness gap.

The next serious step should be a benchmark artifact contract:

- A `BenchmarkRunConfig` with environment, mode, schema, seed, step budget,
  readout/morphism/tensorization flags, and version metadata.
- A `BenchmarkRunResult` with timings, counts, failure status, and optional
  `LinearizationReport`.
- A JSON writer and a no-artifact smoke mode.
- A public runtime config or constructor path for morphism mode, instead of
  touching `_build_morphism`.

Do not pile in a huge benchmarking framework. Build the artifact spine first.

### ~~4. Medium-high: The training layer is correct for research surfaces, but it is not a serious replay/checkpoint/manifest system~~

The first training surfaces are much better than nothing. `StepCollector`
checks action masks, preserves `terminated`/`truncated`, and records bootstrap
semantics at `src/state_collapser/training/collectors.py:124` through
`src/state_collapser/training/collectors.py:187`. `TabularQLearner` respects
source masks at `src/state_collapser/training/learners.py:77` through
`src/state_collapser/training/learners.py:97`, and uses
`bootstrap_allowed`/target masks at `src/state_collapser/training/learners.py:116`
through `src/state_collapser/training/learners.py:147`.

The problem is not that these surfaces are wrong. The problem is that they are
not enough for the package to be mistaken for an RL framework.

The learner stores replay as a Python list:

- `src/state_collapser/training/learners.py:57` through
  `src/state_collapser/training/learners.py:58`.

It updates only from the last observed transition:

- `src/state_collapser/training/learners.py:104` through
  `src/state_collapser/training/learners.py:147`.

There is no serious replay buffer, no vectorized rollout storage, no checkpoint
payload, no optimizer state, no RNG state, no experiment manifest, no artifact
directory contract, and no resumed-run semantics.

The repo says this already. `CONTRIBUTING.md:30` through `CONTRIBUTING.md:40`
calls these future work. That is the correct posture.

The next step should not be "add PPO." The next step should be a minimal
experiment-manifest and artifact payload that can carry:

- environment name and config
- schema config
- seed
- git commit
- package version
- benchmark/training settings
- `LinearizationConfig`
- `LinearizationReport`
- optional learner/checkpoint metadata

If the package gets that right, serious learners can attach without forcing
`state_collapser` to become RLlib or Stable-Baselines3.

### 5. Medium-high: The partition action layer is a central mutable index system with no single invariant checker

`ActionPartitionLayer` is doing the hardest runtime work. It maintains outgoing
collections, action cells, source cells, target cells, child-source support,
base-source support, edge-to-action-cell indexes, dirty collections, and
internal-edge records:

- `src/state_collapser/tower/partition/action_layer.py:44` through
  `src/state_collapser/tower/partition/action_layer.py:109`.

It merges collections at
`src/state_collapser/tower/partition/action_layer.py:227` through
`src/state_collapser/tower/partition/action_layer.py:303`.

It rebuilds action cells at
`src/state_collapser/tower/partition/action_layer.py:305` through
`src/state_collapser/tower/partition/action_layer.py:400`.

It clears obsolete indexes at
`src/state_collapser/tower/partition/action_layer.py:487` through
`src/state_collapser/tower/partition/action_layer.py:504`.

This complexity is justified by the algorithm. It is not random ceremony. The
pointwise liftability fix needs these source-support indexes.

But this is exactly the sort of mutable data structure that can pass many unit
tests and still hide a stale-index bug. The current test suite is strong for a
pre-alpha repo: full/incremental equivalence tests, pointwise liftability tests,
degenerate-tier tests, HGraphML compatibility tests, action-layer tests, schema
tests, and runtime tests all exist. Still, there is no obvious
`assert_consistent()` or diagnostic invariant method that checks the whole
action-layer index system in one place.

The next hardening step should be a debug/invariant checker, used heavily in
tests and optionally in debug benchmarks. It should verify at least:

- every action cell listed by a collection exists in `edge_ids_by_action_cell`
- every edge in an action cell maps back through `action_cell_by_edge_id`
- source/target cells match the current state layer
- source-child support is consistent with edge sources
- base-source support is consistent with edge source ids
- dirty collections are either rebuilt or explicitly marked before readout
- internal edges are not exposed as live outgoing decision edges

Do not rewrite the partition tower just because it is complex. This is the
right complexity. But this complexity needs a hard invariant harness.

### 6. Medium: `FiberConditionedStage` hides the concrete lift-selection policy

`FiberConditionedStage.step(...)` resolves an abstract action cell into concrete
lift candidates and then chooses the first candidate:

- `src/state_collapser/training/stages.py:172` through
  `src/state_collapser/training/stages.py:196`.

This is deterministic and testable, but it is not a policy. If multiple
primitive edges realize the same abstract action cell from the current base
state, the current stage silently uses `lift_candidates[0]`.

That may be acceptable for the first package slice, but it should be named. This
choice affects exploration, training data distribution, and reproducibility. It
is especially important because `FiberConditionedStage` is supposed to be the
professional freeze-and-lift bridge.

The fix is small:

- Add an optional `lift_selector` hook.
- Default it to deterministic first-candidate selection.
- Put the selected candidate index/count in transition diagnostics.
- Add a test where an action cell has two concrete lifts and the selector picks
  the second.

This is not a request for a full hierarchical policy system. It is just making a
currently hidden decision explicit.

### ~~7. Medium: The Gymnasium wrapper is a realized-transition recorder, not a full tower-augmented environment wrapper~~

The Gymnasium wrapper is clear in code:

- `src/state_collapser/adapters/gymnasium.py:1` through
  `src/state_collapser/adapters/gymnasium.py:6`.
- `src/state_collapser/adapters/gymnasium.py:111` through
  `src/state_collapser/adapters/gymnasium.py:117`.

It records realized Gymnasium transitions into an `ExploredGraph`, attaches
metadata, and preserves the wrapped environment's action and observation spaces.

That is useful and correct. But it is not yet a `TowerRuntime` wrapper. It does
not build or update a partition tower around an arbitrary Gymnasium env, return
`LiveRuntimeView`, or produce tower-aware `ActionSelectionInput` by itself.

This is fine as long as docs keep the boundary clear. The danger is naming and
user expectation. A new engineer may see `StateCollapserGymWrapper` and assume
that installing the wrapper is enough to get tower-aware RL. It is not.

Possible next surface:

- Keep `StateCollapserGymWrapper` as the realized-transition recorder.
- Add a separate `TowerAugmentedGymRuntime` or similar only when the package is
  ready to own that stronger behavior.
- Require explicit `state_key`, `action_key`, mask, and label hooks. Do not try
  to infer state identity automatically from arbitrary observations.

The existing `CONTRIBUTING.md:385` through `CONTRIBUTING.md:405` mostly says
this already.

### 8. Low-medium: `pillow` is a mandatory dependency and appears unused by source code

`pyproject.toml:36` through `pyproject.toml:38` makes `pillow>=12.2.0` a base
dependency.

A source search found no package or test usage of `PIL`, `pillow`, or `Image`.
The only relevant hits are `pyproject.toml` and design/security docs discussing
the dependency.

This is not a functional bug. But for a package trying to keep the base runtime
small and research-source-install friendly, an unused mandatory dependency is
noise.

The fix is simple:

- Remove `pillow` from base dependencies if it is not used.
- If future visualization/instrumentation needs it, put it behind a
  visualization or instrumentation extra.

Do not carry dependencies for future intentions.

### 9. Low-medium: A few front-door docs are stale or over-specific

The docs are much better than they were, but a few drift points remain.

README install command still points at `v0.7.0`:

- `README.md:66` through `README.md:70`.

Package metadata is `0.7.1`:

- `pyproject.toml:7`.
- `src/state_collapser/_version.py:3`.
- `CITATION.cff:9`.

`docs/artifact_contracts.md` is stale. It says the project is entering the first
implementation phase at `docs/artifact_contracts.md:5` through
`docs/artifact_contracts.md:10`, and it still treats early blueprint/runtime
snapshot/toy environment artifacts as the registry's active center.

`README.md:304` through `README.md:320` lists `instrumentation/`, and
`CONTRIBUTING.md:355` through `CONTRIBUTING.md:362` points contributors at
instrumentation namespaces. But there are no files under
`src/state_collapser/instrumentation` in the current checkout.

None of this is a runtime blocker. But front-door docs should not make users do
unnecessary archaeology. The artifact contract doc should be rewritten around
current artifacts: benchmark outputs, linearization reports, manifests,
snapshots, HGraphML compatibility, and release/continuity records.

## Abstractions that should justify themselves or die

`PartitionTower`: justified. This is the package's actual algorithmic runtime
object. It is not a framework abstraction for its own sake.

`ActionPartitionLayer`: justified but dangerous. The data structure is central,
mutable, and nontrivial. It should stay, but it needs invariant checking and
benchmark coverage.

`LiveRuntimeView` versus `RuntimeSnapshot`: justified. Separating live references
from serializable values prevents accidental fake serialization and keeps the
runtime honest.

`EncodingRegistry`: justified. It is not just an RL observation encoder. It is
the shared numeric vocabulary for RL tensorization and HGraphML-style graph
message passing. That is a real domain concept.

`LinearizationConfig` and `LinearizationReport`: provisionally justified. They
will fully justify themselves only when benchmarks and manifests actually persist
them. Right now they are well-designed objects waiting for the artifact system
that proves their value.

`state_collapser.training.torch`: justified as an optional boundary, not as a
model family. It should remain downstream of linearization and behind the `ml`
extra. It needs CI coverage.

`StateCollapserGymWrapper`: justified if understood as a realized-transition
recorder. Not justified if marketed as a full tower-aware Gymnasium training
wrapper.

`TabularQLearner`: justified as a reference learner. It should not grow into a
real replay/checkpoint/model stack by accretion. If the package needs serious
learning, build the learner-facing contracts around data and artifacts, not by
turning this class into a framework.

`tower/control`: justified as a reference exploit/explore controller and
research surface. It should eventually either integrate cleanly with
`FiberConditionedStage` or be clearly documented as a separate reference stack.

`instrumentation/`: not yet justified as implemented source surface because it
is empty. It can remain as a planned namespace, but docs should not imply
implemented instrumentation tooling.

Mandatory `pillow`: not justified by current source. Move it or remove it.

## RL correctness traps

The old Gymnasium termination trap is handled well. `StepCollector` keeps
`terminated` and `truncated` separate and derives bootstrap semantics explicitly
at `src/state_collapser/training/collectors.py:161` through
`src/state_collapser/training/collectors.py:187`. `TabularQLearner` uses
`bootstrap_allowed` rather than collapsing everything to a single `done` bit at
`src/state_collapser/training/learners.py:125` through
`src/state_collapser/training/learners.py:131`.

The old action-mask trap is also handled well in the simple collector path.
`StepCollector.collect_step(...)` rejects masked-off actions before stepping at
`src/state_collapser/training/collectors.py:131` through
`src/state_collapser/training/collectors.py:140`.

The old quotient-action trap is improved. The package now distinguishes
representative/readout lift candidates from strict executable lift candidates.
The pointwise tests at `tests/tower/partition/test_pointwise_liftability.py:154`
through `tests/tower/partition/test_pointwise_liftability.py:170` are exactly
the right kind of regression protection.

The degenerate-tier trap is improved. The controller now lifts through
non-executable tiers at `src/state_collapser/tower/runtime.py:552` through
`src/state_collapser/tower/runtime.py:578`, and
`tests/tower/partition/test_degenerate_tier_queries.py:29` through
`tests/tower/partition/test_degenerate_tier_queries.py:47` protects the core
empty-outgoing case.

Remaining traps:

- Multiple concrete lifts under one abstract action are silently resolved by
  first-candidate selection in `FiberConditionedStage`.
- NumPy observations from packaged environments are not strict-linearizable yet.
- Torch tests skip without `ml`, so tensor batch correctness is not CI-proven.
- There is no experiment manifest carrying seed, version, schema, tensorization
  mode, or git metadata.
- There is no checkpoint/resume story, so reproducibility is local and test-level
  rather than run-level.
- Metrics denominators remain early-stage: the benchmark returns operations per
  second, but not enough context to compare runs responsibly.
- Evaluation/train-mode separation exists only as a lightweight string mode in
  the reference tabular learner. There is no serious neural model mode contract
  yet.
- There is no normalization-statistics boundary because there is no serious
  neural learner yet. That is fine, but future neural work must not bury it.

These are not reasons to panic. They are reasons not to overclaim.

## Performance and feedback loop

The feedback loop is currently good for a research package:

- Full local pytest completes in a few seconds.
- Ruff and mypy are fast.
- The smoke benchmark is importable and runnable.
- The examples are small enough for frequent validation.

That is a major asset. Do not destroy it by building a giant training framework
before the benchmark/artifact spine exists.

The runtime performance story is directionally right:

- Partition tower maintenance is the source of truth.
- Compatibility quotient readouts are lazy.
- The package avoids forcing tensorization into the object-native runtime path.
- `LinearizationConfig` can represent control-flow, tensor-available-disabled,
  and tensor-enabled modes separately.

The hot-path concerns are concrete:

- `ActionPartitionLayer` has many mutable indexes and dirty collections.
- `PartitionTower.update_with_delta(...)` has to keep source support, target
  cells, internal edges, and action-cell rebuilds coherent.
- `to_quotient_tier_views()` must stay off the default step path.
- `TorchDecisionBatch.from_linearized(...)` creates tensors from Python lists at
  `src/state_collapser/training/torch.py:57` through
  `src/state_collapser/training/torch.py:119`, which is fine for a boundary smoke
  model but should not be mistaken for an optimized rollout pipeline.
- `linearize_action_selection_input(...)` is record-by-record Python conversion
  at `src/state_collapser/training/linearization.py:726` through
  `src/state_collapser/training/linearization.py:810`. That is appropriate for
  the first boundary, but performance claims need measured conversion counts and
  elapsed conversion time.
- The benchmark mutates a private runtime field for morphism mode and does not
  persist artifacts.

The performance standard should be:

- Maintain the object-native runtime as the control path.
- Make tensorization an explicit boundary with measured conversion overhead.
- Benchmark readout-disabled and readout-enabled paths separately.
- Benchmark morphism-disabled and morphism-enabled paths separately.
- Add artifact output before making scaling claims.
- Keep tests fast enough that contributors run them.

## Tests that actually matter

The current suite is broad and valuable. The most important existing tests are:

- Full/incremental partition equivalence:
  `tests/tower/partition/test_full_incremental_equivalence.py`.
- Pointwise liftability:
  `tests/tower/partition/test_pointwise_liftability.py`.
- Degenerate-tier queries and controller behavior:
  `tests/tower/partition/test_degenerate_tier_queries.py` and
  `tests/tower/control/test_runtime_loop.py`.
- HGraphML compatibility:
  `tests/tower/partition/test_hgraphml_downstream_compatibility.py`.
- Training transitions, continuation, masks, learners, fibers, and stages:
  `tests/training`.
- Example environment geometry, transitions, validity, runtime integration, and
  tower training:
  `tests/examples`.
- Gymnasium wrapper behavior:
  `tests/adapters`.
- Benchmark smoke:
  `tests/benchmarks`.

The missing tests that matter most:

- CI-executed Torch tests with the `ml` extra installed.
- Linearization of actual NumPy observations from package example environments.
- Invariant checks for `ActionPartitionLayer` and `PartitionTower`.
- Randomized or property-style incremental tower update tests that call the
  invariant checker after each delta.
- Explicit multiple-lift selection tests for `FiberConditionedStage`.
- Benchmark artifact serialization tests once the artifact spine exists.
- Tests that assert `LinearizationConfig` and `LinearizationReport` appear in
  benchmark artifacts.
- Tests that exercise HGraphML-compatible `EncodingRegistry.from_tower(...)`
  after tensorization changes.
- Tests for a public morphism/readout benchmark config path that does not mutate
  private runtime attributes.

Useful focused commands already documented in `CONTRIBUTING.md`:

```bash
uv run pytest tests/tower/partition/test_pointwise_liftability.py
uv run pytest tests/tower/partition/test_queries_and_lift.py
uv run pytest tests/training/test_path_fiber.py
uv run pytest tests/training/test_fiber_conditioned_stage.py
uv run pytest tests/examples/test_plate_support_env_exploit_explore_runtime.py
uv run pytest tests/training/test_encoding_registry.py
uv run pytest tests/training/test_linearization_config.py
uv run pytest tests/training/test_linearized_records.py
uv run pytest tests/training/test_torch_batches.py
uv run pytest tests/examples/test_torch_tensor_boundary_smoke_model.py
uv run pytest tests/tower/partition/test_hgraphml_downstream_compatibility.py
```

But for Torch, those commands are only complete when the `ml` extra is installed.

## What I would delete first

First, delete or move the mandatory `pillow` dependency unless a current source
path actually imports it. It is not earning its place in `pyproject.toml:36`
through `pyproject.toml:38`.

Second, delete the stale meaning of `docs/artifact_contracts.md` by rewriting it
around current artifacts. The file can stay, but the first-implementation-era
content should not.

Third, delete the private runtime mutation in the benchmark:
`tower_runtime._build_morphism = morphism_requested` at
`src/state_collapser/benchmarks/tower_runtime_bench.py:73`. Replace it with a
public constructor/config path.

Fourth, delete any language that implies instrumentation is implemented if the
instrumentation namespaces remain empty. Planned namespace is fine. Implemented
tooling is different.

Fifth, consider archiving some generated design PDFs only if repository weight
or public-release cleanliness becomes a real issue. Do not do this blindly:
`logHRL.pdf` is a front-door research artifact, so deleting PDFs is not a simple
"clean repo" operation. The right standard is intentionality, not minimalism for
its own sake.

I would not delete the old quotient/readout surfaces yet. They are compatibility
surfaces, and downstream/documentation history still benefits from them. The
right move is to keep them lazy and clearly non-hot-path.

## What I would rewrite first

The first rewrite should be small and brutal:

1. Add a CI job that installs `ml` and runs the Torch boundary tests.
2. Add NumPy array support to `_linearize_observation(...)`, with tests using a
   real packaged example environment observation.
3. Add a benchmark artifact object/writer that persists config, result,
   package/git metadata, and optional `LinearizationReport`.
4. Replace the benchmark's private morphism flag mutation with a public runtime
   construction/config path.
5. Add `assert_consistent()` style invariant checks for `ActionPartitionLayer`
   and use them in partition tower tests.
6. Add an explicit `lift_selector` hook to `FiberConditionedStage`, defaulting to
   deterministic first-candidate behavior.
7. Refresh `docs/artifact_contracts.md` and the stale README install tag.

Do not rewrite the package into a "real RL framework." That would be the wrong
move. The package's real job is structural: build and maintain quotient/tower
decision structure around an environment or transition system. Serious learners
should attach through clean data surfaces, not be swallowed by a package-owned
training religion.

Do not rewrite `PartitionTower` unless invariant tests prove it is wrong. The
current algorithmic shape is plausible and well-tested for pre-alpha. The next
move is hardening, not aesthetic churn.

## Final standard

The package is currently a serious pre-alpha research runtime. It has a real
algorithmic center, real tests, real examples, real downstream compatibility
pressure, and increasingly honest documentation.

The standard for the next milestone should be:

- Every advertised optional surface has CI coverage in the right extra.
- Linearization works with the package's own Gymnasium observations.
- Benchmark runs produce artifacts, not just terminal summaries.
- `LinearizationConfig` and `LinearizationReport` flow into those artifacts.
- Partition tower source-support invariants are mechanically checked.
- Lift selection is explicit.
- Public docs distinguish source-install research release, smoke benchmarks,
  and serious empirical claims.
- HGraphML compatibility remains protected.

If those things are true, `state_collapser` becomes a believable structural layer
that serious RL or graph-ML engineers can evaluate. If they are not true, the
repo remains a promising research package with enough machinery to fool people
into thinking it is more operationally mature than it is.

The current repo is closer to the good version than the bad one. The next work
should protect that by making the data path measurable, artifacted, and
continuously verified.
