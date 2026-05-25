# Polished Outsider Package Blueprint

## Status

This document is the first blueprint for turning `state_collapser` into:

- a polished package that strangers can productively adopt

It is downstream of:

- [01_001_python_package_readiness_scoping.md]([state_collapser repository root]/docs/design/PyPl_readiness/01_001_python_package_readiness_scoping.md)

It is written under the authority of:

- [README.md]([state_collapser repository root]/README.md)
- [CONTRIBUTING.md]([state_collapser repository root]/CONTRIBUTING.md)
- [EVALUATION.md]([state_collapser repository root]/EVALUATION.md)
- [docs/design/model_train_surfaces/01_001_model_and_training_surface_architecture.md]([state_collapser repository root]/docs/design/model_train_surfaces/01_001_model_and_training_surface_architecture.md)
- [docs/design/model_train_surfaces/01_002_model_and_training_surface_blueprint.md]([state_collapser repository root]/docs/design/model_train_surfaces/01_002_model_and_training_surface_blueprint.md)

This is a blueprint.

It is not:

- a release checklist
- a PyPI upload procedure
- an implementation gameplan
- a benchmark report

Its job is to define exactly what the repository must become in order to count as:

- a serious outsider-usable Python package

and not merely:

- a strong internal research codebase with packaging scaffolding

## Purpose

The purpose of this blueprint is to answer the following question:

> What must `state_collapser` look like, structurally and behaviorally, before a capable outsider can install it, understand it, run it, and productively use it without needing to live inside the project’s design history?

This blueprint therefore focuses on:

- public API boundaries
- user workflows
- documentation architecture
- stable versus experimental labeling
- packaging verification
- evaluation and reproducibility surfaces
- outsider-facing repository behavior

It does **not** try to settle:

- every internal research direction
- every future algorithm family
- every long-term performance or tensor-backend hardening question

## Central Design Claim

The central claim of this blueprint is:

> `state_collapser` becomes productively adoptable by outsiders not when it stops being research-heavy, but when it exposes a small honest public surface, a few canonized workflows, a trustworthy documentation stack, and reproducible evaluation behavior.

This means the repo should optimize for:

- clarity
- honest scope
- stable entrypoints
- clean boundaries
- and repeatable outcomes

not for:

- maximal surface area
- total internal exposure
- or pretending unstable research machinery is already a mature user contract

## The Standard This Blueprint Targets

This blueprint is about the **higher** readiness standard identified in the scoping note.

It is **not** the standard:

- “someone can install it and experiment a bit”

It is the standard:

- “a technically capable outsider can productively adopt it without needing the maintainers’ whole design process in their head”

That is the standard the repository should now begin designing toward.

## Non-Negotiable Constraints

The following constraints are fixed by the repo’s present identity and must govern all work under this blueprint.

### 1. The package may remain pre-alpha

This blueprint does **not** require the package to present itself as stable or final.

It does require:

- that pre-alpha status be communicated honestly and cleanly

### 2. The repo may remain research-heavy

This blueprint does **not** require the design documents, mathematical scholarship, or experimental internal layers to disappear.

It does require:

- that outsiders not need those materials as the price of basic package use

### 3. Public API must be smaller than total internal code surface

The repo must not pretend that:

- every importable module is public

The package needs a smaller supported surface than the total set of internal modules.

### 4. Examples must serve users, not only the repo

The example suite may continue validating internal architecture.

But at least some examples must also function as:

- outsider-facing usage examples

### 5. The package must keep honest stability boundaries

The repo must not imply that:

- exploit/explore control
- training internals
- instrumentation surfaces
- or experimental examples

are equally stable if they are not.

### 6. The package must preserve `gymnasium`-first usability where appropriate

Nothing in this blueprint should push the package toward:

- replacing `gymnasium`

Instead, the package should remain compatible with a user understanding it as:

- RL environment surface plus tower/runtime machinery layered above it

## What “Polished Outsider Package” Means Here

For `state_collapser`, a polished outsider package means all of the following are true at once:

1. A newcomer can install the package from a clean environment and verify it works.
2. A newcomer can identify a small set of supported imports and workflows.
3. A newcomer can tell what is stable, what is experimental, and what is internal.
4. A newcomer can run at least one canonical example end to end.
5. A newcomer can inspect the package’s central outputs without guessing.
6. A newcomer can reproduce at least some evaluation claims.
7. A newcomer is not forced to reconstruct package meaning from continuity logs and design archaeology.

That is the standard this blueprint operationalizes.

## Blueprint Structure

This blueprint is divided into the major package-facing work areas that must be fixed:

1. public API boundary
2. workflow canonization
3. documentation architecture
4. stable/experimental/internal classification
5. installation and environment verification
6. artifact-level packaging checks
7. example-surface redesign for users
8. instrumentation as a user feature
9. evaluation and reproducibility
10. outsider-facing repository governance

## 1. Public API Boundary Blueprint

### The problem

Right now the repository has:

- real code
- real subsystems
- real examples
- real internal architecture

but it still does not present a sharply bounded supported user API.

That is the single largest barrier to productive outsider use.

### The required correction

The package must define three classes of surface:

1. public and supported
2. experimental but intentionally exposed
3. internal and not supported

### Public API law

The package must eventually make it obvious that a user should primarily begin from:

- `state_collapser`
- selected curated subpackages
- selected documented example packages

and not from:

- arbitrary deep internal module paths

### First public-surface target

The package should aim for a first explicit public boundary organized roughly around:

- top-level package metadata
- tower/runtime entry surfaces
- curated example entry surfaces
- selected training surfaces once they are ready
- selected instrumentation/evaluation surfaces once they are ready

### Internal-surface law

The package must feel free to keep many implementation modules internal, including areas like:

- deep runtime helpers
- research-transition modules
- intermediary implementation scaffolding
- incomplete training components

### Required deliverable

The repo must eventually contain one authoritative document that answers:

- what imports are public
- what imports are experimental
- what imports are internal

This can be:

- `docs/public_api.md`

or a successor document if that is cleaner.

But the classification must become explicit.

## 2. Supported Workflow Blueprint

### The problem

The repo currently contains many capabilities, but the outsider journey is not canonized.

The package needs a finite set of workflows that it explicitly supports.

### Canonical workflow law

The package should define two to four named workflows and treat them as:

- first-class package use cases

### Recommended first workflow set

The recommended first supported workflows are:

1. define or bind a hidden-graph RL problem and inspect tower construction
2. run tower-aware training on a canonical example
3. run exploit/explore control on the flagship exploit/explore example
4. run evaluation / tower-depth probing / instrumentation on a canonical example

### Workflow completeness law

Each supported workflow must have all of the following:

- one named entrypoint
- one recommended configuration path
- one documented output story
- one example invocation
- one statement of current stability

### Workflow honesty law

If a workflow is not yet ready to be supported, the package should say so plainly.

It must not imply support by:

- leaving random scripts or examples discoverable without a stability statement

## 3. Documentation Architecture Blueprint

### The problem

The repo has strong design documentation, but outsider-facing documentation is still not sufficiently separated from internal architecture scholarship.

### Required documentation stack

The package needs an explicit outsider-facing doc stack that is distinct from the design stack.

At minimum, the outsider stack should include:

- `README.md`
- `EVALUATION.md`
- `CONTRIBUTING.md`
- `docs/package_usage.md`
- `docs/public_api.md`

and likely needs additional consumer-facing docs for:

- quick start
- core concepts
- defining your own problem
- running training
- inspecting towers
- understanding what is experimental

### Documentation law

Outsider-facing docs must not assume the reader has followed:

- `docs/design/`
- `docs/engineer_continuity/`
- or implementation logs

Those may remain available, but they are not allowed to be the basic path to use.

### Documentation layering

The doc stack should separate:

1. what the package is
2. how to install and run it
3. how to use it
4. how to evaluate it
5. what is stable or unstable
6. why the mathematical model exists

This layered structure matters because outsiders need:

- use guidance first

not:

- proof-of-origin first

### Required “trustworthy honesty” doc

The package should contain one blunt status-style document or section that says:

- what works now
- what is experimental
- what examples are authoritative
- what claims are conceptual
- what claims are empirically validated

This can live in:

- `README.md`
- `docs/package_usage.md`
- or a dedicated status-oriented doc

But it must exist.

## 4. Stable / Experimental / Internal Classification Blueprint

### The problem

The repo currently has a lot of real code whose maturity is uneven.

Without a formal classification, outsiders cannot know what to trust.

### Classification law

Every major user-visible subsystem should be classifiable as one of:

- supported
- experimental
- internal

### First required classification targets

The first areas that must be explicitly classified are:

- `plate_support_env`
- `rl_counterpoint_v3`
- the broader example family
- exploit/explore control
- `state_collapser.training`
- instrumentation surfaces
- any public adapters

### Documentation law

This classification should not be hidden only in code comments.

It must appear in package-facing docs.

### Naming law

Where useful, naming and placement should reinforce the distinction.

For instance:

- internal helpers should not look like polished top-level APIs
- experimental surfaces may need explicit labeling in docs and examples

## 5. Installation And Environment Verification Blueprint

### The problem

Even a strong repo can feel unprofessional if installation is ambiguous or noisy.

### Installation law

The package must make installation:

- boring
- short
- testable

### Required install story

The package must clearly separate:

- base install
- RL extras
- ML extras
- dev install

and explain:

- which workflows require which extras

### Required verification story

The outsider must be able to run:

1. one command that confirms the package imports
2. one command that runs a basic example
3. one command that runs a basic evaluation or probe

without reading contributor-only docs

### Python-version law

Supported Python versions must be:

- explicit in metadata
- reflected in docs
- and validated in CI

## 6. Artifact-Level Packaging Check Blueprint

### The problem

A repo can pass tests locally and still ship a broken distribution artifact.

### Artifact law

The package must verify not just:

- source-tree correctness

but also:

- distribution-artifact correctness

### Required CI checks

The repo should eventually include CI checks for:

- wheel build
- sdist build
- install from wheel
- install from sdist if practical
- import from installed artifact
- smoke example from installed artifact

### Release law

No release should be considered professionally ready unless the artifact-level checks pass.

## 7. Example Surface Blueprint

### The problem

The current examples are strong as validation assets, but only some of them are currently shaped as outsider-facing demonstrations.

### Example law

The example suite must explicitly split into two roles:

1. reference user examples
2. internal evaluation or architectural examples

Some examples may play both roles, but the repo must say which is which.

### Reference example law

The repo should maintain a short list of examples that are clearly recommended to outsiders first.

A plausible first list is:

- `plate_support_env`
- `rl_counterpoint_v3`

because:

- one exercises the flagship constrained robotics-like evaluation path
- the other exercises the new training-surface migration path

### Example usage law

Reference examples should be documented in a user-facing style:

- what to import
- what to construct
- what to run
- what output to inspect

### Internal example law

The broader evaluation family may remain partly evaluation-oriented rather than tutorial-oriented.

But the README and evaluation docs must explain that distinction.

## 8. Instrumentation As A User Feature Blueprint

### The problem

Instrumentation is currently more potential than polished package feature.

### Instrumentation law

Instrumentation should become part of the outsider-facing experience, not just internal diagnostics.

### First instrumentation targets

The first user-facing instrumentation features should likely include:

- tower depth over time
- contraction behavior summaries
- path-space restriction metrics
- active-tier traces where relevant

### Packaging law

Instrumentation should be invocable in a way that feels like:

- a package capability

not:

- hidden engineering residue

### Interpretation law

Instrumentation docs must explain:

- what the metric means
- what it does not mean
- and how it relates to actual learning outcomes

This is especially important in this repository because:

- tower depth alone is not the whole story

## 9. Evaluation And Reproducibility Blueprint

### The problem

Outsiders cannot productively trust a research package if they cannot reproduce its basic claims or reference behaviors.

### Evaluation law

The package must define at least a small canonical evaluation surface that is:

- repeatable
- documented
- and interpretable

### First canonical evaluation set

The package should eventually treat the following as canonical or semi-canonical evaluation surfaces:

- direct tower-aware training on a flagship example
- exploit/explore control on the flagship exploit/explore example
- tower-depth probing on selected examples
- at least one benchmark-like comparison protocol

### Reproducibility law

Where possible, the package should document:

- seeds
- expected outputs
- expected depth or behavior signatures
- known limitations

### Claim-tier law

Evaluation docs should distinguish between:

- structural/runtime evidence
- behavioral control evidence
- learning-performance evidence

This is especially important for a repo like `state_collapser`, where those are related but not identical.

## 10. Outsider-Facing Repository Governance Blueprint

### The problem

A real outsider-usable package needs repo behavior that can absorb issue and PR traffic from strangers.

### Governance law

The repo should eventually provide enough guidance that an outsider knows:

- how to report a bug
- what a good feature request looks like
- what kind of contribution is welcome
- what level of support to expect

### First governance targets

The repo should eventually have:

- issue templates or equivalent guidance
- clearer bug-report expectations
- clearer feature-request expectations
- contribution-scope guidance

This does not need to be elaborate.

It does need to be deliberate.

## Relationship To The Current Training-Surface Work

The package-readiness work must not ignore the fact that:

- `state_collapser.training` now exists

But it must also not overstate its maturity.

So the outsider-package story should treat the training package as:

- a real internal reusable layer
- an important architectural milestone
- not yet a finalized public ML API

This is one of the clearest examples of the stable/experimental/internal classification problem.

## Relationship To `gymnasium`

This blueprint remains fully compatible with a `gymnasium`-first package posture.

That means the outsider story should continue to feel like:

- environment surface
- runtime / tower augmentation
- training and evaluation surfaces above that

not:

- a package that replaces the normal RL environment contract

This is a strength, not a weakness.

It gives outsiders a familiar anchor.

## What This Blueprint Explicitly Defers

The following are important, but they are not the main first-scope subject of this blueprint:

- deep tensor-backend hardening
- large-scale training framework maturity
- full vectorized rollout semantics
- every future algorithm family
- every future instrumentation subsystem

These can matter later.

But outsider package polish is currently blocked more by:

- API discipline
- workflow clarity
- docs
- evaluation reproducibility
- stability labeling

than by those deeper backend questions.

## Acceptance Standard

This blueprint will count as materially fulfilled only when all of the following are true:

1. the package has a documented small supported public surface
2. stable / experimental / internal distinctions are explicit
3. two to four canonical workflows are named and documented
4. outsider-facing docs are sufficient without design-history dependence
5. installation and verification are short and reliable
6. artifact-level packaging checks exist
7. at least some examples clearly teach package use
8. instrumentation and evaluation are documented as real user features
9. reproducible example/evaluation guidance exists
10. outsider-facing repository guidance exists for issue and contribution flow

If the repo instead still depends on:

- design archaeology
- implicit API boundaries
- example-local folklore
- and undocumented stability assumptions

then this blueprint has not been fulfilled.

## Next Document

The next document after this blueprint should be:

- an implementation gameplan in `Phase.Stage.Action` form

That gameplan should decide:

- execution order
- first concrete package-facing doc targets
- first API classification targets
- first workflow canonization targets
- first packaging CI targets
- and which readiness items are first-scope versus deliberately deferred

## Closing claim

The project is already beyond the question:

- “is there a package here at all?”

This blueprint addresses the harder question:

- “can a technically capable outsider use the package productively without needing to absorb the whole internal design culture first?”

That is now the correct package-readiness target.
