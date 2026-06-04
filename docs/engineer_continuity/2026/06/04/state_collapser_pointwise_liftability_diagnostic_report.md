# Diagnostic Report: Pointwise Liftability Gap In `state_collapser` Runtime Surfaces

## Purpose

This report records a Codex investigation requested from the
`big_boy_benchmarking` repository into the local `/Users/foster/state_collapser`
repository.

The immediate downstream symptom is a BBB counterpoint tower-control failure:
deep quotient tiers advertise abstract outgoing action cells, but selected
abstract actions often fail with:

```text
no_lift_candidate_from_current_state
```

The Project Owner clarified the underlying mathematical issue: after
contracting states, an abstract state-cell pools outgoing action information
across its representatives. A concrete rollout cannot execute an arbitrary
action from that pooled set. It can execute only actions with at least one
concrete edge sourced at the rollout's current concrete state.

This document separates that PO insight from Codex's code-level diagnosis.

## Executive Diagnosis

The bad lift logic is not one isolated BBB line. It is a contract gap spanning
three surfaces:

1. `state_collapser` correctly represents quotient-level outgoing action
   collections, but the generic query name `outgoing_action_cells` is easy to
   misuse as executable action availability.
2. `PartitionTower.lift_candidates` explicitly falls back to representative
   edges when no edge is directly executable from the current concrete state.
   That behavior is useful for quotient reasoning/readout, but not safe for
   executable control.
3. `PathFiber` and `FiberConditionedStage` use action-cell membership and
   `lift_candidates` in a way that can mark actions as fiber-admissible even
   when no concrete member edge starts at the current total state.

BBB then compounds the issue by implementing `tier_is_executable` as "the
current quotient state-cell has nonempty outgoing action cells." That catches
empty-Out degenerate tiers, but not pointwise lift failures.

## Repositories And Versions

- Investigation repo: `/Users/foster/big_boy_benchmarking`
- Upstream repo inspected: `/Users/foster/state_collapser`
- Upstream branch status at inspection time: `main...origin/main [ahead 2]`
- Upstream package version at inspection time: `state_collapser==0.7.1`

## Key Conceptual Distinction

These are different predicates:

```text
quotient-available(C):
    a quotient state cell C has at least one outgoing abstract action cell

pointwise-liftable(s, A):
    the selected action cell A has at least one concrete edge whose source is
    the current concrete state s

tier-executable-from-state(s, i):
    at tier i, the state cell [s]_i has at least one outgoing action cell A
    that is pointwise-liftable from s
```

The current code often uses the first predicate where executable control needs
the third.

## Code Finding 1: `outgoing_action_cells` Is Quotient-Level Only

File:

```text
/Users/foster/state_collapser/src/state_collapser/tower/partition/tower.py
```

Relevant method:

```python
def outgoing_action_cells(
    self,
    tier: int,
    state_cell_id: StateCellId,
) -> tuple[ActionCellId, ...]:
    """Return abstract decision actions available from a state cell."""

    if tier < 0 or tier >= len(self.action_layers):
        return ()
    action_layer = self.action_layers[tier]
    collection_id = action_layer.outgoing_collection(state_cell_id)
    return action_layer.action_cells_for_collection(collection_id)
```

Diagnosis:

This method takes a tier and an abstract state cell. It does not take the
current concrete state. Therefore it cannot answer whether a returned action
cell is executable from the current concrete state.

That is correct as a quotient-level query. It is insufficient as a runtime
executability predicate.

## Code Finding 2: Action Cells Are Built By Pooled Coset Outgoing Data

File:

```text
/Users/foster/state_collapser/src/state_collapser/tower/partition/action_layer.py
```

Relevant construction:

```python
def rebuild_action_cells_for_collection(
    self,
    collection_id: ActionCollectionId,
    state_layer: StatePartitionLayer,
    registry: BaseGraphRegistry,
) -> tuple[ActionCellId, ...]:
    """Rebuild decision-level action cells for one dirty collection.

    Edges are grouped by source cell, target cell, and primitive action
    identity. This makes every representative state in a coset see the same
    abstract outgoing decision surface.
    """
```

and:

```python
grouped: dict[tuple[StateCellId, StateCellId, object], dict[EdgeId, None]] = {}
for edge_id in self.edge_ids_for_collection(collection_id):
    source_cell = state_layer.cell_of(registry.source_state_id(edge_id))
    target_cell = state_layer.cell_of(registry.target_state_id(edge_id))
    if source_cell == target_cell:
        continue
    label_key = registry.action_for_edge_id(edge_id).canonical_identity
    grouped.setdefault((source_cell, target_cell, label_key), {})[edge_id] = None
```

Diagnosis:

The docstring says the important part directly: every representative state in a
coset sees the same abstract outgoing decision surface. That is quotient
semantics. It does not imply every representative has every abstract action as
a concrete outgoing edge.

## Code Finding 3: `lift_candidates` Falls Back To Non-Executable Representatives

File:

```text
/Users/foster/state_collapser/src/state_collapser/tower/partition/tower.py
```

Relevant method:

```python
def lift_candidates(
    self,
    tier: int,
    action_cell_id: ActionCellId,
    current_base_state: State,
) -> tuple[BaseEdge, ...]:
    """Return primitive edges that can realize an abstract action.

    If the current base representative has directly executable edges inside
    the action cell, those are preferred. Otherwise the method returns the
    deterministic representative set so a controller can still reason about
    the action at the quotient tier.
    """

    representatives = self.representative_edges(tier, action_cell_id)
    directly_executable = tuple(
        edge for edge in representatives if edge.source == current_base_state
    )
    return directly_executable if directly_executable else representatives
```

Diagnosis:

The implementation and docstring intentionally mix two notions:

- directly executable edges from the current state;
- fallback representatives for quotient-level reasoning.

That means `lift_candidates` is not a strict executable-lift query. Its name is
dangerous for downstream control because a caller can receive edges whose
source is not the current concrete state.

The package has an explicit test for this fallback:

```text
/Users/foster/state_collapser/tests/tower/partition/test_queries_and_lift.py
```

```python
def test_lift_candidates_fall_back_to_representatives() -> None:
    tower, start, _middle, goal, start_to_goal, middle_to_goal = build_lift_tower()
    merged_cell = tower.current_state_cell(1, start)
    action_cell = tower.outgoing_action_cells(1, merged_cell)[0]

    assert tower.lift_candidates(1, action_cell, goal) == (
        start_to_goal,
        middle_to_goal,
    )
```

So the behavior is not an accidental regression. It is an API semantics problem
for executable control.

## Code Finding 4: `PathFiber` Uses Fiber Compatibility, Not Current-Source Executability

File:

```text
/Users/foster/state_collapser/src/state_collapser/training/fibers.py
```

Relevant method:

```python
def admissible_action_cells(self, total_state: State) -> tuple[ActionCellId, ...]:
    """Return fine action cells compatible with the frozen coarse step."""

    frozen_step = self.frozen_behavior.current_step
    if frozen_step is None:
        return ()
    state_cells = self.resolve_state_cells(total_state)
    if isinstance(state_cells, FiberDeparture):
        return ()
    if state_cells.coarse_state_cell != frozen_step.source_cell:
        return ()

    admissible: list[ActionCellId] = []
    for fine_action_cell in self.action_vocabulary(total_state):
        if any(
            self._edge_matches_frozen_step(edge, frozen_step)
            for edge in self.tower.action_cell_members(self.fine_tier, fine_action_cell)
        ):
            admissible.append(fine_action_cell)
    return tuple(admissible)
```

Diagnosis:

This checks whether an action cell contains some edge matching the frozen
coarse step. It does not require:

```python
edge.source == total_state
```

Then:

```python
def lift_candidates(
    self,
    total_state: State,
    action_cell: ActionCellId,
) -> tuple[BaseEdge, ...]:
    """Return deterministic primitive representatives for a fiber action cell."""

    if action_cell not in set(self.admissible_action_cells(total_state)):
        return ()
    return self.tower.lift_candidates(self.fine_tier, action_cell, total_state)
```

Because `tower.lift_candidates` falls back to generic representatives,
`PathFiber.lift_candidates` can also return non-current-source representatives.

## Code Finding 5: `FiberConditionedStage.step` Executes The First Returned Candidate

File:

```text
/Users/foster/state_collapser/src/state_collapser/training/stages.py
```

Relevant flow:

```python
lift_candidates = self.path_fiber.lift_candidates(
    self._current_total_state(source_input),
    action_cell,
)
if not lift_candidates:
    ...

realized_edge = lift_candidates[0]
runtime_action = (
    realized_edge.action
    if self.action_resolver is None
    else self.action_resolver(realized_edge)
)
step_result = self.runtime.step(runtime_action)
```

Diagnosis:

The stage assumes that the first returned lift candidate is executable in the
current runtime state. That assumption is not guaranteed by
`PathFiber.lift_candidates`, because the underlying tower query may fall back
to representative edges sourced somewhere else in the quotient cell.

If the runtime validates source-state/action compatibility, this can fail at
runtime. If the runtime action space is label-only and the same primitive label
can do different things from different states, this can silently execute a
different concrete transition than the representative edge described.

## Code Finding 6: Active-Tier Runtime Delegates Executability But Does Not Define The Strong Contract

File:

```text
/Users/foster/state_collapser/src/state_collapser/tower/runtime.py
```

Relevant flow:

```python
def _is_tier_executable(self, tier: int) -> bool:
    if self._tier_is_executable is None:
        return True
    return self._tier_is_executable(tier)

def _lift_to_executable_tier(self) -> bool:
    while not self._is_tier_executable(self._active_tier_state.active_tier):
        if not self._active_tier_state.has_upstairs():
            return False
        self._active_tier_state = self._move_up(self._active_tier_state)
    return True
```

Diagnosis:

This is a good hook, but the package does not define `tier_is_executable` with
the required pointwise semantics. The runtime can only be as correct as the
callback supplied by environment bindings.

The v0.7.1 fix handled the fully degenerate case where the active tier has
empty outgoing action cells. It did not handle the subtler case where outgoing
abstract action cells exist but no action cell is executable from the current
concrete state.

## Code Finding 7: Upstream Example Runtime Uses The Weak Predicate

File:

```text
/Users/foster/state_collapser/src/state_collapser/examples/plate_support_env/runtime.py
```

Relevant method:

```python
def _tier_is_executable(self, tier: int) -> bool:
    snapshot = self._last_runtime_snapshot
    if snapshot is None:
        return True
    tower_view = snapshot.partition_tower_view
    if tower_view is None:
        return True
    tower = cast(PartitionTower, tower_view)
    positions = snapshot.current_position_at_every_tier
    if tier < 0 or tier >= len(positions):
        return False
    state_cell = positions[tier]
    if state_cell is None:
        return False
    return bool(tower.outgoing_action_cells(tier, cast(StateCellId, state_cell)))
```

Diagnosis:

This is the same weak predicate BBB used. It answers quotient-level
nonemptiness, not current-state executable liftability. Because this appears in
an upstream example runtime, the ambiguity is package-level.

## Downstream BBB Finding

File:

```text
/Users/foster/big_boy_benchmarking/src/big_boy_benchmarking/environments/counterpoint/serious_learning/tower_control.py
```

Weak executable-tier predicate:

```python
def tier_is_executable(self, tier: int) -> bool:
    if tier < 0 or tier >= self.tower_depth:
        return False
    state_cell = self.current_tier_state(tier)
    if state_cell is None:
        return False
    return bool(self.build.tower.outgoing_action_cells(tier, state_cell))
```

Strict filtering happens too late:

```python
vocabulary = self.adapter.build.tower.outgoing_action_cells(tier, source_tier_state)
...
candidates = self.adapter.build.tower.lift_candidates(
    tier,
    action_cell,
    self.adapter.current_core_state,
)
executable = tuple(
    edge for edge in candidates if edge.source == self.adapter.current_core_state
)
if not executable:
    members = self.adapter.build.tower.action_cell_members(tier, action_cell)
    executable = tuple(
        edge for edge in members if edge.source == self.adapter.current_core_state
    )
if not executable:
    return self._failure(
        tier,
        source_tier_state,
        action_cell,
        "no_lift_candidate_from_current_state",
        len(candidates),
    )
```

Diagnosis:

BBB correctly detects the failure at execution time, but the controller should
not have selected that tier/action in the first place. The action vocabulary
and executable-tier predicate should already be filtered to action cells with
at least one member edge sourced at the current concrete state.

The same adapter is used by multiple BBB evaluations:

- noisy-rate contraction diagnostics;
- fraction-sweep diagnostics;
- noisy-rate full-tower training;
- second serious schema comparison.

So this one predicate affects several current reports.

## Minimal Reproduction Run

Codex ran this local repro against `/Users/foster/state_collapser/src`:

```text
PYTHONPATH=/Users/foster/state_collapser/src \
UV_CACHE_DIR=/private/tmp/bbb-uv-cache \
uv run python -c '...'
```

The constructed graph was:

```text
0 --contract--> 1
0 --to2-------> 2
1 --to2-------> 2
1 --one_only--> 2
```

After contracting `0 --contract--> 1`, tier 1 has state cell `[0,1]`.

Observed output:

```text
tier1 cell for zero StateCellId(tier=1, ordinal=3)
tier1 members ['0', '1']
action_cell ActionCellId(tier=1, ordinal=0)
members [('1', ('one_only',), '2')]
lift_from_zero [('1', ('one_only',), '2')]
action_cell ActionCellId(tier=1, ordinal=1)
members [('0', ('to2',), '2'), ('1', ('to2',), '2')]
lift_from_zero [('0', ('to2',), '2')]
```

The first action cell is quotient-available from `[0,1]`, but it is not
pointwise executable from current concrete state `0`. Yet `lift_candidates`
returns the edge from `1` as a fallback representative.

## Why The Young Diagram Algorithm Does Not Contradict This

The Young diagram / nested partition construction ensures that action-side data
is fibered over state-side quotient cells. It does not, by itself, ensure that
every representative state in a quotient state cell can execute every action
cell pooled into that quotient cell.

The research text explicitly says the quotient state cell pools outgoing
information:

```text
each representative of the coset inherits the outgoing-action information
available from the other representatives
```

and also:

```text
Execution then requires a lift/refinement step: move within the coset, or
select a representative path, so that the abstract action becomes executable
in the base graph.
```

Therefore, current-state liftability is an additional runtime/refinement
condition. It must be represented explicitly in code and masks.

## Recommended Upstream Redesign

Add strict, pointwise executable-lift queries to `PartitionTower`.

Proposed names:

```python
def executable_lift_candidates(
    self,
    tier: int,
    action_cell_id: ActionCellId,
    current_base_state: State,
) -> tuple[BaseEdge, ...]:
    ...

def executable_action_cells(
    self,
    tier: int,
    state_cell_id: StateCellId,
    current_base_state: State,
) -> tuple[ActionCellId, ...]:
    ...

def tier_is_executable_from_state(
    self,
    tier: int,
    current_base_state: State,
) -> bool:
    ...
```

The strict candidate query should return:

```python
tuple(
    edge
    for edge in self.action_cell_members(tier, action_cell_id)
    if edge.source == current_base_state
)
```

The action-cell query should filter `outgoing_action_cells` through the strict
candidate query.

Then:

- keep `representative_edges` for quotient/readout representatives;
- either rename `lift_candidates` or document it as non-strict;
- update `PathFiber.admissible_action_cells` and `action_mask` to require
  current-source executable edges;
- update `FiberConditionedStage.step` to consume strict executable candidates;
- update example runtime `tier_is_executable` implementations to use
  `tier_is_executable_from_state`.

## Recommended BBB Redesign

Once upstream exposes strict queries, BBB should:

1. Replace `CounterpointTowerControlAdapter.tier_is_executable` with a
   pointwise liftability check.
2. Replace learner action vocabulary with executable action cells, not raw
   quotient outgoing action cells.
3. Record both counts separately:
   - `abstract_outgoing_action_cell_count`;
   - `pointwise_executable_action_cell_count`.
4. Preserve execution-time fallback diagnostics, but treat
   `no_lift_candidate_from_current_state` as a bug/structural diagnostic rather
   than normal learner failure.
5. Regenerate current affected evaluation reports after the semantics change.

## Tests To Add Upstream

Add a partition-tower test with the asymmetric simplex graph:

```text
0 --contract--> 1
0 --to2-------> 2
1 --to2-------> 2
1 --one_only--> 2
```

Assertions:

- tier 1 state cell for `0` and `1` is the same;
- `outgoing_action_cells(1, [0,1])` includes the `one_only` action cell;
- `executable_lift_candidates(1, one_only_cell, zero) == ()`;
- `executable_lift_candidates(1, one_only_cell, one) == (one_only,)`;
- `tier_is_executable_from_state(1, zero)` is true only because `to2` exists
  from `zero`, not because `one_only` exists from `one`.

Add `PathFiber` tests proving masks exclude action cells whose matching
representatives exist only from other states in the same quotient cell.

Add `FiberConditionedStage` tests proving the stage emits
`NO_LIFT_CANDIDATE` or excludes the action before stepping when no
current-source executable candidate exists.

## Open Design Question For Discussion

There is one architectural question to settle before implementing:

Should `lift_candidates` change behavior and become strict, or should it remain
a quotient-representative method while a new strict method is introduced?

Codex recommendation: add new strict methods first. Preserve the old method for
compatibility, but rename or deprecate it later if it keeps causing confusion.

 </br> 

 ---
 ---
 </br> 

## Initial Design Direction: Source-Support Decorations On The Young Diagram

This section begins the design discussion requested after the diagnostic
report. It is intentionally appended rather than folded into the earlier
diagnosis, so the diagnostic record remains intact.

### Project Owner Direction

The Project Owner's high-level technical question is how to make the query

```text
find s' such that pr_i(s') = s and Out(s') is nonempty
```

really efficient in the current Young diagram formulation. The Project Owner
also clarified that the desired answer should be formulated inside the present
Young diagram picture, not merely as an external implementation trick.

### Codex Design Formulation

In the current formulation, each tier has a projection

```text
pr_i : S_0 -> S_i
```

from concrete/total states to tier-`i` state cells. If `C` is a tier-`i` state
cell, then:

```text
C = pr_i^{-1}(s)
```

is the Young diagram state cell containing the concrete representatives above
the quotient state `s`.

The existing diagram stores:

```text
state cell C
    -> outgoing action-cell collection Out_i(C)
```

The missing efficient datum is a source-support decoration on each action cell.
For every tier-`i` action cell `D` lying over state cell `C`, store:

```text
Supp_i(D) = { s' in C : there exists a concrete edge a in D with src(a) = s' }.
```

So the corrected Young diagram object is not merely:

```text
C -> Out_i(C)
```

but:

```text
C -> { (D, Supp_i(D)) : D in Out_i(C) }.
```

In words: each action Young cell hanging over a state Young cell casts a
source-support shadow onto the entries of the state cell. The shadow marks
exactly those concrete representatives from which that abstract action cell is
actually executable.

### Three Distinct Queries

This gives three separate, fast predicates that should not be conflated.

Quotient-level outgoing availability:

```text
Out_i(C) is nonempty
```

This says the quotient state cell has abstract outgoing action data.

Representative support availability:

```text
Active_i(C) is nonempty
```

where:

```text
Active_i(C) = union over D in Out_i(C) of Supp_i(D).
```

This says at least one representative inside the quotient state cell supports
some outgoing executable edge.

Pointwise current-state executability:

```text
x in Supp_i(D)
```

where `x` is the actual current concrete state. This says the selected abstract
action cell `D` is executable from the current concrete state, not merely from
some representative in the same quotient cell.

#### PO Reply:
I think I disagree a bit here. When we join $\text{Out}$'s... I'm not sure exactly what I'm looking for, but it seems to me that $\text{Active}$ is really a functional construction... like just binning eveything at one level in the right way. ...I'm just suspicious that the thing in the next section is not too big. Like *really* everything attached to Yound diagram structures should just be like pointers to bins of stuff in it.

#### Codex Follow-up:
I agree with this correction. My previous wording risks making
`Active_i(C)` sound like a new heavy object bolted onto the Young diagram,
when the cleaner formulation is that `Active_i(C)` is a functional readout of
the bins already present in the diagram, provided the bins retain the right
source pointers.

The better Young-diagram formulation is:

```text
tier-i state cell C
    is a bin of concrete states

tier-i outgoing collection Out_i(C)
    is a bin of concrete edges whose sources lie in C and whose targets leave C

tier-i action cell D inside Out_i(C)
    is a sub-bin of those concrete edges
```

Then the support is not an independent mathematical structure. It is the image
of the source map restricted to that edge bin:

```text
Supp_i(D) = src(D)
```

and the active representatives of a state cell are likewise:

```text
Active_i(C) = src(Out_i(C)).
```

So yes: this should be thought of as binning everything at one level in the
right way. The efficient implementation should make the source-map image
available by pointers to bins, not by repeatedly scanning and not by copying
large sets around.

Concretely, when `Out` bins are joined during contraction, the joined bin
should preserve its source-keyed sub-bins:

```text
Out_i(C) =
    source s_1 -> edge sub-bin
    source s_2 -> edge sub-bin
    ...
```

and each action cell `D` should inherit the same kind of source-keyed sub-bin:

```text
D =
    source s_1 -> edge sub-bin inside D
    source s_2 -> edge sub-bin inside D
    ...
```

Then:

```text
Out_i(C) nonempty
```

is a quotient-level question about whether the edge bin has entries, while:

```text
current concrete state x has an executable lift in D
```

is a pointer/key question:

```text
D.source_bins contains x.
```

For the simplex example, after contracting `[0] -> [1]`, the quotient outgoing
bin for `[0,1]` may contain edges sourced at both `[0]` and `[1]`. The action
cell for an action that only exists from `[1]` should have a source sub-bin for
`[1]` and no source sub-bin for `[0]`. That is exactly the distinction the
runtime needs.

This means the next section should be interpreted, and probably later
rewritten in a blueprint, as a materialized-view / pointer-to-bin design. The
important thing is not to create a bulky extra structure. The important thing
is to ensure every action bin keeps cheap access to its source-fiber sub-bins.
`Supp_i(D)` and `Active_i(C)` are then names for functional images of existing
bins, with optional cached keys or bitsets only as performance materialization.

#### PO Follow-up
Before we proceed, I want you to show me that you understand one important aspect of what's happening... Take a directed graph given by $3$-simplex. Contract $[0]-->[1]$ to get graph with nodes $[0,1], [2], [3]$ Then contract again to get graph wiht nodes $[0,1,2], [3]$. So the recursive thing happening here is that the active pointers or whatever for second tier here are to [0,1] and [2]. Do you see what I'm gettign at. There is a recursive nested coset thing happening here.

#### Codex Follow-up
Yes, I see it. This is the missing refinement in my previous formulation. I
was speaking as though every support shadow should be described directly on
base states. That is useful for final execution, but it flattens the recursive
Young-diagram structure too early.

The more native formulation is adjacent-tier recursive:

```text
tier 0:
    [0], [1], [2], [3]

tier 1 after contracting [0] -> [1]:
    [0,1], [2], [3]

tier 2 after contracting [0,1] -> [2]:
    [0,1,2], [3]
```

At tier 2, the source cell `[0,1,2]` is not merely a flat bag of base states.
It has a refinement fiber one tier down:

```text
pr_{2,1}^{-1}([0,1,2]) = { [0,1], [2] }.
```

So the tier-2 active/source pointers should naturally point first to the
tier-1 bins `[0,1]` and `[2]`, not immediately all the way down to `[0]`,
`[1]`, and `[2]`.

The corrected recursive support datum for an action cell `D_i` should therefore
be something like:

```text
Supp_{i -> i-1}(D_i)
    = { C_{i-1} in pr_{i,i-1}^{-1}(C_i)
        : some lower action/bin sourced at C_{i-1} contributes to D_i }.
```

In words: the source support of a tier-`i` action cell is first a subset of the
tier-`i-1` state cells that refine its source state cell. Then each one of
those child cells has its own lower support data, recursively, until tier `0`.

For the 3-simplex example:

```text
tier-2 state cell:
    C_2 = [0,1,2]

its tier-1 refinement children:
    [0,1]
    [2]
```

If a tier-2 action cell `D_2` represents movement from `[0,1,2]` to `[3]`,
then its immediate source support should be:

```text
Supp_{2 -> 1}(D_2) subset { [0,1], [2] }.
```

If both the `[0,1] -> [3]` bin and the `[2] -> [3]` bin contributed edges, then:

```text
Supp_{2 -> 1}(D_2) = { [0,1], [2] }.
```

Then, inside the `[0,1]` branch, the next recursive question is:

```text
Supp_{1 -> 0}(D_1) subset { [0], [1] }.
```

This is exactly the nested coset thing: a high-tier action does not merely have
a base-level support set; it has a refinement tree of supporting child bins.

So the clean design distinction is:

```text
authoritative Young-diagram support:
    adjacent-tier source-bin pointers

fast execution materialization:
    optional flattened base-source support cache
```

The adjacent-tier pointers preserve the mathematical structure. The flattened
cache answers hot runtime questions like:

```text
does current base state x support D_i?
```

without walking the refinement tree every time.

This also changes how I would phrase `Active_i(C)`. The native object is not:

```text
Active_i(C) subset S_0
```

as a primary structure. The native object is:

```text
Active_{i -> i-1}(C)
    subset pr_{i,i-1}^{-1}(C),
```

meaning the active child bins immediately below `C`. The base-state version:

```text
Active_i^0(C) subset S_0
```

is then the recursive expansion or cached flattening of those adjacent support
pointers.

That makes the data structure much more faithful:

```text
state cell C_i
    -> child state cells C_{i-1}
    -> outgoing collection Out_i(C_i)
    -> action cells D_i
    -> source support pointers to child state cells C_{i-1}
    -> recursively to lower action/state bins
```

This is also probably the right way to think about lift. A tier-`i` abstract
action should refine by choosing a supported tier-`i-1` child bin and then a
compatible tier-`i-1` action cell beneath it. Repeating that gives a lift path
through the nested Young diagram, ending in a concrete executable edge at tier
`0`.

So yes: the recursive thing is not incidental. It is the actual structure we
should design around. The next blueprint should avoid making source support
look like a flat side table, and should instead specify adjacent support
pointers plus optional flattened caches for speed.


#### PO Follow-up
Ok do another pass through everythign below. If there is anywhere that this better, pointer-focussed way of keeping track of active states would improve efficiency anywhere, clarify and modify below.

#### Codex Follow-up

Agreed. The remainder of this design section should be read in the
pointer-focused way. The primary structure should be adjacent pointers among
Young-diagram bins. Source-id sets and bitsets should be treated as optional
materialized caches for hot runtime checks, not as the mathematical object.

### Efficient Runtime Data Structure

The efficient runtime object should be a pointer-to-bin structure over adjacent
Young-diagram tiers.

Primary adjacent-bin form:

```python
child_state_cells_by_state_cell[tier][state_cell_id] -> tuple[StateCellId]
outgoing_collection_by_state_cell[tier][state_cell_id] -> ActionCollectionId
action_cell_ids_by_collection[tier][collection_id] -> tuple[ActionCellId]

source_child_cells_by_action_cell[tier][action_cell_id] -> tuple[StateCellId]
edge_ids_by_action_cell_by_source_child[tier][action_cell_id][child_state_cell_id] -> tuple[EdgeId]
lower_action_cells_by_action_cell_by_source_child[tier][action_cell_id][child_state_cell_id] -> tuple[ActionCellId]

active_child_cells_by_collection[tier][collection_id] -> tuple[StateCellId]
first_active_child_by_collection[tier][collection_id] -> StateCellId | None
```

In this shape, a tier-`i` action cell does not primarily store a flat set of
base sources. It stores pointers to the tier-`i-1` state bins from which it has
support. Those child bins then carry the next layer of support pointers.

The recursive support definition becomes:

```text
Supp_{i -> i-1}(D_i) =
    source_child_cells_by_action_cell[i][D_i]
```

and:

```text
Active_{i -> i-1}(C_i) =
    active_child_cells_by_collection[i][Out_i(C_i)].
```

That is the native Young-diagram data. It answers "where can this abstract
action refine next?" without scanning a state fiber or flattening all the way
to tier `0`.

Derived hot-path cache form:

```python
base_source_ids_by_action_cell[tier][action_cell_id] -> frozenset[StateId]
edge_ids_by_action_cell_by_base_source[tier][action_cell_id][source_id] -> tuple[EdgeId]
base_active_source_ids_by_collection[tier][collection_id] -> frozenset[StateId]
first_base_active_source_by_collection[tier][collection_id] -> StateId | None
```

The derived cache is useful for direct pointwise execution from a known current
base state:

```python
source_id = registry.state_id_by_state[current_base_state]
source_id in base_source_ids_by_action_cell[tier][action_cell_id]
```

The cache can also be represented as dense bitsets:

```python
base_source_support_bits_by_action_cell[tier][action_cell_id] -> int
base_active_source_bits_by_collection[tier][collection_id] -> int
```

With dense `StateId` ordinals, this makes base-state membership checks cheap:

```python
bool(base_source_support_bits_by_action_cell[tier][D] & (1 << source_id))
```

The pointer version is the authoritative structure. The base-source cache is a
performance materialization for controller masks and direct executability
checks.

### Where The Pointers Should Be Maintained

The best maintenance point is still the existing action-cell rebuild path:

```text
ActionPartitionLayer.rebuild_action_cells_for_collection(...)
```

But the important change is what gets recorded during that pass. The method
already loops over live edge ids in an outgoing collection and groups them into
action cells. For each edge assigned to a tier-`i` action cell `D_i`, the layer
should also record the tier-`i-1` source child cell and, when possible, the
tier-`i-1` action cell containing that same edge:

```text
source_child = state_layers[i - 1].cell_of(registry.source_state_id(edge_id))
lower_action_cell = action_cell_for_edge(i - 1, edge_id)

source_child_cells_by_action_cell[D_i].add(source_child)
edge_ids_by_action_cell_by_source_child[D_i][source_child].append(edge_id)
lower_action_cells_by_action_cell_by_source_child[D_i][source_child].add(lower_action_cell)
active_child_cells_by_collection[collection_id].add(source_child)
```

This uses the bin pointers the tower already has or should already have:

```text
edge id -> source state id
source state id -> tier-(i-1) state cell
edge id -> tier-(i-1) action cell
```

If the last pointer is not currently indexed, the efficient fix is to maintain
an `action_cell_by_edge_id` map per tier when action cells are rebuilt. That
prevents repeated scans through action cells when computing recursive support.

For tier `0`, the adjacent source child is just the concrete source state id:

```python
source_child = registry.source_state_id(edge_id)
```

So the same recursive structure bottoms out naturally at concrete executable
edges.

This does not add a new asymptotic graph pass. It enriches the action-cell
rebuild with bin pointers while the relevant edge ids are already in hand.
Incremental tower updates already rebuild dirty collections, so support
pointers should update only where the action layer is already dirty.

### Query API Implied By The Design

The design suggests two layers of package-level queries: native recursive
queries and derived pointwise execution queries.

Native adjacent support for a selected action cell:

```python
def supported_child_state_cells(
    tier: int,
    action_cell_id: ActionCellId,
) -> tuple[StateCellId, ...]:
    ...
```

Fast implementation:

```text
return source_child_cells_by_action_cell[tier][action_cell_id]
```

Native active child bins for a state cell:

```python
def active_child_state_cells_for_state_cell(
    tier: int,
    state_cell_id: StateCellId,
) -> tuple[StateCellId, ...]:
    ...
```

Fast implementation:

```text
collection = outgoing_collection_by_state_cell[tier][state_cell_id]
return active_child_cells_by_collection[tier][collection]
```

Recursive lower action cells under a selected high-tier action:

```python
def lower_action_cells_for_supported_child(
    tier: int,
    action_cell_id: ActionCellId,
    child_state_cell_id: StateCellId,
) -> tuple[ActionCellId, ...]:
    ...
```

Fast implementation:

```text
return lower_action_cells_by_action_cell_by_source_child[tier][action_cell_id][child_state_cell_id]
```

Derived strict executable candidates for direct base execution:

```python
def executable_lift_candidates_from_base_state(
    tier: int,
    action_cell_id: ActionCellId,
    current_base_state: State,
) -> tuple[BaseEdge, ...]:
    ...
```

Fast implementation with materialized cache:

```text
source_id = registry.state_id_by_state[current_base_state]
return edge_ids_by_action_cell_by_base_source[tier][action_cell_id].get(source_id, ())
```

Fast implementation without materialized cache:

```text
walk the adjacent support pointers along the current state's cell lineage
from tier i down to tier 0
```

That fallback should be `O(depth)` if child-support membership is indexed at
each adjacent tier.

Derived action cells executable from the current concrete state:

```python
def executable_action_cells_from_base_state(
    tier: int,
    state_cell_id: StateCellId,
    current_base_state: State,
) -> tuple[ActionCellId, ...]:
    ...
```

Fast implementation:

```text
source_id = registry.state_id_by_state[current_base_state]
for D in Out_i(state_cell_id):
    keep D iff source_id is in base_source_ids_by_action_cell[tier][D]
```

or, without flattening:

```text
current_child = current_state_cell(tier - 1, current_base_state)
for D in Out_i(state_cell_id):
    keep D iff current_child is in supported_child_state_cells(tier, D)
    and the lower support chain continues recursively to current_base_state
```

Derived tier executable from the current concrete state:

```python
def tier_is_executable_from_state(
    tier: int,
    current_base_state: State,
) -> bool:
    ...
```

Fast implementation:

```text
C = current_state_cell(tier, current_base_state)
return executable_action_cells_from_base_state(tier, C, current_base_state) is nonempty
```

Representative/refinement query:

```python
def active_child_state_cells_for_state_cell(
    tier: int,
    state_cell_id: StateCellId,
) -> tuple[StateCellId, ...]:
    ...
```

Fast implementation:

```text
return active_child_cells_by_collection[tier][Out_i(state_cell_id)]
```

This answers the Project Owner's question in the recursive Young-diagram form:
find active representatives first as active child bins one tier down. Only when
the runtime needs a concrete state does it recursively expand or consult the
flattened base-source cache.

### Critical Semantic Split

The design must keep these two runtime modes separate.

Pointwise execution mode:

```text
The runtime has current concrete state x.
An action D_i is executable only if the current state's entire cell lineage
lies along a support path beneath D_i down to tier 0.
```

Representative reanchoring/refinement mode:

```text
The runtime may choose some active child bin C_{i-1} under C_i, but only if it
also has a valid refinement/reanchoring procedure from the current concrete
state's child lineage to that selected child bin.
```

The second mode is mathematically natural in the quotient-address story, but it
is not free. It requires an explicit local refinement path, internal motion
policy, stutter convention, or other operational rule explaining how the agent
moves from the current representative to the selected supporting
representative.

For BBB's current counterpoint runtime, the safe immediate semantics are
pointwise execution mode. That means learner masks should expose only action
cells whose adjacent support path contains the current concrete state's lineage,
or whose flattened base-source cache contains the current concrete state.

### Complexity Targets

Without source-support pointers:

```text
check state-cell representative support: O(number of pooled edges in Out_i(C))
check selected action pointwise liftability: O(number of edges in D)
find an active representative: O(size of C) or O(number of pooled edges)
```

With adjacent source-support pointers:

```text
check whether C_i has any active child bin: O(1)
enumerate active child bins of C_i: O(number of active child bins)
check whether D_i supports a given child C_{i-1}: O(1)
walk current-state support from tier i down to tier 0: O(depth)
return concrete executable edges at tier 0: O(k)
```

Here `k` is the number of concrete edges in action cell `D` sourced at `x`.
That is the unavoidable output size.

With optional flattened base-source caches:

```text
check whether D_i supports current base state x: O(1)
check whether C_i has any active base representative: O(1)
return concrete executable edges for D_i from x: O(k)
```

The key efficiency improvement from the pointer-focused design is that the
authoritative recursive checks no longer scan state fibers or pooled edge bins.
They follow precomputed bin pointers. The flattened cache only removes the
remaining `O(depth)` walk for the hottest pointwise execution queries.

### Design Consequence

The current Young diagram should be described as a nested state/action
partition system with pointer decorations:

```text
1. state-cell membership and parent/child refinement pointers;
2. outgoing collection/action-cell incidence over state cells;
3. adjacent source-support pointers from action cells back to child state cells;
4. optional flattened base-source caches for hot direct execution checks.
```

The third decoration is the missing executable-lift datum in the native Young
diagram form. It turns the question "does this quotient state have outgoing
action information?" into the control-relevant recursive question "which child
bins actually support those outgoing actions, and does the current state's
lineage pass through one of them?"

### Open Design Questions

Consultant-authored questions for the next design turn:

1. Should the first upstream implementation add adjacent child-bin support
   pointers only, or should it also materialize flattened base-source caches in
   the same pass?
2. Should the implementation add an `action_cell_by_edge_id` index per tier so
   recursive lower-action pointers can be built without scanning action cells?
3. Should `lift_candidates` remain as representative/readout behavior while new
   strict pointwise and recursive-refinement methods are added, or should it be
   deprecated immediately in favor of explicit names?
4. Should representative reanchoring be considered out of scope for the next
   fix, with BBB using pointwise execution only until a real within-fiber
   refinement rule exists?
