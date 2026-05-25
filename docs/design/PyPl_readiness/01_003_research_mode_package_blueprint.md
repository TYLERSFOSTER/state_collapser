# Research-Mode Package Blueprint

## Status

This document is the companion blueprint for the lighter package-readiness route:

- the route that still keeps `state_collapser` explicitly in research mode

It is downstream of:

- [01_001_python_package_readiness_scoping.md]([state_collapser repository root]/docs/design/PyPl_readiness/01_001_python_package_readiness_scoping.md)

It is written alongside:

- [01_002_polished_outsider_package_blueprint.md]([state_collapser repository root]/docs/design/PyPl_readiness/01_002_polished_outsider_package_blueprint.md)

It is written under the authority of:

- [README.md]([state_collapser repository root]/README.md)
- [CONTRIBUTING.md]([state_collapser repository root]/CONTRIBUTING.md)
- [EVALUATION.md]([state_collapser repository root]/EVALUATION.md)
- [docs/design/module_design_desiderata.md]([state_collapser repository root]/docs/design/module_design_desiderata.md)
- [docs/design/model_train_surfaces/01_001_model_and_training_surface_architecture.md]([state_collapser repository root]/docs/design/model_train_surfaces/01_001_model_and_training_surface_architecture.md)

This is a blueprint.

It is not:

- a release checklist
- a “production hardening” plan
- a claim that the repo is already ready for broad outsider adoption

Its job is to define the lighter, more honest route in which the package becomes:

- installable
- legible
- reproducible
- and productively explorable by technically strong outsiders

while still remaining:

- clearly research-mode

## Purpose

The purpose of this blueprint is to answer:

> What package-readiness work should `state_collapser` do if the goal is not yet “polished outsider package,” but rather “serious research package that outsiders can install, inspect, run, and understand without false promises of maturity”?

This route is deliberately lighter than the “polished package strangers can productively adopt” blueprint.

It targets:

- clarity
- reproducibility
- installability
- honest boundaries
- and research-facing usability

It does **not** target:

- strong public API guarantees
- broad workflow canonization
- deep packaging hardening
- or the level of UX polish expected from a mature external-user library

## Central Design Claim

The central claim of this blueprint is:

> `state_collapser` can become a strong research-mode Python package before it becomes a polished outsider package, provided it becomes easy to install, truthful to read, reproducible to run, and explicit about what remains unstable.

This means the repo should optimize for:

- research honesty
- runnable examples
- reproducible evaluation
- clear entrypoints
- and explicit instability labeling

It should **not** yet optimize primarily for:

- minimizing every internal exposure
- guaranteeing a settled public API
- or hiding all evolving research machinery behind polished abstraction walls

## The Standard This Blueprint Targets

This blueprint is for the lower of the two package-readiness standards described in the scoping note.

It is stronger than:

- “works on the maintainer’s machine”

and stronger than:

- “someone can maybe install it if they are persistent”

But it is weaker than:

- “strangers can productively adopt it without much hand-holding”

The intended standard is:

- a technically capable outsider can install the package, run the canonical examples, inspect the current architecture, and reproduce some central behaviors without being misled into thinking the repo is already a polished stable library

That is the research-mode target.

## Non-Negotiable Constraints

### 1. The repo must remain honest about pre-alpha status

This blueprint does not try to hide that the package is:

- pre-alpha
- evolving
- and still under architectural development

### 2. Design documents remain part of the repo’s identity

Unlike the polished outsider route, this research-mode route does not require the design stack to recede as far into the background.

The design documents may remain prominent.

But outsiders still need a usable on-ramp.

### 3. Public API may remain narrow and somewhat provisional

This blueprint does not require the package to fully freeze a mature public API.

It does require:

- enough API clarity that a newcomer can tell what they should start from

### 4. Examples may remain partly architecture-facing

This route does not require every example to become a tutorial-grade user example.

It does require:

- that at least some examples be clearly identified as the recommended starting points

### 5. Internal research machinery may remain visible

This route accepts that:

- the repo still has visible design evolution
- the internal machinery is still discoverable
- the mathematical architecture remains part of the project’s surface

But visibility must not become confusion.

## What “Research-Mode Package” Means Here

For `state_collapser`, a research-mode package means all of the following are true:

1. A technically capable outsider can install it from a clean environment.
2. A technically capable outsider can identify the current flagship examples.
3. A technically capable outsider can run those examples and inspect their outputs.
4. A technically capable outsider can understand what parts are experimental.
5. A technically capable outsider can find the mathematical and architectural documents when they want them.
6. A technically capable outsider can reproduce at least some core structural behaviors.
7. The package does not pretend to be more stable or polished than it really is.

That is the target standard here.

## Blueprint Structure

This blueprint organizes the research-mode route into the following work areas:

1. installability and environment clarity
2. honest root-document stack
3. canonical research-entry examples
4. evaluation and reproducibility
5. current-surface classification
6. research-facing API clarity
7. training-surface honesty
8. issue/reporting hygiene

## 1. Installability And Environment Clarity Blueprint

### The problem

Even for research users, the package must be straightforward to install and verify.

If installation is ambiguous, the repo stops being a package and falls back into “interesting codebase.”

### Research-mode installation law

The package must have:

- a clean install story
- a clean extras story
- a simple verification story

even if the overall repo remains pre-alpha.

### Required install story

The package should clearly distinguish:

- base install
- RL extras
- ML extras
- dev install

and document:

- which examples or workflows require which extras

### Required verification story

A newcomer should be able to do all three of the following with short documented commands:

1. verify the package imports
2. run one canonical training example
3. run one canonical probe/evaluation example

That is enough for research-mode credibility.

## 2. Honest Root-Document Stack Blueprint

### The problem

The repo now has several good root documents, but they must work together as a coherent research-mode entry stack.

### Root-doc law

The root document stack should make the package legible in this order:

1. what the package is
2. why it exists
3. how to install it
4. how to run something real
5. how to evaluate it
6. what is experimental
7. where to find deeper design authority

### Required root stack

The following should function together as the primary research-mode on-ramp:

- `README.md`
- `EVALUATION.md`
- `CONTRIBUTING.md`
- selected package-usage docs

### Honesty law

The README must not imply:

- broad package stability
- a hardened public ML interface
- or general-purpose production maturity

It should instead clearly say:

- this is a pre-alpha research package
- here is what you can actually run
- here is what is architecturally important

## 3. Canonical Research-Entry Example Blueprint

### The problem

The repo now has a broader example family, which is good, but a research-mode user still needs to know:

- which examples should I start with?

### Canonical-example law

The package should clearly identify a small number of canonical research-entry examples.

### Recommended entry examples

The first recommended entry examples should likely be:

- `plate_support_env`
- `rl_counterpoint_v3`

because together they cover:

- the flagship constrained geometric example
- the newer training-surface migration path

### Broader example-family law

The broader example family can remain evaluation-oriented.

But it should be documented as:

- extension or comparison examples

not left to feel like all examples are equally central.

### Example-command law

For the canonical research-entry examples, the docs should provide:

- one recommended import path
- one recommended run command
- one description of expected output

## 4. Evaluation And Reproducibility Blueprint

### The problem

Research-mode users do not need a full benchmark program immediately.

But they do need:

- repeatable structural and behavioral evidence

### Research-evaluation law

The package must provide enough reproducibility that a technically strong user can verify:

- the examples run
- the tower grows
- the runtime is doing something structurally nontrivial

### First required reproducibility surfaces

The first required surfaces are:

- canonical training examples
- canonical probe utility
- documented seeds where appropriate
- documented expected outcome signatures

### Probe law

The tower-depth probe should be treated as:

- a first-class research-mode evaluation tool

because it gives outsiders a concrete way to inspect dynamic tower materialization without first mastering every training path.

### Evaluation-claim law

Evaluation docs should distinguish between:

- “the tower gets deep”
- “the controller moves across tiers”
- “learning actually improves”

These are related, but not interchangeable.

Research-mode honesty requires that distinction.

## 5. Current-Surface Classification Blueprint

### The problem

Even in research mode, the repo needs clearer maturity signaling.

### Classification law

The package should explicitly describe major surfaces as something like:

- current flagship
- experimental
- internal
- reference only

This can be lighter than the full stable/experimental/internal taxonomy of the polished-package route.

But some classification must exist.

### First classification targets

The first things that should be classified in docs are:

- `plate_support_env`
- `rl_counterpoint_v3`
- exploit/explore control
- `state_collapser.training`
- the broader example family
- instrumentation

### Research-mode tone law

The language should be blunt and practical, not legalistic.

For example:

- “This is the flagship example right now.”
- “This path is runnable, but still experimental.”
- “This package is real, but internal-first.”

That tone is more useful for a research package than pseudo-corporate stability language.

## 6. Research-Facing API Clarity Blueprint

### The problem

This route does not require a fully hardened public API, but it still requires that users know where to begin.

### API-clarity law

The package should make it easy to answer:

- what do I import first?
- what examples are meant to be used directly?
- what should I treat as internal?

### Minimum viable API clarity

For research-mode readiness, the package does not need:

- a fully frozen top-level public API

It does need:

- a short list of recommended import surfaces
- a short statement that deeper internals remain unstable

### Documentation law

This may be satisfied initially by:

- `README.md`
- `docs/public_api.md`
- and clear `__init__.py` curation in the example packages

without first requiring the total API freeze expected in the polished-package route.

## 7. Training-Surface Honesty Blueprint

### The problem

The repo now has a real internal training package.

That is a major step forward.

But it would be misleading to present it already as:

- the stable outsider-facing ML API

### Training-surface law

The package should describe `state_collapser.training` as:

- a real internal reusable training surface
- a meaningful architectural milestone
- not yet a hardened public API

### Why this matters

This is the right research-mode stance because it:

- gives credit to the real implementation work
- avoids underselling actual progress
- avoids overselling maturity

### Example-law interaction

The fact that `rl_counterpoint_v3` already uses the new training surfaces should be documented, because it proves:

- the package is not purely abstract

But that proof should not be confused with:

- final API settlement

## 8. Issue And Reporting Hygiene Blueprint

### The problem

Even research-mode packages get issue traffic once they become usable enough to try.

### Minimum governance law

This route does not require a full governance apparatus.

It does require enough repo guidance that outsiders know:

- how to report a bug
- what kind of question is reasonable
- what level of support to expect

### Required minimal outcome

The package should have at least:

- clear issue destination
- contribution guidance
- and some statement of support expectations

This is already partly present through root docs, but should become more explicit over time.

## Relationship To The Polished Outsider Package Blueprint

This blueprint and:

- [01_002_polished_outsider_package_blueprint.md]([state_collapser repository root]/docs/design/PyPl_readiness/01_002_polished_outsider_package_blueprint.md)

are complementary, not contradictory.

The difference is one of:

- target standard
- scope
- and urgency

The polished-package blueprint asks:

- what must the repo become for broad outsider adoption?

This research-mode blueprint asks:

- what must the repo become so that strong outsiders can already use it honestly and productively in research mode?

That lighter route is likely the more realistic near-term target.

## What This Blueprint Explicitly Defers

The following are still important, but not required to fulfill the research-mode route:

- full public API freeze
- artifact-perfect packaging hardening
- strong workflow canonization across every subsystem
- mature instrumentation UX
- large benchmark suite
- full train/eval-mode and tensor-backend hardening

These belong more to the stronger polished-package route.

## Acceptance Standard

This blueprint counts as materially fulfilled only if all of the following are true:

1. the package install story is clear and documented
2. the root docs form a coherent research-mode on-ramp
3. the canonical starting examples are explicitly named
4. at least one training example and one probe/evaluation example are easy to run
5. the current major surfaces are honestly classified
6. the package’s pre-alpha research status is explicit
7. the evaluation guidance supports at least limited reproducibility
8. the current training-surface layer is documented honestly as real but internal-first

If the repo instead remains in a state where:

- only insiders know what to run
- examples are not prioritized
- installation is unclear
- the README overpromises stability
- and the evaluation story is mostly implied

then this blueprint has not been fulfilled.

## Next Document

The next document after this blueprint should be:

- an implementation gameplan in `Phase.Stage.Action` form

That gameplan should focus on:

- the minimum high-value work needed to make the repo a strong research-mode package first

rather than prematurely aiming at the full polished-package target.

## Closing claim

The repo does not need to pretend it is already a mature outsider library.

What it does need is to become:

- installable
- legible
- reproducible
- and honestly bounded

while still visibly remaining:

- a research-mode package

That is the right lighter route for `state_collapser` right now.
