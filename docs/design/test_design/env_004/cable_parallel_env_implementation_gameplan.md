# Cable Parallel Env Implementation Gameplan

## Status

This document governs the implementation of `cable_parallel_env`.

## File targets

- `src/state_collapser/examples/cable_parallel_env/__init__.py`
- `src/state_collapser/examples/cable_parallel_env/env.py`
- `src/state_collapser/examples/cable_parallel_env/runtime.py`
- `src/state_collapser/examples/cable_parallel_env/training.py`
- `tests/examples/test_cable_parallel_env_*.py`

## Implementation order

1. implement pose and cable geometry helpers
2. implement validity and transition logic
3. implement env wrapper
4. implement runtime/training surface
5. add tests
6. validate

## Stop conditions

Full-stop if the env collapses structurally into a renamed `plate_support_env`.
