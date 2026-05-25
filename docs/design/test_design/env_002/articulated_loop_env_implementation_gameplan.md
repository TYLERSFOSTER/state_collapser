# Articulated Loop Env Implementation Gameplan

## Status

This document governs the implementation of `articulated_loop_env`.

## File targets

- `src/state_collapser/examples/articulated_loop_env/__init__.py`
- `src/state_collapser/examples/articulated_loop_env/env.py`
- `src/state_collapser/examples/articulated_loop_env/runtime.py`
- `src/state_collapser/examples/articulated_loop_env/training.py`
- `tests/examples/test_articulated_loop_env_*.py`

## Implementation order

1. implement state, geometry, and mismatch-budget helpers
2. implement validity and transition logic with explicit slack semantics
3. implement env wrapper
4. implement runtime binding to `TowerRuntime`
5. implement first tower-training smoke path
6. add focused tests
7. validate

## Stop conditions

Full-stop if:

- the closure rule yields an empty or trivially tiny feasible graph
- the slack rule makes the feasible graph effectively unconstrained
- the env requires continuous geometry to make sense
- the validity rule no longer encodes loop closure directly
