# Synthetic Blow Review Revisions 02

This folder tracks implementation planning for the unstruck items in the current
full-repo synthetic Blow-style review:

- source review:
  `docs/code_review/03_001_synthetic_blow_full_repo_review_current_state.md`
- created: 2026-06-04
- status: design track opened; implementation blueprint not yet written

## Scope

The Project Owner struck through the review items that should not be implemented
in this pass. This folder therefore scopes only the remaining changes.

### In Scope

1. NumPy observation support at the backend-independent linearization boundary.
2. Partition/action-layer invariant checking for source-support and dirty-index
   correctness.
3. Explicit concrete lift-selection policy for `FiberConditionedStage`.
4. Mandatory dependency cleanup around apparently unused `pillow`.
5. Small front-door documentation cleanup for stale release/version and artifact
   contract material.

## Explicitly Out Of Scope

The following struck-through review items should not drive this implementation
track:

1. Optional Torch CI expansion.
2. Serious benchmark artifact/harness work.
3. Replay, checkpoint, vectorized rollout, or experiment-manifest framework work.
4. A full tower-augmented Gymnasium wrapper beyond the current realized-transition
   recorder.

These may remain valid future work, but they are intentionally deferred here.

## Intended Next Documents

This folder should next receive:

1. `01_001_synthetic_blow_revisions_02_blueprint.md`
2. `01_002_synthetic_blow_revisions_02_implementation_gameplan.md`
3. `01_003_synthetic_blow_revisions_02_implementation_log.md`

The blueprint should ground truth each in-scope item against the current repo
before any code changes are made.

## Implementation Spine

The likely implementation spine is:

1. Add optional NumPy-array handling to
   `src/state_collapser/training/linearization.py` without importing NumPy at
   package import time.
2. Add focused tests that linearize real observations from packaged example
   environments.
3. Add an invariant-checking surface for `ActionPartitionLayer` and/or
   `PartitionTower`, then use it in partition tests.
4. Add a `lift_selector` surface to `FiberConditionedStage`, with deterministic
   first-candidate behavior as the default and diagnostics recording the selected
   lift.
5. Decide whether `pillow` should be removed from base dependencies or moved to a
   future optional visualization/instrumentation extra.
6. Refresh only the stale front-door docs named by the review, without expanding
   into the deferred benchmark/framework work.

## Validation Target

At minimum, the implementation pass should finish with:

```bash
uv run ruff check .
uv run mypy src
uv run pytest
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
```

Focused test additions should cover:

- strict and non-strict NumPy observation linearization
- example-environment observation linearization
- partition/action-layer invariant success and failure cases
- multiple concrete lifts under one abstract action cell
- package metadata/dependency expectations if `pillow` changes

