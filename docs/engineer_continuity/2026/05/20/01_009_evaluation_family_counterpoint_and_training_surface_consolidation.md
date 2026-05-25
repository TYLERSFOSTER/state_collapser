# Engineer Continuity Report
## 01_009_evaluation_family_counterpoint_and_training_surface_consolidation

## Date

2026-05-20

## Interval covered

This report covers the work completed after the prior continuity report:

- [01_008_control_corrections_tower_ownership_and_release_readiness.md]([state_collapser repository root]/docs/engineer_continuity/2026/05/18/01_008_control_corrections_tower_ownership_and_release_readiness.md)

That prior report ended at the `v0.3.0` milestone and described a repository that had:

- corrected exploit/explore polarity
- package-owned dynamic tower construction
- tierwise remaining-edge contraction
- deeper live tower behavior in `PlateSupportEnv`
- better package-facing root docs
- and the first explicit scoping turn toward real outsider-facing package usability

This interval begins there and continues through:

- expansion of the example/evaluation family
- addition of a reusable tower-depth probe utility
- root-level evaluation documentation
- a new `rl_counterpoint_v3` example package derived from the older `[rl_counterpoint repository root]` project but rebuilt for `state_collapser`
- the first serious design pass on model/training surfaces
- the first reusable internal `state_collapser.training` package
- migration of `rl_counterpoint_v3` onto those new training surfaces
- continued README synchronization
- and release preparation for `v0.4.0`

This is another large interval, though different in character from the previous one.

The `01_008` interval was dominated by:

- semantic corrections
- runtime ownership corrections
- dynamic tower construction corrections

This interval is dominated by:

- evaluation-surface buildout
- package-consumer readiness work
- training/model interface architecture
- and first real internal componentization of the training layer

## Executive status

At the start of this interval, the repository had:

- a mathematically and architecturally stronger tower/runtime core than before
- a corrected exploit/explore controller
- a clearer sense that `PlateSupportEnv` was a genuinely useful evaluation example
- and the first package-readiness scoping documents

But it still lacked several things that a serious research package needs:

- a broader evaluation-family story beyond `PlateSupportEnv`
- a reusable depth-probing tool
- a reconstructed music/counterpoint example that connected back to the project’s conceptual origin
- a coherent internal training-surface layer
- and a clearer README that acknowledged the current example and training architecture

At the end of this interval, the repository now has:

- a first wave of additional constrained evaluation environments
- a root-level `EVALUATION.md`
- a reusable `tower_depth_probe` utility
- a new `rl_counterpoint_v3` example package
- a large design stack for model/training surfaces
- a real internal `src/state_collapser/training/` package
- a first migrated example using those reusable training surfaces
- and a README that is much closer to present repo reality

The project is still `pre-alpha`.

But the center of gravity has shifted again:

- from “tower/control/runtime corrections”

to:

- “evaluation breadth, package-facing training structure, and release-facing professionalization”

## Highest-level narrative

This interval has five large movements.

### 1. The repository moved from a single flagship evaluation example toward a real example family

`PlateSupportEnv` remained important throughout this interval.

But the repository stopped treating it as the only serious evaluation environment.

The mathematical-model document contains a list of constrained-system examples that are meant to motivate the hidden-geometry / hard-to-parameterize-HRL setting.

This interval converted that list into a first wave of actual repo-facing example families.

### 2. The project’s counterpoint origin was reintroduced in a package-appropriate form

The older `[rl_counterpoint repository root]` repository is historically important:

- it is one of the project’s conceptual origin points
- it fed directly into the HRL thinking later formalized in `logHRL.tex`

But that old repository also came with its own tower/training assumptions that do not belong inside `state_collapser` as-is.

So the work here was not:

- “port the old repo wholesale”

It was:

- rebuild the underlying RL problem in a `state_collapser`-appropriate way

That became `rl_counterpoint_v3`.

### 3. The project finally took a serious turn toward training/model surface architecture

The README had already been gesturing at:

- policy model integration
- switching models across environments

But that TODO item was still too narrow and too underdesigned.

This interval turned that vague desire into:

- a serious design architecture note
- a blueprint
- an implementation gameplan
- and a first internal implementation

### 4. The package now has a reusable internal training component layer

This is the single most important engineering shift in the interval.

The package now has:

- `src/state_collapser/training/`

with first reusable surfaces for:

- decision inputs
- action decisions
- transitions
- collectors
- learners
- metrics
- reference loops

This is not a finished public ML API.

But it is the first real component layer that starts to look like something a serious ML engineer could build on.

### 5. The repository is now noticeably closer to an actual outsider-facing release posture

This does not mean “ready for stable adoption.”

It means:

- root docs are more truthful
- release history is more accurate
- evaluation guidance exists
- training-surface architecture is no longer only implied
- and the remaining work is increasingly recognizable:
  - serious benchmarking
  - finishing the paper
  - cleanup / professionalization / hardening

That is a much healthier state than the project was in even a few days earlier.

## Detailed continuity

## Phase A — Repository-facing evaluation documentation and probe tooling

One of the first important turns in this interval was the explicit realization that the repository needed a normal, professional root-level evaluation document.

The question arose in a package-readiness frame:

- if this is becoming a serious Python package, what is the correct root document for evaluation/benchmark guidance?

The answer that emerged was:

- `EVALUATION.md`

not because GitHub gives it special root-tab treatment, but because it is the semantically correct package-facing document for:

- evaluation philosophy
- example coverage
- benchmark expectations
- and the relationship between structural and performance evaluation

That document was then populated as a serious root guide rather than a scratch note.

It now explains:

- what counts as evaluation in this repository
- how example runs should be interpreted
- the relationship between tower depth and actual learning performance
- and how to run the current available probes and training paths

This is a package-readiness improvement, not a small documentation flourish.

### A.1 — Tower-depth probing became a real tool rather than an ad hoc shell snippet

The project had already been using direct runtime probing to understand tower growth.

But until this interval, that probing was still too ad hoc.

The earlier command-line heredoc probes were useful for diagnosis, but not yet package-quality.

So this interval converted that repeated diagnostic pattern into:

- [src/state_collapser/examples/tower_depth_probe.py]([state_collapser repository root]/src/state_collapser/examples/tower_depth_probe.py)

This matters for several reasons:

- it makes structural evaluation reproducible
- it gives engineers a real utility surface for “how deep is the tower getting?”
- it makes it easier to compare examples under matched runtime conditions
- and it reinforces the repo’s evaluation story in a way that is not tied to one-off terminal archaeology

The probe also ended up exercising several design truths:

- tower materialization depth is not the same thing as exploit/explore active-tier behavior
- matched comparison conditions matter
- and example suitability cannot be judged from one weak probe surface

That tool is now part of the example/evaluation surface rather than an internal trick.

## Phase B — Example-family buildout from the mathematical-model example list

The next large movement was the conversion of the mathematical-model example list into a first actual example family buildout.

This started from a specific location:

- the example list in [docs/design/mathematical_model_w_Codex_comments.tex]([state_collapser repository root]/docs/design/mathematical_model_w_Codex_comments.tex)

The Project Owner asked for environments “like `plate_support_env`” for those example families.

The important interpretive point here was:

- these were never supposed to be literal robotics simulators of the cited systems

Instead, the task was to construct:

- small discrete evaluation environments inspired by those constrained geometric/control families

### B.1 — Blueprint and gameplan work

The repo went through proper design first:

- [example_family_blueprint_from_mathematical_model_list.md]([state_collapser repository root]/docs/design/test_design/example_family_blueprint_from_mathematical_model_list.md)
- [example_family_implementation_gameplan.md]([state_collapser repository root]/docs/design/test_design/example_family_implementation_gameplan.md)

This design work fixed several important questions:

- which example families should be built now
- which should be deferred
- what counts as a faithful discrete analogue versus a misleading pseudo-simulator
- and how these examples should be structured in `src/state_collapser/examples`

### B.2 — The first real design blocker: exact loop closure froze the graph

The first implementation attempt hit a real design problem:

- the exact loop-closure version of the first articulated mechanism environment froze the feasible graph at the start state

This was an important moment because it forced a substantive design choice rather than a silent hack.

The question became:

- should the environment preserve one-joint actions and relax closure semantics?
- or preserve exact closure and introduce coupled actions?

The Project Owner’s answer was strong and correct:

- do not pre-couple actions
- that just chooses a parameterization in disguise

Instead:

- allow a small closure-error tolerance
- use explicit coupler slack / mismatch budget semantics

That preserved the right spirit of the project:

- difficult hidden constraint geometry
- but not one that is smoothed away by pre-authoring coordinated actions

### B.3 — New evaluation environments landed

The first-wave example family was then implemented under:

- [src/state_collapser/examples/articulated_loop_env]([state_collapser repository root]/src/state_collapser/examples/articulated_loop_env)
- [src/state_collapser/examples/cable_parallel_env]([state_collapser repository root]/src/state_collapser/examples/cable_parallel_env)
- [src/state_collapser/examples/dual_arm_manipulation_env]([state_collapser repository root]/src/state_collapser/examples/dual_arm_manipulation_env)
- [src/state_collapser/examples/parallelogram_singularity_env]([state_collapser repository root]/src/state_collapser/examples/parallelogram_singularity_env)

with focused tests and implementation logs for each.

The interval’s validation record for that work was strong:

- focused family slice passed
- broader examples slice passed
- full repo passed
- lint and mypy passed

### B.4 — Deeper matched probing showed that the new examples were not obviously shallow

There was then a sharp moment of concern when a weaker comparison surface made it look as though the new example environments were not producing the kind of tower depth `PlateSupportEnv` had shown.

That concern was valid.

But the follow-up comparison did something much more careful:

- matched continuous random-discovery probing
- explicit contraction policy
- same measurement surface

That comparison showed:

- `PlateSupportEnv` still behaved like a deep-tower example
- `ArticulatedLoopEnv` was not shallow in the matched setting
- and under that matched probe `ArticulatedLoopEnv` even materialized a slightly deeper tower than `PlateSupportEnv`

This was important not because it “proved” the new examples are all perfect, but because it prevented a false early dismissal of the new family from a bad comparison surface.

## Phase C — Rebuilding the counterpoint RL problem as `rl_counterpoint_v3`

The next major interval movement was the counterpoint rebuild.

This is historically important in the project.

The older `[rl_counterpoint repository root]` repo is one of the projects that originally pushed the Project Owner toward the HRL thinking later formalized in the paper and the design docs.

But that old repo is not the package surface that should live in `state_collapser`.

So the first task here was interpretive:

- understand what `rl_counterpoint` was really about
- separate the RL problem from the old repo’s tower/training stack
- decide what to preserve conceptually and what to reject architecturally

### C.1 — Transformation report

That interpretive work became:

- [01_001_rl_counterpoint_v3_transformation_report.md]([state_collapser repository root]/docs/design/test_design/rl_counterpoint_v3/01_001_rl_counterpoint_v3_transformation_report.md)

The core conclusion of that report was:

- `rl_counterpoint_v3` should be a compact counterpoint RL environment
- not a port of the older repo’s explicit tower stack
- not a transformer / artifact / staged-rank pipeline

This was the correct framing.

### C.2 — Blueprint reset from two voices to three voices

An important correction happened at the blueprint stage.

The first blueprint attempt was too two-voice oriented.

The Project Owner stopped that immediately and correctly:

- the first real version needed to be three-voice from the start
- and the wrong two-voice shape should not be cosmetically patched into a three-voice story

So:

- [01_002_rl_counterpoint_v3_blueprint.md]([state_collapser repository root]/docs/design/test_design/rl_counterpoint_v3/01_002_rl_counterpoint_v3_blueprint.md)

was rewritten from scratch around the correct three-voice scope.

This is worth recording because it was a textbook example of avoiding “sloppy salvage” of a wrong design document.

### C.3 — Gameplan and implementation

The repo then proceeded through:

- [01_003_rl_counterpoint_v3_implementation_gameplan.md]([state_collapser repository root]/docs/design/test_design/rl_counterpoint_v3/01_003_rl_counterpoint_v3_implementation_gameplan.md)

and then implementation, producing:

- [src/state_collapser/examples/rl_counterpoint_v3]([state_collapser repository root]/src/state_collapser/examples/rl_counterpoint_v3)

with:

- `env.py`
- `runtime.py`
- `training.py`
- `__init__.py`

plus focused tests across:

- validity
- transitions
- rewards
- gymnasium integration
- runtime integration
- tower training

### C.4 — First-scope counterpoint reality

The implemented first-scope counterpoint example is:

- flat from the package perspective
- three-voice from the start
- bounded by explicit step-delta actions
- built around hidden validity constraints and structured reward
- and intentionally stripped of the old repo’s explicit rank tower machinery

The key reality checks recorded during implementation were good:

- valid states existed in meaningful numbers
- curated start states existed
- goal states existed
- the default start state had legal outgoing transitions
- and direct depth probing showed real tower growth

This gave the repo something more valuable than a nostalgic port:

- a conceptually important RL problem rebuilt as a clean `state_collapser` example

## Phase D — Model and training surfaces became a real design area

The next major movement was architectural rather than example-local.

The README already contained a TODO item about policy-model integration.

But it was still too narrow in several ways:

- it overemphasized literal `\pi_\theta`
- it did not say enough about how serious ML engineers actually want to work
- and it did not clearly separate:
  - the trainable object
  - the learner/update rule
  - the training loop itself

### D.1 — The central PO claim

The Project Owner drove the key architectural claim here:

- ML engineers do not usually want one rigid package-owned training loop
- they want the pieces of a training loop as good reusable surfaces
- while keeping the actual loop itself something they author

That is the heart of the training-surface architecture.

It is worth recording explicitly because it shaped everything that followed.

### D.2 — The policy-only framing was broadened

The training-surface discussion also clarified another important issue:

- in RL, the trainable object is not always literally a policy distribution

Sometimes it is:

- a Q-function
- an actor-critic stack
- a history-conditioned decision surface

So the package-facing boundary should not be frozen as:

- `\pi_\theta : \mathcal{S}_H \to \mathcal{P}(\mathcal{A}_H \mid \mathcal{S}_H)`

Instead, the broader and more honest architectural picture became:

- `\mathcal{M}_\theta : \mathcal{X}_H \to \mathcal{D}_H`

with:

- package-defined decision input space
- package-defined decision surface

This was not treated as a mathematical-model contradiction.

Instead, it was treated as:

- a generalization of the training/model interface
- consistent with the current hidden-graph / runtime / tower picture

### D.3 — Architecture note and blueprint

This work then passed through:

- [01_001_model_and_training_surface_architecture.md]([state_collapser repository root]/docs/design/model_train_surfaces/01_001_model_and_training_surface_architecture.md)
- [01_002_model_and_training_surface_blueprint.md]([state_collapser repository root]/docs/design/model_train_surfaces/01_002_model_and_training_surface_blueprint.md)

These documents did several important things:

- fixed the anti-master-trainer stance
- fixed the component-surface decomposition
- checked compatibility with the mathematical model
- checked compatibility with present architecture
- checked credibility against contemporary RL practice
- explicitly considered `gymnasium`
- explicitly considered `ROS 2`
- and separated first-scope architecture from next-stage hardening topics

### D.4 — Git-practice formalization

While this work was happening, the repo also got a new prime-directive note:

- [docs/prime_directive/git_practices.md]([state_collapser repository root]/docs/prime_directive/git_practices.md)

Its first explicit rule is important:

- once a blueprint and implementation gameplan are approved for execution, execution should happen on a dedicated implementation branch before merging back

This matters because the repository had already accumulated enough architectural complexity that “accidentally implement on `main` and sort it out later” was no longer a healthy normal state.

That git-discipline note is now part of the repository’s live procedural authority.

## Phase E — The first reusable internal `state_collapser.training` package

This is the single biggest engineering milestone in the interval.

The training-surface blueprint was then converted into:

- [01_003_model_and_training_surface_implementation_gameplan.md]([state_collapser repository root]/docs/design/model_train_surfaces/01_003_model_and_training_surface_implementation_gameplan.md)

and then implemented on a dedicated branch.

### E.1 — First package shape

The new package locus is:

- [src/state_collapser/training]([state_collapser repository root]/src/state_collapser/training)

with first-scope files:

- `inputs.py`
- `decisions.py`
- `transitions.py`
- `collectors.py`
- `learners.py`
- `metrics.py`
- `reference_loops.py`
- `__init__.py`

The package is organized by:

- surface role

not:

- RL-family label

This is exactly what the design work had argued for.

### E.2 — First-scope component surfaces

The package now contains first reusable surfaces for:

- `ActionSelectionInput`
- `ActionDecision`
- `TrainingTransition`
- `StepCollector`
- `EpisodeCollector`
- generic `Learner`
- non-canonical reference `TabularQLearner`
- `EpisodeMetrics`
- `TrainingMetrics`
- `run_reference_online_loop(...)`
- `run_reference_episode_loop(...)`

These are not yet a hardened public API.

But they are real code, not a future-dream package stub.

### E.3 — The first migration target was `rl_counterpoint_v3`

The implementation gameplan did not stop at “abstract surfaces exist.”

It required:

- one real example migration

The chosen target was:

- `rl_counterpoint_v3`

This was a very good choice because:

- it is flatter than the exploit/explore `PlateSupportEnv` path
- it is newer
- it is less entangled with controller-specific machinery
- and it gave the new training package a cleaner first reality check

### E.4 — What changed in the migrated example

The migrated training file:

- [src/state_collapser/examples/rl_counterpoint_v3/training.py]([state_collapser repository root]/src/state_collapser/examples/rl_counterpoint_v3/training.py)

now delegates its actual training orchestration to the new generic package surfaces.

This means the repo now has a concrete proof that:

- the new training package is not merely abstract
- it can actually drive a real example’s tower-aware training path

while preserving:

- the example’s env/runtime ownership split
- the example’s structured training result shape

### E.5 — Validation

The validation story for this work was clean and unusually satisfying:

- focused training slice passed
- migrated example test passed
- broader examples slice passed
- full repo passed
- `mypy src` passed
- `ruff check .` passed

This means the first training-surface implementation landed without destabilizing the broader repository.

That is a real milestone.

## Phase F — README synchronization and package-facing clarity

The README was then revisited against the new state of the repo.

The key realization was:

- the README was still broadly good
- but no longer matched the current training-surface and example-family reality closely enough

### F.1 — What was stale

Several things had become outdated:

- the old narrow policy-model TODO framing
- the lack of mention of `state_collapser.training`
- the lack of mention of `rl_counterpoint_v3`
- the lack of mention of the new example family
- the lack of a root-level probe example
- and small correctness/polish issues

### F.2 — What changed

The README was updated so it now:

- reflects the broader model/training-surface framing
- links to the new training-surface design docs
- mentions the new internal training package
- includes a quick-start example for `rl_counterpoint_v3`
- includes the `tower_depth_probe` CLI example
- names the newer example family
- and acknowledges the new internal training layer in the repo status section

This is important because the README is now much closer to a truthful package-facing document.

## Phase G — Package-readiness framing became sharper

A smaller but important side thread in this interval was the explicit scoping of what remains before the package really feels like something outsiders can use professionally.

That discussion was captured in:

- [docs/design/PyPl_readiness/01_001_python_package_readiness_scoping.md]([state_collapser repository root]/docs/design/PyPl_readiness/01_001_python_package_readiness_scoping.md)

The important outcome was a more mature differentiation between:

- being installable and plausibly consumable

and:

- being professionally usable by outsiders without needing to live inside the design process

The latter still requires:

- serious benchmarking
- stable workflow docs
- more package-facing hardening
- and continued cleanup of user-facing surfaces

But the repository is now much closer to that conversation being concrete rather than hypothetical.

## Net architectural change across the interval

At the start of the interval, the repository still had a lot of its runnable value concentrated in:

- tower/runtime/control machinery
- `PlateSupportEnv`
- and example-local training loops

At the end of the interval, the repository still has that core.

But it also now has:

- a broader evaluation-family story
- a reusable structural probe
- a rebuilt counterpoint environment tied to the project’s conceptual lineage
- a real internal training-surface package
- and one real example already migrated to it

This changes the project’s shape materially.

The repository is no longer only:

- a strong runtime/tower research prototype

It is increasingly also:

- a package that is learning how to present itself as reusable engineering infrastructure

That is not yet complete.

But the turn is real.

## Current repository state at the end of the interval

At the end of this interval, the repository has:

- `v0.3.0` already released behind it
- additional evaluation/example families
- a root-level evaluation guide
- a tower-depth probing utility
- `rl_counterpoint_v3`
- an internal `state_collapser.training` package
- one real migrated example using that new package
- a more accurate README
- and a much sharper understanding of what remains before outsider-facing maturity

The package is still pre-alpha.

But the work remaining is increasingly of a recognizable kind:

- serious benchmarking
- finishing the paper
- cleanup and professionalization
- later hardening of training/model surfaces

Those remaining steps are substantial.

But they are no longer hidden inside architectural confusion about what the repo even is.

## Risks and open follow-ons

The most important unresolved items after this interval are:

### 1. Serious benchmarking is still ahead

The repository now has a genuine example suite and better evaluation tooling.

But it still needs:

- benchmark protocols
- comparison discipline
- stronger claims tied to repeatable evidence

### 2. The training package is real, but still internal-first

`state_collapser.training` now exists.

But it is still:

- an internal reusable layer
- not a settled public API

The later hardening questions remain:

- vectorization
- device/tensor semantics
- batching / sequence semantics
- checkpointing
- train/eval-mode separation

### 3. The paper still matters

The root package story still depends heavily on the mathematical paper and its clarity.

That rewrite remains an important unfinished piece of repo professionalism.

### 4. Outsider usability still requires cleanup

The repository is closer to professional usability, but not there yet.

It still needs:

- more cleanup
- more package-facing polish
- more benchmark clarity
- continued API discipline

## Closing assessment

This interval is best understood as:

- the interval where the project broadened its evaluation surface
- reintroduced its counterpoint origin in package form
- and finally began to build a real reusable training component layer

The prior interval corrected:

- control semantics
- tower-construction ownership
- contraction recursion

This interval consolidated around:

- evaluation breadth
- training-surface architecture
- and release-facing package honesty

That is exactly the right next movement for the project.

The repository is not finished.

But it is much closer to looking like:

- an actual serious Python package with a strong research angle

rather than only:

- a mathematically interesting but internally entangled research codebase

That distinction matters, and this interval materially advanced it.
