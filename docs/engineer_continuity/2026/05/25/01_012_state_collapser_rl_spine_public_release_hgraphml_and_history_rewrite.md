# Engineer Continuity Report
## 01_012_state_collapser_rl_spine_public_release_hgraphml_and_history_rewrite

## Date

2026-05-25

## Interval Covered

This report covers the `state_collapser` work completed after:

- [01_011_young_tableaux_runtime_review_release_and_synthetic_blow_revisions.md]([state_collapser repository root]/docs/engineer_continuity/2026/05/24/01_011_young_tableaux_runtime_review_release_and_synthetic_blow_revisions.md)

The prior report ended with the Young-tableaux runtime refactor, evaluation
environment repairs, the `v0.5.0` release line, the synthetic Blow review and
accepted revisions, and a first outreach/rolodex brief.

This interval begins with the Project Owner identifying the next maturity gap:
`state_collapser` now had serious quotient-tower runtime machinery, but it did
not yet have a mature RL framework/training stack, serious benchmark evidence,
or public-release hardening. The interval then moved through:

- an extended discussion of why `state_collapser` should not become RLlib or
  Stable-Baselines3,
- a design pivot toward a fiber-conditioned training spine,
- documentation explaining the package to engineers,
- root documentation cleanup and routing,
- a temporary cross-repo excursion into `HGraphML`,
- documentation of `HGraphML` as the first downstream application,
- a public-release and security audit for `state_collapser`,
- implementation of the audit's accepted release-hardening actions,
- versioning to `0.6.0`,
- a local-path/security history rewrite for public release,
- deletion of old remote release tags after the rewrite,
- and a small paper-draft marking commit on `logHRL.tex`.

Because the public Git history was intentionally rewritten during this interval,
the visible public log no longer contains the full development sequence. The
old complete history is preserved locally at:

```text
private-full-history-before-public-squash-20260525
```

and in the verified bundle:

```text
[temporary private bundle]/state_collapser-full-history-before-public-squash-20260525.bundle
```

At the time of this report, the public-facing `main` points at:

```text
017d9d4 [DRAFT]
```

with the clean public baseline immediately below it:

```text
b99d78a public release baseline
```

The public release tag retained on the remote is:

```text
v0.6.0
```

## Executive Status

At the beginning of this interval, `state_collapser` had just become a much more
serious research runtime: partition-backed towers, richer examples, better
training surfaces, and a much stronger test suite. It was still not ready to be
presented as a mature RL framework or as a benchmark-supported speed-up
package.

At the end of this interval, `state_collapser` is better understood and better
positioned as:

```text
an upstream quotient-tower / structural decision layer
```

rather than:

```text
a replacement for existing RL frameworks
```

The key conceptual line that emerged was:

```text
RLlib says:
    Give me an env; I will run scalable RL algorithms on it.

Stable-Baselines3 says:
    Give me an env; I will run standard reliable RL algorithms on it.

state_collapser says:
    Give me an env or discovered transition system; I will construct a better
    hierarchical/quotient decision structure around it.
```

This distinction was moved into the repository documentation so that engineers
can understand the package without needing the full research conversation.

The package is now also documented as upstream infrastructure for `HGraphML`,
the first concrete downstream application using partition towers outside the
original RL setting.

The release posture changed from "maybe PyPI next" to:

```text
public GitHub research release first; PyPI later, after serious benchmarking
```

The public-history cleanup is now complete on GitHub:

- remote `main` points to the clean public baseline plus the later draft commit,
- the remote retains only clean `v0.6.0`,
- old remote tags `v0.1.0` through `v0.5.0` were deleted,
- local `main` tracks `origin/main`,
- the working tree is clean before this report is added.

The most important open issue is now downstream compatibility:

```text
HGraphML currently declares state-collapser @ ...@v0.5.0, but the cleaned
state_collapser remote now exposes v0.6.0 as the public release tag.
```

That must be corrected before HGraphML fresh installs or CI can be treated as
stable against the cleaned public upstream.

## Source Reconstruction Note

This report is reconstructed from:

- current `state_collapser` working tree,
- current public `main`,
- the local private backup branch
  `private-full-history-before-public-squash-20260525`,
- the previous engineer continuity report,
- `docs/design/RL_framework_maturity/`,
- `docs/design/public_release_security_audit/`,
- `docs/usage/`,
- `docs/api_notes/`,
- `README.md`,
- `CONTRIBUTING.md`,
- `CHANGELOG.md`,
- `SECURITY.md`,
- the release/history rewrite commands and validation results,
- and the live discussion around `HGraphML` as downstream application.

Because the public history was intentionally squashed, the old commit hashes
below are private/local reconstruction aids. They should not be treated as
public release-history references.

Relevant private-history commits include:

```text
4deeb37 artifact moved to repo
d4e7161 RL framework maturity design
19ec36d implement fiber-conditioned training spine
f2e6aee repo-wide documentation update
2e1f617 public release / security audits
6792555 fixed Python version badge
```

Relevant public-history commits include:

```text
b99d78a public release baseline
017d9d4 [DRAFT]
```

## Authorship And PO Attribution

The Project Owner supplied the core conceptual direction for this interval.
Specifically, the PO:

- identified that the next limitation was not another quotient-tower refactor
  but RL framework maturity, benchmarking, and release posture,
- insisted that `state_collapser` should not be confused with RLlib or
  Stable-Baselines3,
- pushed for a clearer engineer-facing explanation of what the package is,
- corrected the discussion of training to include the essential
  "freeze tier `i+1`, lift to tier `i`" structure,
- identified that the true training relation is not simply a learner hook but a
  staged/fiber-conditioned control spine,
- directed the TODO list out of `README.md` and into `CONTRIBUTING.md`,
- requested root documentation accuracy audits,
- accepted the "routing/policy docs" approach for `docs/package_usage.md` and
  `docs/public_api.md`,
- introduced `HGraphML` as a downstream application of Malik's insight,
- directed that `HGraphML` be documented throughout `state_collapser` as a real
  downstream user,
- clarified that public release should be GitHub-first and research-mode rather
  than PyPI-first,
- explicitly chose to keep the full research/provenance documentation corpus,
  provided local path leakage was removed,
- asked for public-release/security audit and hardening,
- asked about historical diff leakage and chose to rebuild public history before
  public release,
- performed the final remote deletion of old tags after GitHub initially
  rejected the assistant's deletion attempt,
- and made the final paper-draft marking commit.

Codex supplied:

- synthesis of the RL framework comparison,
- design documentation and implementation gameplans,
- code and documentation edits,
- package-level validation,
- release/security audit analysis,
- HGraphML downstream-compatibility test and documentation,
- version and metadata hardening,
- local-path leakage scanning and cleanup,
- clean-history rewrite execution,
- public tag creation and remote push,
- and this continuity reconstruction.

## Major Movement 1: RL Framework Maturity Was Clarified

The interval began from the PO's observation that the repo still lacked the
kind of neural RL stack a mature RL framework would contain:

- no serious PyTorch model family,
- no tensor/device abstraction,
- no vectorized rollout system,
- no replay buffer beyond simple research surfaces,
- no checkpoint/resume surface,
- no experiment manifest/artifact contract,
- and no serious benchmarking evidence.

The assistant initially explained RLlib and Stable-Baselines3 too cryptically.
The PO asked for a clearer comparison: why would an engineer compare
`state_collapser` to those systems at all, and why should it be neither?

The distilled comparison became:

```text
RLlib:
    scalable distributed RL execution and algorithms

Stable-Baselines3:
    standard reliable RL algorithms with ergonomic training loops

state_collapser:
    quotient/hierarchy construction around an env or discovered transition
    system
```

This led to a core repository identity:

```text
Gymnasium env
    -> state_collapser discovers graph/tower/quotient structure
        -> policy learner trains using tower-aware decision inputs
```

This is not merely marketing language. It clarifies ownership boundaries:

- `state_collapser` should not own every PPO/SAC/DQN implementation,
- `state_collapser` should own quotient-tower structure, tower-aware decision
  inputs, fibers, frozen quotient context, lift/descend semantics, and
  collector/learner surfaces that expose this structure cleanly,
- standard RL frameworks may sit beside or downstream of those surfaces where
  appropriate,
- but staged tower training cannot be reduced to "just pass hooks into an
  existing learner."

## Major Movement 2: The True Training Spine Became Fiber-Conditioned

The PO pushed back on a too-generic training-spine formulation:

```text
DecisionInput -> model -> ActionDecision -> collector -> replay -> learner
```

The missing part was the actual hierarchical training behavior:

```text
freeze tier-(i+1), lift to tier-i
```

The PO's correction was important because it showed that tower-aware training is
not merely a better observation vector for an ordinary learner. The package has
to represent:

- a frozen higher-tier quotient behavior,
- the fiber over that frozen quotient path/action/cell,
- lower-tier admissible choices conditioned by that frozen quotient decision,
- departure from the frozen path,
- masks and diagnostics that distinguish "locally possible" from "allowed by
  the staged training contract",
- and training records that preserve both the active lower-tier action and the
  frozen higher-tier context.

This became the basis for the design series:

- `docs/design/RL_framework_maturity/01_001_rl_framework_maturity_and_tower_training_spine_discussion.md`
- `docs/design/RL_framework_maturity/01_002_fiber_conditioned_training_spine_blueprint.md`
- `docs/design/RL_framework_maturity/01_003_fiber_conditioned_training_spine_engineer_documentation_blueprint.md`
- `docs/design/RL_framework_maturity/01_004_fiber_conditioned_training_spine_implementation_gameplan.md`
- `docs/design/RL_framework_maturity/01_005_fiber_conditioned_training_spine_engineer_documentation_implementation_gameplan.md`
- `docs/design/RL_framework_maturity/01_006_fiber_conditioned_training_spine_paired_implementation_log.md`

The corresponding implementation commit was private-history:

```text
19ec36d implement fiber-conditioned training spine
```

It added or updated:

- `docs/api_notes/fiber_conditioned_stage.md`,
- `docs/api_notes/frozen_quotient_behavior.md`,
- `docs/api_notes/partition_tower.md`,
- `docs/api_notes/path_fiber.md`,
- `docs/api_notes/training_inputs_and_transitions.md`,
- `docs/usage/01_001_what_state_collapser_is.md`,
- `docs/usage/01_002_tower_runtime_mental_model.md`,
- `docs/usage/01_003_training_surface_quickstart.md`,
- `docs/usage/01_004_fiber_conditioned_training.md`,
- `docs/usage/01_005_using_your_own_training_loop.md`,
- `docs/usage/01_006_gymnasium_integration.md`,
- `docs/usage/01_007_glossary.md`,
- `docs/usage/01_008_common_misunderstandings.md`,
- `src/state_collapser/training/fibers.py`,
- `src/state_collapser/training/frozen.py`,
- `src/state_collapser/training/stages.py`,
- plus tests for fiber-conditioned stages, frozen quotient behavior, path
  fibers, and related inputs/transitions.

The implemented training spine should be understood as a research-mode staging
surface. It is not yet a mature RL training framework. It is the first serious
package-native representation of how quotient towers interact with learning.

## Major Movement 3: Root Documentation Was Repositioned

The PO judged that `README.md` had reached the stage where construction/TODO
material should move out of the "main room."

The assistant moved the project TODO posture into `CONTRIBUTING.md` and then
performed a root-doc accuracy audit. Accepted root-doc updates included:

- a real `0.5.0` section in `CHANGELOG.md`,
- refreshed `CONTRIBUTING.md` layout, roles, example inventory, and current
  reality,
- cleaned `EVALUATION.md` typos, incomplete sentence, numbering, and
  tower-probe semantics,
- added benchmark and newer design/continuity links to `README.md`,
- and shortened `docs/package_usage.md` / `docs/public_api.md` into routing and
  policy documents rather than stale provisional-surface inventories.

The private-history commit was:

```text
f2e6aee repo-wide documentation update
```

This mattered because the repository had accumulated a huge amount of design
material. The root docs now do more routing and less dumping:

- `README.md` explains what the package is and where to go next,
- `CONTRIBUTING.md` carries active TODO and contribution posture,
- `EVALUATION.md` describes the evaluation and benchmark surface honestly,
- `docs/package_usage.md` routes package users to current usage docs,
- `docs/public_api.md` sets public/provisional API policy rather than trying to
  maintain a fragile inventory by hand.

## Major Movement 4: HGraphML Became A Real Downstream Constraint

The PO then introduced Abdullah N. Malik's observation that the
`state_collapser` quotient-tower machinery should apply beyond RL, especially
to graph ML systems formulated as dataflow over graphs.

The resulting downstream repo, `HGraphML`, is documented separately in its own
continuity report. The `state_collapser` side of the story is:

```text
HGraphML became the first concrete downstream package that calls
state_collapser partition-tower machinery for a non-RL graph-message-passing
application.
```

The assistant added `HGraphML` to `state_collapser` documentation as a
downstream application:

- `docs/usage/01_009_downstream_applications.md`,
- additions to README/API notes,
- and an HGraphML-shaped compatibility test:
  `tests/tower/partition/test_hgraphml_downstream_compatibility.py`.

The key compatibility contract is:

- HGraphML uses `State`, `PrimitiveAction`, and `BaseEdge` to represent known
  graph nodes and edges,
- HGraphML calls `build_partition_tower_full(...)` with a contraction schema,
- HGraphML recovers node fibers from state-cell members,
- HGraphML recovers edge fibers by reading registered base edges and grouping
  them according to active tier state cells,
- HGraphML relies on lazy readout behavior so compatibility quotient views do
  not dominate the hot path.

The downstream documentation now explicitly says:

```text
Do not make a public release that breaks HGraphML's first import unless the
break is intentional, documented, and paired with a migration path.
```

### Immediate Follow-Up Risk

The public-history rewrite removed old public tags `v0.1.0` through `v0.5.0`
from the remote. HGraphML currently declares:

```text
state-collapser @ git+https://github.com/TYLERSFOSTER/state_collapser.git@v0.5.0
```

That tag no longer exists remotely after cleanup. The next HGraphML action
should update the dependency to the clean public release tag:

```text
v0.6.0
```

or to a normal registry dependency once PyPI publication happens later. Until
that is fixed, HGraphML fresh installs from a clean environment may fail.

## Major Movement 5: Public Release And Security Audit

After HGraphML highlighted `state_collapser` as an upstream dependency, the PO
asked for a public-release and security audit of `state_collapser`.

The audit document is:

- `docs/design/public_release_security_audit/01_001_state_collapser_public_release_and_security_audit.md`

The audit was modeled on the HGraphML public-release audit but adjusted for
`state_collapser` as the upstream package.

The audit's bottom-line release posture was:

```text
state_collapser is mechanically close to a lightweight public research release,
but it should not be represented as a mature RL framework or benchmark-proven
speed-up package.
```

The PO made several release decisions inside the audit:

- public release should be GitHub-first,
- PyPI should be deferred until serious benchmarking exists,
- `v0.6.0` is the right version, not `v1.0.0`,
- full docs/provenance corpus should remain in the repo/source distribution,
- local-machine path leakage should be cleaned,
- HGraphML compatibility should be preserved through an explicit downstream
  compatibility test rather than by freezing every internal API.

Implemented hardening included:

- package version bumped to `0.6.0`,
- `_version.py` aligned,
- package metadata updated to canonical GitHub URLs,
- `Typing :: Typed` and Python version classifiers adjusted,
- publish workflow made manual-only,
- README install language shifted to source/GitHub-tag installs rather than
  PyPI,
- active PyPI version badge removed/commented while PyPI is intentionally
  deferred,
- `SECURITY.md` added,
- HGraphML-shaped compatibility test added,
- local path leakage cleaned across scanned root/docs text corpus,
- and design/continuity docs rewritten to use neutral placeholders such as
  `[state_collapser repository root]` where historical specificity needed to
  be preserved without exposing machine layout.

The private-history commit was:

```text
2e1f617 public release / security audits
```

The follow-up small badge fix was:

```text
6792555 fixed Python version badge
```

## Major Movement 6: Public History Was Rebuilt

The PO then asked whether git diffs in both repos exposed local-machine
details. The answer was:

- HGraphML's current tree and scanned history were not showing the same problem,
- `state_collapser` current `HEAD` was clean,
- but `state_collapser` historical commits/diffs still exposed local path
  information because cleanup commits preserve deleted text in GitHub diffs.

The PO judged the repo still private/not widely cloned and chose to fix this
before public release by rebuilding/squashing public history.

The assistant explained the process and then executed it:

1. Verified working tree on old `main`.
2. Created backup branch:

```text
private-full-history-before-public-squash-20260525
```

3. Created verified full-history bundle:

```text
[temporary private bundle]/state_collapser-full-history-before-public-squash-20260525.bundle
```

4. Created an orphan clean-history branch.
5. Restored the exact tracked tree from the backup branch.
6. Verified that no staged generated artifacts were included.
7. Verified no staged local-path matches.
8. Created the clean root commit:

```text
b99d78a public release baseline
```

9. Created clean annotated tag:

```text
v0.6.0
```

10. Validated the clean branch:

```text
ruff check . -> passed
pytest -> 467 passed
mypy src -> passed
build -> succeeded
twine check -> passed
```

11. Force-with-lease pushed clean `main` to GitHub.
12. Pushed clean `v0.6.0`.
13. Attempted to delete old remote tags.
14. GitHub initially rejected deletion/update of old tags due protected release
    behavior.
15. The PO then successfully deleted old remote tags:

```text
v0.1.0
v0.2.0
v0.2.1
v0.3.0
v0.4.0
v0.5.0
```

16. Final verification showed remote GitHub refs:

```text
refs/heads/main -> b99d78a...
refs/tags/v0.6.0 -> b99d78a...
```

After this, public GitHub history no longer exposes old release tags or the old
multi-commit history through `main`.

## Major Movement 7: Post-Rewrite Draft Commit

After the public-history rewrite, the PO made one small public commit:

```text
017d9d4 [DRAFT]
```

This changed:

- `docs/design/logHRL.tex`,
- `docs/design/logHRL.pdf`.

The TeX change marks the paper title as:

```tex
\textsf{[DRAFT]}
```

This commit is now visible on top of the clean public baseline. It does not
undo the history-cleaning work.

## Current Public Repository State

Current remote state after verification:

```text
origin/main -> 017d9d4 [DRAFT]
v0.6.0      -> b99d78a public release baseline
```

Current local tags:

```text
v0.6.0
```

Old release tags:

```text
v0.1.0 through v0.5.0
```

have been deleted remotely and locally.

Current local private branch retaining old history:

```text
private-full-history-before-public-squash-20260525
```

Old local development branches still exist and may point into private history:

```text
codex-second-full-build-experiment
codex/env-001-next-phase
codex/env-001-plate-support-env
codex/example-family-implementation
codex/exploit-explore-implementation
codex/fiber-conditioned-training-spine
codex/find-lowest-unclosed-implementation
codex/model-training-surfaces
codex/package-owned-dynamic-tower-construction
codex/post-young-eval-env-schema-repair
codex/synthetic-blow-revisions-01
codex/v0.5.0-ci-release-prep
codex/young-tableaux-runtime-refactor
```

Because these are local-only private branches, they are acceptable as local
provenance. Do not run:

```bash
git push --all
```

from this checkout unless those branches have been intentionally reviewed.

Also avoid:

```bash
git push --tags
```

unless local tags have first been checked. At the time of this report only
`v0.6.0` is local, but explicit ref pushes remain safer during post-rewrite
cleanup.

## Validation Results To Carry Forward

The clean public baseline was validated with:

```text
uv run ruff check .          -> passed
uv run pytest                -> 467 passed
uv run mypy src              -> passed
python -m build              -> built sdist and wheel
python -m twine check dist/* -> passed
```

One intentionally over-broad command was also tried:

```text
uv run mypy src tests
```

That failed because tests contain lightweight fakes/untyped fixtures that are
not part of the configured type-checking target. The configured repository
check is:

```text
mypy src
```

and that passed.

Local-path scans on the clean public branch found no matches for user-home
absolute paths, machine temporary-directory paths, host-name references, or
shell-prompt-style user/host fragments in the current tree or clean branch
history.

## What Changed In The Repository's Public Meaning

This interval changed the public meaning of `state_collapser`.

Before this interval, an engineer could reasonably misunderstand the package as
either:

- a toy RL package,
- a nascent RL framework,
- or a pile of research docs attached to a runtime.

After this interval, the intended public meaning is much clearer:

```text
state_collapser constructs quotient-tower structure over discovered transition
systems or known graphs, and exposes tower-aware decision/training/readout
surfaces.
```

That makes it:

- adjacent to RL frameworks,
- potentially usable beside Gymnasium/RLlib/SB3,
- upstream of HGraphML's graph-message-passing scaffold,
- and not yet a benchmark-supported speed-up package.

This clarity should help future work avoid two opposite mistakes:

- overbuilding a full RL framework prematurely,
- or underbuilding the quotient/fiber training spine until it becomes just an
  observation wrapper around ordinary learners.

## Known Open Issues And Next Actions

### P0: HGraphML Dependency Pin Is Now Stale

HGraphML still points to:

```text
state_collapser.git@v0.5.0
```

The clean `state_collapser` remote now retains only:

```text
v0.6.0
```

Immediate follow-up:

```text
Update HGraphML's dependency pin to v0.6.0 and rerun its CI/local validation.
```

This is the most concrete downstream preservation issue created by the public
history cleanup.

### P1: Public GitHub Release Should Be Recreated/Confirmed For v0.6.0

The git tag exists and points to the clean baseline. If a GitHub Release object
is desired, create it from the clean `v0.6.0` tag with release notes that avoid
speed-up claims and explain the research/pre-alpha posture.

### P1: CI Should Be Observed On Public Clean History

After the rewrite, verify GitHub Actions on:

- current `main`,
- `v0.6.0` release tag if release workflows are triggered,
- and any public clone/install workflows used by HGraphML.

### P1: Benchmarking Remains The Main Release Maturity Gap

The PO explicitly identified serious benchmarking as the remaining major
release need. Current benchmark smoke is useful but not enough for public
speed-up claims.

Needed benchmark work remains:

- larger discovered graphs,
- readout-disabled vs readout-enabled scaling curves,
- morphism-disabled vs morphism-enabled costs,
- schema-mode comparisons,
- environment-family comparisons,
- regression thresholds,
- artifact output.

### P1: PyPI Remains Deferred

The PO decided no PyPI release until serious benchmarking exists. The publish
workflow is manual-only, and README language should remain GitHub/source-first.

### P2: Old Local Branches Should Be Treated As Private

The private local branches are useful for provenance, but they should not be
pushed casually after public-history cleanup.

If public openness becomes stricter, consider moving the backup bundle to a
private archive location and pruning old local branches after confirming nothing
needed remains only there.

## Handoff Summary For Next Engineer

If you pick up `state_collapser` after this report:

1. Treat `v0.6.0` as the clean public research baseline.
2. Treat `017d9d4 [DRAFT]` as a later paper-draft commit on public `main`.
3. Do not rely on old public tags; they were intentionally deleted.
4. Do not push local private branches unless explicitly asked.
5. Update HGraphML to depend on `state_collapser` `v0.6.0`.
6. Preserve HGraphML compatibility when modifying partition-tower readouts.
7. Keep public language honest: research package, quotient-tower structure,
   no benchmark-supported speed-up claim yet.
8. Keep PyPI deferred until the benchmark story is much stronger.

## Closing Assessment

This was a release-positioning interval more than a feature interval. The
package did gain a serious fiber-conditioned training spine and HGraphML
compatibility documentation/tests, but the deeper change was that the project
became publicly legible:

```text
not RLlib
not Stable-Baselines3
not mature production RL
not benchmark-proven acceleration
but a real quotient-tower structural layer with RL and graph-ML applications
```

That is a much cleaner public posture than the project had one report ago.
