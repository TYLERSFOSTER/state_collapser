# Tensorization Implementation Log

Date: 2026-05-29

Gameplan:

- `docs/design/tensorization/01_003_tensorization_implementation_gameplan.md`

## Execution Authority

The Project Owner explicitly requested execution:

> execute `docs/design/tensorization/01_003_tensorization_implementation_gameplan.md` following `prime_directive`. Use step-by-step procedural rule. Make new branch for work

## Starting State

Branch:

```text
codex/tensorization-boundary
```

Starting commit:

```text
c9fd12fb5f188553eea0173826de50931da86b2c
```

Starting `git status --short`:

```text
M  docs/design/logHRL.bib
M  docs/design/logHRL_w_comments.pdf
M  docs/design/logHRL_w_comments.tex
A  docs/design/tensorization/README.md
AM docs/design/tensorization/design_conversation.md
?? docs/design/tensorization/01_001_tensorization_architecture_blueprint.md
?? docs/design/tensorization/01_002_tensorization_engineer_usage_blueprint.md
?? docs/design/tensorization/01_003_tensorization_implementation_gameplan.md
```

Notes:

- The `docs/design/logHRL*` changes were already present before this
  implementation interval and are not part of this work.
- The tensorization design documents were already present before implementation
  and are treated as the approved design/gameplan context for this work.

## Phase.Stage.Action Log

### Phase 0: Execution Setup And Reality Binding

#### Action 0.1.1

Status: complete.

The Project Owner explicitly approved execution in the active conversation.

#### Action 0.1.2

Status: complete.

Created and switched to:

```text
codex/tensorization-boundary
```

#### Action 0.2.1

Status: complete.

Repository reality is being rebound against the files named in the gameplan.

Confirmed existing symbols:

- `ActionSelectionInput`
- `TrainingTransition`
- `ActionDecision`
- `FiberStageContext`
- `FiberDeparture`
- `PathFiber`
- `FiberConditionedStage`
- `PartitionTower`
- `BaseGraphRegistry`
- `StateCellId`
- `ActionCellId`
- `ActionCollectionId`

#### Action 0.2.2

Status: complete.

Confirmed optional dependency posture:

- core dependencies remain light
- `rl` extra includes `numpy>=2.0.0`
- `ml` extra includes `torch>=2.4.0`
- pytest marker `requires_torch` is registered

### Phase 1: Backend-Independent Linearization Skeleton

#### Actions 1.1.1-1.2.4

Status: complete.

Implemented:

- `src/state_collapser/training/linearization.py`
- `LinearizationState`
- `NumericBackend`
- `TensorDeviceKind`
- `LinearizationConfig`
- `LinearizationReport`
- optional NumPy availability checks
- optional Torch availability checks without module-level Torch import

Notes:

- `state_collapser.training.linearization` does not bind a module-level `torch`
  symbol.
- NumPy did not become a core dependency.
- Torch remains optional and isolated.

### Phase 2: Shared Encoding Registry

#### Actions 2.1.1-2.2.2

Status: complete.

Implemented:

- `EncodingRegistry`
- `EncodingRegistry.from_tower(...)`
- deterministic registry fingerprinting
- tower id reuse for states, edges, action identities, tiers, state cells,
  action collections, and action cells
- stage/fiber/frozen-behavior encoding
- fiber-departure reason encoding

HGraphML compatibility note:

- The registry can be built from `PartitionTower` without `ActionSelectionInput`,
  `TrainingTransition`, or Torch.

### Phase 3: Backend-Independent Linearized Records

#### Actions 3.1.1-3.3.2

Status: complete.

Implemented:

- `LinearizedActionSelectionInput`
- `LinearizedTrainingTransition`
- `linearize_action_selection_input(...)`
- `linearize_training_transition(...)`
- first-scope observation conversion
- fixed/padded action-mask normalization
- fixed/padded tower-position encoding
- stage/fiber/frozen-behavior metadata conversion
- action-cell chosen-action index resolution through
  `fiber_action_vocabulary`

Notes:

- Ragged action vocabularies remain metadata sidecars.
- Lift candidates are not tensorized.
- Unsupported observation forms fail in strict mode and sidecar in non-strict
  mode.

### Phase 4: Report Construction And Timing Hooks

#### Actions 4.1.1-4.2.1

Status: complete.

Implemented:

- `build_linearization_report(...)`
- `ConversionTiming`
- `time_conversions(...)`
- `export_linearized_record(...)`

Notes:

- Reports expose derived benchmark labels.
- Reports/configs are JSON-safe.
- Linearized records are not persisted by default.

### Phase 5: Public Exports

#### Actions 5.1.1-5.2.1

Status: complete.

Updated:

- `src/state_collapser/training/__init__.py`

Exported backend-independent tensorization symbols from
`state_collapser.training`.

Validation:

```text
uv run pytest tests/training/test_linearization_config.py tests/training/test_encoding_registry.py tests/training/test_linearized_records.py
```

Outcome:

```text
10 passed
```

### Phase 6: Torch Boundary Behind `ml`

#### Actions 6.1.1-6.3.1

Status: complete.

Implemented:

- `src/state_collapser/training/torch.py`
- `TorchDecisionBatch`
- `TorchTransitionBatch`
- local Torch import failure message
- CPU/CUDA device handling
- `action_decision_from_logits(...)`

Notes:

- Torch-specific imports are local to `state_collapser.training.torch`.
- CUDA mode raises clearly when CUDA is requested but unavailable.
- No Torch symbols are exported from `state_collapser.training.__init__`.

### Phase 7: Backend-Independent Tests

#### Actions 7.1.1-7.3.2

Status: complete.

Added:

- `tests/training/test_linearization_config.py`
- `tests/training/test_encoding_registry.py`
- `tests/training/test_linearized_records.py`

Validation:

```text
uv run pytest tests/training/test_linearization_config.py tests/training/test_encoding_registry.py tests/training/test_linearized_records.py
```

Outcome:

```text
10 passed
```

### Phase 8: Torch Boundary Tests

#### Actions 8.1.1-8.2.1

Status: complete.

Added:

- `tests/training/test_torch_batches.py`
- `tests/examples/test_torch_tensor_boundary_smoke_model.py`

Validation:

```text
uv run pytest tests/training/test_torch_batches.py tests/examples/test_torch_tensor_boundary_smoke_model.py
```

Outcome:

```text
4 skipped
```

Torch is not installed in the current environment, so Torch-specific tests were
collected and skipped cleanly.

### Phase 9: Training And Fiber Integration

#### Actions 9.1.1-9.2.1

Status: complete.

Implemented through backend-independent record tests and the focused training
validation slice.

Validation:

```text
uv run pytest tests/training tests/examples/test_plate_support_env_fiber_conditioned_stage.py tests/examples/test_training_semantics_shared.py
```

Outcome:

```text
75 passed, 3 skipped
```

### Phase 10: Benchmark-Visible Reporting

#### Actions 10.1.1-10.2.1

Status: complete.

Implemented through:

- `LinearizationConfig.to_dict()`
- `LinearizationConfig.from_dict(...)`
- `LinearizationConfig.derived_benchmark_label`
- `LinearizationReport.to_dict()`
- report tests for disabled mode and backend availability fields

Derived labels covered:

- `none_control_flow`
- `tensor_available_disabled`
- `tensor_enabled_cpu`
- `tensor_enabled_cuda`

### Phase 11: Documentation Implementation

#### Actions 11.1.1-11.2.1

Status: complete.

Added:

- `docs/usage/01_010_tensorization_boundary.md`

Updated routing:

- `README.md`
- `docs/package_usage.md`
- `docs/public_api.md`

### Phase 12: Validation And Completion Review

#### Action 12.1.1

Status: complete.

Validation:

```text
uv run pytest tests/training -k "linearization or torch"
```

Outcome:

```text
5 passed, 3 skipped, 66 deselected
```

#### Action 12.1.2

Status: complete.

Validation:

```text
uv run pytest tests/tower/partition/test_hgraphml_downstream_compatibility.py tests/tower/partition tests/training
```

Outcome:

```text
147 passed, 3 skipped
```

#### Action 12.2.1

Status: complete.

Validation:

```text
uv run pytest tests/training tests/examples/test_plate_support_env_fiber_conditioned_stage.py tests/examples/test_training_semantics_shared.py
```

Outcome:

```text
75 passed, 3 skipped
```

#### Action 12.2.2

Status: complete.

Validation:

```text
uv run pytest -m requires_torch tests/training
```

Outcome:

```text
3 skipped, 71 deselected
```

Torch is not installed in this environment.

#### Action 12.3.1

Status: complete.

Validation:

```text
uv run ruff check
uv run mypy
```

Outcome:

```text
All checks passed.
Success: no issues found in 100 source files.
```

#### Action 12.3.2

Status: complete.

Validation:

```text
uv run pytest
```

Outcome:

```text
477 passed, 4 skipped
```

#### Action 12.4.1

Status: complete.

Semantic completion check:

- Backend-independent records live in `state_collapser.training.linearization`.
- Torch conversion lives in `state_collapser.training.torch`.
- Benchmark labels distinguish absent, disabled, CPU-enabled, and CUDA-enabled
  modes.
- Disabled mode can build reports without constructing Torch batches.
- Masks are boolean fixed/padded tuples before Torch and boolean tensors in
  Torch batches.
- Tower positions are encoded through `EncodingRegistry`.
- HGraphML compatibility is preserved through shared tower/cell/edge encoding
  that does not require RL training objects.
- Persisted artifacts are config/report dictionaries, not every record.
- Ragged tensors, replay, checkpointing, model families, and external RL
  framework adapters remain deferred.

#### Action 12.4.2

Status: complete.

Final `git status --short` at validation time:

```text
 M README.md
M  docs/design/logHRL.bib
M  docs/design/logHRL_w_comments.pdf
M  docs/design/logHRL_w_comments.tex
A  docs/design/tensorization/README.md
AM docs/design/tensorization/design_conversation.md
 M docs/package_usage.md
 M docs/public_api.md
 M src/state_collapser/training/__init__.py
?? docs/design/tensorization/01_001_tensorization_architecture_blueprint.md
?? docs/design/tensorization/01_002_tensorization_engineer_usage_blueprint.md
?? docs/design/tensorization/01_003_tensorization_implementation_gameplan.md
?? docs/design/tensorization/01_004_tensorization_implementation_log.md
?? docs/usage/01_010_tensorization_boundary.md
?? src/state_collapser/training/linearization.py
?? src/state_collapser/training/torch.py
?? tests/examples/test_torch_tensor_boundary_smoke_model.py
?? tests/training/test_encoding_registry.py
?? tests/training/test_linearization_config.py
?? tests/training/test_linearized_records.py
?? tests/training/test_torch_batches.py
```

Pre-existing unrelated dirty files remain:

- `docs/design/logHRL.bib`
- `docs/design/logHRL_w_comments.pdf`
- `docs/design/logHRL_w_comments.tex`

Whitespace validation:

```text
git diff --check
```

Outcome:

```text
passed
```

## Final Validation Summary

Commands run:

```text
uv run pytest tests/training/test_linearization_config.py tests/training/test_encoding_registry.py tests/training/test_linearized_records.py
uv run pytest tests/training/test_torch_batches.py tests/examples/test_torch_tensor_boundary_smoke_model.py
uv run ruff check
uv run mypy
uv run pytest tests/tower/partition/test_hgraphml_downstream_compatibility.py tests/tower/partition tests/training
uv run pytest tests/training tests/examples/test_plate_support_env_fiber_conditioned_stage.py tests/examples/test_training_semantics_shared.py
uv run pytest -m requires_torch tests/training
uv run pytest
uv run pytest tests/training -k "linearization or torch"
git diff --check
```

Final outcomes:

- Focused backend-independent tests: `10 passed`
- Optional Torch selected tests: `4 skipped`
- Ruff: passed
- Mypy: passed
- HGraphML/tower/training compatibility: `147 passed, 3 skipped`
- Training/example compatibility: `75 passed, 3 skipped`
- Torch-marker validation: `3 skipped, 71 deselected`
- Full suite: `477 passed, 4 skipped`
- Exact focused gameplan command: `5 passed, 3 skipped, 66 deselected`
- Whitespace diff check: passed

## Known Residual Risks

- Torch is not installed in this environment, so Torch tests were collected and
  skipped rather than executed.
- CUDA behavior is covered structurally but not exercised on actual CUDA
  hardware.
- NumPy remains optional; NumPy array emission is not yet implemented beyond
  backend availability/reporting and backend-independent Python numeric records.
- Full ragged tensor support is intentionally deferred.

## Merge-Readiness Statement

The tensorization boundary implementation is ready for Project Owner review.

It satisfies the gameplan's first-scope goals without making the runtime
tensor-first, without importing Torch through `state_collapser.training`, and
without forcing HGraphML through RL-specific training objects.
