# PlateSupportEnv Tower-Training Integration Gameplan

## Status

This document is the exact implementation gameplan for the missing layer between:

- the already-implemented `PlateSupportEnv`
- the existing `state_collapser` runtime/core machinery

and:

- a **runnable tower-assisted training workflow** on `PlateSupportEnv`

This gameplan exists because the env itself is complete, but the package-facing training/integration surface needed to actually run tower training on it does not yet exist as a usable workflow.

This document belongs in:

- `docs/design/test_design/env_001/`

because it is tightly coupled to the first package-evaluation env and is the immediate next implementation layer for that env.

## Relationship to existing docs

This gameplan builds on:

- [plate_support_env_spec.md]([state_collapser repository root]/docs/design/test_design/env_001/plate_support_env_spec.md)
- [plate_support_env_implementation_gameplan.md]([state_collapser repository root]/docs/design/test_design/env_001/plate_support_env_implementation_gameplan.md)
- [plate_support_env_implementation_log.md]([state_collapser repository root]/docs/design/test_design/env_001/plate_support_env_implementation_log.md)
- [training_integration_surface_proposal.md]([state_collapser repository root]/docs/design/training_integration_surface_proposal.md)

It does **not** cover:

- benchmark metrics comparison against flat training
- results-reporting polish
- artifact dashboards
- performance analysis

Those belong to later benchmark-design work.

This gameplan covers only the missing layer needed to make the following statement true:

> “We can now run tower training on `PlateSupportEnv`.”

## Execution Contract For This Gameplan

1. **Authoritative sources**
- This gameplan and the documents listed above are the implementation law for the tower-training integration layer for `env_001`.
- Older documents are rationale only unless explicitly referenced by these.

2. **Execution unit**
- The atomic unit of work is exactly one `Phase.Stage.Action`.
- Do not merge, skip, reorder, or reinterpret actions without explicit owner approval.

3. **Completion loop**
- Re-read the current action before coding.
- Implement only that action.
- Run only the tests/checks implied by that action.
- Compare the result back to this gameplan.
- Update the running integration log.
- Only then move on.

4. **No silent simplification**
- Do not silently turn “tower training run” into “mock runtime exercise.”
- Do not silently replace learning with a scripted trajectory.
- Do not silently demote tower updates to logging-only or placeholder behavior.
- Do not silently substitute a benchmark-only harness when the goal is a runnable tower-training workflow.

5. **Mandatory consultation triggers**
- Stop and ask the Project Owner if:
  - the existing tower/runtime API is insufficient in a way that requires changing previously approved behavior
  - a training loop decision would change the package-facing integration surface materially
  - the env can be rolled through the runtime but cannot actually support learning without a new design decision
  - the package-facing entry point proposed here conflicts with existing adapter direction
  - test expectations and runtime reality diverge

6. **Testing rule**
- Every phase must include focused tests.
- A tower-training workflow is not “done” until it is exercised by at least one real rollout/training-path test.

7. **Artifact/log rule**
- Keep a dedicated running log for this integration layer in:
  - `docs/design/test_design/env_001/plate_support_env_tower_training_integration_log.md`
- Record:
  - completed `Phase.Stage.Action` items
  - tests run
  - owner clarifications
  - integration surprises
  - any divergence pressure between env and package runtime

## Implementation target

At the end of this gameplan, the repo should contain:

1. a package-facing adapter/runtime entry point that can expose `PlateSupportEnv` to `state_collapser`
2. a minimal but real tower-training runner for `PlateSupportEnv`
3. tests proving:
   - env-to-runtime coupling works
   - tower updates happen during rollouts
   - learning/training loop execution actually occurs
4. a smoke-level runnable path that the Project Owner can invoke to perform a tower-assisted training run on this env

This is **not** yet the benchmarking layer. It is the first runnable tower-training path.

## Recommended canonical target file set

The recommended canonical implementation targets are:

- `src/state_collapser/examples/plate_support_env/runtime.py`
- `src/state_collapser/examples/plate_support_env/training.py`
- `tests/examples/test_plate_support_env_runtime_integration.py`
- `tests/examples/test_plate_support_env_tower_training.py`

Optional helper files may be added only if justified by real implementation needs, for example:

- `src/state_collapser/examples/plate_support_env/policy.py`
- `src/state_collapser/examples/plate_support_env/rollout.py`

If implementation appears to require relocating this work outside the example subpackage, stop and ask the Project Owner first.

## Running-log file

The running log for this integration work should be:

- `docs/design/test_design/env_001/plate_support_env_tower_training_integration_log.md`

Create it during Phase 1.

---

# Phase 1 — Planning Artifacts and Authority Binding

## Stage 1.1 — Create integration trace

### Action 1.1.1

Create:

- `docs/design/test_design/env_001/plate_support_env_tower_training_integration_log.md`

with:

- implementation date
- current branch
- authoritative documents
- statement that this gameplan is being followed exactly

### Action 1.1.2

Add the first log entry recording:

- start of tower-training integration work
- target source files
- target test files
- explicit note that this layer is for runnable tower training, not benchmark metrics yet

### Action 1.1.3

Bind the following implementation invariants into the log:

- `PlateSupportEnv` remains the env and reward authority
- reward remains one-step local
- tower bookkeeping lives in `state_collapser`, not inside the env
- the result must be a runnable training workflow, not a scripted demo

## Stage 1.2 — Confirm canonical integration targets

### Action 1.2.1

Confirm the canonical runtime-integration file target:

- `src/state_collapser/examples/plate_support_env/runtime.py`

### Action 1.2.2

Confirm the canonical training-runner file target:

- `src/state_collapser/examples/plate_support_env/training.py`

### Action 1.2.3

Confirm the canonical test-file targets:

- `tests/examples/test_plate_support_env_runtime_integration.py`
- `tests/examples/test_plate_support_env_tower_training.py`

### Action 1.2.4

Inspect the repo for any already-existing training runner or runtime adapter that overlaps this role.

Required check:

- repo search for likely names such as:
  - `StateCollapserEnvRuntime`
  - `run_tower_training`
  - `PlateSupportEnvRuntime`

Completion criterion:

- no conflicting implementation found, or
- explicit owner guidance requested if one exists

---

# Phase 2 — Package-Facing Runtime Adapter Design

## Stage 2.1 — Define the env-to-runtime boundary

### Action 2.1.1

Implement a `PlateSupportEnvRuntime` or equivalently named object in:

- `src/state_collapser/examples/plate_support_env/runtime.py`

This object should be the first env-specific integration layer that exposes `PlateSupportEnv` to the package runtime machinery.

### Action 2.1.2

Define the adapter’s minimal responsibilities:

- own or accept a `PlateSupportEnv`
- expose reset and step-style runtime progression
- translate env states/actions into the package’s state/action/runtime surface
- update `state_collapser` runtime structures on each step

### Action 2.1.3

Keep the env itself separate from tower state.

The adapter/runtime object must not mutate `PlateSupportEnv` into a tower-owning class.

## Stage 2.2 — Runtime construction contract

### Action 2.2.1

Define the adapter constructor or factory so that the user can provide:

- an env instance
- a contraction policy
- any required runtime config

Conceptually the shape should support something like:

```python
runtime = PlateSupportEnvRuntime(
    env=PlateSupportEnv(),
    contraction_policy=...,
)
```

### Action 2.2.2

Bind the runtime to the existing `state_collapser` tower machinery rather than inventing an unrelated parallel runtime model.

### Action 2.2.3

Define what the adapter returns on reset and step.

Minimum requirement:

- env observation/result
- current runtime/tower snapshot
- action/result metadata needed by the training layer

## Stage 2.3 — Phase 2 tests

### Action 2.3.1

Add tests confirming:

- the adapter constructs from `PlateSupportEnv`
- reset produces both env-level and runtime-level state
- one step updates both env state and tower state

### Action 2.3.2

Add tests confirming the env remains the reward/transition authority while the runtime remains the tower authority.

### Action 2.3.3

Run the runtime-integration tests for this phase only.

Recommended file:

- `tests/examples/test_plate_support_env_runtime_integration.py`

### Action 2.3.4

Update the integration log with:

- adapter shape
- any mismatch pressure between env semantics and existing tower runtime

---

# Phase 3 — Action and Observation Translation Layer

## Stage 3.1 — Observation mapping

### Action 3.1.1

Implement the mapping from `PlateSupportEnv` internal state / observation into whatever `state_collapser` runtime-facing state object is needed.

This mapping must preserve:

- state identity
- reward locality assumptions
- deterministic state decoding

### Action 3.1.2

Define whether the runtime uses:

- direct env state tuples
- wrapped `State` objects
- or a dedicated env-to-core translation object

If this choice requires changing package-level assumptions materially, stop and ask the Project Owner.

## Stage 3.2 — Action mapping

### Action 3.2.1

Implement the mapping from discrete action indices `{0,...,11}` into the package’s primitive-action representation.

### Action 3.2.2

Make the mapping explicit and deterministic so tests can inspect it directly.

## Stage 3.3 — Phase 3 tests

### Action 3.3.1

Add tests confirming:

- observation/state mapping is stable
- action mapping is stable
- a runtime step built from mapped actions lands in the same env next state as direct env stepping

### Action 3.3.2

Run the runtime-integration tests for the mapping layer.

### Action 3.3.3

Update the integration log with:

- chosen translation shape
- whether any mapping decision required special handling

---

# Phase 4 — Runtime-Step Coupling To Tower Updates

## Stage 4.1 — Reset-time tower initialization

### Action 4.1.1

Implement adapter reset behavior so that:

- env resets
- the corresponding package runtime resets
- the initial discovered/explored/tower state is created consistently

### Action 4.1.2

Ensure the initial env state enters the runtime in the correct way, rather than leaving the runtime “empty until first step.”

## Stage 4.2 — Step-time tower update

### Action 4.2.1

Implement the actual coupling so that each env step:

1. applies the primitive action in the env
2. observes the resulting next state
3. updates the discovered/explored graph
4. refreshes local vista
5. applies contraction-policy consequences
6. updates current tower state/snapshot

### Action 4.2.2

Ensure the step result exposes both:

- env-level transition outcome
- current runtime/tower snapshot

### Action 4.2.3

Ensure invalid self-loop env moves are represented correctly in the runtime rather than silently normalized away.

## Stage 4.3 — Phase 4 tests

### Action 4.3.1

Add tests confirming:

- reset initializes runtime state correctly
- stepping changes runtime state when env state changes
- invalid self-loop actions still produce a coherent runtime update

### Action 4.3.2

Add tests confirming the runtime snapshot exists and evolves across a short rollout.

### Action 4.3.3

Run the runtime-integration tests for this phase.

### Action 4.3.4

Update the integration log with:

- tower-step coupling confirmed
- any mismatch between env invalidity semantics and tower update semantics

---

# Phase 5 — Minimal Tower-Training Loop

## Stage 5.1 — Training-loop contract

### Action 5.1.1

Implement a first minimal tower-training runner in:

- `src/state_collapser/examples/plate_support_env/training.py`

The target is a **real training loop**, not just a rollout script.

### Action 5.1.2

Define the minimal trainer contract.

It must support:

- repeated episodes
- stepwise action selection
- env stepping through the runtime adapter
- parameter or value updates across training

This does **not** need to be a sophisticated trainer, but it must be a real learning loop.

### Action 5.1.3

Choose the simplest honest first learning rule for this env.

Recommended first choice:

- a tabular or discrete-state method appropriate to the env

If a different training rule is required, log why.

## Stage 5.2 — Tower-aware action selection

### Action 5.2.1

Implement the first tower-aware action-selection path.

This does not have to be “full final package intelligence,” but it must genuinely consult the runtime/tower layer rather than ignoring it.

### Action 5.2.2

Make explicit what the training loop receives from the runtime on each step:

- current env state
- current tower snapshot
- any derived action-selection hints used in the first tower-aware loop

### Action 5.2.3

If the current package runtime is insufficient to support a meaningful tower-aware action-selection decision, stop and ask the Project Owner before substituting a fake tower usage pattern.

## Stage 5.3 — Episode bookkeeping

### Action 5.3.1

Implement basic episode bookkeeping:

- episodic return
- step count
- success/failure flag

### Action 5.3.2

Keep this bookkeeping local and minimal.

This is for runnable training only, not benchmark analysis yet.

## Stage 5.4 — Phase 5 tests

### Action 5.4.1

Add tests confirming:

- the training loop runs for at least one episode
- model/value state changes across training
- the tower runtime is actually touched during the loop

### Action 5.4.2

Add tests confirming the tower-training runner is not just replaying a scripted action list.

### Action 5.4.3

Run the tower-training tests for this phase only.

Recommended file:

- `tests/examples/test_plate_support_env_tower_training.py`

### Action 5.4.4

Update the integration log with:

- chosen first learning rule
- how the tower is actually being used during training

---

# Phase 6 — Runnable Smoke Path

## Stage 6.1 — Direct invocation path

### Action 6.1.1

Provide a direct invocation path that a developer can run to perform a small tower-training job on `PlateSupportEnv`.

This may be:

- a callable function in `training.py`
- or a very thin helper exposed from the package example submodule

### Action 6.1.2

The callable should support at least:

- episode count
- random seed
- contraction policy selection or injection

## Stage 6.2 — Smoke-run validation

### Action 6.2.1

Add a smoke test confirming the tower-training path runs end-to-end for a very small training budget.

### Action 6.2.2

Confirm the smoke path:

- resets env
- steps through runtime adapter
- performs learning updates
- returns a structured result object or summary

## Stage 6.3 — Phase 6 tests

### Action 6.3.1

Run the tower-training test suite including the smoke-level end-to-end run.

### Action 6.3.2

Update the integration log with:

- whether the tower-training run is now genuinely runnable
- what the entry point is

---

# Phase 7 — Final Validation Pass

## Stage 7.1 — Focused integration suite

### Action 7.1.1

Run all env-specific runtime/training integration tests created by this gameplan.

This includes at minimum:

- runtime integration tests
- tower-training tests

### Action 7.1.2

Confirm that the env-specific tower-training integration suite passes.

## Stage 7.2 — Broader regression check

### Action 7.2.1

Run the broader repo regression command:

- `.venv/bin/pytest tests`

### Action 7.2.2

If regressions occur, distinguish:

- failure caused by this integration work
- unrelated pre-existing failure

Do not widen scope silently.

## Stage 7.3 — Final log and handoff

### Action 7.3.1

Update the integration log with:

- all completed phases
- final test results
- owner clarifications
- any remaining open questions for later benchmark-design work

### Action 7.3.2

Prepare a concise completion summary tied explicitly to:

- what runtime/training files were added
- what tests were added
- what the runnable tower-training entry point is
- what tower-aware behavior is actually being exercised
- whether the system is now ready for later flat-vs-tower benchmark comparison work

---

# Completion criteria

This gameplan is complete when all of the following are true:

1. `PlateSupportEnv` can be exposed to a package-facing runtime adapter.
2. That adapter updates tower/runtime state during env rollouts.
3. A real training loop exists for tower-assisted training on this env.
4. The training loop genuinely consults runtime/tower state rather than ignoring it.
5. A smoke-level tower-training run can be invoked directly.
6. Runtime/training integration tests pass.
7. Broader repo regression tests pass.
8. The running integration log exists and records the work.
9. The repo is ready for the next stage: flat-vs-tower benchmark comparison design and implementation.
