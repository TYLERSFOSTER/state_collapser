# state_collapser System Flowcharts And Control Flow

Date: 2026-05-30

Status: repo-crawl architecture/control-flow map

## Purpose

This document is a Mermaid-heavy map of how the current `state_collapser`
package works in code. It is grounded in the package source as of the v0.7-era
runtime, after the Young-diagram/partition-tower refactor and tensorization
boundary work.

The main point:

```text
state_collapser is not an RL algorithm runner.
state_collapser is a structural runtime layer around a discovered transition graph.
```

The package discovers or receives graph structure, maintains a nested
state/action partition tower over the discovered base graph, exposes snapshots
and tower-aware decision inputs, and optionally converts those semantic objects
into numeric records or Torch batches at learner/benchmark boundaries.

## Source Files Used For This Crawl

Primary source files:

- `src/state_collapser/core/*`
- `src/state_collapser/graph/*`
- `src/state_collapser/tower/runtime.py`
- `src/state_collapser/tower/snapshot.py`
- `src/state_collapser/tower/partition/*`
- `src/state_collapser/tower/control/*`
- `src/state_collapser/training/*`
- `src/state_collapser/adapters/gymnasium.py`
- `src/state_collapser/examples/*/{env,runtime,training}.py`
- `src/state_collapser/benchmarks/tower_runtime_bench.py`

Design/usage context:

- `README.md`
- `docs/usage/01_010_tensorization_boundary.md`
- `docs/design/tensorization/*`
- `docs/design/Young_tableaux_refactor/*`
- `docs/design/RL_framework_maturity/*`

## Whole Package Layer Map

```mermaid
flowchart TD
    User["User code / examples / downstream package"] --> Entry["Public entry surfaces"]

    Entry --> Examples["state_collapser.examples"]
    Entry --> Adapter["state_collapser.adapters.gymnasium"]
    Entry --> Training["state_collapser.training"]
    Entry --> Bench["state_collapser.benchmarks"]
    Entry --> TowerDirect["Direct tower/partition APIs"]

    Examples --> Env["Example env.py<br/>domain state/action/reward"]
    Examples --> RuntimeBinding["Example runtime.py<br/>env -> HiddenGraph -> TowerRuntime"]
    Examples --> ExampleTraining["Example training.py<br/>small reference loops"]

    Adapter --> Wrapper["StateCollapserGymWrapper<br/>records realized transitions"]

    TowerDirect --> Core["state_collapser.core<br/>State / PrimitiveAction / BaseEdge / rewards"]
    RuntimeBinding --> Core
    Wrapper --> Core

    Core --> Graph["state_collapser.graph<br/>HiddenGraph / ExploredGraph / VistaGraph"]
    Graph --> TowerRuntime["TowerRuntime<br/>explore, refresh vista, maintain tower"]

    TowerRuntime --> PartitionTower["PartitionTower<br/>registry + nested state/action partition layers"]
    PartitionTower --> Readouts["Compatibility QuotientTierView readouts"]
    TowerRuntime --> Snapshot["LiveRuntimeView / RuntimeSnapshot"]

    Snapshot --> Training
    Training --> DecisionInput["ActionSelectionInput"]
    Training --> Transition["TrainingTransition"]
    Training --> Collectors["StepCollector / EpisodeCollector"]
    Training --> ReferenceLoops["run_reference_online_loop<br/>run_reference_episode_loop"]
    Training --> Learner["Learner protocol / TabularQLearner"]
    Training --> FiberStage["FiberConditionedStage"]
    Training --> Linearization["training.linearization<br/>EncodingRegistry / Linearized records / reports"]
    Linearization --> TorchBoundary["training.torch<br/>optional Torch batches"]

    Bench --> TowerRuntime
    Bench --> PartitionTower

    Downstream["HGraphML / graph dataflow downstream"] --> PartitionTower
    Downstream --> Linearization
```

## Conceptual Ownership Map

```mermaid
flowchart LR
    EnvOwn["Environment owns<br/>domain transition semantics"] --> HiddenGraph["HiddenGraph protocol<br/>package-facing transition surface"]
    HiddenGraph --> RuntimeOwn["TowerRuntime owns<br/>discovery loop + tower maintenance"]
    RuntimeOwn --> TowerOwn["PartitionTower owns<br/>nested partition structure"]
    TowerOwn --> TrainingOwn["Training surfaces own<br/>decision input / transition contracts"]
    TrainingOwn --> LearnerOwn["User or example learner owns<br/>model, loop policy, optimizer, replay"]
    TrainingOwn --> TensorOwn["Linearization owns<br/>semantic-to-numeric conversion"]

    RuntimeOwn -. "does not own" .-> LearnerOwn
    TowerOwn -. "does not own" .-> EnvOwn
    TensorOwn -. "does not own" .-> RuntimeOwn
```

## Core Runtime Control Flow

`TowerRuntime` is the main object-native runtime coordinator. It binds:

- a `HiddenGraph`;
- an `ExploredGraph`;
- a `VistaGraph`;
- optional local-star `ContractionPolicy` annotation behavior;
- a partition-tower `ContractionSchema`;
- a `PartitionTower`;
- and snapshot production.

```mermaid
sequenceDiagram
    participant Caller
    participant Runtime as TowerRuntime
    participant Hidden as HiddenGraph
    participant Explored as ExploredGraph
    participant Vista as VistaGraph
    participant Tower as PartitionTower
    participant View as LiveRuntimeView

    Caller->>Runtime: reset(initial_state)
    Runtime->>Explored: new ExploredGraph()
    Runtime->>Vista: new VistaGraph(hidden, explored)
    alt initial state provided
        Runtime->>Explored: add_state(initial_state)
        Runtime->>Vista: refresh_local_vista(initial_state)
    end
    Runtime->>Tower: initialize(visible states, visible edges, current_state)
    Tower-->>Runtime: TowerUpdateResult
    Runtime-->>Caller: LiveRuntimeView

    Caller->>Runtime: step(PrimitiveAction)
    Runtime->>Explored: current_state()
    Runtime->>Hidden: apply_action(current_state, action)
    Hidden-->>Runtime: next_state
    Runtime->>Explored: add_edge(BaseEdge(current, action, next))
    Runtime->>Vista: refresh_local_vista(current_state)
    Runtime->>Vista: refresh_local_vista(next_state)
    opt contraction_policy configured
        Runtime->>Vista: local-star read
        Runtime->>Vista: push/pull selected outgoing info
    end
    Runtime->>Tower: update_with_delta(new visible states/edges, current_state=next)
    Tower-->>Runtime: TowerUpdateResult
    Runtime->>Runtime: compute primitive step reward and cumulative reward
    Runtime-->>Caller: LiveRuntimeView
```

## Runtime Step Flowchart

```mermaid
flowchart TD
    Start["TowerRuntime.step(action)"] --> Current["Read current base state<br/>from ExploredGraph"]
    Current --> HasCurrent{"Current state exists?"}
    HasCurrent -- no --> ErrorNoReset["raise ValueError:<br/>call reset first"]
    HasCurrent -- yes --> Apply["HiddenGraph.apply_action(current, action)"]
    Apply --> HasNext{"Successor exists?"}
    HasNext -- no --> ErrorNoSuccessor["raise ValueError:<br/>invalid primitive action"]
    HasNext -- yes --> Edge["Create BaseEdge(current, action, next)"]
    Edge --> Record["ExploredGraph.add_edge(edge)"]
    Record --> RefreshA["VistaGraph.refresh_local_vista(current)"]
    RefreshA --> RefreshB["VistaGraph.refresh_local_vista(next)"]
    RefreshB --> Policy{"ContractionPolicy configured?"}
    Policy -- yes --> LocalStar["Build LocalStar from vista edges/neighbors"]
    LocalStar --> Select["policy.select(local_star)"]
    Select --> Messages["push_message / pull_message<br/>annotation payloads"]
    Policy -- no --> Backend
    Messages --> Backend{"tower_backend"}
    Backend -- partition --> Delta["PartitionTower.update_with_delta(...)"]
    Backend -- legacy --> Legacy["build_legacy_dynamic_tower(...)"]
    Delta --> ApplyResult["Refresh runtime fields:<br/>positions, selected edges, update result"]
    Legacy --> ApplyResult
    ApplyResult --> Reward["Compute StepReward and PathRewardSummary"]
    Reward --> View["Return LiveRuntimeView"]
```

## Hidden / Explored / Vista Graph Roles

```mermaid
flowchart LR
    Hidden["HiddenGraph<br/>complete environment transition oracle"] -->|apply_action| Runtime["TowerRuntime"]
    Hidden -->|out_edges(state)| Vista["VistaGraph<br/>one-hop visible fringe"]
    Runtime --> Explored["ExploredGraph<br/>visited states, edges, path"]
    Runtime --> Vista
    Vista -->|vista_edges / vista_neighbors| Runtime
    Vista -->|node_payload annotations| Runtime

    Explored -->|visited_states / visited_edges| Visible["Visible base graph"]
    Vista -->|cached outgoing edges for visited states| Visible
    Visible --> PartitionTower["PartitionTower registry + layers"]
```

## Partition Tower Data Model

The partition tower is the runtime form of the paper's nested state/action
coset system. The important implementation choice is that the base graph is not
copied into quotient graphs at every tier. Instead:

- `BaseGraphRegistry` stores stable ids for base states, edges, and actions;
- each `StatePartitionLayer` stores one partition of state ids at one tier;
- each `ActionPartitionLayer` stores outgoing-action collections and action
  cells aligned with the state cells at that tier;
- `ContractionSchema` assigns base edges to ordered contraction blocks;
- `TowerUpdateResult` records deltas, merges, internal edges, diagnostics, and
  optional morphism data.

```mermaid
classDiagram
    class PartitionTower {
      schema
      loop_policy
      reward_aggregator
      registry
      schema_assignment_store
      state_layers
      action_layers
      initialize()
      update_with_delta()
      current_position_at_every_tier()
      outgoing_action_cells()
      lift_candidates()
      refinement_fiber()
      to_quotient_tier_views()
    }

    class BaseGraphRegistry {
      state_id_by_state
      edge_id_by_edge
      action_id_by_identity
      outgoing_edge_ids_by_state_id
      register_delta()
      source_state_id()
      target_state_id()
      action_for_edge_id()
    }

    class StatePartitionLayer {
      tier_index
      cell_of_state_id
      members_by_cell_id
      previous_cells_by_cell_id
      singleton_layer()
      carry_forward_from()
      merge_cells()
    }

    class ActionPartitionLayer {
      tier_index
      outgoing_collection_by_state_cell
      edge_ids_by_collection
      edge_ids_by_action_cell
      internal_edge_ids_by_state_cell
      carry_forward_from()
      merge_collections()
      rebuild_action_cells_for_collection()
    }

    class SchemaAssignmentStore {
      schema
      assignment_by_edge_id
      edge_ids_by_block
      assign_edges()
      edges_in_block()
    }

    class TowerUpdateResult {
      changed
      delta_state_ids
      delta_edge_ids
      schema_assignments
      affected_tiers
      state_merges
      action_merges
      internal_edges
      current_position_by_tier
      morphism
      diagnostics
    }

    PartitionTower --> BaseGraphRegistry
    PartitionTower --> SchemaAssignmentStore
    PartitionTower --> StatePartitionLayer
    PartitionTower --> ActionPartitionLayer
    PartitionTower --> TowerUpdateResult
```

## Partition Tower Full Build

Full build is used by `PartitionTower.initialize(...)` and by
`build_partition_tower_full(...)` when a caller already has discovered graph
data.

```mermaid
flowchart TD
    Start["PartitionTower.initialize(states, edges, current_state)"] --> Register["BaseGraphRegistry.register_delta(states, edges)"]
    Register --> Assign["SchemaAssignmentStore.assign_edges(new_edge_ids)"]
    Assign --> State0["StatePartitionLayer.singleton_layer(tier=0)"]
    State0 --> Action0["ActionPartitionLayer.from_state_layer_and_registry(tier=0)"]
    Action0 --> Blocks["For each ordered schema block<br/>create next tier"]

    Blocks --> CarryState["StatePartitionLayer.carry_forward_from(previous, tier=i)"]
    CarryState --> CarryAction["ActionPartitionLayer.carry_forward_from(previous, new_state_layer, tier=i)"]
    CarryAction --> ContractLoop["For each edge assigned to block i"]
    ContractLoop --> Contract["contract_edge_in_layer(edge, tier=i)"]
    Contract --> MergeState["StatePartitionLayer.merge_cells(source_cell, target_cell)"]
    MergeState --> MergeAction["ActionPartitionLayer.merge_collections(source_collection, target_collection)"]
    MergeAction --> LoopPolicy["Record/drop internal loop edges by LoopPolicy"]
    LoopPolicy --> Dirty["Mark action collections dirty"]
    Dirty --> MoreEdges{"More block edges?"}
    MoreEdges -- yes --> ContractLoop
    MoreEdges -- no --> Rebuild["Rebuild dirty action cells"]
    Rebuild --> Append["Append tier-i state/action layers"]
    Append --> MoreBlocks{"More schema blocks?"}
    MoreBlocks -- yes --> Blocks
    MoreBlocks -- no --> Result["Build TowerUpdateResult<br/>diagnostics + current position"]
```

## Partition Tower Incremental Update

Incremental update is the hot-path version used after exploration. The runtime
passes only newly visible local graph data into `update_with_delta`.

```mermaid
flowchart TD
    Start["PartitionTower.update_with_delta(delta_states, delta_edges)"] --> MaybeMorphism{"build_morphism?"}
    MaybeMorphism -- yes --> Capture["Capture old active cell domain"]
    MaybeMorphism -- no --> Register
    Capture --> Register["BaseGraphRegistry.register_delta(...)"]

    Register --> Assign["Assign only new edge ids to schema blocks"]
    Assign --> NewStates["Add new states as singleton cells to existing layers"]
    NewStates --> InsertEdges["Insert new edges into existing action collections"]
    InsertEdges --> Internal0{"Edge internal in a tier?"}
    Internal0 -- yes --> RecordInternal["Record internal edge by loop policy"]
    Internal0 -- no --> DirtyCollection["Mark source outgoing collection dirty"]

    RecordInternal --> Scheduled
    DirtyCollection --> Scheduled["For each scheduled new edge"]
    Scheduled --> HasBlock{"Assigned block?"}
    HasBlock -- no --> RebuildDirty
    HasBlock -- yes --> EnsureTier["Ensure scheduled tier exists"]
    EnsureTier --> ContractDown["Contract edge from scheduled tier downward"]
    ContractDown --> StateMerge["Merge state cells if endpoints differ"]
    StateMerge --> ActionMerge["Merge outgoing action collections"]
    ActionMerge --> InternalAfter["Record edges becoming internal loops"]
    InternalAfter --> MoreScheduled{"More scheduled edges?"}
    MoreScheduled -- yes --> Scheduled
    MoreScheduled -- no --> RebuildDirty["Rebuild dirty action cells on affected tiers"]
    RebuildDirty --> Morphism{"morphism domain captured?"}
    Morphism -- yes --> BuildMorphism["Build old-cell -> new-cell image maps"]
    Morphism -- no --> EmptyMorphism["Use empty TowerMorphism"]
    BuildMorphism --> Result
    EmptyMorphism --> Result["Return TowerUpdateResult"]
```

## State/Action Coarsening At One Edge

This diagram is the lowest-level "what happens when an edge contracts" view.

```mermaid
flowchart TD
    Edge["edge_id"] --> Source["registry.source_state_id(edge_id)"]
    Edge --> Target["registry.target_state_id(edge_id)"]
    Source --> SourceCell["state_layer.cell_of(source_state_id)"]
    Target --> TargetCell["state_layer.cell_of(target_state_id)"]
    SourceCell --> Same{"source_cell == target_cell?"}
    TargetCell --> Same
    Same -- yes --> Noop["No state merge<br/>edge is already internal at this tier"]
    Same -- no --> SourceColl["action_layer.outgoing_collection(source_cell)"]
    Same -- no --> TargetColl["action_layer.outgoing_collection(target_cell)"]
    SourceColl --> MergeState["state_layer.merge_cells(source_cell, target_cell)"]
    TargetColl --> MergeState
    MergeState --> MergeAction["action_layer.merge_collections(source_coll, target_coll, merged_cell)"]
    MergeAction --> LiveEdges["Live outgoing edge set = union minus new internal loops"]
    MergeAction --> InternalEdges["Internal edges recorded by LoopPolicy"]
    LiveEdges --> Dirty["collection marked dirty"]
    Dirty --> Rebuild["rebuild_action_cells_for_collection"]
    Rebuild --> ActionCells["Action cells grouped by<br/>source cell + target cell + action identity"]
```

## Action-Side Table Meaning

```mermaid
flowchart LR
    StateCell["StateCellId<br/>one coset/state partition cell"] --> Collection["ActionCollectionId<br/>storage-level outgoing edge set"]
    Collection --> ActionCellA["ActionCellId<br/>abstract decision action"]
    Collection --> ActionCellB["ActionCellId<br/>abstract decision action"]
    Collection --> Internal["internal_edge_ids<br/>loops inside state cell"]

    ActionCellA --> EdgeSetA["base EdgeId set"]
    ActionCellB --> EdgeSetB["base EdgeId set"]
    EdgeSetA --> Registry["BaseGraphRegistry<br/>recover BaseEdge objects"]
    EdgeSetB --> Registry

    ActionCellA -. "lift_candidates" .-> PrimitiveEdges["representative or directly executable BaseEdge"]
```

## Compatibility Quotient Readouts

`PartitionTower` is the source of truth. `QuotientTierView` objects are derived
compatibility readouts for older callers and tests.

```mermaid
flowchart TD
    PartitionTower["PartitionTower<br/>registry + nested partition layers"] --> Request["TowerRuntime.compatibility_quotient_tiers()"]
    Request --> Cache{"cached readout exists?"}
    Cache -- yes --> ReturnCached["Return cached QuotientTierView tuple"]
    Cache -- no --> Build["partition.readout.to_quotient_tier_views(tower)"]
    Build --> Views["QuotientTierView compatibility objects"]
    Views --> CacheStore["Store on runtime until next tower update"]
    CacheStore --> Return["Return readouts"]
    PartitionUpdate["Partition update"] -. "invalidates cache" .-> Request
```

## Snapshot And Training Input Flow

```mermaid
flowchart TD
    RuntimeStep["TowerRuntime.reset/step"] --> Live["LiveRuntimeView<br/>live graph/tower references"]
    Live --> Snapshot["RuntimeSnapshot<br/>small serializable value view"]
    Live --> Collector["StepCollector / EpisodeCollector"]
    Collector --> Input["build_action_selection_input(...)"]
    Input --> ASI["ActionSelectionInput<br/>observation + base state + tower_position_key + mask + diagnostics"]
    ASI --> Learner["Learner.act(input)"]
    Learner --> Decision["ActionDecision"]
    Decision --> CollectorStep["StepCollector.collect_step(source_input, decision)"]
    CollectorStep --> RuntimeStep2["runtime.step(chosen_action)"]
    RuntimeStep2 --> NextInput["next ActionSelectionInput"]
    NextInput --> Transition["TrainingTransition<br/>source, action, reward, target, termination, bootstrap"]
    Transition --> LearnerObserve["Learner.observe(transition)"]
    LearnerObserve --> LearnerUpdate["Learner.update()"]
```

## Reference Online Training Loop

```mermaid
sequenceDiagram
    participant Loop as run_reference_online_loop
    participant Collector as StepCollector
    participant Runtime
    participant Learner
    participant Metrics as TrainingMetrics

    Loop->>Collector: reset_episode(seed)
    Collector->>Runtime: reset(seed)
    Runtime-->>Collector: reset result + LiveRuntimeView
    Collector-->>Loop: ActionSelectionInput

    loop up to max_steps_per_episode
        Loop->>Learner: act(current_input, mode="train")
        Learner-->>Loop: ActionDecision
        Loop->>Collector: collect_step(current_input, decision)
        Collector->>Runtime: step(chosen_action)
        Runtime-->>Collector: step result + LiveRuntimeView
        Collector-->>Loop: CollectedStep + TrainingTransition
        Loop->>Learner: observe(transition)
        Loop->>Learner: update()
        alt terminated or truncated
            Loop->>Loop: break episode
        end
    end

    Loop->>Metrics: on_episode_end(EpisodeMetrics)
    Loop-->>Caller: ReferenceLoopResult
```

## Example Environment Runtime Pattern

The example packages follow a repeated shape:

```text
env.py      domain environment, state, transition, rewards
runtime.py  HiddenGraph adapter + TowerRuntime binding
training.py small reference/tabular loops
```

```mermaid
flowchart TD
    EnvPy["example/env.py<br/>domain state + transition + reward"] --> HiddenAdapter["example/runtime.py<br/>ExampleHiddenGraph"]
    EnvPy --> EnvInstance["ExampleEnv"]
    HiddenAdapter --> TowerRuntime["TowerRuntime(hidden_graph=ExampleHiddenGraph)"]
    EnvInstance --> RuntimeBinding["ExampleEnvRuntime"]
    TowerRuntime --> RuntimeBinding
    RuntimeBinding --> Reset["reset() -> observation, info, LiveRuntimeView"]
    RuntimeBinding --> Step["step(action_index) -> observation, reward, done flags, info, LiveRuntimeView"]
    Reset --> TrainingPy["example/training.py"]
    Step --> TrainingPy
    TrainingPy --> SharedLoop["run_shared_tower_training / package reference loops"]
```

## Plate Support Example Flow

```mermaid
flowchart TD
    User["run_tower_training(env=PlateSupportEnv(), config=...)"] --> CreateRuntime["PlateSupportEnvRuntime"]
    CreateRuntime --> Env["PlateSupportEnv"]
    CreateRuntime --> Hidden["PlateSupportHiddenGraph"]
    CreateRuntime --> TowerRuntime["TowerRuntime<br/>schema=default_plate_support_schema"]
    User --> Shared["run_shared_tower_training"]
    Shared --> Learner["TabularQLearner<br/>key=tower_position_key"]
    Shared --> RefLoop["run_reference_online_loop"]
    RefLoop --> StepCollector["StepCollector"]
    StepCollector --> RuntimeReset["PlateSupportEnvRuntime.reset"]
    RuntimeReset --> EnvReset["env.reset"]
    RuntimeReset --> TowerReset["tower_runtime.reset(initial_core_state)"]
    StepCollector --> RuntimeStep["PlateSupportEnvRuntime.step(action_index)"]
    RuntimeStep --> EnvStep["env.step(action_index)"]
    RuntimeStep --> TowerStep["tower_runtime.step(PrimitiveAction(action_index))"]
    TowerStep --> Snapshot["LiveRuntimeView with current_position_at_every_tier"]
    Snapshot --> Input["ActionSelectionInput"]
    Input --> Learner
```

## Exploit / Explore Active-Tier Runtime

This path is separate from the simpler reference loops. It demonstrates
single-active-tier control and freeze/lift machinery with small tabular
components.

```mermaid
flowchart TD
    Start["ExploitExploreTowerRuntime.step()"] --> Signal["Get TierSignalState for active tier"]
    Signal --> Config["Read TierControlConfig"]
    Config --> Frozen["Read FrozenLowerContext"]
    Frozen --> Due["learner.should_train(event_index)"]
    Due --> Decide["ActiveTierController.decide(...)"]
    Decide --> Action{"ControlAction"}

    Action -- LIFT --> MoveUp["move_up(active_tier_state)"]
    Action -- DESCEND --> MoveDown["move_down(active_tier_state)"]
    Action -- TRAIN --> Train["learner.train(frozen_context)"]
    Action -- EXPLORE --> BehaviorExplore["learner.behavior_action(mode='explore')"]
    Action -- EXPLOIT_EXECUTE --> BehaviorExploit["learner.behavior_action(mode='exploit')"]

    BehaviorExplore --> Execute["LiftResolveExecutor.execute(...)"]
    BehaviorExploit --> Execute
    Execute --> Observe["learner.observe(transition, frozen_context)"]
    Train --> UpdateSignal["record td_error / success / residual"]
    Observe --> UpdateSignal
    MoveUp --> Metrics["TierControlMetrics.record"]
    MoveDown --> Metrics
    UpdateSignal --> Advance["advance active tier event/state"]
    Advance --> Metrics
    Metrics --> Result["ExploitExploreStepResult"]
```

## Fiber-Conditioned Training Stage

This is the package-native surface for the "freeze tier i+1, train/lift at tier
i" idea.

```mermaid
flowchart TD
    Stage["FiberConditionedStage"] --> FrozenBehavior["FrozenQuotientBehavior<br/>coarse tier step held fixed"]
    Stage --> PathFiber["PathFiber<br/>fine/coarse tier relation"]
    Stage --> Tower["PartitionTower"]
    Stage --> Runtime["StageRuntimeLike"]

    Reset["stage.reset()"] --> RuntimeReset["runtime.reset()"]
    RuntimeReset --> BuildInput["Build ActionSelectionInput<br/>with stage_context + fiber_action_vocabulary"]
    BuildInput --> Current["current stage input"]

    Decision["ActionDecision"] --> Resolve["Resolve chosen action to ActionCellId"]
    Resolve --> Departure{"Invalid or no matching action cell?"}
    Departure -- yes --> Diagnostic["Diagnostic TrainingTransition<br/>FiberDeparture reason"]
    Departure -- no --> Lift["path_fiber.lift_candidates(current_state, action_cell)"]
    Lift --> HasLift{"Lift candidate exists?"}
    HasLift -- no --> NoLift["Diagnostic TrainingTransition<br/>NO_LIFT_CANDIDATE"]
    HasLift -- yes --> RuntimeStep["runtime.step(realized primitive action)"]
    RuntimeStep --> NextInput["Build next ActionSelectionInput"]
    NextInput --> Transition["TrainingTransition<br/>stage_context + projected_coarse_step"]
```

## Tensorization Boundary

The tensorization path starts after semantic training objects already exist. It
does not sit inside `TowerRuntime.step`.

```mermaid
flowchart TD
    Tower["PartitionTower"] --> Registry["EncodingRegistry.from_tower(tower)"]
    RuntimeView["LiveRuntimeView"] --> Input["ActionSelectionInput"]
    Input --> LinInput["linearize_action_selection_input(input, config, registry)"]
    Transition["TrainingTransition"] --> LinTransition["linearize_training_transition(transition, config, registry)"]

    Config["LinearizationConfig<br/>LinearizationState + NumericBackend + TensorDeviceKind"] --> LinInput
    Config --> LinTransition
    Registry --> LinInput
    Registry --> LinTransition

    LinInput --> Record["LinearizedActionSelectionInput<br/>backend-independent numeric record"]
    LinTransition --> TRecord["LinearizedTrainingTransition<br/>source/target/reward/action flags"]

    Config --> Report["build_linearization_report"]
    Registry --> Report
    Tower --> Report
    Report --> Manifest["LinearizationReport<br/>artifact/benchmark manifest data"]

    Record --> TorchDecision["TorchDecisionBatch.from_linearized(...)<br/>optional ml extra"]
    TRecord --> TorchTransition["TorchTransitionBatch.from_linearized(...)<br/>optional ml extra"]
    TorchDecision --> Model["User/Toy torch.nn.Module"]
    Model --> Logits["logits"]
    Logits --> Decision["action_decision_from_logits(logits, batch)"]
```

## Linearization Mode Logic

```mermaid
flowchart TD
    Config["LinearizationConfig"] --> State{"LinearizationState"}
    State -- ABSENT --> NoneMode["NumericBackend.NONE<br/>TensorDeviceKind.NONE<br/>label=none_control_flow"]
    State -- PRESENT_DISABLED --> Disabled["Tensorization available but disabled<br/>label=tensor_available_disabled"]
    State -- PRESENT_ENABLED --> Backend{"NumericBackend"}

    Backend -- NONE --> Invalid["Invalid:<br/>enabled requires backend"]
    Backend -- NUMPY --> Numpy["Backend-independent numeric layer<br/>CPU/no Torch"]
    Backend -- TORCH --> Device{"TensorDeviceKind"}
    Device -- CPU --> TorchCPU["label=tensor_enabled_cpu"]
    Device -- CUDA --> TorchCUDA["label=tensor_enabled_cuda<br/>requires torch.cuda"]
    Device -- NONE --> InvalidDevice["Invalid for enabled Torch conversion"]
```

## Gymnasium Wrapper Flow

The Gymnasium wrapper is observation-only. It delegates to the env and records
realized transitions. It does not build a hidden graph or own a training loop.

```mermaid
sequenceDiagram
    participant Caller
    participant Wrapper as StateCollapserGymWrapper
    participant Env as GymnasiumLike env
    participant Hooks as StateCollapserGymHooks
    participant Explored as ExploredGraph

    Caller->>Wrapper: reset(seed, options)
    Wrapper->>Env: reset(seed, options)
    Env-->>Wrapper: observation, info
    Wrapper->>Hooks: state_key(observation, info)
    Hooks-->>Wrapper: target state key
    Wrapper->>Explored: add_state(State(key))
    Wrapper->>Wrapper: attach action_mask and state_collapser metadata
    Wrapper-->>Caller: observation, info

    Caller->>Wrapper: step(action)
    Wrapper->>Hooks: action_key(action, previous_observation, previous_info)
    Wrapper->>Env: step(action)
    Env-->>Wrapper: observation, reward, terminated, truncated, info
    Wrapper->>Hooks: state_key(observation, info)
    Wrapper->>Hooks: edge_labeler(source_key, action_key, target_key, info)
    Wrapper->>Explored: add_edge(BaseEdge(source, primitive_action, target))
    Wrapper->>Wrapper: attach action_mask and graph metadata
    Wrapper-->>Caller: observation, reward, terminated, truncated, info
```

## Benchmark Flow

```mermaid
flowchart TD
    CLI["python -m state_collapser.benchmarks.tower_runtime_bench"] --> Args["parse_args<br/>steps / seed / mode / readout / morphism"]
    Args --> Probe["SUPPORTED_ENVIRONMENTS['plate_support_env']"]
    Probe --> RuntimeFactory["runtime_factory(policy, schema)"]
    RuntimeFactory --> Runtime["PlateSupportEnvRuntime + TowerRuntime"]
    Runtime --> BuildMorphism["Set tower_runtime._build_morphism flag"]
    BuildMorphism --> Reset["runtime.reset(seed)"]
    Reset --> MaybeReadout{"readout_requested?"}
    MaybeReadout -- yes --> Readout["tower_runtime.compatibility_quotient_tiers()"]
    MaybeReadout -- no --> Loop
    Readout --> Loop["For each benchmark step"]
    Loop --> RandomAction["rng.randrange(action_count)"]
    RandomAction --> Step["runtime.step(action)"]
    Step --> MaybeReadout2{"readout_requested?"}
    MaybeReadout2 -- yes --> Readout2["compatibility_quotient_tiers()"]
    MaybeReadout2 -- no --> More{"More steps?"}
    Readout2 --> More
    More -- yes --> Loop
    More -- no --> Metrics["discovered states/edges + tower depth + ops/sec"]
    Metrics --> Result["TowerRuntimeBenchResult.summary_line()"]
```

## HGraphML / Downstream Graph-Dataflow Path

The downstream graph-ML use case treats a graph as already discovered. It does
not need RL records or Torch batches for first-pass compatibility.

```mermaid
flowchart TD
    HGraph["Known graph / TensorGraph / graph-message-passing substrate"] --> Adapter["HGraphML state_collapser adapter"]
    Adapter --> StatesEdges["Convert graph nodes/edges to State/BaseEdge"]
    StatesEdges --> FullBuild["build_partition_tower_full(states, edges, current_state=None, schema)"]
    FullBuild --> Tower["PartitionTower"]
    Tower --> Fibers["Read node fibers and edge fibers by tier"]
    Tower --> Registry["EncodingRegistry.from_tower(tower)"]
    Registry --> StableIds["Stable numeric ids for nodes, edges, cells, tiers"]
    StableIds --> MessagePassing["Coarse message passing / lift over fibers"]

    BadPath["Do NOT fake RL ActionSelectionInput"] -. "category error" .-> MessagePassing
    Torch["Do NOT require Torch for this path"] -. "optional only" .-> MessagePassing
```

## Data Object Lifecycle

```mermaid
flowchart LR
    DomainState["Domain state<br/>example env"] --> State["core.State"]
    DomainAction["Domain action index/object"] --> PrimitiveAction["core.PrimitiveAction"]
    State --> BaseEdge["core.BaseEdge"]
    PrimitiveAction --> BaseEdge

    BaseEdge --> Registry["BaseGraphRegistry ids"]
    Registry --> StateLayer["StatePartitionLayer cells"]
    Registry --> ActionLayer["ActionPartitionLayer collections/cells"]
    StateLayer --> RuntimePosition["current_position_at_every_tier"]
    ActionLayer --> AbstractActions["ActionCellId abstract actions"]

    RuntimePosition --> LiveView["LiveRuntimeView"]
    AbstractActions --> LiveView
    LiveView --> ActionInput["ActionSelectionInput"]
    ActionInput --> Decision["ActionDecision"]
    Decision --> TrainingTransition["TrainingTransition"]
    TrainingTransition --> Linearized["LinearizedTrainingTransition"]
    Linearized --> TorchBatch["Optional TorchTransitionBatch"]
```

## What Changes During Exploration

```mermaid
flowchart TD
    Before["Before step:<br/>registry + partition layers"] --> Realized["Realized primitive transition"]
    Realized --> ExploredDelta["ExploredGraph adds edge/path state"]
    ExploredDelta --> VistaDelta["VistaGraph refreshes local outgoing edges"]
    VistaDelta --> VisibleDelta["Visible states/edges for current/refreshed states"]
    VisibleDelta --> RegistryDelta["BaseGraphRegistry registers only new states/edges"]
    RegistryDelta --> LayerDelta["PartitionTower updates only affected layers/cells"]
    LayerDelta --> Result["TowerUpdateResult"]
    Result --> RuntimeFields["Runtime updates positions, selected edges, diagnostics"]
    RuntimeFields --> After["After step:<br/>same base registry plus coarser partition updates"]
```

## What Does Not Happen

```mermaid
flowchart TD
    No1["TowerRuntime.step"] -. "does not" .-> FullRebuild["rebuild whole quotient tower from scratch each step"]
    No2["PartitionTower"] -. "does not" .-> CopyGraph["copy base graph into every quotient tier"]
    No3["training.linearization"] -. "does not" .-> OwnModel["own model architecture / optimizer / replay"]
    No4["training.torch"] -. "does not" .-> ImportTorchCore["make Torch a core dependency"]
    No5["Gymnasium wrapper"] -. "does not" .-> InferHidden["infer hidden graph or replace Gymnasium loop"]
    No6["HGraphML path"] -. "does not" .-> FakeRL["force graph dataflow through RL ActionSelectionInput"]
```

## Current System Summary

```mermaid
flowchart TD
    A["Environment or known graph"] --> B["Core State / PrimitiveAction / BaseEdge"]
    B --> C["HiddenGraph, ExploredGraph, VistaGraph"]
    C --> D["TowerRuntime"]
    D --> E["PartitionTower<br/>registry + nested state/action partitions"]
    E --> F["LiveRuntimeView"]
    F --> G["Training surfaces<br/>ActionSelectionInput / TrainingTransition"]
    G --> H["User learner or reference tabular learner"]
    G --> I["Optional linearization"]
    I --> J["Optional Torch"]
    E --> K["Compatibility readouts"]
    E --> L["HGraphML shared encoding path"]
    D --> M["Benchmark smoke tooling"]
```

The center of the package is therefore:

```text
discovered graph
    -> persistent partition tower
        -> runtime snapshots
            -> training, tensorization, benchmark, and downstream graph-dataflow surfaces
```

