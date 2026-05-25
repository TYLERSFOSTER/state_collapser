# Module Design Desiderata

## Implementation Status Note

The repository now contains a first implemented vertical slice of the design described in this document, including:

- core state/action/edge/reward objects
- hidden, explored, and vista graph layers
- local-star and annotation-store support
- contraction-policy interfaces plus label-based and seeded-random policies
- quotient projection/coset/tier-view layers
- tower runtime and runtime snapshots
- the first robot-constraint toy environment
- a vertical-slice integration path
- a thin Gymnasium-style adapter

This document remains a design-rationale artifact.
The implementation authority for current coding work remains:

- `docs/design/final_initial/final_initial_blueprint.md`
- `docs/design/final_initial/final_initial_implementation_gameplan.md`

## What We Want It To Do

This section collects desired package behaviors and capabilities before committing to module structure or implementation details.

At the top level, the package is intended to do two closely related things.

First, it should provide two mathematical or structural subpackages that work in conjunction with one another:

- path-space computation
- quotienting

These should not be treated as isolated utilities. They are meant to augment one another as a paired foundation layer for the larger package.

Second, the package should use that combined machinery to take a hard reinforcement-learning problem with hidden hierarchical structure and synthetically organize it into an HNSW-based HRL tower.

That tower is not only a representation of structure. It should also support a natural training regimen that is more effective than prior approaches.

## External Compatibility Targets

The package should target a higher abstraction level than any one hardware platform or robot-specific codebase.

It should be usable before hardware exists, and it should remain meaningful when integrated into a larger robotics or embodied-agent stack later.

The current intended external compatibility targets are:

- `gymnasium` as the primary RL environment API boundary
- `torch` as the primary ML backend when learnable models are involved
- `ROS 2` as the primary robotics integration boundary

These roles are intentionally distinct.

`gymnasium` is the safest environment-level compatibility target because it is the mainstream Python RL environment interface.

`torch` is the practical default model backend because the broader RL tooling ecosystem and user expectations are still centered there.

`ROS 2` is not the same kind of dependency as the other two. It should be treated as the larger robotics-system attachment point rather than as the defining RL environment API.

So the package should not be architected as "just a Gymnasium environment." Instead, it should preserve an internal abstraction layer capable of adapting upward into robotics-facing systems while still exposing clean Gymnasium-oriented entry points where appropriate.

## Label Requirements

Nodes and edges should support arbitrary labels that can be strings or numbers.

These labels should be treated as primitive metadata, not as a special ontology with built-in local or global semantics.

In particular:

- nodes may carry multiple labels
- edges may carry multiple labels
- labels should be usable to guide contraction, quotienting, filtering, and structural analysis
- contraction procedures should be able to select edges by label predicates

The label system should remain local/global agnostic.

If a particular family of labels induces a coherent large-scale contraction pattern, that should be understood as a property of the graph together with the contraction rule, not as a special type of label.

One motivating example is an `n`-dimensional lattice whose edges carry labels `0, 1, ..., n - 1`. In that setting, selecting and collapsing edges with label `i` can behave like collapsing dimension `i`, yielding an `(n - 1)`-dimensional lattice structure.

But that kind of structural interpretation should emerge from the graph and the operation. The package should not hard-code labels themselves as "dimensions," "local-only," or "global-only."

## Intended Package Flow

At a high level, the intended library flow is:

1. the user provides a reinforcement-learning problem in a standard external format, likely `gymnasium` first
2. the package reinterprets that problem abstractly in graph terms, with states understood as nodes and actions or transitions understood as edges
3. helper or analysis components compute structural statistics about the resulting implicit graph
4. quotienting or contraction procedures repeatedly coarsen that graph
5. the repeated coarsening induces an abstract hierarchical tower over the RL state space
6. the package supports tiered training over that tower

The package should not require the user to hand-construct a graph directly.

Instead, one major responsibility of the library is to build or expose a usable graph interpretation from a standard RL problem specification.

That reinterpretation step may be straightforward in some settings and much more subtle in others. The package design should leave room for the fact that different environment surfaces may make the states-as-nodes and actions-as-edges picture more or less direct.

The helper layer should be able to return useful statistics about the implicit graph induced by the RL problem.

Those statistics are expected to help characterize the structure before or alongside quotienting and tower construction.

One motivating coarsening pattern is to randomly contract `k` edges at each node. Repeating such operations produces a sequence of coarser graphs, which then serve as the levels of the induced hierarchical structure.

That motivating pattern should not be treated as the only possible contraction mechanism, but it is part of the intended initial picture for how an RL problem gives rise to a tower.

The final goal is not only to analyze or compress the graph. The package should be robust enough to support hierarchical or tiered training procedures over the resulting tower.

This flow should now be understood as covering both:

- an offline regime, where a graph or graph-like state space is already sufficiently available for direct contraction
- an online regime, where the graph interpretation, contractions, and tower are built incrementally during exploration and training

So the package should not assume that the full graph must be known before the tower exists.

## Modeled Reality And State

The package should distinguish at least three conceptual layers:

1. reality itself
2. modeled reality, meaning the agent's evolving representational surface
3. the hidden but abstractly existing graph of all possible modeled states and transitions

This package is primarily concerned with layer 2 and with structural claims about layer 3.

It is not primarily concerned with the direct robotics-system question of whether a representation is implemented correctly on hardware. That is closer to the larger systems boundary associated with `ROS 2`.

Within modeled reality, a state should not be defined as ultimate ground truth about the world.

Instead, a state should be understood as an agent-usable representational locus from which action structure is defined.

In practice, this means a state in the intended sense may include:

- a position or configuration in an environment space
- scalar, tensor, categorical, or string-valued fields
- local marks, notes, or annotations left by the agent
- tier-local information already induced by earlier contractions
- whatever other information is necessary for the agent to treat the state as revisitable, annotatable, and transition-bearing

So the package's notion of state should be expressive enough to support rich structured environment-state descriptions, not only fixed-size numerical vectors.

For discretized settings, it is expected that the full list of fields constituting a state is known, even if the agent does not know the full transition structure of the environment in advance.

The package should also leave room for multiple notions of nearness or similarity between states, including but not limited to:

- metric distance
- embedding-based similarity
- cosine similarity
- other learned or hand-designed proximity functions

These may matter for analysis, contraction proposals, or tower-building heuristics even when they do not define the state itself.

## Graph Implementation Stance

The package should take graph implementation seriously as a first-order architectural decision.

The intended graph model should not be:

- a generic graph-library object used as the primary source of truth
- an untyped collection of miscellaneous node and edge payloads
- a design in which graph legality is reconstructed ad hoc from environment code

Instead, the hidden configuration graph should be treated as a predicate-defined mathematical object.

That means:

- state representations should be explicit, typed, and validated
- primitive action representations should be explicit, typed, and validated
- node membership in the hidden graph should be determined by a node-validity contract
- edge existence in the hidden graph should be determined by an edge-validity contract

So the package should be built around a graph-defining layer consisting of:

- state types
- action types
- graph specification objects or contracts
- node-membership predicates
- edge-membership predicates

This is a better fit for the package than treating the graph as a large pre-materialized object from a generic graph library.

That stance is especially important because the hidden graph may be:

- very large
- only partially explored
- dynamically queried during training
- repeatedly quotiented into higher-tier views

For these reasons, the package should assume that the hidden graph is often best represented intensionally rather than extensionally.

That is, it is often better represented by the rules that define valid states and valid primitive transitions than by a fully materialized store of all nodes and edges.

This lesson is reinforced by the implementation pattern used in the local `rl_counterpoint` project, where graph semantics live in explicit state/action/spec/predicate layers rather than in a generic graph object.

## Derived Graph Layers

Once the hidden configuration graph is understood as a predicate-defined object, the other graph layers in the package should be treated as structured overlays or derived views rather than unrelated graph objects.

The main intended layers are:

- the hidden configuration graph
- the explored subgraph
- the one-hop vista graph
- quotient graphs at successive tower tiers

These should be related, not merely parallel.

More specifically:

- the explored subgraph should be a derived view of the hidden graph restricted to visited history
- the vista graph should be a derived view that expands the explored subgraph by the maintained one-hop neighborhoods
- quotient graphs should be derived contraction views over the currently available graph layer, together with the coset and projection data needed to interpret them

So the package should avoid an architecture in which each of these is implemented as an unrelated graph data structure with loosely synchronized semantics.

Instead, they should be implemented as graph layers whose meaning is inherited from the hidden graph plus the relevant exploration, monitoring, or quotienting operations.

This matters because tower construction, reward descent, refinement, and message passing all rely on the fact that these graph layers are structurally connected.

## State, Action, And Legality As Core Contracts

The package should treat the following as core contracts, not incidental utilities:

- state representation
- primitive action representation
- node legality
- edge legality

This means:

- state definitions should not be buried inside environment wrappers
- action definitions should not be treated as anonymous labels if they carry real semantics
- legality checks should not be scattered across unrelated modules

Instead, there should be a cleanly defined contract layer describing:

- what a state is
- what a primitive action is
- how an action acts on or relates states
- when a state belongs to the hidden graph
- when a primitive action induces a legal edge

For some environments, an action may be represented:

- directly as a target next state
- as a delta or bounded transformation
- as a control symbol that must be decoded

The package should allow such variation while still treating action representation as a first-class part of the graph contract.

This is important because later package behaviors depend on it:

- one-hop neighborhood queries
- message passing along primitive actions
- edge labeling
- contraction family selection
- quotient projection
- direct-image reward aggregation
- refinement from coarse moves back to executable lower-tier behavior

So the graph layer of the package should not be thought of as a passive storage concern.

It is the contract surface on which much of the rest of the package depends.

## Breadcrumbed Online Tower Construction

The package should support the idea that the agent can build tower structure during training by leaving persistent marks or notes in its modeled reality.

The motivating picture is:

- the agent explores an environment that is not fully known in advance
- as it visits states, it records local information
- those records function as breadcrumbs or marks in the agent's modeled space
- those breadcrumbs are used to support local contractions and higher-tier structure

So the tower should not be understood only as an offline object computed by an external analyst.

It should also be possible for the tower to emerge online as a memory-bearing navigation structure used by the agent itself.

In this picture:

- encountered states become candidate nodes
- encountered or inferred transitions become candidate edges
- local labels, annotations, counts, tags, or contraction marks accumulate through experience
- repeated local contraction decisions gradually induce a larger implicit hierarchical tower

This is meant to support the intuition that the agent can move through ordinary environment space while internally navigating a progressively built coarse-to-fine tower.

One important refinement is that the dynamically mapped graph at time `t` should not be understood as only the literal visited trajectory.

The intended picture is:

- black nodes are visited or history states
- grey nodes are one-hop monitored neighbor states off the visited history

So the agent continuously maintains not only the visited path but also a one-hop fringe around it.

This one-hop monitoring is part of the ordinary online graph-construction regime.

## Coarse Planning Versus Fine Execution

One critical design distinction is that the agent never literally moves in the quotient space.

The agent always acts in the original environment or base state space.

The quotient space or tower is valuable only if it gives the agent a cheaper internal control surface for choosing what to do next.

So the intended picture is:

- the body moves in fine space
- the planner reasons in coarse space
- coarse decisions are refined back into ordinary lower-level behavior

The expected speedup comes from reduced branching, shorter effective planning horizon, reuse of previously discovered local structure, and coarse-to-fine guidance.

This means a coarse edge should not automatically be interpreted as a physical edge in the base graph.

A coarse edge is more naturally understood as a higher-level exit relation, macro-action, option, or policy promise whose meaning must eventually be refined back into ordinary fine-scale execution.

So useful quotient or tower construction requires some refinement story:

- how a coarse node relates to its fine representatives
- how a coarse transition becomes executable lower-level behavior
- how the agent uses coarse structure without confusing identification in the quotient with literal interchangeability in the base space

Without that, contraction is merely compression.

With that, contraction can become part of a genuine HRL navigation and training system.

## Contraction As Information Equalization

The package should support two related contraction regimes:

1. contraction applied to an already available graph structure
2. contraction performed during training and exploration, while the agent is still building its modeled reality

These should not be treated as two unrelated systems.

The more general design target is a contraction mechanism that can serve both settings.

One important guiding principle is:

**contraction is an information-equalization operation**

That is, when two nodes or states are contracted, the contraction should not be understood only as a topological identification in an abstract graph.

It should also be understood as a synchronization step in which local knowledge, labels, marks, annotations, or other operationally relevant information are shared strongly enough that the contracted states can behave as one coarse decision locus at the next tier.

This is especially important for online or during-training contraction.

If a transition such as `x -> y` is contracted, then the system should support the idea that:

- `y` can inherit relevant local information available at `x`
- `x` can inherit relevant local information discovered at `y`
- after the relevant exchange, both states can answer the next-tier questions in the same effective way

In that sense, contraction is not merely edge removal or node merging. It is a process that supports coarse-state formation by equalizing enough information across the contracted region.

This perspective is meant to support the intuition that a subspace can be treated as a quotient space when the members of that subspace have synchronized enough local knowledge to behave like representatives of the same coarse state.

For a fully pre-existing graph, this same principle should still apply, even if the required information equalization can be computed or applied in batch rather than accumulated online through experience.

So the design target is not one contraction system for static graphs and another for training-time collapse. The design target is one sufficiently general contraction framework that can operate:

- offline over already available graph structure
- online over partially discovered graph structure during exploration and training

## Tier-0 Direction Selection And Inherited Higher-Tier Contractions

The current mathematical picture suggests an important asymmetry between tier 0 and higher tiers.

At tier 0, contraction can still be defined in something like a native directional way.

The motivating intuition comes from the `\mathbb{Z}^n` lattice case:

- edges have dimension labels
- one can contract by dimension
- or more generally select a family of directions at each vertex for contraction

In the more general setting for this package, the tier-0 analogue is:

- choose contraction families from the dynamically mapped base graph
- for example by label predicate
- or by a rule such as randomly contracting `n` directions at each visited vertex

But this kind of direct directional selection is native only at tier 0.

Once contractions have begun, the quotient process distorts:

- source and target node identity
- edge existence

## Runtime Update Cycle

The package should support a concrete runtime update cycle that implements the mathematical model incrementally during training.

The intended picture is not:

- build a full tower first
- then train over it afterward

Instead, the intended picture is:

- the agent moves by primitive action in the base hidden or explored graph
- the explored graph and full currently understood tower are updated immediately after each step
- reward and training logic are evaluated against that current tower state

So one intended runtime cycle is:

1. **Agent takes a primitive action**

   The control loop selects or samples a primitive action and executes it in the base environment.

2. **A new state enters the explored graph**

   The resulting next state is recorded in the explored-history layer if it was not already present there.

   More generally, the newly traversed primitive edge and its incident states become part of the currently known explored graph structure.

3. **Update the local `1`-hop vista**

   At the newly occupied state, the package queries the local star or outgoing `1`-hop neighborhood determined by the hidden-graph contract.

   This newly queried neighborhood data is added to the current vista graph.

   The runtime assumption is that the dynamically mapped graph should always be updated at least by:

   - the newly traversed explored edge
   - the newly occupied state
   - the local outgoing `1`-hop neighborhood at that state

4. **Apply the contraction policy at tier `0`**

   The package applies the chosen contraction policy to the newly updated local star data at tier `0`.

   This should be understood uniformly across different contraction styles.

   For example:

   - one policy may choose all edges with a given label
   - another may randomly sample a specified fraction of outgoing edges

   Both are instances of a common edge-family selection policy.

   The key point is that contraction is not chosen globally once and for all after graph discovery is complete.

   Rather, each new local graph update is immediately subjected to the chosen tier-`0` contraction policy.

5. **Propagate induced contractions through higher tiers**

   Once the tier-`0` contraction update has been applied, the induced quotient consequences should be implemented through the entire currently known tower.

   That is:

   - all known contraction consequences over history should remain in force
   - the new local contraction information should be propagated upward through every tier currently represented

   The intended model is a full current-tower update after each base-step graph update.

6. **Update current position at every tier**

   The package should maintain the agent's current position not only in the base explored graph but also in every quotient tier induced by the current tower.

   Because higher-tier paths are quotient images of lower-tier paths, base movement determines the induced current position in the full tower.

   So after each primitive action, the system should know:

   - the current base-tier state
   - the current quotient-state representative or coset at each higher tier

7. **Compute current step reward and cumulative path reward**

   Reward should then be computed against the currently understood tower state.

   At the present package stage, the intended reward model is:

   - primitive actions carry local reward contributions
   - cumulative path reward is formed by weighted aggregation over those local contributions
   - quotient-tier reward summaries are formed by averaging or aggregating over the corresponding preimage edge families

   So after each runtime update, the package should be able to compute:

   - current step reward
   - updated cumulative reward along the current base path
   - corresponding quotient-tier reward summaries as needed by training logic

8. **Hand the updated tower state to training/control logic**

   The final result of the runtime cycle is the current fully updated training state.

   This should include at least:

   - current explored graph information
   - current vista graph information
   - current quotient/tower state
   - current position at each tier
   - current reward information

   The training or control layer then acts on this current state.

This runtime cycle should be treated as one of the main bridges between the mathematical model and the code architecture.

It is close to the level of specificity needed for code skeleton design.
- the clean interpretation of original directional fields

So higher-tier contraction should not be treated as though each quotient graph still comes equipped with a fresh intrinsic notion of the same original directions.

Instead, the intended higher-tier picture is inherited:

- the contraction families at later tiers are the images of contraction-relevant edge families from earlier tiers
- correspondingly, one may need to reason in terms of preimages of the currently highlighted contraction families relative to earlier graph levels

So language such as "preimages of edges to contract" is intended in a serious structural sense, not merely as loose visual intuition.

The design implication is:

- tier-0 contraction selection may be direct
- higher-tier contraction selection is inherited through quotient maps and image/preimage structure

This should be reflected in both the mathematical model and the implementation architecture.

## Local Contraction, Message Passing, And Coarse Identity

During online contraction, the central engineering problem is not merely declaring that two states belong to the same coarse class.

The system must also address how that declaration becomes operationally meaningful for later behavior.

One motivating sketch is:

- the agent is at a state `x`
- it identifies possible actions or outgoing transitions
- it selects some subset to contract, possibly guided by labels
- for a contraction such as `x -> y`, it assigns a next-tier identity or mark
- that identity must be supported by information flow, not just by a one-time declaration

The present design direction is that contraction may require at least a small amount of message passing or bidirectional information sharing across the contracted relation.

The motivating intuition is:

- `x` should be able to discharge relevant local information into `y`
- `y` should be able to recoil or return relevant information back into `x`
- after this exchange, `x` and `y` should answer the next-tier questions in the same effective way

This is one reason the phrase "contraction is an information-equalization operation" is central rather than decorative.

The goal is not only to merge graph structure. The goal is to build a coarse identity that is behaviorally meaningful.

That means a contracted region may need:

- persistent marks or labels
- synchronized local annotations
- some rule for inheritance of outgoing coarse structure
- some rule for what it means for two states to behave as representatives of one next-tier state

In this sense, the package should support the idea that a subspace can be treated as a quotient space when enough local knowledge has been equalized across it for its members to function like coset-style representatives of one coarse state.

This also suggests that the package may need contraction primitives richer than plain graph merge operations, potentially including:

- annotation propagation
- merge or synchronization of node-local memory
- neighborhood message passing
- rules for persistent coarse-state identity

## Why The Tower Speeds Things Up

The intended speedup does not come from the agent physically teleporting through the environment.

It comes from the agent being able to reuse coarsened structural knowledge discovered elsewhere in a contracted region.

For example, if a state `x` is contracted with a state `y`, and `y` later discovers useful exit structure, then `x` can benefit from that information once the relevant contraction-induced synchronization has occurred.

So the point of contraction is not only to shrink a graph numerically.

It is to create shared higher-level decision loci from which the agent can plan with fewer effective branches and then refine those decisions back down into ordinary behavior.

In this sense, the tower is a progressively built collapsed memory of the environment's actionable structure.

The package should therefore aim to support:

- local contraction decisions
- persistence of the resulting coarse marks
- reuse of discovered exit structure across contracted states
- repeated accumulation of these effects into a larger implicit tower

## Training-Time Hierarchical Control Principle

For the training and online navigation part of the system, one central control principle is:

- collapse when local structure is still unresolved
- otherwise act from the lowest trustworthy tier available
- refine upward only as needed to make the move executable

This should not be treated as the entire purpose of the package.

The package has broader responsibilities, including structural analysis, helper statistics, offline quotienting, and offline or online tower construction.

But for the training-time regime, this principle is meant to organize the agent's behavior more deeply than a simple exploration-versus-exploitation scheduler.

The intended picture is that the agent should not need to switch crudely between "tower-building mode" and "tier-training mode."

Instead, the agent should use the state of local tower maturity itself as the guide:

- if the current region is not yet well collapsed, the agent should perform the local work needed to induce or improve the tower there
- if the current region already supports a trustworthy coarse tier, the agent should make the coarsest reliable move available first
- finer tiers should be consulted only as necessary to refine that move back into executable lower-level behavior

So the design target is an intrinsic hierarchical control rule, not merely a hand-scheduled tradeoff between separate operating modes.
