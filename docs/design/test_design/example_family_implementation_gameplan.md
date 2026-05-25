# Example Family Implementation Gameplan

## Status

This document is the implementation gameplan for the evaluation-environment family defined in:

- [example_family_blueprint_from_mathematical_model_list.md]([state_collapser repository root]/docs/design/test_design/example_family_blueprint_from_mathematical_model_list.md)

It is written under the authority of:

- [docs/prime_directive/prime_directive.md]([state_collapser repository root]/docs/prime_directive/prime_directive.md)
- [docs/prime_directive/common_failure_mode_001.md]([state_collapser repository root]/docs/prime_directive/common_failure_mode_001.md)
- [docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md]([state_collapser repository root]/docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md)
- [docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md]([state_collapser repository root]/docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md)

It is intentionally operational.

It is not another environment-ideas note.

Its job is to define:

- the exact implementation order
- the concrete target file set
- the environment-family sequencing
- the validation sequence
- the stop conditions

This gameplan is organized in `Phase.Stage.Action` form.

## Execution Contract

### Rule 1 — Gameplan Is Law

When this implementation begins:

- this gameplan is law
- the environment-family blueprint is law
- the general evaluation strategy is law
- I do not silently simplify
- I do not silently reorder the environment-family build sequence
- I do not silently reinterpret an environment into a weaker or more decorative substitute

### Rule 2 — Single Action Discipline

During execution:

- one `Phase.Stage.Action` is the atomic implementation unit
- I re-read the exact action text before touching code
- I verify against that action before advancing

### Rule 3 — Mandatory Full Stop Conditions

I must full-stop and return to the Project Owner if:

- a chosen example family cannot be discretized honestly without a new design choice not fixed by the blueprint
- one environment’s implementation exposes a hidden need to reorder the family sequence
- a proposed env would violate reward-locality assumptions in a way not already authorized
- the required state/action design for a candidate env expands beyond "small, discrete, inspectable" and becomes de facto simulator work
- a file move, package naming change, or folder renumbering seems required but is not clearly authorized here

### Rule 4 — No Decorative Examples

I must not:

- build a visually different environment that does not actually encode the intended hidden constraint geometry
- rename `plate_support_env` ideas into a new package without changing the governing constraint family
- introduce large simulator-style complexity under the label of "fidelity"
- claim an example is evaluation-ready when it is only an ambient state lattice with superficial validity filters

### Rule 5 — Running Log Requirement

When implementation begins, maintain a running log at:

- `docs/design/test_design/example_family_implementation_log.md`

The log must record:

- completed `Phase.Stage.Action` items
- test results
- surprises
- owner clarifications
- blockers

## Canonical Target File Set

### Global evaluation-design references

- `docs/design/test_design/evaluation_strategy.md`
- `docs/design/test_design/example_family_blueprint_from_mathematical_model_list.md`
- `docs/design/test_design/example_family_implementation_gameplan.md`
- `docs/design/test_design/example_family_implementation_log.md`

### New env-specific design folders

- `docs/design/test_design/env_002/`
- `docs/design/test_design/env_003/`
- `docs/design/test_design/env_004/`
- `docs/design/test_design/env_005/`

Each env folder should eventually contain at least:

- a spec
- an implementation gameplan
- an implementation log

### Example package targets

- `src/state_collapser/examples/articulated_loop_env/`
- `src/state_collapser/examples/parallelogram_singularity_env/`
- `src/state_collapser/examples/cable_parallel_env/`
- `src/state_collapser/examples/dual_arm_manipulation_env/`

Each package should eventually include at least:

- `__init__.py`
- `env.py`
- `runtime.py`
- `training.py`

### Tests

- `tests/examples/`
- any additional supporting tests if the new environments require new shared helpers

## Global Implementation Rules

### Rule A

Every environment must remain:

- discrete
- small enough to inspect
- hidden-constraint-heavy
- reward-locality-compatible
- suitable for plain, top-tier-only, and full-tower comparison where feasible

### Rule B

No chosen environment may be implemented as a literal robotics simulator.

These are package-evaluation environments, not benchmark physics engines.

### Rule C

The new environment family must be implemented in the same general package shape as:

- `src/state_collapser/examples/plate_support_env/`

but without merely cloning `plate_support_env` semantics.

### Rule D

Each new environment must be justified structurally, not merely narratively.

That means:

- state variables
- action set
- validity rule
- hidden constraint geometry
- and evaluation value

must all be explicit in its env-specific spec.

### Rule E

Deferred example families:

- multi-contact humanoid robot
- multi-ped robots

must remain deferred unless the Project Owner explicitly changes the blueprint.

### Rule F

Implementation order is:

1. `articulated_loop_env`
2. `dual_arm_manipulation_env`
3. `cable_parallel_env`
4. `parallelogram_singularity_env`

This order is authoritative for the first-wave buildout unless the owner changes it.

## Phase 1 — Establish The Family-Level Artifact Surface

### Stage 1.1 — Create The Running Log

#### Action 1.1.1

Create:

- `docs/design/test_design/example_family_implementation_log.md`

The log must include:

- status
- authoritative sources
- action-completion entries
- test-result entries
- owner-clarification entries
- blocker entries

### Stage 1.2 — Bind The Authoritative Source Set

#### Action 1.2.1

Record in the running log that the implementation is governed by:

- `example_family_blueprint_from_mathematical_model_list.md`
- `evaluation_strategy.md`
- the prime-directive stack

#### Action 1.2.2

Record in the running log that the first-wave build set is:

- `articulated_loop_env`
- `dual_arm_manipulation_env`
- `cable_parallel_env`
- `parallelogram_singularity_env`

and that the deferred set is:

- multi-contact humanoid robot
- multi-ped robots

This step is not for re-deciding the family set.

It is to bind the implementation surface before editing.

## Phase 2 — Build The Family-Level Design Folder Structure

### Stage 2.1 — Create The Env-Specific Design Folders

#### Action 2.1.1

Create:

- `docs/design/test_design/env_002/`
- `docs/design/test_design/env_003/`
- `docs/design/test_design/env_004/`
- `docs/design/test_design/env_005/`

Do not populate them with placeholder filler.

Only create these folders once the implementation interval actually begins.

### Stage 2.2 — Map Folder Numbers To Environment Families

#### Action 2.2.1

Record the canonical mapping:

- `env_002` → `articulated_loop_env`
- `env_003` → `parallelogram_singularity_env`
- `env_004` → `cable_parallel_env`
- `env_005` → `dual_arm_manipulation_env`

This prevents numbering drift later.

## Phase 3 — Build env_002: Articulated Loop Environment

### Stage 3.1 — Write The Env-Specific Spec

#### Action 3.1.1

Write:

- `docs/design/test_design/env_002/articulated_loop_env_spec.md`

This spec must make explicit:

- the conceptual picture
- the exact state type
- the exact action set
- the exact validity rule
- the hidden loop-closure constraint geometry
- the reason this env is evaluation-relevant for `state_collapser`

#### Action 3.1.2

Ensure the spec defines:

- a small closed discrete kinematic loop
- a closure rule that is neither too strict nor too decorative
- enough feasible graph structure to make quotient behavior interesting

### Stage 3.2 — Write The Env-Specific Implementation Gameplan

#### Action 3.2.1

Write:

- `docs/design/test_design/env_002/articulated_loop_env_implementation_gameplan.md`

It should define:

- file targets
- state and action implementation sequence
- validity-rule implementation sequence
- runtime/training integration sequence
- test sequence
- stop conditions

### Stage 3.3 — Implement The Example Package

#### Action 3.3.1

Create:

- `src/state_collapser/examples/articulated_loop_env/__init__.py`
- `src/state_collapser/examples/articulated_loop_env/env.py`
- `src/state_collapser/examples/articulated_loop_env/runtime.py`
- `src/state_collapser/examples/articulated_loop_env/training.py`

The package must follow the general example-package shape of `plate_support_env`.

#### Action 3.3.2

Implement the env so that:

- the naive ambient parameterization is simple
- the feasible hidden graph is cut down by loop-closure constraints
- the resulting example is inspectable and discrete

### Stage 3.4 — Add Tests

#### Action 3.4.1

Add env-specific tests under `tests/examples/` covering at minimum:

- geometry/closure logic
- validity
- primitive transitions
- rewards
- runtime integration
- a first training smoke path

### Stage 3.5 — Validate env_002

#### Action 3.5.1

Run the focused env-specific test slice and record results in the family implementation log.

Do not advance to the next family until `env_002` is structurally validated.

## Phase 4 — Build env_005: Dual-Arm Manipulation Environment

### Stage 4.1 — Write The Env-Specific Spec

#### Action 4.1.1

Write:

- `docs/design/test_design/env_005/dual_arm_manipulation_env_spec.md`

The spec must make explicit:

- the shared-object picture
- left/right arm state variables
- object pose variables
- validity rules for coordinated manipulation
- why this example is central to the package’s motivating claim

### Stage 4.2 — Write The Env-Specific Implementation Gameplan

#### Action 4.2.1

Write:

- `docs/design/test_design/env_005/dual_arm_manipulation_env_implementation_gameplan.md`

This gameplan must define the implementation order and stop conditions for the env.

### Stage 4.3 — Implement The Example Package

#### Action 4.3.1

Create:

- `src/state_collapser/examples/dual_arm_manipulation_env/__init__.py`
- `src/state_collapser/examples/dual_arm_manipulation_env/env.py`
- `src/state_collapser/examples/dual_arm_manipulation_env/runtime.py`
- `src/state_collapser/examples/dual_arm_manipulation_env/training.py`

#### Action 4.3.2

Keep the first version aggressively minimal.

Do not allow the env to expand into an overlarge manipulation simulator.

### Stage 4.4 — Add Tests

#### Action 4.4.1

Add env-specific tests under `tests/examples/` covering:

- state validity
- coordinated transition rules
- support/manipulation feasibility
- runtime integration
- training smoke behavior

### Stage 4.5 — Validate env_005

#### Action 4.5.1

Run the focused env-specific slice and record results in the family implementation log.

Do not advance until the dual-arm environment is structurally validated as a hidden-constraint env rather than merely a larger state tuple.

## Phase 5 — Build env_004: Cable Parallel Environment

### Stage 5.1 — Write The Env-Specific Spec

#### Action 5.1.1

Write:

- `docs/design/test_design/env_004/cable_parallel_env_spec.md`

The spec must make explicit:

- platform pose variables
- cable state variables
- coupled cable/support feasibility
- how this env differs structurally from `plate_support_env`

### Stage 5.2 — Write The Env-Specific Implementation Gameplan

#### Action 5.2.1

Write:

- `docs/design/test_design/env_004/cable_parallel_env_implementation_gameplan.md`

### Stage 5.3 — Implement The Example Package

#### Action 5.3.1

Create:

- `src/state_collapser/examples/cable_parallel_env/__init__.py`
- `src/state_collapser/examples/cable_parallel_env/env.py`
- `src/state_collapser/examples/cable_parallel_env/runtime.py`
- `src/state_collapser/examples/cable_parallel_env/training.py`

#### Action 5.3.2

Ensure this env is not merely `plate_support_env` with renamed supports.

Its validity structure must reflect cable-style coupled support semantics.

### Stage 5.4 — Add Tests

#### Action 5.4.1

Add env-specific tests under `tests/examples/` covering:

- geometry/reachability
- validity
- transition structure
- runtime integration
- training smoke behavior

### Stage 5.5 — Validate env_004

#### Action 5.5.1

Run the focused env-specific slice and record results in the family implementation log.

## Phase 6 — Build env_003: Parallelogram Singularity Environment

### Stage 6.1 — Write The Env-Specific Spec

#### Action 6.1.1

Write:

- `docs/design/test_design/env_003/parallelogram_singularity_env_spec.md`

The spec must make explicit:

- the linkage variables
- the consistency rule
- the singular or near-singular region
- why that singular structure matters for evaluation

### Stage 6.2 — Write The Env-Specific Implementation Gameplan

#### Action 6.2.1

Write:

- `docs/design/test_design/env_003/parallelogram_singularity_env_implementation_gameplan.md`

### Stage 6.3 — Implement The Example Package

#### Action 6.3.1

Create:

- `src/state_collapser/examples/parallelogram_singularity_env/__init__.py`
- `src/state_collapser/examples/parallelogram_singularity_env/env.py`
- `src/state_collapser/examples/parallelogram_singularity_env/runtime.py`
- `src/state_collapser/examples/parallelogram_singularity_env/training.py`

#### Action 6.3.2

Ensure that singularity is operational, not decorative.

The env must contain meaningful changes in local feasible geometry near the singular regime.

### Stage 6.4 — Add Tests

#### Action 6.4.1

Add env-specific tests under `tests/examples/` covering:

- linkage consistency
- singular-region behavior
- transition structure
- runtime integration
- training smoke behavior

### Stage 6.5 — Validate env_003

#### Action 6.5.1

Run the focused env-specific slice and record results in the family implementation log.

## Phase 7 — Cross-Family Evaluation Readiness

### Stage 7.1 — Confirm Shared Evaluation Shape

#### Action 7.1.1

For each built environment, confirm that the env design still supports the general evaluation strategy:

- plain Gymnasium problem
- top-tier-only problem
- full-tower problem

If one environment cannot honestly support that comparison structure, stop and record why.

### Stage 7.2 — Record Structural Differences Across The Family

#### Action 7.2.1

Record in the family implementation log what each built environment contributes uniquely:

- loop-closure hidden geometry
- singular-region hidden geometry
- cable-coupling hidden geometry
- dual-arm coordination hidden geometry

This is to prevent the family from collapsing into four superficial variants of the same env.

## Phase 8 — Repo Integration

### Stage 8.1 — Export Example Packages Cleanly

#### Action 8.1.1

Update package exports as needed so each environment can be imported cleanly from the examples namespace without forcing users through unstable internal paths.

### Stage 8.2 — Preserve Existing Example Behavior

#### Action 8.2.1

Ensure the buildout does not regress:

- `plate_support_env`
- `robot_constraint_toy`

unless an explicit owner directive authorizes such a change.

## Phase 9 — Validation Sequence

### Stage 9.1 — Per-Environment Focused Validation

#### Action 9.1.1

Run focused test slices for each environment as it lands.

Record results incrementally in the family implementation log.

### Stage 9.2 — Broader Example Validation

#### Action 9.2.1

After the family is implemented, run the broader example test slice across:

- existing example envs
- the new example env family

Record results.

### Stage 9.3 — Full Validation

#### Action 9.3.1

Run:

- full `pytest`
- `ruff`
- `mypy`

Record results in the family implementation log.

## Phase 10 — Completion Criteria

### Stage 10.1 — Family Completion Check

#### Action 10.1.1

This implementation counts as complete only if:

- each chosen first-wave family has:
  - a real env package
  - a real spec
  - a real implementation gameplan
  - real tests
- each env encodes the intended hidden constraint geometry honestly
- the family supports the evaluation strategy rather than only increasing example count
- deferred families remain deferred unless the owner explicitly changes the decision

### Stage 10.2 — Stop Condition

#### Action 10.2.1

If one or more environments are implemented but the resulting family still looks like:

- a collection of renamed variants of `plate_support_env`

then do not report the family as complete.

Report the structural failure explicitly.
