# Counterpoint First Serious Learning Evaluation Readout

<!-- ![Artifacts: Partial](badges/artifacts_partial.svg)
![Behavior: Mixed](badges/behavior_mixed.svg)
![Goals: Partial](badges/goals_partial.svg)
![Scope: Fixture Only](badges/scope_fixture_only.svg)
![Provenance: Local Tmp](badges/provenance_local_tmp.svg) -->

## Status At A Glance

- Artifact evidence: partial; required result tables exist and were readable,
  but expected evaluation and arm manifests are absent.
- Behavioral result: mixed; direct arms and the empty-schema tower execute real
  steps, while non-empty tower arms complete artifacts but expose lift/action
  realization failures.
- Goal result: partially met; the run validates the serious harness and exposes
  the key tower-control failure mechanism, but does not show tower advantage.
- Claim scope: fixture-only; claims apply only to
  `counterpoint_symbolic_n3_small_v001`, the locked budget,
  `tensor_available_disabled`, and this artifact set.
- Provenance: local temporary artifact root; the evidence is source-bound from
  this repo readout but has not been promoted as a durable artifact bundle.

This repository directory is the human-readable readout surface for the
counterpoint first serious learning evaluation.

Source evaluation root:

```text
/private/tmp/bbb-counterpoint-serious-learning-serious-001/evaluations/counterpoint_first_serious_learning_v001
```

Source binding:

```text
readout_source.json
```

To regenerate this repo-side readout, point the protocol at this directory, not
at the raw artifact root:

```text
execute artifact-table readout pointed at folder /Users/foster/big_boy_benchmarking/docs/evaluations/counterpoint_symbolic_v001/first_serious_learning
```

Protocol applied:

```text
docs/prime_directive/artifact_table_to_readable_document_protocol.md
```

## Summary of Goals Behind this Evaluation

This evaluation asks whether the first real counterpoint benchmark can support a
meaningful comparison between direct learning on the concrete symbolic graph and
tower-control learning through contraction schemas.

The environment is `counterpoint_symbolic_n3_small_v001`, a benchmark-owned
finite symbolic hidden graph. The goal is not to generate beautiful music. The
goal is to compare learning/control behavior under a fixed legality contract,
reward bundle, action-mask policy, seed/budget discipline, and artifact
contract.

The key baselines are direct tabular Q and the empty-schema tower. Direct
tabular Q is the primary concrete-environment learner baseline. The empty-schema
tower checks whether the tower runtime and active-tier control path work when no
nontrivial contraction is present. The non-empty tower arms then test whether
random, structured motion, and intentionally bad contraction schemas can realize
valid concrete actions and support learning through the tower interface.

This readout is therefore a diagnostic learning/control evaluation, not a
musical-quality report, tensor-enabled performance result, CUDA/GPU result,
production performance result, or general claim that towers are better or worse
than direct learning.

## Summary of Methodology Behind this Evaluation

This readout summarizes a locked serious-run artifact set followed by
aggregation and human readout generation. The source binding points at a local
artifact root under `/private/tmp`, while this directory is the durable
repo-side readout surface.

The evaluation compares direct environment arms against active-tier
exploit/explore tower-control arms under shared seed, budget, mask, artifact,
timing, and linearization discipline. The direct arms are `direct_masked_random`
and `direct_tabular_q`. The tower arms are the empty-schema tower, random
balanced and unbalanced contraction towers, structured motion tower, and
bad/adversarial tower.

The budget lock records `counterpoint_symbolic_n3_small_v001`,
`tensor_available_disabled`, 16 episodes per run, 4 replicates, 3 random schema
seeds, and a max horizon of 8 steps per episode. The aggregate tables summarize
returns, confidence intervals, baseline deltas, learning curves, timing
categories, controller events, schema diagnostics, and per-run lift/action
realization evidence.

The methodology can support artifact-completion, behavioral-status, and
diagnostic claims for this fixture and budget. It cannot support tensor-enabled,
CUDA/GPU, musical-quality, production-performance, or general tower-superiority
claims.

## One-Screen Verdict

All seven required arms produced machine-readable artifacts, and every run row
is marked `success`. That is artifact success, not behavioral success.

The direct environment arms and the empty-schema tower arm executed real
8-step episodes and received nonzero return. The non-empty tower arms completed
artifact runs but failed behaviorally: their episodes have mean return `0.0`,
mean step count `0.0`, and success rate `0%`. The per-run lift-fiber artifacts
show repeated `invalid_action_index` failures for those non-empty tower arms.

This run is useful diagnostic evidence about the current tower-control/action
realization surface. It does not support a positive tower-performance claim.

## Files

- [readout_source.json](readout_source.json): source binding from this repo readout surface to the raw artifact tables.
- [result_readout.md](result_readout.md): full human readout.
- [glossary.md](glossary.md): field and arm translations.
- [runbook.md](runbook.md): reconstructed commands and rerun notes.
- [artifact_index.md](artifact_index.md): evidence map with file purposes.
- [results/summary.md](results/summary.md): compact reader-facing result summary.
- [results/human_summary.md](results/human_summary.md): short result summary.
- [results/arm_readout_table.md](results/arm_readout_table.md): reader-facing arm table.
- [results/diagnostic_findings.md](results/diagnostic_findings.md): behavioral failure analysis.
- [results/timing_readout.md](results/timing_readout.md): timing summary with category boundaries.

## Claim Boundary

This readout is limited to `counterpoint_symbolic_n3_small_v001` under
`tensor_available_disabled`. Tensor execution was disabled. This is not a CUDA,
GPU, tensor-enabled, musical-quality, general superiority, or production
performance result.

## Provenance Status

The source binding for this readout is `readout_source.json`. It identifies the
source artifact root, source evaluation root, source tables, environment
instance, linearization mode, claim boundary, goal-summary sources, and
expected-file policy.

Absent files are classified by expectation status:

| File | Classification | Expectation source | Interpretation |
| --- | --- | --- | --- |
| `evaluation_manifest.json` | `expected_missing_gap` | Serious evaluation artifact contract | Expected evaluation-level provenance is absent. |
| `evaluation_arm_manifest.json` | `expected_missing_gap` | Serious evaluation artifact contract | Expected arm-contract provenance is absent. |
| `calibration_summary.json` | `conditional_absent` | Calibration path contract | Expected for calibration, not necessarily for this locked serious run. |
| `calibration_run_index.csv` | `conditional_absent` | Calibration path contract | Expected for calibration, not necessarily for this locked serious run. |
| `calibration_recommendation.md` | `conditional_absent` | Calibration path contract | Expected for calibration, not necessarily for this locked serious run. |

The aggregate, run index, budget lock, learning curves, timing summary,
controller summary, schema diagnostic summary, and per-run diagnostic files were
available and used for this readout.

## Clarifying Questions And Turns

#### Project Owner / Evaluator Turn

> Ok. The two things I need to understand better here are (1) these tower arms: *empty-schema*, *random balanced* and *unbalanced*, *structured motion*, and *bad/adversarial*, and then (2) the meaning of each of your statements here: "their episodes have mean return 0.0, mean step count 0.0, and success rate 0%. The per-run lift-fiber artifacts show repeated invalid_action_index failures for those non-empty tower arms."

#### Embedded Engineering Consultant / Codex Turn

> The tower arms are all attempts to run the same active-tier
> `tower_exploit_explore` control loop while changing only the contraction
> schema. The contraction schema is the experimental knob: it decides how the
> concrete counterpoint graph is grouped into coarser tower addresses.
>
> `empty-schema` is the tower shell with no meaningful contraction. It is not
> supposed to be clever. Its job is to ask: if we route through the tower
> machinery but do not compress the graph in a nontrivial way, can the system
> still execute ordinary concrete counterpoint actions? In this run, yes: the
> empty-schema tower has 64 episodes, mean return `12.830`, mean step count
> `8.0`, and 100% episode success. So the tower shell itself is not completely
> broken.
>
> `random balanced` is a control schema. It groups states/actions randomly while
> trying to keep the quotient cells relatively balanced. Its purpose is to test
> whether compression by itself helps. If this worked well, we would be
> suspicious that any arbitrary compression can help. If it fails, that suggests
> the structure of the grouping matters.
>
> `random unbalanced` is a worse random control. It intentionally allows skewed
> cells, such as giant cells or singleton-heavy partitions. Its purpose is to
> test a likely pathology: contraction that destroys addressability or produces
> messy lift fibers.
>
> `structured motion` is the first real positive candidate schema. It groups by
> counterpoint-ish local motion labels such as direction pattern, interval
> motion, beat phase, or related edge labels. This is the schema family we hoped
> might preserve useful action/reward structure better than random grouping.
>
> `bad/adversarial` is the negative control. It intentionally overcompresses or
> groups incompatible things. It exists so the diagnostics have something that
> should visibly fail. A benchmark where the bad schema looks just as good as
> the structured schema would be suspicious.
>
> The second sentence needs careful unpacking. `mean return 0.0` means those
> non-empty tower episodes accumulated no reward. `mean step count 0.0` is more
> severe: those episodes did not execute even one concrete environment step.
> `success rate 0%` means every episode row for those arms is marked
> unsuccessful. So this is not "the agent explored badly for 8 steps and got low
> reward." It is "the tower controller never successfully realized an executable
> concrete action for those episodes."
>
> The `invalid_action_index` lift-fiber failures identify where that happened.
> The non-empty tower controller descends/explores at active tiers, but when it
> tries to lift or realize an abstract/tower action into a concrete environment
> action, the chosen action index does not map to a valid concrete action. That
> blocks `exploit_execute` and `train`, leaving zero concrete steps. This is why
> the current readout treats non-empty towers as behavior-failed rather than as
> legitimate zero-performance learners.
>
> The important interpretation is: this run validates the harness and shows the
> empty tower shell can execute, but it does not yet evaluate whether
> structured motion is a good contraction for learning. The non-empty schemas
> are failing at action realization before learning can really happen.

#### Project Owner / Evaluator Turn

> Great. That's what I was expecting. Could it be that the reason we have all these `0.0` measurements because there are not actual rewards present yet, and no actual model to drive a policy in the first place?

#### Embedded Engineering Consultant / Codex Turn

> For rewards: no, that is not the main explanation. Rewards are present in
> this environment. We know that from two independent facts. First, the reward
> bundle exists in the counterpoint environment implementation. Second, and more
> importantly for this readout, the direct arms and the empty-schema tower arm
> actually receive nonzero returns around `12.8`. If the environment had no real
> reward signal, those arms would not be getting meaningful nonzero return
> while the non-empty towers alone get `0.0`.
>
> For "no actual model": partially, but not in the way that explains these
> zeroes. There is not a big trained neural policy here. The serious evaluation
> is deliberately modest: masked random, direct tabular Q, and tower
> exploit/explore with tabular-Q surfaces. But that is enough to choose actions
> and step the environment. The direct masked-random arm has no learning model
> at all and still executes 8-step episodes with nonzero reward. So lack of a
> sophisticated model is not sufficient to explain `0.0` return and `0.0`
> steps.
>
> The crucial clue is `mean step count 0.0`. A weak or untrained policy would
> usually still take legal or semi-legal concrete steps and then earn low,
> noisy, or bad returns. Here the non-empty tower arms do not reach concrete
> environment stepping. The controller explores at tower tiers, then the lift
> path tries to realize an abstract/tower action as a concrete environment
> action, and that attempt fails with `invalid_action_index`.
>
> So the current best interpretation is not "we forgot rewards" or "there is no
> policy." It is: the non-empty contraction schemas expose a mismatch in the
> tower action-realization interface. The tabular/explore machinery can choose a
> tower-side action index, but for non-empty schemas that index is not being
> mapped into a valid concrete counterpoint action. Because no concrete action
> executes, no environment transition happens, no reward can be earned, and no
> training event can occur.
>
> That distinction matters for the next implementation question. We should not
> respond by adding reward shaping or a stronger learner first. The next useful
> diagnostic is lower-level: inspect the selected tower action index, the active
> tier's available action count, the lift fiber for that abstract action, and
> the concrete legal-action mask. The bug or missing design is probably in that
> action-index/lift-fiber/concrete-mask alignment.

#### Project Owner / Evaluator Turn

> .Give me an extremely detailed diagnosis of why this is occuring: "The non-empty contraction schemas expose a mismatch in the tower action-realization interface. The tabular/explore machinery can choose a tower-side action index, but for non-empty schemas that index is not being mapped into a valid concrete counterpoint action. Because no concrete action executes, no environment transition happens, no reward can be earned, and no training event can occur." Dig into `state_collapser` repository if necessary, but don't change anything in `state_collapser`. Don't try to fix anything in either repo yet. Just report back here.

#### Embedded Engineering Consultant / Codex Turn

> I read the BBB tower-control path, the recorded artifact rows, and the
> relevant `state_collapser` tower/control code read-only. I did not change
> either repo.
>
> The short diagnosis is sharper than my earlier wording: the non-empty tower
> arms are not choosing a valid abstract action that later fails to map to a
> concrete action. They are reaching a coarsened active tier with no outgoing
> action vocabulary at all. BBB's tower learner then returns the sentinel action
> `-1`, and the BBB lift/resolve executor records that sentinel as
> `invalid_action_index`. So `invalid_action_index` is the artifact label, but
> the underlying condition is closer to:
>
> ```text
> active tier has no available outgoing action cells
> -> learner returns -1
> -> executor rejects -1 before any lift candidate is attempted
> -> no concrete environment step
> -> no reward
> -> no learner update
> ```
>
> The artifact evidence is very direct. In representative non-empty tower
> `lift_fiber_events.csv` files, every failure row has `abstract_action=-1`,
> blank `realized_action`, `candidate_count=0`, `success=False`, and
> `failure_reason=invalid_action_index`. That means the failure occurs before
> the executor has selected an `ActionCellId` or inspected real lift
> candidates. By contrast, the empty-schema tower's successful rows have real
> `ActionCellId(...)` abstract actions, concrete realized action tuples such as
> `(0, 0, 1)`, `candidate_count=1`, and `success=True`.
>
> The controller trace explains why only the non-empty towers reach this bad
> state. `state_collapser`'s first-release active-tier controller chooses the
> lowest/highest-indexed unclosed tier. At the start of an episode, every tier
> looks unclosed because it has no visits yet. For a non-empty tower with
> several tiers, the controller immediately descends: random balanced goes
> `0 -> 1 -> 2 -> 3 -> 4`, random unbalanced goes `0 -> 1 -> 2`, structured
> motion goes `0 -> 1 -> 2 -> 3 -> 4`, and bad/adversarial goes `0 -> 1`.
> Once it reaches that deepest tier, it repeatedly chooses `explore`. Empty
> schema has only tier `0`, so there is nowhere to descend; it explores and
> executes at the concrete tier instead.
>
> The BBB learner then asks the tower for the action vocabulary at the active
> tier and active tier state. The relevant BBB code path is:
>
> ```text
> CounterpointTierLearner._action_vocabulary
> -> tower.outgoing_action_cells(tier, state)
>
> CounterpointTierLearner._action_input
> -> action_mask = index < len(vocabulary)
>
> CounterpointTierLearner.behavior_action
> -> if the mask is empty/all-false, return -1
> ```
>
> The executor path then does:
>
> ```text
> CounterpointLiftResolveExecutor._execute
> -> if action is not an int or action < 0:
>      failure_reason = invalid_action_index
> ```
>
> That is exactly what the artifacts show: all non-empty failures have
> `abstract_action=-1`.
>
> The next layer down is why `outgoing_action_cells(...)` is empty at those
> coarsened tiers. In `state_collapser`, a `PartitionTower` builds state cells
> and action cells over a registered base graph. Action cells are live outgoing
> decision edges from a state cell. When state cells are merged by a contraction
> schema, the action layer removes edges whose source and target now lie inside
> the same merged state cell. Those become internal edges under the default
> `LoopPolicy.drop_internal`.
>
> That behavior is reasonable as a quotient/tower representation rule: if an
> edge stays inside the same coarsened state cell, it is no longer an outgoing
> quotient action. But it is poisonous for our current online controller if the
> active tier has collapsed so far that all concrete environment edges have
> become internal. At that point the tier may represent a huge amount of
> structure, but it exposes no outgoing decision actions to the learner.
>
> I verified this with a read-only probe of the small counterpoint fixture. For
> the empty schema, the tower has depth `1`; the sampled current tier-0 state is
> a singleton with `11` outgoing action cells and `0` internal edges. For random
> balanced, the tower has state-cell counts `[108, 3, 1, 1, 1]`; by tier `2`
> and below, the current state cell contains all `108` base states, has
> `1140` internal edges, and has `0` outgoing action cells. For random
> unbalanced, structured motion, and bad/adversarial, the collapse happens even
> earlier: the active coarse cell contains all `108` base states, all `1140`
> edges are internal, and there are `0` outgoing action cells.
>
> That matches the artifact active tiers exactly:
>
> - random balanced failures occur at active tier `4`;
> - random unbalanced failures occur at active tier `2`;
> - structured motion failures occur at active tier `4`;
> - bad/adversarial failures occur at active tier `1`;
> - every one of those failure rows has `abstract_action=-1`.
>
> The schema construction explains why the collapse is so aggressive. The
> `state_collapser` partition schema assigns base edges to contraction blocks.
> Contracting an edge merges its source and target state cells. The small
> counterpoint graph is connected enough that contracting enough of its edges
> very quickly creates one giant state cell. Random schemas eventually schedule
> enough connecting edges to collapse the graph. The bad/adversarial schema is
> supposed to do that. The structured-motion schema is more troubling: the BBB
> adapter currently builds it with a dimension list that includes the universal
> edge label `counterpoint_transition`. Because every counterpoint edge has that
> label, the first structured-motion block effectively schedules every edge and
> collapses the graph immediately, making it behave like an overcompression
> schema rather than a useful motion-preserving schema.
>
> So I would not describe the core issue as missing rewards, missing model, or
> ordinary poor exploration. Rewards exist. The direct and empty-schema arms
> prove that concrete stepping and reward accumulation work. The tabular learner
> machinery also exists. The failure is specifically at the interface between:
>
> - an active-tier controller that eagerly descends to the deepest unclosed
>   tier;
> - non-empty contraction schemas that collapse the current tier into a giant
>   cell;
> - `state_collapser` action-layer semantics that drop internal edges from the
>   outgoing decision surface;
> - BBB learner glue that treats an empty tier action vocabulary as "return
>   `-1`";
> - BBB lift/resolve glue that logs `-1` as `invalid_action_index`.
>
> The current result is therefore a real design/adapter failure, not a
> scientific negative result about tower learning. Before we can evaluate
> whether `structured motion` is a good schema, we need the online control
> surface to handle coarsened tiers that have no outgoing action cells. Possible
> future directions include: preventing descent into zero-action tiers, lifting
> through refinement fibers to a finer tier with executable actions, exposing
> internal-loop decisions intentionally, changing schema construction so useful
> structured tiers do not immediately collapse the whole graph, or improving the
> failure taxonomy from `invalid_action_index` to something like
> `no_available_tier_action`. But those are design choices for the next step;
> the diagnosis here is that non-empty towers are failing before action
> realization reaches a concrete counterpoint edge.


#### Project Owner / Evaluator Turn

> Ok well let me first say this "problem" is dumb as fuck. The solution is literally "if you find your self in the degenerate case, hop up one tier." Riiiiieeeeeght??? *Jiiiiiiiiii......* Do you see that?

#### Embedded Engineering Consultant / Codex Turn

> Yes. I see it. That is the simple control-law correction hiding under the
> stupid-looking failure.
>
> More precisely: if the active tier is degenerate for action selection, meaning
> the current tier-state has zero outgoing action cells, then that tier is not a
> valid execution locus. The controller should not ask the learner to choose an
> action there. It should immediately move to a finer tier where executable
> outgoing action cells exist.
>
> In `state_collapser` naming, that is "lift" / move upstairs, because tier `0`
> is the concrete/base tier and larger tier numbers are more collapsed. So in
> the observed failure:
>
> ```text
> active tier 4 has 0 outgoing actions
> -> do not explore at tier 4
> -> lift to tier 3
> -> if tier 3 also has 0 outgoing actions, lift again
> -> continue until nearest tier with outgoing actions
> -> choose/execute there
> ```
>
> The important tiny wrinkle is that "hop up one tier" may need to be a loop,
> not exactly one hop. In the probe I ran:
>
> - random balanced had no outgoing actions at tiers `2`, `3`, and `4`, but did
>   have outgoing actions at tier `1`;
> - random unbalanced had no outgoing actions at tiers `1` and `2`, so it would
>   need to lift all the way to tier `0`;
> - structured motion had no outgoing actions at tiers `1` through `4`, so it
>   would also need to lift all the way to tier `0`;
> - bad/adversarial had no outgoing actions at tier `1`, so it would need tier
>   `0`.
>
> So the actual rule is:
>
> ```text
> before explore/exploit_execute:
>   if current tier has no outgoing action cells:
>     lift until a finer executable tier is found
>     if none exists, then and only then record a real no-action failure
> ```
>
> That would turn the current dumb failure into normal tower-control behavior:
> coarse tiers can still be useful addresses or diagnostic compression levels,
> but they are not automatically executable decision surfaces. If a coarse cell
> has swallowed all outgoing edges into internal loops, execution must happen at
> a finer refinement where concrete outgoing edges reappear.
>
> This also changes the interpretation of the non-empty schema result. The
> current result is not "non-empty schemas cannot support learning." It is
> "the first controller treated a non-executable coarse tier as if it were an
> executable action tier." The immediate design fix is not a stronger learner,
> not reward shaping, and not necessarily new schema math. It is to teach the
> controller/adapter that zero-action active tiers are pass-through or
> lift-through tiers, not places where the learner should be forced to emit
> `-1`.
>
> And yes, this is exactly the kind of failure that feels irritating because the
> artifacts make it look like a big mysterious tower-learning collapse, while
> the actual operational rule is basically: "you walked down into a room with no
> doors; go back up until there is a door."


#### Project Owner / Evaluator Turn

> I think the next important question is: *Does this fix to contoroller logic go in `state_collapser`, or is it local to `big_boy_benchmarking` or even to this specific evaluation? I strongly suspect `state_collapser`, but this does also seem a learner issue, so maybe not.

#### Embedded Engineering Consultant / Codex Turn

> I agree with your suspicion, with one important split:
>
> ```text
> The control invariant belongs in state_collapser.
> The environment-specific action realization remains in BBB.
> The evaluation should not own the fix.
> ```
>
> The reason I think the invariant belongs in `state_collapser` is that the
> failure is not counterpoint-specific. Any partition tower can create a
> coarsened tier where the active state cell has zero outgoing action cells,
> especially when internal edges are dropped from the decision surface. That is
> a generic tower-control condition. The generic active-tier runtime should know
> that a zero-action tier is not executable and should route control to a finer
> executable tier before asking a learner for an action.
>
> The learner should not be responsible for deciding that. A learner can answer:
>
> ```text
> Given this action vocabulary/mask, which action should I choose?
> ```
>
> But it should not have to answer:
>
> ```text
> Is this tower tier a valid execution locus, or should active control lift to
> another tier first?
> ```
>
> That second question is controller/runtime topology, not learning. In the
> current BBB binding, the learner receives an empty/all-false action mask and
> returns `-1`. That is a local symptom of a missing upstream contract. A better
> upstream contract would prevent the learner from being called at an
> action-empty tier in the first place, or would give it a typed "no action
> available" result that the runtime routes into lift/refine behavior rather
> than into executor failure.
>
> What belongs in `state_collapser`, in my view:
>
> - a first-class notion of tier action availability;
> - a controller/runtime rule that `explore` and `exploit_execute` require a
>   nonempty action vocabulary;
> - a default fallback such as "lift to the nearest finer executable tier";
> - typed failure/status vocabulary for `no_available_tier_action`, distinct
>   from invalid concrete action indices;
> - tests showing that a coarse tier with no outgoing actions does not call the
>   learner for an executable action.
>
> What remains local to BBB:
>
> - how a counterpoint `ActionCellId` becomes a concrete `CounterpointAction`;
> - legality-mask checks against `counterpoint_legal_action_mask_v001`;
> - counterpoint-specific diagnostics and artifact rows;
> - any temporary guard we add while waiting for upstream semantics.
>
> A BBB stopgap could absolutely implement the hop-up rule locally in
> `CounterpointTowerControlAdapter` or the BBB tower-control wrapper. That would
> let this benchmark continue. But if we only fix it locally, we risk teaching
> BBB a rule that every future `state_collapser` tower environment will also
> need. That is usually the sign that the rule belongs upstream.
>
> I would not put the fix in this specific evaluation. The evaluation can record
> the failure, prove the mechanism, and later verify the correction. But the
> evaluation should not encode the controller semantics. It should remain a
> consumer of the environment and tower-control machinery.
>
> So my recommended ownership is:
>
> ```text
> state_collapser:
>   define and test the generic active-tier executable-locus rule
>
> big_boy_benchmarking:
>   adapt counterpoint action realization to that rule
>   optionally carry a temporary local guard if upstream is not ready
>
> this evaluation:
>   preserve the current failure as evidence
>   rerun after the rule exists
>   compare before/after behavior
> ```
>
> In short: yes, the durable fix smells upstream. The learner is involved only
> because the current runtime asks it a question it should never have been asked
> at that tier.

