# `rl_counterpoint_v3` Blueprint

## Status

This document is the first authoritative blueprint for:

- `src/state_collapser/examples/rl_counterpoint_v3/`

It supersedes the earlier incorrect two-voice framing.

It is downstream of:

- [01_001_rl_counterpoint_v3_transformation_report.md]([state_collapser repository root]/docs/design/test_design/rl_counterpoint_v3/01_001_rl_counterpoint_v3_transformation_report.md)

This is a design document.

It is not:

- an implementation gameplan
- a partial port note
- a scratchpad of possible scopes

Its job is to define the first correct `rl_counterpoint_v3` problem for `state_collapser`.

## Purpose

The purpose of `rl_counterpoint_v3` in this repository is:

- to rebuild the underlying counterpoint RL problem that historically motivated the project-manager’s HRL thinking
- but to rebuild it in the example-oriented, inspectable, package surfaces of `state_collapser`

The environment should therefore be:

- musically meaningful
- graph-theoretically nontrivial
- small enough to inspect
- rich enough that induced tower structure could plausibly matter

And it should **not** be:

- a port of the explicit hand-authored tower from `[rl_counterpoint repository root]/tower`
- a transformer training stack
- a checkpoint/artifact/lineage system
- a staged-rank curriculum package

## Core Design Claim

The central claim of this blueprint is:

> The first `rl_counterpoint_v3` example should be a **three-voice flat constrained RL problem**, not an already-authored hierarchy over one voice, two voices, and three voices.

That means:

- the problem surface itself is 3-voice from the beginning
- the environment does not encode explicit rank-1 / rank-2 / rank-3 training phases
- the environment does not own any frozen-parent scaffold semantics
- the hierarchy, if useful, should be something `state_collapser` attempts to induce over the flat 3-voice problem

This is the single most important architectural constraint in the whole blueprint.

## First-Scope Decision

### Decision

The first `rl_counterpoint_v3` implementation will be:

- a **three-voice counterpoint problem**

not:

- a two-voice bridge problem
- a direct port of the old rank tower

### Why this is the right scope

The reason is not “bigger is better.”

The reason is that the point of this example is historical and conceptual:

- `rl_counterpoint` mattered because of the hierarchical pressure created by multi-voice counterpoint
- a two-voice port would recover only part of that pressure
- the first serious `state_collapser` counterpoint example should therefore begin where hidden structure is genuinely present: the three-voice problem

There is also a more specific design reason.

A two-voice problem is too close to the old explicit rank decomposition:

- one line
- then a second line over it

and therefore creates more temptation to rebuild the old hand-authored tower by stealth.

A three-voice flat problem is better for `state_collapser` because:

- the ambient problem is already meaningfully coupled
- inner-voice constraints become real
- the problem no longer looks like a trivial extension of a single line
- induced quotient structure has more room to matter without us pre-supplying it

So the first scope should start where:

- the hierarchy pressure is real
- but the hierarchy is not already explicitly authored into the example surface

## Canonical Package Shape

The example package should eventually be:

```text
src/state_collapser/examples/rl_counterpoint_v3/
  __init__.py
  env.py
  runtime.py
  training.py
```

Its tests should live under:

- `tests/examples/`

Its design and implementation documents should live under:

- `docs/design/test_design/rl_counterpoint_v3/`

This package should follow the broad example-package idiom of:

- `plate_support_env`
- the newer example-family envs

while remaining musically and structurally distinct from all of them.

## Core Problem Statement

The first `rl_counterpoint_v3` environment is:

- a finite-horizon episodic RL problem over **three-note chord states**
- where each step proposes a bounded simultaneous signed pitch update to all three voices
- and legality is determined by a hidden subset of valid contrapuntal transitions

The task is:

- generate a short three-voice passage
- that stays inside the legal voiceleading graph
- while accumulating a narrow first slice of contrapuntal reward
- and trying to reach a simple musically meaningful terminal cadence-like configuration

The key hidden geometry comes from the fact that:

- the ambient state and action products are simple
- but the legal node and edge sets are sharply trimmed by ordering, interval, spacing, and motion constraints

That is exactly the sort of problem that should be valuable inside `state_collapser`.

## State Surface

### Canonical first state type

The first implementation should use an immutable state record:

```python
@dataclass(frozen=True, slots=True)
class RlCounterpointState:
    bass_pitch: int
    inner_pitch: int
    upper_pitch: int
    beat_index: int
```

### Semantics

- `bass_pitch` is the lowest voice
- `inner_pitch` is the middle voice
- `upper_pitch` is the highest voice
- `beat_index` is the within-measure position

### Why this state is right

This is the smallest explicit state that still captures:

- three-voice ordering
- interior-voice existence
- episodic metrical structure

It intentionally does **not** include:

- explicit long observation windows
- model-side feature tensors
- explicit lower-rank parent state
- explicit rank labels

The environment may still maintain history internally for reward evaluation, but the explicit graph state should remain small and concrete.

### State invariants

A valid state must satisfy:

1. all three pitches are within a configured MIDI band
2. voice order is strict:
   - `bass_pitch < inner_pitch < upper_pitch`
3. adjacent vertical intervals lie inside a configured admissible set
4. the outer interval lies inside a configured admissible set
5. `beat_index` lies in `{0, ..., measure_size - 1}`

These invariants are the basic node-membership conditions of the hidden graph.

## Episode Context Versus Explicit State

This blueprint deliberately separates:

### Explicit state

- the three pitches
- the current metrical slot

### Internal episode context

- step index
- full episode history
- measure size
- max steps
- terminal target configuration
- optional cadence deadline logic

### Why this separation matters

If too much temporal machinery is pushed directly into state, the example becomes:

- a sequence-model observation problem

rather than:

- a graph problem with episode context

The initial example should stay closer to the latter.

## Action Surface

### Canonical first action type

The primitive action should be interpreted as:

- a bounded signed pitch delta for each of the three voices

Internally:

```python
StepDelta = tuple[int, int, int]
```

### Action family

The ambient primitive action family should be:

```text
{ -d, ..., 0, ..., +d }^3 \ {(0, 0, 0)}
```

with a small configured:

- `max_step_size`

The first recommended default is:

- `max_step_size = 2`

### Why this is the right action surface

This preserves a central good idea from `rl_counterpoint`:

- actions live in a simple bounded per-voice delta lattice

while avoiding a large and overgrown first branching factor.

The important property is:

- the ambient action lattice is simple
- but the legal-action subset from any given state is hidden and structured

That is the real value here.

### Action semantics

If the current state is:

```text
(bass_pitch, inner_pitch, upper_pitch, beat_index)
```

and the action is:

```text
(delta_bass, delta_inner, delta_upper)
```

then the candidate next state is:

```text
(
  bass_pitch + delta_bass,
  inner_pitch + delta_inner,
  upper_pitch + delta_upper,
  (beat_index + 1) mod measure_size
)
```

Candidate legality is then checked by the edge predicate.

## Graph Specification Surface

The environment should have a small explicit graph spec object, conceptually descended from the old `CounterpointGraphSpec`, but smaller and shaped for `state_collapser` examples.

### Canonical first spec

```python
@dataclass(frozen=True, slots=True)
class RlCounterpointGraphSpec:
    tonic_pitch_class: int = 0
    pitch_min: int = 48
    pitch_max: int = 79
    measure_size: int = 4
    max_steps: int = 16
    max_step_size: int = 2
    allowed_adjacent_intervals_mod_12: frozenset[int] = ...
    allowed_outer_intervals_mod_12: frozenset[int] = ...
    forbidden_parallel_interval_classes: frozenset[int] = ...
    max_outer_span: int = ...
    require_strict_voice_order: bool = True
```

The exact field names may shift slightly, but this is the right scale and authority boundary.

### What the spec owns

The spec should own:

- pitch bounds
- interval-class rules
- spacing bounds
- action-step bounds
- episode length / measure structure

This keeps the environment small and explicit instead of scattering the problem definition across multiple files.

## Node Legality

Node legality is the first part of the hidden graph.

A state is valid iff:

1. all pitches are within range
2. ordering is strict:
   - `bass_pitch < inner_pitch < upper_pitch`
3. adjacent intervals are permitted
4. the outer interval is permitted
5. the overall span does not exceed a configured maximum
6. the bass pitch class belongs to an allowed harmonic root-class family

### Why these rules

These are direct descendants of the real problem content in `rl_counterpoint`:

- pitch order
- vertical spacing
- outer-interval admissibility
- root-class admissibility

This is enough to create a meaningful hidden state subset without porting the whole old repo.

## Edge Legality

Edge legality is where the example becomes truly interesting for `state_collapser`.

A transition is valid iff:

1. the candidate target state is node-valid
2. each voice motion is within the configured step bound
3. the transition satisfies a narrow first slice of contrapuntal motion rules

### First-pass motion rules

The first implementation should include only a small number of edge rules.

Recommended first slice:

1. **No voice crossing**
   - already implied by strict target ordering
2. **No exact zero action**
   - `(0, 0, 0)` excluded from the action family
3. **Disallow parallel perfect intervals in the outer voices**
   - if the bass and upper voices move in the same direction and the outer interval class stays inside the configured perfect set, reject
4. **Disallow exact unison adjacency collapse**
   - target adjacent intervals must remain positive and legal
5. **Optional inner-voice leap guard**
   - if needed, reject certain larger simultaneous motions involving the middle voice even if the raw step bound allows them

### Why keep this slice narrow

The first port is not trying to formalize all of counterpoint.

It is trying to recover:

- a real constrained RL problem

with enough hidden edge structure that induced tower behavior becomes meaningful.

So the first legality stack should be:

- sharp
- testable
- inspectable

not encyclopedic.

## Reward Surface

The first reward surface should preserve the old repo’s reward **shape**, but not its full musical elaboration.

### Reward protocol

The environment should expose:

- structured reward context
- structured reward result

The context should include at least:

- current step index
- max steps
- measure size
- source state
- target state
- action
- finite episode history
- whether the step is terminal/final

The reward result should include:

- scalar reward
- terminal-success flag
- optional hard-violation flag
- diagnostics mapping

This preserves one of the strongest old-repo interfaces while staying within the lighter example style of `state_collapser`.

### First-pass reward terms

The first reward should be intentionally narrow.

Recommended terms:

1. **Per-step cost**
   - small negative reward each step
2. **Terminal cadence success reward**
   - larger positive reward on successful terminal configuration
3. **Simple consonance preference**
   - small positive weight for preferred adjacent and/or outer interval classes
4. **Downbeat stability preference**
   - on downbeats, prefer especially stable sonorities
5. **Optional mild melodic smoothness preference**
   - discourage needlessly large simultaneous leaps if this is not already captured well enough by legality

### Explicit non-goal

The first implementation should **not** try to port:

- full TC21M reward bundles
- rank-owned reward decomposition
- advanced cadence micro-terms
- rich beat-class taxonomies
- transformer-specific reward diagnostics

The first reward should be good enough to make the RL problem real, not complete enough to settle computational music theory.

## Terminal Condition

The terminal condition should be musically meaningful but simple.

### Recommended first success condition

The episode succeeds when:

- the final step lands in a configured terminal beat regime
- the bass resolves to the tonic pitch class
- the outer voice forms a desired terminal consonance above it
- the inner voice lies between them in a configured admissible terminal relation

This is intentionally a **three-voice** terminal condition from the start.

It should not be defined as:

- “first solve a 1-voice cadence”
- then “extend to 2 voices”
- then “extend to 3 voices”

That would reimport the old hand-authored hierarchy.

Instead, terminal success should be checked directly on the 3-voice state.

### Truncation

The episode truncates when:

- `step_index >= max_steps`

The first port should avoid complicated rank-local deadline logic.

## Reset Semantics

Reset should:

- sample from a curated subset of valid 3-voice start states
- initialize beat and episode counters
- initialize history
- initialize terminal target context if needed

The start-state subset must be:

- non-terminal
- valid
- and have at least one legal outgoing action

This is important because a frozen or degenerate start set would ruin the example immediately.

## Runtime Surface

The runtime integration should follow the normal `state_collapser` example pattern.

### Runtime responsibilities

The runtime should:

- translate `RlCounterpointState` into package core `State`
- translate primitive discrete action indices into package `PrimitiveAction`
- expose the environment as a `HiddenGraph` problem
- let `TowerRuntime` construct induced tower structure over the flat 3-voice counterpoint problem

### What the runtime must not do

It must not:

- reconstruct rank-1 / rank-2 / rank-3 explicit projections
- import hand-authored lower-rank parent-child semantics
- own any staged chord-rank hierarchy

If the runtime starts encoding the old `rl_counterpoint/tower` decomposition, the blueprint has been violated.

## Training Surface

The initial training surface should be minimal and example-shaped.

### Required first training surface

- one `run_tower_training(...)` entrypoint

This is enough for:

- environment validity
- runtime validity
- basic learning smoke tests
- early structural evaluation

### Not required for first implementation

- exploit/explore control path
- transformer policy integration
- curriculum staging
- artifact-backed musical generation outputs

Those may come later, but they should not control the first build.

## What Must Be Intentionally Omitted

The first implementation must not include:

- explicit imported tower rank semantics
- transformer models
- tensor observation encoders
- PyTorch training loops
- checkpoint lineage
- artifact directories
- MIDI export
- parent/child frozen scaffold training
- reward bundles copied wholesale from the old repo

These are not “nice-to-haves postponed.”

They are things that would actively distort the correct `state_collapser` example boundary if imported too early.

## Why This Is A Good `state_collapser` Example

If implemented correctly, `rl_counterpoint_v3` should be a strong example because it has:

- simple ambient tuple states
- simple ambient tuple actions
- a hidden legal node and edge subset
- real interior-voice coupling
- no obvious human-labeled subtask decomposition at the example surface
- rich local structural regularity that may admit quotienting

This is exactly the kind of setting where the package’s claims should be tested:

- hierarchy is not handed to the system
- but strong hidden structure is present

## Relation To Existing Examples

This example broadens the repo in a genuinely new direction.

### Relative to `plate_support_env`

- not a spatial support-placement problem
- instead a symbolic but heavily constrained voiceleading problem

### Relative to `articulated_loop_env`

- not closure mismatch over link directions
- instead ordered pitch-tuple legality and motion constraints

### Relative to `dual_arm_manipulation_env`

- not coordination over a shared physical object
- instead coordination over three simultaneous melodic/vertical lines

### Relative to `parallelogram_singularity_env`

- not singular linkage geometry
- instead hidden contrapuntal graph structure

So this example is not a reskin of the current family.

It adds a new symbolic domain with genuinely different hidden geometry.

## Acceptance Standard

The first implementation will count as faithful to this blueprint only if:

1. it is three-voice from the start
2. it is a flat constrained RL problem
3. it preserves ordered pitch tuples and bounded per-voice deltas
4. it has real hidden node and edge legality
5. it uses a narrow structured reward protocol
6. it does not smuggle the old explicit `rl_counterpoint` tower back in through env or runtime design

If the resulting package instead looks like:

- a compressed port of `[rl_counterpoint repository root]/tower`

then the blueprint has failed.

## Next Document

The next document after this blueprint should be:

- an implementation gameplan in `Phase.Stage.Action` form

That gameplan should take as fixed:

- first scope is three voices
- flat constrained RL problem
- no imported explicit rank tower
- narrow structured reward slice
- simple example-package surface
