# Example Family Blueprint From Mathematical-Model List

## Status

This document is a blueprint for turning the robotics-style example list in:

- `docs/design/mathematical_model_w_Codex_comments.tex`

into concrete `state_collapser` evaluation environments under:

- `src/state_collapser/examples/`

It is not an implementation gameplan.

It is not a bibliography note.

It is a decision document whose job is to:

- decide which cited example families should become package examples now
- decide which should be deferred
- explain why
- sketch each chosen environment in enough detail that a later implementation gameplan can be written cleanly

It sits downstream of:

- [evaluation_strategy.md]([state_collapser repository root]/docs/design/test_design/evaluation_strategy.md)
- [plate_support_env_spec.md]([state_collapser repository root]/docs/design/test_design/env_001/plate_support_env_spec.md)

## Purpose

The purpose of this document is to answer the following design question:

> Given the mathematical-model list of constrained mechanical systems with hard-to-isolate hierarchical structure, which of these should be instantiated as discrete evaluation environments in the current repo, and what should those environments look like?

The environments described here are **not** intended to be faithful robotics simulators.

They are intended to be:

- small
- discrete
- inspectable
- structurally honest analogues of the cited problem families

The goal is to preserve the kind of hidden constraint geometry that makes hierarchy hard to isolate, while still fitting the current package’s runtime, tower, and evaluation surfaces.

## Governing Constraints

The decision logic in this document follows the current repo reality.

At the present stage, an example environment should be:

- discrete
- small enough to inspect
- suitable for hidden-graph and tower runtime use
- meaningful under reward locality assumptions
- rich enough that tower construction could plausibly matter

This means we are **not** choosing examples based on which robotics system is most impressive in the literature.

We are choosing examples based on which system can be converted into:

- a package-appropriate evaluation environment
- with a state graph whose hidden constraint geometry is nontrivial
- without requiring continuous control, heavy physics, or external simulators

## The Source List

The source list in the mathematical-model document is:

1. articulated mechanism with loop-closure constraints
2. parallelogram linkage with singularities
3. cable-driven parallel robot
4. dual-arm manipulation system
5. multi-contact humanoid robot
6. multi-ped robots

## High-Level Decisions

### Decision 1 — Not every cited system should become a first-wave repo example

Some of the cited systems make excellent conceptual motivation examples, but poor first-wave discrete package environments.

In particular:

- multi-contact humanoid robot
- multi-ped robots

are likely too large and too hard to discretize cleanly at the current stage if the goal is:

- interpretable graph structure
- honest evaluation
- fast implementation

These should be treated as later-family aspirations, not immediate environment targets.

### Decision 2 — First-wave environments should be small discrete analogues, not literal simulators

For every selected family, the implementation target should look more like:

- `plate_support_env`

than like:

- a research robotics benchmark

Each chosen env should probably have its own package folder under:

- `src/state_collapser/examples/<env_name>/`

with at least:

- `__init__.py`
- `env.py`
- `runtime.py`
- `training.py`

and matching tests under:

- `tests/examples/`

### Decision 3 — The first wave should prioritize hidden constraint geometry over physical realism

The best first-wave additions are the ones where:

- the ambient Cartesian parameterization is misleadingly simple
- but the feasible state/action region is cut down sharply by coupled constraints
- and that feasible region should produce repeated quotientable regularity

That is the real target.

## Summary Of Which Examples To Build

### Build now

These are good first-wave example families for the current repo:

1. articulated mechanism with loop-closure constraints
2. parallelogram linkage with singularities
3. cable-driven parallel robot
4. dual-arm manipulation system

### Defer

These should be treated as later-wave environments:

5. multi-contact humanoid robot
6. multi-ped robots

The deferred families are still valuable conceptually, but they are less suitable for the current stage because:

- they are larger
- they risk requiring too many coupled discrete contact/mode variables
- they will be harder to evaluate honestly before instrumentation and package-consumer workflow surfaces mature further

## Proposed Naming And Ordering

The next environment family numbering after `env_001` should be:

- `env_002` articulated loop-closure mechanism
- `env_003` parallelogram singularity mechanism
- `env_004` cable-driven parallel support system
- `env_005` dual-arm shared-object manipulation

The corresponding example package names should be explicit and conservative:

- `articulated_loop_env`
- `parallelogram_singularity_env`
- `cable_parallel_env`
- `dual_arm_manipulation_env`

These names are intentionally descriptive rather than clever.

## Detailed Blueprint For Each Candidate

## env_002 — Articulated Loop-Closure Mechanism

### Canonical package placement

- `src/state_collapser/examples/articulated_loop_env/`

### Why this family should be built

This is probably the most direct next example after `plate_support_env`.

Why:

- loop-closure constraints are a very clean illustration of a feasible set that is much smaller than the naive product parameterization
- the ambient coordinates suggest easy factorization
- the actual feasible transitions are strongly coupled
- it should produce repeated local equivalence structure without obvious subtasks

### Conceptual picture

The world contains:

- a planar articulated chain or small linkage
- one or more joints with discrete angle bins
- a loop-closure requirement that forces the end of the chain to match a target anchor or return socket

The agent controls:

- joint-angle increments
- possibly one or two mode variables such as brace state or engagement state

The state is valid only when:

- the chain satisfies loop closure
- link motion does not violate simple discrete collision or range constraints

### Discrete analogue we should implement

The best first implementation is not a general articulated-mechanism simulator.

It should be:

- a small closed kinematic loop with 3–4 discrete joints
- with angle bins such as `{-1, 0, +1}` or a slightly richer small set
- with closure defined by a discrete endpoint coincidence rule

### Recommended state shape

Something like:

```text
(theta_1, theta_2, theta_3, brace_mode)
```

or, if a four-joint version is needed:

```text
(theta_1, theta_2, theta_3, theta_4, brace_mode)
```

### Recommended action shape

Discrete actions that:

- increment or decrement one joint bin
- toggle or adjust brace/engagement mode if needed

### Constraint geometry

The hidden constraint is:

- not all joint combinations close the loop

This means the feasible graph is cut out of a much larger ambient lattice.

### What should make this interesting for `state_collapser`

- many ambient states do not correspond to feasible loop-closed states
- nearby feasible states should often differ in ways that reflect hidden quotientable regularity
- there is no obvious subtask decomposition in the usual HRL sense

### Main risk

If the closure rule is too strict, the graph becomes too small or fragmented.

If it is too loose, the env loses the whole point.

So implementation should choose:

- a closure condition that permits enough feasible states to make graph structure interesting

## env_003 — Parallelogram Linkage With Singularities

### Canonical package placement

- `src/state_collapser/examples/parallelogram_singularity_env/`

### Why this family should be built

This family is attractive because it adds a different kind of hidden geometry:

- not only coupled feasibility
- but singular or near-singular mode boundaries

This is useful because it can expose:

- bottlenecks
- mode collapse
- topological thinness

that may matter for tower construction.

### Conceptual picture

The world contains:

- a discrete parallelogram-style linkage
- a small set of shape variables
- one or more singular configurations where motion options collapse or become sharply restricted

The agent controls:

- local joint-shape adjustments
- possibly orientation/mode toggles

The state is valid only when:

- the linkage remains consistent with the parallelogram structure

### Discrete analogue we should implement

The first version should represent:

- a small four-bar or parallelogram linkage
- with discrete relative-angle or offset bins
- where singular configurations are explicit discrete states at which outgoing degree changes sharply

### Recommended state shape

Something like:

```text
(left_angle_bin, right_angle_bin, top_offset_bin, bottom_offset_bin)
```

or a more minimal reduced variant if that is too redundant.

### Recommended action shape

- increment/decrement one linkage variable at a time
- possibly one coarse pose/mode move if needed to keep the graph connected enough

### Constraint geometry

The hidden structure comes from:

- linkage consistency constraints
- singular configurations where the local feasible transition set changes abruptly

### What should make this interesting for `state_collapser`

- not all locally similar ambient states have similar feasible neighborhoods
- singular states can act like hidden structure boundaries
- quotienting may reveal repeated motion structure away from singularities

### Main risk

If singularity is represented only as "one weird state," the env may be too thin.

So the implementation should ensure there is a meaningful region of altered local geometry, not just one decorative singular point.

## env_004 — Cable-Driven Parallel Support System

### Canonical package placement

- `src/state_collapser/examples/cable_parallel_env/`

### Why this family should be built

This is a strong next example because it stays close in spirit to `plate_support_env`, but introduces a different hidden-constraint logic:

- tension or support feasibility through multiple coupled cables
- rather than rigid support reachability by discrete arms

This is likely a very good evaluation environment for:

- comparing two related but not identical support-constraint systems

### Conceptual picture

The world contains:

- a platform in a discrete workspace
- several anchored cables
- cable-length or cable-tension mode variables

The agent controls:

- platform pose
- cable mode adjustments

The state is valid only when:

- cable geometry remains feasible
- enough support/tension balance exists

### Discrete analogue we should implement

The first version should likely be:

- a small grid-positioned platform
- 3 or 4 anchor points
- discrete cable extension/tension bins
- validity determined by simple reach/balance inequalities

### Recommended state shape

Something like:

```text
(x_idx, y_idx, theta_idx, c1, c2, c3, c4)
```

where each `c_i` is a discrete cable state.

### Recommended action shape

- move platform in a small discrete workspace
- rotate platform if useful
- increase/decrease one cable state at a time

### Constraint geometry

The feasible set is not just:

- pose product cable modes

Instead:

- many pose/cable combinations are invalid because they violate coupled support constraints

### What should make this interesting for `state_collapser`

- hidden feasible region inside a naive ambient parameter product
- local equivalence classes across repeated support configurations
- natural comparison against `plate_support_env`

### Main risk

If this env is too similar to `plate_support_env`, it may not add enough new evaluation value.

So the design should emphasize:

- cable-coupling structure
- not just "plate support with renamed arms"

## env_005 — Dual-Arm Shared-Object Manipulation

### Canonical package placement

- `src/state_collapser/examples/dual_arm_manipulation_env/`

### Why this family should be built

This is probably the most important example in the set from the standpoint of the repo’s motivating story:

- two coordinated effectors
- one shared object
- many feasible moves depend on hidden coordination constraints
- no obvious clean subtask hierarchy

This feels very central to the package’s conceptual identity.

### Conceptual picture

The world contains:

- a shared object in a small workspace
- two discrete arms or grippers
- object pose and grip-mode variables

The agent controls:

- left arm adjustment
- right arm adjustment
- object pose moves mediated through valid dual-arm support states

The state is valid only when:

- the object remains jointly supportable/manipulable
- the arms do not violate reach/coupling constraints

### Discrete analogue we should implement

The first version should be significantly smaller than a real dual-arm manipulation simulator.

The right scale is probably:

- small object pose grid
- small left-arm and right-arm discrete extension/contact states
- optional binary grasp mode indicators

### Recommended state shape

Something like:

```text
(obj_x, obj_y, obj_theta, left_mode, right_mode, left_reach, right_reach)
```

or a similarly small but expressive tuple.

### Recommended action shape

- adjust left arm state
- adjust right arm state
- move or rotate object by one discrete step when joint support permits

### Constraint geometry

The feasible graph should be defined by:

- left/right coordination
- object support feasibility
- shared-object manipulation constraints

This gives a richer version of the "support and coordinated movement" story already present in `plate_support_env`.

### What should make this interesting for `state_collapser`

- strong hidden coupling
- no obvious human-readable subtask breakdown
- many locally similar ambient descriptions but sharply constrained feasible transitions

### Main risk

This could get too large too quickly.

So the first implementation should be aggressively minimized and made interpretable first.

## Deferred Families

## env_later_A — Multi-Contact Humanoid Robot

### Decision

Defer.

### Why

This family is conceptually excellent but currently too risky for a first-wave package example because it tends to require:

- many contact-mode variables
- large discrete combinatorics
- difficult interpretation of feasible transitions

The likely result right now would be:

- a noisy, under-inspectable env
- not an honest early evaluation environment

### When to revisit

After:

- instrumentation is stronger
- evaluation methodology is more mature
- the package has clearer outsider-facing workflows

## env_later_B — Multi-Ped Robot

### Decision

Defer.

### Why

This family has similar issues to the humanoid family:

- many coordinated contact/support states
- fast combinatorial blow-up
- hard-to-interpret graph structure unless very carefully simplified

It is still a very good later target, but not yet the best use of the current implementation bandwidth.

## Cross-Example Structural Requirements

Every environment selected from this blueprint should be designed to support, where possible:

1. plain Gymnasium training
2. top-tier-only training
3. full-tower training

This requirement comes from:

- [evaluation_strategy.md]([state_collapser repository root]/docs/design/test_design/evaluation_strategy.md)

And every environment should be:

- small enough to inspect
- reward-local
- hidden-constraint-heavy
- not trivially decomposable into obvious subtasks

## Recommended Implementation Order

The recommended order is:

1. `articulated_loop_env`
2. `dual_arm_manipulation_env`
3. `cable_parallel_env`
4. `parallelogram_singularity_env`

### Why this order

#### 1. `articulated_loop_env`

This is the cleanest next discrete constrained-geometry example after `plate_support_env`.

#### 2. `dual_arm_manipulation_env`

This is likely the most important conceptually for the package claim.

#### 3. `cable_parallel_env`

This provides a strong comparison family near `plate_support_env` without being identical.

#### 4. `parallelogram_singularity_env`

This is valuable, but singularity structure is a little easier to make decorative rather than operational, so it should come after the more straightforward constrained-feasibility families.

## Folder And Doc Shape Recommendation

For each selected env family, create:

- `src/state_collapser/examples/<env_name>/__init__.py`
- `src/state_collapser/examples/<env_name>/env.py`
- `src/state_collapser/examples/<env_name>/runtime.py`
- `src/state_collapser/examples/<env_name>/training.py`

And create matching design folders:

- `docs/design/test_design/env_002/`
- `docs/design/test_design/env_003/`
- `docs/design/test_design/env_004/`
- `docs/design/test_design/env_005/`

Each env folder should eventually get at least:

- a spec
- an implementation gameplan
- an implementation log

## Final Summary

The mathematical-model list should not be implemented literally as six robotics simulators.

It should be translated into a family of small, discrete, hidden-constraint evaluation environments.

The first-wave build set should be:

- articulated loop-closure mechanism
- parallelogram singularity mechanism
- cable-driven parallel support system
- dual-arm shared-object manipulation system

The deferred set should be:

- multi-contact humanoid robot
- multi-ped robots

And all of the first-wave environments should be implemented in the repo in the same general example-package style as:

- `src/state_collapser/examples/plate_support_env/`

while remaining faithful to the package’s actual evaluation needs:

- hidden constraint geometry
- non-canonical hierarchy
- reward locality
- discrete inspectability
