# Engineer Continuity Report
## 01_011_young_tableaux_runtime_review_release_and_synthetic_blow_revisions

## Date

2026-05-24

This report is filed under 2026-05-24 because the work it covers was completed
on that date, even though the continuity write-up was requested afterward.

## Interval covered

This report covers the work completed after the prior continuity report:

- [01_010_package_readiness_and_loghrl_research_document_consolidation.md]([state_collapser repository root]/docs/engineer_continuity/2026/05/23/01_010_package_readiness_and_loghrl_research_document_consolidation.md)

The prior report ended with a first complete `logHRL.tex` draft and a much
clearer mathematical account of the quotient tower as a nested state/action
partition-table construction.

This interval begins immediately after that paper-consolidation milestone and
continues through:

- a final `paths.png` paper asset repair
- the first code review comparing the new `logHRL.tex` partition-table model
  against the existing `/src` implementation
- the Project Owner's discussion and corrections on what kind of equivalence
  mattered between paper and code
- the Young-tableaux / nested-partition runtime refactor blueprint
- the Phase.Stage.Action implementation gameplan for that runtime refactor
- implementation of the partition-backed runtime refactor
- a post-refactor audit of all evaluation environments
- an evaluation-environment repair blueprint and gameplan
- implementation of schema-driven nontrivial towers across the evaluation
  environments
- the `v0.5.0` version bump and CI typing repair
- creation of a synthetic Jonathan-Blow-style review kit
- a full synthetic Blow code review of the whole repository
- multiple rounds of Project Owner comments and assistant replies inside that
  review
- a blueprint and gameplan for implementing the review's accepted revisions
- implementation of those revisions
- and a small outreach brief for an auxiliary GPT model to research possible
  outreach contacts

The visible git range after the prior continuity report is:

```text
2b725fa..51f5bed
```

At the end of the interval, `main` and `origin/main` point at:

```text
51f5bed synthetic blow revision implemented
```

## Source reconstruction note

This report is reconstructed from:

- current git history
- the previous continuity report
- the current repository state
- implementation logs in `docs/design/Young_tableaux_refactor/`
- implementation logs in `docs/design/test_design/post_young_audit/`
- implementation logs in `docs/design/synthetic_blow_revisions_01/`
- the code review documents in `docs/code_review/`
- the current `README.md` and `CONTRIBUTING.md`
- the current source and test tree
- and the live conversation context around the branch merges and release work

As before, the high-level authorship/ownership line is clear:

- the Project Owner supplied the mathematical intent, the architectural
  corrections, the implementation priorities, the review lens, the release
  judgment, and the accept/reject decisions
- Codex supplied code review, synthesis, blueprinting, implementation planning,
  code edits, tests, docs, local validation, and continuity reconstruction

## Executive status

At the beginning of this interval, the repository had:

- a serious `logHRL.tex` research draft
- a paper-level algorithm describing quotient towers in terms of nested
  state/action partition tables
- a working but older runtime implementation that did not literally implement
  the paper's RAM data structure
- several evaluation environments
- a v0.4.0 release
- and an emerging training-surface layer

At the end of this interval, the repository has:

- a partition-backed tower runtime under `src/state_collapser/tower/partition/`
- explicit stable ids for states, edges, actions, schema blocks, state cells,
  action collections, and action cells
- a base-graph registry backing the partition tower
- first-class state and action partition layers
- explicit contraction schemas driving tower construction
- runtime integration through `TowerRuntime`
- compatibility readouts back into old `QuotientTierView` surfaces
- schema-driven nontrivial towers across all six evaluation environments
- explicit flat-baseline support through `NoContractionSchema` and
  `--schema-mode none`
- version `0.5.0`
- a synthetic Blow full-repository review and accepted revision plan
- first-class action-mask handling in training
- explicit continuation/bootstrap semantics in training transitions
- shared reference training helpers for ordinary example training loops
- a split between live runtime views and serializable value snapshots
- lazy compatibility quotient readouts
- optional morphism construction
- loop-policy carry-forward fixes
- internal/preimage edge aggregation surface
- a real hook-based Gymnasium wrapper surface
- a runtime benchmark smoke surface
- updated README and CONTRIBUTING guidance
- and a much larger test suite, with final validation passing

The project remains pre-alpha/research-mode, but the runtime and training
surfaces are significantly more serious than they were at the prior continuity
point.

The center of gravity shifted:

- from "the paper now says what the runtime ought to be"

to:

- "the runtime now substantially follows the paper's nested partition-table
  architecture, and the training/runtime boundaries have been hardened enough
  that larger evaluation work can begin"

## Commit-range summary

The visible git range after the last continuity report contains this sequence:

- `9bbb733` - `paths.png` fix
- `4bf8305` - mid code review
- `e061c71` - first code review complete, begin prep for redesign/refactor
- `7f342f8` - Young tableaux refactor blueprint and gameplan
- `97c475d` - implementation of `01_002_young_tableaux_runtime_refactor_implementation_gameplan.md`
- `17b8fad` - environment test fix planning
- `4fd0074` - repair post-young evaluation environment schemas
- `fea2ce5` - prepare `v0.5.0` release and fix CI typing
- `529e462` - synthetic Blow revision blueprint and gameplan
- `51f5bed` - synthetic Blow revision implemented

The aggregate repository diff for this interval is large:

```text
123 files changed, 26465 insertions(+), 560 deletions(-)
```

That large insertion count is mostly documentation, design records, code review
reports, implementation logs, new tests, and the new partition runtime package.

## Highest-level narrative

This interval had six major movements.

## 1. The paper/code mismatch was turned into an explicit code review

The Project Owner began this interval by changing gears from paper work to code
review. The specific concern was that `logHRL.tex` had changed substantially:
the construction in the paper now describes the tower "in RAM" as nested
state/action partition data, Young-diagram-like tables, outgoing-action
pointers, base-edge contraction schedules, and incremental maintenance.

The Project Owner asked for a detailed assessment of whether `/src` actually
matched that model, explicitly noting that some answers might be
"homotopically equivalent" or "computationally equivalent" rather than
literal.

Codex produced:

- [01_001_loghrl_partition_tower_vs_src_review.md]([state_collapser repository root]/docs/code_review/01_001_loghrl_partition_tower_vs_src_review.md)

The review conclusion was:

- the old source was not a literal implementation of the new `logHRL.tex`
  partition-table/Young-diagram construction
- it was computationally adjacent on the state-quotient side
- it did build quotient tier views and remove projected loops
- but it did not own the explicit ordered base-edge partition schedule
- it did not maintain nested action partition tables
- it did not treat state-cell-to-action-cell outgoing pointers as first-class
  runtime data
- and it still rebuilt quotient views in a way that was not the desired
  amortized local-maintenance architecture

The Project Owner then added discussion at the bottom of the review. The most
important Project Owner correction was that "computationally equivalent" was
not enough if the runtime model still paid the wrong costs. The accepted target
became:

```text
It changes the runtime model from repeated global reconstruction to amortized
local maintenance. If implemented well, it is plausibly the difference between
"research scaffold that works on small examples" and "runtime architecture that
can scale to serious evaluation."
```

That sentence became the organizing goal for the next implementation arc.

### PO attribution

The Project Owner supplied:

- the review target
- the insistence that the paper's "in RAM" model mattered
- the homotopic/computational-equivalence framing
- the concern that the old runtime might be acceptable as a quotient picture
  but unacceptable as a runtime architecture
- and the decisive standard that the refactor needed to support amortized local
  maintenance

Codex supplied:

- the code inspection
- the detailed mismatch report
- the issue ordering
- the first technical bridge from review findings to implementation blueprint

## 2. The Young-tableaux runtime refactor was designed and implemented

After the code review discussion, Codex created:

- [01_001_young_tableaux_runtime_refactor_blueprint.md]([state_collapser repository root]/docs/design/Young_tableaux_refactor/01_001_young_tableaux_runtime_refactor_blueprint.md)
- [01_002_young_tableaux_runtime_refactor_implementation_gameplan.md]([state_collapser repository root]/docs/design/Young_tableaux_refactor/01_002_young_tableaux_runtime_refactor_implementation_gameplan.md)
- [01_003_young_tableaux_runtime_refactor_implementation_log.md]([state_collapser repository root]/docs/design/Young_tableaux_refactor/01_003_young_tableaux_runtime_refactor_implementation_log.md)

The Project Owner then instructed Codex to create a branch and implement the
gameplan according to `prime_directive`.

The branch was:

```text
codex/young-tableaux-runtime-refactor
```

The implementation introduced the new partition runtime package:

- `src/state_collapser/tower/partition/ids.py`
- `src/state_collapser/tower/partition/base_registry.py`
- `src/state_collapser/tower/partition/schema.py`
- `src/state_collapser/tower/partition/state_layer.py`
- `src/state_collapser/tower/partition/action_layer.py`
- `src/state_collapser/tower/partition/loop_policy.py`
- `src/state_collapser/tower/partition/reward_aggregation.py`
- `src/state_collapser/tower/partition/update.py`
- `src/state_collapser/tower/partition/tower.py`
- `src/state_collapser/tower/partition/readout.py`
- `src/state_collapser/tower/partition/diagnostics.py`

The key technical changes were:

- stable typed ids for all partition-tower entities
- `BaseGraphRegistry` as the authoritative store for base states, edges,
  action identities, endpoints, labels, and outgoing-edge indices
- `ContractionSchema` / `NoContractionSchema` / `DimensionwiseSchema` as the
  first serious contraction-schedule surface
- `StatePartitionLayer` as the state-cell table
- `ActionPartitionLayer` as the outgoing-action collection/cell table
- state-cell-to-action-collection pointers
- state/action merge records
- loop/internal-edge recording under a loop policy
- `PartitionTower` as the authoritative nested partition structure
- `build_partition_tower_full(...)` as a full-build reference path
- `to_quotient_tier_views(...)` as a compatibility readout back into the older
  quotient view API
- `TowerRuntime` integration so the runtime uses the partition tower rather
  than the older full-rebuild helper as its primary construction path

The associated tests created a substantial new suite:

- id allocation tests
- registry tests
- schema tests
- state-layer tests
- action-layer tests
- loop-policy tests
- reward aggregation tests
- tower initialization tests
- incremental update tests
- readout tests
- full/incremental equivalence tests
- query/lift tests

The refactor was merged back to `main`, and the Project Owner made/merged an
additional planning commit afterward.

### PO attribution

The Project Owner supplied:

- the underlying mathematical model: the original graph plus nested state and
  action Young-diagram-like partition structures
- the insistence that the data structure should not mutate graph representation
  wholesale
- the requirement that the tower become a runtime architecture, not just a
  quotient readout
- the requirement to branch before implementation
- and the final merge/commit flow decisions

Codex supplied:

- the detailed blueprint and Phase.Stage.Action gameplan
- the partition package implementation
- compatibility readout design
- runtime integration
- extensive tests
- and the implementation log

## 3. The evaluation environments were audited and repaired after the refactor

After the Young-tableaux runtime refactor, the Project Owner raised a new
concern: many evaluation environments had been added before the refactor, so
their tests and tower behavior might now be wrong or shallow.

Codex produced:

- [01_001_post_young_diagram_evaluation_environment_audit.md]([state_collapser repository root]/docs/design/test_design/post_young_audit/01_001_post_young_diagram_evaluation_environment_audit.md)
- [01_002_post_young_diagram_evaluation_environment_repair_blueprint.md]([state_collapser repository root]/docs/design/test_design/post_young_audit/01_002_post_young_diagram_evaluation_environment_repair_blueprint.md)
- [01_003_post_young_diagram_evaluation_environment_repair_implementation_gameplan.md]([state_collapser repository root]/docs/design/test_design/post_young_audit/01_003_post_young_diagram_evaluation_environment_repair_implementation_gameplan.md)
- [01_004_post_young_diagram_evaluation_environment_repair_implementation_log.md]([state_collapser repository root]/docs/design/test_design/post_young_audit/01_004_post_young_diagram_evaluation_environment_repair_implementation_log.md)

The audit found that the examples were API/test healthy but mostly
tower-flat:

```text
plate_support_env                    max_depth: 2
articulated_loop_env                 max_depth: 1
dual_arm_manipulation_env            max_depth: 1
cable_parallel_env                   max_depth: 1
parallelogram_singularity_env        max_depth: 1
rl_counterpoint_v3                   max_depth: 1
```

The repair branch was:

```text
codex/post-young-eval-env-schema-repair
```

The repair added or updated:

- shared schema assertion helpers
- schema assignment checks in runtime integration tests
- deterministic environment-local action sequences
- `tower_depth_probe` schema-mode support
- default schema wiring in all target evaluation environments
- explicit `NoContractionSchema` flat baselines
- training pass-through of runtime schema configuration
- README language distinguishing `ContractionSchema` from legacy
  `ContractionPolicy`

After repair, the default probe showed nontrivial towers across all target
environments:

```text
plate_support_env                    max_depth: 2 scheduled_assignments: 84  unscheduled_assignments: 0
articulated_loop_env                 max_depth: 2 scheduled_assignments: 117 unscheduled_assignments: 0
dual_arm_manipulation_env            max_depth: 2 scheduled_assignments: 121 unscheduled_assignments: 0
cable_parallel_env                   max_depth: 2 scheduled_assignments: 88  unscheduled_assignments: 0
parallelogram_singularity_env        max_depth: 2 scheduled_assignments: 35  unscheduled_assignments: 0
rl_counterpoint_v3                   max_depth: 2 scheduled_assignments: 248 unscheduled_assignments: 0
```

The explicit flat baseline remained available:

```text
plate_support_env                    max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 84
articulated_loop_env                 max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 117
dual_arm_manipulation_env            max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 121
cable_parallel_env                   max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 88
parallelogram_singularity_env        max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 35
rl_counterpoint_v3                   max_depth: 1 scheduled_assignments: 0 unscheduled_assignments: 248
```

Validation at the end of that branch:

```text
uv run pytest tests/examples
169 passed in 1.14s

uv run pytest
354 passed in 1.43s

uv run ruff check .
All checks passed!
```

### PO attribution

The Project Owner supplied:

- the concern that evaluation environments might be invalid after the
  Young-diagram refactor
- the request for audit-first, blueprint-second, gameplan-third process
- the instruction to implement only after the plan was ready
- and the merge-flow direction

Codex supplied:

- the audit
- the repair design
- the schema and probe changes
- the tests proving nontrivial tower behavior
- the flat-baseline controls
- and the implementation log

## 4. The project was prepared as release `v0.5.0` and CI typing was fixed

After the post-Young evaluation-environment repair, the Project Owner wanted to
make the work a new release:

```text
v0.5.0
```

CI was failing on GitHub, and Codex investigated and repaired the local issue
that corresponded to CI failure. The release-prep commit was:

```text
fea2ce5 prepare v0.5.0 release and fix CI typing
```

Files changed in that commit:

- `pyproject.toml`
- `src/state_collapser/_version.py`
- `src/state_collapser/tower/partition/base_registry.py`
- `src/state_collapser/tower/partition/reward_aggregation.py`
- `src/state_collapser/tower/partition/tower.py`
- `uv.lock`

The version is now:

```text
0.5.0
```

as recorded in:

- `pyproject.toml`
- `src/state_collapser/_version.py`

The user also requested release title and release notes for this release.

### PO attribution

The Project Owner supplied:

- the release judgment
- the version number
- the concern about GitHub CI failure
- and the request for release-facing language

Codex supplied:

- the CI diagnosis
- the typing fixes
- the version bump
- and the release title/notes draft

## 5. A synthetic Blow review process was created and run

The Project Owner then requested a full code review through a synthetic
Jonathan-Blow-inspired lens. This started with a review kit:

- [synthetic_blow_review_kit/README.md]([state_collapser repository root]/docs/code_review/synthetic_blow_review_kit/README.md)
- [synthetic_blow_review_kit/source_notes.md]([state_collapser repository root]/docs/code_review/synthetic_blow_review_kit/source_notes.md)
- [synthetic_blow_review_kit/synthetic_blow.md]([state_collapser repository root]/docs/code_review/synthetic_blow_review_kit/synthetic_blow.md)

Codex then produced:

- [02_001_synthetic_blow_full_repo_review.md]([state_collapser repository root]/docs/code_review/02_001_synthetic_blow_full_repo_review.md)

The review's high-level verdict was:

- the repository is much more real than a typical research scaffold
- it has typed surfaces, a serious test suite, partition-backed tower runtime,
  and multiple running examples
- but it was not yet trustworthy as an RL training package
- the tower machinery was ahead of the training machinery
- the highest-risk issues were silent RL correctness and runtime-scaling
  issues, not style issues

The top issues included:

- termination/truncation/bootstrap semantics were wrong or inconsistent
- action masks existed but were not first-class in the learner target path
- the partition runtime still paid global readout costs on every update
- `RuntimeSnapshot` claimed serializability while carrying live mutable objects
- loop-policy alternatives were partly nominal, and carry-forward hard-coded the
  default
- several Gymnasium environments coerced actions instead of validating them
- the old `GymnasiumAdapter` name overclaimed what the object actually did
- the code did not yet have serious benchmark/performance regression surfaces

The Project Owner then added multiple rounds of comments and blank answer slots
inside the review document. The most important PO positions were:

- continuation/bootstrapping should be understood through lift logic, not only
  flat Gymnasium episode booleans
- masks are part of the actual constrained decision surface
- lazy runtime behavior matters because the whole point of the partition
  refactor is avoiding global reconstruction costs
- live views and serializable snapshots must be separated
- loop handling should include aggregation over preimage/internal loops,
  including choices such as `avg` and `max`
- the Gymnasium bridge needs to be understood as a three-world boundary:
  external env world, state-collapser structural world, and training/model
  world
- the hook names for Gymnasium integration are not standard Gymnasium API, but
  a competent RL engineer who built the Gymnasium problem should be able to
  supply the required semantic hooks
- the report should also include a synthetic Blow-style critique of Python as
  the implementation language, while making clear that the Project Owner asked
  for that extra assessment and does not intend to rewrite the package now

### PO attribution

The Project Owner supplied:

- the synthetic Blow review lens
- the insistence that the review be hard, performance-aware, and whole-repo
- the continuation/lift correction
- the mask-as-decision-surface framing
- the three-world Gymnasium framing
- the loop aggregation insight, especially `max` vs average
- the language-choice concern
- and all accept/reject guidance in the review conversation

Codex supplied:

- the review kit
- the full review
- the higher-level explanations under PO prompts
- the synthesized responses to PO follow-ups
- and the final assessment that enough decisions existed to write a revision
  blueprint

## 6. The accepted synthetic Blow revisions were designed and implemented

After the review conversation stabilized, Codex created:

- [01_001_synthetic_blow_review_revision_blueprint.md]([state_collapser repository root]/docs/design/synthetic_blow_revisions_01/01_001_synthetic_blow_review_revision_blueprint.md)
- [01_002_synthetic_blow_review_revision_implementation_gameplan.md]([state_collapser repository root]/docs/design/synthetic_blow_revisions_01/01_002_synthetic_blow_review_revision_implementation_gameplan.md)
- [01_003_synthetic_blow_review_revision_implementation_log.md]([state_collapser repository root]/docs/design/synthetic_blow_revisions_01/01_003_synthetic_blow_review_revision_implementation_log.md)

The implementation branch was:

```text
codex/synthetic-blow-revisions-01
```

The final implementation commit was:

```text
51f5bed synthetic blow revision implemented
```

The implementation covered ten practical areas.

### 6.1 Strict action boundaries in example environments

The package now rejects invalid raw actions before coercion across the example
Gymnasium environments.

The boundary rule is:

- reject invalid action-space values before converting to `int`
- reject `bool`
- preserve normal integer and NumPy integer scalar compatibility

New tests include:

- `tests/examples/test_env_action_boundaries.py`

### 6.2 First-class action masks

New module:

- `src/state_collapser/training/masks.py`

New helpers include:

- `mask_from_info(...)`
- `legal_actions(...)`
- `action_is_legal(...)`

`StepCollector` now:

- extracts `info["action_mask"]` by default
- preserves factory override behavior
- rejects masked-off selected actions before stepping the runtime
- attaches target masks from step-result info

`TabularQLearner` now:

- respects masks during action selection
- raises on all-false masks
- bootstraps only over legal target actions when a target mask is present

### 6.3 Explicit continuation/bootstrap semantics

New module:

- `src/state_collapser/training/continuation.py`

New concepts include:

- `BootstrapSemantics`
- `default_bootstrap_allowed(...)`
- `default_bootstrap_reason(...)`

`TrainingTransition` now carries:

- `bootstrap_allowed`
- `bootstrap_input`
- `bootstrap_reason`

This implements the Project Owner's correction that the target decision surface
should not be inferred blindly from raw `terminated`/`truncated` booleans.

### 6.4 Shared ordinary training loops

New module:

- `src/state_collapser/examples/_shared_training.py`

The ordinary example training loops now delegate to this helper instead of
copying local Q-target formulas.

The intentionally experimental exploit/explore path in `plate_support_env`
remains isolated and intentionally unmigrated.

### 6.5 Live runtime view vs value snapshot split

`src/state_collapser/tower/snapshot.py` now distinguishes:

- `LiveRuntimeView`: live graph/tower handoff object
- `RuntimeSnapshot`: value-style snapshot object with no live graph/tower
  references

`TowerRuntime.reset(...)` and `TowerRuntime.step(...)` now return live views,
and the live view exposes `to_snapshot()` when a stable value snapshot is
needed.

This directly fixes the old "snapshot as live camera feed" problem.

### 6.6 Lazy compatibility readouts and optional morphisms

The default runtime path no longer eagerly rebuilds old-style quotient-tier
readouts after each partition update.

Instead:

- `TowerRuntime.compatibility_quotient_tiers()` explicitly requests the
  compatibility readout
- the legacy `quotient_tiers` property delegates to that explicit path
- `PartitionTower.update_with_delta(..., build_morphism=False)` avoids full
  morphism-domain capture by default
- explicit `build_morphism=True` preserves old behavior for callers that need it

This is one of the most important runtime-scaling corrections in the interval.

### 6.7 Loop-policy carry-forward and internal aggregation

`ActionPartitionLayer.carry_forward_from(...)` now accepts the configured
`loop_policy` instead of hard-coding `LoopPolicy.drop_internal()`.

New module:

- `src/state_collapser/tower/partition/internal_aggregation.py`

Supported internal/preimage aggregation modes include:

- `sum`
- `mean`
- `max`

This reflects the Project Owner's point that many RL problems want a downstairs
best-case signal rather than an average signal.

### 6.8 Hook-based Gymnasium wrapper

The old overclaiming adapter name was removed from the serious public role.

The toy/native object is now:

- `RobotConstraintRuntimeAdapter`

The serious bridge surface is:

- `StateCollapserGymHooks`
- `StateCollapserGymWrapper`

The wrapper:

- delegates to an existing Gymnasium-like env
- records realized transitions into an `ExploredGraph`
- supports opaque discovered-graph operation
- propagates hook-provided masks to `info["action_mask"]`
- records hook-provided edge labels
- exposes tower context through `info["state_collapser"]`

The hook object makes the semantic boundary explicit:

- `state_key`
- `action_key`
- optional `action_mask`
- optional `edge_labeler`

This implements the three-world design discussed in the review:

- Gymnasium environment world
- `state_collapser` graph/tower world
- training/model decision-input world

### 6.9 Benchmark smoke surface

New package:

- `src/state_collapser/benchmarks/`

New benchmark:

- `state_collapser.benchmarks.tower_runtime_bench`

The benchmark supports:

- default schema mode
- no-schema flat mode
- optional compatibility readout
- optional morphism construction
- summary-only CLI output

This is not yet serious benchmarking, but it establishes a performance
regression surface.

### 6.10 Documentation cleanup

`README.md` and `CONTRIBUTING.md` now mention:

- explicit masks
- continuation/bootstrap semantics
- live views vs value snapshots
- lazy readouts
- benchmarks
- hook-based Gymnasium integration
- observation-to-state inference as future work
- hot-path discipline

### Final validation for this implementation

The final validation recorded in the implementation log was:

```text
uv run ruff check .
All checks passed!

uv run mypy src
Success: no issues found in 85 source files

uv run pytest
437 passed in 2.01s
```

Benchmark smoke:

```text
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 10 --summary-only
tower_runtime_bench mode=default steps=10 elapsed_seconds=0.005364 operations_per_second=1864.15 readout_requested=False morphism_requested=False tower_depth=2 discovered_states=22 discovered_edges=60
```

### PO attribution

The Project Owner supplied:

- the instruction to implement the accepted review gameplan
- the strict branch/process expectations from `prime_directive`
- the accepted semantics for masks, continuation, lifts, Gymnasium hooks,
  loop aggregation, and runtime hot paths
- the release and merge decisions

Codex supplied:

- implementation
- tests
- docs
- local validation
- implementation log
- merge instructions

## Outreach helper

During the interval, the Project Owner also requested a Markdown brief for an
auxiliary GPT model that would do hardcore internet research to build a targeted
outreach Rolodex.

Codex initially created the brief on the Desktop as a working handoff artifact.
The Project Owner then moved the document into the repository, and it now lives
at:

```text
docs/outreach/state_collapser_outreach_rolodex_brief.md
```

That document explains:

- what `state_collapser` is
- what kinds of researchers or engineers might be interested
- what not to overclaim
- and target categories such as HRL researchers, MDP abstraction researchers,
  robotics/control people, graph ML/geometric deep learning researchers, and RL
  framework maintainers

This artifact is now tracked as repository documentation rather than an
out-of-repo sidecar.

### PO attribution

The Project Owner supplied:

- the outreach goal
- the intended auxiliary-GPT use case
- the tone: personal targeted outreach, not mass marketing

Codex supplied:

- the outreach brief
- the target-person category structure
- and the honest project summary for outreach research

## Current package architecture after this interval

## Runtime/tower architecture

The tower runtime is now centered on:

- `TowerRuntime`
- `PartitionTower`
- `BaseGraphRegistry`
- `ContractionSchema`
- `StatePartitionLayer`
- `ActionPartitionLayer`
- `LiveRuntimeView`
- `RuntimeSnapshot`

The important architectural shift is:

- old model: rebuild quotient-tier views from visible graph data
- new model: maintain nested partition tables as runtime state, and read out
  quotient-tier views only when compatibility/debug consumers ask for them

The compatibility surface still exists because much of the package and tests
understand `QuotientTierView`, but it is no longer supposed to be the default
hot-path representation.

## Evaluation environment architecture

The six current evaluation environments are:

- `plate_support_env`
- `articulated_loop_env`
- `dual_arm_manipulation_env`
- `cable_parallel_env`
- `parallelogram_singularity_env`
- `rl_counterpoint_v3`

They now all have schema-driven nontrivial tower behavior under default probe
settings, plus a no-schema flat baseline.

`tower_depth_probe` now has enough schema/probe control to distinguish:

- a meaningful tower generated by environment labels/schema
- a flat Python/runtime baseline

## Training architecture

Training is still intentionally simple and research-mode, but it is much less
bug-prone than before.

Important surfaces now include:

- `ActionSelectionInput`
- `TrainingTransition`
- `StepCollector`
- `TabularQLearner`
- `BootstrapSemantics`
- mask helpers
- shared ordinary example training helper

The key conceptual improvement is that training transitions now carry
decision-surface information more explicitly:

- legal action masks
- bootstrap permission
- bootstrap input override
- bootstrap reason
- tower position key

This is not yet a neural/tensor training stack, but it is a better reference
surface for RL correctness.

## Gymnasium architecture

The package now distinguishes:

- package-native toy/runtime adapter surfaces
- real Gymnasium-like wrappers
- user-supplied semantic hooks

This is important because a Gymnasium observation is not automatically a stable
mathematical graph state. The new wrapper asks users to name that interpretation
explicitly rather than inferring it magically.

## Benchmark architecture

Benchmarking is not yet serious, but the first benchmark surface exists.

The benchmark can compare:

- schema mode vs flat mode
- readout-disabled vs readout-enabled paths
- morphism-disabled vs morphism-enabled paths

This is the beginning of the benchmarking work the Project Owner identified as
one of the remaining release-readiness pillars.

## Major documents created or changed

Important new or heavily updated documents:

- [01_001_loghrl_partition_tower_vs_src_review.md]([state_collapser repository root]/docs/code_review/01_001_loghrl_partition_tower_vs_src_review.md)
- [01_001_young_tableaux_runtime_refactor_blueprint.md]([state_collapser repository root]/docs/design/Young_tableaux_refactor/01_001_young_tableaux_runtime_refactor_blueprint.md)
- [01_002_young_tableaux_runtime_refactor_implementation_gameplan.md]([state_collapser repository root]/docs/design/Young_tableaux_refactor/01_002_young_tableaux_runtime_refactor_implementation_gameplan.md)
- [01_003_young_tableaux_runtime_refactor_implementation_log.md]([state_collapser repository root]/docs/design/Young_tableaux_refactor/01_003_young_tableaux_runtime_refactor_implementation_log.md)
- [01_001_post_young_diagram_evaluation_environment_audit.md]([state_collapser repository root]/docs/design/test_design/post_young_audit/01_001_post_young_diagram_evaluation_environment_audit.md)
- [01_002_post_young_diagram_evaluation_environment_repair_blueprint.md]([state_collapser repository root]/docs/design/test_design/post_young_audit/01_002_post_young_diagram_evaluation_environment_repair_blueprint.md)
- [01_003_post_young_diagram_evaluation_environment_repair_implementation_gameplan.md]([state_collapser repository root]/docs/design/test_design/post_young_audit/01_003_post_young_diagram_evaluation_environment_repair_implementation_gameplan.md)
- [01_004_post_young_diagram_evaluation_environment_repair_implementation_log.md]([state_collapser repository root]/docs/design/test_design/post_young_audit/01_004_post_young_diagram_evaluation_environment_repair_implementation_log.md)
- [02_001_synthetic_blow_full_repo_review.md]([state_collapser repository root]/docs/code_review/02_001_synthetic_blow_full_repo_review.md)
- [01_001_synthetic_blow_review_revision_blueprint.md]([state_collapser repository root]/docs/design/synthetic_blow_revisions_01/01_001_synthetic_blow_review_revision_blueprint.md)
- [01_002_synthetic_blow_review_revision_implementation_gameplan.md]([state_collapser repository root]/docs/design/synthetic_blow_revisions_01/01_002_synthetic_blow_review_revision_implementation_gameplan.md)
- [01_003_synthetic_blow_review_revision_implementation_log.md]([state_collapser repository root]/docs/design/synthetic_blow_revisions_01/01_003_synthetic_blow_review_revision_implementation_log.md)

## Major source areas changed

Important source areas changed:

- `src/state_collapser/tower/partition/`
- `src/state_collapser/tower/runtime.py`
- `src/state_collapser/tower/snapshot.py`
- `src/state_collapser/training/`
- `src/state_collapser/adapters/gymnasium.py`
- `src/state_collapser/examples/*/runtime.py`
- `src/state_collapser/examples/*/training.py`
- `src/state_collapser/examples/*/env.py`
- `src/state_collapser/examples/tower_depth_probe.py`
- `src/state_collapser/benchmarks/`

Important test areas changed:

- `tests/tower/partition/`
- `tests/tower/`
- `tests/training/`
- `tests/examples/`
- `tests/adapters/`
- `tests/benchmarks/`
- `tests/integration/`

## Validation status at end of interval

The final full validation from the last implementation branch was:

```text
uv run ruff check .
All checks passed!

uv run mypy src
Success: no issues found in 85 source files

uv run pytest
437 passed in 2.01s
```

The current git state when this continuity report was started was clean on
`main` before adding this report:

```text
## main...origin/main
```

This continuity report itself is a new docs-only change.

## Known limitations and honest caveats

The repository is much stronger, but the following limitations remain.

## 1. This is still not a mature RL framework

There is no serious neural model training stack yet:

- no PyTorch model family
- no tensor/device abstraction
- no vectorized rollout system
- no replay buffer design beyond simple tabular/research surfaces
- no checkpoint/resume surface
- no experiment manifest/artifact contract

This is consistent with the current research-mode package posture, but should
not be confused with production RL infrastructure.

## 2. Benchmarking is still only a smoke surface

The benchmark package is a good start, but it is not yet the "serious
benchmarking" the Project Owner identified as one of the remaining release
needs.

Needed future benchmarking includes:

- larger discovered graphs
- readout-disabled vs readout-enabled scaling curves
- morphism-disabled vs morphism-enabled costs
- schema-mode comparisons
- environment-family comparisons
- regression thresholds
- artifact output

## 3. Compatibility readouts still exist and can be expensive

The hot path is now better, but old compatibility surfaces still exist. That is
intentional, but future engineers should be careful not to accidentally put
`to_quotient_tier_views()` back into default step/update paths.

## 4. Observation-to-state inference is explicitly unsolved

The Gymnasium wrapper is honest: it asks for semantic hooks.

It does not solve the harder problem of automatically discovering the correct
graph state from arbitrary observations. That remains future work.

## 5. Internal/preimage aggregation is only a first surface

The internal aggregation module supports `sum`, `mean`, and `max`, but the
broader theory of downstairs reward/value aggregation is still evolving.

The Project Owner's insight that `max` direct image may be better than `sum` or
average in many RL problems should remain active in future design.

## 6. The package is still written in Python

The synthetic Blow review raised the language concern explicitly: a
performance-critical graph/runtime system might eventually want compiled-core
pieces.

The Project Owner does not intend to rewrite the project in another language at
this stage. The current stance is:

- keep Python for research velocity
- keep hot-path discipline
- benchmark before optimizing
- isolate surfaces that could later move to a compiled backend if needed

## 7. `logHRL.tex` remains ahead of some package surfaces

The runtime is now much closer to the paper's data-structure story than before.
But the paper's full theorem-facing picture still extends beyond the package:

- lift semantics are not fully mature
- abstract action traversal is not fully mature
- serious policy/model training is not present
- path-volume/log-speedup claims still need careful benchmarking and paper
  cleanup

## Recommended next steps

If the next engineer/model picks up from here, the recommended orientation is:

1. Read the prior continuity report:
   [01_010_package_readiness_and_loghrl_research_document_consolidation.md]([state_collapser repository root]/docs/engineer_continuity/2026/05/23/01_010_package_readiness_and_loghrl_research_document_consolidation.md)

2. Read this report.

3. Read the implementation logs in this order:
   - [01_003_young_tableaux_runtime_refactor_implementation_log.md]([state_collapser repository root]/docs/design/Young_tableaux_refactor/01_003_young_tableaux_runtime_refactor_implementation_log.md)
   - [01_004_post_young_diagram_evaluation_environment_repair_implementation_log.md]([state_collapser repository root]/docs/design/test_design/post_young_audit/01_004_post_young_diagram_evaluation_environment_repair_implementation_log.md)
   - [01_003_synthetic_blow_review_revision_implementation_log.md]([state_collapser repository root]/docs/design/synthetic_blow_revisions_01/01_003_synthetic_blow_review_revision_implementation_log.md)

4. Read the synthetic Blow review:
   [02_001_synthetic_blow_full_repo_review.md]([state_collapser repository root]/docs/code_review/02_001_synthetic_blow_full_repo_review.md)

5. Run current validation before making non-doc changes:

```text
uv run ruff check .
uv run mypy src
uv run pytest
```

6. For runtime performance work, start with:

```text
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 1000 --summary-only
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 1000 --readout --summary-only
uv run python -m state_collapser.benchmarks.tower_runtime_bench --steps 1000 --morphism --summary-only
```

7. For environment behavior, compare default schema mode to flat mode:

```text
uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --summary-only
uv run python -m state_collapser.examples.tower_depth_probe --steps 20 --seed 7 --schema-mode none --summary-only
```

## Most important conceptual through-line

This interval converted a paper-level data-structure correction into actual
runtime architecture.

The Project Owner's mathematical picture was:

- keep the discovered base graph
- maintain nested state partitions
- maintain nested action/outgoing partitions
- let state cells point into action-side partition data
- update locally as exploration discovers new graph data
- read quotient views as projections/readouts, not as the authoritative runtime
  store

The code is now much closer to that picture.

The synthetic Blow review then forced the package to stop treating several
training/runtime issues as harmless research rough edges:

- masks are not decoration
- bootstrap semantics are not raw booleans
- snapshots are not live references
- hot paths should not rebuild global compatibility views
- Gymnasium integration needs honest semantic hooks
- loop/internal aggregation needs a real surface

That is the real accomplishment of the interval.

The package is still pre-alpha, but it has moved from "clever research scaffold"
toward "coherent research runtime with a plausible path to serious evaluation."
