# Research-Mode Package Implementation Gameplan

## Status

This document is the implementation-law gameplan for the research-mode package-readiness route.

It is downstream of:

- [01_001_python_package_readiness_scoping.md]([state_collapser repository root]/docs/design/PyPl_readiness/01_001_python_package_readiness_scoping.md)
- [01_003_research_mode_package_blueprint.md]([state_collapser repository root]/docs/design/PyPl_readiness/01_003_research_mode_package_blueprint.md)

It is written alongside:

- [01_002_polished_outsider_package_blueprint.md]([state_collapser repository root]/docs/design/PyPl_readiness/01_002_polished_outsider_package_blueprint.md)

It is written under the authority of:

- [README.md]([state_collapser repository root]/README.md)
- [EVALUATION.md]([state_collapser repository root]/EVALUATION.md)
- [CONTRIBUTING.md]([state_collapser repository root]/CONTRIBUTING.md)
- [docs/prime_directive/prime_directive.md]([state_collapser repository root]/docs/prime_directive/prime_directive.md)
- [docs/prime_directive/git_practices.md]([state_collapser repository root]/docs/prime_directive/git_practices.md)

This document is a `Phase.Stage.Action` implementation gameplan.

It is not:

- a release checklist
- a benchmark protocol
- a polished-public-package implementation plan

Its job is to define exactly how the repository should be upgraded into:

- a strong research-mode Python package

without pretending that the package is already:

- a broadly adoptable polished outsider library

## Execution Contract

This gameplan is governed by the following execution laws.

### 1. Branch discipline is mandatory

Before implementation begins:

- create or switch to a dedicated implementation branch
- perform the work there
- merge back only after validation is complete

This is fixed by:

- [docs/prime_directive/git_practices.md]([state_collapser repository root]/docs/prime_directive/git_practices.md)

### 2. Research-mode honesty is mandatory

No implementation step may:

- imply the package is already stable for broad outsider adoption
- present experimental surfaces as settled public APIs
- hide pre-alpha status behind polished-sounding but untrue wording

### 3. The design stack remains visible, but not required for basic use

This route does not require:

- de-emphasizing the design and mathematical docs entirely

It does require:

- that a newcomer can install and run core examples without first reading them

### 4. README, evaluation, and usage docs are first-class package surfaces

For this work, the documentation is not secondary polish.

It is part of the implementation surface.

### 5. Canonical example prioritization is mandatory

By the end of execution, a newcomer must be able to tell:

- which examples to start with
- which examples are broader evaluation-family members

### 6. The route is deliberately lighter than the polished outsider package route

This implementation must not silently escalate into:

- full public API freeze
- full packaging-artifact hardening
- broad workflow canonization across every subsystem

Those belong to the stronger package-readiness track.

### 7. Every change must improve real newcomer legibility

No step should be executed merely because it feels package-like in the abstract.

Each step must materially improve one or more of:

- installability
- runnability
- discoverability
- honesty
- reproducibility

### 8. Stop conditions are real

If implementation reveals that:

- the README, EVALUATION, and usage stack cannot be made coherent without reopening major architecture
- canonical examples cannot be named honestly without a new owner decision
- the current example and training surfaces are too unstable to classify even at a research-mode level

then execution must stop for design clarification rather than silently improvising policy.

## Canonical Target Files

The canonical target files for this work are:

- `README.md`
- `EVALUATION.md`
- `CONTRIBUTING.md` only if a small alignment fix is needed
- `docs/package_usage.md`
- `docs/public_api.md`
- possibly a new research-status or experimentation guidance doc if needed
- selected example-package `__init__.py` files only if curation is needed for clarity
- selected testing or CI config files only if the gameplan reaches the lightweight verification stage

The canonical implementation log target is:

- `docs/design/PyPl_readiness/01_005_research_mode_package_implementation_log.md`

The canonical validation surfaces are:

- root docs consistency
- documented commands that actually run
- targeted package-import and example smoke checks

## Fixed First-Scope Decisions

The following decisions are already fixed by this gameplan and must not be reopened casually during execution.

### 1. This is not the full polished-outsider-package route

The current target is:

- strong research-mode usability

not:

- full polished outsider adoption

### 2. Canonical starting examples must be explicit

The first canonical research-entry examples are expected to be:

- `plate_support_env`
- `rl_counterpoint_v3`

unless implementation exposes a real contradiction.

### 3. The tower-depth probe is part of the research-mode evaluation surface

The repo must continue to surface:

- `tower_depth_probe`

as a real research-facing utility.

### 4. `state_collapser.training` must be described as internal-first

The package should acknowledge:

- the training package is real
- it is reusable
- it is an architectural milestone

while also clearly stating:

- it is not yet a finalized public ML API

### 5. Stability labeling may remain lightweight, but it must exist

This route does not require a full formal maturity taxonomy.

It does require clear language like:

- flagship
- experimental
- internal-first
- evaluation-oriented

### 6. The root-document stack is part of the product surface

This implementation is not done if:

- docs remain internally accurate but newcomer-hostile

The docs are part of the work itself.

## Phase 1. Branch, Log, And Current-State Audit

### Stage 1.1. Branch Setup

#### Action 1.1.1

Create or switch to a dedicated implementation branch before touching files.

#### Action 1.1.2

Record the branch name in the implementation log.

### Stage 1.2. Implementation Log Creation

#### Action 1.2.1

Create:

- `docs/design/PyPl_readiness/01_005_research_mode_package_implementation_log.md`

#### Action 1.2.2

The log must record:

- branch name
- starting repo state
- files changed
- validation commands
- design surprises
- any cases where a more-polished package behavior was intentionally deferred

### Stage 1.3. Current-Surface Audit

#### Action 1.3.1

Audit the current root documentation stack:

- `README.md`
- `EVALUATION.md`
- `CONTRIBUTING.md`
- `docs/package_usage.md`
- `docs/public_api.md`

#### Action 1.3.2

Audit the current package entry examples:

- `plate_support_env`
- `rl_counterpoint_v3`
- tower-depth probe

#### Action 1.3.3

Audit the current install and verification story from docs only.

The audit question is:

- can a technically strong outsider tell what to install and what to run?

#### Action 1.3.4

Record the audit results in the implementation log before editing documentation.

## Phase 2. Root-Document Stack Coherence

### Stage 2.1. README Role Clarification

#### Action 2.1.1

Re-read `README.md` as the primary research-mode landing page.

#### Action 2.1.2

Ensure the README clearly communicates:

- what the package is
- why it exists
- that it is pre-alpha
- what the canonical starting examples are
- what the first real training/evaluation entrypoints are
- where deeper docs live

#### Action 2.1.3

Ensure the README does **not** imply:

- broad public API stability
- polished outsider support
- completed benchmark maturity

### Stage 2.2. EVALUATION Role Clarification

#### Action 2.2.1

Re-read `EVALUATION.md` as the research-mode evaluation companion doc.

#### Action 2.2.2

Ensure it clearly explains:

- what counts as evaluation in this repo
- what canonical evaluation surfaces are
- what structural evidence versus learning-performance evidence means
- how to run the probe and the canonical examples

#### Action 2.2.3

Ensure it explains limitations honestly, especially around:

- tower depth not being the whole story
- examples having different maturity levels

### Stage 2.3. CONTRIBUTING Role Clarification

#### Action 2.3.1

Re-read `CONTRIBUTING.md` only for alignment with the research-mode package story.

#### Action 2.3.2

Do not rewrite it unless a real mismatch is found.

#### Action 2.3.3

If a mismatch exists, make only the minimal correction needed so contribution expectations do not contradict the research-mode stance.

### Stage 2.4. Package Usage / Public API Doc Role Clarification

#### Action 2.4.1

Read:

- `docs/package_usage.md`
- `docs/public_api.md`

as research-mode newcomer docs rather than internal design notes.

#### Action 2.4.2

Identify whether they currently answer:

- what do I import?
- what do I run first?
- what should I not treat as stable?

#### Action 2.4.3

Record any missing newcomer-critical sections before editing.

## Phase 3. Canonical Research-Entry Example Definition

### Stage 3.1. Flagship Example Classification

#### Action 3.1.1

Explicitly classify:

- `plate_support_env`

as the flagship constrained geometric example if that remains honest after audit.

#### Action 3.1.2

Explicitly classify:

- `rl_counterpoint_v3`

as the flagship training-surface migration example if that remains honest after audit.

#### Action 3.1.3

If either classification would be misleading, stop and record why before choosing a replacement.

### Stage 3.2. Broader Example-Family Classification

#### Action 3.2.1

Classify the broader example family as something like:

- evaluation-oriented
- comparison-oriented
- extension examples

#### Action 3.2.2

Ensure docs do not leave the false impression that every example is equally central for a newcomer.

### Stage 3.3. Canonical Command Surface

#### Action 3.3.1

For the two canonical research-entry examples, define the one recommended command or code path a newcomer should use first.

#### Action 3.3.2

For the probe utility, define the one recommended command a newcomer should use first.

#### Action 3.3.3

Ensure those commands are the ones actually placed in newcomer-facing docs.

## Phase 4. Install Story And Verification Story

### Stage 4.1. Install Story Audit

#### Action 4.1.1

Audit the install instructions in the current docs for:

- base install
- dev install
- RL extras
- ML extras

#### Action 4.1.2

Verify whether the docs explain which workflows require which extras.

#### Action 4.1.3

If not, document the missing mapping and correct it.

### Stage 4.2. Verification Story Construction

#### Action 4.2.1

Define a simple three-step verification story for research-mode newcomers:

1. import check
2. one canonical training run
3. one canonical evaluation/probe run

#### Action 4.2.2

Ensure these are short enough to belong in the root docs.

#### Action 4.2.3

Ensure the commands are actually runnable in the current repo state.

### Stage 4.3. Verification Placement

#### Action 4.3.1

Place the install story where a newcomer expects it:

- primarily README
- secondarily deeper usage docs

#### Action 4.3.2

Place the fuller verification and interpretation story where it belongs:

- package usage doc
- evaluation doc

## Phase 5. Stability And Maturity Language

### Stage 5.1. Research-Mode Classification Vocabulary

#### Action 5.1.1

Choose and apply a lightweight classification vocabulary for current docs, such as:

- flagship
- experimental
- internal-first
- evaluation-oriented

#### Action 5.1.2

Ensure the vocabulary is used consistently enough to be meaningful.

### Stage 5.2. Subsystem Classification Pass

#### Action 5.2.1

Apply that vocabulary to the major newcomer-visible surfaces:

- `plate_support_env`
- `rl_counterpoint_v3`
- exploit/explore path
- `state_collapser.training`
- broader example family
- instrumentation

#### Action 5.2.2

Do not overformalize.

This is a research-mode package, so the goal is:

- newcomer clarity

not:

- bureaucratic taxonomy

### Stage 5.3. Public Versus Internal Hints

#### Action 5.3.1

Ensure the docs distinguish between:

- recommended starting surfaces
- deeper internal surfaces

#### Action 5.3.2

Do this without pretending the package has already completed a polished public API freeze.

## Phase 6. Training-Surface Honesty Pass

### Stage 6.1. Training Package Description

#### Action 6.1.1

Re-read current docs anywhere `state_collapser.training` is mentioned.

#### Action 6.1.2

Ensure the package is described as:

- real
- reusable
- important
- internal-first

#### Action 6.1.3

Ensure it is **not** described as:

- the settled outsider-facing ML API

### Stage 6.2. Migrated Example Integration Story

#### Action 6.2.1

Ensure the docs explain why `rl_counterpoint_v3` matters:

- it is the first real migration target onto the new training surfaces

#### Action 6.2.2

Ensure the docs do not overclaim this as meaning:

- all training surfaces are now stable

## Phase 7. Evaluation And Reproducibility Pass

### Stage 7.1. Probe-Centric Reproducibility

#### Action 7.1.1

Ensure `tower_depth_probe` is documented as:

- a first-class research-mode evaluation tool

#### Action 7.1.2

Ensure docs explain what it demonstrates and what it does not.

### Stage 7.2. Canonical Reproducibility Hooks

#### Action 7.2.1

For each canonical research-entry workflow, ensure the docs provide:

- a seed where appropriate
- a short expected behavior description
- a pointer to what output to inspect

#### Action 7.2.2

Do not promise exact scientific claims if the current repo state does not yet support them.

### Stage 7.3. Evaluation-Honesty Pass

#### Action 7.3.1

Ensure evaluation docs distinguish between:

- structural tower evidence
- controller behavior evidence
- training-performance evidence

#### Action 7.3.2

If current docs blur these together, correct them.

## Phase 8. Research-Facing API Clarity

### Stage 8.1. Import-Surface Pass

#### Action 8.1.1

Ensure newcomer-facing docs make it clear where to begin importing from:

- top-level package
- canonical example packages
- probe utility path

#### Action 8.1.2

Do not promise a larger public API than the repo can currently support honestly.

### Stage 8.2. Curated Example Package Surface Check

#### Action 8.2.1

Inspect the `__init__.py` surfaces of the canonical research-entry example packages.

#### Action 8.2.2

If a small curation improvement would materially improve clarity, make it.

#### Action 8.2.3

Do not expand example exports merely to appear polished.

Only do it if it makes the research-mode entrypath genuinely clearer.

## Phase 9. Minimal Governance Hygiene

### Stage 9.1. Issue And Support Clarity

#### Action 9.1.1

Ensure the root docs make it clear:

- where bugs should be reported
- where contributions should start
- what level of maturity/support the repo currently offers

#### Action 9.1.2

Do not create a large governance apparatus unless it is truly needed in this scope.

### Stage 9.2. Contribution-Boundary Honesty

#### Action 9.2.1

Ensure contribution docs and root docs do not give contradictory signals about:

- maturity
- package stability
- or expected contribution style

## Phase 10. Lightweight Verification And Validation

### Stage 10.1. Documentation-Command Verification

#### Action 10.1.1

Run the key newcomer-facing commands documented after the edits, including:

- import check
- canonical training example
- canonical probe example

#### Action 10.1.2

If a documented command fails, either:

- fix the command
- fix the doc
- or fix the underlying package issue

before completion.

### Stage 10.2. Focused Package Validation

#### Action 10.2.1

Run the focused validation necessary to ensure the research-mode doc and example changes did not introduce regressions in:

- canonical examples
- probe utility
- relevant usage surfaces

#### Action 10.2.2

Run lint/type/doc consistency checks for touched files where practical.

### Stage 10.3. Completion Check

#### Action 10.3.1

Confirm that the package now satisfies the research-mode acceptance standard:

- install story is clear
- root docs are coherent
- canonical entry examples are explicit
- training and probe entry commands are documented and runnable
- maturity language is honest
- reproducibility guidance exists at a lightweight but real level

## Phase 11. Closeout

### Stage 11.1. Implementation Log Finalization

#### Action 11.1.1

Update:

- `docs/design/PyPl_readiness/01_005_research_mode_package_implementation_log.md`

with:

- files changed
- classifications chosen
- commands verified
- validation performed
- deferred stronger-package work

### Stage 11.2. Merge Readiness

#### Action 11.2.1

Only after:

- docs are coherent
- newcomer commands were verified
- the implementation log is complete

should the work be considered ready for merge.

## Completion Standard

This gameplan counts as successfully executed only if the repository now behaves like:

- a serious research-mode Python package

rather than merely:

- a strong but insider-dependent research codebase

Concretely, completion requires that:

- installation is clear
- newcomer entry examples are explicit
- the root doc stack is coherent
- the probe utility is part of the visible research-mode surface
- `state_collapser.training` is described honestly
- current stability is clearly but lightly classified
- documented newcomer commands actually run

If the implementation instead leaves the repo in a state where:

- outsiders still have to guess what to run
- docs still overpromise
- or the package still only makes sense through design-history reconstruction

then execution has failed.
