# Contributing

Thanks for contributing to `state_collapser`.

This repository is a pre-alpha Python package with a real implemented vertical slice, active mathematical/design documentation, and a strong expectation that code changes stay aligned with the project’s explicit design authority. This guide is meant to make contribution expectations clear for both ordinary package work and design-sensitive runtime work.

## Scope

Contributions are welcome in areas such as:

- bug fixes
- tests
- documentation
- packaging and release workflow
- example environments
- runtime and control improvements
- instrumentation and evaluation tooling
- downstream compatibility work for packages such as `HGraphML`

Because this package is still pre-alpha, many contributions will touch active design surfaces. In those cases, contributors are expected to check the relevant design documents before making structural changes.

## Current Project Roadmap

`state_collapser` is currently a research repo working toward a public GitHub
research-release posture first, then industrial-grade benchmarking and real
PyPI readiness later.

### Critical TODO

- ***System maturity:*** Deep tensor-backend hardening, large-scale training
  framework maturity, and full vectorized rollout semantics.
- ***Training surfaces:*** The first reusable training layer now has explicit
  action masks and continuation/bootstrap semantics. The next hardening stage
  is tensor/device, batch/sequence, vectorized rollout, and
  serialization/checkpoint integration.
- ***Runtime surfaces:*** The runtime now separates `LiveRuntimeView` from
  serializable `RuntimeSnapshot` values and keeps compatibility quotient
  readouts lazy. Future performance work should preserve that
  hot-path/readout separation.
- ***Fiber-conditioned training spine:*** After `FiberConditionedStage` is
  stable, revisit whether the proto exploit/explore `tower/control` stack should
  be refactored around it, preserved as a reference controller, or deprecated.
- ***Terminology cleanup:*** Plan a deliberate compatibility/deprecation pass
  for old `base` and `lower` vocabulary after new `total_state`, `fine_tier`,
  `coarse_tier`, and `frozen_quotient_behavior` surfaces are established.
- ***Benchmarking:*** We now have a basic package evaluation suite in
  [src/state_collapser/examples](./src/state_collapser/examples)
  and lightweight runtime benchmark smoke tooling in `state_collapser.benchmarks`.
  We still need serious benchmarking across larger coordination-constrained
  environments.
- ***Gymnasium bridge hardening:*** The package now has an explicit hook-based
  Gymnasium wrapper, but the harder observation-vs-state inference problem
  remains future work. Automatic inference is not required for the core package
  to be useful; serious integrations should provide explicit `state_key`,
  `action_key`, mask, and edge-label hooks.
- ***Package usability:*** Keep the public GitHub/source-install path honest and
  usable, then do the remaining work needed for a real PyPI release after
  serious benchmarking. The initial scoping for this work appears in
  [docs/design/PyPl_readiness](./docs/design/PyPl_readiness).
- ***Downstream compatibility:*** Treat `HGraphML` as the first real downstream
  package consuming `state_collapser` partition towers outside RL. Public
  release work should preserve its current first-import behavior or document a
  migration path.
- ***Research document hardening:*** Edit, proofread, and perfect
  [docs/design/logHRL.tex](./docs/design/logHRL.tex).

### Non-Critical TODO

- Design and implement visualization tools under
  [src/state_collapser/instrumentation](./src/state_collapser/instrumentation),
  including graph-tower and quotient-graph visualization tools under
  [src/state_collapser/instrumentation/tower_metrics](./src/state_collapser/instrumentation/tower_metrics).
- Design and implement a path-space metric suite. The current motivating
  sketch is in the draft Substack post
  [The Geometry of Reinforcement Learning](https://hackcraft.substack.com/p/80a781af-8526-4ac7-9462-243727ed1a27?postPreview=paid&updated=2026-05-04T17%3A07%3A17.101Z&audience=everyone&free_preview=false&freemail=true).

## Development Setup

The project uses:

- a `src/` layout
- `pyproject.toml`
- Python `3.11` or `3.12`

Recommended local workflow:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

If you are working on RL-facing or model-facing surfaces, install the relevant extras:

```bash
pip install -e ".[dev,rl,ml]"
```

If you use `uv`, the equivalent workflow is:

```bash
uv sync --extra dev
uv sync --extra dev --extra rl --extra ml
```

## Local Validation

Run these checks before opening a pull request:

```bash
.venv/bin/python -m pytest tests
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy src
```

If you are using `uv`, the equivalent commands are:

```bash
uv run pytest tests
uv run ruff check .
uv run mypy src
```

If your change touches a narrow subsystem, run the relevant focused tests first, but do not skip the full validation pass before proposing a merge.

## Repository Layout

Current important repository areas:

```text
src/state_collapser/
  adapters/
  benchmarks/
  contract/
  core/
  examples/
  graph/
  instrumentation/
  quotient/
  tower/
  training/

tests/
  adapters/
  benchmarks/
  contract/
  core/
  examples/
  graph/
  integration/
  quotient/
  tower/
  training/

docs/
  api_notes/
  code_review/
  design/
  engineer_continuity/
  outreach/
  prime_directive/
  usage/
```

High-level roles:

- `adapters/`
  - integration boundaries for Gymnasium and future external environment APIs
- `benchmarks/`
  - lightweight benchmark smoke tooling and hot-path comparison entry points
- `core/`
  - foundational contracts for states, actions, edges, labels, annotations, and rewards
- `graph/`
  - hidden, explored, vista, and local-star graph layers
- `contract/`
  - contraction-policy and selection surfaces
- `quotient/`
  - projections, cosets, and tier views
- `tower/`
  - partition-backed tower runtime, snapshots, trustworthiness, lazy quotient readouts, and exploit/explore control
- `training/`
  - reusable training-facing inputs, transitions, masks, collectors, learner hooks, reference loops, and fiber-conditioned stage surfaces
- `examples/`
  - reference environments and runtime/training integrations
- `instrumentation/`
  - metrics and future visualization / evaluation support

## Public API Expectations

Only names exported from:

- [src/state_collapser/__init__.py](./src/state_collapser/__init__.py)

should be treated as stable public API unless later documentation states otherwise.

Most of the repo is still evolving. Contributors should avoid assuming that all submodules are public just because they are importable.

## Contribution Workflow

The normal contribution flow is:

1. Branch from `main`.
2. Make a focused change.
3. Add or update tests in the same change.
4. Run local validation.
5. Update documentation when behavior, structure, or workflow changes.
6. Open a pull request or propose the merge.

Keep changes scoped. Avoid mixing unrelated refactors, doc rewrites, and runtime behavior changes unless they are part of one tightly coupled design move.

## Design Authority

This repository is more design-authoritative than many ordinary Python packages.

For implementation-sensitive work, contributors should consult the relevant documents under:

- [docs/design](./docs/design)

In particular, several design stacks now matter:

### Fiber-conditioned training spine

- [docs/design/RL_framework_maturity](./docs/design/RL_framework_maturity)
- [docs/usage](./docs/usage)
- [docs/api_notes](./docs/api_notes)

### First major implementation stack

- [docs/design/final_initial/final_initial_blueprint.md](./docs/design/final_initial/final_initial_blueprint.md)
- [docs/design/final_initial/final_initial_implementation_gameplan.md](./docs/design/final_initial/final_initial_implementation_gameplan.md)

### Exploit / explore control stack

- [docs/design/HRL_exploit-explore/01_013_exploit_explore_algorithm_blueprint.md](./docs/design/HRL_exploit-explore/01_013_exploit_explore_algorithm_blueprint.md)
- [docs/design/HRL_exploit-explore/01_014_exploit_explore_algorithm_implementation_gameplan.md](./docs/design/HRL_exploit-explore/01_014_exploit_explore_algorithm_implementation_gameplan.md)
- [docs/design/HRL_exploit-explore/01_015_abc_find_unclosed_correction.md](./docs/design/HRL_exploit-explore/01_015_abc_find_unclosed_correction.md)
- [docs/design/HRL_exploit-explore/01_016_find_lowest_unclosed_system_change_blueprint.md](./docs/design/HRL_exploit-explore/01_016_find_lowest_unclosed_system_change_blueprint.md)
- [docs/design/HRL_exploit-explore/01_017_find_lowest_unclosed_implementation_gameplan.md](./docs/design/HRL_exploit-explore/01_017_find_lowest_unclosed_implementation_gameplan.md)

### General package and mathematical context

- [docs/design/mathematical_model.pdf](./docs/design/mathematical_model.pdf)
- [docs/design/reward_locality_for_quotient_training.md](./docs/design/reward_locality_for_quotient_training.md)
- [docs/design/module_design_desiderata.md](./docs/design/module_design_desiderata.md)
- [docs/design/package_best_practices_proposal.md](./docs/design/package_best_practices_proposal.md)

### Downstream application context

- [docs/usage/01_009_downstream_applications.md](./docs/usage/01_009_downstream_applications.md)

If a contribution discovers tension between code and design documents, that tension should be surfaced explicitly. Do not silently resolve it by weakening semantics or changing behavior without documenting the move.

## Coding Expectations

Contributions should preserve the current package style:

- typed Python
- immutable data structures where the current design expects them
- explicit tests for runtime behavior
- conservative, inspectable control logic over cleverness

Contributors should not silently:

- weaken reward locality assumptions
- flatten quotient/tower semantics into decorative wrappers
- turn active-tier control into effective flat learning
- replace a real training path with a scripted placeholder
- treat instrumentation or evaluation helpers as substitutes for actual runtime behavior
- break known downstream HGraphML tower/fiber behavior without documenting the
  change and migration path

## Testing Expectations

When changing runtime behavior, add or update focused tests in the same area.

Current important testing areas include:

- package metadata and packaging smoke tests
- core immutability and hashing contracts
- hidden-graph legality and local neighborhood behavior
- explored / vista graph accumulation and propagation
- quotient projection and reward aggregation
- tower runtime snapshots and control behavior
- partition-tower state/action layer behavior
- reusable training surfaces and fiber-conditioned stage behavior
- example runtime/training paths
- benchmark CLI/import smoke behavior

If a change affects one of these surfaces, the corresponding tests should move with it.

## Example Environment Contributions

Example environments are now a real part of the package, not just placeholders.

Current example structure includes:

- [src/state_collapser/examples/robot_constraint_toy.py](./src/state_collapser/examples/robot_constraint_toy.py)
- [src/state_collapser/examples/plate_support_env](./src/state_collapser/examples/plate_support_env)
- [src/state_collapser/examples/rl_counterpoint_v3](./src/state_collapser/examples/rl_counterpoint_v3)
- [src/state_collapser/examples/articulated_loop_env](./src/state_collapser/examples/articulated_loop_env)
- [src/state_collapser/examples/cable_parallel_env](./src/state_collapser/examples/cable_parallel_env)
- [src/state_collapser/examples/dual_arm_manipulation_env](./src/state_collapser/examples/dual_arm_manipulation_env)
- [src/state_collapser/examples/parallelogram_singularity_env](./src/state_collapser/examples/parallelogram_singularity_env)

When adding a new serious example environment:

- prefer an example subpackage if the env is expected to grow beyond one file
- include env-specific tests
- document the environment under:
  - [docs/design/test_design](./docs/design/test_design)
- preserve reward locality if the environment is meant to exercise the current quotient/tower training assumptions

New evaluation environments should also be consistent with:

- [docs/design/test_design/evaluation_strategy.md](./docs/design/test_design/evaluation_strategy.md)

## Instrumentation And Evaluation Tooling

The repository now has an explicit home for instrumentation work:

- [src/state_collapser/instrumentation/pathspace_metrics](./src/state_collapser/instrumentation/pathspace_metrics)
- [src/state_collapser/instrumentation/tower_metrics](./src/state_collapser/instrumentation/tower_metrics)

Contributors adding metrics, path-space analysis, or training-run visualization should prefer these namespaces over scattering such code across examples or core runtime modules.

## Compatibility Targets

Current compatibility commitments are:

- `gymnasium` as the primary RL environment API target
- `torch` as the primary ML backend target
- `ROS 2` as the intended robotics integration boundary

Contributions should preserve that layering.

In particular:

- do not make robot-specific infrastructure part of the conceptual core
- do not collapse the RL environment boundary into the robotics boundary
- prefer adapters over hard-coded backend assumptions

## Gymnasium Integration Guidance

Gymnasium environments provide the interaction shell: `reset`, `step`, action
spaces, observation spaces, rewards, and episode flags. They do not, by
themselves, solve the package-specific question of what counts as a stable
state identity in the discovered graph.

When contributing a Gymnasium integration, prefer the hook-based wrapper in
`state_collapser.adapters.gymnasium` and provide explicit hooks for:

- `state_key`, especially when observations are arrays, partial observations,
  histories, or otherwise not already stable graph-state identities
- `action_key`, so primitive actions become stable package action identities
- action masks, either through Gymnasium `info["action_mask"]` or through the
  wrapper hook
- transition labels, since labels are what contraction schemas use to build
  quotient towers

Do not add automatic observation-to-state inference unless that inference is the
explicit subject of the contribution. For now, automatic inference is future
work; explicit hooks are the professional boundary.

## Benchmark And Hot-Path Discipline

Correctness tests are necessary, but they are not enough for runtime claims in
this package. Changes to tower construction, partition updates, compatibility
readouts, or training collection should preserve the hot-path distinction
between maintaining the partition tower and materializing compatibility
`QuotientTierView` readouts.

When changing runtime-sensitive code:

- avoid hidden calls to `to_quotient_tier_views()` in default step/update paths
- keep compatibility readouts behind explicit APIs such as
  `compatibility_quotient_tiers()`
- benchmark both readout-disabled and readout-enabled modes when performance is
  part of the claim
- avoid unit tests that assert brittle wall-clock thresholds
- prefer benchmark tests that assert importability, CLI shape, flags, and
  structured result fields

After runtime hot-path changes, run at least:

```bash
uv run pytest tests/benchmarks
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
```

## Documentation Expectations

If a contribution changes any of the following, update docs in the same change:

- user-facing install or usage workflow
- public API expectations
- example package structure
- release/version workflow
- authoritative design assumptions

At minimum, contributors should consider whether the change requires updates to:

- [README.md](./README.md)
- [docs/package_usage.md](./docs/package_usage.md)
- [docs/public_api.md](./docs/public_api.md)
- env-specific design docs
- relevant design blueprints or gameplans

## Release And Versioning

Releases are tag-driven.

Typical release work includes:

- updating version metadata in:
  - [pyproject.toml](./pyproject.toml)
  - [src/state_collapser/_version.py](./src/state_collapser/_version.py)
- ensuring CI is green
- creating a git tag such as:
  - `vX.Y.Z`
- pushing the tag to GitHub
- creating the release in GitHub

Do not create a release tag that disagrees with package version metadata.

## Current Reality

This repository now contains:

- a real partition-backed quotient/tower runtime with persistent state/action partition layers
- lazy compatibility readouts for older quotient-tier consumers
- a concrete constrained flagship environment in `plate_support_env`
- a migrated `rl_counterpoint_v3` example package
- a first-wave evaluation family for hidden constraint geometry
- runnable tower-aware training paths across current example packages
- a first exploit/explore active-tier control implementation
- a reusable internal `state_collapser.training` package
- a first `FrozenQuotientBehavior -> PathFiber -> FiberConditionedStage` bridge
- lightweight benchmark smoke tooling for hot-path/readout comparisons

So contributions should treat the repository as a real package with live runtime semantics, not just as a design notebook.

## License

By contributing, you agree that your contributions are made under the project’s [MIT License](./LICENSE).
