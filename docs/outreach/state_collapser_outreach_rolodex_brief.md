# Search Brief For Building A `state_collapser` Outreach Rolodex

## Purpose Of This Brief

You are an auxiliary GPT model doing internet research.

Your task is to build a high-quality list of people who might plausibly be
interested in a new research Python package called `state_collapser`.

The goal is not mass marketing.

The goal is a carefully targeted "I made this; you may find it interesting or
useful" outreach list for the project owner to contact personally.

Prioritize fit, intellectual relevance, and likely curiosity over audience size.

## One-Sentence Project Summary

`state_collapser` is a pre-alpha Python research package for inducing
hierarchical reinforcement-learning structure by building quotient-style towers
over dynamically discovered state/action graphs, especially for RL problems that
do not come with obvious human-readable subtasks.

## Short Project Explanation

Many hierarchical reinforcement learning methods work best when a task already
has meaningful subtasks, options, skills, or a natural hierarchy.

`state_collapser` is aimed at the harder case:

- the environment is complicated,
- the useful hierarchy is hidden,
- the state/action graph is discovered online,
- and the learner needs a coarse-to-fine structure that is induced rather than
  hand-specified.

The package builds quotient towers by recursively contracting discovered
state/action graph structure. The intended payoff is a reduction in effective
path-search and training burden: learn first on coarse quotient structure, then
lift/refine back to executable fine-scale behavior.

The associated research document frames this as a geometry-of-RL idea:
hierarchical addresses can reduce effective path-volume in a way analogous to
binary search, HNSW-style graph search, multiscale neural architectures, and
coarse-to-fine control.

The current implementation is research-mode/pre-alpha. It has working runtime
surfaces, example environments, Gymnasium-facing adapters, tower-aware training
components, and ongoing work to refactor the runtime toward a more efficient
nested partition/Young-diagram-like data structure.

## Core Concepts To Communicate To Search Targets

Relevant phrases:

- hierarchical reinforcement learning
- problem-agnostic hierarchy induction
- quotient MDPs / quotient tasks
- graph contraction
- state abstraction
- action abstraction
- options / skills / temporal abstraction
- coarse-to-fine RL
- path-space geometry
- path-volume reduction
- graph search and HNSW-style hierarchical addressing
- graph ML / geometric deep learning
- constrained robotics and control
- learned abstractions for hard exploration
- discovered state/action graphs
- dynamic quotient tower
- nested partitions / partition coarsening
- lift/refinement from abstract action to executable behavior

Avoid implying:

- this is already a polished production library,
- this is already benchmark-proven at scale,
- this replaces standard RL frameworks,
- this is only about music/counterpoint,
- this is only about graph theory.

The honest pitch is:

> This is a research package and mathematical program for inducing useful
> quotient/coset hierarchy in RL problems where the hierarchy is not given.

## Who You Are Looking For

Look for people in the following categories.

## Category 1: Hierarchical Reinforcement Learning Researchers

Highest priority.

Find researchers who work on:

- HRL theory or algorithms,
- options, skills, subgoals, temporal abstraction,
- state abstraction and action abstraction,
- task decomposition,
- option discovery,
- representation learning for hierarchy,
- goal-conditioned RL with abstraction,
- coarse-to-fine or multiscale RL.

Good signs:

- papers explicitly mention hierarchical RL, options, skills, subtask discovery,
  state abstraction, or temporal abstraction;
- they publish at NeurIPS, ICML, ICLR, RLDM, AAMAS, AAAI, IJCAI, CoRL, IROS, or
  RSS;
- they maintain public code or write about practical RL frameworks;
- they have worked on both theory and implementable systems.

Reason for fit:

`state_collapser` is directly about inducing hierarchy for RL without needing
human-readable subtasks.

## Category 2: RL Theory / MDP Abstraction Researchers

Highest priority.

Find people working on:

- MDP homomorphisms,
- bisimulation metrics,
- state abstraction,
- model minimization,
- representation learning for MDPs,
- approximate abstractions,
- value-preserving or policy-preserving abstraction,
- quotient MDPs,
- successor features or representation compression.

Good signs:

- papers use terms like "bisimulation", "MDP homomorphism", "state abstraction",
  "quotient", "latent MDP", "abstraction discovery", or "representation
  learning for control";
- they care about theory and correctness conditions;
- they might appreciate a mathematically explicit quotient-tower construction.

Reason for fit:

`state_collapser` is essentially trying to build useful quotient structure over
the discovered state/action graph.

## Category 3: Robotics RL And Constrained Control People

High priority.

Find people working on:

- robot learning under constraints,
- manipulation with complex configuration spaces,
- contact-rich manipulation,
- motion planning plus RL,
- hierarchical robot control,
- learned skills/options for robotics,
- safe exploration,
- constrained MDPs,
- model-based RL for robotics,
- sim-to-real control with difficult state/action geometry.

Good signs:

- they publish at CoRL, RSS, ICRA, IROS, NeurIPS/ICML robotics workshops;
- they work on problems where the natural low-dimensional structure is hidden,
  constrained, or hard to parametrize;
- they use graph/planning abstractions, skill hierarchies, or coarse-to-fine
  controllers.

Reason for fit:

The package is especially motivated by RL problems where the ambient parameter
space is misleading and the reachable state/action structure is a constrained
subset with hidden hierarchy.

## Category 4: Graph ML / Geometric Deep Learning / Graph Search Researchers

High priority.

Find people working on:

- graph neural networks,
- graph representation learning,
- graph coarsening,
- graph quotients,
- simplicial or topological graph ML,
- hierarchical graph search,
- HNSW or approximate nearest neighbor graph search,
- multiscale graph algorithms,
- graph pooling and graph contraction.

Good signs:

- papers combine graph structure with learning or search;
- they think geometrically about graph hierarchy;
- they have interest in hierarchical navigable small worlds, graph coarsening,
  or multiscale graph methods.

Reason for fit:

`state_collapser` imports a graph-search intuition into RL: hierarchy as an
address system over path spaces.

## Category 5: ML Systems / RL Framework Maintainers

Medium-high priority.

Find people involved in:

- Gymnasium / Farama Foundation,
- Stable-Baselines3,
- RLlib,
- CleanRL,
- Tianshou,
- TorchRL,
- PettingZoo,
- Minari,
- Acme,
- Dopamine,
- JAX RL libraries,
- reproducible RL benchmarking.

Good signs:

- they care about package surfaces, environment APIs, adapters, reproducibility,
  and maintainable RL experimentation;
- they might not be the deepest theory match, but could give valuable API and
  benchmarking feedback.

Reason for fit:

`state_collapser` is trying to integrate with conventional RL surfaces while
adding an unusual graph/tower runtime layer.

## Category 6: Exploration, Planning, And Search Researchers

Medium-high priority.

Find people working on:

- hard exploration,
- planning in large state spaces,
- graph search in RL,
- model-based planning,
- Monte Carlo tree search with abstractions,
- search over learned latent spaces,
- novelty/search bonuses over abstract states,
- state-space compression for exploration.

Good signs:

- they care about reducing search burden;
- they work at the boundary between planning and RL;
- they may understand the pitch that quotient hierarchy reduces effective
  path-volume.

Reason for fit:

The project's thesis is fundamentally about reducing flat path-space search.

## Category 7: Computational Creativity / Music RL Researchers

Medium priority, but use carefully.

Find people working on:

- RL for music generation,
- symbolic music generation,
- counterpoint generation,
- algorithmic composition,
- structured generative models for music,
- constraint-based music generation,
- neural-symbolic music systems.

Good signs:

- they understand Western counterpoint, voice leading, symbolic composition, or
  constraints in music generation;
- they may be interested in the author's original practice problem: RL for
  tonal counterpoint.

Reason for fit:

The project owner came to this through a failed/then-improved RL counterpoint
project. The best music contacts could appreciate the motivating example, but
the package itself is broader than music.

Warning:

Do not over-prioritize music AI people unless they also care about RL,
constraints, hierarchy, or structured search.

## Category 8: Mathematically Inclined ML Researchers

Medium priority.

Find people interested in:

- category theory and ML,
- topology/geometric methods in ML,
- algebraic or geometric views of RL,
- compositionality in learning,
- quotient constructions,
- multiscale structure,
- mathematical foundations of abstraction.

Good signs:

- they write theory papers, surveys, or conceptual work;
- they may appreciate a novel mathematical framing even before the package is
  industrially mature.

Reason for fit:

The paper uses quotient towers, path-volume, graph contraction, nested
partitions, and lift fibers. The right math-ML people could give valuable
feedback.

## Category 9: Benchmarking / Reproducible RL Evaluation People

Medium priority.

Find people working on:

- RL benchmark suites,
- reproducibility,
- evaluation methodology,
- environment design,
- diagnostic metrics,
- sample-efficiency comparisons.

Reason for fit:

The project needs serious benchmarking. People who understand how to evaluate
RL claims could be excellent early readers even if they are not HRL specialists.

## Category 10: Independent Researchers / Builders With Relevant Taste

Medium priority.

Find credible independent researchers, open-source maintainers, or technical
writers who:

- write deeply about RL, graph ML, or AI systems;
- build tools rather than only comment on trends;
- have a history of responding to unusual research prototypes;
- care about mathematical clarity or useful open-source experiments.

Reason for fit:

This project is early and weird in a good way. Some of the best feedback may
come from people outside standard institutional channels.

## What Not To Look For

Do not prioritize:

- generic AI influencers,
- LLM prompt-engineering accounts,
- startup founders with no relevant RL/graph/control work,
- people whose only connection is "AI",
- people who only discuss consumer AI tools,
- very famous researchers with no plausible fit or public contact route,
- investors,
- journalists, unless they specifically cover technical RL/robotics research,
- music AI people with no RL/constraint/search angle.

The target is a technically serious, intellectually relevant outreach list.

## Prioritization Rules

For each candidate, assign a priority tier.

## Tier A: Strong Fit

Use Tier A when the person has direct overlap with at least two of:

- hierarchical RL,
- MDP/state/action abstraction,
- quotient/bisimulation/homomorphism ideas,
- graph coarsening/search,
- robotics RL with hidden/constrained geometry,
- open-source RL framework work.

These are the people most worth a carefully personalized email.

## Tier B: Good Fit

Use Tier B when the person has one strong overlap or several adjacent overlaps.

Examples:

- robotics RL person who may appreciate induced hierarchy;
- graph ML person who may appreciate quotient towers;
- RL framework maintainer who may appreciate package/API surfaces;
- music RL person who may appreciate the counterpoint motivating example.

## Tier C: Weak But Plausible Fit

Use Tier C when the person is interesting but the connection is more speculative.

Include only if the contact is unusually relevant, unusually accessible, or
likely to be generous with feedback.

## Desired Output Format

Return a table with these columns:

1. Name
2. Priority Tier
3. Affiliation
4. Role / title
5. Why they are relevant
6. Which category they fit
7. Representative paper/project/link
8. Public contact route
9. Suggested email angle
10. Confidence score from 1 to 5

Also produce a shorter "top 25" list after the full table.

For each candidate, include sources. Prefer official personal pages,
institutional pages, Google Scholar, Semantic Scholar, GitHub, lab pages,
conference pages, or project documentation.

Avoid using only LinkedIn unless no better source exists.

## Suggested Search Queries

Use combinations like:

```text
"hierarchical reinforcement learning" "options" professor
"option discovery" reinforcement learning researcher
"MDP homomorphism" reinforcement learning
"bisimulation metrics" reinforcement learning
"state abstraction" "reinforcement learning"
"quotient MDP" reinforcement learning
"graph coarsening" "reinforcement learning"
"hierarchical robot learning" "CoRL"
"skill discovery" "robot learning"
"coarse-to-fine reinforcement learning"
"graph search" "reinforcement learning" abstraction
"HNSW" "graph machine learning" researcher
"graph contraction" "machine learning" "reinforcement learning"
"Gymnasium" "Farama" maintainer
"Stable-Baselines3" maintainer reinforcement learning
"TorchRL" maintainer
"CleanRL" reinforcement learning
"symbolic music generation" "reinforcement learning"
"counterpoint" "reinforcement learning" music generation
"constrained MDP" "robot learning" hierarchy
```

Also search recent conference proceedings:

- NeurIPS
- ICML
- ICLR
- RLDM
- CoRL
- RSS
- ICRA
- IROS
- AAMAS
- AAAI
- IJCAI

## Outreach Angle Guidance

The project owner should probably send short, low-pressure emails.

The email should not claim the project is finished.

Recommended tone:

> I made a research Python package that induces quotient-style hierarchy over
> discovered RL state/action graphs. It is pre-alpha, but I think it connects to
> your work on [specific topic]. I would be grateful if you found it interesting,
> had feedback, or knew someone else who might care.

Customize the angle by category:

- HRL researchers: "problem-agnostic hierarchy induction without hand-specified
  subtasks"
- abstraction theorists: "quotient/state-action abstraction and lift/refinement"
- robotics people: "hidden constrained geometry and coarse-to-fine control"
- graph ML people: "graph contraction towers and HNSW-like addressing"
- framework maintainers: "Gymnasium-compatible research runtime layer"
- music AI people: "counterpoint as a motivating constrained RL problem"

## Important Honesty Constraints

When describing the project, keep these constraints:

- It is pre-alpha.
- It is research-mode.
- It needs serious benchmarking.
- It is not yet a polished PyPI-ready package for strangers.
- The central idea is stronger than the current implementation.
- The current work is moving toward a more efficient nested partition-table
  runtime.
- The ask is feedback, interest, pointers, or collaboration, not adoption at
  scale.

## One-Paragraph Pitch For Search Context

`state_collapser` is a research Python package for hierarchical reinforcement
learning in problems where the hierarchy is not obvious. It grows a discovered
state/action graph, builds quotient-style towers by contracting graph structure,
and exposes coarse-to-fine runtime surfaces so an agent can learn over abstract
states/actions and later lift back to executable behavior. The mathematical
framing connects HRL, quotient MDP/state abstraction, graph contraction,
HNSW-like hierarchical addressing, and path-volume reduction. The project is
pre-alpha and needs serious benchmarking, but it may interest researchers in
hierarchical RL, abstraction, robotics RL, graph ML, planning/search, RL
frameworks, and structured music-generation RL.

## Final Instruction

Build a list of people who are intellectually likely to care.

Do not optimize for fame.

Optimize for fit, curiosity, and likelihood of giving useful feedback.
