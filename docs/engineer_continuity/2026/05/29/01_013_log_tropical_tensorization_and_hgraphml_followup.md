# Engineer Continuity Report
## 01_013_log_tropical_tensorization_and_hgraphml_followup

## Date

2026-05-29

## Interval Covered

This report covers the `state_collapser` work completed after:

- `docs/engineer_continuity/2026/05/25/01_012_state_collapser_rl_spine_public_release_hgraphml_and_history_rewrite.md`

The prior report ended after the public-release/security push, the first
`HGraphML` downstream integration, the release-history rewrite, public-release
cleanup, and the `v0.6.0` release posture.

This interval begins with release/discoverability cleanup and then moves through
three major streams:

- public-release metadata and discoverability hardening,
- research-document work around log/tropical/adic analogies and address
  capacity,
- and the first serious tensorization boundary for `state_collapser`, including
  an explicit HGraphML downstream follow-up plan.

At the time this report is written, local `state_collapser` is on:

```text
main
```

with:

```text
7b5d0fd tensorization/lineariztion implemented
```

as both local `HEAD` and `origin/main`.

The `state_collapser` working tree was clean immediately before this continuity
report was added.

## Executive Summary

This interval continued the transition from "research package with strong
runtime machinery" toward "public research infrastructure with clear boundaries
for serious downstream use."

The main completed engineering movement was the first tensorization boundary.
The package now has:

```text
state_collapser.training.linearization
```

for backend-independent numeric records, configuration, reports, and shared
tower encodings, and:

```text
state_collapser.training.torch
```

for optional Torch conversion behind the `ml` extra.

This work deliberately did not turn `state_collapser` into RLlib,
Stable-Baselines3, TorchRL, or a package-owned `.learn(...)` framework. The
object-native training/runtime path remains direct. Tensorization is an explicit
semantic-to-numeric boundary near a learner, benchmark harness, or model
adapter.

The central design rule from the Project Owner was the "tiny hinge" concern:
the tensorization door is useful, but the hinge cannot be so heavy that the
object-native runtime becomes slower or conceptually distorted. The implemented
shape honors that:

```text
runtime/tower/fiber semantics remain object-native
    -> optional linearization boundary
        -> optional Torch batch conversion
```

rather than:

```text
all runtime traffic
    -> mandatory tensorization dispatcher
        -> disabled tensor adapter
            -> object-native learner anyway
```

The second major movement was conceptual/research-facing. The PO developed and
pressed a much stronger analogy between the quotient-tower/log-HRL picture and
log/tropical/adic geometry. The final formulation was not that
`state_collapser` is literally tropical geometry, but that log geometry has
multiple recurring instances where a parametrized contraction creates:

- hierarchical contraction structures,
- reduced/special-fiber computations,
- lifting back into finer fibers or disks,
- and faster calculation by replacing flat fine geometry with scale-organized
  structure.

That language was captured in the log/tropical design documents.

The third movement was downstream discipline around `HGraphML`. HGraphML should
not be forced into RL-specific `ActionSelectionInput` or `TrainingTransition`
objects. The `state_collapser` tensorization work therefore protects a shared
`EncodingRegistry` that can serve HGraphML's graph-message-passing use case
without pretending graph message passing is RL action selection.

## Source Reconstruction

This report is reconstructed from:

- current `state_collapser` `main`,
- recent git log,
- `docs/design/log_tropical_geometry/`,
- `docs/design/logHRL_state_vs_path_address_capacity_note.tex`,
- `docs/design/model_train_surfaces/01_005_big_boy_benchmarking_tensorization_alignment_note.md`,
- `docs/design/tensorization/`,
- `docs/usage/01_010_tensorization_boundary.md`,
- `src/state_collapser/training/linearization.py`,
- `src/state_collapser/training/torch.py`,
- the tensorization test suite additions,
- the tensorization implementation log,
- and the downstream HGraphML instructions at:

```text
/Users/foster/HGraphML/docs/design/tensorization/01_005_hgraphml_state_collapser_tensorization_followup_instructions.md
```

Visible recent commits since the last report include:

```text
10beb3c fixed ci.yml so Codecov is skipped while the repo is private
9b6cf18 Fix Python 3.12 CI
957afeb Add citation metadata
a7a1fae Add release closure continuity addendum
b089acd log idea
bc75603 assets
1654ad3 adic discussion around log contraction
cd4f260 adic discussion around log contraction
e5834b8 added llms.txt for 'LLM SEO'
c9fd12f logHRL
7b5d0fd tensorization/lineariztion implemented
```

## Authorship And PO Attribution

The Project Owner supplied the key conceptual direction for this interval.
Specifically, the PO:

- identified that public-release work was essentially complete but that
  discoverability still needed cheap, standards-friendly metadata,
- requested `CITATION.cff`,
- asked whether `llms.txt` was a real standard and chose to add it only as a
  cheap forward-compatible documentation affordance, not as magic SEO,
- initiated the log/tropical/adic geometry discussion and explicitly framed it
  as a Manin/Kontsevich/Kapranov-style mathematical wandering exercise,
- corrected the assistant away from overclaiming when the log/tropical analogy
  started to hallucinate,
- supplied the sharper statement that the common pattern is parametrized
  contraction producing hierarchical contraction structures, computation on a
  reduction/special fiber, and lifting in disk/fiber movement,
- identified the phrase "loss of fine coordinates while preserving asymptotic
  decision geometry" as the right point of contact,
- pointed out the notational/conceptual problem in the paper around conflating
  address capacity with path-space volume,
- requested a standalone TeX note rather than modifying the main paper,
- imported the downstream `big_boy_benchmarking` tensorization-alignment note,
- identified the major risk that tensorization architecture could become a heavy
  switchable hinge rather than a light conversion boundary,
- chose the exact tensorization namespaces:

```text
state_collapser.training.linearization
state_collapser.training.torch
```

- chose orthogonal enum fields rather than a single overloaded backend mode:

```text
LinearizationState
NumericBackend
TensorDeviceKind
```

- specified that NumPy belongs in the first scope as a backend-independent
  numeric layer but not as a mandatory core dependency,
- specified that fixed discrete action spaces should be first-scope complete
  while ragged fibers remain sidecars,
- specified that linearized records should not be persisted by default,
- insisted that HGraphML compatibility is "REALLY important",
- accepted that HGraphML needs first-pass compatibility coverage but not first
  full tensorization,
- requested the two tensorization blueprints and then the Phase.Stage.Action
  implementation gameplan,
- directed execution of that gameplan on a new branch under the prime-directive
  workflow,
- caught the missing HGraphML downstream action after implementation,
- and requested detailed downstream HGraphML instructions.

Codex supplied:

- public-release/discoverability implementation support,
- `CITATION.cff` and release-continuity addenda,
- `llms.txt`,
- synthesis and documentation of the log/tropical/adic discussion,
- the standalone address-capacity TeX note,
- the tensorization design conversation document,
- the tensorization architecture blueprint,
- the tensorization engineer-usage blueprint,
- the tensorization Phase.Stage.Action implementation gameplan,
- the tensorization implementation,
- tensorization tests and docs,
- validation,
- the HGraphML follow-up instructions document,
- and this continuity report.

## Major Movement 1: Release/Discoverability Cleanup

After the `v0.6.0` release posture was reached, the next public-facing question
was not another code feature but visibility and metadata.

The PO asked whether there were broad online ways to share the work, including
ways that would make it more legible to LLMs. The assistant explained a set of
low-cost public surfaces:

- GitHub topics,
- `CITATION.cff`,
- a tiny GitHub Pages landing site,
- and `llms.txt`.

The PO selected `CITATION.cff` for both `state_collapser` and HGraphML and asked
whether committing/pushing was enough. The answer was yes for GitHub citation UI
and repository metadata: once `CITATION.cff` is committed at repo root, GitHub
can expose citation information.

The PO also asked about GitHub sharing surfaces. The assistant explained that
making the repo public and releasing/tagging is usually enough for basic public
visibility, while GitHub topics, Discussions, and a social preview image improve
discoverability and presentation.

Implemented or discussed during this interval:

- `CITATION.cff` for citation metadata,
- release-detail addenda to continuity reporting,
- Python badge/CI behavior cleanup,
- Codecov skipping while the repo remained private,
- `llms.txt` as a cheap forward-compatible documentation surface.

The important positioning decision was conservative: `llms.txt` was not treated
as a mature standard or "LLM SEO magic." It was treated as a harmless routing
file that may become useful as tool conventions mature.

## Major Movement 2: Log/Tropical/Adic Geometry Discussion

The PO initiated a conceptual discussion with an explicit warning: the claim was
stronger and more speculative than the assistant would naturally want to commit
to. The PO described the paper as potentially "a weird reconfiguring of the
entire log/tropical geometry picture."

The first assistant response undercommitted and softened the claim too much. The
PO corrected this and asked to set aside the strongest claim temporarily, then
focus on the older "coordinatewise logarithm" tropical picture: amoebas,
logarithmic base changes, and the limiting process as a base parameter moves
toward an extreme.

The core analogy that emerged:

```text
tropical/log geometry:
    fine algebraic/analytic structure
        -> logarithmic/valuation contraction
            -> combinatorial or scale-organized skeleton
                -> simplified computation

state_collapser:
    fine state/action path geometry
        -> quotient tower contraction
            -> scale-organized address/fiber structure
                -> cheaper decision/search computation
```

The PO then supplied an image showing p-adic/adic-style hierarchical disk
structures sitting over a base curve with an infinitesimal/adic parameter. The
assistant initially risked overreading it. The PO corrected the framing:

The more honest point is not a single literal identification. The point is that
log geometry repeatedly exhibits a pattern where parametrized contraction,
valuation, degeneration, or log scaling produces hierarchical structures and
computational simplifications.

The refined statement recorded into the log/tropical documents was:

```text
The log is not a shared pun. It is a repeated computational signature of
passing from flat fine geometry to scale-organized computation.
```

Important examples and motifs discussed:

- coordinatewise log maps and amoebas,
- tropicalization as a different but related map,
- adic disks and hierarchical contraction structures,
- reduction/special-fiber computation,
- lifting movement inside disks or fibers,
- max-plus/tropical algebra,
- semiring pictures related to Dudzik/Lessard-style work,
- and the relationship between logarithmic speed-up in the theorem and
  logarithmic scale projection in tropical/log geometry.

Artifacts:

- `docs/design/log_tropical_geometry/01_001_log_tropical_geometry_and_quotient_tower_discussion.md`
- `docs/design/log_tropical_geometry/01_001_log_tropical_geometry_and_quotient_tower_discussion.tex`
- rendered auxiliary/PDF outputs in the same folder

PO attribution:

The core analogy, the correction away from hallucinated specificity, the adic
parameter interpretation, and the stronger philosophical framing are PO-originated.
Codex supplied phrasing, organization, and TeX/Markdown artifact conversion.

## Major Movement 3: Address Capacity Versus Path-Space Volume

The PO identified a serious conceptual issue in the `logHRL` theorem language:
the text was conflating address capacity and path-space volume.

The problematic pattern was:

```text
prod_i b_i >= # discovered states
```

appearing near claims about:

```text
prod_i b_i asymp |Omega|
```

where `Omega` denotes a path set or finite path-volume domain.

The PO correctly pointed out that these are not automatically the same object.
An address system for discovered states and a path-space volume are related
only through an additional modeling map or hypothesis. A product of address
branching factors may cover state addresses while failing to cover path
enumeration volume, or vice versa.

The discussion separated:

- state-address capacity,
- path-address capacity,
- discovered state count,
- finite path volume,
- and the cost of hierarchical search through a decision/address tower.

The assistant clarified that the later theorem structure may not be doomed if
the address family is explicitly path-indexing or if a map from path families to
tower addresses is added. But the notation cannot silently use the same product
for state capacity and path volume.

The PO requested a standalone TeX file rather than changes to the main paper.

Artifact:

```text
docs/design/logHRL_state_vs_path_address_capacity_note.tex
```

Purpose of the artifact:

- explain the notation problem,
- identify when no fix is needed,
- identify when a fix is needed,
- give a possible corrected theorem-shape,
- and preserve the main paper untouched for later deliberate editing.

PO attribution:

The conceptual bug was PO-identified. Codex supplied the standalone explanatory
TeX note.

## Major Movement 4: Big Boy Benchmarking Forced Tensorization To The Surface

A Codex assistant in another repo produced:

```text
docs/design/model_train_surfaces/01_005_big_boy_benchmarking_tensorization_alignment_note.md
```

inside `state_collapser`.

The note argued that serious `big_boy_benchmarking` work is blocked until
`state_collapser` can distinguish:

```text
pre-linearization / current control-flow state_collapser
tensor-capable architecture with tensor path disabled
tensor-capable architecture with tensor path enabled
```

The PO then opened a new tensorization design folder:

```text
docs/design/tensorization/
```

The first design conversation concretized what was known and unknown.

The most important PO concern was mechanical:

```text
Adding a door is fine. But the hinge might become too heavy.
```

Translated into architecture:

Tensorization must not add a switchable abstraction layer that slows down the
object-native runtime or forces all training loops through conversion machinery
even when tensors are disabled.

The resolved design was:

```text
semantic runtime path remains object-native and direct
explicit tensorization boundary appears only near learner/model/benchmark edges
disabled mode validates/reports boundary availability without constructing tensors
```

This became the "tiny hinge rule" in the design docs and gameplan.

Artifacts:

- `docs/design/tensorization/README.md`
- `docs/design/tensorization/design_conversation.md`

## Major Movement 5: Tensorization Blueprints

The PO resolved the open design questions:

Namespace:

```text
state_collapser.training.linearization
state_collapser.training.torch
```

No top-level:

```text
state_collapser.ml
```

Mode fields:

```text
LinearizationState = ABSENT | PRESENT_DISABLED | PRESENT_ENABLED
NumericBackend = NONE | NUMPY | TORCH
TensorDeviceKind = NONE | CPU | CUDA
```

Derived benchmark labels:

```text
none_control_flow
tensor_available_disabled
tensor_enabled_cpu
tensor_enabled_cuda
```

NumPy:

```text
yes in first scope, but not as unconditional core dependency
```

Torch:

```text
behind the ml extra
```

Fixed discrete versus ragged:

```text
fixed discrete action spaces first
ragged fibers and variable action-cell vocabularies as sidecars
full ragged tensorization deferred
```

Persistence:

```text
persist config/report, not every linearized record
```

HGraphML:

```text
first-pass compatibility coverage is important
first-pass full HGraphML tensorization is not required
```

Tiny Torch model:

```text
allowed only as tests/examples smoke model
not a package policy model
```

Artifacts:

- `docs/design/tensorization/01_001_tensorization_architecture_blueprint.md`
- `docs/design/tensorization/01_002_tensorization_engineer_usage_blueprint.md`
- `docs/design/tensorization/01_003_tensorization_implementation_gameplan.md`

The two blueprints were intentionally paired. The architecture blueprint defined
the package internals; the engineer-usage blueprint forced usability questions
early so the implementation would not create a theoretically clean but unusable
surface.

## Major Movement 6: Tensorization Implementation

The PO then approved execution of:

```text
docs/design/tensorization/01_003_tensorization_implementation_gameplan.md
```

following `prime_directive`, with a new implementation branch.

The implementation created the backend-independent module:

```text
src/state_collapser/training/linearization.py
```

Key implemented surfaces:

- `LinearizationState`
- `NumericBackend`
- `TensorDeviceKind`
- `LinearizationConfig`
- `LinearizationReport`
- `EncodingRegistry`
- `LinearizedActionSelectionInput`
- `LinearizedTrainingTransition`
- `ConversionTiming`
- `numpy_availability()`
- `torch_availability()`
- `build_linearization_report(...)`
- `time_conversions(...)`
- `linearize_action_selection_input(...)`
- `linearize_training_transition(...)`
- `export_linearized_record(...)`

The implementation created the Torch-specific module:

```text
src/state_collapser/training/torch.py
```

Key implemented surfaces:

- `TorchDecisionBatch`
- `TorchTransitionBatch`
- `action_decision_from_logits(...)`

The Torch module uses local Torch imports. Torch is not imported by:

```text
state_collapser.training.linearization
```

and Torch-specific symbols are not exported from:

```text
state_collapser.training.__init__
```

Backend-independent symbols are exported from:

```text
src/state_collapser/training/__init__.py
```

so engineers can write:

```python
from state_collapser.training import EncodingRegistry
from state_collapser.training import LinearizationConfig
```

without touching Torch.

## Major Movement 7: Shared Encoding Registry

The most important HGraphML-facing implementation piece is:

```python
EncodingRegistry.from_tower(...)
```

This can build a stable numeric vocabulary from a `PartitionTower` without any
RL-specific training objects.

It encodes:

- base states,
- base edges,
- primitive action identities,
- state cells,
- action collections,
- action cells,
- tower tiers,
- stage ids,
- fiber ids,
- frozen behavior ids,
- fiber-departure reasons,
- and other small labels where needed.

The registry deliberately serves a broader role than "RL observation encoder."
It is shared tower/cell/edge vocabulary, which is exactly the surface HGraphML
will later need for graph-message-passing tensorization.

This satisfies the PO's HGraphML concern at the upstream level:

```text
first-pass tensorization is RL/counterpoint-driven,
but shared tower encoding is HGraphML-compatible from day one
```

## Major Movement 8: Tensorization Tests

New tests were added:

```text
tests/training/test_linearization_config.py
tests/training/test_encoding_registry.py
tests/training/test_linearized_records.py
tests/training/test_torch_batches.py
tests/examples/test_torch_tensor_boundary_smoke_model.py
```

Coverage includes:

- enum value stability,
- config serialization,
- invalid mode rejection,
- report serialization,
- backend availability fields,
- no backend-independent module-level Torch symbol,
- registry construction from `PartitionTower`,
- HGraphML-compatible registry use without RL objects,
- tower/state/edge/cell id encoding,
- action-mask padding,
- tower-position padding,
- stage/fiber metadata encoding,
- strict versus non-strict observation behavior,
- transition conversion,
- Torch batch conversion,
- CUDA availability behavior,
- and a tiny local Torch smoke model converting logits back to
  `ActionDecision`.

Torch is not installed in the local environment, so Torch-specific tests were
collected and skipped cleanly.

## Major Movement 9: Tensorization Documentation

The implementation added:

```text
docs/usage/01_010_tensorization_boundary.md
```

This is the engineer-facing usage guide for the new surface.

It explains:

- object-native mode,
- tensor-capable disabled mode,
- tensor-enabled CPU mode,
- tensor-enabled CUDA mode,
- action-mask semantics,
- tower-position ids,
- fiber-conditioned training,
- HGraphML boundary,
- artifact reporting,
- and the explicit non-goal of becoming a full RL framework.

Routing updates were made in:

```text
README.md
docs/package_usage.md
docs/public_api.md
```

The root docs now point tensor/model-boundary users to:

```text
docs/usage/01_010_tensorization_boundary.md
```

## Major Movement 10: Validation Results

The tensorization implementation log records the validation in:

```text
docs/design/tensorization/01_004_tensorization_implementation_log.md
```

Important validation results:

```text
uv run ruff check
All checks passed.
```

```text
uv run mypy
Success: no issues found in 100 source files.
```

```text
uv run pytest
477 passed, 4 skipped
```

Focused tensorization validation:

```text
uv run pytest tests/training -k "linearization or torch"
5 passed, 3 skipped, 66 deselected
```

HGraphML/tower/training compatibility slice:

```text
uv run pytest tests/tower/partition/test_hgraphml_downstream_compatibility.py tests/tower/partition tests/training
147 passed, 3 skipped
```

Training/example compatibility slice:

```text
uv run pytest tests/training tests/examples/test_plate_support_env_fiber_conditioned_stage.py tests/examples/test_training_semantics_shared.py
75 passed, 3 skipped
```

Torch marker validation:

```text
uv run pytest -m requires_torch tests/training
3 skipped, 71 deselected
```

Known validation limitation:

Torch and CUDA behavior were not exercised on real installed Torch/CUDA in this
environment. The tests were collected and skipped cleanly. Actual Torch/CUDA
runtime validation remains future work in an environment with the `ml` extra
installed.

## Major Movement 11: HGraphML Follow-Up Instructions

After the tensorization implementation, the PO asked:

```text
What about HGraphML. Didn't our conversation include something we needed to do there?
```

The correct answer was yes, but with a scope distinction.

The upstream `state_collapser` implementation handled HGraphML as a
compatibility constraint:

- shared `EncodingRegistry`,
- no RL-specific object requirement,
- no Torch requirement,
- partition-tower compatibility tests green.

It did not modify `/Users/foster/HGraphML`.

The PO then requested detailed HGraphML-side instructions.

Artifact created in HGraphML:

```text
/Users/foster/HGraphML/docs/design/tensorization/01_005_hgraphml_state_collapser_tensorization_followup_instructions.md
```

The HGraphML instruction document says:

- wait until HGraphML depends on a `state_collapser` commit/tag exposing
  `EncodingRegistry`,
- add a HGraphML compatibility test importing
  `state_collapser.training.EncodingRegistry`,
- build an encoding registry from a real `TowerBundle`,
- verify graph nodes and edges remain encodable,
- verify node fibers and edge fibers remain compatible,
- avoid fake `ActionSelectionInput` construction,
- avoid `TrainingTransition`,
- avoid routing graph message passing through `TorchDecisionBatch`,
- optionally add a small helper around `TowerBundle`,
- document that this is shared tower encoding rather than RL tensorization,
- and defer full HGraphML tensorized graph-message-passing kernels.

At the time of this report, the HGraphML follow-up document is untracked in the
HGraphML repo under:

```text
docs/design/tensorization/
```

This report does not stage or commit that downstream file.

## Current State Of `state_collapser`

Current `state_collapser` branch:

```text
main
```

Current `HEAD`:

```text
7b5d0fd tensorization/lineariztion implemented
```

Current relationship:

```text
HEAD -> main, origin/main, origin/HEAD
```

Current state before this report:

```text
clean
```

After this report is added, the expected new uncommitted file is:

```text
docs/engineer_continuity/2026/05/29/01_013_log_tropical_tensorization_and_hgraphml_followup.md
```

## Current State Of HGraphML

HGraphML has an untracked downstream instruction folder:

```text
docs/design/tensorization/
```

containing:

```text
01_005_hgraphml_state_collapser_tensorization_followup_instructions.md
```

No HGraphML source implementation was performed in this interval. The document
is an instruction/design artifact for the next HGraphML-side compatibility pass.

## Open Follow-Ups

### State Collapser

The tensorization boundary is implemented, but remaining future work includes:

- validating Torch tests in an environment with the `ml` extra installed,
- validating CUDA mode on real CUDA hardware,
- deciding whether NumPy should remain only optional or get a small `numeric`
  extra,
- adding serious `big_boy_benchmarking` comparisons:

```text
none_control_flow
tensor_available_disabled
tensor_enabled_cpu
tensor_enabled_cuda
```

- extending artifact/manifest integration for benchmark outputs,
- and eventually designing full ragged tensor support if benchmarks demand it.

### HGraphML

The next HGraphML-side work is exactly what the new instruction document says:

- update HGraphML's `state-collapser` dependency to a commit/tag containing
  `EncodingRegistry`,
- add a compatibility test for `EncodingRegistry.from_tower(...)`,
- verify `TowerBundle` node/edge fibers remain compatible,
- optionally add a helper such as `build_encoding_registry(bundle)`,
- and document that this is tower encoding for graph message passing, not an RL
  tensor path.

### Research Document

The log/tropical analogy is now recorded, but it remains research-facing and
should be handled carefully:

- avoid literal overclaiming,
- distinguish coordinatewise log/tropicalization/adic reduction as different
  maps,
- preserve the deeper common pattern of scale-organized computation,
- and revisit the main `logHRL` theorem notation around state address capacity
  versus path volume before using the theorem as a polished paper claim.

## Final Continuity Note

The most important durable result of this interval is that `state_collapser`
now has the first version of the numerical boundary it needed for serious
benchmarking and downstream ML integration, without sacrificing the package's
identity.

It is still not a mature RL framework.

It is now closer to being something more specific and more useful:

```text
a quotient-tower structural layer with object-native semantics,
explicit fiber-conditioned training surfaces,
and an optional semantic-to-numeric boundary for learners and benchmarks
```

The PO's HGraphML insistence also paid off architecturally. Without that
pressure, the tensorization surface could easily have collapsed into an
RL-only observation/action encoder. Instead, the central encoding object is
shared tower/cell/edge infrastructure, which is the right shape for both:

```text
RL/counterpoint:
    ActionSelectionInput
        -> LinearizedActionSelectionInput
            -> TorchDecisionBatch
```

and:

```text
HGraphML:
    TensorGraph
        -> PartitionTower
            -> EncodingRegistry
                -> graph-message-passing-compatible stable ids
```

That distinction should be preserved in future work.
