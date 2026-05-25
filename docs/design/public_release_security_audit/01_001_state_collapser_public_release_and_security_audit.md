# state_collapser Public Release And Security Audit

## Status

Hard public-release and security audit for `state_collapser`, modeled on the
HGraphML release audit but adjusted for this repository's role as the upstream
package.

Audit date:

```text
2026-05-25
```

Repository audited:

```text
[state_collapser repository root]
```

Current branch during audit:

```text
main
```

Current audited HEAD:

```text
f2e6aee repo-wide documentation update
```

Current package version:

```text
state-collapser 0.6.0
```

Current latest local tag:

```text
v0.5.0 -> fea2ce5 prepare v0.5.0 release and fix CI typing
```

## Executive Verdict

`state_collapser` is mechanically close to a lightweight public research
release, but it is not yet clean enough for a confident public release from the
current tree.

The codebase itself is in strong shape:

- full tests pass,
- Ruff passes,
- mypy passes,
- isolated package build succeeds,
- `twine check` succeeds,
- CI and PyPI publish workflows exist,
- the package has real runtime, examples, training surfaces, benchmark smoke
  tools, and extensive documentation.

The blockers are release/security hygiene and public dependency visibility, not
core runtime correctness.

The highest-priority release blockers at the start of the audit were:

1. The repository is not publicly visible from unauthenticated web checks.
   - **PO Reply:**
   At what stage in public release should I change that on the Github side?
   - **Codex Response:**
   Make the repository public after the local-path cleanup, version bump, and
   HGraphML compatibility smoke test are committed, but before you create the
   GitHub release/tag that downstream users are supposed to consume. In other
   words: keep it private while we are cleaning embarrassing or machine-local
   release hygiene; make it public for the final verification pass. The order I
   recommend is: clean docs and metadata, bump version, commit, push, switch
   GitHub visibility to public, verify badges/CI/public clone/public tag fetch,
   then create the release. HGraphML should not be switched to rely on the public
   Git URL until this public-fetch check succeeds.
2. `state-collapser` is not visible on PyPI from unauthenticated web checks.
   - **PO Reply:** We will hold off on PyPl release. This will be lighter public release. No PyPl release unitl *real* benchmarking is done.
   - **Codex Response:**
   Agreed. That changes the release target from "PyPI pre-alpha package" to
   "public GitHub research release." PyPI should no longer be treated as an
   immediate blocker or immediate action item. It remains future work after real
   benchmarking, stronger benchmark artifacts, and a more settled package
   story. For now, the correct release route is: public GitHub repo, public
   tags, honest release notes, source install instructions, and HGraphML pinned
   to a public Git tag or commit. The publish workflow can remain in the repo,
   but it should not be triggered yet.
3. The current `main` contains post-`v0.5.0` changes while `pyproject.toml` and
   `_version.py` still say `0.5.0`.
   - **PO Reply:**
   Clearly we need to fix this. Please explain `v0.6.0` versus `v1.0.0` to me.
   - **Codex Response:**
   `v0.6.0` is the right kind of next release number if we are releasing the
   current post-`v0.5.0` work as another pre-alpha research milestone. It says:
   the package has meaningfully advanced, but the public API, benchmark claims,
   training framework maturity, and downstream compatibility contract are still
   not stable enough to promise long-term support.

   `v1.0.0` would say something much stronger: stable public API, clear install
   story, mature documentation, settled compatibility policy, serious benchmark
   evidence, and confidence that downstream users can build against the package
   without near-term breakage. We are not there yet. Holding PyPI until serious
   benchmarking makes `v1.0.0` even more clearly premature.

   I would use `v0.6.0`, not `v0.5.1`, because the current work is not just a
   bugfix patch over `v0.5.0`: it adds the HGraphML downstream compatibility
   posture, public-release hardening, documentation cleanup, and possibly a new
   compatibility test. That is minor-version material in a pre-1.0 project.
4. Many public-facing docs contain absolute local paths rooted at the PO's local
   machine layout.
   - **PO Reply:**
   Correct these.
   - **Codex Response:**
   Done for the scanned text corpus. I removed the actual local-machine path
   prefix from root docs and docs, then tightened the high-traffic public docs
   (`CONTRIBUTING.md`, `EVALUATION.md`, README-adjacent docs, usage docs, and
   API notes) back into relative links where appropriate. A follow-up scan now
   finds no absolute user-home or private temp-directory path strings in the
   audited repo text. Some historical design/continuity markdown now uses neutral
   placeholders such as `[state_collapser repository root]` where preserving the
   exact historical reference mattered more than maintaining a clickable link.
5. The source distribution includes the full docs/provenance corpus, which is
   acceptable for research release only if local path leakage is cleaned or
   intentionally accepted.
   - **PO Reply:**
   I very much want full docs/provenance corpus, exactly because this is research... like lab notes I guess... but yes correct all local path leakage.
   - **Codex Response:**
   Agreed. For this project, the broad source distribution is a feature, not a
   mistake: it makes the package legible as a research artifact with lab-note
   provenance. The policy should be: keep the docs, continuity reports,
   prime-directive material, design docs, and code reviews in the public
   research repo/source archive, but sanitize local-machine paths and secrets.
   I cleaned the local path leakage in the scanned text corpus. The next audit
   should verify the rebuilt sdist contains the full provenance corpus but no
   local-machine path strings.
6. HGraphML now depends on this package; public release must preserve the
   partition-tower surfaces HGraphML calls or provide a migration path.
   - **PO Reply:**
   What is the correct way to carry out this "preservation"?
   - **Codex Response:**
   The correct preservation mechanism is not "freeze the entire internal API."
   It is to define a small downstream compatibility contract and test it. For
   the immediate release, add an HGraphML-shaped compatibility test inside
   `state_collapser`: build a tiny known directed graph, wrap nodes/actions as
   `State`, `PrimitiveAction`, and `BaseEdge`, call
   `build_partition_tower_full(...)` with a label schema, and recover node/edge
   fibers from the same `PartitionTower` registry/layer queries HGraphML uses.

   Then document those queries as provisional downstream-facing surfaces. Future
   refactors may replace them with a cleaner official readout adapter, but they
   should not silently break HGraphML. If we need to change them, the release
   should include either a compatibility shim or a migration note for HGraphML.

This is not a "do not release" conclusion. It is a "release after a targeted
hardening pass" conclusion.

## Follow-Up Implementation Status

The PO's audit replies changed the target from "PyPI-ready pre-alpha package" to
"public GitHub research release." The follow-up implementation pass therefore
did the release-hardening work needed for that target while deliberately
deferring PyPI.

Implemented during the follow-up pass:

- bumped package metadata and runtime version to `0.6.0`,
- updated package metadata to canonical GitHub URLs, a changelog URL,
  `Typing :: Typed`, a broader quotient-tower description, and the currently
  validated Python `3.11`/`3.12` range,
- changed PyPI publishing from automatic GitHub-release publication to
  manual-only `workflow_dispatch`,
- updated README installation language to advertise source/GitHub-tag installs
  rather than PyPI,
- commented out the active PyPI Python-version badge while PyPI is intentionally
  deferred,
- added `SECURITY.md`,
- added an HGraphML-shaped partition-tower compatibility test,
- cleaned local-machine path leakage across the scanned root/docs text corpus
  while preserving the full research/provenance documentation corpus.

## Release Readiness By Target

| Release target | Current readiness | Verdict |
|---|---:|---|
| Local research development | 95% | Ready |
| Private GitHub milestone | 90% | Ready |
| Public GitHub pre-alpha research release | 85% | Ready after final public-visibility and CI verification |
| PyPI pre-alpha research release | 65% | Mechanically viable, but intentionally deferred until serious benchmarking |
| HGraphML upstream dependency release | 80% | Needs public repo/tag fetch verification; in-repo compatibility smoke now exists |
| Benchmark-supported speed-up release | 35% | Not ready; benchmark smoke exists, serious benchmark evidence does not |
| Mature RL framework release | 20% | Explicitly out of scope |

## Bottom-Line Recommendation

Do not publish the current dirty `main` tree as `0.5.0`.

Instead:

1. Release the current post-`v0.5.0` work as `v0.6.0`.
2. Keep the release explicitly GitHub-first and research-mode.
3. Make the GitHub repository publicly visible before HGraphML depends on it by
   Git URL.
4. Ensure HGraphML uses a public Git tag or commit that unauthenticated users can
   fetch.
5. Preserve the full research/provenance documentation corpus, but keep local
   path leakage cleaned.
6. Keep PyPI publication disabled/manual until serious benchmarking is complete.
7. Tag and publish the GitHub release only after local validation and public CI
   pass.

Safe release language:

```text
state_collapser is a pre-alpha research package for constructing quotient-tower
structure over discovered transition systems and exposing tower-aware training
surfaces.
```

Unsafe release language:

```text
state_collapser is a mature RL framework.
```

Also unsafe without benchmark artifacts:

```text
state_collapser speeds up RL training.
```

## Audit Method

The audit inspected:

- git branch, status, tags, and remote,
- root release docs,
- package metadata,
- CI and publish workflows,
- source layout and test layout,
- `.gitignore`,
- local generated artifacts,
- tracked generated artifacts,
- sdist and wheel contents,
- root docs and design docs for local path leakage,
- secret/key/token-like patterns,
- PyPI and GitHub public visibility,
- HGraphML downstream dependency surfaces,
- local validation results.

Commands run included:

```bash
git status --short
git branch --show-current
git log --oneline --decorate --max-count=12
git tag --list --sort=-creatordate
git remote -v
rg --count-matches "[absolute user-home path pattern]" README.md CONTRIBUTING.md EVALUATION.md CHANGELOG.md pyproject.toml docs
rg -n "BEGIN RSA|BEGIN OPENSSH|PRIVATE KEY|api[_-]?key|password|secret|token|pypi|twine|codecov|CODECOV|TWINE|PYPI" README.md CONTRIBUTING.md EVALUATION.md CHANGELOG.md pyproject.toml .github docs src tests
git ls-files | rg "\.DS_Store|dist/|coverage\.xml|\.coverage|\.pytest_cache|\.ruff_cache|\.mypy_cache|\.venv|\.aux$|\.log$|\.out$|\.toc$|\.fls$|\.fdb_latexmk$|\.synctex|__pycache__|\.pyc$"
.venv/bin/python -m pytest tests
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy src
.venv/bin/python -m build --sdist --wheel --outdir [temporary build directory]
.venv/bin/python -m twine check [temporary build directory]/*
```

Public web checks were also performed for:

```text
https://pypi.org/project/state-collapser/
https://github.com/TYLERSFOSTER/state_collapser
https://github.com/TYLERSFOSTER/state_collapser/releases
```

Those public checks returned not-found/not-public behavior at audit time.

## Current Git State

The working tree was dirty at audit start from the HGraphML downstream
documentation pass:

```text
M CHANGELOG.md
M CONTRIBUTING.md
M README.md
M docs/api_notes/partition_tower.md
M docs/package_usage.md
M docs/public_api.md
M docs/usage/01_001_what_state_collapser_is.md
?? docs/usage/01_009_downstream_applications.md
```

This was expected in the current work session, but it matters for release:

```text
Do not build and publish from a dirty working tree.
```

The latest local tag is `v0.5.0`, but current `main` includes commits after
that tag. At audit start, package metadata still said `0.5.0`, which meant
building from current `main` would create a new artifact with the same version
number as the already-tagged release but different contents.

That was a release blocker. The follow-up pass bumps the package to `0.6.0`.

Recommended fixes:

- If publishing exactly `v0.5.0`, publish artifacts built from tag `v0.5.0`.
- If publishing current `main`, bump to `0.5.1` or `0.6.0` before building.
- Because the HGraphML downstream documentation and compatibility guard are
  included, prefer the new minor pre-1.0 release `v0.6.0` rather than silently
  replacing `0.5.0`.

## Validation Results

### Tests

```text
.venv/bin/python -m pytest tests
467 passed
```

The test suite is broad for a pre-alpha research package. It covers:

- core state/action/edge/reward structures,
- hidden/explored/vista graph layers,
- contraction policies,
- quotient/coset/projection behavior,
- partition tower construction and updates,
- runtime snapshots,
- exploit/explore control,
- training inputs, collectors, learners, masks, transitions, and stages,
- example environment geometry and runtime integration,
- Gymnasium wrapper behavior,
- benchmark smoke tooling.

The count is `467 passed` after adding the HGraphML-shaped compatibility test.

### Lint

```text
.venv/bin/python -m ruff check .
All checks passed
```

### Typing

```text
.venv/bin/python -m mypy src
Success: no issues found in 88 source files
```

### Build

The first isolated build attempt during the original audit failed under
network-restricted conditions because `hatchling` could not be fetched. With
network access for build dependencies, the build succeeded. After the follow-up
version bump, the release-validation build should produce:

```text
state_collapser-0.6.0.tar.gz
state_collapser-0.6.0-py3-none-any.whl
```

### Twine Check

```text
.venv/bin/python -m twine check [temporary build directory]/*
PASSED
```

The package is mechanically buildable and PyPI metadata is syntactically valid.

## Public Visibility Audit

### GitHub Repository

Local remote:

```text
origin git@github.com:TYLERSFOSTER/state_collapser
```

Root README badges point to:

```text
https://github.com/TYLERSFOSTER/state_collapser/actions/workflows/ci.yml
https://github.com/TYLERSFOSTER/state_collapser/releases
```

Public unauthenticated web check:

```text
https://github.com/TYLERSFOSTER/state_collapser
```

returned not-found/not-public behavior during the audit.

Impact:

```text
HGraphML and strangers cannot depend on a Git URL if the repository is private
or otherwise not publicly fetchable.
```

Recommendation:

```text
Make the GitHub repository public before using it as HGraphML's public upstream
dependency.
```

### PyPI Project

Public unauthenticated web check:

```text
https://pypi.org/project/state-collapser/
```

returned not-found behavior during the audit.

Impact:

```text
pip install state-collapser is not currently a public install path.
```

Recommendation:

```text
Do not let HGraphML advertise state-collapser as a registry dependency until
state-collapser is actually published to PyPI. For the GitHub-only research
release, HGraphML should depend on a public Git tag or commit instead.
```

## Package Metadata Audit

Current metadata strengths:

- package name: `state-collapser`
- version field exists and now reflects the planned `0.6.0` release
- MIT license expression
- README-backed long description
- Python `>=3.11,<3.13`, matching the currently validated CI range
- classifiers for pre-alpha/research/Python 3.11/3.12
- `Typing :: Typed`
- keywords exist
- runtime dependency is small: `pillow>=12.2.0`
- optional extras are separated:
  - `dev`
  - `rl`
  - `ml`
- project URLs exist
- wheel includes `py.typed`
- changelog URL exists

Release weaknesses at audit start and follow-up status:

1. **Version was stale relative to current `main`.**

   Current tree is post-`v0.5.0`, and metadata previously still said `0.5.0`.
   Follow-up status: fixed by bumping `pyproject.toml` and
   `src/state_collapser/_version.py` to `0.6.0`.

2. **Project URLs may not match the actual public repository identity.**

   Follow-up status: fixed by making project URLs canonical with
   `https://github.com/TYLERSFOSTER/state_collapser`.

3. **No upper Python bound.**

   Follow-up status: fixed by setting `requires-python = ">=3.11,<3.13"` until
   Python `3.13+` is explicitly covered by CI.

4. **No `Typing :: Typed` classifier.**

   Follow-up status: fixed.

5. **No `Changelog` project URL.**

   Follow-up status: fixed.

6. **Description is narrower than current package posture.**

   Previous description said:

   ```text
   Tools for recursive pseudo-dimensional reductions of RL state spaces.
   ```

   Follow-up status: fixed with a broader quotient-tower/runtime/training
   description while keeping the project in pre-alpha research posture.

## Wheel Audit

Wheel contents are package-focused:

```text
state_collapser/*
state_collapser-0.6.0.dist-info/*
```

The wheel does not include:

- tests,
- docs,
- design files,
- continuity reports,
- prime-directive docs,
- local caches,
- build artifacts,
- LaTeX auxiliary files.

Wheel status:

```text
good
```

## Sdist Audit

The source distribution is much broader. It includes:

- package source,
- tests,
- root docs,
- `.github` workflows,
- assets and images,
- design docs,
- PDFs and TeX sources,
- code reviews,
- prime-directive docs,
- engineer continuity reports,
- outreach docs.

It does not appear to include generated caches, local venvs, `dist/`, coverage
files, or LaTeX auxiliary build artifacts.

This is acceptable only if the project intentionally wants a research/provenance
sdist. It is not a polished minimal package sdist.

Release decision needed:

```text
Should the PyPI sdist be a broad research archive, or should PyPI receive a
clean package-focused sdist while the full provenance remains in GitHub?
```

Because the PO has previously preferred keeping design/provenance material in
research sdists, the stronger immediate requirement is not exclusion. The
stronger immediate requirement is local-path cleanup.

## Security Audit

### Secrets

No obvious committed secrets, private keys, API keys, passwords, or PyPI tokens
were found by pattern scan.

The scan did find words such as `token` and `secret` in ordinary prose, for
example in prime-directive model-process discussion. Those are not credential
values.

### GitHub Actions Security

CI workflow:

```text
.github/workflows/ci.yml
```

Strengths:

- runs on push to `main` and pull requests,
- tests Python `3.11` and `3.12`,
- installs with `uv`,
- runs Ruff, mypy, pytest with coverage, and build.

Risks / follow-ups:

- Codecov action is present. Tokenless upload may be fine for public repos, but
  this should be verified after the repo is public. If a token is required, it
  should live in GitHub secrets, not in the repo.
- CI currently installs `dev` and `rl` extras, but not `ml`; tests marked
  `requires_torch` may be skipped or not exercised depending on test selection.
  If ML/HGraphML compatibility becomes release-critical, add an ML/downstream
  CI job.

Publish workflow:

```text
.github/workflows/publish.yml
```

Strengths:

- originally triggered on GitHub release publication,
- uses PyPI trusted publishing via `id-token: write`,
- does not require a committed PyPI token.

Risks / follow-ups:

- Follow-up status: changed to manual-only `workflow_dispatch` so a GitHub
  research release does not accidentally publish to PyPI.
- PyPI trusted publisher must be configured on the PyPI project before publish
  works.
- Because the PyPI project does not appear public yet, the first publish must be
  planned deliberately.
- Release publication from a stale version would create a bad artifact if the
  version is not bumped or the tag is wrong; the follow-up pass bumps the next
  release to `0.6.0`.

### Local Path Leakage

This is the biggest security/public-release hygiene issue.

Root docs contain absolute local paths:

```text
CONTRIBUTING.md: 39 matches
EVALUATION.md: 10 matches
```

Many design and continuity docs also contain absolute local paths rooted at the
PO's machine.

This is not a credential leak. It is still a public-release problem because it:

- exposes local machine layout,
- makes docs less portable,
- makes markdown links unusable for strangers,
- creates an avoidable privacy/professionalism issue,
- would be included in the current broad sdist.

Recommended policy:

```text
No public-facing root docs should contain absolute user-home paths.
Use relative markdown links in README, CONTRIBUTING, EVALUATION, docs/usage,
docs/api_notes, docs/package_usage, and docs/public_api.
```

For historical continuity/design docs, choose one of two policies:

1. Clean all absolute local paths before public release.
2. Keep internal history intact in GitHub but exclude those docs from PyPI sdist.

If the sdist includes all docs, option 1 is safer.

### Generated / Local Files

The working directory contains local generated files and caches, including:

- `.venv/`
- `.mypy_cache/`
- `.ruff_cache/`
- `.pytest_cache/`
- `.coverage`
- `coverage.xml`
- `dist/`
- local LaTeX build files
- `.DS_Store`

These appear ignored and not tracked. `git ls-files` did not report tracked
generated artifacts matching the checked patterns.

This is good.

Recommendation:

```text
Before release, run git status --ignored and verify no ignored artifacts are
staged. Do not use git add -f on generated files.
```

## Documentation Audit

### README

Strengths:

- clear high-level explanation,
- honest comparison with RLlib and Stable-Baselines3,
- explains the structural-layer role,
- includes HGraphML as downstream graph-dataflow application,
- documents install extras,
- points users to usage, API notes, contributing, evaluation, and design docs,
- does not put the full TODO list back in the main room.

Weaknesses:

- installation was local-development first.
- Follow-up status: fixed by separating local editable install from public
  GitHub-tag install and by explaining that PyPI is intentionally deferred.
- PyPI Python-version badge pointed to a package that does not appear public
  yet.
- Follow-up status: fixed by commenting out the active PyPI Python-version badge.
- GitHub badges point to a repo that does not appear public yet.
- Release badge points to releases that do not appear public yet.

Recommendation:

```text
Keep the badge row, but only after the repo and package are public enough that
the badges render correctly.
```

### CONTRIBUTING

Strengths:

- realistic roadmap,
- HGraphML downstream compatibility is now represented,
- development/validation commands are clear,
- design authority is explicit.

Weakness:

```text
CONTRIBUTING.md contained 39 absolute local paths at audit start.
```

Follow-up status: fixed in the scanned text corpus. This mattered because
CONTRIBUTING is a high-traffic public file.

### EVALUATION

Strengths:

- clear current evaluation philosophy,
- separates structural, behavioral, and performance evaluation,
- does not pretend benchmark evidence is mature,
- includes current runnable entry points and benchmark-smoke posture.

Weakness:

```text
EVALUATION.md contained 10 absolute local paths at audit start.
```

Follow-up status: fixed in the scanned text corpus.

### Usage And API Notes

Strengths:

- small, routing-oriented docs,
- public API policy is appropriately conservative,
- partition tower note now identifies HGraphML-facing queries,
- downstream application note exists.

Risk:

The public API policy says most surfaces are provisional, but HGraphML depends
on some of them now. This is not a contradiction, but it creates a compatibility
obligation:

```text
pre-alpha does not mean break downstream consumers silently.
```

## HGraphML Downstream Compatibility Audit

HGraphML is now a real downstream consumer. Its current adapter depends on:

- `state_collapser.core.action.PrimitiveAction`
- `state_collapser.core.edges.BaseEdge`
- `state_collapser.core.state.State`
- `state_collapser.tower.partition.ContractionSchema`
- `state_collapser.tower.partition.LabelBlockSchema`
- `state_collapser.tower.partition.PartitionTower`
- `state_collapser.tower.partition.tower.build_partition_tower_full`
- `PartitionTower.state_layers`
- `PartitionTower.registry`
- state layer cell/member queries,
- registry edge id, edge lookup, and source/target id queries.

This means HGraphML is not just using top-level `__version__`. It is using
pre-alpha but real partition runtime surfaces.

Current issue:

```text
state_collapser did not yet have an in-repo compatibility test shaped like the
HGraphML adapter at audit start.
```

Recommendation:

Follow-up status: option 1 is implemented. The upstream suite now includes an
HGraphML-shaped test that builds a known graph, calls
`build_partition_tower_full`, and recovers node/edge fibers from the same
registry/layer surfaces HGraphML uses. Option 3 remains the best long-term API
direction.

## Evaluation / Benchmarking Audit

Current benchmark posture:

```text
benchmark smoke exists; serious benchmark evidence does not
```

Strengths:

- `state_collapser.benchmarks` exists,
- benchmark smoke tests exist,
- evaluation doc is honest,
- multiple example environments exist,
- tower-depth probe exists,
- flat schema mode exists for baseline-style checks.

Gaps:

- no benchmark artifact schema mature enough for publication claims,
- no repeated large benchmark matrix,
- no published scaling curves,
- no rigorous readout-enabled vs readout-disabled cost comparisons,
- no morphism-enabled vs morphism-disabled cost comparison,
- no environment-family benchmark report,
- no HGraphML downstream benchmark compatibility.

Conclusion:

```text
Do not claim speed-up in public release notes yet.
```

It is fine to claim:

```text
runtime benchmark smoke tooling exists
```

It is not fine to claim:

```text
state_collapser has demonstrated RL training speed-up
```

without the serious benchmark track.

## Public API Audit

Top-level public API remains:

```python
import state_collapser
state_collapser.__version__
```

This is conservative and appropriate for pre-alpha.

However, the package now has documented provisional engineer-facing surfaces:

- partition tower,
- training inputs/transitions,
- frozen quotient behavior,
- path fiber,
- fiber-conditioned stage.

This split is healthy if documented honestly:

```text
stable top-level API: tiny
provisional engineer-facing API: useful but pre-alpha
internal modules: importable but not promised
```

The HGraphML update makes one thing more urgent:

```text
PartitionTower full-graph construction/readout must become either documented
provisional API or be replaced by a cleaner exported downstream adapter.
```

The new docs are a good first step, but future releases should either stabilize
the graph-readout path or make migration easy.

## Dependency Audit

Runtime dependencies:

```text
pillow>=12.2.0
```

Optional dependency groups:

```text
dev: build, mypy, pre-commit, pytest, pytest-cov, ruff, twine
rl: gymnasium, numpy
ml: torch
```

This is a good dependency posture. The base package is light.

Risks:

- `pillow` as a required base dependency should be confirmed. If it is only for
  examples/assets, move it to an optional extra. If core package logic uses it,
  keep it.
- `ml` extra is not installed in CI. If torch-facing behavior is release
  critical, add an ML CI job or a focused optional test job.
- HGraphML depends on `state_collapser`; once `state-collapser` is on PyPI,
  HGraphML can use a normal registry dependency.

## Release Workflow Audit

### CI

Current CI workflow is appropriate for a pre-alpha Python package:

- Python matrix `3.11` and `3.12`,
- install dev and RL extras,
- Ruff,
- mypy,
- pytest with coverage,
- build distributions,
- Codecov upload.

Recommendations:

- Verify CI passes on public GitHub after repo visibility changes.
- Add ML optional dependency coverage if torch-facing surfaces are promoted.
- Consider an HGraphML-shaped compatibility test/job before the next release.

### Publish

Current publish workflow uses PyPI trusted publishing:

```text
manual workflow_dispatch -> build -> pypa/gh-action-pypi-publish
```

This is the right modern approach.

Recommendations:

- Keep publishing manual-only during the GitHub-only research-release period.
- Configure PyPI trusted publisher before first release.
- Make first PyPI publication deliberate; project name squatting/creation is a
  one-way public event.
- Never publish from a dirty tree or stale version.
- Confirm that GitHub release tag, `pyproject.toml`, and `_version.py` all agree.

## Prioritized Findings

### P0: Public visibility is not established

Impact:

```text
HGraphML and strangers cannot install or inspect the package through public URLs.
```

Evidence:

- GitHub public web check returned not-found/not-public behavior.
- PyPI public web check returned not-found behavior.

Fix:

```text
Make GitHub repo public before HGraphML or public docs depend on public
installation. PyPI is intentionally deferred until serious benchmarking.
```

### P0: Version/tag mismatch on current main

Impact at audit start:

```text
Building current main would create a new 0.5.0 artifact different from the v0.5.0 tag.
```

Fix:

```text
Bump version before publishing main.
```

Follow-up status:

```text
Fixed by bumping package metadata and runtime version to 0.6.0.
```

### P0: Absolute local paths in public-facing docs

Impact:

```text
Public docs leak local machine layout and render as nonportable local links.
```

Evidence at original audit time:

- `CONTRIBUTING.md`: 39 local user-home path matches.
- `EVALUATION.md`: 10 local user-home path matches.
- many design and continuity docs contained additional matches.

Current status after PO-requested cleanup:

- scanned root docs and docs no longer contain the original local user-home path
  pattern,
- high-traffic public docs now use relative links where practical,
- historical design/continuity docs use neutral placeholders where the exact
  original local reference was part of provenance.

Fix:

```text
Replace root-doc absolute links with relative links before public release.
Then decide whether to clean all design/continuity docs or exclude them from
PyPI sdist.
```

Follow-up status:

```text
Fixed in the scanned text corpus while preserving the full research/provenance
documentation corpus.
```

### P1: Sdist is a broad research archive

Impact:

```text
PyPI sdist includes far more than package source.
```

This is not automatically wrong. It is a release-style decision.

Fix:

```text
Either explicitly bless broad research sdist after path cleanup, or configure
hatch sdist includes/excludes for a cleaner PyPI artifact.
```

PO decision and follow-up status:

```text
Bless the broad research/provenance archive for this research-mode release, but
keep local-machine paths cleaned.
```

### P1: HGraphML compatibility is not tested upstream

Impact:

```text
state_collapser can accidentally break its first downstream graph-ML application.
```

Fix:

```text
Add HGraphML-shaped partition-tower readout test or downstream CI job.
```

Follow-up status:

```text
Fixed by adding an HGraphML-shaped upstream partition-tower compatibility test.
```

### P1: Project URLs and public badges need verification

Impact:

```text
README and PyPI metadata can point at missing or private pages.
```

Fix:

```text
Make URLs canonical and public, then verify badge rendering.
```

Follow-up status:

```text
Canonical URLs are fixed in package metadata. Public badge rendering still needs
to be verified after the GitHub repository visibility changes.
```

### P1: PyPI trusted publishing needs setup

Impact:

```text
Publish workflow may fail at release time.
```

Fix:

```text
Configure PyPI trusted publisher for the exact GitHub repo/workflow/environment.
```

Follow-up status:

```text
Deferred. PyPI publishing is now manual-only and should remain parked until the
benchmark-supported registry release decision.
```

### P2: Missing public security policy

Impact:

```text
Public users do not know how to report security issues.
```

Fix:

```text
Add SECURITY.md if public adoption is expected.
```

Follow-up status:

```text
Fixed.
```

### P2: Python version policy is loose

Impact:

```text
pip may install on Python versions not covered by CI.
```

Fix:

```text
Either test Python 3.13+ or cap requires-python to the validated range.
```

Follow-up status:

```text
Fixed by capping the current release line to >=3.11,<3.13.
```

## Recommended Immediate Implementation Plan

If the goal is a lightweight public research release soon, do this in order:

1. Use `0.6.0` as the next release.
2. Make GitHub repository public, or delay HGraphML public dependency until it
   is public.
3. Clean absolute local paths from:
   - `README.md`
   - `CONTRIBUTING.md`
   - `EVALUATION.md`
   - `docs/package_usage.md`
   - `docs/public_api.md`
   - `docs/usage`
   - `docs/api_notes`
4. Preserve historical design/continuity docs in the research corpus, but keep
   local-machine path leakage cleaned.
5. Update package metadata:
   - canonical public URLs,
   - changelog URL,
   - typing classifier,
   - description,
   - Python version policy.
6. Add an HGraphML-shaped compatibility test for full-graph partition-tower
   construction and fiber-style readout.
7. Verify CI on public GitHub.
8. Keep PyPI publishing manual-only and deferred until serious benchmarking.
9. Build from a clean tree.
10. Run:
    - tests,
    - Ruff,
    - mypy,
    - build,
    - twine check.
11. Tag release.
12. Publish GitHub release.
13. Verify:
    - README badges,
    - public Git tag fetch,
    - HGraphML install against the public Git tag or commit.

If the goal is only a GitHub-visible research repo, the minimum is:

1. Make repo public.
2. Fix root-doc absolute paths.
3. Keep release language pre-alpha and benchmark-honest.
4. Push tags.
5. Verify HGraphML can fetch the tag unauthenticated.

## Final Assessment

`state_collapser` is much closer to a credible public research package than it
was earlier in the project. The package now has a real partition-backed runtime,
training surfaces, examples, evaluation guidance, benchmark smoke tooling, and a
downstream graph-ML application in HGraphML.

The code passes serious local validation.

The release process exists.

The package builds.

The main remaining work is not "make the code real." It is:

```text
make the public boundary clean
```

That means public URLs, version/tag discipline, local-path cleanup, sdist policy,
manual PyPI publishing discipline, and HGraphML compatibility protection.

With the follow-up hardening pass, the remaining public-release work is mostly
external verification: make the GitHub repository public, verify public CI and
badge rendering, verify unauthenticated tag fetches, and verify HGraphML against
the public tag or commit. A speed-up or mature-framework release is still not
ready.
