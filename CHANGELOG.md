# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project aims to follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.7.0] - 2026-05-29

### Added

- Added the first tensorization boundary under `state_collapser.training`,
  including backend-independent linearization records, benchmark-mode config,
  and benchmark-visible reports.
- Added `EncodingRegistry` for stable numeric ids over states, edges, actions,
  state cells, action cells, action collections, tower tiers, stage ids, fiber
  ids, frozen behavior ids, departure reasons, and labels.
- Added optional Torch conversion under `state_collapser.training.torch`,
  including `TorchDecisionBatch`, `TorchTransitionBatch`, and
  `action_decision_from_logits`.
- Added tensorization usage documentation and design records under:
  - `docs/usage/01_010_tensorization_boundary.md`
  - `docs/design/tensorization/`
- Added a HGraphML tensorization-follow-up bridge documenting how downstream
  graph-ML compatibility should use shared tower encoding without depending on
  RL-specific training records or Torch.

### Changed

- Bumped package metadata and runtime version to `0.7.0`.
- Clarified that tensorization is an explicit learner, adapter, or benchmark
  boundary rather than a replacement for the object-native runtime.
- Preserved the position that `state_collapser` is not a full RL framework:
  PPO/DQN/SAC, replay buffers, vectorized rollout, checkpoint/resume, and
  experiment manifests remain outside the first tensorization release.

### Validation

- Static validation passed during release preparation:
  - `ruff check .`
  - `mypy src`
- Regression and tensorization validation passed during release preparation:
  - full pytest suite with coverage
  - tensorization-focused training tests
  - optional Torch smoke tests when the `ml` extra is installed
- Package build validation passed during release preparation:
  - `python -m build`

## [0.6.0] - 2026-05-25

### Added

- Added the fiber-conditioned training-spine surface after the `v0.5.0` tag,
  including `FrozenQuotientBehavior`, `PathFiber`, and `FiberConditionedStage`
  documentation and tests.
- Added engineer-facing usage and API notes under:
  - `docs/usage/`
  - `docs/api_notes/`
- Documented `HGraphML` as the first downstream graph-ML application consuming
  `state_collapser` partition towers outside the original RL setting.
- Added an HGraphML-shaped partition-tower compatibility test so downstream
  node-fiber and edge-fiber readout behavior is protected inside the upstream
  test suite.
- Added synthetic-review revision work and associated design/implementation
  records under:
  - `docs/design/synthetic_blow_revisions_01/`
- Moved the project outreach brief into the repository so continuity records no
  longer refer only to an out-of-repo Desktop artifact.

### Changed

- Reframed the release target as a lightweight public GitHub research release
  rather than a PyPI release.
- Made PyPI publishing manual-only while benchmarking remains the release
  blocker for registry publication.
- Updated package metadata to `0.6.0`, canonical GitHub URLs, a broader
  quotient-tower description, a changelog URL, `Typing :: Typed`, and the
  currently validated Python `3.11`/`3.12` version range.
- Updated README installation guidance so source installs and public Git tags
  are the advertised current paths.

### Fixed

- Removed absolute local user-home and private temporary-directory path leakage
  from the scanned root/docs text corpus.
- Preserved the full research/provenance documentation corpus while replacing
  machine-local paths with relative links or neutral repository-root
  placeholders.

### Validation

- Full regression suite passed:
  - `467 passed`
- Static validation passed:
  - `ruff check .`
  - `mypy src`
- Package build and metadata validation passed:
  - `state_collapser-0.6.0.tar.gz`
  - `state_collapser-0.6.0-py3-none-any.whl`
  - `twine check`

## [0.5.0] - 2026-05-24

### Added

- Partition-backed tower runtime package under:
  - `src/state_collapser/tower/partition/`
- Young-tableaux / nested-partition runtime surfaces for:
  - stable state and action identifiers
  - base graph registration
  - state partition layers
  - action partition layers
  - contraction schemas
  - loop handling
  - lazy compatibility readouts
  - reward and internal-edge aggregation
  - incremental update diagnostics
- Lightweight runtime benchmark smoke tooling under:
  - `src/state_collapser/benchmarks/`
- Benchmark smoke tests under:
  - `tests/benchmarks/`
- Post-Young-diagram evaluation-environment audit, repair blueprint,
  implementation gameplan, and implementation log under:
  - `docs/design/test_design/post_young_audit/`
- Synthetic Blow review kit materials under:
  - `docs/code_review/synthetic_blow_review_kit/`
- Young-tableaux refactor design, gameplan, and implementation log under:
  - `docs/design/Young_tableaux_refactor/`

### Changed

- Reworked tower construction around persistent state/action partition tables
  rather than repeated global quotient reconstruction.
- Preserved compatibility with legacy `QuotientTierView` consumers through lazy
  readout APIs instead of hot-path materialization.
- Updated runtime snapshots so partition-backed tower behavior remains visible
  to existing tower-aware example integrations.
- Repaired the post-Young-diagram evaluation environments so example schemas
  drive meaningful partition-tower contraction behavior.
- Updated reward aggregation support so quotient/direct-image behavior is not
  hard-coded to average-only aggregation.

### Fixed

- Fixed CI typing failures present during the `v0.5.0` release-preparation pass.
- Fixed evaluation-environment schema drift introduced by the Young-tableaux
  runtime refactor.
- Fixed benchmark/test package layout issues so benchmark smoke tests are part
  of the ordinary test surface.

### Validation

- Full regression suite passed during release preparation.
- Static validation passed during release preparation:
  - `ruff check .`
  - `mypy src`
- Focused runtime, partition, benchmark, and example-environment tests passed
  during the Young-tableaux and post-Young repair implementation passes.

## [0.4.0] - 2026-05-20

### Added

- First wave of additional evaluation/example packages under:
  - `src/state_collapser/examples/articulated_loop_env/`
  - `src/state_collapser/examples/cable_parallel_env/`
  - `src/state_collapser/examples/dual_arm_manipulation_env/`
  - `src/state_collapser/examples/parallelogram_singularity_env/`
- Rebuilt counterpoint evaluation package:
  - `src/state_collapser/examples/rl_counterpoint_v3/`
- Reusable tower-depth probe utility:
  - `src/state_collapser/examples/tower_depth_probe.py`
- Root-level evaluation guide:
  - `EVALUATION.md`
- First internal reusable training-surface package under:
  - `src/state_collapser/training/`
- Model/training-surface design and implementation records:
  - `docs/design/model_train_surfaces/01_001_model_and_training_surface_architecture.md`
  - `docs/design/model_train_surfaces/01_002_model_and_training_surface_blueprint.md`
  - `docs/design/model_train_surfaces/01_003_model_and_training_surface_implementation_gameplan.md`
  - `docs/design/model_train_surfaces/01_004_model_and_training_surface_implementation_log.md`
- Python-package-readiness scoping document:
  - `docs/design/PyPl_readiness/01_001_python_package_readiness_scoping.md`
- Git-discipline note:
  - `docs/prime_directive/git_practices.md`

### Changed

- Expanded the repository from a single flagship evaluation example toward a broader constrained-evaluation family.
- Reframed the README’s old policy-only model TODO into a broader model/training-surface architecture story.
- Updated `README.md` so it now reflects:
  - `state_collapser.training`
  - `rl_counterpoint_v3`
  - the new example family
  - the tower-depth probe workflow
- Migrated `rl_counterpoint_v3` tower training to use the new reusable training surfaces rather than owning the full tabular loop locally.

### Fixed

- Fixed the first articulated-loop example design so feasible motion is supported by explicit closure-slack / mismatch-budget semantics rather than by freezing the graph or introducing pre-coupled actions.
- Fixed the tower-depth probe typing surface so `mypy` accepts the shared runtime protocol.
- Fixed README drift relative to the current package surface and example inventory.

### Validation

- Full regression suite passed:
  - `251 passed`
- Static validation passed:
  - `ruff check .`
  - `mypy src`
- Focused training-surface slice passed:
  - `tests/training`
  - migrated `rl_counterpoint_v3` training tests

## [0.3.0] - 2026-05-17

### Added

- Package-owned dynamic tower construction under:
  - `src/state_collapser/tower/construction.py`
- Package-owned tower-construction queries and diagnostics for:
  - tierwise contraction records
  - tower stopping reasons
  - deeper runtime inspection of dynamically constructed tiers
- New design and implementation records for the tower-construction correction:
  - `docs/design/HRL_exploit-explore/01_018_tower_construction_ownership_misalignment_diagnosis.md`
  - `docs/design/HRL_exploit-explore/01_019_package_owned_tower_construction_correction.md`
  - `docs/design/HRL_exploit-explore/01_020_package_owned_dynamic_tower_construction_blueprint.md`
  - `docs/design/HRL_exploit-explore/01_021_package_owned_dynamic_tower_construction_implementation_gameplan.md`
  - `docs/design/HRL_exploit-explore/01_021_package_owned_dynamic_tower_construction_implementation_log.md`
  - `docs/design/HRL_exploit-explore/01_022_tierwise_remaining_edge_contraction_blueprint.md`
  - `docs/design/HRL_exploit-explore/01_023_tierwise_remaining_edge_contraction_implementation_gameplan.md`
  - `docs/design/HRL_exploit-explore/01_023_tierwise_remaining_edge_contraction_implementation_log.md`

### Changed

- Re-centered dynamic tower construction as a package-owned operation rather than an example-owned one.
- Reworked `TowerRuntime` so explored-graph growth, vista refresh, quotient-tier creation, and tower query support are coordinated under package authority.
- Removed primary example-owned quotient-tier construction from:
  - `src/state_collapser/examples/plate_support_env/runtime.py`
  - `src/state_collapser/examples/robot_constraint_toy.py`
  - `src/state_collapser/adapters/gymnasium.py`
- Corrected contraction semantics so deeper contraction is chosen tierwise from the still-nontrivial remainder rather than from one fixed family selected once on `G_t^0`.
- Adopted the first reference tierwise contraction-budget rule:
  - approximately `20%` of the eligible nontrivial remainder per tier
- Updated exploit/explore runtime synchronization so active-tier control remains valid as tower depth changes across runtime rebuilds.

### Fixed

- Fixed the architectural ownership leak where example and adapter code were defining tier semantics directly.
- Fixed the shallow-tower failure mode in `PlateSupportEnv` where one selected edge family became trivial after a single collapse and prevented deeper tower growth.
- Fixed a downstream exploit/explore runtime bug where deeper package-built towers could leave the active control tier pointing past the rebuilt tower depth.

### Validation

- Full regression suite passed:
  - `182 passed`
- Static validation passed:
  - `ruff check .`
  - `mypy src`
- Live `PlateSupportEnv` exploit/explore runs no longer remained capped at two tiers under the corrected contraction semantics.

## [0.2.1] - 2026-05-17

### Changed

- Corrected the first exploit/explore controller so it more faithfully implements:
  - `ABC = Always Be Closing`
- Replaced confidence-gated descent with a `find lowest unclosed` control picture driven by tier-level productive-learning signals.
- Reinterpreted lift as a response to productive-learning exhaustion at the current tier rather than as a generic need for finer correction.

### Fixed

- Fixed the runtime behavior where the exploit/explore controller could remain pinned at active tier `0` in direct `PlateSupportEnv` runs.
- Removed pathological dependence on overly fine state-local maturity buckets for tier movement.

### Added

- Focused control tests for the corrected polarity:
  - `tests/tower/control/test_lowest_unclosed_selection.py`
  - `tests/tower/control/test_lift_on_productive_exhaustion.py`
- New exploit/explore correction documents:
  - `docs/design/HRL_exploit-explore/01_015_abc_find_unclosed_correction.md`
  - `docs/design/HRL_exploit-explore/01_016_find_lowest_unclosed_system_change_blueprint.md`
  - `docs/design/HRL_exploit-explore/01_017_find_lowest_unclosed_implementation_gameplan.md`
  - `docs/design/HRL_exploit-explore/01_017_find_lowest_unclosed_implementation_log.md`

### Validation

- Full regression suite passed:
  - `178 passed`
- Static validation passed:
  - `ruff check .`
  - `mypy src`
- Direct exploit/explore `PlateSupportEnv` runs no longer remained pinned at tier `0`.

## [0.2.0] - 2026-05-16

### Added

- The first exploit/explore controller implementation under:
  - `src/state_collapser/tower/control/`
- Active-tier control surfaces for:
  - active-tier state
  - per-tier config
  - signal state
  - frozen lower-tier context
  - learner and executor contracts
  - metrics
  - runtime-loop control
- `ExploitExploreTowerRuntime` in the tower runtime surface.
- `PlateSupportEnv` exploit/explore integration, including:
  - `PlateSupportExploitExploreRuntime`
  - `PlateSupportLiftResolveExecutor`
  - `PlateSupportTierLearner`
  - `run_exploit_explore_training(...)`
- Exploit/explore scholarship, blueprint, and implementation docs under:
  - `docs/design/HRL_exploit-explore/`
- Initial instrumentation namespace structure under:
  - `src/state_collapser/instrumentation/pathspace_metrics/`
  - `src/state_collapser/instrumentation/tower_metrics/`

### Changed

- Clarified the repository’s HRL direction around:
  - `ABC = Always Be Closing`
  - single active control tier semantics
  - coarse-to-fine training control rather than effective parallel all-tier learning
- Updated `README.md` and `CONTRIBUTING.md` to more accurately reflect the package’s implemented surfaces and design authority structure.

### Validation

- Full regression suite passed during the implementation interval:
  - `171 passed`
- Static validation passed:
  - `ruff check .`
  - `mypy src`

## [0.1.0] - 2026-05-13

### Added

- The first distributable package surface under `src/state_collapser`, including:
  - `core`
  - `graph`
  - `contract`
  - `quotient`
  - `tower`
  - `examples`
  - `adapters`
- Core graph/runtime implementation for:
  - hidden graph
  - explored graph
  - vista graph
  - local star
  - quotient projection
  - cosets
  - nested tier views
  - runtime snapshots
  - `TowerRuntime`
- First contraction-policy surfaces:
  - label-based contraction
  - seeded-random contraction
- First example surfaces:
  - `robot_constraint_toy`
  - `plate_support_env`
- First Gymnasium-facing adapter surface.
- First runnable `PlateSupportEnv` tower-training path via:
  - `run_tower_training(...)`
- Initial design-to-implementation artifacts:
  - `docs/design/final_initial/final_initial_blueprint.md`
  - `docs/design/final_initial/final_initial_implementation_gameplan.md`
  - `docs/design/final_initial/implementation_running_log.md`
  - `docs/design/test_design/env_001/plate_support_env_spec.md`
  - `docs/design/test_design/env_001/plate_support_env_implementation_gameplan.md`
  - `docs/design/test_design/env_001/plate_support_env_implementation_log.md`
  - `docs/design/test_design/env_001/plate_support_env_tower_training_integration_gameplan.md`
  - `docs/design/test_design/env_001/plate_support_env_tower_training_integration_log.md`

### Changed

- Moved the repository from a design-only state into a first implemented vertical slice on `main`.
- Clarified the package as a runtime graph-discovery, annotation, and nested quotient-view engine over a predicate-defined hidden graph.
- Clarified that explored graph, vista graph, and quotient tiers should be treated as derived overlays/views rather than unrelated graph objects.
- Clarified that quotient reward aggregation should ignore internal collapsed edges and use only boundary-crossing preimage contributors.
- Clarified that full tower update occurs immediately after each newly discovered state during runtime.

### Validation

- Added broad test coverage across:
  - contracts
  - graph layers
  - quotient behavior
  - runtime snapshots
  - tower runtime behavior
  - example environments
  - adapters
  - integration slices
