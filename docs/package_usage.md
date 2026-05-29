# Package Usage Notes

This document is a stable routing note for package users. It intentionally does
not maintain a full inventory of implemented modules, examples, or training
surfaces. Those details change quickly while `state_collapser` is still
pre-alpha, and duplicating them here would make this file drift from the repo.

## Start Here

- New to the package: [usage overview](./usage/01_001_what_state_collapser_is.md)
- Trying to understand the tower runtime:
  [tower runtime mental model](./usage/01_002_tower_runtime_mental_model.md)
- Trying to train with your own learner:
  [training surface quickstart](./usage/01_003_training_surface_quickstart.md)
- Working with freeze-and-lift training:
  [fiber-conditioned training](./usage/01_004_fiber_conditioned_training.md)
- Using your own training loop:
  [own training loop guide](./usage/01_005_using_your_own_training_loop.md)
- Adding a tensor/model boundary:
  [tensorization boundary](./usage/01_010_tensorization_boundary.md)
- Integrating a Gymnasium environment:
  [Gymnasium integration](./usage/01_006_gymnasium_integration.md)
- Looking at downstream applications:
  [downstream applications](./usage/01_009_downstream_applications.md)
- Looking for exact provisional API surfaces:
  [API notes](./api_notes)

## Current Package Posture

`state_collapser` is an installable Python package with real implemented runtime,
example, training, and benchmark surfaces. It is still pre-alpha, so users should
distinguish between:

- stable top-level package metadata
- documented provisional engineer-facing surfaces
- importable internal modules that may still change

The stable top-level import surface remains intentionally small:

```python
import state_collapser

print(state_collapser.__version__)
```

For public API expectations, read [public API policy](./public_api.md).

## Optional Dependency Groups

Install the RL-facing optional dependency group with:

```bash
pip install -e ".[rl]"
```

Install the model-backend optional dependency group with:

```bash
pip install -e ".[ml]"
```

Install everything currently defined for local development with:

```bash
pip install -e ".[dev,rl,ml]"
```

`ROS 2` is intentionally not represented as a normal Python optional dependency.
It is a broader systems integration boundary whose concrete attachment points
should be designed explicitly rather than implied by a PyPI extra alone.

## Rule Of Thumb

Use the README for the project overview, `docs/usage` for engineer-facing
workflow guidance, and `docs/api_notes` for exact provisional surfaces. Treat
this document as a map, not as the implementation inventory.

If you are maintaining a downstream package such as `HGraphML`, start with the
downstream-applications note and the public API policy before depending on new
submodules.
