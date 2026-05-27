# state_collapser Discoverability Follow-Up

**Date:** 2026-05-27

## Current Status

`state_collapser` already has the most important public-discoverability pieces:

- clear root README positioning;
- GitHub release/tag posture;
- truthful badges;
- `CITATION.cff`;
- package metadata in `pyproject.toml`;
- `SECURITY.md`;
- GitHub topics, per Project Owner;
- public-history cleanup;
- downstream cross-linking with `HGraphML`.

## Remaining Useful Work

### Add `llms.txt`

Add a root-level `llms.txt` that gives agents and retrieval systems a compact
map of the repository.

Recommended contents should point to:

- `README.md`;
- `EVALUATION.md`;
- `docs/usage/01_001_what_state_collapser_is.md`;
- `docs/usage/01_002_tower_runtime_mental_model.md`;
- `docs/usage/01_003_training_surface_quickstart.md`;
- `docs/usage/01_009_downstream_applications.md`;
- `docs/api_notes`;
- `docs/design/logHRL.pdf`;
- `SECURITY.md`;
- `CITATION.cff`.

### Check Release-Tag Inclusion Of Citation Metadata

`CITATION.cff` exists on `main`, but it appears to have been added after the
original clean `v0.6.0` baseline. Decide whether that is fine, or whether a
future `v0.6.1` release should include citation metadata inside the release tag
itself.

Do not silently retag `v0.6.0`.

### Verify GitHub About Metadata

Confirm the GitHub sidebar has a concise description such as:

```text
Quotient-tower runtime and training surfaces for hierarchical structure in transition systems.
```

If a homepage URL is useful, point it at the GitHub repo or a future docs page.

### Social Preview Image

Add a GitHub social preview image so shared links render professionally on
LinkedIn, Slack, Discord, and other unfurling surfaces.

Recommended content:

```text
state_collapser
quotient towers for hierarchical reinforcement learning
```

Use the existing logo assets if they render cleanly at GitHub's recommended
preview dimensions.

### Discussions Decision

Decide whether to enable GitHub Discussions.

Recommended posture:

- enable Discussions if the Project Owner wants public questions and conceptual
  discussion around quotient towers;
- leave Discussions off if the repo should avoid an extra public moderation
  surface for now.

### Optional Metadata Tightening

Consider adding `Security` and `Source` URLs to `[project.urls]` in
`pyproject.toml`.

Current metadata is already acceptable, so this is optional polish rather than
a release blocker.

## Non-Goals

Do not treat these as reasons to delay the existing public release:

- lack of `llms.txt`;
- no social preview image;
- no Discussions tab;
- citation metadata landing after `v0.6.0`.

These are discoverability polish items, not core release-hardening blockers.
