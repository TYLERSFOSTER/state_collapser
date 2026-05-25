# Model And Training Surface Architecture

## Status

This document is the first architecture note devoted specifically to:

- model surfaces
- training surfaces
- training-loop ownership
- ML-engineer-facing composability

inside `state_collapser`.

It is motivated directly by the current `README.md` TODO item:

- `Policy model integration`

but it is intentionally broader than that one phrase.

This document is not:

- an implementation gameplan
- a benchmark protocol
- a specific learner blueprint
- a neural-network selection recommendation

Its purpose is to establish what a professional and serious training/model surface should look like for this package.

## Why This Document Exists

The repo now contains:

- real environment packages
- real runtime surfaces
- real tower construction logic
- real tower-aware training loops
- a first exploit/explore controller

But the current training story is still narrow and example-local.

In particular, the package is approaching a point where an outside engineer will naturally ask:

- where does my model plug in?
- what part of the package owns the training loop?
- what if I want to use a transformer on one environment and a CNN on another?
- what if I am not training a literal policy `\pi_\theta`, but rather a `Q_\theta`, `V_\theta`, or actor-critic pair?
- what is the package surface for serious ML engineering work, rather than for only the current example-local tabular loops?

This document addresses that question.

## Prompting Source

The immediate design pressure behind this note came from a discussion with the Project Owner about:

1. the `README.md` TODO item on policy-model integration
2. the fact that in RL the trainable object is not always literally a policy `\pi_\theta`
3. the practical reality that serious ML engineers usually do **not** want a very rigid master training loop
4. the stronger idea that a good package should expose:
   - the component parts of training as clean surfaces
   - while leaving the training loop itself easy for the engineer to author

That last point is the center of gravity of this document.

## PO-Originated Design Claims

For clarity, several of the most important architectural claims in this document were introduced directly by the Project Owner rather than first proposed here by the LLM.

The most important PO-originated claims are:

### 1. The package should not over-own the training loop

The strongest claim introduced by the PO was that, from a serious ML-engineering perspective, the training loop itself should usually remain something the engineer authors.

What the package should provide instead is:

- strong component surfaces
- clean contracts
- swappable parts

rather than one highly rigid master training framework.

This idea is the single most important design input in the entire note.

### 2. The package boundary must be broader than literal policy models

The PO explicitly raised the issue that in RL the trained object is not always a literal:

\[
\pi_\theta(a\mid s).
\]

The PO also explicitly raised `Q_\theta`-style alternatives and pressed on the fact that a narrow "policy only" interface would be architecturally misleading.

So the move away from:

- a policy-only model surface

toward:

- a broader action-decision or decision-surface model boundary

is not just a generalization introduced by the LLM; it is directly responsive to a PO-supplied design constraint.

### 3. The package should expose the parts of training, not one official choreography

The PO’s formulation was not merely "make training pluggable."

It was more specific:

> it is much more useful to have all the component parts of a training loop as nice surfaces, but the loop itself something the engineer makes.

This is stronger than ordinary modularity language.

It implies that the architectural center of gravity should be:

- component contracts
- decision boundaries
- collector/update/buffer/metrics surfaces

rather than:

- top-down orchestration ownership

by the package.

### 4. The motivating standard is serious ML engineering practice

The PO also explicitly framed the question in terms of:

- what serious or professional ML engineers actually want

rather than:

- what a simplified research-demo API might expose

That framing matters, because it is what drives the emphasis in this document on:

- composability
- swappability
- typed intermediate surfaces
- and freedom to write custom loops

instead of a package-owned "one true trainer."

### 5. The question is really about surface design, not just model choice

The initial README TODO item speaks in terms of:

- policy model integration

But the PO clarified that the deeper question is not only:

- "How do I swap one model for another?"

It is:

- "What are the right package surfaces for serious ML engineering work?"

That clarification is what justifies the much broader scope of this note.

## LLM Synthesis Boundary

For additional clarity, the parts of this document that are primarily LLM synthesis rather than direct PO introduction are things like:

- the proposed surface taxonomy
  - problem surface
  - decision-input surface
  - action-decision surface
  - transition surface
  - collector surface
  - learner/update surface
  - replay/batch surface
  - metrics surface
  - reference-loop surface
- the suggested top-level package shape under `state_collapser/training/`
- the more general mathematical notation
  - `\mathcal{M}_\theta : \mathcal{X}_H \to \mathcal{D}_H`

Those are attempts to formalize and organize the design pressure introduced by the PO.

They should therefore be read as:

- architectural synthesis under PO direction

not as the original source of the document’s core motivation.

## Executive Summary

The central design claim of this document is:

> `state_collapser` should expose strong, typed, composable model/training **surfaces**, but should avoid over-owning the actual training **loop**.

More concretely:

- the package should **not** prematurely harden around one official training orchestration framework
- the package should **not** assume the learned object is always a literal policy distribution
- the package **should** expose clean contracts for:
  - decision input
  - action-decision output
  - rollout collection
  - transition recording
  - learner/update logic
  - replay/batching
  - metrics/instrumentation
- the package **should** provide a few reference loops
- but the package should still leave engineers free to author their own training loops without fighting the library

This is much closer to how serious ML engineering actually works.

## What The Repo Currently Does

Before deciding what the training/model surfaces should become, we should state clearly what they are **right now**.

### 1. Training is currently example-local

At present, the main training entrypoints live in example packages such as:

- `src/state_collapser/examples/plate_support_env/training.py`
- `src/state_collapser/examples/rl_counterpoint_v3/training.py`

These are real and useful, but they are not yet a package-wide training architecture.

### 2. Most current training is tabular

The dominant current pattern is:

- tabular Q-learning
- epsilon-greedy action selection
- Q-tables implemented as Python dictionaries

For example, the current `run_tower_training(...)` loops:

- build an example runtime
- reset an episode
- use the current runtime snapshot as a state key
- select an action epsilon-greedily
- step the runtime
- apply a one-step TD update to a Q-table

This is a valid first vertical slice, but it is not yet a general model surface.

### 3. The current "learned state" is often a tower-position key

The current tower-aware training loops frequently define the learning key as something like:

- `tuple(snapshot.current_position_at_every_tier)`

This means the learned object is effectively:

- `Q(\text{tower-position-key}, a)`

That is a perfectly reasonable first slice, but it is still:

- tabular
- example-local
- and not yet generalized to trainable ML models

### 4. The closest thing the repo has to a reusable learner surface is `TierLearner`

The most reusable training-facing contract in the repo right now is:

- `src/state_collapser/tower/control/learner.py`

which defines the `TierLearner` protocol with methods like:

- `behavior_action(...)`
- `observe(...)`
- `should_train(...)`
- `train(...)`

This is important because it already points in the right direction:

- the learner is treated as a component
- the controller/runtime orchestrates around it
- the learned object is not hardcoded into the runtime itself

But even here:

- the current concrete learner is still tabular
- the contract is scoped to active-tier exploit/explore control
- it is not yet the package-wide training/model abstraction

### 5. There is currently no general pluggable model interface

At present, the package does **not** have a stable surface for:

- plugging in a CNN
- swapping to a transformer
- using `Q_\theta` instead of `\pi_\theta`
- actor-critic style training
- history-conditioned models
- masked action-scoring models

This is exactly the gap the `README.md` TODO is pointing toward.

## Why The "Policy Model" Framing Is Too Narrow

The current README TODO uses the language of policy models and writes, roughly speaking, in the direction of:

\[
\pi_\theta : \mathcal{S}_H \longrightarrow \mathcal{P}(\mathcal{A}_H \mid \mathcal{S}_H).
\]

That is a useful starting point, but it is too narrow to serve as the package’s real architectural boundary.

### The problem

In RL, the trainable object is not always a literal policy of the form:

\[
\pi_\theta(a \mid s).
\]

Very often, what is trained instead is:

- an action-value function `Q_\theta(s,a)`
- a state-value function `V_\theta(s)`
- an actor-critic pair
- a model that returns action logits rather than normalized probabilities
- a history-conditioned next-action scorer
- a model whose output becomes a decision surface only after masking, argmax, sampling, or other post-processing

So if the package’s training/model boundary were specified only as:

\[
\mathcal{M}_\theta : \mathcal{S}_H \to \mathcal{P}(\mathcal{A}_H),
\]

that would exclude or awkwardly distort many serious RL methods.

### The correction

The right abstraction is not:

- "policy model"

but something more like:

- "action-decision model"

or:

- "decision-surface model"

The package needs to be able to say:

> a model consumes some package-defined decision input and returns enough structured information to support action choice and learning

That returned information might be:

- probabilities
- logits
- Q-values
- actor/value heads
- masked action scores
- a sampled action plus diagnostics

So the correct design target is a broader model surface than literal `\pi_\theta`.

## Why A Rigid Package-Owned Training Loop Is The Wrong Goal

The Project Owner made a strong and important point:

> In real ML engineering, it is usually much more useful to have all the component parts of a training loop as nice surfaces, while leaving the loop itself something the engineer makes.

This is exactly right.

### Why this matters

A training loop is often "just a loop," but the loop sits on top of a large number of moving parts:

- reset
- rollout
- action selection
- reward handling
- replay/storage
- learner update
- target-network updates maybe
- evaluation hooks
- logging/metrics
- checkpointing

What engineers actually need to swap is often not:

- the whole training system

but rather:

- the model
- the update rule
- the collector
- the replay/batching scheme
- the logging/evaluation hooks
- the runtime interpretation layer

If the package over-owns the training choreography, it becomes harder, not easier, to do serious experimental engineering.

### Why this is especially true for `state_collapser`

`state_collapser` is not just another generic RL trainer.

Its distinctive value lies in:

- hidden-graph structure
- explored/vista graph layers
- tower construction
- runtime snapshots
- quotient tiers
- active-tier control surfaces
- instrumentation around tower behavior

That means the package should own:

- the problem/runtime/tower special sauce

but it should be very careful about over-owning:

- the exact training loop engineers must use

This is analogous to what `gymnasium` does well:

- it gives you a standard environment boundary
- it does **not** force one single training worldview

That is a good model for `state_collapser`.

It is worth recording that this entire anti-rigid-loop section is not merely a general design preference imported from elsewhere.

It is a direct response to the PO’s explicit claim that, in serious ML engineering, one usually wants the training components exposed as strong surfaces while the training loop itself remains something the engineer writes.

## Why Top-Level Folders For "Three Kinds Of RL" Are Probably The Wrong First Cut

One proposed direction was:

- perhaps create one folder per major RL learning family

for example:

- policy learning
- Q-learning
- actor-critic

That is understandable, but it is probably too rigid too early.

### Why this is not the best first decomposition

Organizing the package first by RL method family risks freezing a taxonomy before the package has clarified its true extension points.

The better decomposition is probably by **surface role**, not by **algorithm-school label**.

From an ML engineer’s perspective, the important reusable pieces are more like:

- what input the model sees
- what output the model returns
- how rollout is collected
- what transition object is emitted
- how learning updates are performed
- how metrics are produced

This section is also answering a concrete PO-raised prompt rather than only drifting into abstract package taxonomy.

The PO explicitly floated the idea of one folder per major RL family and then, in the same discussion, redirected toward the deeper question of what the right reusable surfaces really are.

So the move away from top-level algorithm-family folders and toward surface-role decomposition should be read as a direct answer to that PO pressure.

Method families can then sit inside one of those roles, rather than determining the whole directory structure from the start.

## The Core Architectural Principle

The central principle of this document is:

> The package should expose **component contracts**, not one official training choreography.

That means:

- strong type surfaces
- strong runtime data objects
- strong adapter boundaries
- easy model-swapping
- easy loop authorship
- a few reference loops
- but no over-rigid "one true training engine"

## Recommended Surface Taxonomy

The following surfaces are the ones I currently believe matter most.

### 1. Problem Surface

This is the layer that answers:

- what RL problem is being trained on?

It should include:

- environment
- hidden graph
- runtime
- reset/step results
- reward/termination surface
- action/observation translation

This is already partly present in the repo.

Examples:

- `env.py`
- `runtime.py`
- `TowerRuntime`
- `RuntimeSnapshot`

This is the package’s existing strength.

### 2. Decision-Input Surface

This is one of the most important missing pieces.

A serious package should not make each learner/model reach deep into raw runtime internals ad hoc.

Instead, it should define a deliberate input object for action selection and/or learning.

Depending on method, that input might include:

- raw env observation
- current base state
- current tower-position tuple
- active-tier state
- frozen lower context
- action mask
- short history window
- tower metadata

The key design point is:

- the package should decide what a clean model-facing input object looks like
- instead of forcing every engineer to reverse-engineer it from runtime internals

Candidate name:

- `ActionSelectionInput`

This is better than `PolicyInput`, because the surface must support more than literal policies.

### 3. Action-Decision Surface

This is the output-side complement to the decision-input surface.

The package should not require every model to return only:

- a policy distribution

Instead, it should support a structured "decision output" object that can carry things like:

- action probabilities
- action logits
- Q-values
- sampled action
- greedy action
- action mask
- value estimate
- actor/value diagnostics

Candidate name:

- `ActionDecision`

This would allow the package to support multiple RL styles without forcing all of them into a fake `\pi_\theta` shape.

### 4. Transition Surface

This should be a first-class package object.

Not just:

- `(s, a, r, s')`

but a richer typed transition record that can include:

- decision input
- chosen action
- reward
- next decision input
- terminated/truncated flags
- tower metadata
- active tier
- frozen-context version
- diagnostics

This object becomes the lingua franca between:

- rollout
- replay/storage
- learner/update logic
- evaluation

Candidate name:

- `TrainingTransition`

### 5. Rollout / Collector Surface

The package should expose a collector surface that owns:

- stepping env/runtime
- gathering transitions
- packaging trajectory fragments
- optionally attaching tower/control metadata

But it should not force one giant rollout engine.

Different engineers may want:

- online single-step collection
- episode collection
- active-tier exploit/explore collection
- custom metadata capture

Candidate names:

- `Collector`
- `EpisodeCollector`
- `ActiveTierCollector`

The collector layer is where loop-building convenience should come from without forcing total orchestration.

### 6. Learner / Updater Surface

This must stay distinct from the model itself.

That distinction is professionally important.

The model is:

- a parameterized function approximator

The learner/updater is:

- the algorithm that updates it

Examples:

- tabular Q updater
- DQN-style updater
- policy-gradient updater
- PPO-style updater
- actor-critic updater

The existing `TierLearner` protocol already points in this direction, but it is too narrow and active-tier-specific to be the whole long-term answer.

What should happen eventually is:

- a broader learner/updater surface
- with method families implemented under it
- while still allowing the active-tier learner to remain a special-case higher-level controller-facing contract if needed

### 7. Replay / Batch Surface

Some methods need:

- online one-step updates

Others need:

- replay buffers
- sequence batches
- on-policy rollout batches

This should be modular and swappable, not hidden inside one training engine.

Candidate names:

- `TransitionBuffer`
- `ReplayBuffer`
- `TrajectoryBatch`
- `SequenceBatch`

The key design requirement is:

- the transition/batch layer must not assume one algorithm family

### 8. Metrics / Instrumentation Surface

For this repo, this layer is more important than in many generic ML libraries.

Because `state_collapser` makes structural claims, engineers will want to inspect things like:

- episodic return
- success rate
- tower depth
- contraction behavior
- active-tier traces
- path-space metrics
- quotient-structure growth

This means metrics and instrumentation should not be bolted on as an afterthought.

They should be exposed as clean hooks or reporters usable by custom loops.

Candidate surfaces:

- `TrainingMetrics`
- `TowerMetrics`
- `CollectorMetrics`
- callback/hook protocol for reporting

### 9. Reference Loop Surface

The package should probably provide a few reference loops.

That is useful.

But they should be:

- examples
- templates
- minimal working orchestration surfaces

not:

- the one official training framework all users are expected to adopt

That distinction matters a great deal.

The package should help engineers write loops, not trap them inside one.

## Recommended Top-Level Package Shape

The most professional first move is probably something like:

```text
src/state_collapser/training/
    __init__.py
    inputs.py
    decisions.py
    transitions.py
    collectors.py
    metrics.py
    learners/
    buffers/
    reference_loops/
```

This is intentionally organized by **surface role**.

Not by:

- policy-gradient vs Q-learning vs actor-critic

Those method families would more naturally live under:

- `learners/`

or perhaps a later:

- `algorithms/`

subtree if that becomes useful.

## Recommended Division Of Responsibility

The professional long-term split should probably look like this:

### `gymnasium.Env`

Owns:

- raw RL problem dynamics
- raw reward/termination shell
- action/observation spaces

### `state_collapser` problem/runtime layer

Owns:

- hidden graph
- explored graph
- vista graph
- tower construction
- runtime snapshots
- active-tier control surfaces
- package-facing structural instrumentation

### training component layer

Owns:

- decision inputs
- decision outputs
- rollout collection
- transition recording
- learner/update interfaces
- replay/batching interfaces
- metrics hooks

### engineer-authored loop

Owns:

- orchestration order
- update schedule
- evaluation schedule
- checkpointing choices
- algorithm-specific control flow

This is the balance I think a serious ML engineer would actually respect.

## A Better Mathematical Framing Of The Model Surface

The README currently gestures toward something like:

\[
\pi_\theta : \mathcal{S}_H \to \mathcal{P}(\mathcal{A}_H \mid \mathcal{S}_H).
\]

That is not wrong, but it is too narrow for the architecture.

The more general package-facing mathematical picture should be something like:

\[
\mathcal{M}_\theta : \mathcal{X}_H \longrightarrow \mathcal{D}_H
\]

where:

- `\mathcal{X}_H` is a package-defined decision-input space
- `\mathcal{D}_H` is a package-defined action-decision surface

Here:

- `\mathcal{X}_H` might be built from:
  - state
  - history
  - tower context
  - active tier
  - frozen lower context
  - masks

and:

- `\mathcal{D}_H` might carry:
  - probabilities
  - logits
  - Q-values
  - sampled actions
  - value heads
  - diagnostics

Then:

- a literal policy model is just one special case
- a Q-model is another special case
- actor-critic is another special case

This gives the package a mathematically honest and professionally useful boundary.

## How Environment-Specific Model Swapping Should Feel

The motivating usability question was something like:

> What if an engineer decides, in the middle of working on an RL problem using `state_collapser`, "I want to use a transformer instead of this CNN"?

The right package answer should be:

- the engineer should not have to rebuild the RL problem
- the engineer should not have to rewrite tower construction
- the engineer should not have to rewrite the whole runtime
- the engineer should swap:
  - the model
  - perhaps the decision-input adapter
  - perhaps the learner/update component

but the rest of the problem/runtime stack should remain stable

This means the package boundary between:

- problem/runtime

and:

- model/learner/collector

must be clean and deliberate.

This model-swapping story is also directly rooted in the PO’s concrete motivating scenario:

- an engineer working on one RL problem inside `state_collapser`
- deciding midstream to use a transformer instead of a CNN

That scenario is part of why this document insists that model replacement should not force the engineer to rebuild the underlying RL problem or the tower/runtime machinery.

## Relation To Current Example Loops

The current example loops should not be viewed as mistakes.

They are useful first vertical slices.

But they should be understood as:

- reference loops
- minimal smoke loops
- early validation harnesses

not:

- the final package-wide training architecture

This distinction should remain explicit as the repo grows.

## What A Serious ML Engineer Is Likely To Want

From a professional ML engineering perspective, the package should ideally provide:

1. clear problem/runtime boundaries
2. explicit decision-input objects
3. explicit action-decision objects
4. explicit transition records
5. pluggable collectors
6. pluggable learners/updaters
7. pluggable replay/batch surfaces
8. strong metrics and instrumentation hooks
9. optional reference loops
10. freedom to author custom training loops cleanly

What such an engineer does **not** usually want is:

- a giant opaque training engine they have to bend around

unless the package is explicitly a trainer framework

and `state_collapser` should probably not define itself that way.

## Recommended Immediate Architectural Direction

The next clean architectural move is probably:

1. keep current example-local loops as reference surfaces
2. do **not** rush into one master trainer
3. design the package-level training component contracts first
4. especially define:
   - decision-input
   - action-decision
   - transition
   - learner/update
   - metrics hooks
5. only then introduce a new `state_collapser.training` package
6. populate it with reusable parts plus a few reference loops

That direction would let the package mature professionally without prematurely trapping itself in a rigid orchestration model.

## Non-Goals

This document does **not** yet decide:

- the exact shape of the future neural model APIs
- whether PyTorch should be the first ML backend
- whether JAX or TensorFlow support matters
- exact replay-buffer implementation details
- whether actor-critic should be prioritized over value-based learners

Those are later design questions.

The current document is about:

- the shape of the package boundary
- and who should own the training loop

## Bottom Line

The repo should move toward:

- **professional component surfaces**
- **package-owned runtime/tower structure**
- **engineer-authored loops**

not toward:

- one over-rigid package-owned training choreography

The right long-term architecture is:

- `state_collapser` owns the structural machinery
- `state_collapser` exposes strong training/model surfaces
- the engineer remains free to compose those surfaces into the loop they need

That is the design I believe best fits:

- the current repo reality
- the `README.md` TODO
- the mathematical scope of the package
- and the expectations of serious ML engineers.

## Next Document

The next document after this one should probably be either:

1. a surface blueprint for `src/state_collapser/training/`

or:

2. a narrower contract note just for the first two missing pieces:
   - decision-input surface
   - action-decision surface

Those are the most foundational next moves.

## Contemporary RL Practice Cross-Check

This section records a more serious external reality check against contemporary RL tooling and engineering practice.

The goal here is not to prove that the exact proposal in this document is already standard everywhere.

It is instead to answer questions like:

- would a serious RL engineer recognize these as sensible surfaces?
- do current RL frameworks expose analogous boundaries?
- is the proposal too idiosyncratic relative to industry or research engineering practice?
- how well do `gymnasium` and `ROS 2` fit the picture?

The short answer is:

> Yes, most of the proposed surfaces are recognizably professional and contemporary, but they need to be refined in a few practical directions if they are to feel truly production-grade to experienced RL engineers.

## High-Level Verdict

At a high level, the document’s architecture matches contemporary RL practice better than a package-owned monolithic training loop would.

In particular, the following broad instincts align well with serious RL engineering:

- keep the environment boundary clean
- separate acting/collection from learning/updating
- treat replay/batching as a first-class component
- treat metrics/logging as a first-class component
- allow the trainable object to be broader than a literal policy distribution
- avoid forcing one single training choreography on all users

Those are not eccentric ideas.

They are strongly reflected, in different styles, across modern RL libraries.

## Evidence From Contemporary RL Tooling

### 1. Clean environment boundaries remain standard

`gymnasium` still centers the environment contract around:

- `reset(...)`
- `step(...)`
- wrappers for modification/extension
- vector-environment construction

This strongly supports the idea that `state_collapser` should not collapse env semantics into training semantics.

The package’s current instinct:

- keep the env as the problem shell
- layer tower/runtime machinery on top

is therefore consistent with contemporary convention rather than opposed to it.

### 2. Modern RL stacks do expose intermediate training surfaces

Current RL frameworks often introduce explicit intermediate surfaces between:

- env
- model
- learner
- replay
- metrics

For example:

- RLlib explicitly uses env-to-module connector pipelines between the environment and the model-facing batch surface.
- RLlib also exposes replay buffers, metrics loggers, and distinct environment-runner / learner-side concepts.
- Tianshou explicitly splits training into policy/algorithm, collector, replay buffer, and trainer concepts.
- Acme explicitly separates actor, learner, environment loop, adders, replay, and dataset-facing learner inputs.

This matters because it means the surface-oriented decomposition proposed in this document is not alien.

It is much closer to current practice than a simplistic "env plus one giant trainer" architecture would be.

### 3. Contemporary libraries do not all insist on one rigid loop

There is variation here.

Some frameworks are more orchestration-heavy:

- Stable-Baselines3 exposes a more algorithm-owned training flow where you instantiate an algorithm class with a policy and an env, then call `.learn(...)`.

Some are more modular:

- Acme explicitly describes actors, learners, environment loops, adders, and replay as separate pieces.
- Tianshou explicitly exposes collectors and buffers as components.
- RLlib exposes connector pipelines and replay/learner machinery as independent parts of the stack.

And some lean very strongly into engineer-authored or reference loops:

- CleanRL emphasizes single-file algorithm implementations and deliberately does not position itself as a modular import-first training framework.

This is important because it shows the PO’s intuition was not outside contemporary practice.

If anything, the repo’s desired direction sits in a serious and respectable middle:

- stronger reusable surfaces than CleanRL
- less training-loop rigidity than a fully algorithm-owned framework

That is a coherent place to aim.

## Surface-By-Surface Evaluation

What follows is a more direct judgment of the proposed surfaces from a serious RL engineer’s perspective.

### 1. Problem Surface

Verdict:

- strongly aligned with standard practice

Why:

- modern RL systems almost always keep a clear problem/environment boundary
- `gymnasium` in particular reinforces this
- `state_collapser` adding runtime and tower structure on top of that boundary is unusual, but not professionally strange

What is good:

- env remains primary problem shell
- runtime is a separate structural layer
- hidden-graph/tower machinery stays package-owned

What still needs refinement:

- clearer story for vectorized envs
- clearer statement of what is public and stable in runtime snapshots

Overall:

- a serious RL engineer would recognize this as a solid boundary

### 2. Decision-Input Surface

Verdict:

- highly aligned with modern practice, and probably essential

Why:

- RLlib’s env-to-module connectors are direct evidence that serious frameworks treat the transformation from environment data to model-readable input as its own layer
- Acme and Tianshou also effectively rely on explicit or implicit intermediate input packaging

What is good:

- this surface solves the `\pi_\theta` vs `Q_\theta` vs actor-critic problem
- it provides the right place to insert tower metadata, frozen lower context, masks, or history windows

What still needs refinement:

- this surface will need a very careful distinction between:
  - inference input
  - training input
  - recurrent/history-conditioned input
- device / dtype / tensorization questions are not yet addressed

Overall:

- yes, a serious RL engineer would be happy to see this surface
- in fact, many would expect something like it

### 3. Action-Decision Surface

Verdict:

- strongly aligned with modern practice

Why:

- modern systems often have to carry more than a sampled action
- the output may be:
  - logits
  - probabilities
  - Q-values
  - value estimates
  - masks
  - diagnostics

This is especially compatible with:

- RLlib-style module outputs
- actor-critic systems
- masked action-selection systems

What is good:

- it avoids overcommitting to a literal policy distribution
- it supports both acting and learning

What still needs refinement:

- the package will need a precise decision about whether:
  - action selection itself happens inside the model surface
  - or is a separate downstream selection rule from scores/logits/values

That is a real design choice.

Overall:

- this is a professional and contemporary surface

### 4. Transition Surface

Verdict:

- absolutely standard in spirit, though the package’s tower metadata will make it richer than average

Why:

- every serious RL stack ends up standardizing transition or batch objects somehow
- Acme learners consuming transition tuples or sequences and Tianshou collectors writing to replay buffers both reflect this clearly

What is good:

- the proposal makes transition records first-class rather than implicit
- this is exactly the right place to include tower-specific metadata

What still needs refinement:

- need a decision about whether the canonical unit is:
  - single transition
  - n-step transition
  - sequence fragment
  - episode fragment
- serious RL engineers will also want stable serialization rules

Overall:

- yes, this surface is very aligned with contemporary practice

### 5. Rollout / Collector Surface

Verdict:

- very strongly aligned with modern RL engineering

Why:

- Tianshou’s `Collector` is explicit evidence for this
- Acme’s actor/environment loop plus adders is another strong analogue
- RLlib’s environment runners also play a related role

What is good:

- making collection its own surface is one of the most professional parts of the proposal
- it prevents env stepping, metric capture, and learner updates from collapsing into one big opaque loop

What still needs refinement:

- collector APIs usually need very explicit semantics for:
  - stopping conditions
  - episode vs step quotas
  - vector env behavior
  - exploration vs evaluation mode

Overall:

- a serious RL engineer would absolutely recognize and appreciate this surface

### 6. Learner / Updater Surface

Verdict:

- strongly aligned with best practice

Why:

- separating model from learner/update logic is standard and important
- Acme’s actor/learner split is direct evidence for this kind of thinking
- RLlib’s learner-side machinery also supports this view

What is good:

- it lets `state_collapser` remain agnostic about whether the learning rule is:
  - Q-learning
  - actor-critic
  - PPO-style
  - imitation-style

What still needs refinement:

- the package should eventually decide whether "learner" means:
  - one update object per algorithm family
  - or a lower-level update-step protocol

Overall:

- this is a serious, contemporary surface

### 7. Replay / Batch Surface

Verdict:

- strongly aligned with current practice

Why:

- replay buffers are explicit, configurable components in RLlib
- replay buffers are explicit in Tianshou
- Acme’s adders plus Reverb-backed replay are another strong example

What is good:

- the proposal does not assume all methods are online one-step learners
- it leaves room for:
  - replay
  - sequences
  - offline data

What still needs refinement:

- a serious engineer will expect clarity around:
  - ownership of memory
  - batch shapes
  - device transfer
  - sampling semantics
  - prioritization if supported

Overall:

- yes, this is a highly standard and expected component

### 8. Metrics / Instrumentation Surface

Verdict:

- strongly aligned with good practice, and unusually important for this repo

Why:

- most serious RL systems have extensive logging, metrics, and evaluation hooks
- RLlib explicitly exposes metrics logging machinery
- Stable-Baselines3, Acme, and CleanRL all have strong logging/evaluation stories in different forms

What is good:

- because `state_collapser` makes structural claims, its instrumentation needs to be first-class
- that is not overkill here; it is part of the product

What still needs refinement:

- engineers will want:
  - clear structured metrics payloads
  - callback/hook semantics
  - distinction between training metrics and evaluation metrics

Overall:

- this surface is not only acceptable; it is necessary

### 9. Reference Loops Instead Of One Master Loop

Verdict:

- this is a credible and professional package stance

Why:

- it is compatible with:
  - Acme’s reusable components and environment loops
  - Tianshou’s collectors and trainers
  - CleanRL’s emphasis on readable loop ownership

What is good:

- it keeps the package flexible
- it avoids premature overcommitment
- it respects the PO’s core engineering intuition

What still needs refinement:

- the package must still offer enough scaffolding that users are not left assembling everything from raw internals

So the right balance is:

- strong reference loops
- strong components
- weak insistence on one orchestrator

Overall:

- this is a serious position, not an amateur one

## Where The Proposal Is Already Strong

Relative to contemporary RL practice, this document is already strong in the following ways:

### 1. It correctly treats env and training as different boundaries

That is standard.

### 2. It correctly generalizes beyond literal policy models

That is necessary for real RL work.

### 3. It correctly treats collection, replay, and learning as separable concerns

That is exactly how many serious libraries think.

### 4. It correctly emphasizes instrumentation

This is especially important for a structural RL package.

### 5. It correctly resists premature top-level organization by algorithm family

That is a mature architectural instinct.

## Where The Proposal Still Needs Professional Hardening

Even though the direction is good, a serious RL engineer would still want several additional practical clarifications before calling the architecture fully professional.

### 1. Vectorization needs to be first-class

Modern RL practice strongly expects:

- multiple environments
- vector envs
- batched collection

`gymnasium` explicitly supports vectorized environments, and many RL frameworks assume them heavily.

So the future training surfaces should explicitly account for:

- single-env vs vector-env decision inputs
- batch-first transition surfaces
- collector semantics over multiple envs

### 2. Tensor/device boundaries need explicit design

A serious ML engineer will immediately ask:

- when do objects become tensors?
- who owns device placement?
- what is NumPy vs PyTorch vs JAX responsibility?

The current document is correctly architecture-first, but it is not yet implementation-hard enough on those questions.

### 3. Batch and sequence semantics need to be explicit

Especially if history-conditioned models are supported, the package will need clear decisions about:

- timestep batch
- transition batch
- n-step batch
- recurrent sequence batch
- episode fragment batch

This is one of the places where professional quality shows.

### 4. State serialization and checkpointing surfaces are still missing

Even if the package avoids a giant training framework, serious engineers will want:

- reproducible learner state
- buffer state if relevant
- collector state if relevant
- metrics snapshots

The architecture does not yet cover that.

### 5. Evaluation-mode surfaces need to be separated cleanly from training-mode surfaces

This will matter for:

- deterministic vs exploratory action selection
- tower-depth probing
- metrics collection
- benchmark reproducibility

The current note points in the right direction, but the split is not yet explicit enough.

## How Well This Proposal Fits Gymnasium

The fit with `gymnasium` is very good.

### Why the fit is strong

`gymnasium` is already built around:

- a clean environment contract
- wrappers for modifying behavior
- vector environments

This matches the proposal’s core assumptions well:

- the env remains primary problem shell
- `state_collapser` sits on top as a structural/runtime layer
- training components live above both

### The best conceptual alignment

The cleanest alignment is:

- `gymnasium.Env`
  - owns raw RL problem dynamics
- `state_collapser` runtime/tower layer
  - owns structural interpretation
- training/model components
  - consume packaged inputs and produce decisions

This is architecturally natural.

### What Gymnasium suggests for `state_collapser`

Because Gymnasium is so env-centered, it supports the PO’s instinct that:

- `state_collapser` should not over-own the whole training world

Instead, it should expose a strong runtime and strong training surfaces over the env.

### Where care is still needed

The package should make sure that tower-specific data remains accessible without making the env itself weird or overloaded.

That means:

- keep env simple
- keep tower/runtime metadata in runtime-side objects
- let training collectors and decision-input builders decide how much of that metadata reaches the model

So overall:

- `gymnasium` integrates very naturally with this proposal

This `gymnasium` comparison is present because the PO explicitly asked whether the proposed loop/component split was consistent with `gymnasium` conventions rather than merely with the LLM’s own sense of software architecture.

## How Well This Proposal Fits ROS 2

The fit with `ROS 2` is more indirect, but still meaningful.

### Why the fit is not as direct as with Gymnasium

`ROS 2` is not an RL environment library.

It is a robotics middleware and execution system organized around:

- nodes
- topics
- services
- actions
- executors

So the relevant question is not:

- "Does ROS 2 already expose these RL surfaces?"

but:

- "Can these surfaces sit cleanly over ROS 2-based problem integrations?"

### What ROS 2 suggests architecturally

ROS 2 strongly reinforces:

- separation of responsibilities
- explicit execution management
- modular computational units

That is broadly compatible with the proposal.

For example, a plausible future robotics integration story is:

- one ROS-facing node or adapter owns real-world or simulator interaction
- a `gymnasium`-like wrapper or env layer exposes the RL problem
- `state_collapser` runtime sits above that
- collectors/learners run in the process topology the engineer wants

That is architecturally credible.

### What the proposal should not assume

The package should not assume that ROS 2 itself becomes:

- the training framework
- the learner API
- the replay API

Instead, ROS 2 should be viewed as:

- a systems integration substrate

over which an environment or adapter may be built.

### Overall ROS 2 judgment

So the fit is:

- not direct in the way Gymnasium is direct
- but still conceptually compatible with the proposal’s emphasis on modular surfaces and explicit ownership boundaries

The inclusion of `ROS 2` here also comes directly from the PO’s prompt.

The purpose of the section is therefore not to force `ROS 2` into the center of the package design, but to answer the PO’s question about whether the proposed training-surface architecture would still look reasonable in robotics-facing integration settings.

## What The Tower Changes, And What It Does Not

One subtle concern in the prompt was:

- the tower introduces a strange new component into RL training
- but because layers freeze and contexts persist, many components should still look like existing RL framework pieces

I think that is exactly right.

### What the tower really changes

The tower mainly changes:

- what decision input may need to contain
- what metadata transitions may need to carry
- what collector/runtime may have to observe
- what metrics become important

It may also introduce:

- active-tier control
- frozen lower context
- tier-local learners in some settings

### What the tower does not fundamentally change

It does **not** require reinventing all of RL training from scratch.

A great many ordinary RL components still make sense:

- model modules
- collectors
- replay buffers
- update rules
- evaluation hooks
- logging

The tower mostly adds:

- additional structure around those

rather than destroying the usefulness of existing RL component boundaries.

This section, too, is answering a PO-originated concern.

The PO explicitly noted that the tower introduces a strange new component into RL training, while also emphasizing that the freezing and layer structure should still allow many ordinary RL components to remain recognizable.

So this section should be read as a clarification of that PO concern, not as a free-floating aside.

This is one of the strongest arguments in favor of the architecture proposed in this note.

## Final Cross-Check Verdict

If a serious RL engineer read the proposed surface decomposition in this document, my best judgment is:

- they would find the direction credible and largely contemporary
- they would probably agree that strong components are preferable to one rigid master loop
- they would recognize most of the named surfaces as legitimate engineering boundaries

They would likely still ask for:

- vectorization story
- tensor/device story
- batch/sequence story
- serialization/checkpoint story
- evaluation/train-mode separation

Those are real next-hardening steps.

But the underlying architecture is not out of step with contemporary RL practice.

It is, in fact, closer to serious current practice than a simpler but more rigid package-owned training framework would be.

## References For This Cross-Check

The judgments in this section were informed by the current official documentation of:

- `gymnasium`
- Ray RLlib
- Tianshou
- Acme
- CleanRL
- `ROS 2`

The main relevance of those references was:

- `gymnasium`
  - clean env boundary, wrappers, vector envs
- RLlib
  - env-to-module connector pipelines, replay buffers, learner-side machinery, metrics logging
- Tianshou
  - explicit collector + buffer + policy/algorithm split
- Acme
  - actor/learner/environment-loop/adders/replay decomposition
- CleanRL
  - evidence that engineer-owned readable loops remain a respectable contemporary stance
- `ROS 2`
  - modular execution and ownership separation for robotics-facing integration settings

## Compatibility Note

This note does not appear to contradict either the current mathematical model or the current package architecture, but there are two places where the language must stay disciplined if that remains true.

### No contradiction with the current mathematical model

There is no clear contradiction with the current mathematical model.

The mathematical model is mainly about:

- RL problems as hidden graph structures
- quotient and tower construction
- executable lift
- abstract intermediate states

It is not tightly committed to one particular ML training object.

So broadening the training/model boundary from something like:

\[
\pi_\theta : \mathcal{S}_H \to \mathcal{P}(\mathcal{A}_H \mid \mathcal{S}_H)
\]

to something like:

\[
\mathcal{M}_\theta : \mathcal{X}_H \to \mathcal{D}_H
\]

is best understood as a generalization of the ML interface, not a change to the hidden-graph or tower mathematics.

If anything, it is more mathematically honest about real RL practice, because many real learners do not directly parameterize a literal policy distribution.

### No contradiction with the current architecture

There is also no clear contradiction with the current package architecture at a high level.

It matches the main existing split fairly well:

- `gymnasium.Env`
  - owns the problem shell
- `state_collapser` runtime and tower machinery
  - owns graph and tower structure
- training runner or learner
  - sits above that

So this note should be read as a refinement of the training/model layer rather than a rewrite of the core package architecture.

### First caution

The first caution is that:

\[
\mathcal{X}_H
\]

must stay downstream of the problem/runtime split.

If `\mathcal{X}_H` includes things like:

- tower context
- active tier
- frozen lower context
- action masks

that is fine, but only if those are package-defined runtime or collector outputs.

They must not become:

- env-owned semantics
- example-owned hierarchy leaks

So this remains compatible with the architecture only if `\mathcal{X}_H` is built after the env/runtime boundary rather than by collapsing those layers together.

### Second caution

The second caution is that:

\[
\mathcal{D}_H
\]

should not be mistaken for "the action space itself."

If `\mathcal{D}_H` carries things like:

- probabilities
- logits
- Q-values
- sampled actions
- value heads
- diagnostics

then it is not merely an action set or a policy codomain.

It is a broader decision object or decision surface.

That is acceptable, but it means the notation is architectural rather than the same kind of mathematical object as:

\[
\mathcal{P}(\mathcal{A}_H \mid \mathcal{S}_H).
\]

### Overall judgment

So the best current judgment is:

- no, this note does not contradict the current mathematical model
- no, it does not contradict the current architecture
- yes, it is a real broadening of the training/model interface

and it remains aligned provided that:

- the env remains the problem shell
- the runtime remains package-owned structural machinery
- `\mathcal{X}_H` is derived from those surfaces rather than replacing them
- `\mathcal{D}_H` is understood as a decision object rather than just "the action space"
