# PlateSupportEnv Implementation Gameplan

## Status

This document is the implementation gameplan for `env_001`, the first package-evaluation environment:

- [plate_support_env_spec.md]([state_collapser repository root]/docs/design/test_design/env_001/plate_support_env_spec.md)

It is written in the same spirit as the implementation gameplan that successfully drove the second full build experiment in this repository.

This document is intended to be:

- concrete
- implementation-facing
- test-driven
- strict enough to follow without silent reinterpretation

## Execution Contract For This Gameplan

1. **Authoritative source**
- This gameplan and the env spec above are the implementation law for `env_001`.
- Older design documents may provide rationale, but they do not override this gameplan during implementation unless the Project Owner explicitly says so.

2. **Execution unit**
- The atomic unit of work is exactly one `Phase.Stage.Action`.
- Do not merge actions.
- Do not skip actions.
- Do not reorder actions unless the Project Owner explicitly authorizes reordering.

3. **Completion loop**
- Read the current action again before coding.
- Implement only that action.
- Run only the tests/checks implied by that action.
- Compare the result back to this gameplan and the env spec.
- Update the running env-implementation log.
- Only then move to the next action.

4. **No silent simplification**
- Do not build a “lighter first pass” unless the Project Owner explicitly asks for that.
- Do not weaken the validity rule, reward rule, or transition semantics silently.
- Do not silently replace the environment with a smaller or more convenient surrogate.

5. **Mandatory consultation triggers**
- Stop and ask the Project Owner if:
  - the env spec is ambiguous at implementation time
  - a proposed goal state is invalid or trivial
  - the validity rule yields a degenerate graph
  - Gymnasium integration requires an unplanned design choice
  - a required test expectation conflicts with the env spec
  - implementation appears to require changing the env spec or this gameplan

6. **Testing rule**
- Tests are part of implementation, not cleanup afterward.
- Each phase includes required unit or integration tests.
- Do not mark a phase complete until the listed tests for that phase pass.

7. **Artifact/log rule**
- Keep a running implementation log for this env in the same folder as this gameplan.
- Record:
  - completed `Phase.Stage.Action` items
  - test results
  - surprises
  - owner clarifications
  - any blocked points

## Overall implementation target

The implementation target is:

- one fully functioning discrete `gymnasium.Env`
- conforming exactly to the env spec
- with enough tests that both flat Gymnasium training and later `state_collapser`-assisted evaluation can treat it as a reliable benchmark object

This gameplan does **not** include:

- the flat-RL baseline training harness
- the quotient-tower training harness
- comparative performance evaluation scripts

Those belong to later test-design or benchmark-design stages.

This gameplan covers only:

- the environment itself
- its correctness tests
- its package placement and documentation wiring

## Canonical target file set

The canonical implementation targets are:

- `src/state_collapser/examples/plate_support_env/env.py`
- `src/state_collapser/examples/plate_support_env/__init__.py`
- `tests/examples/test_plate_support_env_geometry.py`
- `tests/examples/test_plate_support_env_validity.py`
- `tests/examples/test_plate_support_env_transitions.py`
- `tests/examples/test_plate_support_env_rewards.py`
- `tests/examples/test_plate_support_env_gymnasium.py`
- `tests/examples/test_plate_support_env_graph_properties.py`

Optional supporting test fixture or helper modules may be added if necessary, but only if justified by concrete implementation needs.

These target locations are part of the implementation plan, not merely suggestions.

If implementation appears to require relocating the env outside these paths, stop and ask the Project Owner before proceeding.

## Running-log file

The running log for this env implementation should be:

- `docs/design/test_design/env_001/plate_support_env_implementation_log.md`

Create it during Phase 1.

---

# Phase 1 — Environment Planning Artifacts

## Stage 1.1 — Bind authority and create implementation trace

### Action 1.1.1

Create the running implementation log file:

- `docs/design/test_design/env_001/plate_support_env_implementation_log.md`

The log should begin with:

- implementation date
- current branch
- authoritative documents
- a statement that this gameplan is being followed exactly

### Action 1.1.2

Add the first log entry recording:

- start of env implementation
- target source file(s)
- target test file(s)
- the fact that the implementation is env-only, not yet benchmark/training harness work

### Action 1.1.3

Re-read the env spec and bind the following as explicit implementation invariants inside the log:

- exact state tuple shape
- exact action count
- invalid move semantics as self-loop
- reward locality
- fixed start state
- fixed goal-state validation requirement

## Stage 1.2 — Implementation target confirmation

### Action 1.2.1

Confirm the concrete source-file target for the environment implementation.

Default target:

- `src/state_collapser/examples/plate_support_env/env.py`

If a different target path is needed, stop and ask the Project Owner.

### Action 1.2.2

Confirm the concrete test-file targets listed in this gameplan and log them.

### Action 1.2.3

Verify that no existing package file already implements an overlapping environment with conflicting semantics.

This is an inspection action only.

Required check:

- repo search for `PlateSupportEnv`

Completion criterion:

- no conflicting implementation found, or
- explicit owner guidance requested if one exists

---

# Phase 2 — Core Geometry and State Helpers

## Stage 2.1 — State record and static constants

### Action 2.1.1

Implement the immutable internal state record:

- `PlateSupportState`

with exactly the fields:

- `x_idx`
- `y_idx`
- `theta_idx`
- `e1`
- `e2`
- `e3`

The implementation must follow the env spec’s recommended frozen dataclass shape unless a repo-local style constraint makes that impossible.

### Action 2.1.2

Implement the static geometry constants in the env module:

- workspace size
- support socket local coordinates
- arm base coordinates
- start state
- candidate goal state
- max steps

### Action 2.1.3

Implement helpers for:

- state-to-observation encoding
- observation-to-state decoding only if needed internally

Do **not** yet implement Gymnasium class methods.

## Stage 2.2 — Rotation and socket geometry

### Action 2.2.1

Implement the exact quarter-turn helper:

- `rotate_local_point(theta_idx, point)`

with exactly the mapping specified in the env spec.

### Action 2.2.2

Implement the helper that computes world-space socket positions from:

- plate center
- orientation
- local support sockets

### Action 2.2.3

Implement a helper that returns the three socket world coordinates as an ordered tuple aligned with arms `1,2,3`.

## Stage 2.3 — Phase 2 tests

### Action 2.3.1

Add unit tests for:

- state immutability/hashing behavior
- exact rotation behavior for all four `theta_idx` values
- socket-world-coordinate computation for at least several representative poses

Recommended file:

- `tests/examples/test_plate_support_env_geometry.py`

### Action 2.3.2

Run only the Phase 2 geometry/state tests.

Completion criterion:

- all new Phase 2 tests pass

### Action 2.3.3

Update the running implementation log with:

- files created
- test results
- any geometry surprises

---

# Phase 3 — Validity Predicate

## Stage 3.1 — Bounds and reachability

### Action 3.1.1

Implement the helper that checks whether a plate center is inside workspace bounds.

### Action 3.1.2

Implement the helper that checks whether all rotated/transformed support sockets remain in bounds.

### Action 3.1.3

Implement the engaged-arm reachability check using the exact Manhattan-distance rule from the env spec.

For each engaged arm:

- compute `d_i`
- require `d_i <= e_i`

## Stage 3.2 — Support count and stability

### Action 3.2.1

Implement the engaged-arm count predicate requiring at least two engaged arms.

### Action 3.2.2

Implement the exact first stability rule from the spec:

- left and right reachable
- or all three reachable

Do not silently generalize this rule.

Also preserve the env’s fixed arm-to-socket assignment exactly:

- arm `1` tests only against the left socket
- arm `2` tests only against the middle socket
- arm `3` tests only against the right socket

Do not add matching, permutation, or reassignment logic.

### Action 3.2.3

Implement the full state validity predicate by combining:

- center bounds
- socket bounds
- reachability
- minimum support count
- stability

## Stage 3.3 — Phase 3 tests

### Action 3.3.1

Add unit tests for each individual validity sub-predicate:

- center bounds
- socket bounds
- engaged-arm count
- reachability
- stability

### Action 3.3.2

Add unit tests for the full validity predicate covering:

- clearly valid states
- clearly invalid out-of-bounds states
- clearly invalid unsupported states
- clearly invalid unreachable-support states
- clearly invalid unstable-support states

Recommended file:

- `tests/examples/test_plate_support_env_validity.py`

### Action 3.3.3

Run only the Phase 3 validity tests.

Completion criterion:

- all new Phase 3 tests pass

### Action 3.3.4

Update the running implementation log with:

- validity-rule implementation status
- any surprising valid/invalid cases

---

# Phase 4 — Goal and Start-State Validation

## Stage 4.1 — Start-state checks

### Action 4.1.1

Implement an explicit helper or internal assertion that verifies the configured start state is valid.

### Action 4.1.2

Test that the start state satisfies the full validity predicate.

## Stage 4.2 — Goal-state checks

### Action 4.2.1

Implement an explicit helper or internal assertion that verifies the configured goal state is valid.

### Action 4.2.2

Implement checks that the goal state is:

- not equal to the start state
- not one primitive action away from the start state
- different from the start state in both:
  - plate pose
  - support configuration

### Action 4.2.3

If the candidate goal state fails these requirements, stop and ask the Project Owner before substituting a new one.

This is a mandatory consultation boundary.

## Stage 4.3 — Phase 4 tests

### Action 4.3.1

Add tests for:

- valid start state
- valid goal state
- goal/start non-equality
- goal nontriviality relative to start

Recommended file:

- `tests/examples/test_plate_support_env_validity.py`

### Action 4.3.2

Run the start/goal validation tests.

### Action 4.3.3

Update the implementation log with the final accepted start/goal validation result.

---

# Phase 5 — Transition Semantics

## Stage 5.1 — Primitive action application

### Action 5.1.1

Implement the internal helper that applies one primitive action proposal to a state without yet committing to it.

This helper must cover:

- six plate-motion actions
- six arm-extension actions

### Action 5.1.2

Implement exact arm-extension clipping behavior:

- extension actions clip into `{0,1,2}`

If clipping yields the same extension value as the current state, do **not** silently classify that action as invalid on that basis alone.

The clipped candidate must still flow through the normal full-state validity check.

### Action 5.1.3

Implement exact plate-motion proposal behavior:

- translation and rotation are proposed directly
- no fallback clipping of pose

## Stage 5.2 — Validity-filtered transition rule

### Action 5.2.1

Implement the full transition helper:

- produce candidate state
- evaluate validity
- if valid, accept candidate
- if invalid, return self-loop current state

### Action 5.2.2

Implement explicit metadata output from the transition helper sufficient to distinguish:

- valid transition
- invalid move
- self-loop caused by invalidity

This metadata must also support distinguishing:

- valid self-transition caused by a clipped arm action that leaves the state unchanged
- invalid self-loop caused by candidate-state rejection

This metadata may be internal at this phase, but it must exist because later `step()` info requires it.

## Stage 5.3 — Phase 5 tests

### Action 5.3.1

Add tests for:

- each plate-motion action in at least one valid case
- each plate-motion action in at least one invalid case
- each arm-extension action in at least one valid case
- each arm-extension action in at least one invalid-resulting case

### Action 5.3.2

Add tests confirming invalid moves are self-loops rather than crash/failure states.

Also add tests covering clipped arm-boundary actions, including:

- a clipped arm action that yields a valid self-transition
- a clipped arm action that still yields an invalid resulting full state if such a case exists

Recommended file:

- `tests/examples/test_plate_support_env_transitions.py`

### Action 5.3.3

Run the Phase 5 transition tests.

### Action 5.3.4

Update the implementation log with:

- transition semantics complete
- invalid-move behavior confirmed

---

# Phase 6 — Reward and Termination Semantics

## Stage 6.1 — Reward function

### Action 6.1.1

Implement the reward helper so that reward depends only on:

- current state
- action
- resulting next state

This must preserve reward locality.

### Action 6.1.2

Implement exact rewards:

- `+100.0` on goal-reaching transition
- `-3.0` on invalid self-loop
- `-1.0` on valid non-goal transition

### Action 6.1.3

Add a brief inline source comment explaining that the reward is intentionally one-step local because that is a repo-level design constraint.

## Stage 6.2 — Termination and truncation

### Action 6.2.1

Implement the goal predicate.

### Action 6.2.2

Implement the episode termination rule:

- `terminated = True` iff goal reached

### Action 6.2.3

Implement the truncation rule:

- `truncated = True` iff `max_steps` reached without termination

## Stage 6.3 — Phase 6 tests

### Action 6.3.1

Add tests for:

- reward on valid non-goal move
- reward on invalid self-loop
- reward on goal-reaching move

### Action 6.3.2

Add tests for:

- termination on goal
- non-termination on non-goal
- truncation at `max_steps`

Recommended files:

- `tests/examples/test_plate_support_env_rewards.py`
- or a split between rewards and Gymnasium lifecycle tests if clearer

### Action 6.3.3

Run the Phase 6 reward/termination tests.

### Action 6.3.4

Update the implementation log with explicit confirmation that reward locality is preserved.

---

# Phase 7 — Gymnasium Env Class

## Stage 7.1 — Class shell and spaces

### Action 7.1.1

Implement the `PlateSupportEnv` class as a `gymnasium.Env`.

### Action 7.1.2

Declare:

- `action_space = Discrete(12)`
- `observation_space = MultiDiscrete([5, 5, 4, 3, 3, 3])`

### Action 7.1.3

Implement internal state tracking fields including:

- current state
- goal state
- step counter
- optional render mode

## Stage 7.2 — `reset()`

### Action 7.2.1

Implement `reset(seed=None, options=None)`.

### Action 7.2.2

Ensure `reset()` returns:

- encoded observation
- `info` containing at least:
  - `"state"`
  - `"goal_state"`

### Action 7.2.3

Ensure `reset()` restores:

- current state to start state
- step counter to zero

## Stage 7.3 — `step()`

### Action 7.3.1

Implement `step(action)` using the already-implemented transition, reward, and termination helpers.

### Action 7.3.2

Ensure `step()` returns:

- observation
- reward
- terminated
- truncated
- `info`

with `info` containing at least:

- `"state"`
- `"valid_transition"`
- `"invalid_move"`
- `"goal_reached"`

### Action 7.3.3

Ensure invalid action indices raise appropriate Gymnasium-style errors rather than being silently remapped.

## Stage 7.4 — Minimal rendering

### Action 7.4.1

Implement minimal support for:

- `render_mode=None`
- optional `render_mode="ansi"`

### Action 7.4.2

For `ansi`, provide a concise text description of current env state as specified in the env spec.

## Stage 7.5 — Phase 7 tests

### Action 7.5.1

Add tests for:

- correct spaces
- `reset()` return structure
- `step()` return structure
- step counter behavior
- info-dict keys
- invalid action handling

Recommended file:

- `tests/examples/test_plate_support_env_gymnasium.py`

### Action 7.5.2

Run the Phase 7 Gymnasium integration tests.

### Action 7.5.3

Update the implementation log with:

- Gymnasium conformance status
- any API surprises

---

# Phase 8 — Hidden Graph and Reachability Sanity Checks

## Stage 8.1 — Small graph inspection helpers

### Action 8.1.1

Implement internal or test-side helpers to enumerate:

- all valid states
- valid outgoing transitions from a state

for this finite discrete env

These helpers may live in tests if they are only needed for benchmark validation.

### Action 8.1.2

Use those helpers to inspect the hidden feasible graph induced by the env rules.

This is an implementation/test sanity phase, not yet package-integration work.

## Stage 8.2 — Graph-property tests

### Action 8.2.1

Add tests confirming at least:

- the start state has at least one valid outgoing transition
- the goal state is reachable from the start state in the hidden graph
- the hidden graph is nontrivial (more than a tiny handful of valid states)
- invalid moves actually exist

Recommended file:

- `tests/examples/test_plate_support_env_graph_properties.py`

### Action 8.2.2

If the goal is not reachable under the implemented rules, stop and ask the Project Owner before changing the env spec or goal.

This is a mandatory consultation boundary.

The reachability check must be based on the actual implemented transition graph, not on a looser coordinate-nearness heuristic.

### Action 8.2.3

Run the graph-property tests.

### Action 8.2.4

Update the implementation log with:

- approximate graph size
- whether goal reachability was confirmed
- whether invalid moves are meaningfully present

---

# Phase 9 — Package-Level Documentation Wiring

## Stage 9.1 — Local test-design docs

### Action 9.1.1

Review the env spec and this gameplan after implementation and update only if implementation revealed a real mismatch that was explicitly owner-approved.

Do not silently rewrite either document.

### Action 9.1.2

If no owner-approved mismatch exists, leave the spec/gameplan unchanged and log that they were implementable as written.

## Stage 9.2 — Public/internal docs

### Action 9.2.1

Add or update the minimal package documentation entry points that should mention this new env, if the Project Owner wants it visible immediately.

Likely candidates:

- `docs/package_usage.md`
- `README.md`

Only do this if the env is now intended to be part of the visible package surface.

If unclear, stop and ask the Project Owner.

### Action 9.2.2

If documentation wiring is approved, add only a minimal accurate note:

- env name
- purpose
- relation to package evaluation

Do not turn this into a benchmark-results section.

---

# Phase 10 — Final Validation Pass

## Stage 10.1 — Focused env suite

### Action 10.1.1

Run all env-specific tests created for `PlateSupportEnv`.

This includes:

- geometry tests
- validity tests
- transition tests
- reward tests
- Gymnasium tests
- graph-property tests

### Action 10.1.2

Confirm the env-specific suite passes cleanly.

## Stage 10.2 — Broader regression check

### Action 10.2.1

Run the broader relevant repo test command expected by the Project Owner’s standard workflow if this env is being integrated into the main package.

Default:

- `.venv/bin/pytest tests`

### Action 10.2.2

If broader regressions fail, stop and identify whether:

- the env implementation caused the failure
- or an unrelated pre-existing failure exists

Do not silently “fix everything” unless the Project Owner authorizes that scope expansion.

## Stage 10.3 — Final log and handoff

### Action 10.3.1

Update the env implementation log with:

- all completed phases
- final test results
- any owner clarifications that occurred
- any remaining open questions for benchmark-design work

### Action 10.3.2

Prepare a concise completion summary tied explicitly to:

- what env files were added
- what tests were added
- whether the env satisfies reward locality
- whether the goal is reachable
- whether the env is ready for flat-vs-tower benchmark design

---

# Completion criteria

This gameplan is complete when all of the following are true:

1. `PlateSupportEnv` exists as a functioning discrete `gymnasium.Env`.
2. It matches the env spec exactly unless an owner-approved change says otherwise.
3. Reward is explicitly one-step local.
4. Invalid moves are self-loops with penalty.
5. Start and goal states are validated.
6. Goal reachability in the hidden feasible graph has been checked.
7. The env-specific tests pass.
8. The broader required regression test pass has been completed if requested by the implementation context.
9. The running implementation log exists and records the work.
10. The env is ready to be used in later package-evaluation experiments comparing flat RL against quotient-tower-assisted RL.
