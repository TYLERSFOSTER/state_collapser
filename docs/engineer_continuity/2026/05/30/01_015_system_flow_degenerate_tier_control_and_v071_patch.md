# Engineer Continuity Report
## 01_015_system_flow_degenerate_tier_control_and_v071_patch

## Date

2026-05-30

## Interval Covered

This report covers the `state_collapser` work completed after:

```text
docs/engineer_continuity/2026/05/30/01_014_v070_downstream_alignment_documentation_and_docstring_quality.md
```

The previous report ended after the `v0.7.0` tensorization/documentation
alignment, the docstring-quality pass, and the first HGraphML/downstream
compatibility documentation. This second May 30 report covers the subsequent
work:

- a full repo crawl producing Mermaid system-flow and control-flow diagrams;
- a downstream `big_boy_benchmarking` degenerate-tier failure diagnosis;
- the PO's simplification of that diagnosis into the core empty-`Out` rule;
- the design blueprint and Phase.Stage.Action implementation workplan for
  degenerate-tier control;
- the implementation of the degenerate-tier runtime fix;
- the handoff note for `big_boy_benchmarking`;
- the associated documentation and bibliography updates;
- the `v0.7.1` patch release preparation;
- and the PO-caught version/lockfile correction that prevented a likely CI
  mismatch.

At the time this report is written, the local repository is on:

```text
main
```

with recent visible history:

```text
0de2e23 (HEAD -> main, tag: v0.7.1, origin/main, origin/HEAD) Bump version to v0.7.1
d5affe0 (codex/degenerate-tier-control) degenerate tier control fix implementation
a6c6599 degenerate tier control logic diagnosis share from big_boy_benchmarking
d4e9d4f flowchart and control flow summaries of package operation
0fe0dd0 engineer continuity report
e62d8d0 doc strings across package scripts
```

The working tree was clean after the `v0.7.1` release/version check:

```text
## main...origin/main
```

## Executive Summary

This interval moved from documentation/architecture visibility into a concrete
runtime correction driven by downstream benchmarking.

The major new code behavior is:

```text
if an active tower tier is not executable because its current state-cell has
no outgoing action cells, the exploit/explore runtime lifts to a finer tier
until it reaches an executable tier.

Only if tier 0 is also non-executable does the runtime return a clean
NO_AVAILABLE_ACTION result.
```

This matters because `big_boy_benchmarking` exposed a failure path where the
controller could select a coarse tier that was structurally meaningful but
had no action surface at the current state. A learner then received an empty
action vocabulary, produced an invalid sentinel action, and the executor
reported `invalid_action_index` without making a concrete environment step.

The first attempted analysis around this failure risked becoming too heavy:
agents were drifting toward larger protocol machinery. The PO identified the
real core rule much more sharply:

```text
if Out is empty, hop up one tier; recurse.
```

That PO correction is the conceptual center of this interval. Codex then
grounded the rule in the repo, wrote the blueprint/workplan, implemented the
runtime/controller changes, and added focused tests. The result is deliberately
small: no new learner abstraction, no tensorization changes, no replay-buffer
changes, and no special counterpoint-only hack in `state_collapser`.

The second important release-management point is also PO-attributed. During
the `v0.7.1` patch release preparation, Codex initially supplied version-bump
commands that omitted `uv.lock`. The PO caught the likely CI risk:

```text
Did you fix the uv.lock correctly so CI will be green?
```

After checking the repo, `uv.lock` was confirmed to carry the local package
version change:

```diff
name = "state-collapser"
-version = "0.7.0"
+version = "0.7.1"
```

The final version metadata is aligned across:

```text
pyproject.toml
src/state_collapser/_version.py
CITATION.cff
CHANGELOG.md
uv.lock
```

That correction should be preserved in future release procedure notes: package
metadata changes require `uv.lock` to be refreshed and committed.

## Commit-Level Summary

### d4e9d4f

```text
flowchart and control flow summaries of package operation
```

Added:

```text
docs/design/system_flow/01_001_system_flowcharts_and_control_flow.md
```

This is a repo-crawl architecture/control-flow map with Mermaid diagrams. It
summarizes the package as:

```text
state_collapser is not an RL algorithm runner.
state_collapser is a structural runtime layer around a discovered transition graph.
```

It maps:

- public entry surfaces;
- examples;
- Gymnasium adapter;
- graph discovery;
- `TowerRuntime`;
- `PartitionTower`;
- live runtime snapshots;
- training surfaces;
- tensorization;
- optional Torch conversion;
- and downstream HGraphML-style graph-dataflow use.

The document exists because the PO asked for a detailed crawl through the repo
with Mermaid flowcharts and control-flow diagrams showing how the whole system
works. Codex performed the crawl and authored the map.

### a6c6599

```text
degenerate tier control logic diagnosis share from big_boy_benchmarking
```

Added:

```text
docs/design/degenerate_tier_control/error_diagnosis_conversation.md
```

This document was supplied from the `big_boy_benchmarking` side as a downstream
diagnosis conversation. It captured the symptom:

```text
active coarse tower tier has zero outgoing action cells
    -> learner receives no valid action surface
    -> learner returns an invalid sentinel
    -> executor reports invalid_action_index
    -> no concrete environment step occurs
```

The PO then pushed back on the heaviness of the diagnosis and reframed it as a
simple control invariant:

```text
If the active tier has empty Out, lift to a finer tier.
If tier 0 also has empty Out, the local problem is truly trivial/dead-ended.
```

That reframing drove the actual upstream fix.

### d5affe0

```text
degenerate tier control fix implementation
```

Changed 17 files, including:

```text
src/state_collapser/tower/control/controller.py
src/state_collapser/tower/control/signals.py
src/state_collapser/tower/runtime.py
src/state_collapser/examples/plate_support_env/runtime.py
tests/tower/control/test_controller.py
tests/tower/control/test_runtime_loop.py
tests/tower/control/test_signals.py
tests/tower/partition/test_degenerate_tier_queries.py
tests/examples/test_plate_support_env_exploit_explore_runtime.py
docs/design/degenerate_tier_control/01_001_degenerate_tier_control_blueprint.md
docs/design/degenerate_tier_control/01_002_degenerate_tier_control_implementation_workplan.md
docs/design/degenerate_tier_control/01_003_big_boy_benchmarking_handoff_note.md
docs/usage/01_002_tower_runtime_mental_model.md
docs/design/logHRL.bib
CHANGELOG.md
CONTRIBUTING.md
```

This commit implemented the degenerate-tier control invariant, added tests,
and documented the downstream handoff.

### 0de2e23

```text
Bump version to v0.7.1
```

Changed:

```text
CHANGELOG.md
CITATION.cff
pyproject.toml
src/state_collapser/_version.py
uv.lock
```

This is the `v0.7.1` patch release metadata commit. The key detail is that
`uv.lock` was included after the PO explicitly caught the risk of a stale
lockfile.

## Major Movement 1: System Flow Documentation

The PO asked for a detailed crawl through the repo and a document of Mermaid
flowcharts/control-flow diagrams explaining the whole system.

Codex created:

```text
docs/design/system_flow/01_001_system_flowcharts_and_control_flow.md
```

The document now gives future agents and engineers a compact mental model of
the package:

```text
environment / hidden graph
    -> explored graph and vista graph
    -> tower runtime
    -> partition tower
    -> snapshots and readouts
    -> training surfaces
    -> optional tensorization
    -> optional Torch boundary
```

The document is especially important because recent work added several
orthogonal surfaces:

- Young-diagram / partition-tower runtime;
- fiber-conditioned training;
- tensorization and optional Torch conversion;
- HGraphML compatibility;
- benchmark-facing metadata;
- and now degenerate-tier control.

Without a visual map, future work could easily confuse these layers. The map
explicitly says which parts own which responsibilities and, just as important,
which parts do not own which responsibilities.

The central design line preserved there is:

```text
state_collapser constructs and maintains structural decision geometry.
It does not own the entire RL algorithm stack.
```

## Major Movement 2: Downstream Degenerate-Tier Diagnosis

The next trigger came from outside the repo. The PO reported that the
`big_boy_benchmarking` team had placed a diagnosis document into this repo:

```text
docs/design/degenerate_tier_control/error_diagnosis_conversation.md
```

Codex read it and summarized the failure as an active-tier mismatch:

```text
The controller can route decision-making to a tier where the current state-cell
has no outgoing action cells.
```

In that state, the tower is not wrong and the graph need not be globally
broken. The issue is local executability:

```text
This tier is not currently a valid place to ask for an action.
```

The PO immediately simplified the fix:

```text
There's not something simpler like a check "is out empty" and if it is,
up a tier. That recurses and no problem emerges unless original graph is
trivial, in which case explore. If no explore, the whole problem is trivial.
```

This was the decisive architecture correction. Codex had been willing to drift
toward heavier machinery, but the PO correctly identified that the runtime
already had enough structure:

- `PartitionTower.outgoing_action_cells(tier, state_cell_id)` tells whether a
  tier-state has an action surface;
- the active-tier controller already knows how to lift/descend/train/explore;
- the runtime can preflight action selection;
- tier 0 is the base/fine fallback.

Therefore the fix should be a small executable-tier predicate, not a new
training system.

## Major Movement 3: Blueprint and Workplan

After the PO's correction, Codex re-evaluated the current repo concretely and
created:

```text
docs/design/degenerate_tier_control/01_001_degenerate_tier_control_blueprint.md
```

The blueprint's core rule is:

```text
if the current active tier has empty Out, move to a finer tier.
Repeat until Out is nonempty.
Only if tier 0 also has empty Out is the problem locally trivial/dead-ended.
```

The blueprint intentionally kept the implementation narrow. It explicitly
rejected:

- new learner protocols;
- tensorization changes;
- replay-buffer changes;
- special `big_boy_benchmarking`-only runtime hacks;
- and broad environment-specific legality systems.

Then Codex wrote:

```text
docs/design/degenerate_tier_control/01_002_degenerate_tier_control_implementation_workplan.md
```

This workplan followed the repo's Phase.Stage.Action pattern and specified:

- branch creation;
- focused signal/controller tests;
- runtime-loop tests;
- partition-tower degenerate query tests;
- plate-support example integration;
- documentation updates;
- and regression validation commands.

The PO asked for relevant published references to be added to the bibliography
after the workplan. Codex added references to:

- the CCH routing paper associated with arXiv `1402.0402`;
- the 2025 CCH survey/preprint associated with arXiv `2502.10519`.

Those entries went into:

```text
docs/design/logHRL.bib
```

## Major Movement 4: Degenerate-Tier Runtime Implementation

The implementation centered on making active-tier selection aware of whether
the target tier is executable.

### Control Signal Update

`select_lowest_unclosed_tier(...)` now accepts an optional executability
predicate:

```text
tier_is_executable: Callable[[int], bool] | None
```

If a tier is unclosed but not executable, it is skipped as a target for
decision execution. This preserves the old closure logic while adding a local
action-surface constraint.

Files:

```text
src/state_collapser/tower/control/signals.py
tests/tower/control/test_signals.py
```

### Controller Update

`ActiveTierController.decide(...)` now passes the executability predicate into
lowest-unclosed-tier selection. It can return the new clean control action:

```text
ControlAction.NO_AVAILABLE_ACTION
```

when no executable tier is available.

Files:

```text
src/state_collapser/tower/control/controller.py
tests/tower/control/test_controller.py
```

### Runtime Update

`ExploitExploreTowerRuntime` now accepts:

```text
tier_is_executable
```

as an optional runtime hook. Before attempting action selection, the runtime can
check whether the active tier has an outgoing action surface. If not, it lifts
until it finds an executable tier or reaches the base-tier terminal
`NO_AVAILABLE_ACTION` case.

Files:

```text
src/state_collapser/tower/runtime.py
tests/tower/control/test_runtime_loop.py
```

### Partition-Tower Query Coverage

A new test documents the important structural case:

```text
coarse tier has empty outgoing action cells
base tier is still executable
```

That is the exact pattern the downstream benchmark failure exposed.

File:

```text
tests/tower/partition/test_degenerate_tier_queries.py
```

### Plate-Support Example Integration

The plate-support exploit/explore runtime now wires its executable-tier
predicate through `PartitionTower.outgoing_action_cells(...)`:

```text
return bool(tower.outgoing_action_cells(tier, state_cell))
```

This validates the pattern in an existing example-family runtime without
making the fix counterpoint-specific.

Files:

```text
src/state_collapser/examples/plate_support_env/runtime.py
tests/examples/test_plate_support_env_exploit_explore_runtime.py
```

## Major Movement 5: Big Boy Benchmarking Handoff

After implementing the upstream fix, Codex created:

```text
docs/design/degenerate_tier_control/01_003_big_boy_benchmarking_handoff_note.md
```

The handoff tells downstream benchmark agents to pass a predicate equivalent
to:

```python
def tier_is_executable(tier: int) -> bool:
    positions = latest_runtime_snapshot.current_position_at_every_tier
    tower = latest_runtime_snapshot.partition_tower_view
    if tower is None:
        return True
    if tier < 0 or tier >= len(positions):
        return False
    state_cell = positions[tier]
    if state_cell is None:
        return False
    return bool(tower.outgoing_action_cells(tier, state_cell))
```

The key downstream effect should be:

```text
Before:
active coarse tier has zero outgoing action cells
    -> learner returns -1
    -> executor reports invalid_action_index
    -> zero concrete steps

After:
active coarse tier has zero outgoing action cells
    -> state_collapser lifts to a finer executable tier
    -> learner chooses only after a nonempty action surface exists
```

The handoff also notes an optional future downstream-specific stricter rule:

```text
tier is executable if outgoing action cells are nonempty
and at least one outgoing action cell has a legal concrete lift candidate
```

That stricter legality rule belongs downstream because concrete action
legality and counterpoint masks are environment-specific.

## Major Movement 6: Patch Release v0.7.1

After the degenerate-tier control fix landed, the PO asked whether local
verification was enough to make this a `v0.7.1` patch release.

Codex answered yes, because the change is:

- a behavioral runtime fix;
- backward-compatible;
- narrow in scope;
- covered by focused tests;
- documented for downstream benchmark consumers;
- and not a new package surface on the scale of `v0.7.0` tensorization.

The version metadata was bumped to:

```text
0.7.1
```

Files:

```text
pyproject.toml
src/state_collapser/_version.py
CITATION.cff
CHANGELOG.md
uv.lock
```

The release tag visible locally is:

```text
v0.7.1
```

at commit:

```text
0de2e23 Bump version to v0.7.1
```

## Important Correction: PO Caught the uv.lock Risk

This deserves its own section because it is exactly the kind of release-detail
failure that future agents can repeat.

Codex initially gave a version-bump command sequence that included:

```text
pyproject.toml
src/state_collapser/_version.py
CITATION.cff
CHANGELOG.md
```

but omitted:

```text
uv.lock
```

The PO caught the issue and asked whether `uv.lock` had been fixed correctly
for CI. Codex then checked the repo and confirmed that `uv.lock` now contains:

```diff
[[package]]
name = "state-collapser"
-version = "0.7.0"
+version = "0.7.1"
source = { editable = "." }
```

That file is included in the `v0.7.1` commit.

The corrected release command shape was:

```bash
git add pyproject.toml src/state_collapser/_version.py CITATION.cff CHANGELOG.md uv.lock
git commit -m "Bump version to v0.7.1"
git tag -a v0.7.1 -m "state_collapser v0.7.1"
git push origin main
git push origin v0.7.1
```

Future version changes should always check:

```bash
rg -n "version =|__version__|version:|date-released|state-collapser" pyproject.toml src/state_collapser/_version.py CITATION.cff CHANGELOG.md uv.lock
```

and verify that `uv.lock` is not stale.

## Validation

Validation reported/run during this interval included:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

The full suite passed during degenerate-tier implementation validation:

```text
490 passed, 4 skipped
```

Focused degenerate-tier/control validations included:

```bash
uv run pytest tests/tower/control
uv run pytest tests/tower/partition/test_queries_and_lift.py tests/tower/partition/test_degenerate_tier_queries.py
uv run pytest tests/examples/test_plate_support_env_exploit_explore_runtime.py
```

Tensorization-adjacent smoke was also kept in view because the change touches
runtime control but must not disturb the recent `v0.7.0` tensorization surface:

```bash
uv run pytest tests/training tests/examples/test_torch_tensor_boundary_smoke_model.py
```

After the `v0.7.1` version/lockfile correction, Codex reran the package-version
smoke:

```bash
uv run pytest tests/test_package.py
```

with result:

```text
3 passed
```

## Attribution

### Project Owner

The PO supplied the crucial conceptual correction for degenerate-tier control.
The durable package rule:

```text
if Out is empty, hop up one tier
```

is PO-originated. Codex did not invent that simplification. Codex's earlier
reasoning was drifting toward heavier architecture, and the PO correctly
recognized that the runtime already had the local query needed to solve the
problem.

The PO also:

- identified that the downstream `big_boy_benchmarking` diagnosis needed to be
  brought back into `state_collapser`;
- insisted that the fix be evaluated against the actual repo, not treated as
  an abstract conversation;
- directed Codex to create the blueprint and then the Phase.Stage.Action
  implementation workplan;
- asked for published bibliography entries for the two CCH-related references;
- asked whether the handoff note was now the correct object to give to
  `big_boy_benchmarking`;
- judged that the implemented patch was release-worthy as `v0.7.1`;
- and caught the `uv.lock` version/CI risk before the release process was
  considered complete.

The PO's role in this interval is therefore not merely "requested work." The
PO corrected the architecture, corrected the scope, corrected release hygiene,
and caught a concrete CI-risk omission.

### Big Boy Benchmarking Team

The downstream `big_boy_benchmarking` side supplied the failure diagnosis that
made the upstream bug visible. That diagnosis showed the invalid-action path in
the counterpoint benchmark setting and made clear that the active tier could
be structurally present but non-executable.

The downstream artifact did not by itself define the final upstream design.
The PO simplified it, and Codex implemented the simplified upstream invariant.

### Codex

Codex:

- read and summarized the downstream diagnosis;
- re-evaluated the repo to locate the actual control/runtime integration
  points;
- wrote the degenerate-tier blueprint;
- wrote the Phase.Stage.Action workplan;
- implemented the control/runtime fix;
- added focused tests;
- updated docs and changelog material;
- created the downstream handoff note;
- added the requested bibliography references;
- checked the release metadata;
- verified the package-version smoke test;
- and wrote this continuity report.

Codex also made one important release-process mistake: the first supplied
version-bump command omitted `uv.lock`. That mistake was caught by the PO and
corrected before this report.

## Current State

`state_collapser` now has a small but important active-tier control invariant:

```text
do not ask a learner to choose an action at a tier-state with empty Out.
```

The implementation supports this through:

- optional tier executability predicates;
- controller-level filtering of unclosed tiers;
- runtime lifting through non-executable active tiers;
- a clean `NO_AVAILABLE_ACTION` result when no tier is executable;
- and example integration through `PartitionTower.outgoing_action_cells(...)`.

The `big_boy_benchmarking` team should use:

```text
docs/design/degenerate_tier_control/01_003_big_boy_benchmarking_handoff_note.md
```

as the upstream handoff document for wiring its counterpoint runtime.

The `v0.7.1` release metadata is aligned, including `uv.lock`.

## Remaining Follow-Up

### Downstream BBB Integration

The upstream package fix exists, but `big_boy_benchmarking` still needs to wire
the predicate through its counterpoint tower-control adapter and rerun the
previous failing artifacts.

Expected downstream validation:

```text
previous invalid_action_index / zero-step failure
    -> now lifts to executable finer tier
    -> concrete environment steps occur
```

### CI Confirmation

Local validation and package metadata alignment are good, but GitHub CI should
still be checked after the pushed `v0.7.1` commit/tag. The specific CI-sensitive
detail was `uv.lock`, and it is now included.

### Future Runtime Diagnostics

The implementation intentionally avoids overbuilding diagnostics. Future
benchmark work may want explicit counters such as:

```text
degenerate_tier_lift_count
no_available_action_count
```

but those should be added only if benchmark artifacts need them.

### Downstream-Specific Legality

The upstream predicate only checks whether a tier has outgoing action cells.
For counterpoint or other constrained domains, a downstream stricter predicate
may also need to check whether any action cell has legal concrete lift
candidates. That is not a generic `state_collapser` responsibility yet.

## Files Added Or Substantially Changed

Primary new design/docs:

```text
docs/design/system_flow/01_001_system_flowcharts_and_control_flow.md
docs/design/degenerate_tier_control/error_diagnosis_conversation.md
docs/design/degenerate_tier_control/01_001_degenerate_tier_control_blueprint.md
docs/design/degenerate_tier_control/01_002_degenerate_tier_control_implementation_workplan.md
docs/design/degenerate_tier_control/01_003_big_boy_benchmarking_handoff_note.md
```

Runtime/control implementation:

```text
src/state_collapser/tower/control/controller.py
src/state_collapser/tower/control/signals.py
src/state_collapser/tower/runtime.py
src/state_collapser/examples/plate_support_env/runtime.py
```

Tests:

```text
tests/tower/control/test_controller.py
tests/tower/control/test_runtime_loop.py
tests/tower/control/test_signals.py
tests/tower/partition/test_degenerate_tier_queries.py
tests/examples/test_plate_support_env_exploit_explore_runtime.py
```

Release/version:

```text
CHANGELOG.md
CITATION.cff
pyproject.toml
src/state_collapser/_version.py
uv.lock
```

Additional docs:

```text
CONTRIBUTING.md
docs/usage/01_002_tower_runtime_mental_model.md
docs/design/logHRL.bib
```

## High-Signal Takeaway For Future Agents

Do not reframe the degenerate-tier fix as a learner problem.

The right upstream invariant is:

```text
A tier-state with empty outgoing action cells is not an executable decision
locus. Lift to a finer tier before asking the learner for an action.
```

Do not reframe the `v0.7.1` patch release as merely "version files changed."

The release was made CI-safe because the PO caught that `uv.lock` must change
with package metadata. Future release bumps should include the lockfile check
as a required step.

