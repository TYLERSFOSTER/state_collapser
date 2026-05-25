# Example Family Implementation Log

## Status

- Branch:
  - `codex/example-family-implementation`
- Overall status:
  - first-wave example-family implementation completed
- Governing blueprint:
  - [example_family_blueprint_from_mathematical_model_list.md]([state_collapser repository root]/docs/design/test_design/example_family_blueprint_from_mathematical_model_list.md)
- Governing gameplan:
  - [example_family_implementation_gameplan.md]([state_collapser repository root]/docs/design/test_design/example_family_implementation_gameplan.md)
- Supporting evaluation methodology:
  - [evaluation_strategy.md]([state_collapser repository root]/docs/design/test_design/evaluation_strategy.md)
- Prime-directive sources:
  - [prime_directive.md]([state_collapser repository root]/docs/prime_directive/prime_directive.md)
  - [common_failure_mode_001.md]([state_collapser repository root]/docs/prime_directive/common_failure_mode_001.md)
  - [common_failure_mode_002_implementation_without_owner_approval.md]([state_collapser repository root]/docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md)
  - [common_failure_mode_003_gameplan_rewrite_during_implementation.md]([state_collapser repository root]/docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md)

## Bound Family Set

- First-wave build set:
  - `articulated_loop_env`
  - `dual_arm_manipulation_env`
  - `cable_parallel_env`
  - `parallelogram_singularity_env`
- Deferred:
  - multi-contact humanoid robot
  - multi-ped robots

## Action Log

### Phase 1.Stage 1.Action 1.1.1

- Status: completed
- Result:
  - created this running log

### Phase 1.Stage 2.Actions 1.2.1–1.2.2

- Status: completed
- Result:
  - bound the governing source set
  - bound the first-wave build set and deferred set

### Phase 2.Stage 1.Action 2.1.1

- Status: completed
- Result:
  - created:
    - `docs/design/test_design/env_002/`
    - `docs/design/test_design/env_003/`
    - `docs/design/test_design/env_004/`
    - `docs/design/test_design/env_005/`

### Phase 2.Stage 2.Action 2.2.1

- Status: completed
- Result:
  - bound canonical numbering:
    - `env_002` → `articulated_loop_env`
    - `env_003` → `parallelogram_singularity_env`
    - `env_004` → `cable_parallel_env`
    - `env_005` → `dual_arm_manipulation_env`

### Phase 3 — env_002 completed

- Status: completed
- Result:
  - wrote the env-specific spec, gameplan, and implementation log
  - implemented:
    - `src/state_collapser/examples/articulated_loop_env/__init__.py`
    - `src/state_collapser/examples/articulated_loop_env/env.py`
    - `src/state_collapser/examples/articulated_loop_env/runtime.py`
    - `src/state_collapser/examples/articulated_loop_env/training.py`
  - added focused env tests covering:
    - geometry
    - validity
    - primitive transitions
    - runtime integration
    - tower-training smoke behavior
  - resolved the initial frozen-graph failure by moving from exact hard closure to a small explicit coupler-slack / mismatch-budget model while preserving primitive one-joint actions

### Phase 4 — env_005 completed

- Status: completed
- Result:
  - wrote the env-specific spec, gameplan, and implementation log
  - implemented:
    - `src/state_collapser/examples/dual_arm_manipulation_env/__init__.py`
    - `src/state_collapser/examples/dual_arm_manipulation_env/env.py`
    - `src/state_collapser/examples/dual_arm_manipulation_env/runtime.py`
    - `src/state_collapser/examples/dual_arm_manipulation_env/training.py`
  - added focused env tests covering:
    - geometry
    - validity
    - coordinated transitions
    - runtime integration
    - tower-training smoke behavior

### Phase 5 — env_004 completed

- Status: completed
- Result:
  - wrote the env-specific spec, gameplan, and implementation log
  - implemented:
    - `src/state_collapser/examples/cable_parallel_env/__init__.py`
    - `src/state_collapser/examples/cable_parallel_env/env.py`
    - `src/state_collapser/examples/cable_parallel_env/runtime.py`
    - `src/state_collapser/examples/cable_parallel_env/training.py`
  - added focused env tests covering:
    - geometry / required-tension structure
    - validity
    - transition behavior
    - runtime integration
    - tower-training smoke behavior

### Phase 6 — env_003 completed

- Status: completed
- Result:
  - wrote the env-specific spec, gameplan, and implementation log
  - implemented:
    - `src/state_collapser/examples/parallelogram_singularity_env/__init__.py`
    - `src/state_collapser/examples/parallelogram_singularity_env/env.py`
    - `src/state_collapser/examples/parallelogram_singularity_env/runtime.py`
    - `src/state_collapser/examples/parallelogram_singularity_env/training.py`
  - added focused env tests covering:
    - singular-geometry logic
    - validity
    - transition behavior
    - runtime integration
    - tower-training smoke behavior

### Phases 7–10 completed

- Status: completed
- Result:
  - confirmed the new environments fit the shared evaluation shape as small discrete hidden-constraint examples
  - preserved:
    - `plate_support_env`
    - `robot_constraint_toy`
  - completed broader example validation and full repo validation
  - refreshed stale editable-install metadata in `.venv` so the package-version test reflects current source state

## Test Results

- Focused env_002 validation:
  - `.venv/bin/python -m pytest tests/examples/test_articulated_loop_env_geometry.py tests/examples/test_articulated_loop_env_validity.py tests/examples/test_articulated_loop_env_transitions.py tests/examples/test_articulated_loop_env_runtime_integration.py tests/examples/test_articulated_loop_env_tower_training.py`
  - result: `11 passed`
- Focused env_002 + env_005 validation:
  - result: `22 passed`
- Focused first-wave family validation:
  - `.venv/bin/python -m pytest` over the 20 new example tests
  - result: `43 passed`
- Broader example validation:
  - `.venv/bin/python -m pytest tests/examples`
  - result: `119 passed`
- Full repo validation:
  - `.venv/bin/python -m pytest`
  - result: `225 passed`
  - `.venv/bin/python -m ruff check .`
  - result: passed
  - `.venv/bin/python -m mypy src`
  - result: passed

## Surprises

- The first exact-closure version of `articulated_loop_env` produced a valid start state with no valid outgoing primitive transitions.
- The correct fix was not coordinated / pre-coupled actions; it was the owner-approved explicit mismatch-tolerance / coupler-slack semantics.
- The full `pytest` run initially failed on `tests/test_package.py` because local installed metadata in `.venv` still reported `state-collapser==0.2.0` while source was `0.3.0`.
- Refreshing the editable install resolved that environment-level mismatch cleanly.

## Owner Clarifications

- `env_002` clarification:
  - preserve primitive one-joint actions
  - do not solve the connectivity problem by introducing pre-coupled coordinated actions
  - instead use a small explicit closure error tolerance / coupler-slack or mismatch-budget idea so the env remains relevant to the project’s anti-parametrization goal

## Blockers

- Resolved blocker:
  - the initial `env_002` exact-closure design locally froze the feasible graph
  - resolution came from owner direction to preserve one-joint primitive actions and instead widen validity with a small closure-error tolerance / coupler-slack budget
- Final blocker status:
  - none
