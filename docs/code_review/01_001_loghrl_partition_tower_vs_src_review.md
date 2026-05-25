# Code Review 01.001: `logHRL` Partition-Tower Model vs Current `/src`

## Scope

This report reviews whether the current implementation under `src/state_collapser`
matches the substantially revised construction in:

- `docs/design/logHRL.tex`

The focus is the paper's current "in RAM" description of the quotient tower as:

- a fixed discovered base graph,
- nested state partition tables,
- nested action partition tables,
- outgoing-incidence pointers from state cells to action cells,
- contraction driven by an explicit or implicit ordered partition of the base-tier edge set,
- loop/stutter handling,
- and incremental online update along exploration.

This is a code review report only. It does not implement fixes.

## High-Level Conclusion

The current code is not a literal implementation of the current `logHRL.tex`
partition-table / Young-diagram construction.

It is best described as an earlier, partial, package-owned dynamic quotient
builder. It is computationally close to the state-side graph-contraction picture:
it builds tier views, maps base states into quotient-node identifiers, removes
internal loops from quotient edge projection, and exposes current position across
tiers. In that limited sense, the state quotient graph produced by the code can
often be regarded as computationally equivalent to a graph contraction tower for
the particular contraction schedule the code actually uses.

But it is not currently equivalent to the full paper construction. The largest
mismatches are:

- the contraction policy does not actually define the contraction schema used by
  the tower builder;
- there is no explicit ordered partition of the full base-tier edge set into
  contraction blocks;
- the runtime rebuilds the full tower from visible graph data on each refresh,
  rather than incrementally propagating only the new vista;
- the action-side partition / outgoing-action-cell story is not represented as
  the paper describes;
- state-cell-to-action-cell outgoing pointers are not first-class data;
- loop removal has no stutter symbol or reward/fiber correction record;
- the tower is not yet used as an abstract action traversal/lift surface.

So the honest answer is:

> The code is homotopically/computationally adjacent to the current paper model
> on the state-quotient side, but it is not yet an implementation of the current
> RAM data structure or of the theorem-facing action/reward/lift structure.

The code is still a useful scaffold. It is not paper-conformant.

## Fine-Level Conclusion

### What matches reasonably well

The following parts of the implementation are aligned with the current paper at
the level of broad quotient-tower intent.

1. `TowerRuntime` is now the package-owned owner of dynamic tower construction.

   Evidence:

   - `src/state_collapser/tower/runtime.py:46`
   - `src/state_collapser/tower/runtime.py:216`

   The runtime owns explored graph growth, vista refresh, tower refresh, tier
   records, and current tier positions.

2. The discovered graph is represented sparsely through visited state/edge state
   and one-hop vista cache.

   Evidence:

   - `src/state_collapser/graph/explored_graph.py:8`
   - `src/state_collapser/graph/vista_graph.py:12`
   - `src/state_collapser/tower/construction.py:58`
   - `src/state_collapser/tower/construction.py:69`

   This is consistent with the paper's sparse node/outgoing-edge memory story.

3. A tier stores projection maps from base states/edges into quotient
   identifiers.

   Evidence:

   - `src/state_collapser/quotient/projection.py:12`
   - `src/state_collapser/quotient/tier_view.py:14`

   This provides the state-side map analogous to `pi_i^S`.

4. A tier stores reverse coset membership.

   Evidence:

   - `src/state_collapser/quotient/cosets.py:12`
   - `src/state_collapser/tower/construction.py:123`
   - `src/state_collapser/tower/construction.py:230`

   This makes quotient-node membership inspectable, which is close to the
   paper's state-cell table.

5. The builder removes projected loops from live quotient edges.

   Evidence:

   - `src/state_collapser/tower/construction.py:232`
   - `src/state_collapser/tower/construction.py:235`
   - `src/state_collapser/tower/construction.py:251`

   This aligns with the paper's statement that internal arrows of merged cells
   become loops and are removed.

### What does not match

The following findings are ordered by architectural severity.

## Finding 1: The tower builder ignores `ContractionPolicy.select(...)`

Severity: high.

The paper says the contraction schema is an explicit or implicit ordered
partition of the base-tier edge set. The code has a `ContractionPolicy` protocol,
but the tower builder does not call `select(...)` when deciding which edges to
contract.

Evidence:

- `src/state_collapser/contract/policy.py:14` defines `ContractionPolicy.select`.
- `src/state_collapser/tower/construction.py:82` accepts a `ContractionPolicy`.
- `src/state_collapser/tower/construction.py:88` only checks whether the policy
  is `None`.
- `src/state_collapser/tower/construction.py:90` returns all nontrivial visible
  base edges, sorted by stable key.
- `src/state_collapser/tower/construction.py:97` selects the first 20 percent of
  those edges.

So `LabelContractionPolicy` and `SeededRandomContractionPolicy` do not define the
tower contraction schedule. They only influence vista annotation messaging in
`TowerRuntime.step(...)`.

Evidence:

- `src/state_collapser/tower/runtime.py:110`
- `src/state_collapser/tower/runtime.py:117`
- `src/state_collapser/tower/runtime.py:126`
- `src/state_collapser/tower/runtime.py:127`

I verified this behavior with an in-memory check: a hidden graph with two visible
edges labelled `x` and `y`, run with `LabelContractionPolicy({"y"})`, selected
the `x` edge for contraction because it sorted first.

Observed output:

```text
(('x',),)
```

Impact:

The current code does not implement the TeX paper's contraction-schema boundary.
This is not just a naming mismatch. It means the policy object exposed to users
does not control the quotient tower the way the documentation implies.

## Finding 2: There is no explicit ordered partition of the full base-tier edge set

Severity: high.

The paper requires:

```tex
A_t^0 = Sigma_0^1 \sqcup Sigma_0^2 \sqcup \cdots \sqcup Sigma_0^d
```

and later relies on the fact that every base-tier edge participates in the
schedule exactly once.

Evidence in paper:

- `docs/design/logHRL.tex:922`
- `docs/design/logHRL.tex:926`
- `docs/design/logHRL.tex:1031`
- `docs/design/logHRL.tex:1037`
- `docs/design/logHRL.tex:1165`
- `docs/design/logHRL.tex:1169`

The code instead computes the eligible set dynamically at each tier:

- `src/state_collapser/tower/construction.py:170`
- `src/state_collapser/tower/construction.py:187`

Eligibility is based on whether a base edge is still nontrivial in the current
tier:

- `src/state_collapser/tower/construction.py:90`
- `src/state_collapser/tower/construction.py:93`

Then the code selects the first 20 percent:

- `src/state_collapser/tower/construction.py:102`
- `src/state_collapser/tower/construction.py:103`

Impact:

This is not an ordered partition of the full edge set. It is an iterative
"remaining nontrivial edge" schedule. Some base edges may become trivial because
of earlier contractions without ever being selected as contraction-driving edges.
That may be computationally reasonable for a quotient graph, but it contradicts
the paper's current statement that the base-tier edge set is partitioned and
processed block-by-block.

## Finding 3: The implementation is full rebuild, not incremental update

Severity: high.

The paper distinguishes the static full-build algorithm from an online
incremental update algorithm in which only newly discovered edges are propagated
through existing partition layers.

Evidence in paper:

- `docs/design/logHRL.tex:1299`
- `docs/design/logHRL.tex:1303`
- `docs/design/logHRL.tex:1334`
- `docs/design/logHRL.tex:1461`
- `docs/design/logHRL.tex:1914`

The current runtime refresh always calls `build_dynamic_tower(...)`:

- `src/state_collapser/tower/runtime.py:199`
- `src/state_collapser/tower/runtime.py:216`

`build_dynamic_tower(...)` reconstructs tier `0` from visible base states and
edges, then repeatedly constructs fresh `QuotientTierView` objects:

- `src/state_collapser/tower/construction.py:115`
- `src/state_collapser/tower/construction.py:120`
- `src/state_collapser/tower/construction.py:137`
- `src/state_collapser/tower/construction.py:222`

Impact:

The final quotient tower may sometimes be computationally equivalent to what an
incremental algorithm would produce on the same discovered graph and same
schedule. But the runtime behavior, asymptotic claim, and tower-morphism story in
the paper are not implemented. There is no persisted prior tower, no delta-edge
propagation, and no explicit `G_t^\bullet -> G_{t+1}^\bullet` morphism.

## Finding 4: State partitions are implicit and mostly recoverable, but not first-class

Severity: medium.

The code's state-side representation is the strongest point of alignment.

Each tier maps base states to quotient-node identifiers:

- `src/state_collapser/quotient/projection.py:16`
- `src/state_collapser/tower/construction.py:229`

Each quotient node stores its base-state members:

- `src/state_collapser/quotient/cosets.py:16`
- `src/state_collapser/tower/construction.py:230`

The quotient-node identifier includes the tier and component data:

- `src/state_collapser/tower/construction.py:227`
- `src/state_collapser/tower/construction.py:228`

This is enough to recover a partition of the base state set at each tier. It is
also enough to query whether two states share a coset:

- `src/state_collapser/quotient/tier_view.py:48`
- `src/state_collapser/tower/runtime.py:178`

Impact:

For state cells alone, the code is computationally close to the paper. It does
not expose a dedicated `StatePartitionLayer` object, child-to-parent morphisms,
or a Young-diagram-style nested table, but the information is mostly recoverable
from `ordered_quotient_tiers`.

This is a "representation mismatch," not necessarily a mathematical mismatch.

## Finding 5: The action partition is not the paper's action partition

Severity: high.

This is the largest data-structure mismatch.

The paper says tier `0` action-side partition cells are outgoing-edge buckets:

```tex
Pi_0^A := { Out(s) | s in S_t^0 }
```

Evidence in paper:

- `docs/design/logHRL.tex:963`
- `docs/design/logHRL.tex:967`
- `docs/design/logHRL.tex:975`
- `docs/design/logHRL.tex:977`
- `docs/design/logHRL.tex:1058`
- `docs/design/logHRL.tex:1064`

The code instead gives every base edge its own base edge identifier at tier `0`:

- `src/state_collapser/tower/construction.py:125`
- `src/state_collapser/tower/construction.py:126`
- `src/state_collapser/tower/construction.py:127`
- `src/state_collapser/tower/construction.py:128`

At higher tiers, the code stores quotient edge membership keyed by quotient-edge
identifier:

- `src/state_collapser/tower/construction.py:237`
- `src/state_collapser/tower/construction.py:244`
- `src/state_collapser/tower/construction.py:245`

There is no first-class representation of:

- `Out_i(C)` for a state cell `C`;
- a state-cell-to-action-cell pointer;
- an action partition layer whose cells are outgoing action collections;
- action cells fibered over state cells by an explicit incidence relation.

The closest available field is:

- `src/state_collapser/quotient/tier_view.py:21`

But `outgoing_knowledge_by_tier` is keyed only by tier, not by state cell. It is
a global set of known edge identifiers for a tier, not a map:

```text
state_cell -> outgoing_action_cell_collection
```

Impact:

The code can often reconstruct quotient outgoing edges by inspecting the tuple
shape of quotient-edge identifiers, because those identifiers include the source
quotient node. But that is not a stable typed API and it is not the coupled
state/action partition table described in the paper.

This breaks direct implementation of the theorem-facing maps `pi_i^A`,
action-cell reward descent, and agent traversal over pooled outgoing action
information.

## Finding 6: Loop removal exists, but the stutter convention does not

Severity: high.

The paper now explicitly requires that actions becoming internal loops either:

- remain as formal stutter actions, or
- be removed while recording a reward/fiber correction.

Evidence in paper:

- `docs/design/logHRL.tex:1098`
- `docs/design/logHRL.tex:1585`
- `docs/design/logHRL.tex:1589`
- `docs/design/logHRL.tex:1648`
- `docs/design/logHRL.tex:1687`
- `docs/design/logHRL.tex:1708`

The code silently skips projected loops:

- `src/state_collapser/tower/construction.py:232`
- `src/state_collapser/tower/construction.py:235`
- `src/state_collapser/quotient/tier_view.py:55`
- `src/state_collapser/quotient/tier_view.py:60`

There is no stutter symbol in `ProjectionMap`:

- `src/state_collapser/quotient/projection.py:16`
- `src/state_collapser/quotient/projection.py:17`

There is no recorded loop/stutter correction in `RuntimeSnapshot`:

- `src/state_collapser/tower/snapshot.py`

Impact:

The quotient graph structure has loop disappearance, but the reward/path theorem
preconditions are not represented. This matters because the paper's reward
descent proposition depends on accounting for the reward contribution of removed
internal actions.

## Finding 7: Message passing exists only as vista annotation, not as tower construction

Severity: medium.

The paper's current version has moved past the earlier "message passing" wording
into partition-cell coalescence. Still, the key operational idea was that outgoing
information gets shared across contracted representatives.

The code has push/pull message methods:

- `src/state_collapser/graph/vista_graph.py:40`
- `src/state_collapser/graph/vista_graph.py:49`

And `TowerRuntime.step(...)` calls them:

- `src/state_collapser/tower/runtime.py:126`
- `src/state_collapser/tower/runtime.py:127`

But the tower builder does not consume those annotation stores. It rebuilds
visible base edges from the vista cache:

- `src/state_collapser/tower/construction.py:58`
- `src/state_collapser/tower/construction.py:63`
- `src/state_collapser/tower/construction.py:64`

Impact:

Outgoing information sharing in the actual tower is achieved indirectly by
projecting all visible base edges through the new quotient-node IDs. That can
produce a quotient graph with pooled outgoing edges, but it is not the
state-cell/action-cell pointer update mechanism described by the paper.

## Finding 8: The runtime does not yet support abstract quotient-action traversal and lift

Severity: medium-high.

The paper says that at tier `i`, the agent can choose an abstract outgoing action
from a state cell, and execution requires lift/refinement to make the action
executable in the base graph.

Evidence in paper:

- `docs/design/logHRL.tex:1131`
- `docs/design/logHRL.tex:1136`
- `docs/design/logHRL.tex:1749`
- `docs/design/logHRL.tex:1751`

The current learner/control surfaces mostly use tower positions as state keys,
but still choose primitive environment actions.

Evidence:

- `src/state_collapser/examples/plate_support_env/training.py:101`
- `src/state_collapser/examples/plate_support_env/training.py:102`
- `src/state_collapser/examples/plate_support_env/training.py:222`
- `src/state_collapser/examples/plate_support_env/runtime.py:261`

The generic `LiftResolveExecutor` protocol exists:

- `src/state_collapser/tower/control/executor.py:11`

But the concrete PlateSupport executor executes an integer primitive action and
then reads the active tier's target position from the resulting snapshot:

- `src/state_collapser/examples/plate_support_env/runtime.py:254`
- `src/state_collapser/examples/plate_support_env/runtime.py:261`

Impact:

The runtime can train a primitive-action learner keyed by tower positions. It
cannot yet train over quotient action cells and then lift/refine those choices.
That is weaker than the paper's traversal model.

## Finding 9: Test coverage currently proves interface survival, not paper-model correspondence

Severity: medium.

The existing focused tests pass:

```text
uv run pytest tests/quotient tests/tower/test_runtime.py tests/integration/test_vertical_slice.py
22 passed
```

But the tests do not cover the main paper-alignment requirements.

Current tests cover:

- projection lookup;
- reverse coset membership;
- cumulative global outgoing knowledge;
- one tiny two-state contraction;
- runtime position tracking;
- basic vertical slice survival.

Evidence:

- `tests/quotient/test_projection.py`
- `tests/quotient/test_cosets.py`
- `tests/quotient/test_tier_view.py`
- `tests/tower/test_runtime.py`
- `tests/integration/test_vertical_slice.py`

Missing tests:

- `ContractionPolicy.select(...)` actually determines `Sigma`;
- explicit ordered partition blocks are respected;
- every base-tier edge is accounted for exactly once under the intended schema;
- tier `0` action partitions are outgoing buckets;
- merged state cells point to merged outgoing action-cell collections;
- removed loops produce stutter symbols or reward correction records;
- incremental update gives the same result as full rebuild while touching only
  the delta;
- quotient action cells can be selected and lifted/refined to executable base
  actions.

Impact:

The green test suite does not validate the new `logHRL.tex` construction.

## Equivalence Assessment

The following table gives the most useful "homotopy/computational equivalence"
classification.

| Paper claim | Current code status | Equivalence judgment |
| --- | --- | --- |
| Sparse base graph with node/outgoing-edge access | `ExploredGraph` plus `VistaGraph` provide sparse visible graph data | Mostly equivalent |
| State partition at each tier | `ProjectionMap.state_projection` plus `CosetStore.quotient_node_members` | Computationally equivalent, not literal table object |
| Nested state Young diagram | Encoded indirectly through per-tier projections and recursive quotient-node IDs | Recoverable, but not first-class |
| Action partition initialized by `Out(s)` buckets | Code initializes one quotient edge per base edge | Not equivalent |
| Action diagram fibered over state diagram | No state-cell-to-action-cell pointer map | Not equivalent |
| Ordered partition of base-tier edge set | Code uses current eligible nontrivial edge batches | Not equivalent |
| Policy-defined contraction schema | Builder ignores `ContractionPolicy.select(...)` | Not equivalent |
| Contract selected edges and discard loops | Code contracts selected pairs and skips internal quotient edges | Partially equivalent |
| Stutter/reward correction for removed loops | No representation | Not equivalent |
| Incremental update along exploration | Full rebuild on refresh | Final-output equivalence possible; operationally not equivalent |
| Tower morphisms `G_t -> G_{t+1}` | No explicit morphism data | Not equivalent |
| Path-address maps on states | State map exists | Mostly equivalent |
| Path-address maps on actions | Edge projection exists only for live quotient edges; loops become `None` | Partial and theorem-insufficient |
| Abstract quotient action traversal/lift | Learners use primitive actions keyed by tower position | Not equivalent |

## Overall Judgment

The code and the paper are not in fatal contradiction if the code is understood
as a pre-paper scaffold that computes some quotient graph tiers. The state-side
quotient graph is close enough that one can see the intended shape.

But the current code would mislead a reader if presented as the implementation of
the current paper construction. The paper has moved to a more precise coupled
state/action partition-table model. The code still implements a lighter quotient
tier view centered on projection maps and reverse coset membership, with a
hard-coded edge batching rule and no action-table fiber structure.

The most important correction is not cosmetic. The implementation needs a real
contraction-schema surface and a real coupled action partition surface. Without
those, the code cannot faithfully support the paper's theorem-side claims about
action cells, reward descent, stutters, lift fibers, and quotient-action
traversal.

## Suggested Alignment Targets For A Future Implementation Plan

These are not implementation steps for this review task. They are the natural
alignment targets implied by the findings.

1. Introduce a first-class contraction schema object that produces ordered
   base-tier edge blocks.

2. Make `ContractionPolicy` either produce that schema directly or clearly rename
   it so users do not assume it controls tower contraction.

3. Introduce explicit state/action partition layer types, for example:

   ```text
   PartitionTower
   StatePartitionLayer
   ActionPartitionLayer
   StateCellId
   ActionCellId
   ```

4. Initialize tier `0` action cells as outgoing buckets over source state cells,
   not merely singleton base-edge identifiers.

5. Store an explicit incidence map:

   ```text
   state_cell_id -> outgoing action cell collection
   ```

6. Represent loop/stutter behavior explicitly, either by keeping formal stutter
   actions or by recording stutter reward/fiber corrections.

7. Add parent/child maps between partition layers so the Young-diagram nesting
   and tower morphisms are inspectable.

8. Implement incremental update as a separate mechanism from full rebuild, with
   tests proving equivalence of final tower state on small examples.

9. Add quotient-action traversal APIs:

   ```text
   outgoing_action_cells(tier, state_cell)
   lift_action_cell(...)
   refinement_fiber(...)
   ```

10. Add tests that directly encode the paper model rather than only asserting
    survival of the current runtime surfaces.

## Verification Performed

Commands run:

```text
uv run pytest tests/quotient tests/tower/test_runtime.py tests/integration/test_vertical_slice.py
```

Result:

```text
22 passed
```

I also ran a small in-memory behavior check showing that
`LabelContractionPolicy({"y"})` did not control the actual selected contraction
edge; the builder selected an `x`-labelled edge because the builder uses stable
edge ordering and a 20 percent batch rule rather than `policy.select(...)`.

___
___
# PO/LLM Discussion
- **Issue 1:** The contraction policy does not actually define the contraction schema used by the tower builder;
   - **PO Response:** Right. Do we even have an edge-labelling system that would allow us to define schemas associated to those to main examples in the paper: dimensionwise and random at some rate? What is missing? Is it a situation where we could tack just a bit on in a natural way, or is this a refactoring-levle issue?
   - **LLM Reply:** We have the beginning of the needed system, but not the actual schema system yet. At the core level, `PrimitiveAction` has `labels`, `BaseEdge` has `labels`, and `LabelContractionPolicy` can select edges whose edge or action labels match a requested set. `SeededRandomContractionPolicy` also exists. So the raw hooks for "dimensionwise" and "random" are present. What is missing is that these hooks are not wired into tower construction as the source of the ordered contraction schema.

     More concretely: a dimensionwise schema needs actions/edges in the relevant environments to carry labels such as `x`, `y`, `z`, `voice:bass`, `voice:inner`, `voice:upper`, `plate:x`, `plate:y`, `theta`, `support:e1`, etc. Most current example runtimes construct `PrimitiveAction(...)` with no labels and construct `BaseEdge(...)` with no labels. The robot toy does label some target regions, but that is region metadata, not a general dimensionwise action schema. So the label field exists, but the environments are not yet systematically labelling movement dimensions.

     A random-at-rate schema also needs more than the current random policy. The existing random policy selects a fixed `sample_size` from a single `LocalStar`. The paper wants something closer to an ordered partition of the base-tier edge set, or of newly discovered base-tier edges, into random blocks at some rate. That means we need a schema object that can take the current base edge universe and return blocks like `Sigma_0^1, Sigma_0^2, ...`, not just a local-star selector.

     My judgment: adding labels to actions/edges is a natural, small-to-medium extension. Making the tower builder actually consume a schema is refactoring-level, but localized refactoring. It is not a whole-package rewrite. The refactor target is mainly `tower/construction.py` plus the `contract/policy.py` surface: either rename the current `ContractionPolicy` as a local selector/message policy, or promote it into a real `ContractionSchema`/`EdgeBlockSchema` surface that produces ordered base-edge blocks.
   - **PO Follow-up:** Give me a runtime/efficiency evaluation of this. We are now entering the phase where we're trying to really improve performance, so we don't want to add things that will significantly slow down the system. I cna't imagine why this would be somethign that could cause that, but please evaluate.
   - **LLM Assement:** The edge-label/schema piece should not be a runtime problem if we implement it as a schema assignment pass, not as a repeated per-tier policy recomputation. The current labels themselves are just small tuples on `PrimitiveAction` or `BaseEdge`; checking them is cheap relative to graph traversal. A dimensionwise schema can be nearly free at runtime if the action already carries a compact dimension label and the schema maps that label to a block index.

     The thing to avoid is calling a local-star policy over and over while constructing every tier. That would keep policy selection in the hot loop. The faster design is:

     ```text
     new edge arrives -> assign schema block once -> store block id on edge metadata/index
     tower update -> process only edges whose block id is active for the affected tier/update
     ```

     For a random-at-rate schema, the same principle applies. We should not resample the whole visible graph every refresh. We should assign newly visible edges into persistent random blocks once, using a seeded schema state. That is `O(Delta m)` for the new vista, not `O(m_t)` every step.

     So the runtime assessment is:

     - adding labels is negligible;
     - adding an explicit schema object is likely runtime-positive, because it lets us stop sorting/scanning arbitrary eligible edges repeatedly;
     - persisted random block assignment is essential for both speed and semantic stability;
     - the only way this slows things down is if we implement schema selection as heavyweight callback logic inside every tier loop.

     My recommendation is to treat the schema as cached structural metadata, not as a dynamic policy inference step.

   - **PO Reply:** Ok I like this. Does this include details that make the schema itself is a detail you set up, maybe in training loop, that plugs in to nice other surfaces?

   - **LLM Reply:** [...]
- **Issue 2:** There is no explicit ordered partition of the full base-tier edge set into contraction blocks;
   - **PO Response:** Please explain in a bit more detail. Is the focus here on "full," because that's not necessarily an issue. If the focus is on "ordered partition," then yes we may want to swap out what data structure we're using. Please explain what your focus is here.
   - **LLM Reply:** The main concern is `ordered partition`, not `full` in the sense of the entire hidden graph. In the online setting, "full" should mean the edge universe currently being scheduled: the currently discovered/visible base-tier edge set at time `t`, or the newly discovered delta edge set in the incremental algorithm. It does not need to mean every edge of the true hidden environment.

     The issue is that the code does not currently create a committed block decomposition of the relevant base-tier edge set. Instead, at each tier it recomputes "all currently nontrivial visible edges," sorts them, takes the first 20 percent, contracts those, and repeats. That is a valid iterative contraction heuristic, but it is not the data structure described in the paper.

     In the paper, the schema is an object like:

     ```text
     A_t^0 = Sigma_0^1 sqcup Sigma_0^2 sqcup ... sqcup Sigma_0^d
     ```

     where each block has an identity in the schedule. Dimensionwise blocks might be `x`, then `y`, then `z`; random blocks might be a seeded random partition into rate-sized chunks. In the current code, the block is just "whatever sorted nontrivial edges are in the first 20 percent this tier." So the code is ordered procedurally, but it is not representing an ordered partition.

     My refinement to the original finding is: the word `full` should be softened. The important mismatch is that there is no explicit ordered block schema over the chosen edge universe.
   - **PO Follow-up:** Good. Please evaluate, without any implementation in code, but in runtime thinking instead, if swapping out this core data structure, the one currently being used, with the nested partitino structure should improve runtime. I think it would if implemented correctly, because it's so much lighter and uses far fewer updates.
   - **LLM Assement:** I agree with your instinct. If implemented correctly, the nested partition structure should improve runtime substantially, especially once graphs are larger than toy examples.

     The current builder repeatedly reconstructs tiers from the base edge list. At each tier it scans states, scans edges, projects edge endpoints, drops loops, and builds quotient-edge identifiers. That means the package keeps rediscovering structure that a partition table would already know.

     A nested partition structure changes the hot operation from:

     ```text
     rescan all base edges and rebuild quotient edges
     ```

     to:

     ```text
     union two state cells
     union or relink their outgoing action-cell collections
     mark/remove newly internal edges
     update affected pointers
     ```

     That is usually much lighter because contractions are local. If a new vista adds a small number of edges, most partition cells do not change. The update should touch only the cells incident to the new edges and whatever action cells become newly internal or newly outgoing after coarsening.

     The caveat is "if implemented correctly." A naive nested partition table that copies whole cells at every tier could be worse. The right implementation should use:

     ```text
     stable integer cell ids
     union-by-size/rank for state cells
     action-cell collections with structural sharing
     dirty queues for affected cells
     explicit outgoing pointers
     no full per-tier edge scan unless validating/debugging
     ```

     With that discipline, the asymptotic shape improves from repeated global rebuilds toward amortized local coarsening. In sparse RL graphs, where each exploration step usually adds a small local vista, this should be a real performance improvement.

   - **PO Reply:** I support this approach. This is what I want to blueprint an then implement.
- **Issue 3:** The runtime rebuilds the full tower from visible graph data on each refresh, rather than incrementally propagating only the new vista;
   - **PO Response:** Please clarify. Are you saying that the package does unecessary computation every step? What is your focus on this point?
   - **LLM Reply:** Yes, partly: the package currently does unnecessary computation every refresh, because `TowerRuntime._refresh_dynamic_tower(...)` calls `build_dynamic_tower(...)`, which reconstructs tier `0` and all subsequent tiers from the current visible graph. It does not update an existing partition tower by applying only the new vista/delta.

     But the bigger focus is semantic, not performance. The TeX document now says the online construction has tower morphisms `G_t^\bullet -> G_{t+1}^\bullet` and that only newly discovered base-tier edges need to be propagated through existing partition layers. The code does not maintain that morphism-level story. It may produce the same final quotient tiers that an incremental algorithm would produce on a small deterministic graph, but it gets there by rebuilding, not by carrying old partition cells forward and coarsening them.

     For now, this is probably acceptable as an implementation scaffold if the repo is still in research mode. Full rebuild is simpler and easier to inspect. The risk is that the paper/runtime story will overclaim: if we say the package implements incremental partition propagation, it does not. If we only say the package currently computes a current tower by full rebuild, while the paper describes the intended online incremental form, that is honest.

     One extra caution: once random schemas are real, full rebuild can become semantically dangerous unless the random partition is persisted. Otherwise the tower can jitter because "random schema at time `t`" gets resampled during rebuild instead of extended incrementally.
   - **PO Follow-up:** Ok I totally agree. We absolutely should be incrementally propagating only the new vista instead. Please give me a high level outline of how we would make this change to the package.
   - **LLM Outline:** High-level package change:

     1. Introduce a persistent `PartitionTower`-like object owned by `TowerRuntime`.

        This object would hold the base graph registry, schema assignments, state partition layers, action partition layers, current positions, and any cell/morphism metadata. `TowerRuntime` would stop treating `build_dynamic_tower(...)` as the normal update path.

     2. Split tower construction into `initialize` and `update_with_vista`.

        `initialize` creates tier-0 singleton state cells and tier-0 outgoing action buckets. `update_with_vista` receives only newly discovered states/edges, adds singleton cells for new states, adds outgoing action data for new edge buckets, assigns schema blocks to new edges, and enqueues contraction consequences.

     3. Persist the contraction schema.

        Each base edge should receive a schema block identity exactly once for the active schema. Dimensionwise schemas assign by label; random schemas assign by seeded block/rate logic. The update loop should process block identities, not recompute arbitrary "eligible edge" sets from scratch.

     4. Propagate contractions through affected partition cells.

        For each newly active contraction edge, look up its current endpoint cells at the relevant tier. If they are distinct, merge the state cells, merge their outgoing action-cell collections, remove or mark internal loops according to the loop/reward convention, and enqueue any downstream effects caused by the merge.

     5. Maintain explicit outgoing pointers.

        Each state cell should know its outgoing action-cell collection. This is what prevents repeated global edge scans. When two state cells merge, the outgoing pointer for the merged cell is built from the two prior outgoing collections plus local loop filtering.

     6. Keep current positions and morphisms as update outputs.

        After the update, `RuntimeSnapshot` can still expose `ordered_quotient_tiers`, but internally the package should know how old cells map into new cells. This gives the `G_t^\bullet -> G_{t+1}^\bullet` story a real implementation referent.

     7. Keep full rebuild as a debug/validation path.

        We should probably retain a slow full-build function for tests. The incremental tower can be checked against full rebuild on small deterministic graphs. That gives us confidence while allowing production/runtime paths to be incremental.

   - **PO Reply:** I fully support all this. I want to blueprint, gameplan, and then implement this.
- **Issue 4:** The action-side partition / outgoing-action-cell story is not represented as the paper describes;
   - **PO Response:** High level, what happens instead?
   - **LLM Reply:** High level: the code builds quotient edges, not an action partition table.

     At tier `0`, every base edge gets its own edge identifier. At tier `i`, the code scans every base edge, projects its source and target states into tier-`i` quotient nodes, throws the edge away if the source and target project to the same quotient node, and otherwise creates a quotient-edge identifier of the form:

     ```text
     ("tier-edge", tier_index, source_node, action_identity, target_node)
     ```

     It then records which base edges are members of that quotient edge.

     That gives us a quotient graph edge set. It does not give us the paper's action-side data structure, where the action table starts as outgoing buckets `Out(s)` and then coarsens in parallel with state cells. In the paper's data structure, a state cell points to its outgoing action-cell collection. In the current code, there is no first-class object for "the outgoing action cell collection of this state cell." You could reconstruct something like it by scanning quotient edges and grouping by source quotient node, but that grouping is not stored as the core representation.

     So the current implementation answers: "What quotient edges exist after this contraction?" The paper's structure answers: "For this state coset, what outgoing action information has been pooled across its representatives, and how does that action information sit in the nested action partition tower?"
   - **PO Follow-up:** The latter seems blatantly more efficient. Does the fix here basically overlap with previous point?
   - **LLM Assement:** Yes, it overlaps heavily with the previous point. The action-side partition fix is basically one of the main reasons the incremental partition update becomes faster.

     The current code builds quotient edges by scanning all base edges and asking, for each edge, where its source and target project at the next tier. That is global edge reconstruction. The paper-style action table instead keeps outgoing action data attached to state cells. Then when state cells merge, the action update is local:

     ```text
     Out(C_ab) = Out(C_a) union Out(C_b), with internal edges removed/handled
     ```

     That means the package no longer needs to rediscover outgoing structure by scanning the whole edge set. It can update the outgoing action data exactly where the contraction occurred.

     So the fix is not separate from incremental propagation. The package needs:

     - persistent state cells,
     - persistent action cells/outgoing buckets,
     - a state-cell-to-action-cell incidence map,
     - local merge operations,
     - loop/internal-edge handling during those local merges.

     The runtime win is especially strong for action queries. With current tuple-shaped quotient edges, "what can I do from this coset?" is not a first-class local lookup. With outgoing pointers, it is one map lookup plus iteration over that cell's outgoing collection.

   - **PO Reply:** I fully support this. Include this in blueprint and then gameplan.
- **Issue 5:** State-cell-to-action-cell outgoing pointers are not first-class data;
   - **PO Response:** Give me complete explanation of `first-class` from CS perspective.
   - **LLM Reply:** In CS, saying something is `first-class` means it exists as a real object in the program's model, not merely as an implicit consequence of other objects. A first-class thing usually has its own representation, can be named, stored, passed around, queried, tested, serialized, and protected by invariants.

     For example, functions are first-class in Python because a function can be bound to a variable, passed as an argument, returned from another function, stored in a list, and called later. By contrast, "the third line of a string happens to contain a function name" is not first-class function structure. It is text from which function-like information might be inferred.

     Applied here, a first-class state-cell-to-action-cell pointer would be an explicit data structure, something like:

     ```text
     outgoing_action_cells_by_state_cell: dict[StateCellId, frozenset[ActionCellId]]
     ```

     or a method backed by such storage:

     ```text
     partition_layer.outgoing_action_cells(state_cell_id)
     ```

     It would have tests saying that after merging two state cells, the merged state cell points to the merged outgoing action-cell collection with loops removed or recorded.

     What we have now is weaker. The quotient-edge identifier includes a source quotient node, and `CosetStore` records edge members. A caller could infer outgoing edges for a state cell by scanning all quotient-edge IDs and selecting those whose tuple contains that state cell as source. But that relationship is not named as a core object, not protected by a type, not directly queryable, and not tested as an invariant. That is why I called it not first-class.
   - **PO Follow-up:** Got it. Explain to me why it *should* be first class, especially *against* my gut instinct that making these outgoing pointers first class will be taxing on RAM.
   - **LLM Reply:** The RAM concern is reasonable, but in this case first-class outgoing pointers should usually save work without requiring much extra memory. The important distinction is between duplicating outgoing edge data and storing a pointer/index to outgoing edge data. We do not want to copy all outgoing edges into every representative node. We want each state cell to carry a reference to one action-cell collection.

     Conceptually:

     ```text
     StateCellId -> ActionCellCollectionId
     ActionCellCollectionId -> compact set/list of ActionCellId
     ActionCellId -> member edge ids or representative data
     ```

     The first line is tiny: one pointer or integer id per active state cell. The second and third lines can use structural sharing and union-by-size so merges do not repeatedly copy huge collections.

     Also, the information already exists implicitly. The current implementation stores quotient-edge ids containing source-node data, and a caller can infer outgoing edges by scanning/grouping those ids. Making the pointer first-class is basically materializing the index the system already needs. In database terms, this is like adding an index on `source_cell`. It costs some memory, but prevents repeated table scans.

     Why it should be first-class:

     - It makes the core agent query cheap: `outgoing actions from current coset`.
     - It makes the algorithm match the mathematical object.
     - It gives tests a direct invariant to assert after merges.
     - It avoids reverse-engineering tuple-shaped quotient-edge identifiers.
     - It localizes updates to affected cells instead of forcing global scans.

     The RAM-safe version should use compact ids, not heavy Python object graphs everywhere. If we use integer ids, `slots=True` dataclasses where needed, and shared cell collections, the pointer layer should be cheap compared with the cost of rebuilding/scanning quotient edges repeatedly.

   - **PO Reply:** I fully support this.
- **Issue 6:** Loop removal has no stutter symbol or reward/fiber correction record;
   - **PO Response:** So this one is a bit different. I think that the stutter symbol... I'm suspicious that it is actually doing anything helpful. I think it should be optional in this system. The reason is that the stutter symbol sort of undoes the coarsening. If we throw out loops and just ignore the missing actions, we get something meaningful for training: rewards for inter abstract task movement, ignore inner abstract task movement. Does this make sense? Please push back.
   - **LLM Reply:** This makes sense, and I agree with the instinct that stutter actions should not be automatically exposed as ordinary selectable abstract actions. If a loop is internal to a coset, keeping it as a live action at the quotient level can absolutely blur the abstraction and partially undo the purpose of coarsening. For many training regimes, "ignore intra-coset motion; train on inter-coset movement" is a coherent and useful quotient objective.

     The pushback is only this: silently throwing loops away changes what quantity the quotient reward is estimating. If the fine-scale reward includes rewards/costs for internal movement, and the quotient level ignores those moves, then quotient reward is no longer an exact direct image of fine reward. That is fine if it is an intentional modeling choice. It is not fine if the theorem or docs claim exact reward descent from the original fine MDP/path reward.

     So I would separate two ideas:

     ```text
     navigation semantics: loops are removed by default
     reward accounting semantics: choose what happens to internal-loop reward
     ```

     I would not make stutter a required exposed action. I would make the loop convention explicit. Possible conventions:

     ```text
     drop_internal: ignore loop rewards at this tier
     aggregate_internal: record internal reward statistics as a fiber/residual term
     formal_stutter: retain a non-navigation stutter symbol for theorem/accounting use
     ```

     My recommended default is probably `drop_internal` for practical coarse training, with enough metadata to say "this quotient objective ignores intra-coset reward." If we later want theorem-level equivalence to fine cumulative reward, then we need either `aggregate_internal` or a formal stutter/correction. In short: optional stutter, yes. Silent unrecorded loop deletion, no, unless we explicitly accept that the quotient task is a different reward problem.
   - **PO Follow-up:** Yeah but the whole point is that direct image is not an exact reward. The whole point is forgettign when you go downstairs. ...ALSO: I just had you add other direct image aggregation possiblities in paper. That needs to be incorporated so it should be part of what we're discussing here.
   - **LLM Reply:** Agreed. I would revise my earlier framing here. I was too attached to the "exact reward descent" reading. The better view is: going downstairs is intentionally forgetful, and direct image reward is an aggregation choice over the forgotten fiber, not necessarily an exact preservation of fine reward.

     With the paper update, the quotient reward should be understood as:

     ```text
     action cell D -> Agg({ fine rewards / outcomes inside D })
     ```

     where `Agg` might be mean, sum, max, softmax, order-`p` mean/norm, or something environment-specific. Under that picture, dropping internal loops is not automatically a defect. It is one valid forgetting convention:

     ```text
     coarse reward = aggregate rewards for inter-cell movement
     internal movement = ignored at this abstraction level
     ```

     That is especially natural if the quotient task is "choose good exits between abstract regions," not "estimate the exact fine-scale return accumulated while wandering inside a region."

     The only thing I would still insist on is that the convention be explicit. Not explicit as in "record every thrown-away loop reward," but explicit as in the tower/reward config says:

     ```text
     internal_loop_policy = drop
     reward_aggregator = max | mean | sum | p_norm | softmax | custom
     ```

     Then the theorem and diagnostics can say the quotient objective is approximate/aggregated/forgetful, not exact. For practical RL, this is probably the right default: remove loops from quotient navigation, choose an aggregation rule that matches the training purpose, and treat any fine-scale mismatch as a residual or refinement-layer issue.

   - **PO Reply:** I'm happy with this.
- **Issue 7:** The tower is not yet used as an abstract action traversal lift surface.
   - **PO Response:** I think this might not be a problem. We had a lot of design discussion around the training loop being the left-to-engineer piece.
   - **LLM Reply:** I agree this might not be a problem, depending on what claim we want the package to make. The training loop itself should remain engineer-owned. We should not force all users into one rigid tower-training loop.

     The distinction I want to preserve is between:

     ```text
     package owns component surfaces
     engineer owns training loop composition
     ```

     It is okay if the package does not automatically train over quotient action cells. It is also okay if the reference learners are simple and primitive-action-based. But if the paper says the tower lets an agent traverse abstract outgoing action cells and then lift/refine to executable behavior, the package should eventually expose the components that make that possible.

     So I would downgrade this from "bug" to "missing surface." The missing surfaces are things like:

     ```text
     outgoing_action_cells(tier, state_cell)
     representatives(action_cell)
     lift_candidates(action_cell, current_base_state)
     refinement_fiber(coarse_action_or_address)
     ```

     The package does not need to decide the training loop. But a serious RL engineer should be able to build that loop without reverse-engineering tuple-shaped quotient-edge IDs. That is the line I would draw.
   - **PO Follow-up:** Ok I like this direction better. Please give me more detail.
   - **LLM Follow-up:** The package should expose enough component surfaces that an ML engineer can build a quotient-action training loop, without the package prescribing that loop.

     The minimal useful surfaces are:

     ```text
     current_state_cell(tier)
     outgoing_action_cells(tier, state_cell)
     action_cell_members(action_cell)
     representative_edges(action_cell)
     lift_candidates(action_cell, current_base_state)
     reward_aggregate(action_cell, aggregator=...)
     refinement_fiber(coarse_address_or_action_cell)
     ```

     Then the engineer can choose among several loop styles:

     ```text
     primitive-action loop keyed by tower position
     quotient-action loop with immediate lift
     coarse policy downstairs plus refinement policy upstairs
     actor-critic over action cells with primitive-action executor
     Q-learning over action-cell ids with custom lift resolver
     ```

     This matches the training-surface philosophy we discussed earlier: the package should make the parts good, inspectable, and efficient; the engineer owns the loop.

     The key point is that "not used by default" is fine. "Impossible to use without spelunking internal tuple ids" is not fine. If the tower really is an address system, the package should expose the addressable objects: cells, outgoing action cells, fibers, representatives, and lift candidates.

   - **PO Reply:** I'm happy with this.
- **PO Request:** I understand that we haven't created an explicit blueprint for the upgrade we're discussing here, but I'd like an rough assement of overall improvement in runtime for the changes we're proposing here.
   - **LLM Runtime Improvement Assement:** Roughly, I would expect a meaningful runtime improvement on any environment where the discovered graph grows beyond toy size, and potentially a large improvement once online exploration runs for many steps.

     The current shape is closer to:

     ```text
     each step:
       rebuild tier 0 from visible graph
       for each tier:
         sort/scan visible edges
         scan base states
         rescan base edges to build quotient edges
     ```

     If the visible graph grows roughly linearly with exploration time, repeatedly rebuilding from scratch can create a cumulative cost that behaves much closer to quadratic over the exploration interval:

     ```text
     sum_t O(d_t * (n_t + m_t))
     ```

     where `n_t` and `m_t` grow with time.

     The proposed partition-tower update should move the normal online path toward:

     ```text
     each step:
       add Delta states/edges
       assign schema blocks to Delta edges
       process affected contractions
       update affected state/action cells and pointers
     ```

     In sparse environments, `Delta` is small: usually the new local vista around the realized transition. That makes the expected online cost closer to local update cost:

     ```text
     O(schema assignment on Delta edges)
     + O(number of affected cell merges)
     + O(size of affected outgoing collections)
     ```

     With union-by-size/rank and structural sharing, the total cost of merges should be near-linear or quasilinear in the amount of graph information actually discovered, rather than repeatedly proportional to the whole discovered graph at every step.

     Practical expectation:

     - On tiny tests, the new structure may be neutral or slightly slower because of extra bookkeeping.
     - On medium graphs, it should reduce repeated scans and become noticeably faster.
     - On long online runs, it could be a major improvement because it avoids rebuilding old tower structure every step.
     - The biggest wins should come from explicit outgoing pointers and delta propagation, not merely from renaming policy/schema surfaces.

     My rough qualitative estimate: this is not a micro-optimization. It changes the runtime model from repeated global reconstruction to amortized local maintenance. If implemented well, it is plausibly the difference between "research scaffold that works on small examples" and "runtime architecture that can scale to serious evaluation."
