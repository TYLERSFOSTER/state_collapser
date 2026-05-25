# Parallelogram Singularity Env Implementation Gameplan

## Status

This document governs the implementation of `parallelogram_singularity_env`.

## File targets

- `src/state_collapser/examples/parallelogram_singularity_env/__init__.py`
- `src/state_collapser/examples/parallelogram_singularity_env/env.py`
- `src/state_collapser/examples/parallelogram_singularity_env/runtime.py`
- `src/state_collapser/examples/parallelogram_singularity_env/training.py`
- `tests/examples/test_parallelogram_singularity_env_*.py`

## Implementation order

1. implement state and singularity helpers
2. implement validity and transitions
3. implement env wrapper
4. implement runtime/training surface
5. add tests
6. validate

## Stop conditions

Full-stop if singularity cannot be made operational in a small discrete state graph.
