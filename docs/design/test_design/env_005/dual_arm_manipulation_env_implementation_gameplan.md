# Dual-Arm Manipulation Env Implementation Gameplan

## Status

This document governs the implementation of `dual_arm_manipulation_env`.

## File targets

- `src/state_collapser/examples/dual_arm_manipulation_env/__init__.py`
- `src/state_collapser/examples/dual_arm_manipulation_env/env.py`
- `src/state_collapser/examples/dual_arm_manipulation_env/runtime.py`
- `src/state_collapser/examples/dual_arm_manipulation_env/training.py`
- `tests/examples/test_dual_arm_manipulation_env_*.py`

## Implementation order

1. implement state and support helpers
2. implement validity and transitions
3. implement env wrapper
4. implement runtime/training surface
5. add tests
6. validate

## Stop conditions

Full-stop if the state/action story expands into a large simulator-style design.
