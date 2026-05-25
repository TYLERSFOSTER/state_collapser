# Implementation Contracts

## Purpose

This document defines the first concrete implementation contracts for `state_collapser`.

It is intentionally more rigid than the other design documents.

Its job is to identify:

- core classes and protocols
- required methods
- minimal stored fields
- runtime update order
- reward object shape
- contraction-policy interface
- trustworthiness predicate placeholder

The goal is to make code scaffolding straightforward rather than interpretive.

This document does not attempt to settle every future mathematical question.

It defines the minimum implementation surface needed to build a serious first version of the package.

## Scope

These contracts target the current package stage:

- hidden graph represented as a predicate-defined object
- explored, vista, and quotient graphs represented as derived overlays or views
- reward decorating graph-level transition structure
- online runtime tower updates after each primitive step
- no full higher-categorical or simplicial implementation

## Core Design Rule

The package should be implemented around contracts, not around one monolithic graph object.

The minimum contract layers are:

1. state and action contracts
2. hidden-graph contract
3. derived graph-layer contracts
4. contraction-policy contract
5. runtime update contract
6. reward-summary contract
7. trustworthiness contract

## Core Classes And Protocols

The following names are recommended as the first stable implementation surface.

Exact file placement can change, but these roles should remain.

### `State`

Represents one modeled state at the base hidden-graph level.

This should be:

- immutable
- hashable
- suitable for use as a key in dictionaries and sets

Recommended implementation forms:

- frozen dataclass
- named tuple
- explicit immutable record object

Minimal contract:

- structural equality
- stable hash
- human-readable representation

### `PrimitiveAction`

Represents one primitive action or indecomposable transition token.

This should be:

- immutable
- hashable
- explicit, not an anonymous string unless the environment itself is that simple

The package should allow multiple action-encoding styles, for example:

- direct-next-state action
- delta action
- decoded control action

Minimal contract:

- structural equality
- stable hash
- human-readable representation

### `GraphSpec`

Defines the static or semi-static rules of a hidden graph family.

This object should hold environment-independent graph-definition parameters.

Examples:

- field ranges
- dimensionality
- action bounds
- constraint parameters
- label conventions

This should be:

- immutable where practical
- small enough to pass around freely

### `HiddenGraph`

Predicate-defined graph contract for the underlying hidden state-action space.

This is not required to store all nodes or all edges explicitly.

Its job is to answer legality and local-neighborhood questions.

### `ExploredGraph`

Derived overlay representing the visited-history restriction of the hidden graph.

This is the first runtime graph layer.

### `VistaGraph`

Derived overlay representing the explored graph plus maintained `1`-hop query information.

This is the operational graph layer on which message passing and local contraction work first.

### `QuotientGraph`

Derived graph layer representing one contraction tier over a source graph layer.

Each quotient graph should know its source layer and its projection map.

### `ContractionPolicy`

Pluggable strategy object defining how edge families are selected for contraction.

This is the main abstraction unifying:

- label-based contractions
- random edge-family sampling
- future learned contraction strategies

### `RewardSummary`

Structured reward object storing both immediate and aggregate reward information.

This should be used instead of raw scalar reward alone wherever quotient aggregation matters.

### `TowerRuntime`

Coordinating runtime object responsible for one-step updates of:

- explored graph
- vista graph
- quotient tiers
- current positions across tiers
- reward summaries

### `TrustworthinessPolicy`

Placeholder contract determining whether a tier is currently trustworthy enough to be used first by training/control logic.

This should remain pluggable.

The initial implementation may use a simple heuristic rule.

## Required Methods

The following methods or equivalent protocol operations should exist.

Exact naming can vary slightly, but the roles should not.

### `HiddenGraph`

Required methods:

- `is_valid_state(state: State) -> bool`
- `is_valid_action(state: State, action: PrimitiveAction) -> bool`
- `apply_action(state: State, action: PrimitiveAction) -> State`
- `is_valid_edge(source: State, action: PrimitiveAction, target: State) -> bool`
- `out_actions(state: State) -> tuple[PrimitiveAction, ...]`
- `out_neighbors(state: State) -> tuple[State, ...]`
- `out_edges(state: State) -> tuple[BaseEdge, ...]`

Contract notes:

- `apply_action(...)` and `is_valid_edge(...)` should agree
- `out_neighbors(...)` should be derivable from valid outgoing actions
- this layer is query-oriented, not necessarily materialized

### `ExploredGraph`

Required methods:

- `has_state(state: State) -> bool`
- `has_edge(edge: BaseEdge) -> bool`
- `add_state(state: State) -> None`
- `add_edge(edge: BaseEdge) -> None`
- `visited_states() -> tuple[State, ...]`
- `visited_edges() -> tuple[BaseEdge, ...]`
- `current_state() -> State`
- `current_path() -> tuple[BaseEdge, ...]`

### `VistaGraph`

Required methods:

- `refresh_local_vista(state: State) -> None`
- `vista_neighbors(state: State) -> tuple[State, ...]`
- `vista_edges(state: State) -> tuple[BaseEdge, ...]`
- `push_message(edge: BaseEdge, payload: VistaPayload) -> None`
- `pull_message(edge: BaseEdge, payload: VistaPayload) -> None`
- `node_payload(state: State) -> NodeAnnotationStore`

Contract notes:

- `refresh_local_vista(...)` should perform the local `1`-hop query
- push/pull should operate only along legal known edges in the current vista layer

### `QuotientGraph`

Required methods:

- `source_graph() -> GraphLayer`
- `tier_index() -> int`
- `project_state(state: StateLike) -> QuotientNodeId`
- `project_edge(edge: EdgeLike) -> QuotientEdgeId`
- `node_members(node_id: QuotientNodeId) -> tuple[StateLike, ...]`
- `edge_members(edge_id: QuotientEdgeId) -> tuple[EdgeLike, ...]`
- `out_edges(node_id: QuotientNodeId) -> tuple[QuotientEdgeId, ...]`
- `current_position() -> QuotientNodeId`

Contract notes:

- every quotient graph should carry explicit projection/provenance data
- quotient edges should be understood through their preimage families

### `ContractionPolicy`

Required methods:

- `select_edge_family(local_star: LocalStar, tier_index: int) -> EdgeSelection`

Optional methods:

- `seed(seed: int) -> None`
- `policy_name() -> str`

Contract notes:

- label-based contraction and random sampling should both implement this same interface
- the output should be a selected edge family, not a full quotient graph

### `RewardSummary`

Required fields/methods:

- `step_reward: float`
- `cumulative_reward: float`
- `count: int`
- `mean: float`
- `variance: float | None`
- `confidence_interval: tuple[float, float] | None`
- `merge(other: RewardSummary) -> RewardSummary`

The initial implementation may allow some fields to be `None` until enough samples exist.

### `TowerRuntime`

Required methods:

- `reset(initial_state: State) -> RuntimeSnapshot`
- `step(action: PrimitiveAction) -> RuntimeSnapshot`
- `current_snapshot() -> RuntimeSnapshot`
- `tier_graphs() -> tuple[GraphLayer, ...]`
- `current_positions() -> tuple[PositionLike, ...]`

### `TrustworthinessPolicy`

Required methods:

- `is_trustworthy(snapshot: RuntimeSnapshot, tier_index: int) -> bool`

Optional method:

- `score(snapshot: RuntimeSnapshot, tier_index: int) -> float`

## Minimal Stored Fields

This section defines the minimum fields each object should store.

### `State`

Minimum stored fields:

- `state_id` or equivalent stable identity
- structured payload containing modeled-state content

The exact payload can vary by environment.

Examples:

- coordinates
- scalar fields
- tensor-like fields
- categorical values
- strings

### `PrimitiveAction`

Minimum stored fields:

- `action_id` or equivalent stable identity
- encoding payload
- optional label set

### `BaseEdge`

Recommended minimal stored fields:

- `source: State`
- `action: PrimitiveAction`
- `target: State`
- optional labels

This should be a first-class record type.

### `NodeAnnotationStore`

Recommended minimal stored fields:

- local labels
- local notes/marks
- pushed vista payloads received from neighbors
- pulled vista payloads received from neighbors
- tier-local contraction marks

### `ExploredGraph`

Minimum stored fields:

- set or map of visited states
- set or map of visited edges
- ordered current path history
- current base state

### `VistaGraph`

Minimum stored fields:

- all explored-graph fields or a reference to the explored graph
- local queried `1`-hop neighborhoods for visited states
- node annotation stores
- message-passing payload records

### `QuotientGraph`

Minimum stored fields:

- `tier_index`
- reference to source graph layer
- state-to-quotient-node projection map
- edge-to-quotient-edge projection map
- quotient-node membership map
- quotient-edge membership map
- quotient-node annotation store
- current quotient position

### `RuntimeSnapshot`

Minimum stored fields:

- current base state
- current explored graph
- current vista graph
- ordered quotient tiers
- current position at every tier
- current step reward summary
- current cumulative reward summary

## Runtime Update Order

The runtime update order should be implemented exactly as a first-class algorithm.

For one primitive action step:

1. execute primitive action in base environment
2. validate and decode resulting base transition
3. add new state and traversed edge to explored graph
4. refresh local `1`-hop vista at newly occupied state
5. collect local star data at tier `0`
6. apply tier-`0` contraction policy to that local star
7. update tier-`0` quotient information
8. propagate induced quotient updates through higher tiers
9. update current position at every tier
10. compute current step reward summary
11. update cumulative reward summaries
12. produce runtime snapshot for training/control logic

This order should be represented clearly in code.

The package should avoid hiding these steps behind opaque side effects.

## Reward Object Shape

The implementation should distinguish:

- raw primitive step reward
- cumulative base-path reward
- quotient-tier aggregated reward summaries

Recommended object split:

### `StepReward`

Fields:

- `value: float`
- `source_state: State`
- `action: PrimitiveAction`
- `target_state: State`
- `time_index: int`

### `PathRewardSummary`

Fields:

- `step_count: int`
- `weights: tuple[float, ...]`
- `cumulative_value: float`
- `per_step_rewards: tuple[float, ...]`

### `QuotientRewardSummary`

Fields:

- `tier_index: int`
- `edge_id: QuotientEdgeId | None`
- `member_count: int`
- `mean_reward: float`
- `variance: float | None`
- `confidence_interval: tuple[float, float] | None`

Initial package requirement:

- support local action reward
- support cumulative path reward formed by weighted aggregation over primitive local rewards
- support quotient reward formed by aggregation over preimage edge families

## Contraction-Policy Interface

The contraction-policy interface should be small and strict.

Recommended core protocol:

```python
class ContractionPolicy(Protocol):
    def select_edge_family(
        self,
        local_star: LocalStar,
        tier_index: int,
    ) -> EdgeSelection:
        ...
```

Recommended input object:

### `LocalStar`

Fields:

- `center_state`
- `out_edges`
- `out_neighbors`
- local labels
- local annotations
- tier index

Recommended output object:

### `EdgeSelection`

Fields:

- selected edges
- selection reason or metadata
- tier index
- optional policy score

Required policy properties:

- deterministic or seeded-stochastic behavior
- no direct mutation of tower state
- edge-family selection only

The runtime engine applies the resulting selection.

This keeps policy choice separate from quotient update logic.

## Trustworthiness Predicate Placeholder

The package should not hardcode a permanent definition of trustworthiness yet.

But it should define a placeholder contract now.

Recommended first contract:

```python
class TrustworthinessPolicy(Protocol):
    def is_trustworthy(
        self,
        snapshot: RuntimeSnapshot,
        tier_index: int,
    ) -> bool:
        ...
```

Optional scoring extension:

```python
class ScoredTrustworthinessPolicy(TrustworthinessPolicy, Protocol):
    def score(
        self,
        snapshot: RuntimeSnapshot,
        tier_index: int,
    ) -> float:
        ...
```

The initial heuristic may depend on simple quantities such as:

- minimum number of supporting member edges
- minimum number of reward observations
- minimum message-equalization completeness
- minimum local vista coverage

But the contract should remain replaceable.

## Initial File-Level Scaffolding Recommendation

Recommended first module skeleton:

```text
src/state_collapser/
    core/
        state.py
        action.py
        edges.py
        labels.py
        annotations.py
        rewards.py

    graph/
        spec.py
        hidden_graph.py
        explored_graph.py
        vista_graph.py
        local_star.py

    contract/
        policy.py
        selection.py
        projection.py
        quotient_graph.py

    tower/
        runtime.py
        snapshot.py
        trustworthiness.py
```

This is not yet the full package shape.

It is the recommended minimum scaffolding for the first implementation pass.

## Initial Non-Goals

The first implementation pass should not try to solve all future directions.

Non-goals for the initial scaffold:

- full higher-categorical path machinery
- full ROS 2 integration
- final optimized CUDA aggregation
- production-grade distributed RL training
- universal support for strongly nonlocal reward rules

These should remain explicitly out of scope for the initial implementation layer.

## Open Implementation Questions For Review

The contracts in this document are now concrete enough to support scaffolding, but several implementation choices still need to be reviewed explicitly before coding proceeds too far.

These are not questions about the identity of the project.

They are questions about which concrete implementation variant should be chosen first.

### 1. Exact Concrete State Type

Open question:

- What should a base modeled state literally be in Python?
    - **PO Answer:** What does this mean? Explain the options immediately below.
        - *LLM Answer*: This means: what concrete Python object will represent one state in the hidden graph? The three options differ mainly in how much structure lives in the state object itself. A frozen dataclass means a state is an immutable named record with explicit fields like position, scalar fields, strings, and categorical values. A tuple plus side-store means the state itself is a small immutable mathematical key, while richer evolving data lives elsewhere. A richer immutable record object means we define a custom class with more behavior and structure than a dataclass, but still keep it immutable. My recommendation for the first implementation is: use a frozen dataclass for the base state, because it is explicit, readable, hashable, and serious enough for a professional package without overengineering.
            - **PO Answer:** (i) Yes. My initial intuition matches yours: use a frozen dataclass. I think an important issue here is speed. The whole point of this `state_collapser` repo is to speed up RL training, so we need to make sure that we don't introduce some bad slow-down with all the peripheral stuff we're adding. ...(2) Ah and this brings one important thing to mind: I want to make sure that we aren't reproducing RL architecture/functionality that already exists in `gymnasium`. In my understanding, the realtime discovered graph $G^0_{t}$ is a separate functionality than anything that exists in gymnasium, which is why we're building it in the present repo. I just want to make sure this is correct.
                - *LLM Answer*: Yes, that is correct. `gymnasium` gives the environment interaction shell: reset, step, observations, actions, rewards, and episode boundaries. It does not give the realtime discovered graph `G^0_t`, the `1`-hop vista layer, the quotient tower, the message-passing equalization machinery, or the runtime tower update cycle. Those are exactly the additional structural capabilities this repo is introducing. On speed: I agree we should be careful, but a frozen dataclass is still a good first choice because it gives clarity and stable identity while we validate the model. If profiling later shows state-object overhead matters, we can optimize representation after the graph/runtime logic is correct.
                    - **PO Answer:** Yes. I like this.

Current options:

- frozen dataclass
- tuple plus side-store
- richer immutable record object

Why this matters:

- state equality and hashing depend on it
- serialization depends on it
- annotation strategy depends partly on it
- graph-layer performance and clarity depend on it

Review question:

- Should the base `State` object be a minimal mathematical locus, or a richer runtime record?
    - **PO Answer:** What does this mean? Explain the options immediately below.
        - *LLM Answer*: The concern is whether the `State` object itself should contain only the stable data that identifies where the agent is in modeled reality, or whether it should also contain changing runtime information like notes, cached vista data, contraction marks, and reward-related decorations. A minimal mathematical locus keeps the state identity stable and makes quotienting and hashing cleaner. A richer runtime record can be convenient, but it risks mixing identity with changing annotations. My recommendation is: the base `State` should be a minimal mathematical locus, and changing runtime data should live outside it.
            - **PO Answer:** Yes. I agree: "*the base `State` should be a minimal mathematical locus, and changing runtime data should live outside it.*"

### 2. Exact Annotation Storage Model

Open question:

- Where should notes, marks, and other evolving local annotations live?
    - **PO Answer:** This partly depends on what `gymnasium`'s capabilities are. One really important thing to keep in mind here is that whenever we can, we should use capabilities in existing libraries. But on second thought, we're really talking about the graph structure. It seems to me they should live "at" or "in" state node. What's really happening is that nodes are getting all these decorations that basically describe, to the agent, new ways to moave *as if in quot*... so maybe a betweer way is everything, th3se quotinting notes, are in nodes of $G^0_t$, but the quotienting is like tiered itself, so by what we're following, we know what tier we're in. Does this make sense?

        One important asside that just occured to me: Aggregating upstairs edge rewards should ignore collapsed edges, so like -f A->B->C->D collapses to A->[B,C]->D, only A->B and C-> get used downstairs. I think I hadn't clarifi3d this before.  
        - *LLM Answer*: Yes, your answer makes sense, and I think it points to the right split. The quotienting notes should not live inside the hidden-graph state identity itself. They should live at the nodes of the current runtime graph layer, especially `G^0_t`, in a node annotation store keyed by base-state identity. Then higher-tier consequences are derived from those node-level decorations by the tower update. This fits your idea that the agent is really moving in `G^0_t` while accumulating new ways of moving as if in quotient. I also think your aside is important: when aggregating reward upstairs, collapsed internal edges should not count as outgoing quotient-edge contributors. For a collapse like `A -> B -> C -> D` with `[B,C]` as one quotient node, the relevant quotient-edge reward data comes from the boundary-crossing preimage edges, not the internal collapsed edges.
            - **PO Answer:** Yes. I agree, with the caveat that the node annotation store also be able to do *quickly* do the kind of message passing we need. It occurs to me that some of this message passing *might* be sped up with CUDA matrix computations, but that might require labels to become purely numerical.
                - *LLM ANswer*: Agreed. The node annotation store should be designed for fast neighborhood update, not just conceptual cleanliness. I would still avoid forcing labels to become purely numerical at the core contract level. Instead, the contract should allow arbitrary labels, while the runtime may optionally maintain an encoded numerical view for fast batch update or GPU acceleration later. That keeps the mathematical design honest while leaving room for CUDA-backed acceleration as an optimization layer rather than a foundational restriction.boundary-crossing preimage edges, not the internal collapsed edges.
                    - **PO Answer:** Ok. I agree with you. The contract should allow for arbitrary labels.

Current options:

- inside the state object itself
- in an external node annotation store keyed by stable state identity

Why this matters:

- mutating annotations inside a state can blur state identity
- external storage keeps state identity stable
- contraction equalization and message passing will rely on this decision

Review question:

- Should annotations be part of the state, or decorations attached to a stable state identity?

### 3. Exact Quotient Storage Model

Open question:

- How should quotient tiers be stored and updated in memory?
    - **PO Answer:** Does above answer this?
        - *LLM Answer*: Partly, but not fully. Your earlier answer clarifies where quotienting notes conceptually live, but this question is narrower: what concrete data structures should store the quotient itself? My recommendation is that the first implementation should use explicit projection dictionaries and explicit membership maps. In other words: store a map from lower-tier states to quotient-node ids, a map from lower-tier edges to quotient-edge ids, and reverse maps from quotient ids back to member states and edges. This is the most inspectable and least ambiguous first version, which matters a lot while the model is still being refined.
            - **PO Answer:** I understand, but I think you're missing the point. In reality, all the quotient graphs are just the original graph, but using accumulated, tier-nested annotations to skip around through contraction-coset representatives. This makes me think that your "where" question is sort of missing what the actual structure is. "Where" the agent is at any given time is really just "which annotations subset is it following?". Do you see? ...So I guess it's more like there is an agent for each tier, not that there is a whole different graph for each tier. The agents at each tier use this descend/ascend thing described in the asnwers to these questions. Does this clarify?
                - *LLM Answer*: Yes, this clarifies the issue substantially. The important correction is that quotient tiers should not be thought of as wholly separate graph objects in the strong ontological sense. They are better understood as tier-indexed quotient views over the same discovered graph, realized through nested annotation/projection structure. That said, I still think the code should materialize explicit quotient-view data structures for each tier in version `1`, because the runtime needs inspectable objects representing: current projection, current coset membership, current tier position, and current outgoing quotient possibilities. So conceptually I agree with your correction, while implementation-wise I still recommend explicit tier-view objects built over one shared underlying discovered graph.
                    - **PO Answer:** No you are missing the critical thing here. ***As we move down the tower, coset and outgoing edge data is nested.*** That makes the query like... you know you could do things like "what are my outgoing edges here? I am in tier 7." And then the query is like "All outgoing edges tier 7," and the actual query is like "<= 7", and then returns all outping edges accumulated at all higher tiers. Is thi smaking sense yet?
                        - *LLM Answer:* Yes, this makes sense, and it is the key correction. The quotient structure is not just a family of separate tier views with independent outgoing-edge sets. It is a nested accumulated structure. At tier `k`, the effective outgoing-edge query is not "exactly tier `k` data only"; it is something like "all quotient-relevant outgoing-edge data accumulated through tiers `0` through `k`," or in your language a `<= k` query. That means the storage model should explicitly support nested outgoing-edge accumulation by tier. So the first implementation should store, for each base state and tier, a tier-indexed annotation bundle whose outgoing-edge knowledge is cumulative. This supports the query pattern you described and matches the idea that the agent is really following progressively accumulated skip knowledge rather than moving in disconnected quotient graphs.
                            - **PO Answer:** Correct.

Current options:

- explicit projection dictionaries
- union-find-like merge structures
- lazy view objects
- hybrid structures

Why this matters:

- update cost depends on it
- inspectability depends on it
- debugging quotient behavior depends on it
- tower propagation depends on it

Review question:

- Should the first implementation optimize for inspectable explicit maps, or for more clever incremental update machinery?

### 4. Exact Message Payload Shape

Open question:

- What exactly should the `1`-hop push/pull message carry in version `1`?
    - **PO Answer:** The point here is the ultimate behavior we want. Imagine an agent moving around $G^{1}_{t}$. It's really moving around $G^{0}_{t}$, but it's using new, accumulated notes at nodes to move around via skips. The skips are possible because every node in every cosets knows all outgoing arrows of all nodes in the coset, and can jumpt across any of these. This is the reason for the out-1-hop message passing. The idea is that each time a new edge is "contracted" in $G^{0}_{t}$, what really happends is that new "possible outgoing edge" data is passed all around in coset. That is what the message passing is for. It needs to be forward and backard since the graph is directed, but coset equiv is not. Do you understand?
        - *LLM Answer*: Yes, I understand. The goal is not generic message passing for its own sake. The goal is to make every state in a coset know the outgoing possibilities discovered at the other states in that coset, so that the agent can move in `G^0_t` while using accumulated quotient-style skip knowledge. Given that, the minimal honest version-`1` payload should be a bundled local vista packet. It should carry: the source state's outgoing `1`-hop edge set, the corresponding outgoing target states, any labels attached to those outgoing edges, and the current contraction/coset marks needed to interpret them upstairs. In short: the payload should carry newly available outgoing-edge possibility data, not just labels or notes in isolation.
            - **PO Answer:** Correct.

Current options:

- full local outgoing-neighborhood data
- labels only
- notes only
- contraction marks only
- bundled local vista packet containing several of these

Why this matters:

- payload size affects runtime complexity
- payload semantics determine whether contraction-as-information-equalization is honest or superficial

Review question:

- What is the minimal honest payload that still captures the intended push-pull semantics?

### 5. Exact Trustworthiness Heuristic

Open question:

- What should make a tier trustworthy enough to be used first by training/control logic?
    - **PO Answer:** I just don't understand what you're asking here. Please explain what the concern is here.
        - *LLM Answer*: The concern is this: your control principle says the agent should use the lowest trustworthy tier first. For code, that means we need a rule that decides when a tier is mature enough that the agent is allowed to rely on it. Without such a rule, the runtime cannot decide whether to act using base-tier detail or using a coarser tier. So the question is not philosophical; it is a runtime gating question. My recommendation for the first implementation is a simple heuristic: a tier is trustworthy at the current position if the current quotient node has at least a minimum number of observed member states or edges, has nonempty pushed/pulled outgoing-vista knowledge, and has at least one known outgoing quotient edge with reward statistics attached. That gives us a first binary rule we can later replace.
            - **PO Answer:** Oh I see. No. The full tier is always constructed, meaning that the sequence of edge contractions that get us down to a point are always all implemented when a new node is discovered. An episode always works lowest tier to highest tier via lifts. So like... agent stake sstep in lowest tier, then that is lefted to next, ... all the way to top, then at top tier, we're working with actual hidden states. We move to existing state already in discovered graph, or else we find a new state and add node. If we add a new node, we do sequence of contractions, effectively adding to whole tower. Then we repeat, starting at bottom tier. That is one step in episode. Also, this maybe makes the `gymnasium` interface more clear.
                - *LLM Answer*: Yes, this removes most of the earlier trustworthiness concern. If every new discovered state triggers a full immediate tower update all the way through the contraction sequence, and each episode step always runs bottom-tier to top-tier via lifts, then trustworthiness is not primarily a maturity-gating problem. In that implementation picture, the full current tower is always available by construction. So for version `1`, I recommend downgrading `TrustworthinessPolicy` from a central control dependency to an optional extension point. We can keep the contract in the document for future use, but the first implementation does not need to rely on it to decide whether a tier may be used. The tower is simply the current fully updated tower.
                    - **PO Answer:** Yes. I agree.

Current possibilities:

- minimum number of supporting member edges
- minimum reward sample count
- minimum local vista coverage
- minimum equalization completeness
- combination score over several signals

Why this matters:

- the training-time control principle depends on it
- coarse-versus-fine action choice depends on it

Review question:

- What should the first operational definition of local tier trustworthiness be?

### 6. Exact First Contraction Policy Implementation

Open question:

- Which contraction policy should be implemented first?
    - **PO Answer:** Both from day one.
        - *LLM Answer*: I agree. Both should be implemented from day one, because they are two instances of the same policy interface and implementing both immediately tests whether the abstraction is real rather than accidental. The first implementation should therefore ship with at least: one label-based `ContractionPolicy` and one seeded-random `ContractionPolicy`.
            - **PO Answer:** Yes. I agree.

Current possibilities:

- label-based contraction
- random edge-family sampling
- both from day one

Why this matters:

- this determines the first honest demonstration of tower construction
- it also determines how much policy-pluggability is exercised immediately

Review question:

- Should the first implementation start with label-based contraction, random contraction, or both?

### 7. Exact First Toy Environment

Open question:

- What is the smallest honest environment that exercises the actual package idea?
    - **PO Answer:** I don't understand. Please explain.
        - *LLM Answer*: This question is asking: what is the smallest toy problem we can build that genuinely exercises the package's mathematical mechanism, instead of only testing interfaces? We need one environment small enough to understand completely, but rich enough to show hidden graph, local `1`-hop vista, push-pull, contraction, tower update, and reward descent. My recommendation is a small labeled directed lattice or grid-world-like environment with writable node notes and explicit edge labels. This is better than a purely abstract hand-written graph because it gives us local geometry, labels for contraction, and simple reward on primitive actions, while still being small enough to inspect visually.
            - **PO Answer:** Ah I understand. ...So good types of toy problems would be things that look very much like they could come from an industrial "robot constraint space is hard to parametrize" issue. So what I have in mind is a robot arm that needs to learn how to best navigate some set of contraints that make its parameter space opaque. The reason this type of toy problem is a good start is because its a case where we feel like the ambient parameter reduction suggests some induced reduciton, but we can't name the reduction explicitly because we can't find new parameters. This example is also nice because we can play with cases where in *some* behavorial regions, we've foudn aparametrization so that we can do some label-based reduction in tower construction.
                - *LLM Answer*: I think this is an excellent direction for the first honest toy environment. It is much better than a purely abstract graph toy, because it already looks like the kind of constrained opaque state space that would motivate the package in practice. My recommendation is: make the first toy environment a discretized robot-arm-style constraint navigation problem with a small enough state space to inspect, but with locally meaningful transition structure, partial regional parameterizability, and edge labels available only in some regions. That would let the first implementation test both random contraction and label-based contraction in the same environment, which is unusually valuable.
                    - **PO Answer:** Yes. I like this.

The first toy environment should ideally exercise:

- hidden graph
- explored graph
- local `1`-hop vista
- push-pull message passing
- contraction
- tower update
- reward descent

Why this matters:

- the first vertical slice will only be convincing if the toy environment actually exercises the core mathematics

Review question:

- What should the first toy environment be?

### 8. Exact Trainer/Control Handoff

Open question:

- What object should the runtime return after each step for training or control logic?
    - **PO Answer:** I don't understand. Please clarify.
        - *LLM Answer*: The issue is that after one primitive action and one full tower update, some downstream piece of code needs to receive the result and decide what to do next. So we need to decide what the stable output of `TowerRuntime.step(...)` is. My recommendation is that it should return a full `RuntimeSnapshot`. That snapshot should contain the current base state, the updated explored and vista graphs, the current quotient tiers, the current position at each tier, and the current reward summaries. Gymnasium-style tuples or trainer-specific views can then be derived from the snapshot, rather than making the runtime itself commit too early to one downstream interface.
            - **PO Answer:** Yes. This sounds correct to me.

Current possibilities:

- full runtime snapshot
- base transition plus tier metadata
- tier-indexed observation bundle
- Gymnasium-style tuple plus tower-side info

Why this matters:

- adapter shape depends on it
- trainer implementation depends on it
- public-facing interoperability depends on it

Review question:

- What should be the stable handoff object from `TowerRuntime.step(...)`?

## Final Contract Statement

If the package obeys the contracts in this document, then code scaffolding should be able to proceed without major interpretive ambiguity.

That is the purpose of this document.

## Post-Mortem On The Review Questions

This section records the implementation consequences of the question-and-answer review above.

Its job is to state what new implementation realities have become clear, and what parts of the current contracts or surrounding design docs should now be interpreted differently or strengthened.

### 1. The hidden runtime value of this review

The review questions clarified that the package implementation should not be designed around a naive picture in which:

- quotient tiers are merely separate graph snapshots
- a coarse tier is consulted only intermittently
- message passing is a decorative side effect
- trustworthiness is the main gating mechanism for whether a tier may be used

Instead, the review clarified a stronger runtime picture:

- the tower is updated fully at every step
- contraction consequences are propagated all the way through the current tower immediately
- tier data is nested and cumulative
- the agent's effective tier query is often cumulative in the sense of "`<= k`" rather than "exactly `k`"
- the package's special value relative to `gymnasium` is precisely this realtime graph-discovery, vista, quotient, and tower-update machinery

This means the first implementation should be built less like a collection of independent graph utilities and more like a runtime graph-and-annotation engine.

### 2. `gymnasium` should be treated as a shell, not as a competing graph layer

One implementation concern raised in the review was whether the package might accidentally re-implement functionality that already exists in `gymnasium`.

The review clarified that it is not.

`gymnasium` provides:

- reset/step interaction
- observation and action surfaces
- reward return
- episode boundaries

What `state_collapser` adds is:

- the realtime discovered graph `G^0_t`
- the explored graph / vista graph distinction
- local `1`-hop query machinery
- contraction/equalization
- full tower update after each new discovered state
- cross-tier position tracking
- nested accumulated outgoing-edge knowledge

Implementation consequence:

- the first code scaffold should keep `gymnasium` adapters thin
- the main runtime and graph layers should be package-native

This is already directionally present in the docs, but should now be treated as an implementation invariant rather than only a design intention.

### 3. The state object should stay minimal and stable

The review confirmed:

- use a frozen dataclass first
- keep `State` as a minimal mathematical locus
- do not place changing notes or contraction decorations inside the base state identity

Implementation consequence:

- the first `State` contract should be a small immutable record
- all changing graph/runtime/tower information should be stored in overlay structures keyed by stable state identity

This is already reflected in the document, but the review makes it a stronger decision rather than a mere recommendation.

### 4. Node annotation storage must be designed for speed

The review added an important constraint to the annotation-store decision:

- the annotation store is not only conceptually cleaner outside the state
- it must also support fast local message passing and fast cumulative query

The review also clarified that:

- arbitrary labels should remain valid at the contract level
- later numeric encodings for fast matrix or CUDA-backed update should be treated as optional optimization layers

Implementation consequences:

- `NodeAnnotationStore` should be designed as a first-class performance-sensitive structure
- the core contract must not require numeric-only labels
- but the runtime should leave room for encoded numerical views of labels and messages

This is not yet fully reflected in the rest of the docs and should be carried into actual module design.

### 5. Quotient tiers are nested accumulated views, not isolated levels

The most important structural correction from the review is:

- quotient tiers should not be modeled as isolated outgoing-edge worlds
- coset and outgoing-edge data accumulates and nests as one moves down the tower

So a query at tier `k` is not merely:

- "what are my outgoing edges at exactly tier `k`?"

It is more like:

- "what outgoing-edge knowledge has accumulated through tiers `0` through `k`?"

Implementation consequences:

- tier data structures must support cumulative outgoing-edge knowledge
- quotient annotations should be stored in a way that permits "`<= k`"-style queries
- cross-tier runtime query should be thought of as cumulative annotation-following, not simple tier swapping

This is a real change in how the quotient storage section should be interpreted.

The code should still use explicit tier-view objects in version `1`, but those objects should be understood as nested cumulative views over one shared discovered graph.

### 6. The message payload should be interpreted as skip-capability propagation

The review sharpened the meaning of push/pull.

The message payload is not generic "context." It is specifically the propagation of newly available outgoing-edge possibilities across a coset-like region so that nodes can move "as if in quotient."

Implementation consequences:

- the `VistaPayload` contract should be interpreted operationally as outgoing-edge possibility data
- push/pull should propagate:
  - outgoing edge possibilities
  - corresponding target states
  - labels and contraction marks needed to interpret those possibilities
- the payload design should support cumulative nested skip knowledge

This means the initial implementation should avoid an anemic payload design that carries only loose metadata.

### 7. Collapsed internal edges should be excluded from quotient-edge reward aggregation

The review added an important reward clarification:

- when a region is collapsed, internal collapsed edges should not contribute as outgoing quotient-edge reward transitions

For example, if

- `A -> B -> C -> D`

collapses so that `[B,C]` is one quotient node, then the relevant boundary-crossing edges determine quotient-edge reward contributions, not the internal edge `B -> C`.

Implementation consequences:

- quotient reward aggregation code must distinguish:
  - internal collapsed member edges
  - boundary-crossing preimage edges
- only the latter should contribute to outgoing quotient-edge reward summaries

This consequence should later be propagated into the reward-design documents as well, because it is a real operational restriction.

### 8. Full tower update at every step reduces the immediate role of trustworthiness

The review substantially changed the role of the trustworthiness question.

Originally, `TrustworthinessPolicy` was treated as a likely central runtime gate for whether a tier may be used.

But the clarified runtime picture is:

- every new discovered state triggers the full contraction sequence
- the whole current tower is updated immediately
- an episode step proceeds from lowest tier upward via lifts

Implementation consequence:

- `TrustworthinessPolicy` should remain in the contracts as an extension point
- but it should be downgraded in the first implementation from central dependency to optional future policy surface

This means version `1` does not need a complex trust-scoring subsystem in order to be faithful to the current model.

That is a meaningful simplification.

### 9. Both contraction-policy families should exist from day one

The review settled that the first implementation should include:

- label-based contraction
- random edge-family sampling

Implementation consequence:

- the code scaffold should include at least two concrete `ContractionPolicy` implementations immediately
- tests should verify that both run through the same runtime update pipeline

This is important because it tests whether the policy abstraction is genuine.

### 10. The first toy environment should be robot-constraint-flavored, not purely abstract

The review improved the toy-environment choice significantly.

The first toy environment should not just be a bare graph puzzle.

It should resemble:

- an opaque constraint navigation problem
- something like a discretized robot-arm state/constraint space
- a setting where some local parameter reductions exist, but no clean global reduction is available

Implementation consequences:

- the first toy environment should be designed to support:
  - hidden graph semantics
  - local `1`-hop query
  - regionally available labels
  - both random and label-based contraction
  - reward on primitive transitions
- this environment should likely become the main first end-to-end example and test fixture

This is a stronger and more honest first implementation target than a purely abstract synthetic graph.

### 11. `TowerRuntime.step(...)` should return a full snapshot

The review confirmed that the stable runtime handoff should be:

- a full `RuntimeSnapshot`

Implementation consequence:

- the runtime should not directly commit to Gymnasium-style tuples internally
- adapters may derive Gymnasium-style or trainer-specific views from the snapshot later

This is a good architectural outcome because it keeps the package's own runtime semantics explicit.

### 12. New implementation tasks implied by the review

The answered questions imply several concrete implementation tasks that are not yet fully spelled out elsewhere in the docs.

These should now be treated as real next-step engineering work:

1. define a `NodeAnnotationStore` API that supports fast cumulative tier-indexed update and query
2. define a `VistaPayload` object around outgoing-edge possibility propagation
3. define cumulative nested outgoing-edge query semantics by tier
4. define explicit quotient-tier view objects as nested cumulative overlays over the shared discovered graph
5. define clear separation between:
   - internal collapsed member edges
   - boundary-crossing quotient-edge contributors
6. downgrade trustworthiness from a required first-pass runtime dependency to an optional extension point
7. scaffold two concrete contraction policies immediately
8. design the first robot-constraint-style toy environment as the main vertical-slice proving ground
9. ensure the `RuntimeSnapshot` contract is rich enough to support later adapters cleanly

### 13. Documents that should eventually be updated in light of this review

This document now contains the most precise consequences of the review.

But some of these consequences are not yet fully propagated into the rest of the docs.

The most important later doc updates should likely be:

- `module_design_desiderata.md`
  - to emphasize more strongly that tier queries are cumulative and nested
- `package_best_practices_proposal.md`
  - to reflect `TowerRuntime` more strongly as a graph-and-annotation runtime engine
- `reward_locality_for_quotient_training.md`
  - to note explicitly that internal collapsed edges should be excluded from outgoing quotient-edge reward aggregation

### 14. Final post-mortem conclusion

The review questions did not expose major conceptual instability.

Instead, they did something more useful:

- they forced the runtime picture to become sharper
- they reduced the role of some unnecessary abstractions
- they identified several concrete data-structure and query requirements that now need to be implemented honestly

The largest implementation shift produced by the review is this:

- the first version of `state_collapser` should be implemented not mainly as a collection of quotient graph utilities, but as a realtime nested annotation-and-query engine over a shared discovered graph, with tiered quotient views derived from that engine

That should guide the next code-scaffolding step.
