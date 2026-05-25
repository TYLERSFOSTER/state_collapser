# Glossary

## Total Graph

The discovered transition graph at the finest runtime tier. In notation this is
often `G_t^0`. Do not confuse this with a globally meaningful "base graph";
"base" is projection-relative.

## Total State

A state in the total discovered graph. Compatibility APIs may still use
`current_base_state`.

## Fine Tier

The more detailed tier in an adjacent training pair. First-scope
fiber-conditioned training uses `fine_tier = coarse_tier - 1`.

## Coarse Tier

The more collapsed quotient tier in an adjacent training pair. This is the tier
whose behavior is frozen while training the finer stage.

## Upstairs

The finer side of a projection.

## Downstairs

The coarser quotient side of a projection.

## PartitionTower

The runtime source of truth for nested state/action partition tables.

## QuotientTierView

A compatibility readout of tower structure. Do not confuse this with the hot-path
runtime representation.

## FrozenQuotientBehavior

A coarse quotient behavior held fixed while training a finer stage. It may carry
a concrete `FrozenQuotientStep` now and later can carry policy-level behavior.

## PathFiber

The fine-tier behavior lying over a frozen coarse behavior. Do not confuse this
with `PartitionTower.refinement_fiber(...)`, which is a local adjacent-cell query.

## FiberConditionedStage

A package-native stage that exposes ordinary `ActionSelectionInput` and
`TrainingTransition` objects while restricting actions to the active path fiber.

## FiberDeparture

A diagnostic record explaining why an attempted action is outside the current
fiber or cannot be lifted.

## ActionSelectionInput

The learner-facing input object for choosing an action.

## TrainingTransition

The learner-facing transition object produced after a step or diagnostic stage
event.
