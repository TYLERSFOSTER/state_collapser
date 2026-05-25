# Reward Locality For Quotient Training

## Implementation Status Note

The first implemented vertical slice now includes concrete reward objects and aggregation helpers for:

- primitive step reward
- cumulative weighted base-path reward
- quotient reward aggregation over explicit contributors

The current implementation follows the local/compositional reward regime described in this document and uses boundary-contributor filtering in the quotient reward tests.

This document remains the conceptual boundary statement for what reward regimes the current package stage is designed to support.

## Purpose

This document develops one of the main design constraints for `state_collapser`:

> What is the largest class of reward rules that are still local enough for mainstream RL training and still descend cleanly to quotient-level aggregated rewards?

The present answer is:

> RL problems where reward is Markov-local or near-Markov-local with respect to the modeled state used by training.

This document expands that statement, explains how we arrived at it, and describes the boundary where quotient-level reward descent begins to break.

## Why This Question Matters

`state_collapser` is not being designed as a generic graph package or as a purely mathematical quotienting toolkit.

It is meant to support:

- hidden or explorable state spaces
- dynamically built state graphs
- quotient or contraction towers
- hierarchical control and training over those towers

That means the package does not only need a theory of graph contraction.

It also needs a theory of when reward can still function sensibly after contraction.

This is especially important because the package is intended to remain recognizable as an RL-facing library rather than becoming a disconnected graph-theoretic side project.

So the reward question is not secondary.

It is part of the condition for the whole package to be trainable in a mainstream RL sense.

## The Correct Surface

One major clarification from the design discussion is that the correct reasoning surface is not:

- full omniscient knowledge of a completed fine graph
- ultimate physical reality
- a reward function discovered only through exploration

Instead, the correct surface is:

- an explorable but hidden state space
- a dynamically built associated state graph
- a reward-computation rule that may be globally known in advance
- a modeled state used by training

This matters because reward can be globally understood even when the graph is not.

For example:

- the environment may be only partially explored
- but the engineer may still know that reward is computed as a local function of `(state, action, next_state)`

That kind of reward knowledge is not something the agent must discover edge by edge.

So the question is:

> Given a known reward-computation rule, when does that rule descend cleanly to quotient-level aggregated rewards in a hidden/explorable graph setting?

That is the right version of the problem.

## The Quotient-Graph Picture Being Assumed

This reward discussion depends on a specific understanding of quotient graphs in the package.

The quotient graph is not being treated as a cartoon that forgets the original graph and replaces it with a small lossy summary.

Instead:

- the quotient graph is tied to the original dynamically built graph
- quotient nodes carry the data of the cosets they represent
- quotient edges carry the data of the transition families they represent
- the quotient structure can therefore remember the representative-level structure of the original explored graph

So a quotient path is not merely a vague coarse walk.

It is a sequence of quotient nodes and quotient edges whose realizability is understood in terms of representative compatibility.

This is what makes quotient-level reward discussion legitimate in the first place.

It is also important that the graph layers involved here are not assumed to be unrelated graph objects.

The intended implementation surface is:

- a hidden graph defined by state/action/spec/legality contracts
- derived explored and vista layers over that hidden graph
- quotient layers derived from those available graph views

This matters for reward because reward descent should be understood as occurring along structurally related graph layers, not across disconnected ad hoc graph representations.

At a quotient node, one can examine:

- the represented fine states
- the represented outgoing transition families
- the observed or known reward behavior attached to those transitions

And from that, one can attempt to build quotient-level reward summaries.

For the present stage of the project, the working scope should be understood as edge-computed reward decorating the `1`-categorical graph structure:

```text
reward decorates Cat^1(G_t)
```

That is:

- reward is attached to the graph-level transition/composition surface currently being modeled
- the package is not yet trying to implement the full simplicial, higher-categorical, or homotopy-colimit picture that may ultimately sit behind the mathematics

This scope restriction is deliberate.

The broader path-space discussion strongly suggests that a fuller treatment might eventually want:

- path fibers over quotient paths
- higher compositional summaries
- simplicial or `(\infty)`-categorical quotient structure
- a more Malik-Foster-style simplicial HNSW treatment

But that is not the implementation target for the present package stage.

For now, the working design stance is:

- retain enough quotient and coset structure to make edge-level reward aggregation meaningful
- reason at the level of graph edges and their induced composition
- leave the fuller simplicial or higher-categorical development to a later stage or a child library if the project grows that way

## The Intuitive Good Case

The clean motivating case is:

- reward is computed locally on state-action-state transitions

That is:

```text
r_t = R(s_t, a_t, s_{t+1})
```

If the reward rule has this form, then quotient-level reward is easy to define statistically.

For a quotient edge, one can aggregate over the represented fine transitions using:

- empirical mean reward
- empirical reward distribution
- confidence intervals
- weighted estimates
- min/max bounds
- other summary statistics

This is the core situation in which direct image or quotient-level reward descent is natural.

## How We Arrived At The Current Criterion

The design discussion moved through several clarifications.

### 1. The starting intuition

The starting intuition was:

- rewards ought to aggregate to lower tiers
- modulo rewards being computed in a "reasonable" way

That raised the question:

- what exactly counts as reasonable?

### 2. Rejecting the wrong reasoning surface

An early mistake was to reason as though:

- reward knowledge only arrives through exploration
- the key problem is descending reward from a fully known fine graph

That surface was corrected.

The correct picture is:

- the graph may be hidden
- the reward rule may still be globally known

So the question became:

- not whether the reward is known edge by edge already
- but whether the known reward rule is local enough to be compatible with quotient aggregation

### 3. Noticing the RL-training constraint

The next important move was noticing that not all theoretically possible reward functions are equally relevant.

Some very complicated reward schemes are not just awkward for quotient descent.

They are already awkward for the kind of mainstream RL training pipeline the package wants to remain compatible with.

In particular, very long-range, highly global, or history-heavy reward definitions are often poor fits for ordinary backprop-trained policy learning unless heavily engineered.

So the question narrowed again:

- not "what rewards are possible in principle?"
- but "what rewards lie in the region where mainstream RL training still makes sense, and quotient aggregation still makes sense?"

### 4. The criterion that emerged

That is how we arrived at:

> Reward should be Markov-local or near-Markov-local with respect to the modeled state used by training.

This is the largest natural working region currently visible.

## What "Markov-Local" Means Here

Markov-local does not mean:

- local with respect to ultimate physical reality
- local with respect to some omniscient simulator state the package never sees

It means:

- local with respect to the modeled state surface that the package actually uses for training and control

So if the modeled state is `\tilde{s}_t`, then Markov-local reward means something like:

```text
r_t = R(\tilde{s}_t, a_t, \tilde{s}_{t+1})
```

or equivalently that the training-relevant reward at time `t` is determined by the current modeled transition record.

This is the right locality notion for the package because:

- the package builds graph structure over modeled states
- contraction and quotienting act over modeled states
- training also acts over modeled states

So reward locality must be judged at that same representational layer.

## What "Near-Markov-Local" Means Here

Near-Markov-local means:

- reward is not strictly a function only of the immediate modeled transition
- but it can be made local by a modest and explicit augmentation of modeled state

Examples:

- reward depends on a short fixed action window
- reward depends on the last `k` visited modeled states
- reward depends on whether a short local flag has been set
- reward depends on a bounded local memory summary

In such cases, one can enlarge modeled state so that the augmented state restores locality.

Then reward becomes Markov-local relative to the augmented modeled state, even if it was not local relative to the smaller original one.

This is why the answer is not just "strictly Markov-local."

The package should probably support the larger class:

- naturally Markov-local rewards
- near-Markov-local rewards that can be made local by controlled state augmentation

## Why This Region Is The Right One

This reward class is the natural target because it satisfies two requirements at once.

### Requirement 1: mainstream RL compatibility

Mainstream RL training usually assumes or works best when reward behaves locally relative to the state used for policy learning.

That is the regime in which things like:

- transition tuples
- rollouts
- value estimation
- replay
- policy-gradient updates

all remain relatively standard and interpretable.

### Requirement 2: quotient-level reward descent

If reward is local at the modeled-state level, then quotient nodes and quotient edges can inherit reward structure by aggregating over the represented transition families.

That makes quotient-level reward a natural statistical summary rather than a conceptual distortion.

So this region is not arbitrary.

It is the overlap region where:

- standard RL training remains natural
- quotient-level aggregation remains natural

## The Easy Case

The easiest class is:

```text
r_t = R(\tilde{s}_t, a_t, \tilde{s}_{t+1})
```

with no other dependencies.

In that case:

- each explored transition carries a reward value or reward rule
- quotient edges represent families of such transitions
- quotient rewards can be formed by aggregation

This is the cleanest setting for the package.

The quotient edge can carry:

- average reward
- a reward histogram or empirical distribution
- uncertainty estimates
- per-representative reward traces if needed

This case is the strongest initial target for implementation.

This should be read together with the current categorical scope restriction:

- the package is presently targeting reward that decorates graph edges and edge-composition structure
- not a full higher-path or simplicial reward calculus

## The State-Augmentation Case

A slightly larger but still manageable region is:

- reward depends on a bounded short context
- that context can be encoded into modeled state without blowing up the representation too badly

Examples:

- short history window
- local mode bit
- recent note/annotation signal
- bounded countdown or timer

Then the package can say:

- enlarge modeled state
- rebuild or reinterpret the graph over the augmented state
- recover locality there

This keeps quotient reward descent possible, though at greater structural cost.

The main cost is:

- the state graph becomes larger
- contraction decisions become more expensive
- tower construction may become more complex

But conceptually the system still works.

## The Borderline Region

The boundary becomes blurry when reward depends on context that is:

- longer than a small bounded window
- partially episode-global
- not easily compressible into a stable local summary

Here the package may still be able to function, but only with more elaborate engineering.

This is the region where questions arise like:

- how much history must be folded into modeled state?
- can the relevant history be summarized without losing reward semantics?
- is the resulting modeled state still reasonable for graph construction and contraction?

This is not immediate failure, but it is the beginning of the limit.

## The Hard Region

The hard region includes reward rules like:

- reward if you eventually do `X` after `Y`
- reward only if this is the first time in the episode
- reward based on cumulative patterning over a long segment
- reward based on a global episode property that is not encoded locally

These are not merely inconvenient.

They undermine the clean quotient-reward story because the reward is no longer naturally attached to a local modeled transition.

In such cases:

- a quotient edge does not have a canonical reward by direct aggregation
- a reward attached to a representative transition may depend on long-range context not preserved at the quotient edge level
- naive coarse reward can become misleading

This is also often the region where straightforward backprop-based policy training is already becoming more awkward.

So this is the point where the package should likely stop claiming that direct quotient-level reward descent is natural.

## The Practical Limit

The practical limit can therefore be stated as:

> Direct quotient-level reward aggregation is natural only so long as reward is localizable to the modeled transition objects used by training, either immediately or after modest explicit state augmentation.

Beyond that point:

- quotient reward may still be definable in some looser sense
- but it is no longer a clean direct-image reward
- and the connection to standard RL training surfaces becomes weaker

This is the operational boundary the package should probably respect.

## Why This Is A Package-Design Constraint

This is not just a theoretical observation.

It should directly shape implementation decisions.

### 1. Modeled state must be explicit

If reward locality is judged relative to modeled state, then modeled state cannot remain vague.

The package must define it clearly.

### 2. Reward contracts must be explicit

The package should know whether a reward rule is:

- Markov-local
- near-Markov-local via augmentation
- outside the target class

This should not be left implicit.

### 3. Quotient-edge reward summaries should be statistical objects

For local reward settings, quotient reward should probably not be stored only as one scalar.

Often it should be capable of carrying:

- empirical mean
- count
- variance
- confidence interval
- possibly the full empirical distribution

### 4. The package should not overpromise on arbitrary reward functions

It is better to explicitly support the right reward class than to pretend every RL reward surface naturally descends through quotienting.

## Proposed Reward Taxonomy

The package should likely classify reward rules into at least these categories:

1. **Local reward**
   - depends on modeled `(state, action, next_state)`
   - clean quotient aggregation

2. **Augmentably local reward**
   - depends on bounded context
   - becomes local after explicit modeled-state augmentation

3. **Weakly nonlocal reward**
   - depends on more context than is comfortable
   - quotient aggregation becomes conditional or approximate

4. **Strongly nonlocal reward**
   - depends on long-range or global episode properties
   - direct quotient descent is not a clean fit

This taxonomy would be useful both conceptually and in code.

## Recommended Initial Package Stance

The initial implementation stance should likely be:

- strongly optimize for local reward
- explicitly support augmentably local reward
- document weakly nonlocal reward as experimental or approximate
- avoid claiming clean support for strongly nonlocal reward in early versions

This gives the package a clear and defensible target region.

## Connection To The Larger Architecture

This reward-locality criterion fits well with the rest of the current design:

- modeled states are explicit
- notes and annotations can become part of modeled state if needed
- contraction carries coset and transition-family data
- quotient levels can store statistical reward summaries
- hierarchical training stays recognizable as RL

So this is not an isolated design fact.

It is one of the main joints holding the whole package together.

## Final Statement

The current best answer to the reward question is:

> The largest natural class of reward rules for `state_collapser` consists of RL problems where reward is Markov-local or near-Markov-local with respect to the modeled state used by training.

This is the region where:

- mainstream RL training still makes sense
- quotient-level aggregated reward still makes sense
- tower construction remains structurally meaningful

That is the reward regime the package should treat as its primary design target.
