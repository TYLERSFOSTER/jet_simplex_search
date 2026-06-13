# Engineering Continuity Report

Date: 2026-06-13

Repository: `jet_simplex_search`

Branch at report time:

```text
codex/synthetic-blow-code-revisions
```

Current public-release posture: library pre-release engineering tree. The code
is substantially more release-shaped than the 2026-06-12 continuity report:
public API boundaries are clearer, the graph-H workflow uses a clean quotient
tower bridge, release metadata points to the GitHub `state_collapser` tag, the
README no longer advertises the sibling checkout as the primary install path,
and verification now includes 111 pytest tests, all smoke scripts, package
build, and Ruff lint. CI, changelog/release notes, final public-release review,
and any publication/tagging remain explicitly unapproved and undone.

## Scope Since Previous Continuity Report

The previous continuity report was:

```text
docs/engineer_continuity/2026/06/12/01_001_engineering_continuity_report.md
```

That report described the initial working package after the first static
small-object simplex-search implementation. Since then, the main workstreams
were:

- reviewed the project through the synthetic Blow review kit;
- wrote review reports under `code_review`;
- designed a clean H-to-G skeleton and quotient realization refactor;
- designed and executed the synthetic Blow code-revision workplan;
- added a JSS-owned clean static tower bridge;
- switched public graph workflows to that clean tower bridge;
- split graph-H search from skeleton/tower-only search;
- made artifact output typed instead of duck-typed;
- added semantic witness/projection regressions;
- updated release-facing README and package metadata;
- removed tracked backup/temp SVG files;
- verified the result with tests, smoke scripts, build, and Ruff lint.

The current implementation log for the largest code pass is:

```text
docs/design/synthetic_blow_code_revisions/01_004_synthetic_blow_code_revision_implementation_log.md
```

## Attribution And Algorithmic Ownership

The quotient-tower simplex search algorithm remains PM Abdul Malik's work and
part of his thesis. This includes:

- degree-wise simplex enumeration;
- cached simplex frontiers;
- formal identity handling for degenerates;
- static quotient towers;
- small-object fiber-addressed lift search over existing downstairs simplices.

This attribution is preserved in the README and design documents. The root
README now links public-facing design spine documents, but it intentionally does
not link internal Prime Directive or release-prep documents.

Important user clarification preserved in the implementation:

- `search_simplices(...)` studies the original graph `H`.
- `H` is skeletonized to a clean simple search graph `G`.
- The quotient tower is built statically from `G`.
- Bottom-tier simplices are enumerated directly.
- Higher-tier simplices are lifted only over existing downstairs simplex
  records.
- If a downstairs boundary or lower-dimensional shape exists without a
  downstairs interior simplex record, upstairs search for that interior does not
  occur. This is the small-object behavior and is intentionally distinct from
  Kan filling.

## Current High-Level Pipeline

The public graph-H pipeline is now:

```text
GraphInput H
  -> skeletonize_graph(H)
  -> skeleton graph G
  -> CleanStaticTowerAdapter.from_graph(G, schema=...)
  -> run_static_small_object_search(clean_adapter, k=...)
  -> compute_h_lifts_for_tier_zero(...)
  -> SearchWithHLiftsResult
```

The lower-level skeleton/tower path is now:

```text
search_skeleton_simplices(adapter=..., k=...)
```

or:

```text
search_skeleton_simplices(graph=clean_G, contraction_schema=..., k=...)
```

The first form uses the provided adapter directly. The second form treats the
graph as an already-clean skeleton/search graph and builds a clean tower adapter
from it. It does not skeletonize raw `H`; raw `H` belongs on the public
`search_simplices(...)` path.

## Public API State

The old mixed-purpose public API has been split.

Primary public graph-H API:

```python
search_simplices(
    *,
    graph: GraphInput,
    contraction_schema: object | None = None,
    k: int,
    artifact_config: ArtifactConfig | None = None,
) -> SearchWithHLiftsResult
```

Lower-level skeleton/tower API:

```python
search_skeleton_simplices(
    *,
    adapter: StaticTowerAdapterProtocol | None = None,
    graph: GraphInput | None = None,
    contraction_schema: object | None = None,
    k: int,
    artifact_config: ArtifactConfig | None = None,
) -> SimplexSearchResult
```

Important behavior:

- `search_simplices(...)` no longer accepts an adapter. Passing `adapter=` is a
  Python signature error and is covered by tests.
- `search_skeleton_simplices(...)` accepts exactly one of `adapter` or `graph`.
- Providing both adapter and graph raises `TypeError`.
- Providing neither raises `TypeError`.
- Both public paths validate `k`.

New result module:

```text
src/jet_simplex_search/results.py
```

It defines:

```python
SearchWithHLiftsResult
SearchResult = SimplexSearchResult | SearchWithHLiftsResult
```

Package root exports now include:

```python
SearchResult
SearchWithHLiftsResult
SimplexSearchResult
search_simplices
search_skeleton_simplices
skeletonize_graph
```

## Clean Static Tower Bridge

New module:

```text
src/jet_simplex_search/clean_tower.py
```

Purpose:

`state_collapser` can produce quotient tower layers whose raw action-cell view
is not the clean simple graph required by the simplex search engine. The
synthetic Blow review identified this as a central correctness/performance
surface: the package must search in clean quotient tiers, not repeatedly scan or
reinterpret raw unclean action-cell layers. JSS now owns a clean tower bridge for
this release.

Core records:

- `CleanTowerConfig`
- `CleanTierProjection`
- `CleanTowerDiagnostics`
- `CleanTower`
- `CleanStaticTowerAdapter`

Key behavior:

- clean tower construction starts from a clean directed graph;
- stored clean tier graphs contain no loops;
- stored clean tier graphs contain no parallel endpoint pairs;
- formal identities remain simplex-engine edges and are not stored as graph
  edges;
- each contraction block is applied through a temporary one-block
  `state_collapser` partition tower;
- the temporary quotient state cells are realized into deterministic clean
  `GraphInput` vertices;
- quotient non-loop edges are realized as one edge per projected endpoint pair;
- internal projected edges become formal downstream identities;
- source-sensitive edge-fiber targets are recorded in projection data;
- projected parallel quotient edges merge only when their labels agree exactly;
- label conflicts raise `CleanTowerConstructionError`.

Important implementation detail:

`CleanStaticTowerAdapter.bottommost_nondegenerate_tier()` returns the last tier
with more than one vertex, falling back to tier `0` when all tiers are singleton.
This keeps direct enumeration on the bottommost nondegenerate tier while avoiding
meaningless search solely at pi0/singleton collapse.

Current clean tower limitation:

JSS owns this bridge for the current release. A future `state_collapser` clean
quotient tower primitive could replace it, but no direct edits to
`../state_collapser` were made in this pass.

## Raw State-Collapser Adapter

The raw adapter still exists:

```text
src/jet_simplex_search/tower_adapter.py
```

Class:

```python
StateCollapserStaticTowerAdapter
```

It remains tested as a lower-level compatibility/integration boundary. Public
graph-H workflows now use `CleanStaticTowerAdapter`, not this raw adapter.

Cleanup performed:

- removed unread `_simple_edge_action_ids_cache`;
- removed unused `_edge_id_to_action_cell`;
- kept `_action_cell_to_edge_id`, which is still used for raw action-cell edge
  naming;
- kept source/target and edge-fiber caches that still serve raw adapter
  behavior.

## Artifact Writer State

Artifact writing is now typed by explicit result classes rather than
attribute-shape duck typing.

Public artifact entry:

```python
write_search_artifact(result: SearchResult, config: ArtifactConfig)
```

Supported result kinds:

- `SimplexSearchResult`
- `SearchWithHLiftsResult`

Unsupported objects raise:

```python
ArtifactWriteError
```

Manifest schema/result markers:

- skeleton-only search:
  - `schema_version = 1`
  - `result_kind = "simplex_search"`
- graph-H search with H-lifts:
  - `schema_version = 2`
  - `result_kind = "skeleton_search_with_h_lifts"`

Expanded H witness artifacts remain explicitly unimplemented. The old
`max_expanded_h_lift_witnesses` config knob was removed because it advertised
nonexistent behavior. Setting `include_expanded_h_lift_witnesses=True` still
raises an explicit artifact error.

## Witness And Projection Correctness

The synthetic Blow review specifically warned that counts alone are not enough:
simplex records must carry truthful witness/projection data.

New regression module:

```text
tests/test_witness_consistency.py
```

It checks:

- every recorded witness edge exists in the normalized graph for the simplex
  tier;
- witness edge source and target match the corresponding simplex vertices;
- `last_edge_ids` connect the final prefix target to the extension target;
- every lifted simplex above the bottom tier has a `projection_simplex_id`;
- projected upstairs vertices equal the downstairs simplex vertex tuple;
- projected upstairs last-edge witnesses are compatible with the downstairs
  last edge.

The existing small-object/Kan-distinction regression remains:

```text
tests/test_fiber_lift.py::test_missing_downstairs_two_simplex_prevents_upstairs_triangle_search
```

That test supplies downstairs degrees `0` and `1` but an empty downstairs degree
`2` record set, while upstairs has a triangle. The lift emits no upstairs
degree-2 simplex. This proves the package does not search for upstairs interiors
when no corresponding downstairs interior simplex exists.

## Skeleton Label Policy

The v0.1 label policy is strict:

- parallel H edges may collapse to one skeleton edge only when their label
  tuples are exactly identical;
- projected quotient edges may merge in the clean tower only when their label
  tuples are exactly identical;
- mismatches raise explicit errors.

Source locations:

```text
src/jet_simplex_search/skeleton.py
src/jet_simplex_search/clean_tower.py
```

Relevant tests:

```text
tests/test_skeleton.py
tests/test_clean_tower.py
```

The README Known Limitations section now states this v0.1 exact-label policy.

## Release Metadata State

`pyproject.toml` now points to the real GitHub release tag:

```toml
"state-collapser @ git+https://github.com/TYLERSFOSTER/state_collapser.git@v0.7.2"
```

The local editable dependency override was removed:

```toml
[tool.uv.sources]
state-collapser = { path = "../state_collapser", editable = true }
```

is no longer present.

Direct reference support was enabled for Hatch:

```toml
[tool.hatch.metadata]
allow-direct-references = true
```

Metadata added:

- project URLs:
  - Homepage;
  - Repository;
  - Issues;
- classifiers:
  - alpha development status;
  - science/research audience;
  - MIT license;
  - Python 3, 3.11, 3.12;
  - mathematics topic.

Dev dependency added:

```toml
"ruff>=0.8"
```

Ruff config added:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E4", "E7", "E9", "F"]
```

Important accuracy note:

The `Typing :: Typed` classifier was not kept because the package does not ship
a `py.typed` marker yet.

## README State

README updates since the previous continuity report:

- kept the existing logo and title unchanged;
- added a Ruff badge;
- updated installation language to GitHub source pre-release;
- removed sibling checkout as the primary install story;
- removed the root README link to the internal/incorrect continuity-report
  path;
- did not link `docs/prime_directive`;
- did not link release-prep docs;
- added a separate `Known Limitations` section;
- preserved Abdul Malik attribution;
- kept quick-start example output verified by test.

Known README issue that remains outside this pass:

The visual caption currently says `acheived`; this typo was present in the
existing README text and was not corrected during this scoped implementation.

Quick-start regression test:

```text
tests/test_readme_quickstart.py
```

It asserts:

```text
{(1, 0): 2, (1, 1): 3, (1, 2): 4, (0, 0): 3, (0, 1): 6, (0, 2): 10}
{0: 3, 1: 3, 2: 1}
```

## Repository Hygiene

Tracked SVG editor backup/temp files were deleted:

```text
assets/images/.$degens_dark.svg.bkp
assets/images/.$degens_light.svg.bkp
assets/images/.$how_dark.svg.bkp
assets/images/.$logo_dark.svg.bkp
assets/images/.$logo_light.svg.bkp
assets/images/.$logo_light.svg.dtmp
```

Narrow ignore rules were added:

```gitignore
assets/images/.$*.svg.bkp
assets/images/.$*.svg.dtmp
```

Tracked bytecode check:

```text
git ls-files | rg '(__pycache__|\.pyc$)'
```

No tracked bytecode was found.

## New And Updated Test Coverage

New tests:

```text
tests/test_clean_tower.py
tests/test_witness_consistency.py
tests/test_release_metadata.py
tests/test_readme_quickstart.py
tests/integration/test_clean_state_collapser_tower.py
```

Updated tests:

```text
tests/test_api.py
tests/test_artifacts.py
tests/test_ids.py
tests/test_skeleton.py
tests/integration/test_state_collapser_static_tower.py
```

Notable test responsibilities:

- `tests/test_clean_tower.py`
  - no-schema one-tier behavior;
  - rejection of stored loops;
  - rejection of parallel clean-tier edges;
  - one-block clean quotient realization;
  - multi-step clean quotient realization after projected parallel merge;
  - skipped empty schema blocks;
  - explicit quotient label conflicts;
  - `max_tiers`;
  - search over clean adapter.
- `tests/integration/test_clean_state_collapser_tower.py`
  - clean bridge with real `LabelBlockSchema`;
  - graph-based skeleton search route uses clean bridge.
- `tests/test_witness_consistency.py`
  - witness edge truth;
  - lifted projection truth.
- `tests/test_release_metadata.py`
  - project name/version;
  - Python range;
  - GitHub `state_collapser` tag dependency;
  - no local uv source override;
  - URLs/classifiers/Ruff;
  - README badge compatibility.
- `tests/test_readme_quickstart.py`
  - README example remains runnable and count-correct.

## Verification State

Final full test result:

```text
uv run pytest
111 passed in 0.11s
```

Smoke verification:

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

Build verification:

```text
uv build --out-dir /private/tmp/jet-simplex-search-revision-build
Successfully built jet_simplex_search-0.1.0.tar.gz
Successfully built jet_simplex_search-0.1.0-py3-none-any.whl
```

The build command needed approval/escalation in the Codex sandbox because uv
needed to open its cache path:

```text
/Users/foster/.cache/uv/sdists-v9/.git
```

That was a sandbox permission issue, not a package build issue.

Ruff lint:

```text
uv run ruff check .
All checks passed!
```

Ruff format:

```text
uv run ruff format --check .
30 files would be reformatted, 29 files already formatted
```

No broad formatting pass was applied. This is intentionally deferred because it
would touch many existing files outside the semantic refactor surface.

## Current Git State At Report Time

Current status includes both the recent implementation and pre-existing staged
review/design changes. Do not assume every status entry was created in the
latest code pass.

Status observed while writing this report:

```text
 M .gitignore
MM README.md
 D assets/images/.$degens_dark.svg.bkp
 D assets/images/.$degens_light.svg.bkp
 D assets/images/.$how_dark.svg.bkp
 D assets/images/.$logo_dark.svg.bkp
 D assets/images/.$logo_light.svg.bkp
 D assets/images/.$logo_light.svg.dtmp
R  code_review/synthetic_blow_project_review.md -> code_review/01_001_synthetic_blow_project_review.md
A  code_review/01_002_synthetic_blow_project_review.md
A  docs/design/synthetic_blow_code_revisions/01_001_synthetic_blow_code_revision_scope.md
A  docs/design/synthetic_blow_code_revisions/01_002_synthetic_blow_code_revision_blueprint.md
 M pyproject.toml
 M src/jet_simplex_search/__init__.py
 M src/jet_simplex_search/api.py
 M src/jet_simplex_search/artifacts.py
 M src/jet_simplex_search/errors.py
 M src/jet_simplex_search/ids.py
 M src/jet_simplex_search/skeleton.py
 M src/jet_simplex_search/tower_adapter.py
 M tests/test_api.py
 M tests/test_artifacts.py
 M tests/test_ids.py
 M tests/test_skeleton.py
 M uv.lock
?? docs/design/synthetic_blow_code_revisions/01_003_synthetic_blow_code_revision_implementation_workplan.md
?? docs/design/synthetic_blow_code_revisions/01_004_synthetic_blow_code_revision_implementation_log.md
?? src/jet_simplex_search/clean_tower.py
?? src/jet_simplex_search/results.py
?? tests/integration/test_clean_state_collapser_tower.py
?? tests/test_clean_tower.py
?? tests/test_readme_quickstart.py
?? tests/test_release_metadata.py
?? tests/test_witness_consistency.py
```

This continuity report itself is additionally untracked after creation:

```text
docs/engineer_continuity/2026/06/13/01_001_engineering_continuity_report.md
```

## Changed Source Map

Major source additions:

```text
src/jet_simplex_search/clean_tower.py
src/jet_simplex_search/results.py
```

Major source edits:

```text
src/jet_simplex_search/api.py
src/jet_simplex_search/artifacts.py
src/jet_simplex_search/errors.py
src/jet_simplex_search/ids.py
src/jet_simplex_search/skeleton.py
src/jet_simplex_search/tower_adapter.py
src/jet_simplex_search/__init__.py
```

Metadata/docs edits:

```text
README.md
pyproject.toml
uv.lock
.gitignore
docs/design/synthetic_blow_code_revisions/01_004_synthetic_blow_code_revision_implementation_log.md
```

## Important Invariants To Preserve

Do not weaken these without Project Owner approval:

- `search_simplices(...)` is graph-H only.
- `search_skeleton_simplices(...)` is the lower-level skeleton/tower API.
- The public graph-H path uses `CleanStaticTowerAdapter`.
- The raw `StateCollapserStaticTowerAdapter` remains lower-level and tested.
- Clean tower stored tiers do not contain loops.
- Clean tower stored tiers do not contain parallel endpoint pairs.
- Formal identities are simplex-engine devices, not stored graph edges.
- Internal quotient edges project to formal downstream identities.
- Source-sensitive edge-fiber target lookup is part of clean projection data.
- Strict v0.1 label policy requires exact label tuple agreement.
- Artifact writer accepts explicit result classes only.
- Missing downstairs interior means no upstairs interior search.
- Degenerate simplex addresses remain first-class records and are not collapsed
  to their nondegenerate spines.
- H-lift counts preserve original H loop/parallel multiplicity without
  polluting skeleton/tower search.

## Known Deferred Work

Still not implemented:

- Kan replacement;
- horn filling;
- cofibrant replacement variants beyond the current small-object search;
- expanded H witness assignment artifacts;
- compressed artifact storage;
- SQLite or DuckDB artifact storage;
- bitset/CSR acceleration;
- GPU/tensor acceleration;
- multiprocessing;
- benchmarks sufficient for public speedup claims;
- CI;
- changelog/release notes;
- PyPI publication;
- tagging;
- GitHub public visibility changes;
- broad Ruff formatting pass.

## Release Readiness Notes

Safer public claims now:

- The package is a Python library pre-release.
- It studies graph `H`, skeletonizes to `G`, builds a static quotient tower, and
  searches directed flag simplices through dimension `k`.
- Degenerate simplices are first-class.
- The graph-H workflow computes compressed tier-0 H-lift counts.
- The package uses a GitHub `state_collapser` `v0.7.2` dependency.
- Local tests, smoke scripts, Ruff lint, and build have passed in this tree.

Still unsafe to claim:

- production readiness;
- PyPI availability;
- GitHub CI status;
- benchmark-validated asymptotic or wall-clock superiority;
- Kan replacement;
- complete expanded witness enumeration;
- public release complete.

Before public release, still do:

1. Add CI and only then consider CI badges.
2. Decide changelog/release-note format.
3. Run a final public-facing profanity/path/internal-link review.
4. Decide whether to apply Ruff formatting as a separate mechanical commit.
5. Decide whether to add `py.typed` and typing classifier.
6. Decide whether to make the repo public.
7. Decide whether to tag `v0.1.0`.
8. Decide whether PyPI publication is in scope.

## Resume Instructions

When resuming from this point:

1. Run `git status --short`.
2. Remember that some staged review/design files predate the final code pass.
3. Do not revert user or prior staged changes.
4. Run `uv run pytest` before making behavior claims.
5. Run smoke scripts if changing enumeration, lifting, or README counts.
6. Use `CleanStaticTowerAdapter` for public graph workflow work.
7. Use raw `StateCollapserStaticTowerAdapter` only for explicit lower-level
   adapter work.
8. Keep root README free of internal Prime Directive and release-prep links.
9. Keep Abdul Malik attribution in public and design docs.
10. Do not tag, publish, upload distributions, or make the repo public without
    explicit Project Owner approval.

## Quick Command Reference

Tests:

```bash
uv run pytest
```

Smoke harness:

```bash
uv run python -c "import subprocess, sys; failures=[]
for i in range(1,17):
    path=f'smoke/smoke_{i:03}.py'
    proc=subprocess.run([sys.executable, path], text=True, capture_output=True)
    status='ok' if proc.returncode==0 else f'fail {proc.returncode}'
    print(f'{path}: {status}')
    if proc.returncode!=0:
        failures.append(path)
raise SystemExit(1 if failures else 0)"
```

Build:

```bash
uv build --out-dir /private/tmp/jet-simplex-search-revision-build
```

Ruff lint:

```bash
uv run ruff check .
```

Ruff format check:

```bash
uv run ruff format --check .
```

