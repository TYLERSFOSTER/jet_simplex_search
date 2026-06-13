# Synthetic Blow Code Revision Implementation Log

## Status

Implementation log for:

```text
docs/design/synthetic_blow_code_revisions/01_003_synthetic_blow_code_revision_implementation_workplan.md
```

## Approval

Project Owner instruction:

```text
execute docs/design/synthetic_blow_code_revisions/01_003_synthetic_blow_code_revision_implementation_workplan.md
```

Scope interpreted as approved for `jet_simplex_search` source, tests, docs, and
release metadata. This implementation does not directly edit `../state_collapser`.

## Baseline

Branch:

```text
codex/synthetic-blow-code-revisions
```

Starting commit:

```text
4a2c1f9a6511b2d39414e981439f413561669b82
```

Initial git status:

```text
M  README.md
R  code_review/synthetic_blow_project_review.md -> code_review/01_001_synthetic_blow_project_review.md
A  code_review/01_002_synthetic_blow_project_review.md
A  docs/design/synthetic_blow_code_revisions/01_001_synthetic_blow_code_revision_scope.md
A  docs/design/synthetic_blow_code_revisions/01_002_synthetic_blow_code_revision_blueprint.md
?? docs/design/synthetic_blow_code_revisions/01_003_synthetic_blow_code_revision_implementation_workplan.md
```

Baseline tests:

```text
uv run pytest
90 passed in 0.09s
```

Baseline smoke:

```text
smoke/smoke_001.py: ok
smoke/smoke_002.py: ok
smoke/smoke_003.py: ok
smoke/smoke_004.py: ok
smoke/smoke_005.py: ok
smoke/smoke_006.py: ok
smoke/smoke_007.py: ok
smoke/smoke_008.py: ok
smoke/smoke_009.py: ok
smoke/smoke_010.py: ok
smoke/smoke_011.py: ok
smoke/smoke_012.py: ok
smoke/smoke_013.py: ok
smoke/smoke_014.py: ok
smoke/smoke_015.py: ok
smoke/smoke_016.py: ok
```

Adjacent `state_collapser`:

```text
status: clean
tags: v0.6.0, v0.7.0, v0.7.1, v0.7.2
remote: git@github.com:TYLERSFOSTER/state_collapser
```

## Phase 0 - Execution Gate, Baseline, And Source Synchronization

- Completed branch creation.
- Completed baseline test run.
- Completed baseline smoke run.
- Completed adjacent `state_collapser` status/tag/remote check.
- Created this implementation log before source edits.

## Phase 1 - Result Model And Public API Boundary

- Added `jet_simplex_search.results.SearchWithHLiftsResult`.
- Added `SearchResult` as the explicit artifact/result union.
- Removed the internal `StaticSearchContext` helper.
- Split public API intent:
  - `search_simplices(...)` is graph-H only.
  - `search_skeleton_simplices(...)` handles adapter-backed or graph-backed skeleton/tower search.
- Added API tests for graph-H results, skeleton-only results, adapter rejection on the public H path, adapter/graph exclusivity, and artifact writing.

Focused verification:

```text
uv run pytest tests/test_api.py
8 passed in 0.05s
```

## Phase 2 - Artifact Writer Type Discipline

- Made artifact writing accept only the explicit `SearchResult` union.
- Added an `ArtifactWriteError` path for unsupported result objects.
- Split single-result and combined H-lift payload construction.
- Removed the unimplemented expanded-H-lift config knob from `ArtifactConfig`.
- Added schema/result-kind markers to artifact manifests.
- Added artifact tests for simple search output, combined H-lift output, manifest tables, unsupported result rejection, and explicit expanded-witness non-support.

Focused verification:

```text
uv run pytest tests/test_artifacts.py
7 passed in 0.06s
```

## Phase 3 - Clean Static Tower Bridge

- Added `jet_simplex_search.clean_tower`.
- Added `CleanTowerConfig`, `CleanTierProjection`, `CleanTowerDiagnostics`, `CleanTower`, and `CleanStaticTowerAdapter`.
- Added `CleanTowerConstructionError`.
- Built clean quotient tiers by invoking `state_collapser` one contraction block at a time, then realizing each quotient as a simple loop-free, parallel-free `GraphInput`.
- Made internal collapsed edges project to formal downstream identities.
- Made projected parallel edges merge into one clean downstream edge only when their labels agree exactly.
- Added source-sensitive edge-fiber target indexes as owned clean tower projection data.
- Added tests for:
  - no-schema single-tier behavior;
  - rejection of stored loops and parallel edges;
  - one-block contraction realization;
  - multi-step declared-block contraction;
  - skipped empty blocks;
  - explicit label conflicts;
  - `max_tiers`;
  - static search over the clean adapter.

Focused verification:

```text
uv run pytest tests/test_clean_tower.py
8 passed in 0.04s
```

## Phase 4 - Public Workflow Switch To Clean Tower

- Switched graph-based `search_simplices(...)` to `CleanStaticTowerAdapter.from_graph(...)`.
- Switched graph-based `search_skeleton_simplices(...)` to `CleanStaticTowerAdapter.from_graph(...)`.
- Kept adapter-based `search_skeleton_simplices(adapter=...)` as the lower-level fake/raw-adapter route.
- Kept raw `StateCollapserStaticTowerAdapter` integration tests for compatibility coverage.
- Added `tests/integration/test_clean_state_collapser_tower.py` to exercise the clean bridge against real `LabelBlockSchema` behavior.
- Tightened the multi-step clean tower regression so the first quotient step creates projected parallel edges, the clean bridge merges them, and the second contraction step runs on the cleaned edge.

Focused verification:

```text
uv run pytest tests/test_api.py tests/test_clean_tower.py tests/integration/test_state_collapser_static_tower.py tests/integration/test_clean_state_collapser_tower.py
23 passed in 0.06s
```

## Phase 5 - Witness, Lift, And Semantic Regression Tests

- Added `tests/test_witness_consistency.py`.
- Added witness checks proving every recorded witness edge exists in the normalized tier graph and connects the claimed source/target vertices.
- Added projection checks proving every lifted simplex:
  - has a downstream simplex id;
  - projects vertexwise to that downstream simplex;
  - has projected last-edge witnesses compatible with the downstream last edge.
- Confirmed the existing missing-downstairs-interior regression in `tests/test_fiber_lift.py` remains active: degree-2 upstairs simplices are not emitted when no downstairs degree-2 simplex record is supplied.

Focused verification:

```text
uv run pytest tests/test_fiber_lift.py tests/test_witness_consistency.py
7 passed in 0.05s
```

## Phase 6 - Skeleton Label Policy Documentation

- Updated `SkeletonLabelPolicy` and `skeletonize_graph` docstrings to call out the v0.1 exact-label policy.
- Kept clean quotient edge label conflicts explicit in `CleanTowerConstructionError`.
- Renamed skeleton tests so identical-label acceptance and different-label rejection name the v0.1 policy directly.

Focused verification:

```text
uv run pytest tests/test_skeleton.py
9 passed in 0.03s
```

## Phase 7 - Dead Code And Stale Cache Cleanup

- Deleted unused `fiber_id` from `ids.py` and removed its preservation-only test.
- Removed unread raw-adapter `_simple_edge_action_ids_cache`.
- Removed unused raw-adapter `_edge_id_to_action_cell`.
- Confirmed remaining cleanup search hits are historical design references or live `simplex_fiber_ids` lifting state.

Focused verification:

```text
uv run pytest tests/test_ids.py tests/test_tower_adapter_fake.py tests/integration/test_state_collapser_static_tower.py tests/test_api.py tests/test_artifacts.py
27 passed in 0.07s
```

## Phase 8 - Release-Facing Metadata And README

- Updated `pyproject.toml`:
  - `state-collapser` now points to the GitHub `v0.7.2` tag;
  - local `[tool.uv.sources]` path override was removed;
  - project URLs and classifiers were added;
  - Ruff was added to the dev dependency group;
  - Ruff config was added;
  - Hatch direct-reference metadata opt-in was added.
- Updated `uv.lock` through `uv run`.
- Updated `README.md`:
  - added a Ruff badge;
  - changed installation language from sibling checkout to GitHub source pre-release;
  - kept the existing logo and title;
  - removed the root continuity-report link;
  - avoided links to `docs/prime_directive` and release-prep docs;
  - added a separate Known Limitations section;
  - kept the quick-start output verified.
- Added `tests/test_release_metadata.py`.
- Added `tests/test_readme_quickstart.py`.

Focused verification:

```text
uv run pytest tests/test_release_metadata.py tests/test_readme_quickstart.py
5 passed in 0.05s
```

## Phase 9 - Repository Hygiene

- Deleted tracked SVG backup/temp files from `assets/images`.
- Added narrow `.gitignore` patterns:
  - `assets/images/.$*.svg.bkp`;
  - `assets/images/.$*.svg.dtmp`.
- Checked tracked bytecode with `git ls-files | rg '(__pycache__|\\.pyc$)'`; no tracked bytecode was found.
- Confirmed README has no internal continuity, Prime Directive, or release-prep links.

## Phase 10 - Full Verification

- Ran the full test suite after all source and metadata edits.
- Ran all smoke scripts.
- Built both source distribution and wheel to `/private/tmp/jet-simplex-search-revision-build`.
- Ran Ruff lint.
- Ran Ruff format check; it reports a broad pre-existing formatting pass across 30 files. Per the workplan stop condition, no mass-formatting was applied in this refactor.

Verification:

```text
uv run pytest
111 passed in 0.11s
```

```text
smoke/smoke_001.py: ok
smoke/smoke_002.py: ok
smoke/smoke_003.py: ok
smoke/smoke_004.py: ok
smoke/smoke_005.py: ok
smoke/smoke_006.py: ok
smoke/smoke_007.py: ok
smoke/smoke_008.py: ok
smoke/smoke_009.py: ok
smoke/smoke_010.py: ok
smoke/smoke_011.py: ok
smoke/smoke_012.py: ok
smoke/smoke_013.py: ok
smoke/smoke_014.py: ok
smoke/smoke_015.py: ok
smoke/smoke_016.py: ok
```

```text
uv build --out-dir /private/tmp/jet-simplex-search-revision-build
Successfully built jet_simplex_search-0.1.0.tar.gz
Successfully built jet_simplex_search-0.1.0-py3-none-any.whl
```

```text
uv run ruff check .
All checks passed!
```

```text
uv run ruff format --check .
30 files would be reformatted, 29 files already formatted
```

## Phase 11 - Implementation Log Closeout And Final Review

- Reviewed final status and diff stats.
- Confirmed root README does not link internal continuity, Prime Directive, or release-prep docs.
- Confirmed cleanup symbol search has no product/test hits for deleted helpers; remaining `simplex_fiber_ids` hits are live lift state.
- Confirmed pre-existing staged report/design files remain present and were not reverted.
- Confirmed Abdul Malik attribution remains in README and controlling design documents.

Final status notes:

```text
New/modified implementation files include:
- src/jet_simplex_search/clean_tower.py
- src/jet_simplex_search/results.py
- src/jet_simplex_search/api.py
- src/jet_simplex_search/artifacts.py
- src/jet_simplex_search/tower_adapter.py
- src/jet_simplex_search/skeleton.py
- pyproject.toml
- uv.lock
- README.md
- tests/test_clean_tower.py
- tests/test_witness_consistency.py
- tests/test_release_metadata.py
- tests/test_readme_quickstart.py
- tests/integration/test_clean_state_collapser_tower.py
```

## Phase 12 - Deferred Follow-Up Ledger

- JSS owns the clean tower bridge for this revision.
- A future `state_collapser` clean quotient tower primitive may replace the JSS bridge, but this revision does not require direct edits to `../state_collapser`.
- Deferred/non-goal features remain:
  - Kan replacement;
  - horn filling;
  - cofibrant replacement variants beyond current small-object search;
  - expanded H witness enumeration artifacts;
  - GPU/tensor/CSR acceleration;
  - PyPI publication;
  - tagging;
  - GitHub visibility changes;
  - broad Ruff formatting pass across existing files.
