# Evaluation Strategy

## Status

This document records a general evaluation methodology for example environments used to assess `state_collapser`.

It is not env-specific.

Its role is to define:

- what makes an example environment a good `state_collapser` testbed
- how `state_collapser` should be evaluated on such an environment
- what comparison structure is required to isolate the actual value of the tower apparatus

This document is intended to sit above env-specific design folders such as:

- `docs/design/test_design/env_001/`

and to guide future example creation and evaluation work.

## Purpose

The purpose of this methodology is to prevent `state_collapser` evaluation from becoming vague, undercontrolled, or accidentally rigged.

In particular, evaluation should not collapse into:

- “the package ran”
- “the package got some reward”
- “the package beat one weak baseline”

Instead, evaluation should answer two distinct questions:

1. Is a given example environment actually a good `state_collapser` testbed?
2. Does `state_collapser` actually help on that environment in a way that justifies its added structure?

## Core Evaluation Questions

### 1. Is an example environment a good `state_collapser` testbed?

This means asking:

- Does the environment instantiate the kind of hidden, non-canonical hierarchy the package claims to help with?
- Does it preserve reward locality?
- Is it discrete enough for the current package surfaces?
- Is it nontrivial without becoming so large that the results are hard to interpret?

### 2. Does `state_collapser` help on that environment?

This means asking:

- Compared to what baseline?
- Measured how?
- Under what training budget?
- By what evidence of hierarchy use, not just reward improvement?

These two questions must be kept separate.

An environment can be:

- a bad testbed even if the package performs well on it

and the package can:

- fail to help on an environment that is nevertheless a good and honest testbed

## Required Three-Mode Comparison

Every serious evaluation environment should, where possible, support the same underlying RL problem in three modes:

1. **Plain Gymnasium problem**
   - flat training directly on the env
2. **Top-tier-only problem**
   - training using only the uppermost tier abstraction/control surface
3. **Full tower problem**
   - training using the full multi-tier tower controller

This three-way comparison is required because each column tests a different claim.

### Gymnasium vs Tower

This comparison tests:

- whether the full `state_collapser` apparatus is actually worth its overhead
- whether all the extra structure still buys a net improvement rather than merely adding sophistication

### Top tier vs Tower

This comparison tests:

- whether the multi-tier control story matters beyond just having some abstraction at all
- whether the actual tower control loop is responsible for the speedup, rather than a single coarse tier doing all the work

### Gymnasium vs Top tier

This comparison tests:

- whether abstraction helps at all

### Why the three-way comparison matters

If one evaluates only:

- `Gymnasium vs Tower`

then even a positive result leaves open the possibility that:

- all benefit came from a trivial single coarse abstraction
- the rest of the tower is dead weight

If one evaluates only:

- `Top tier vs Tower`

then one does not know whether the full package meaningfully outperforms ordinary RL once all of its added machinery is counted.

So the key methodological rule is:

- every serious example should be testable in **flat**, **top-tier-only**, and **full-tower** modes

because that isolates:

- baseline performance
- abstraction-only performance
- full hierarchical-control performance

## Three Evaluation Layers

For environments like `PlateSupportEnv`, evaluation should have three layers:

1. structural evaluation
2. behavioral evaluation
3. performance evaluation

These should be treated as distinct.

### Structural Evaluation

Structural evaluation asks:

- What hidden constraint geometry does the env represent?
- What makes flat parametrization misleading, weak, or unhelpful?
- What quotientable or collapsible regularity should plausibly exist?

This layer is about whether the environment is a faithful model of the sort of problem `state_collapser` is meant to address.

### Behavioral Evaluation

Behavioral evaluation asks:

- Does the tower actually build meaningful structure?
- Do tiers stabilize differently?
- Does control shift in the intended downstairs/upstairs way?

This layer is about whether the package is using its own hierarchy in a meaningful way, rather than merely carrying extra bookkeeping during effectively flat learning.

### Performance Evaluation

Performance evaluation asks for ordinary empirical metrics such as:

- sample efficiency
- success rate
- reward
- variance across seeds
- possibly path-space restriction metrics, if and when instrumentation supports them

This layer is about whether the package’s claimed advantages show up in measured outcomes.

## What Makes A Good `state_collapser` Evaluation Environment

An example environment should pass a simple screen before being treated as a serious evaluation env.

It should be:

- constrained enough to hide hierarchy
- discrete enough for the current package
- small enough to inspect
- rich enough that tower structure could plausibly matter
- not so artificial that it only proves something about toy graphs

More specifically:

### 1. Hidden or non-canonical hierarchy

The environment should not hand the package an obvious ready-made task hierarchy.

Instead, it should plausibly contain:

- hidden equivalences
- hidden regularity
- or hidden path-space compression opportunities

that could be surfaced by contraction and quotient construction.

### 2. Reward locality

The environment should preserve the reward-locality assumptions that the package currently relies on.

If reward locality is broken, then evaluation is no longer testing the package under its intended mathematical and runtime assumptions.

### 3. Discreteness and inspectability

At the present stage, environments should be:

- discrete
- inspectable
- small enough that graph behavior and tier behavior can be understood directly

This is important because early evaluation must remain interpretable.

### 4. Meaningful constraint geometry

The environment should represent some form of coupled, constrained, or nontrivially feasible state/action structure.

Typical examples include:

- support/placement constraints
- shared-object constraints
- contact constraints
- constrained movement manifolds

## Evidence That `state_collapser` Is Actually Helping

A positive evaluation should not be defined only by:

- “tower reward is higher”

There should also be evidence that:

- the hierarchy is being used
- the training burden is being redistributed in the intended way
- the tower is providing meaningful compression or control support

That means evaluation should look for evidence such as:

- different tier behavior over time
- nontrivial tower growth
- meaningful active-tier shifts
- reduced effective path-space burden
- full-tower advantage over top-tier-only abstraction

## Negative Controls And Bad-Fit Environments

Evaluation should include, or at least allow for, environments where `state_collapser` is not expected to help much.

This matters because otherwise evaluation becomes too easy to game.

It is useful to have:

- one or more “bad fit” environments

for which:

- hierarchy is already trivially available
- flat training is already easy
- or contraction-derived hierarchy is unlikely to provide real advantage

This helps establish that the methodology is not rigged in favor of the package.

## New-Example Design Rubric

When proposing a new example environment, the following questions should be answered first:

1. What kind of hidden constraint geometry does this env represent?
2. Why is a natural hierarchical decomposition not already obvious?
3. Why is the environment discrete enough for current package evaluation?
4. What makes this env small enough to inspect but rich enough to matter?
5. How will the env support the required three-mode comparison?
6. What would success for `state_collapser` look like here?
7. What would failure for `state_collapser` look like here?

No new example should be treated as a serious evaluation env without an explicit answer to those questions.

## Practical Methodology Program

At a high level, the evaluation program should proceed in this order:

1. Define what makes an environment a good `state_collapser` evaluation environment.
2. Define what counts as success or failure for the package on that environment.
3. Require flat / top-tier-only / full-tower comparability.
4. Evaluate the environment structurally, behaviorally, and empirically.
5. Build a small taxonomy of example families.

## Example-Family Taxonomy

A useful initial taxonomy of example families would include:

- support/placement constraints like `PlateSupportEnv`
- coupled-arm or shared-object constraints
- contact-mode or locomotion-style constraints
- at least one “bad fit” control environment as a negative case

This taxonomy matters because the package should not be validated only on a single kind of constrained toy problem.

## What Counts As Success

At the methodology level, success should mean something like:

- the environment is a credible hidden-hierarchy testbed
- the tower grows meaningful structure
- the full tower outperforms flat learning enough to justify its added complexity
- the full tower also outperforms top-tier-only abstraction enough to justify multi-tier control

## What Counts As Failure

Failure should include cases such as:

- the environment did not really test hidden hierarchy in the first place
- the package reduced to effective flat learning with extra bookkeeping
- top-tier-only abstraction captured all benefits and the rest of the tower added no value
- the full tower’s overhead erased any benefit over the plain Gymnasium baseline

## Immediate Consequence For Future Env Design

Going forward, env-specific design work should not start with:

- “can we build a toy env?”

It should start with:

- “can this env be evaluated in flat, top-tier-only, and full-tower modes?”
- “does it actually instantiate the kind of hidden hierarchy this package claims to help with?”

That should be the first screening criterion for future example design.
