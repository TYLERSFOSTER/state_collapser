# Synthetic Blow Revisions 02 Implementation Log

Date: 2026-06-04

Branch:

```text
codex/synthetic-blow-revisions-02
```

Blueprint:

```text
docs/design/synthetic_blow_revisions_02/01_001_synthetic_blow_revisions_02_blueprint.md
```

Gameplan:

```text
docs/design/synthetic_blow_revisions_02/01_002_synthetic_blow_revisions_02_implementation_gameplan.md
```

Downstream handoff:

```text
big_boy_benchmarking_synthetic_blow_revisions_02_handoff.md
```

## Status Table

| Phase | Status | Notes |
| --- | --- | --- |
| Phase 0: Branch, Baseline, And Log | Complete | Branch created; baseline validation clean. |
| Phase 1: NumPy Observation Linearization | Complete | Lazy NumPy observation support implemented and tested. |
| Phase 2: Partition Source-Support Invariant Checking | Complete | Invariant report/assertion APIs implemented and tested. |
| Phase 3: Explicit Lift Selection In `FiberConditionedStage` | Complete | Default-preserving lift selector hook implemented and tested. |
| Phase 4: Mandatory `pillow` Dependency Cleanup | Complete | No source/test usage found; base dependency removed and lock updated. |
| Phase 5: Small Front-Door Documentation Cleanup | Complete | README, artifact contract, and instrumentation wording updated. |
| Phase 6: Downstream Handoff Alignment | Complete | Root handoff now names implemented APIs and diagnostics. |
| Phase 7: Full Validation | Complete | Focused tests, full pytest, ruff, mypy, build, benchmark smoke, and diff checks passed. |
| Phase 8: Closeout | Complete | Log completed; no commit requested. |

## Phase 0 Notes

### Phase 0.Stage 1

Completed directive re-read:

```text
docs/prime_directive/git_practices.md
docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md
docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md
```

Project Owner explicitly requested execution of the gameplan and update of the
downstream handoff document.

Branch creation required escalated permission because the sandbox could not
create `.git/refs/heads/codex/synthetic-blow-revisions-02.lock`. The branch was
created successfully after approval.

Current branch:

```text
codex/synthetic-blow-revisions-02
```

Pre-existing untracked files observed at Phase 0:

```text
big_boy_benchmarking_synthetic_blow_revisions_02_handoff.md
docs/code_review/03_001_synthetic_blow_full_repo_review_current_state.md
docs/design/logHRL_bin.bib
docs/design/synthetic_blow_revisions_02/
docs/design/tropicalization_and_binary_coset_towers_comments.tex
```

The implementation will not modify unrelated untracked files:

```text
docs/design/logHRL_bin.bib
docs/design/tropicalization_and_binary_coset_towers_comments.tex
```

## Validation

### Phase 0 Baseline

Static validation:

```text
uv run ruff check .
All checks passed.

uv run mypy src
Success: no issues found in 90 source files.
```

Focused baseline tests:

```text
uv run pytest tests/training/test_linearized_records.py tests/training/test_fiber_conditioned_stage.py tests/tower/partition/test_pointwise_liftability.py tests/tower/partition/test_hgraphml_downstream_compatibility.py
18 passed.
```

Full test baseline:

```text
uv run pytest
503 passed, 4 skipped.
```

Benchmark smoke baseline:

```text
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
tower_runtime_bench mode=default steps=10 elapsed_seconds=0.007479 operations_per_second=1337.00 readout_requested=False morphism_requested=False tower_depth=2 discovered_states=22 discovered_edges=60
```

### Phase 1 NumPy Linearization

Test-first result:

```text
uv run pytest tests/training/test_linearized_records.py
4 failed, 3 passed.
```

The failures were expected and came from missing NumPy handling in
`_linearize_observation(...)`.

Implementation summary:

- Added `_try_linearize_numpy_observation(...)`.
- NumPy is imported lazily with `importlib.util.find_spec("numpy")` and
  `importlib.import_module("numpy")`.
- Supported dtype kinds are `b`, `i`, `u`, and `f`.
- Supported arrays flatten in row-major order to `tuple[float, ...]`.
- Metadata includes `kind`, `shape`, and `dtype`.
- Unsupported arrays raise `ValueError` in strict mode and sidecar metadata in
  non-strict mode.

Validation:

```text
uv run pytest tests/training/test_linearized_records.py
7 passed.

uv run mypy src
Success: no issues found in 90 source files.
```

### Phase 2 Partition Invariants

Implementation summary:

- Added `src/state_collapser/tower/partition/invariants.py`.
- Added `PartitionInvariantIssue` and `PartitionInvariantReport`.
- Added `action_layer_invariant_report(...)`.
- Added `ActionPartitionLayer.invariant_report(...)`.
- Added `ActionPartitionLayer.assert_consistent(...)`.
- Added `PartitionTower.invariant_report(...)`.
- Added `PartitionTower.assert_consistent(...)`.
- Exported invariant report types from `state_collapser.tower.partition`.

Issue classes covered include:

- state-cell outgoing collection consistency;
- dirty collection detection;
- action-cell forward/reverse edge-index consistency;
- source/target state-cell consistency;
- adjacent-tier source-child support maps;
- lower action-cell support maps;
- flattened base-source support maps;
- collection-level active source unions;
- internal-edge separation.

Important repo-reality adjustment:

```text
Action layers retain some historical/obsolete collection and internal-edge
records after merges. The invariant checker treats historical unattached
collections without live action cells as allowed, and validates internal-edge
geometry only for active state cells while still checking record/key
consistency.
```

Validation:

```text
uv run pytest tests/tower/partition/test_partition_invariants.py tests/tower/partition/test_full_incremental_equivalence.py tests/tower/partition/test_pointwise_liftability.py tests/tower/partition/test_queries_and_lift.py tests/tower/partition/test_hgraphml_downstream_compatibility.py
26 passed.

uv run mypy src
Success: no issues found in 91 source files.
```

### Phase 3 Lift Selector

Implementation summary:

- Added `LiftSelector`.
- Added `deterministic_first_lift_selector(...)`.
- Added `FiberConditionedStage.lift_selector`.
- Replaced hidden `lift_candidates[0]` selection with validated selector logic.
- Exported selector types/helpers from `state_collapser.training`.

Selector signature:

```python
Callable[[tuple[BaseEdge, ...], ActionSelectionInput, ActionCellId], BaseEdge]
```

Default behavior:

```text
deterministic_first_lift_selector(...) returns lift_candidates[0].
```

Successful transition diagnostics added:

```text
lift_candidate_count
selected_lift_index
lift_selector
```

Validation:

```text
uv run pytest tests/training/test_fiber_conditioned_stage.py tests/examples/test_plate_support_env_fiber_conditioned_stage.py
13 passed.

uv run mypy src
Success: no issues found in 91 source files.

uv run ruff check src/state_collapser/training/stages.py tests/training/test_fiber_conditioned_stage.py
All checks passed.
```

### Phase 7 Final Validation

Focused validation:

```text
uv run pytest tests/training/test_linearized_records.py
7 passed.

uv run pytest tests/tower/partition/test_partition_invariants.py tests/tower/partition/test_full_incremental_equivalence.py tests/tower/partition/test_pointwise_liftability.py tests/tower/partition/test_queries_and_lift.py tests/tower/partition/test_hgraphml_downstream_compatibility.py
26 passed.

uv run pytest tests/training/test_fiber_conditioned_stage.py tests/examples/test_plate_support_env_fiber_conditioned_stage.py
13 passed.
```

Benchmark smoke:

```text
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
tower_runtime_bench mode=default steps=10 elapsed_seconds=0.007728 operations_per_second=1293.95 readout_requested=False morphism_requested=False tower_depth=2 discovered_states=22 discovered_edges=60
```

Static and full validation:

```text
uv run ruff check .
All checks passed.

uv run mypy src
Success: no issues found in 91 source files.

uv run pytest
516 passed, 4 skipped.

uv run python -m build
Successfully built state_collapser-0.7.1.tar.gz and state_collapser-0.7.1-py3-none-any.whl.
```

Diff checks:

```text
git diff --check
passed with no output.
```

Tracked diff summary:

```text
15 files changed, 529 insertions(+), 90 deletions(-)
```

## Dependency And Lockfile Actions

### Phase 4

Usage search:

```text
rg -n "PIL|pillow|Image" src tests pyproject.toml README.md docs
```

No source or test usage of `PIL`, `pillow`, or `Image` was found. Hits were
dependency metadata, design/review text, or unrelated title words.

Dependency decision:

```text
pillow>=12.2.0 removed from base dependencies.
```

Lockfile:

```text
uv lock
Resolved 89 packages.
Removed pillow v12.2.0.
```

`uv lock` first failed under sandboxed permissions while trying to access the
user uv cache. It was rerun with escalation and completed successfully.

Dependency validation:

```text
uv sync --extra dev --extra rl
Resolved 89 packages.
Uninstalled pillow==12.2.0.

uv run python -c "import state_collapser; print(state_collapser.__version__)"
0.7.1

uv run python -m build
Successfully built state_collapser-0.7.1.tar.gz and state_collapser-0.7.1-py3-none-any.whl.
```

## Downstream Handoff

The root handoff has been updated to name actual implemented APIs and
diagnostics:

```text
PartitionTower.invariant_report(...)
PartitionTower.assert_consistent(...)
ActionPartitionLayer.invariant_report(...)
ActionPartitionLayer.assert_consistent(...)
LiftSelector
deterministic_first_lift_selector(...)
lift_candidate_count
selected_lift_index
lift_selector
```

Placeholder search:

```text
rg -n "expected|planned|TODO|exact API|will be finalized|after implementation|Expected Upstream|expected to" big_boy_benchmarking_synthetic_blow_revisions_02_handoff.md
No matches.
```

## Documentation Cleanup

Phase 5 changes:

- README GitHub install tag updated from `v0.7.0` to `v0.7.2`.
- README instrumentation wording now says the namespace is reserved for future
  work and implemented instrumentation tooling is not yet part of the package
  surface.
- CONTRIBUTING instrumentation wording now says the namespace is reserved for
  future work.
- `docs/artifact_contracts.md` was refreshed to current artifact reality:
  `LiveRuntimeView`, `RuntimeSnapshot`, `LinearizationConfig`,
  `LinearizationReport`, design blueprints, implementation gameplans,
  implementation logs, engineer continuity reports, and deferred serious
  benchmark bundles.

Stale-front-door search:

```text
rg -n "v0\\.7\\.0|entering the first implementation phase|pillow|Pillow|instrumentation" README.md CONTRIBUTING.md docs/artifact_contracts.md docs/package_usage.md docs/public_api.md pyproject.toml
```

Remaining hits are intentional instrumentation references now framed as
reserved/future work. No stale version, Pillow dependency, or first
implementation phase hit remains in the target front-door docs.

## Surprises And Blockers

- Branch creation needed escalation because `.git/refs` writes were blocked by
  the sandbox.
- `uv lock` needed escalation because sandboxed access to the user uv cache was
  blocked.
- During invariant integration, historical internal-edge records attached to
  obsolete state cells had to be distinguished from active internal-edge
  records. The implementation preserves the current runtime history model and
  validates active internal-edge geometry.

## Closeout

Completed implementation scope:

- numeric NumPy observation linearization;
- partition/action invariant reporting and assertions;
- explicit lift selector hook and diagnostics;
- base dependency cleanup removing Pillow;
- small front-door documentation cleanup;
- downstream `big_boy_benchmarking` handoff update.

Struck-through items intentionally not implemented:

- Torch CI matrix expansion;
- serious benchmark artifact writing;
- replay/checkpoint/vectorized rollout/manifest framework work;
- full tower-augmented Gymnasium wrapper;
- package-owned neural model family;
- direct `big_boy_benchmarking` repo integration.

Deviations from gameplan:

```text
None requiring Project Owner approval.
```

Implementation notes:

- `ActionPartitionLayer.invariant_report(...)` is exposed through a local import
  to avoid import cycles.
- `PartitionTower.invariant_report(...)` combines per-tier reports.
- `deterministic_first_lift_selector(...)` preserves current selection behavior.
- Generated build artifacts were created by validation and are expected to
  remain ignored unless the Project Owner asks otherwise.

Current untracked files include pre-existing docs/research files that were not
part of this implementation:

```text
docs/design/logHRL_bin.bib
docs/design/tropicalization_and_binary_coset_towers_comments.tex
```

## v0.7.2 Release-Prep Addendum

Release-prep request:

```text
Prepare the implemented Synthetic Blow Revisions 02 work for a v0.7.2 tagged
release so big_boy_benchmarking can depend on a release tag.
```

Metadata updates:

- `pyproject.toml` version set to `0.7.2`.
- `src/state_collapser/_version.py` version set to `0.7.2`.
- `CITATION.cff` version set to `0.7.2` with release date `2026-06-05`.
- `README.md` GitHub install command updated to `v0.7.2`.
- `CHANGELOG.md` gained a `0.7.2` section.
- `big_boy_benchmarking_synthetic_blow_revisions_02_handoff.md` now tells
  downstream engineers to depend on the `v0.7.2` tag.
- `CONTRIBUTING.md` now names invariant checks and explicit lift selector hooks
  in roadmap/current-reality/testing guidance.
- `uv.lock` updated from `state-collapser v0.7.1` to `v0.7.2`.

Release-prep validation:

```text
uv run python -c "import state_collapser; print(state_collapser.__version__)"
0.7.2

uv run ruff check .
All checks passed.

uv run mypy src
Success: no issues found in 91 source files.

uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
tower_runtime_bench mode=default steps=10 elapsed_seconds=0.008284 operations_per_second=1207.11 readout_requested=False morphism_requested=False tower_depth=2 discovered_states=22 discovered_edges=60

uv run pytest
516 passed, 4 skipped.

uv run python -m build
Successfully built state_collapser-0.7.2.tar.gz and state_collapser-0.7.2-py3-none-any.whl.
```

Local environment note:

```text
During uv-driven reinstall commands, uv warned about a stale
state_collapser-0.7.1.dist-info directory missing a RECORD file. The commands
completed successfully and installed/reported 0.7.2.
```
