# Engineer Continuity Report
## 01_008_control_corrections_tower_ownership_and_release_readiness

## Date

2026-05-18

## Interval covered

This report covers the work completed after the prior continuity report:

- [01_007_exploit_explore_design_implementation_and_merge.md]([state_collapser repository root]/docs/engineer_continuity/2026/05/15/01_007_exploit_explore_design_implementation_and_merge.md)

That prior report ended at a very specific and important intermediate state:

- the first exploit/explore controller existed
- it had been implemented, validated, and merged
- the repository had a new `tower/control/` subsystem
- `PlateSupportEnv` had a runnable exploit/explore path
- but direct runtime probing still showed the controller remaining pinned at active tier `0`

This interval begins there and continues through:

- diagnosis of the first exploit/explore control failure
- correction of the `ABC = Always Be Closing` runtime semantics
- implementation of the `find lowest unclosed` control correction
- diagnosis of a deeper architectural ownership failure around tower construction
- re-centering dynamic tower construction as a package-owned operation
- correction of contraction recursion so deeper tiers are driven by tierwise nontrivial remainder rather than by a one-shot selected base-edge family
- validation of genuinely deeper dynamic tower growth in `PlateSupportEnv`
- merge of those corrections back into `main`
- release/version work through `v0.3.0`
- README, CONTRIBUTING, and CHANGELOG corrections
- the beginning of explicit Python-package-readiness planning

This report is intentionally large because the interval was not a small patch sequence.

It contained:

- multiple semantic corrections
- multiple implementation passes
- multiple branch/merge events
- several repo-facing documentation corrections
- and the first serious turn from "research code that runs" toward "package outsiders might eventually use"

## Executive status

At the start of this interval, the repository had:

- a first exploit/explore controller
- a first exploit/explore runtime
- a direct example integration
- but a live behavior problem:
  - exploit/explore control stayed stuck at tier `0`

At the end of this interval, the repository has:

- a corrected exploit/explore control polarity
- a package-owned dynamic tower-construction surface
- corrected tierwise contraction semantics
- validated deeper tower growth on `PlateSupportEnv`
- `v0.2.1` marking the first exploit/explore control correction
- `v0.3.0` marking the package-owned dynamic tower-construction and tierwise-contraction milestone
- a significantly more accurate `CHANGELOG.md`
- a more professional `README.md` and `CONTRIBUTING.md`
- and the first explicit scoping document for what remains before the project becomes professionally usable by outside Python users

So the end-state shift is substantial:

- the project has moved from:
  - "first exploit/explore controller exists but its live semantics are wrong"

to:

- "the control semantics, tower-construction ownership, and contraction recursion have all been materially corrected, and deeper tower behavior is now actually visible in live example runs"

That is the positive side.

The cautionary side is equally important:

- these corrections revealed how much architectural meaning had leaked into example code
- how easily shallow but passing implementations can violate the intended mathematical/runtime semantics
- and how much work remains before the repository should be thought of as a polished outsider-facing Python package

## Highest-level narrative

This interval has five large movements.

### 1. The first exploit/explore controller was found to be semantically inverted

The first exploit/explore implementation did run.

But when the direct `PlateSupportEnv` exploit/explore path was probed, the runtime showed:

- active control staying at tier `0`
- no descent into lower tiers
- and therefore no actual realization of the intended "go downstairs and learn there" picture

This forced a much sharper clarification of what `ABC = Always Be Closing` was actually supposed to mean.

### 2. `ABC` was corrected from confidence-gated descent to "find lowest unclosed"

The Project Owner sharpened the intended semantics:

- `ABC` does not merely mean "prefer coarse control"
- it includes the directive:
  - find the lowest, highest-indexed tier that is currently unclosed and go there

This changed the control polarity:

- descent should not be something earned only after maturity
- the unclosed tier is the target
- lift should happen when learning at the current tier is no longer productive

This led to a real correction pass and implementation, not a wording tweak.

### 3. Direct diagnosis then exposed a deeper architectural problem: tower construction ownership was wrong

While trying to understand why the example was not behaving correctly, the Project Owner forced a full stop and a ground-truth check around a much deeper issue:

- why was tower-construction semantics showing up as though they lived in `PlateSupportEnv`?

That question exposed a real architectural leak:

- package semantics had leaked into example-specific code
- `TowerRuntime` was consuming tiers
- but examples and adapters were still constructing the tower meaning

This was not just "the example is weak."

It was a real ownership failure.

### 4. Dynamic tower construction was moved back under package ownership

The repo then went through:

- diagnosis
- design correction
- blueprint
- gameplan
- implementation

to re-center tower construction under package-owned runtime authority.

This was implemented as a real branch and merged back into `main`.

### 5. A second contraction correction was then required when the package-owned tower still stalled shallowly

After package ownership was corrected, the next live diagnosis revealed that the tower still often bottomed out too quickly.

The reason turned out to be:

- the builder selected one contraction family once on `G_t^0`
- then reused that same selected family forever at lower tiers
- once that family became trivial after one collapse, tower growth stopped

The Project Owner clarified the intended law:

- once a contraction edge has already been collapsed at tier `n`, it should not keep driving tier `n+1`
- deeper contraction should be chosen tierwise from the still-nontrivial remainder

This led to the next correction:

- tierwise remaining-edge contraction
- first reference rule:
  - approximately `20%` of the eligible nontrivial remainder per tier

This correction is what finally produced clearly deeper tower behavior in live `PlateSupportEnv` runs.

## Detailed continuity

## Phase A — Immediate runtime diagnosis after the first exploit/explore merge

The prior report ended with the first exploit/explore controller implemented and merged.

The next step in this interval was not immediately more design.

It was reality-checking the actual runtime.

The old experiment path under:

- [src/state_collapser/examples/plate_support_env/training.py]([state_collapser repository root]/src/state_collapser/examples/plate_support_env/training.py)

was rerun directly to verify that the older tower-aware training path still functioned.

That check confirmed:

- the old path still ran end-to-end
- it was not strong, but it was alive
- the new `tower/control` work had not simply destroyed the previous `PlateSupportEnv` training surface

The new exploit/explore path was then run directly.

The key result was:

- the runtime executed
- control decisions were being made
- learner state was being built
- but the active control tier remained at tier `0`

This was the first direct evidence that:

- the first exploit/explore implementation existed
- but did not yet realize the intended semantics

## Phase B — The `ABC` control semantics were corrected

The Project Owner then drove a long clarification cycle around what `ABC` really means.

Several important corrections emerged during that dialogue.

### B.1 — Descent should not be blocked by lack of closure

The first important correction was:

- non-closure should not be treated as a reason not to descend
- it should be treated as the reason to descend

This was summarized by the owner’s sharpened formulation:

- `ALWAYS BE CLOSING` includes:
  - `FIND UNCLOSED`

### B.2 — Lift should not be triggered by abstract fidelity need

The second correction was:

- lifting should not be thought of as "finer correction is theoretically needed"

Instead:

- lifting should happen when useful learning at the current tier has gone locally stale
- that is, when the current tier no longer seems to be the productive learning locus

The Project Owner’s analogy was extremely clear:

- one stops reading a research paper closely once the main content at that level is clear

This reframed "closure" at a tier as:

- useful learning has tapered off here
- the main content at this resolution has largely been extracted

### B.3 — This did not match the current design docs well enough

When the design stack under `docs/design/HRL_exploit-explore` was re-read against the new interpretation, the result was:

- architectural match: moderate to strong
- actual control-law semantics match: low to medium

That led to a specific corrective design note:

- [01_015_abc_find_unclosed_correction.md]([state_collapser repository root]/docs/design/HRL_exploit-explore/01_015_abc_find_unclosed_correction.md)

This note preserved the older blueprint history but recorded the semantic correction explicitly.

### B.4 — Control-correction blueprint and gameplan were then written

The design stack then advanced through:

- [01_016_find_lowest_unclosed_system_change_blueprint.md]([state_collapser repository root]/docs/design/HRL_exploit-explore/01_016_find_lowest_unclosed_system_change_blueprint.md)
- [01_017_find_lowest_unclosed_implementation_gameplan.md]([state_collapser repository root]/docs/design/HRL_exploit-explore/01_017_find_lowest_unclosed_implementation_gameplan.md)

This was the first correction pass after the initial exploit/explore merge.

## Phase C — `Find Lowest Unclosed` implementation

The correction was implemented on a dedicated branch:

- `codex/find-lowest-unclosed-implementation`

The running log for that work is:

- [01_017_find_lowest_unclosed_implementation_log.md]([state_collapser repository root]/docs/design/HRL_exploit-explore/01_017_find_lowest_unclosed_implementation_log.md)

The owner approved one important simplification for the first corrected runtime:

- tier-level signals

with future alternatives explicitly preserved for later exploration:

- local-region signals
- quotient-position signals
- aggregated productive-learning summaries over a neighborhood

The implementation then:

- replaced confidence-gated descent semantics
- added tier-level productive-learning signals
- reworked control selection around lowest-unclosed semantics
- reinterpreted lift around productive-learning exhaustion
- added focused tests

Key test additions:

- `tests/tower/control/test_lowest_unclosed_selection.py`
- `tests/tower/control/test_lift_on_productive_exhaustion.py`

The direct runtime result was the first real behavioral correction:

- the exploit/explore path no longer remained pinned at tier `0`

This work was validated and later merged back into `main`.

That branch is part of the reason `v0.2.1` exists.

## Phase D — Recognition that tower-construction ownership was still wrong

After the control correction, the next set of questions shifted from:

- "why is control not descending correctly?"

to:

- "what does tower construction itself currently mean in this example?"

This exposed a deeper concern:

- the current contraction logic for `PlateSupportEnv` still looked like a fixed two-tier projection scheme

That led to a much more severe Project Owner intervention:

- why would tower-construction semantics live in `PlateSupportEnv` at all?

The correct answer was:

- they should not

This forced a full-stop ground-truth check.

### D.1 — Ground-truth repo investigation

The repo was inspected specifically to check whether the feared architectural drift had actually occurred.

The answer was:

- yes, it had

The strongest evidence was:

- `TowerRuntime` consumed already-existing quotient tiers
- while example and adapter code still built those tiers and their meanings

The specific leak surfaces included:

- `src/state_collapser/examples/plate_support_env/runtime.py`
- `src/state_collapser/examples/robot_constraint_toy.py`
- `src/state_collapser/adapters/gymnasium.py`

### D.2 — Design-history investigation

The repo’s design history was then re-read to determine when this misalignment had happened.

The resulting diagnosis was written into:

- [01_018_tower_construction_ownership_misalignment_diagnosis.md]([state_collapser repository root]/docs/design/HRL_exploit-explore/01_018_tower_construction_ownership_misalignment_diagnosis.md)

This diagnosis concluded that:

- the early package-design layer was still aligned with package-owned tower construction
- a soft ambiguity appeared in the training-integration design surface
- the first hard documented misalignment emerged during the `PlateSupportEnv` tower-training integration history
- later exploit/explore planning then reinforced that drift rather than correcting it

### D.3 — Correction design stack

The next documents in the stack were:

- [01_019_package_owned_tower_construction_correction.md]([state_collapser repository root]/docs/design/HRL_exploit-explore/01_019_package_owned_tower_construction_correction.md)
- [01_020_package_owned_dynamic_tower_construction_blueprint.md]([state_collapser repository root]/docs/design/HRL_exploit-explore/01_020_package_owned_dynamic_tower_construction_blueprint.md)
- [01_021_package_owned_dynamic_tower_construction_implementation_gameplan.md]([state_collapser repository root]/docs/design/HRL_exploit-explore/01_021_package_owned_dynamic_tower_construction_implementation_gameplan.md)

These documents re-established the intended law:

- dynamic tower construction is a package operation
- examples provide problem semantics, not primary tower semantics

## Phase E — Package-owned dynamic tower construction implementation

This work was carried out on the branch:

- `codex/package-owned-dynamic-tower-construction`

The running log is:

- [01_021_package_owned_dynamic_tower_construction_implementation_log.md]([state_collapser repository root]/docs/design/HRL_exploit-explore/01_021_package_owned_dynamic_tower_construction_implementation_log.md)

The key implementation changes were:

- addition of:
  - `src/state_collapser/tower/construction.py`
- re-binding of:
  - `TowerRuntime`
  as the first package-level authority for dynamic tower construction
- displacement of example-owned fixed tier builders from:
  - `PlateSupportEnv`
  - `robot_constraint_toy`
  - Gymnasium adapter paths
- addition of explicit runtime/tier queries
- ensuring exploit/explore runtime consumed snapshot positions from package-built tower state rather than fixed fine/coarse tier semantics

This pass corrected the ownership boundary.

It also produced a first live behavioral improvement:

- exploit/explore control now consumed package-built tower state
- and sample runs descended immediately off tier `0`

This work was validated, merged, and later became part of `v0.3.0`.

## Phase F — Diagnosis of shallow tower growth even after ownership correction

Once package-owned dynamic tower construction existed, the next reality check was:

- does the example now deepen the tower in the intended way?

The answer was:

- not enough

Even after the ownership correction, the live example still often produced only:

- tier `0`
- tier `1`

This forced the next diagnosis.

### F.1 — Precise failure mode

The key findings were:

- the default contraction policy in the example path was extremely weak
- the policy was highly repetitive
- the builder was selecting a contraction family once on `G_t^0`
- then projecting that same selected family downward forever
- once that selected family became trivial after one collapse, recursion stopped

This diagnosis is what directly motivated the next correction.

## Phase G — Tierwise remaining-edge contraction correction

The Project Owner then clarified the missing law:

- one should never keep using an already-collapsed edge family as the driver of the next deeper contraction
- if contraction repeats on the same arrow forever, the semantics are wrong

The corrected idea was:

- choose contraction families tierwise from the still-nontrivial remainder
- first experimental rule:
  - roughly `1/5` of the eligible remaining edges per tier

### G.1 — Design stack

This produced:

- [01_022_tierwise_remaining_edge_contraction_blueprint.md]([state_collapser repository root]/docs/design/HRL_exploit-explore/01_022_tierwise_remaining_edge_contraction_blueprint.md)
- [01_023_tierwise_remaining_edge_contraction_implementation_gameplan.md]([state_collapser repository root]/docs/design/HRL_exploit-explore/01_023_tierwise_remaining_edge_contraction_implementation_gameplan.md)

### G.2 — Implementation

The implementation was carried out on the same package-owned tower-construction branch and recorded in:

- [01_023_tierwise_remaining_edge_contraction_implementation_log.md]([state_collapser repository root]/docs/design/HRL_exploit-explore/01_023_tierwise_remaining_edge_contraction_implementation_log.md)

The corrected builder now:

- computes tierwise eligible nontrivial remainder
- retires already-collapsed contraction members
- selects approximately `20%` of the current remainder
- records per-tier contraction diagnostics and stopping reasons

### G.3 — Important runtime surprise

The first corrected recursion immediately broke an old implicit assumption:

- `PlateSupportEnv` was no longer resetting into a two-tier tower

Deeper package-built towers then exposed another runtime bug:

- the exploit/explore runtime could hold an active control tier index that no longer existed after a rebuilt tower changed depth

This produced a `KeyError` and required:

- clamping the active tier during runtime synchronization

That fix was implemented as part of the same correction interval.

### G.4 — Behavioral result

The final live run after this correction was radically different from the earlier shallow behavior.

Observed tiers across a live exploit/explore run included:

- `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]`

The last sampled episode showed repeated descent through deeper package-built tiers.

This is the strongest single behavioral milestone of the interval:

- the repo moved from:
  - "exploit/explore exists but stalls shallowly"

to:

- "deeper tower growth and repeated descent are actually visible in live example runs"

## Phase H — Merge back into `main`

The completed package-owned tower-construction branch was merged back into `main` with a fast-forward.

Post-merge state was:

- branch: `main`
- `HEAD` at the tower-construction/correction commits
- worktree clean

This means the corrected ownership model and corrected contraction semantics are now part of mainline repo reality, not only branch-local experiments.

## Phase I — Release/version work

This interval also included real release/version work.

### I.1 — `v0.2.0`

The project version was bumped from `0.1.0` to `0.2.0` to mark:

- the first exploit/explore controller implementation

This included:

- `pyproject.toml`
- `src/state_collapser/_version.py`
- version tests

### I.2 — `v0.2.1`

After the `find lowest unclosed` correction, a `v0.2.1` release tag was created to mark:

- corrected exploit/explore control semantics

The release title/description for that version emphasized:

- `ABC` control semantics correction
- lowest-unclosed descent
- productive-learning-based lift

### I.3 — `v0.3.0`

Finally, after package-owned dynamic tower construction and tierwise contraction correction were merged, the version was bumped again to:

- `0.3.0`

and tagged:

- `v0.3.0`

The `v0.3.0` release was framed as:

- package-owned dynamic tower construction
- tierwise contraction over the remaining nontrivial edge family

This is a real semantic release boundary, not only a cosmetic one.

## Phase J — README, CONTRIBUTING, and release-facing repo corrections

This interval also included several user-facing documentation corrections.

### J.1 — Badge and release-state sanity work

There was an extended badge/debugging interval where it became clear that:

- README badge correctness depends not just on markdown, but on upstream service state
- CI, PyPI, release, issues, and Codecov all depend on external/public service reality

That debugging episode produced important process corrections:

- do not fake live badges with hand-written stand-ins
- distinguish clearly between local repo truth and public service truth

### J.2 — README restructuring

The README was reworked to look more like a professional Python package README.

This included:

- reorganizing sections into a more standard Python-package order
- moving practical install/usage content into more prominent positions
- replacing placeholders with real prose
- clarifying the expected speed-up story

A comparison draft was created and then adopted:

- `README_python_package_draft.md`

The active root README then became much more package-consumer friendly.

### J.3 — CONTRIBUTING rewrite

The root `CONTRIBUTING.md` was rewritten into a more professional Python-package contribution guide.

This included:

- clearer setup
- validation commands
- repo layout explanation
- contribution workflow
- design-authority expectations
- release/version guidance

### J.4 — CHANGELOG correction

At the end of this interval, `CHANGELOG.md` itself was found to be badly inaccurate:

- most real release history had been stranded under `Unreleased`
- the tagged releases were not properly represented

It was then rewritten to provide a more accurate release history for:

- `0.1.0`
- `0.2.0`
- `0.2.1`
- `0.3.0`

This was done by grounding the changelog in:

- implementation logs
- continuity reports
- tagged release points

## Phase K — Beginning of Python-package-readiness scoping

After the major semantic/runtime corrections, the project also began to ask a new class of question:

- what would it take to turn this from "research repo with a real package" into "a package outsiders can actually use professionally"?

This produced the first scoping document under:

- `docs/design/PyPl_readiness/`

Specifically:

- [01_001_python_package_readiness_scoping.md]([state_collapser repository root]/docs/design/PyPl_readiness/01_001_python_package_readiness_scoping.md)

This document distinguishes two standards:

1. installable and professionally consumable
2. stable enough that strangers can rely on it without deep hand-holding

It concludes that:

- the project is already fairly strong on the first
- but only partway along on the second

and then scopes the major remaining work:

- public API stabilization
- outsider-facing workflows
- packaging verification
- documentation
- stable/experimental boundary marking
- reproducible examples
- issue/PR intake posture

This matters because it marks the first explicit planning move beyond:

- "keep correcting semantics and architecture"

toward:

- "prepare for real external package use"

## Major artifacts created or substantially advanced in this interval

### Design / implementation-control artifacts

- `docs/design/HRL_exploit-explore/01_015_abc_find_unclosed_correction.md`
- `docs/design/HRL_exploit-explore/01_016_find_lowest_unclosed_system_change_blueprint.md`
- `docs/design/HRL_exploit-explore/01_017_find_lowest_unclosed_implementation_gameplan.md`
- `docs/design/HRL_exploit-explore/01_017_find_lowest_unclosed_implementation_log.md`
- `docs/design/HRL_exploit-explore/01_018_tower_construction_ownership_misalignment_diagnosis.md`
- `docs/design/HRL_exploit-explore/01_019_package_owned_tower_construction_correction.md`
- `docs/design/HRL_exploit-explore/01_020_package_owned_dynamic_tower_construction_blueprint.md`
- `docs/design/HRL_exploit-explore/01_021_package_owned_dynamic_tower_construction_implementation_gameplan.md`
- `docs/design/HRL_exploit-explore/01_021_package_owned_dynamic_tower_construction_implementation_log.md`
- `docs/design/HRL_exploit-explore/01_022_tierwise_remaining_edge_contraction_blueprint.md`
- `docs/design/HRL_exploit-explore/01_023_tierwise_remaining_edge_contraction_implementation_gameplan.md`
- `docs/design/HRL_exploit-explore/01_023_tierwise_remaining_edge_contraction_implementation_log.md`

### Package/readiness scoping

- `docs/design/PyPl_readiness/01_001_python_package_readiness_scoping.md`

### New or substantially corrected code surfaces

- `src/state_collapser/tower/control/`
- `src/state_collapser/tower/construction.py`
- `src/state_collapser/tower/runtime.py`
- `src/state_collapser/examples/plate_support_env/runtime.py`
- `src/state_collapser/examples/plate_support_env/training.py`
- `src/state_collapser/examples/robot_constraint_toy.py`
- `src/state_collapser/adapters/gymnasium.py`
- `src/state_collapser/quotient/tier_view.py`

### New or substantially corrected tests

- `tests/tower/control/test_lowest_unclosed_selection.py`
- `tests/tower/control/test_lift_on_productive_exhaustion.py`
- updates under:
  - `tests/tower/`
  - `tests/examples/`
  - `tests/quotient/`

## Behavioral and validation milestones

The interval includes several important validation markers.

### First exploit/explore implementation validation

- full suite:
  - `171 passed`

### `Find Lowest Unclosed` correction validation

- focused correction suite:
  - `35 passed`
- full suite:
  - `178 passed`

### Package-owned dynamic tower-construction correction validation

- focused correction slice:
  - `29 passed`
- broader slice:
  - `68 passed`
- full suite:
  - `181 passed`

### Tierwise remaining-edge contraction correction validation

- focused correction slice:
  - `30 passed`
- broader slice:
  - `69 passed`
- full suite:
  - `182 passed`

Across these stages:

- `ruff check .` remained green
- `mypy src` remained green

This matters because the interval was not only conceptual. It produced real, repeatedly validated code changes.

## What was learned in this interval

Several important lessons were forced into the project’s continuity memory.

### 1. A runnable controller can still be semantically wrong

The first exploit/explore implementation passed tests and ran, but its live behavior still violated the intended training story.

This is an important caution for future work:

- passing tests do not by themselves validate the semantics

### 2. `ABC` is a stronger and more directional law than originally encoded

The corrected control semantics now clearly emphasize:

- find the lowest unclosed tier
- descend by default
- lift when productive learning at the current tier is exhausted

That should remain part of the repo’s conceptual memory.

### 3. Ownership errors can hide inside passing example integrations

The tower-construction ownership leak is a major cautionary example:

- architecture can drift even when examples run
- example integration can silently absorb package semantics if ownership is not aggressively policed

### 4. Recursive contraction semantics matter as much as tower ownership

Correct ownership was necessary but not sufficient.

Even after tower construction moved into the package, recursion still behaved shallowly until the contraction rule itself was corrected.

### 5. The project is beginning to transition from internal research iteration to package-usability planning

The package-readiness scoping work is not yet a packaging implementation plan.

But it does mark the start of a new repo phase:

- making the package professionally usable by outsiders

## Current end state

At the end of this interval:

- `main` includes:
  - corrected exploit/explore control polarity
  - package-owned dynamic tower construction
  - tierwise remaining-edge contraction semantics
- the repo has passed through:
  - `v0.2.0`
  - `v0.2.1`
  - `v0.3.0`
- `PlateSupportEnv` now shows deeper package-built tower growth in live exploit/explore runs
- root user-facing docs are materially more professional and more accurate
- `CHANGELOG.md` now reflects actual release history rather than an undifferentiated `Unreleased` mass
- a new readiness-planning track exists under:
  - `docs/design/PyPl_readiness/`

## Recommended continuity handoff for the next engineer

The next engineer should not assume the main problem is still:

- "build the first exploit/explore controller"

That has already happened.

They also should not assume the main problem is still:

- "fix the pinned-at-tier-0 behavior"

That has also already happened.

The live frontier has moved.

The next engineer should treat the current project state as:

1. exploit/explore control exists
2. lowest-unclosed semantics exist
3. package-owned tower construction exists
4. tierwise remaining-edge contraction exists
5. deeper tower behavior is now visible

The next likely frontiers are instead:

- improving contraction-policy quality rather than just contraction semantics
- understanding whether the new deep tower behavior is mathematically meaningful or merely mechanically deeper
- developing evaluation methodologies for comparing:
  - plain Gymnasium
  - top-tier-only
  - full tower
- promoting instrumentation into a real user-facing package feature
- freezing a real public API
- defining supported outsider workflows
- packaging and PyPI-readiness work beyond the current scoping level

The most important warning for the next engineer is:

- do not casually reintroduce example-owned tower semantics
- do not collapse the distinction between:
  - passing tests
  - semantically correct tower/control behavior

That distinction defined much of this interval.
