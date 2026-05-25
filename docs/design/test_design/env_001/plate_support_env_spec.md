# PlateSupportEnv Specification

## Purpose

`PlateSupportEnv` is the first proposed package-evaluation environment for `state_collapser`.

The goal of this environment is to provide a **small, discrete, robot-flavored constrained RL problem** that is simple enough to implement quickly, but structured enough that a quotient-tower method could plausibly outperform flat `gymnasium` training.

This environment is intended to test:

- whether `state_collapser` helps on a hidden feasible state graph cut out by constraints
- whether tower construction helps navigate a constrained discrete space more efficiently than flat RL
- whether the package can exploit repeated local support-configuration structure

## Canonical repository placement

For `env_001`, the canonical first implementation should live at:

- `src/state_collapser/examples/plate_support_env/env.py`

The example package should expose the env through:

- `src/state_collapser/examples/plate_support_env/__init__.py`

Its env-specific tests should live under:

- `tests/examples/`

Its env-specific design and implementation-planning docs should live in:

- `docs/design/test_design/env_001/`

This placement is part of the intended first implementation shape for the repository.

Implementation should not silently relocate this env into a different package area unless the Project Owner explicitly approves that change.

It is **not** intended to be a physically accurate robotics simulator.

## Conceptual picture

The world contains:

- one rigid rectangular metal plate
- three vertical support arms mounted below the plate at fixed base positions
- a discrete workspace grid

The agent controls:

- the plate pose on the grid
- the extension state of each support arm

The plate must remain adequately supported. Many ambient configurations are invalid because the support arms do not reach the plate correctly or because the support pattern is not stable enough.

So the true state space is a constrained subset of the naive Cartesian product:

```text
position x orientation x arm_1 x arm_2 x arm_3
```

This is exactly the kind of discrete hidden-feasibility graph that should be interesting for `state_collapser`.

## Workspace and plate geometry

### Workspace grid

The plate center moves on a discrete `5 x 5` grid:

- `x_idx in {0,1,2,3,4}`
- `y_idx in {0,1,2,3,4}`

These indices correspond to integer workspace coordinates.

### Plate orientation

The plate orientation is discretized into four bins:

- `theta_idx = 0` means `0` degrees
- `theta_idx = 1` means `90` degrees
- `theta_idx = 2` means `180` degrees
- `theta_idx = 3` means `270` degrees

So orientation is quarter-turn only.

### Plate support points

The plate has three designated support sockets in local plate coordinates:

- `p_left  = (-1, 0)`
- `p_mid   = ( 0, 0)`
- `p_right = ( 1, 0)`

After rotating and translating the plate, these become the world-space locations that the three support arms must reach if engaged.

### Support-arm base locations

The three support arms are mounted at fixed workspace base positions:

- `b_1 = (1, 2)`
- `b_2 = (2, 2)`
- `b_3 = (3, 2)`

These are fixed throughout the episode.

### Fixed arm-to-socket assignment

This environment uses a **fixed support assignment**:

- arm `1` is assigned to the left socket
- arm `2` is assigned to the middle socket
- arm `3` is assigned to the right socket

This is part of the environment definition for `env_001`.

The first implementation must **not** reinterpret support feasibility as:

- best matching
- nearest-socket matching
- permutation over sockets
- assignment search

Each arm is tested only against its designated socket.

## State space

Each state is a discrete tuple:

```python
(x_idx, y_idx, theta_idx, e1, e2, e3)
```

where:

- `x_idx in {0,1,2,3,4}`
- `y_idx in {0,1,2,3,4}`
- `theta_idx in {0,1,2,3}`
- `e1, e2, e3 in {0,1,2}`

Each `e_i` is the extension mode of support arm `i`.

### Arm extension semantics

For each support arm:

- `e_i = 0` means retracted / not supporting
- `e_i = 1` means medium extension
- `e_i = 2` means full extension

These are discrete support modes, not continuous lengths.

For `env_001`, their operational meaning is defined exactly by the reachability rule:

- `e_i = 0` gives no support and no reach
- `e_i = 1` allows Manhattan reach distance at most `1`
- `e_i = 2` allows Manhattan reach distance at most `2`

The implementation should treat this as the definition, not as a loose physical metaphor.

## Observation space

For a tabular or simple discrete-baseline version of the env, the observation is exactly the full state tuple:

```python
(x_idx, y_idx, theta_idx, e1, e2, e3)
```

Gymnasium encoding options:

1. `spaces.MultiDiscrete([5, 5, 4, 3, 3, 3])`
2. a flattened integer encoding of the same state

The recommended first implementation is:

```python
gymnasium.spaces.MultiDiscrete([5, 5, 4, 3, 3, 3])
```

because it is more interpretable.

## Exact Python state type

The first implementation should use a small immutable state record.

Recommended:

```python
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class PlateSupportState:
    x_idx: int
    y_idx: int
    theta_idx: int
    e1: int
    e2: int
    e3: int
```

This should be the internal canonical state representation used by the env implementation.

The Gymnasium observation returned to agents may still be the corresponding discrete tuple or NumPy array encoding of this state.

## Action set

Use a discrete action space of size `12`.

### Plate motion actions

These actions attempt to move the plate pose:

- `0`: move `x` by `+1`
- `1`: move `x` by `-1`
- `2`: move `y` by `+1`
- `3`: move `y` by `-1`
- `4`: rotate by `+1` quarter-turn
- `5`: rotate by `-1` quarter-turn

### Arm extension actions

These actions attempt to change arm states:

- `6`: increase `e1` by `1`
- `7`: decrease `e1` by `1`
- `8`: increase `e2` by `1`
- `9`: decrease `e2` by `1`
- `10`: increase `e3` by `1`
- `11`: decrease `e3` by `1`

All extension values are clipped to remain in `{0,1,2}`.

## Derived geometry needed for validity

To decide whether a state is valid, compute the world-space socket positions of the plate support points.

### Rotation rule

Let `R(theta_idx)` be the discrete rotation:

- `theta_idx = 0`: `(u, v) -> ( u,  v)`
- `theta_idx = 1`: `(u, v) -> (-v,  u)`
- `theta_idx = 2`: `(u, v) -> (-u, -v)`
- `theta_idx = 3`: `(u, v) -> ( v, -u)`

The implementation should provide a helper with exactly this behavior, for example:

```python
def rotate_local_point(theta_idx: int, point: tuple[int, int]) -> tuple[int, int]:
    ...
```

### World support sockets

If the plate center is `(x_idx, y_idx)`, the world position of socket `p` is:

```text
(x_idx, y_idx) + R(theta_idx)(p)
```

So each state determines three world-space support socket positions:

- `s_1`
- `s_2`
- `s_3`

corresponding to the left, middle, and right plate sockets.

## Validity rule

A state is valid if and only if **all** of the following hold.

### 1. Plate center is inside workspace

The center must satisfy:

- `0 <= x_idx <= 4`
- `0 <= y_idx <= 4`

This is already enforced by state bins, but it matters for transitions.

### 2. Plate support sockets remain inside an expanded reachable window

All support sockets must remain inside:

- `x in {0,1,2,3,4}`
- `y in {0,1,2,3,4}`

If a rotated plate would place a socket off-grid, the state is invalid.

This is intentionally stricter than checking the plate center alone.

The implementation must not silently weaken this to:

- center-only bounds
- partial socket bounds
- clamped socket positions

If any support socket is off-grid, the full state is invalid.

### 3. Reachability constraint for each engaged arm

Arm `i` is engaged if `e_i > 0`.

For each engaged arm:

- compute Manhattan distance

```text
d_i = |s_i.x - b_i.x| + |s_i.y - b_i.y|
```

- require:

```text
d_i <= e_i
```

So medium extension reaches distance `1`, and full extension reaches distance `2`.

If arm `i` is retracted (`e_i = 0`), it provides no support and has no reach requirement.

### 4. Minimum support count

At least **two** arms must be engaged:

```text
#{ i : e_i > 0 } >= 2
```

This is the simplest discrete “plate should not be floating on one support” rule.

### 5. Stability rule

Among engaged arms, the set of reached sockets must include at least one support on the left side and at least one on the right side of the plate’s local support set.

Operationally:

- arm `1` supports the left socket
- arm `2` supports the middle socket
- arm `3` supports the right socket

The state is stable if:

- arm `1` is engaged and reachable, and
- arm `3` is engaged and reachable

or:

- all three arms are engaged and reachable

So the simplest first stability rule is:

```text
(arm 1 reachable and arm 3 reachable)
or
(arms 1, 2, 3 all reachable)
```

This intentionally rules out “middle + one side only” as insufficient support.

### Summary validity predicate

A state is valid iff:

- plate center is in bounds
- all support sockets are in bounds
- every engaged arm reaches its assigned socket
- at least two arms are engaged
- the support pattern is stable under the left/right rule above

## Transition function

Each action proposes a candidate next state.

### Step rule

Given current state `s` and action `a`:

1. Copy the current state.
2. Apply the action’s local change:
   - plate translation
   - plate rotation
   - arm extension increment/decrement
3. Clip the changed coordinate if needed:
   - arm extensions clipped into `{0,1,2}`
4. For plate position and rotation:
   - if the proposed new `x_idx`, `y_idx`, or `theta_idx` falls outside legal discrete bins, the proposal is invalid
5. Evaluate the full validity predicate on the candidate next state.

### Valid move

If the candidate state is valid:

- next state becomes the candidate

### Invalid move

If the candidate state is invalid:

- next state remains the current state

So invalid moves are **self-loops with penalty**.

This is recommended for the first version because it:

- preserves a clean discrete transition system
- avoids introducing an absorbing failure state
- makes the hidden feasible graph explicit

## Start state

Use a fixed valid initial state:

```python
(2, 2, 0, 1, 1, 1)
```

Interpretation:

- plate centered in the middle of the workspace
- orientation `0`
- all three arms at medium extension

This should be valid under the rules above.

If later desired, a small set of valid starts can be sampled, but the first benchmark should use a fixed start for reproducibility.

## Goal state

Use a fixed target pose and support configuration:

```python
(1, 1, 1, 2, 2, 2)
```

Interpretation:

- plate translated into a different workspace region
- orientation `90` degrees
- all three supports fully extended

This gives a goal that requires both motion and support reconfiguration while remaining inside the feasible support envelope.

The exact target should be checked during implementation to ensure:

- it is valid
- it is not reachable trivially in one or two steps
- it requires at least one support-configuration change plus at least one pose change

The “not reachable trivially” requirement must be checked using the **actual primitive transition rule of this environment**, not a naive coordinate or Hamming-distance heuristic.

If this specific tuple fails those criteria, choose another fixed valid goal of the same type.

The implementation must perform this validation at env-construction time or in a dedicated unit test:

- goal state is valid
- goal state is not equal to start state
- goal state is not reachable in one primitive action from start state
- goal state requires at least one plate-pose change and at least one arm-configuration change relative to start state

## Reward function

Use a simple sparse-plus-step-cost reward.

### Per-step reward

If the action yields a valid non-goal transition:

- reward = `-1.0`

If the action is invalid and causes a self-loop:

- reward = `-3.0`

If the action reaches the goal state:

- reward = `+100.0`

### Why this reward is good for the first evaluation

It is:

- local to the one-step transition
- easy for flat RL to understand
- easy for `state_collapser` reward aggregation to descend over edge families
- simple enough that evaluation differences are not confounded by reward engineering

## Reward locality

Yes. This environment is intentionally designed to satisfy the repo’s reward-locality requirement.

The reward is computed entirely from the one-step transition event:

- current state `s`
- primitive action `a`
- resulting next state `s'`

More concretely:

- `+100.0` if `s'` is the goal state
- `-3.0` if the action is invalid and produces the self-loop `s' = s`
- `-1.0` otherwise

So the reward function is a local function of the primitive transition:

```text
R(s, a, s')
```

and therefore lies squarely inside the intended manageable class for `state_collapser`.

Path reward in this environment is just the accumulation of these local one-step rewards along a trajectory, which is exactly the locality regime the package is meant to handle.

## Episode termination

An episode terminates if either:

1. the goal state is reached, or
2. the step count reaches `max_steps`

Recommended:

```python
max_steps = 50
```

This is long enough for the task to require planning but short enough to preserve pressure toward efficient solutions.

## Success criterion

An episode is successful if the terminal state equals the goal state exactly:

```python
(x_idx, y_idx, theta_idx, e1, e2, e3) == goal_state
```

Recommended evaluation metrics:

- success rate over evaluation episodes
- average episodic return
- average episode length on successful episodes
- number of invalid-action self-loops per episode

## Exact Gymnasium API behavior

The first implementation should behave like a standard modern Gymnasium env.

### `reset()`

Recommended return shape:

```python
obs, info = env.reset(seed=seed, options=options)
```

with:

- `obs`: the encoded start observation
- `info`: a dictionary containing at least:
  - `"state"`: the internal `PlateSupportState`
  - `"goal_state"`: the internal goal `PlateSupportState`

### `step()`

Recommended return shape:

```python
obs, reward, terminated, truncated, info = env.step(action)
```

with:

- `obs`: encoded next observation
- `reward`: Python `float`
- `terminated`: `True` iff the goal state was reached
- `truncated`: `True` iff `max_steps` was reached without termination
- `info`: a dictionary containing at least:
  - `"state"`: resulting internal `PlateSupportState`
  - `"valid_transition"`: `bool`
  - `"invalid_move"`: `bool`
  - `"goal_reached"`: `bool`

### Observation encoding

Recommended first implementation:

- return a NumPy integer array of shape `(6,)`
- with entries:

```text
[x_idx, y_idx, theta_idx, e1, e2, e3]
```

- dtype:

```python
np.int64
```

This matches the declared `MultiDiscrete([5, 5, 4, 3, 3, 3])` observation space cleanly.

### Action handling

The env should accept:

- plain Python `int`
- NumPy integer scalar types accepted by Gymnasium

Invalid action indices outside `{0, ..., 11}` should raise the usual Gymnasium-style error rather than silently remapping.

## Transition edge cases

The first implementation should follow these exact rules:

### Arm extension updates

- apply the increment/decrement
- clip to `{0,1,2}`
- then validate the resulting full state

So arm actions never fail because of extension-range overflow alone; they only fail if the resulting full state is invalid.

If clipping yields the same extension value as before, that is still a legitimate candidate-state proposal.

So, for example:

- if `e1 = 2` and the action is “increase `e1`,”
- the clipped candidate still has `e1 = 2`
- that candidate must then be evaluated normally under the full validity predicate

If the resulting candidate state equals the current state and is valid, it is a **valid self-transition**, not automatically an invalid move.

### Plate translation / rotation updates

- propose the new plate coordinate or orientation
- do **not** clip position or orientation into some fallback pose
- if the proposed new state is outside the legal bins or fails the validity predicate, reject it and keep the current state

So plate-motion invalidity is handled by rejection/self-loop, not clipping.

This should be preserved exactly because it defines the hidden feasible transition graph.

## Rendering

Rendering is not required for the first functional evaluation environment, but a minimal human-readable render is recommended.

The first implementation may provide:

- `render_mode=None` by default
- optional `render_mode="ansi"`

For `ansi`, a simple text summary is enough, for example:

```text
PlateSupportState(x=2, y=3, theta=1, e=(2,1,2), valid=True)
```

No graphical renderer is required for the initial benchmark.

These metrics allow comparison between:

- flat `gymnasium` training
- quotient-tower-assisted training

## Why this environment is useful for package evaluation

This environment has all the properties needed for a first meaningful `state_collapser` evaluation:

- discrete state space
- explicit primitive actions
- hidden feasible graph cut out by constraints
- repeated local structural motifs
- nontrivial support reconfiguration
- local reward
- interpretable success condition

At the same time, it avoids unnecessary complexity:

- no continuous dynamics
- no force simulation
- no partial observability
- no high-dimensional observation encoder
- no difficult perception problem

So `PlateSupportEnv` is a strong first environment because it is simple enough to build quickly, but not so simple that quotient-tower machinery would be meaningless.

## First evaluation use

The intended first package-evaluation comparison is:

1. implement `PlateSupportEnv` as a discrete `gymnasium.Env`
2. train a flat baseline agent on it
3. train an otherwise comparable agent/runtime with `state_collapser` enabled
4. compare:
   - sample efficiency
   - success rate
   - convergence stability
   - invalid-move frequency

If `state_collapser` is doing something real, this environment is small enough that:

- debugging is possible
- state-graph inspection is possible
- quotient behavior can be visualized
- failure modes can be diagnosed

That makes it a good first evaluation environment before attempting more realistic constrained-robot cases.
