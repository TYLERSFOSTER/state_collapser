# Common Misunderstandings

## "`G_t^0` is the base graph."

Better: `G_t^0` is the total discovered graph at time `t`. "Base" is relative to
a projection, so new docs should prefer "total graph" unless quoting legacy
compatibility vocabulary.

## "Lift is an external heuristic."

Better: in this package, lift is implemented through the path fiber of a tower
projection. A fine action is admissible when it lies over the frozen coarse
behavior.

## "`state_collapser` is RLlib or Stable-Baselines3."

No. RLlib and Stable-Baselines3 run learner frameworks over environments.
`state_collapser` constructs quotient/fiber decision structure around an
environment or discovered transition system.

## "The package should hide the training loop."

No. The package should expose good training components. The engineer owns the
loop, model, optimizer, checkpoint, and experiment policy.

## "`PartitionTower.refinement_fiber(...)` is the whole path fiber."

No. `refinement_fiber(...)` is a local adjacent-cell query. `PathFiber` composes
tower queries with a frozen coarse behavior over time.

## "`FiberConditionedStage` is a Gymnasium env."

No. It is package-native first. A Gymnasium adapter can wrap it later.
