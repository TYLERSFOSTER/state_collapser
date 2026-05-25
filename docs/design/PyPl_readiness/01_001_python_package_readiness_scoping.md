# Python Package Readiness Scoping

## Status

This document is the initial scoping note for the work of turning `state_collapser` into a Python package that other people can actually use.

It is intentionally broad and strategic.

It is not yet:

- a blueprint
- a gameplan
- a packaging checklist
- or a PyPI release procedure

Its purpose is to establish the current package-readiness picture and to scope the major work categories that remain.

## Two Different Meanings Of "A Python Package Other People Can Use"

There are really two different standards hiding inside that phrase:

1. installable and professionally consumable
2. stable enough that strangers can rely on it without a lot of hand-holding

The project is already fairly far along on the first.

It is only partway along on the second.

That distinction matters, because:

- the repo already looks like a serious pre-alpha Python package
- but it does not yet fully offer a polished public Python package experience

## Where The Repo Is Already Strong

The project already has a lot of the difficult package scaffolding in place:

- `pyproject.toml`
- versioning
- tags and releases
- a real `README.md`
- a real `CONTRIBUTING.md`
- a meaningful test suite
- lint and typecheck discipline
- installable source layout under `src/`
- a small but real public package surface
- example subpackages that actually run

So this is not a "start from scratch" situation.

It already looks like a serious pre-alpha Python package repository.

## What Still Has To Happen

### 1. Define A Stable Public API

Right now, the repo has a great deal of real code, but much of it still reads as:

- research package internals
- evolving architectural surfaces
- example-driven implementation

To make the package genuinely usable for outsiders, the project needs to decide:

- what imports are public and supported
- what is experimental or internal
- what the main user entrypoints are supposed to be

This is probably the single biggest packaging question.

Concretely, the package should aim for:

- a clearly documented top-level API
- a rule of the form:
  - `state_collapser.*` public
  - some deeper submodules explicitly internal or unstable
- fewer situations where users must know the repo design history in order to use the package correctly

### 2. Tighten Installation And Dependency Story

The project already has `pyproject.toml`, but a real user package needs a very clear dependency story covering:

- base install
- optional RL extras
- optional ML extras
- exact supported Python versions
- what a minimal user needs versus what a dev contributor needs

This part is close, but it should be polished and tested from a clean environment.

### 3. Publish To PyPI For Real

If "other people can use it" is meant in the normal Python sense, then the project needs:

- build artifacts
- upload to PyPI
- verification of install from PyPI
- verification that metadata is correct

The package is structurally close, but public package usability is not real until:

- `pip install state-collapser`

actually works.

### 4. Decide What Counts As Supported Behavior

The repo still evolves through fairly deep design corrections.

That is fine for a research project, but external users need clarity about:

- what workflows are stable enough to try
- what examples are reference examples
- what parts are pre-alpha and may still break

A professional package can still be pre-alpha, but it has to be honest.

### 5. Improve User-Facing Docs Around Usage, Not Just Theory

The project now has strong design material, but an outside user will want:

- install instructions
- a quick start
- one simple end-to-end example
- "how do I define my own hidden graph or env?"
- "how do I run tower training?"
- "how do I run exploit/explore?"
- "what outputs or objects do I inspect?"

This is probably the second biggest gap after API stabilization.

### 6. Separate Internal Research Machinery From User Workflows

The repo still exposes a lot of implementation evolution directly.

For a usable package, one usually wants:

- user docs simple
- public entrypoints simple
- internal machinery still present, but not required reading

That implies likely cleanup work around:

- naming
- exports
- docs
- what gets imported from where

### 7. Add Package-Consumer Examples

The project already has strong internal examples.

What it still needs are examples written more like:

- user installs package
- user imports a small supported surface
- user defines a problem
- user runs training
- user inspects tower output

That is different from examples that primarily validate repo design.

### 8. Add CI Checks For Packaging Itself

If not already covered strongly enough, CI should check things like:

- wheel builds
- sdist builds
- import from installed artifact
- maybe a smoke-tested minimal install path

This catches the class of problem where:

- repo works locally
- published package is broken

## How Involved Is It?

### To Become A Real Installable Pre-Alpha Package

- moderate work
- very achievable from current repo state

### To Become A Polished Package That Strangers Can Productively Adopt

- substantial work
- mostly API, documentation, and stability work
- not primarily raw code scaffolding work

## Honest Estimate

If the goal is:

### "People can install it and experiment with it"

Then the project is fairly close.

Main remaining tasks:

- PyPI publish
- API clarification
- usage docs
- package-install verification

### "People can adopt it without needing your design history in their head"

Then the project is not close enough yet.

That would require:

- stronger public API boundaries
- more tutorial-grade docs
- more stable semantics
- clearer supported workflows

## Shortest Truthful Answer

The project already has:

- a real Python package repo

The project does not yet fully have:

- a polished public Python package experience

So the next work is less:

- "invent package structure"

and more:

- stabilize API
- polish install and docs
- publish
- define what is actually supported

## Next-Level Steps To Make It Professionally Usable By Outsiders

What follows is the higher bar.

### 1. Freeze A Real Public API

Too much repo understanding still depends on internal design context.

The project needs to decide:

- what imports are officially public
- what modules are internal
- what stability promise is being made

Concretely:

- define a small supported surface
- document it in one place
- avoid making users import deep internal modules unless necessary

A stranger should be able to answer:

- what do I import?
- what object do I construct?
- what function do I call?
- what outputs do I inspect?

### 2. Define The Supported User Workflows

The package should probably settle on roughly two to four canonical workflows, for example:

- define a hidden-graph problem and inspect tower construction
- run tower-aware training
- run exploit/explore control
- run instrumentation on a training run

Right now the repo supports pieces of this, but the user journey is not yet canonized.

Each workflow should have:

- one recommended entrypoint
- one recommended config path
- one documented output story

### 3. Write Outsider-Facing Docs, Not Just Design Docs

The project already has strong design material.

What is missing is package-consumer documentation.

At minimum, the package likely wants:

- `Quick Start`
- `Core Concepts`
- `Define Your Problem`
- `Run Training`
- `Inspect Towers`
- `Examples`
- `What Is Experimental`

These docs must not assume the reader has followed the design history.

### 4. Draw A Hard Line Between Stable And Experimental

This is essential.

The package should clearly mark:

- stable enough to use
- experimental but available
- internal and not supported

For example:

- `PlateSupportEnv` may become a reference example
- some exploit/explore surfaces may remain experimental
- some tower internals should be internal-only

If everything looks equally official, outside users will misuse unstable parts.

### 5. Make Installation And Environment Setup Boring

A professional package should be easy to install and verify.

That means:

- clean PyPI package
- extras that make sense
- documented install commands
- one command to verify install worked
- one command to run a basic example

A user should not have to infer setup from contributor docs.

### 6. Add Artifact-Level Packaging Checks

CI should verify:

- wheel builds
- sdist builds
- package installs from built artifact
- import works from installed artifact
- maybe one smoke example runs from installed package

This is different from merely having tests pass in a repo checkout.

### 7. Improve Examples So They Teach Usage

Examples should do two jobs:

- validate package behavior
- demonstrate package use

The repo currently does the first better than the second.

It needs examples that read more like:

- here is how a user uses `state_collapser`

and less like:

- here is how the repo probes its own evolving internals

### 8. Make Instrumentation A User Feature

The new instrumentation work could become a major usability win.

Outsiders will understand the package faster if they can:

- inspect tower depth over time
- inspect contraction behavior
- inspect path-space restriction
- inspect active-tier traces

That should feel like part of the package experience, not like hidden repo tooling.

### 9. Reduce Conceptual Leakage From Internals

A lot of current surfaces still expose implementation evolution directly.

Professional usability improves when:

- names are consistent
- entrypoints are few
- defaults are sane
- internals are hidden unless needed

This is mostly cleanup and API discipline.

### 10. Add "Trustworthy Honesty" Docs

For a research-heavy package, outsiders need a blunt status page.

Something like:

- what works now
- what is under active redesign
- what examples are authoritative
- what claims are conceptual versus empirically validated

That makes the package feel more professional, not less.

### 11. Strengthen Evaluation And Reproducibility

For outsiders to take the package seriously, they need to reproduce claims.

That means the project likely wants:

- canonical benchmark or example runs
- fixed seeds where appropriate
- documented expected outcomes
- known limitations

Especially for:

- `PlateSupportEnv`
- future example environments

### 12. Prepare For Issue And PR Traffic From Strangers

A professional package needs repo behavior that can absorb outside use:

- issue templates
- bug report expectations
- feature request guidance
- contribution boundaries
- support expectations

This is not huge work, but it matters.

## Best Next-Level Roadmap

If this work is prioritized, the highest-value order is probably:

1. freeze the public API
2. define two to four canonical user workflows
3. write outsider-facing usage docs
4. publish and verify install-from-artifact
5. add packaging CI checks
6. promote instrumentation into a real user feature
7. clearly label experimental versus stable surfaces
8. build reproducible example and evaluation guidance

## Final Summary

To become professionally usable by outsiders, the repo now needs less raw invention and more:

- API discipline
- user workflow clarity
- packaging verification
- polished docs
- honest stability boundaries
- reproducible example use

That is substantial work, but it is the right kind of work now.

The hard part is no longer:

- "is there a package here?"

The harder and more important question is now:

- "can an outsider use it without needing to live inside the design process?"
