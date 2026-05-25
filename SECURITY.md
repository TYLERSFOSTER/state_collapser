# Security Policy

`state_collapser` is currently a pre-alpha research package.

## Supported Versions

Security review and fixes target the current `main` branch and the latest public
GitHub research release tag. Older pre-alpha tags may receive fixes when doing
so is practical, but they should not be treated as long-term supported release
lines.

## Reporting A Vulnerability

Please report suspected security issues through GitHub Issues once the
repository is public, unless the issue contains sensitive exploit details or
private data. For sensitive reports, contact the Project Owner privately first
and include:

- the affected version or commit,
- the affected surface,
- reproduction steps when available,
- whether the issue involves credentials, local files, generated artifacts, or
  unsafe code execution.

## Current Scope

The current release line is intended for research use. It does not claim mature
production-RL security hardening, sandboxing, model-supply-chain guarantees, or
long-term API stability.

Before public releases, the project should continue to check for:

- committed credentials or private keys,
- absolute local-machine path leakage,
- accidental inclusion of generated artifacts,
- stale version/tag metadata,
- unsafe publishing triggers.
