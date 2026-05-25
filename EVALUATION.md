# Evaluating `state_collapser`

`state_collapser` is a research-oriented Python package. The present document explains what evaluation means in this package, which example environments are currently authoritative, how to run the current evaluation tools, and how to interpret the resulting signals responsibly. This file is for:

- package users who want to understand how to assess `state_collapser`
- contributors who want to add new evaluation environments or benchmarks
- researchers who want to reproduce or extend the repo’s current evidence

**Status:** The current evaluation surface is real, runnable, and increasingly structured, but it is still `pre-alpha`.
- **Currently in place:**
  - multiple discrete example environments under [src/state_collapser/examples](./src/state_collapser/examples)
  - runnable tower-aware training entrypoints
  - a first exploit/explore training path for `PlateSupportEnv`
  - focused tests for each example environment
  - a CLI tower-depth probe utility for inspecting dynamic tower growth
  - lightweight runtime benchmark smoke tooling for hot-path/readout checks
- **Not yet in place:**
  - a polished benchmark harness with persistent artifacts and standardized result tables
  - broad empirical claims across many seeds and many budgets
  - a finalized public benchmarking API
  - complete visualization and instrumentation support

## Evaluation Philosophy
Evaluation in the `state_collapser` repo has two distinct jobs:

1. Determine whether an environment is actually a good `state_collapser` testbed.
2. Determine whether the package’s tower apparatus helps on that environment in a way that justifies its added structure.

### Core Evaluation Questions

Every serious evaluation effort in this repo that is focussed on a specific evaluation environment should first ask:

> **Question 1**. *Is this a good `state_collapser` environment?*
  
This means asking:

  >> **Question 1.1.**  *Does the environment contain hidden or non-canonical structure rather than an obvious ready-made task hierarchy?*</br>
  **Question 1.2.**  *Does it preserve the reward-locality assumptions that current tower construction and quotient training depend on?*</br>
  **Question 1.3.**  *Is it discrete and inspectable enough for the current package surfaces?*</br>
  **Question 1.4.**  *Is it small enough to reason about, but rich enough that tower structure could matter?*

Once the evaluation has decided that the specific environment is a serious
testbed for the package, it should next ask:

> **Question 2.**  *Does `state_collapser` actually help here?*

This means asking:

  >> **Question 2.1.** *Compared to what baseline?*</br>
  **Question 2.2.** *Under what training budget?*</br>
  **Question 2.3.** *Using what evidence besides raw reward?*</br>
  **Question 2.4.** *By what sign do we know the hierarchy is actually being used?*

### Canonical Comparison Structure

Where possible, the same underlying RL problem should be evaluated in three modes:
- `Flat`: train directly on the base environment
- `Top-tier-only`: train with only the uppermost abstraction or tower surface
- `Full tower`: train with the full tower machinery

Taken together, these three modes isolate baseline performance, abstraction-only performance, and full hierarchical-control performance. We deploy the following comparison structures:

1. **Primary comparison structure: `Flat` vs `Full tower`.**</br>
    This asks whether the full `state_collapser` apparatus is worth its overhead. If the tower path cannot beat or justify itself against direct training on the same problem, then extra hierarchy bookkeeping is not enough on its own.

2. **Secondary comparison structure: `Top-tier-only` vs `Full tower`.**</br>
    This asks whether the multi-tier story matters beyond merely introducing one abstraction layer. If only a single top tier is doing the useful work, then the rest of the tower may be dead weight.

3. **Auxiliary comparison structure: `Flat` vs `Top-tier-only`.**</br>
    This asks whether abstraction helps at all.

### Evaluation Layers

The repo’s methodology separates evaluation into three layers.

1. **Structural Evaluation**</br>
    Asks whether the environment is a faithful test of the package’s intended problem class:

    >> **Question 3.1.** *What hidden constraint geometry does the environment represent?*</br>
    **Question 3.2.** *What makes the flat ambient parameterization misleading or weak?*</br>
    **Question 3.3.** *What quotientable or collapsible regularity should plausibly exist?*

2. **Behavioral Evaluation**</br>

    Behavioral evaluation asks about tower-depth probes, active-tier traces, and structural diagnostics:

    >> **Question 4.1.** Does the tower actually build nontrivial structure?</br>
    **Question 4.2.** Do tiers materialize and evolve differently over time?</br>
    **Question 4.3.** Does control move through the tower in a meaningful way?</br>
    **Question 4.4.** Does the runtime look like it is using hierarchy rather than merely carrying it?

3. **Performance Evaluation**</br>
    Performance evaluation asks for the usual empirical metrics:

    >> **Metric 5.1.** Sample efficiency</br>
    **Metric 5.2.** Success rate</br>
    **Metric 5.3.** Cumulative reward</br>
    **Metric 5.4.** Variance across seeds</br>
    **Metric 5.5.** ***Eventually**, path-space or tower-growth metrics once the instrumentation suite matures.*

## Current Authoritative Example Environments

The current evaluation environments live under [src/state_collapser/examples](./src/state_collapser/examples).

### Primary existing reference environment

- [plate_support_env](./src/state_collapser/examples/plate_support_env)

This is currently the most developed environment package. It includes:

- the base environment
- a tower runtime integration
- a tower-aware training path
- a first exploit/explore training path

It remains the strongest existing reference environment for package behavior.

### First-wave additional evaluation family

- [articulated_loop_env](./src/state_collapser/examples/articulated_loop_env)
- [dual_arm_manipulation_env](./src/state_collapser/examples/dual_arm_manipulation_env)
- [cable_parallel_env](./src/state_collapser/examples/cable_parallel_env)
- [parallelogram_singularity_env](./src/state_collapser/examples/parallelogram_singularity_env)

These environments are intended to broaden the evaluation family across different kinds of hidden constraint geometry:

- loop-closure hidden geometry
- shared-object coordination geometry
- cable-support coupling geometry
- singular or near-singular local feasible-geometry changes

They are real, tested packages, but they are newer than `plate_support_env` and should be treated accordingly.

### Older toy vertical slice

- [robot_constraint_toy.py](./src/state_collapser/examples/robot_constraint_toy.py)

This remains useful as a small integration slice, but it should not be mistaken for the repo’s main evaluation surface.

## Current Runnable Evaluation Entry Points

### 1. Tower-aware training

Most example packages expose a `run_tower_training(...)` surface in their `training.py`.

For example, on `PlateSupportEnv`:

```python
from state_collapser.examples.plate_support_env import (
    PlateSupportEnv,
    TowerTrainingConfig,
    run_tower_training,
)

result = run_tower_training(
    env=PlateSupportEnv(),
    config=TowerTrainingConfig(
        episodes=20,
        max_steps_per_episode=50,
        alpha=0.5,
        gamma=0.95,
        epsilon=0.2,
        seed=0,
    ),
)
```

Analogous `run_tower_training(...)` entry points exist for the newer example packages.

### 2. Exploit/explore training

Right now, the exploit/explore reference path is most developed on `PlateSupportEnv`:

```python
from state_collapser.examples.plate_support_env import (
    ExploitExploreTrainingConfig,
    PlateSupportEnv,
    run_exploit_explore_training,
)

result = run_exploit_explore_training(
    env=PlateSupportEnv(),
    config=ExploitExploreTrainingConfig(
        episodes=10,
        max_control_steps_per_episode=20,
        alpha=0.5,
        gamma=0.95,
        seed=0,
    ),
)
```

This is the right entry point for evaluating the current `Always Be Closing` exploit/explore control story on the most mature example.

### 3. Tower-depth probing

The repository now includes a CLI utility for probing dynamic tower depth:

- [tower_depth_probe.py](./src/state_collapser/examples/tower_depth_probe.py)

Run it with:

```bash
.venv/bin/python -m state_collapser.examples.tower_depth_probe
```

Examples:

Run only two environments:

```bash
.venv/bin/python -m state_collapser.examples.tower_depth_probe \
  plate_support_env articulated_loop_env
```

Show only summary depth:

```bash
.venv/bin/python -m state_collapser.examples.tower_depth_probe \
  plate_support_env articulated_loop_env \
  --summary-only
```

Increase the probe horizon:

```bash
.venv/bin/python -m state_collapser.examples.tower_depth_probe \
  plate_support_env \
  --steps 200
```

Change contraction sample size:

```bash
.venv/bin/python -m state_collapser.examples.tower_depth_probe \
  plate_support_env \
  --sample-size 2
```

The sample-size option affects the legacy annotation/local-star contraction
policy. In the current partition-backed runtime, the main partition contraction
schedule is controlled by schema mode.

Use the default environment schemas:

```bash
.venv/bin/python -m state_collapser.examples.tower_depth_probe \
  plate_support_env \
  --schema-mode default
```

Probe an explicit flat schema baseline:

```bash
.venv/bin/python -m state_collapser.examples.tower_depth_probe \
  plate_support_env \
  --schema-mode none
```

Probe without the legacy annotation/local-star contraction policy:

```bash
.venv/bin/python -m state_collapser.examples.tower_depth_probe \
  plate_support_env \
  --no-contraction-policy
```

This does not disable partition schema scheduling. Use `--schema-mode none` when
the point is to compare against a flat partition-tower baseline.

Keep one uninterrupted trace without resetting on terminal or truncation:

```bash
.venv/bin/python -m state_collapser.examples.tower_depth_probe \
  plate_support_env \
  --no-reset-on-terminal
```

In full-output mode, the current probe prints:

- `schema_mode`
- `depth_curve`
- `max_depth`
- `scheduled_assignments`
- `unscheduled_assignments`
- `reset_events`

In `--summary-only` mode, it prints:

- `max_depth`
- `scheduled_assignments`
- `unscheduled_assignments`

This is a structural and behavioral diagnostic, not yet a benchmark score.

## Recommended Evaluation Workflow

For a serious new evaluation pass, the recommended order is:

1. Confirm the environment is structurally appropriate.
2. Run a tower-depth probe to see whether nontrivial tower materialization occurs at all.
3. Run tower-aware training on the same environment.
4. Where applicable, run exploit/explore control.
5. Compare against flat and top-tier-only baselines when those surfaces exist.
6. Repeat across multiple seeds before making empirical claims.

In practice, that means:

### Step 1 — Structural sanity

Inspect:

- the state definition
- the primitive action set
- the validity rule
- the hidden feasible-graph interpretation

If the environment is basically an unconstrained lattice with a decorative filter, it is not yet a good evaluation environment.

### Step 2 — Tower-growth sanity

Run the tower-depth probe first.

This tells you:

- whether the tower stays trivial
- whether nontrivial recursive contraction appears
- whether results are highly sensitive to the contraction policy or probe settings

### Step 3 — Training pass

Run the environment’s `run_tower_training(...)` entry point.

At this stage, treat the result as:

- a smoke or early empirical signal

not as a finished benchmark claim.

### Step 4 — Control-specific pass

If the environment supports it, run the exploit/explore path and inspect:

- success
- control traces
- active-tier behavior
- whether the runtime appears to use the hierarchy meaningfully

## How To Interpret Tower Depth

Tower depth is useful, but it is easy to overread.

### What tower depth can tell you

- whether recursive contraction is doing nontrivial work
- whether an environment admits deep quotient-style structure under the current contraction policy
- whether a change in contraction semantics materially affects tower materialization

### What tower depth does not tell you by itself

- whether learning is better
- whether exploit/explore control is better
- whether the hierarchy is semantically meaningful for policy improvement

Depth is a behavioral signal, not a complete empirical score.

High depth can still correspond to:

- poor learning
- unstable control
- or artificial contraction behavior

So depth should be interpreted alongside:

- reward trajectories
- success rates
- active-tier traces
- and qualitative understanding of the environment geometry

## What Makes A Good Evaluation Environment In This Repo

The current rule of thumb is that a strong `state_collapser` environment should be:

- discrete
- inspectable
- reward-locality-compatible
- structurally constrained
- not already handed a clean subtask decomposition

Good environment families typically involve:

- hidden support constraints
- coordination constraints
- constrained loop geometry
- singular or bottleneck-like feasible regions

Environments that are less useful include:

- trivial flat lattices
- problems with obvious built-in hierarchical task structure
- large simulator-like systems that exceed the current package’s inspectability and runtime assumptions

## Reproducibility Expectations

When reporting evaluation results, it helps to record:

- exact environment name
- exact training or probe command
- seed
- contraction-policy settings
- number of steps or episodes
- any reset policy used in the probe
- whether the result is structural, behavioral, or performance-oriented

For now, a good minimum standard is:

- fixed seed
- explicit command
- explicit environment
- explicit note of whether contraction policy was enabled

## Current Limitations

The current evaluation surface is still limited in several ways:

- flat vs top-tier-only vs full-tower benchmarking is not yet fully standardized across all environments
- exploit/explore evaluation is still most mature only on `PlateSupportEnv`
- tower-depth probing exists, but richer instrumentation and visualization are still under active development
- the repo does not yet ship a full artifact-writing benchmark harness with plots, CSV outputs, or standardized reports

So the current evaluation suite should be read as:

- real
- useful
- increasingly principled

but not yet as a finished benchmark platform.

## Related Documentation

Package-facing docs:

- [README.md](./README.md)
- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [CHANGELOG.md](./CHANGELOG.md)

Evaluation and example design docs:

- [docs/design/test_design/evaluation_strategy.md](./docs/design/test_design/evaluation_strategy.md)
- [docs/design/test_design/example_family_blueprint_from_mathematical_model_list.md](./docs/design/test_design/example_family_blueprint_from_mathematical_model_list.md)
- [docs/design/test_design/example_family_implementation_gameplan.md](./docs/design/test_design/example_family_implementation_gameplan.md)

Current example-family implementation trail:

- [docs/design/test_design/example_family_implementation_log.md](./docs/design/test_design/example_family_implementation_log.md)
- [docs/design/test_design/rl_counterpoint_v3](./docs/design/test_design/rl_counterpoint_v3)
- [docs/design/test_design/post_young_audit](./docs/design/test_design/post_young_audit)

## Future Work

The next major evaluation improvements likely include:

- a standardized benchmark harness
- persistent output artifacts for runs
- stronger top-tier-only comparison surfaces
- tower and path-space instrumentation
- visualization tools under [src/state_collapser/instrumentation](./src/state_collapser/instrumentation)
- documented reproducible benchmark bundles for the most important example environments

That work will build on the evaluation foundations described here rather than replace them.
