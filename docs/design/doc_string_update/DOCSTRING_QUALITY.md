# Docstring Quality Work

This document tracks the docstring-quality cleanup for `state_collapser`.

The goal is not to make every internal helper verbose. The goal is to make the
repo's public, provisional, design-sensitive, test, and tooling Python surfaces
easier for outside engineers to understand without having to reconstruct intent
from implementation details or design documents.

## Current Assessment

The repo has many docstrings, and most major modules are not bare. The current
quality is usable for research-mode development, but not yet professionalized
for outside contributors.

The main issue is not absence everywhere. The issue is uneven quality:

- many important surfaces have only terse "Return X" docstrings;
- many protocol methods, properties, and runtime methods are undocumented;
- example environments vary in docstring quality;
- design-sensitive objects often do not state invariants, side effects, or
  compatibility expectations directly in code;
- formatting-level docstring lint is not currently enforced.
- tests and utility scripts have not yet been treated as first-class narrative
  documentation, even though they encode important contracts and usage examples.

## Current Static Signal

The initial non-mutating Ruff docstring check on `src/state_collapser` reported:

```text
617 total docstring/style findings
414 D202 blank-line-after-function
151 D102 undocumented-public-method
25  D107 undocumented-public-init
13  D105 undocumented-magic-method
10  D101 undocumented-public-class
4   D103 undocumented-public-function
```

The `D202` count is mostly formatting noise. The more meaningful finding is the
large number of missing public class/function/method docstrings.

After the first implementation pass, the meaningful missing-docstring Ruff check
on package source is clean:

```text
uv run ruff check src/state_collapser --select D101,D102,D103,D105,D107 --statistics
```

The expanded repo-level inventory in `docstring_quality_inventory.json` now
scans all repo Python files outside `.git`, `.venv`, `dist`, `build`, and cache
directories. The current regenerated scan reports:

```text
204 Python files scanned
195 files with heuristic docstring-improvement candidates
1446 total heuristic candidates
823 package-src heuristic candidates
623 test candidates
0 asset/tooling candidates
```

Those counts are a work queue, not a lint contract. The first implementation
pass removed missing public package-source docstrings and all asset/tooling
docstring misses. Remaining package-source entries are deliberately conservative
heuristic review candidates for thin design-surface docstrings, not known
failures. Remaining test entries should be cleaned with lighter, purpose-driven
scenario docstrings rather than boilerplate.

## Cleanup Priorities

### Package Src Priorities

1. `state_collapser.training.linearization`
2. `state_collapser.training.torch`
3. `state_collapser.tower.partition`
4. `state_collapser.tower.runtime`
5. `state_collapser.adapters.gymnasium`
6. public example runtime/training surfaces

### Test Priorities

1. Tensorization and Torch-boundary tests.
2. HGraphML downstream-compatibility tests.
3. Tower partition/runtime regression tests.
4. Training surface and fiber-conditioned tests.
5. Example-environment integration tests.
6. Remaining smoke, contract, and unit tests.

Test docstrings should explain the behavioral contract, regression scenario, or
edge case being protected. They should not mechanically restate the test name.

### Tooling Priorities

1. Repo scripts, if added.
2. Python docs tooling, if added.
3. Asset-maintenance helpers such as image/color replacement scripts.

Tooling docstrings should explain command purpose, inputs, outputs, filesystem
side effects, and any assumptions about running location.

## What Good Docstrings Should Do Here

Good docstrings in this repo should explain:

- what the surface is for;
- what layer owns the concept;
- important invariants;
- important side effects;
- whether the surface is object-native, tensor-facing, benchmark-facing, or
  downstream-facing;
- compatibility constraints, especially around HGraphML and optional Torch;
- what is intentionally not owned by the surface.
- for tests, what behavior or regression the test protects;
- for scripts/tooling, what the command changes and what inputs it expects.

For simple helpers, a short one-line docstring is enough. For design-sensitive
classes and public methods, docstrings should carry enough context that an
engineer can use the surface without reading the full design-history trail.
For tests, a concise one- or two-sentence scenario docstring is usually enough.
For scripts and docs tooling, module-level docstrings should usually be stronger
than individual helper docstrings.

## Current Rules Of Thumb

- Do not turn docstrings into copied design docs.
- Do not add docstrings to every private helper just to satisfy a linter.
- Prefer concise semantic docstrings over mechanical restatements of the
  function name.
- Prioritize public and provisional surfaces before internal implementation
  details.
- Treat tests as executable documentation: document the scenario when the test
  name alone does not explain the contract.
- Treat repo scripts and tooling as operational documentation: document side
  effects and assumptions before implementation trivia.
- Keep backend boundaries explicit: backend-independent linearization should not
  imply Torch, and Torch should remain behind the `ml` extra.
- Keep downstream boundaries explicit: HGraphML should be able to reuse tower
  encodings without depending on RL-specific training records.

## Open Work Area

Use this section to decide the first cleanup pass before editing source files.

### PO Request

Generate a JSON at root that is nested like the repo's tree, and at its leaves lists all functions classes whatever that need doc string improve.

### Codex Reply

Generated `docstring_quality_inventory.json` in this design folder.

The inventory is an AST-based, non-mutating scan of repo Python files outside
`.git`, `.venv`, `dist`, `build`, and cache directories. Its leaves are
file-level lists of modules, classes, functions, methods, and properties that
either lack docstrings or have thin docstrings for their tier.

The JSON intentionally does not enumerate `D202` blank-line formatting findings.
Those are formatting cleanup, not semantic docstring-quality targets.

The inventory now includes package code, tests, and tooling. Package code should
receive API-grade semantic docstrings. Tests should receive scenario/contract
docstrings where useful. Tooling should receive operational docstrings that make
inputs, outputs, and side effects clear.
