# Engineer Continuity Report
## 01_006_always_be_closing_and_downstairs_closure
## Date

2026-05-14

## Status

Focused design-continuity note capturing a newly recognized conceptual problem in the current project direction: the present training picture risks destroying the intended speedup by effectively learning too many tower levels in parallel instead of progressively pushing more and more training load downward into closed lower tiers.

This note is not a finished solution. It is an initial sketch of the problem, the insight behind it, and the next major line of mathematical/modeling work it appears to require.

## Trigger

The Project Owner recognized that the current repository direction has accidentally drifted away from the mechanism that originally made the speedup story compelling.

The key comparison used was voice-leading style staged growth:

- melody
- then `2`-part
- then `3`-part

That staged buildup carries a real sense of hierarchical reuse and staged learning compression.

But in the current repository direction, the system is closer to doing the analogue of:

- simultaneous or parallel learning across all levels

which tends to collapse back toward an overburdened version of the original flat problem rather than a true hierarchical speedup.

## Core realization

The important correction is:

- the system should not merely build tower structure while continuing to train every level in roughly the same way
- instead, once enough discovery and aggregation have occurred downstairs, more and more of the real learning burden should be pushed downward into that lower closed tier

That is, the package should not just be:

- “maintain all levels”

but something more like:

- “discover upstairs, aggregate downstairs, and then increasingly train in the closed lower world”

The Project Owner identified this as a missing operational directive and suggested the intentionally named principle:

- **ALWAYS BE CLOSING**

The reference is intended.

## Initial statement of the missing idea

The current system has:

- discovery
- repeated visitation
- local notes / annotations
- quotient-style aggregation
- reward aggregation machinery

But what is still missing is a strong closure principle that says:

- if exploration downstairs keeps striking the same nodes, stars, or local structural regions again and again,
- then eventually the system should stop treating that downstairs region primarily as an object of ongoing exploration,
- and instead treat it as a sufficiently closed training substrate

In other words, repeated downstairs rediscovery should become evidence that:

- the local lower-tier world has stabilized enough to deserve becoming the main training locus

rather than evidence that the system should continue paying full exploratory cost at all levels.

## Why this matters

Without this closure move, the system risks the following failure mode:

- tower construction exists
- reward aggregation exists
- multiple tiers exist
- but training continues to behave like an overgrown flat learner with extra bookkeeping

This means the project would preserve structural complexity without obtaining the intended training compression.

That would amount to losing the real speedup story.

The Project Owner’s point is that the speedup is not supposed to come merely from:

- “having a hierarchy”

It is supposed to come from:

- using higher exploration / aggregation to eventually make lower closed tiers trainable in a more efficient way

## The newly exposed central question

The real mathematical/design question appears to be:

- **When should a downstairs tier be considered closed?**

This is not yet answered in the present repository.

And it now appears to be one of the central unanswered questions for the training story.

## Initial closure heuristics that are now in view

At this stage these are only sketch directions, not approved final criteria.

Possible closure signals might include:

- repeated visitation of the same downstairs nodes
- repeated visitation of the same downstairs stars or local neighborhoods
- stabilization of outgoing-edge knowledge
- stabilization of quotient/coset annotations over the local region
- diminishing novelty in local push-pull updates
- sufficiently mature reward aggregation over the downstairs region
- sufficient agreement between repeated lifts/refinements and existing lower-tier structure

But the Project Owner’s formulation suggests that the deepest issue is not merely “enough repeats” in a shallow statistical sense.

It is more structural:

- at what point does a downstairs tier count as sufficiently discovered, equalized, and reward-informative that training should preferentially happen there?

## Relation to current package structure

This idea interacts directly with:

- quotient-tier views
- runtime snapshots
- reward aggregation
- tower training
- exploration policy
- trustworthiness / maturity ideas

It also partly reframes earlier questions about:

- lowest trustworthy tier first

because the more important missing idea may not just be trustworthiness at decision time, but:

- a closure regime that determines when a lower tier should become the dominant training substrate

## Why this is probably mathematical-model work first

The Project Owner explicitly noted that addressing this likely requires substantial mathematical-model work first.

That assessment seems right.

The missing concept is not just an implementation detail like:

- a new class
- a runner parameter
- a trainer callback

It is closer to:

- a new principle governing the relationship between exploration, closure, aggregation, and where real learning should happen

That likely needs to be clarified in the mathematical model before major new implementation work proceeds, because otherwise code changes risk hard-coding the wrong closure criterion.

## Suggested next work to set aside

The following next-work item should be considered set aside for deliberate future treatment:

- formulate the **ALWAYS BE CLOSING** principle carefully in the mathematical model and design documents

That likely decomposes into subproblems such as:

- define what it means for a lower tier to be “closed”
- define what observations count as evidence of closure
- define how closure changes exploration behavior
- define how closure changes training allocation across levels
- define how reward aggregation supports the transfer of training burden downward
- determine whether closure is local, regional, tier-wide, or dynamic
- determine whether closure is reversible when novelty reappears

## Working summary

The new insight is:

- the project currently risks learning all tower levels in parallel in a way that weakens the intended speedup

The missing directive is:

- **ALWAYS BE CLOSING**

The unresolved central question is:

- when should a downstairs tier be considered closed enough that increasingly more training should happen there?

The correct present response is:

- do not rush an implementation patch
- treat this as a major upcoming mathematical/design problem
- preserve this note as the first explicit continuity record of that realization

## Authorship / contribution note

This idea originated with the Project Owner.

The assistant’s role here is only:

- to capture the recognition cleanly
- preserve it in continuity form
- frame the likely next work without overcommitting to a premature solution
