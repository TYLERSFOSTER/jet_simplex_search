# Engineering Continuity Report

Date: 2026-06-12

Repository: `jet_simplex_search`

Current public-release posture: pre-release engineering tree. The implementation
is functional and tested locally, but release hygiene, CI, packaging metadata,
and dependency publication still need explicit release work before the
repository should be made public or published.

## Project Purpose

`jet_simplex_search` searches for directed flag simplices in sparse graphs,
including degenerate simplices, through a static quotient tower supplied by
`state_collapser`.

The core speedup is fiber-addressed tower descent:

- enumerate bottom-tier simplices directly;
- cache each simplex frontier using the recurrence
  `F(sigma) = F(partial_m sigma) cap A(tgt sigma)`;
- lift one tier upward only over known downstairs simplex fibers;
- for a downstairs extension, inspect only the upstairs fiber of its final edge.

The algorithmic content is PM Abdul Malik's work and part of his thesis. That
attribution is preserved in the design documents and must remain intact.

## Current Implementation Surface

Package source lives under:

```text
src/jet_simplex_search/
```

Important modules:

- `graph.py`: sparse graph input records and validation.
- `normalize.py`: first-scope loop policy; strips input loops and adds exactly
  one formal identity per vertex.
- `records.py`: immutable simplex, witness, fiber, edge-fiber, and result
  records.
- `frontier.py`: adjacency/frontier intersection helpers.
- `search.py`: direct tier enumeration and full static small-object search.
- `lift.py`: fiber-addressed lifting from tier `r + 1` to tier `r`.
- `tower_adapter.py`: adapter protocol plus real `state_collapser` static tower
  adapter.
- `diagnostics.py`: count and frontier-size diagnostics.
- `artifacts.py`: single-JSON and manifest-table artifact writers.
- `api.py`: public `search_simplices` and context builder.

Current top-level export:

```python
from jet_simplex_search import search_simplices
```

## Dependency State

`pyproject.toml` declares:

```toml
dependencies = [
  "state-collapser",
]

[tool.uv.sources]
state-collapser = { path = "../state_collapser", editable = true }
```

This is acceptable for local development, but it is not yet public-release
packaging. Before release, decide whether `state-collapser` is published,
vendored, or documented as a source checkout dependency.

Last verified local `state_collapser` version:

```text
0.7.2
```

## Verified Behavior

The implementation currently supports:

- directed flag simplex enumeration through user-provided `k`;
- first-class degenerate simplex records;
- identity-loop generation after input-loop stripping;
- directed face-edge witness tracing;
- fake-adapter tower lift tests;
- real `state_collapser` static tower integration tests;
- source-sensitive final-edge fiber lifting;
- artifacts with simplex rows, simplex-fiber rows, edge-fiber rows, and
  diagnostics.

Last recorded full test result in the implementation log:

```text
uv run pytest
58 passed
```

Release-prep verification during README work:

```text
uv run pytest
58 passed
```

README quick-start smoke:

```text
{(1, 0): 2, (1, 1): 3, (1, 2): 4, (0, 0): 3, (0, 1): 6, (0, 2): 10}
```

Temporary build verification:

```text
uv build --out-dir /private/tmp/jet-simplex-search-readme-build
Successfully built jet_simplex_search-0.1.0.tar.gz
Successfully built jet_simplex_search-0.1.0-py3-none-any.whl
```

Recent smoke scripts were added under:

```text
smoke/
```

They exercise low-dimensional degeneracy and missing-face behavior through
dimension `4`. Each `smoke_003.py` through `smoke_016.py` has a matching
Markdown count argument.

## Public Documentation State

Design and execution history:

- `docs/design/initial_design/01_001_static_tower_small_object_simplex_search.md`
- `docs/design/initial_design/01_002_static_tower_small_object_package_blueprint.md`
- `docs/design/initial_design/01_003_static_tower_small_object_implementation_workplan.md`
- `docs/design/initial_design/01_004_static_tower_small_object_implementation_log.md`

Prime-directive release protocol:

- `docs/prime_directive/public_release_readiness_protocol.md`

The release protocol says not to rewrite design history into a fake clean
story, not to publish stale public entry points, and not to claim final
benchmark superiority without an approved evaluation.

## Deferred Work

These are explicitly deferred from the first implementation:

- Kan replacement.
- Meaningful non-identity input loops.
- One simplex per multigraph witness choice.
- Compressed, SQLite, or DuckDB artifact storage.
- Bitset, CSR, GPU, or tensor acceleration.
- Multiprocessing.

The README and public materials should not imply these are implemented.

## Known Release Gaps

Before a public release, complete or decide:

- Add CI before using a CI badge.
- Resolve local editable `state_collapser` dependency for public users.
- Add package classifiers and project URLs in `pyproject.toml`.
- Add a release hygiene script or adapt the existing prime-directive
  expectation to this repository.
- Run public hygiene checks for stale paths, local absolute paths, raw
  artifacts, and public-facing profanity redaction.
- Decide whether smoke scripts are examples, tests, or internal validation
  artifacts.
- Add a changelog or release notes.
- Verify source distribution and wheel builds.
- Decide whether to publish to PyPI. The release protocol marks publishing as a
  stop condition requiring explicit Project Owner approval.

## Safe Public Claims Today

It is safe to say:

- The package provides a Python API for static quotient-tower simplex search.
- It emits degenerate simplices as first-class records.
- It uses `state_collapser` static partition towers.
- It supports JSON/JSONL artifact output.
- Local tests and smoke examples cover low-dimensional degeneracy behavior.

It is not yet safe to say:

- The package is production-ready.
- The package is published on PyPI.
- CI is passing on GitHub.
- The speedup is benchmark-validated at public-release standard.
- Kan replacement is implemented.
- Multigraph witness-choice semantics are complete.

## Handoff Guidance

When resuming:

1. Run `git status --short` and preserve unrelated user changes.
2. Run `uv run pytest`.
3. Run the smoke scripts relevant to any README/example changes.
4. Keep `state_collapser` as the semantic owner of tower behavior.
5. Keep public claims bounded to verified behavior.
6. Do not tag, publish, upload release assets, or make the repository public
   without explicit Project Owner approval.
