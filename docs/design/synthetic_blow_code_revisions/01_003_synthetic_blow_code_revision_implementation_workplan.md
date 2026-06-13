# Synthetic Blow Code Revision Implementation Workplan

## Status

Implementation workplan derived from:

```text
code_review/01_002_synthetic_blow_project_review.md
docs/design/synthetic_blow_code_revisions/01_001_synthetic_blow_code_revision_scope.md
docs/design/synthetic_blow_code_revisions/01_002_synthetic_blow_code_revision_blueprint.md
```

This document is a Phase.Stage.Action execution plan. It is not an
implementation patch. Per the repo Prime Directive, this workplan becomes
binding only for an implementation pass explicitly approved by the Project
Owner.

## Attribution

The static quotient-tower simplex search algorithm is PM Abdul Malik's work and
part of his thesis. This includes:

- degree-wise simplex enumeration;
- cached frontier recurrence;
- formal identity handling for degenerate skeleton addresses;
- static quotient tower construction;
- small-object fiber-addressed lift search over existing downstairs simplices.

The Project Owner clarified the H-to-G package pipeline:

```text
study H
  -> clean / skeletonize to G
  -> build the clean tower G^bullet
  -> search simplices in G^bullet
  -> perform multiplicity / etale H-lift accounting
```

This implementation must preserve that attribution and that pipeline in source,
tests, artifacts, README language, and release-facing documentation.

## Planning Decisions Carried From The Blueprint

The implementation workplan assumes these blueprint decisions:

1. Use a `jet_simplex_search`-owned clean tower bridge for this revision.
2. Treat a future `state_collapser` clean-tower primitive as an upstream
   follow-up, not as a blocker for this JSS revision.
3. Keep the v0.1 clean quotient edge label policy strict: exact label agreement.
4. Make `search_simplices` graph/H-only.
5. Keep `search_skeleton_simplices` as the lower-level adapter/skeleton API.
6. Move `SearchWithHLiftsResult` out of `api.py` into a result module.
7. Replace artifact duck typing with explicit result classes.
8. Remove public release dependency drift around `state_collapser`.
9. Delete dead helpers and tracked backup/temp image files.

If the Project Owner rejects one of these decisions before implementation, this
workplan must be revised before source edits begin.

## Umbrella Execution Spine

This workplan is one umbrella job with ordered phases. Child streams are
checkpoints, not endpoints.

Ordered streams:

1. Baseline, branch, and implementation log.
2. Result model and public API boundary.
3. Typed artifact writer.
4. Clean static tower bridge and adapter.
5. Public H workflow switch to the clean tower.
6. Regression and release tests.
7. Dead-code and stale-cache cleanup.
8. Release-facing docs and metadata cleanup.
9. Repository hygiene.
10. Full verification and implementation log closeout.

During an approved implementation pass, do not stop after completing one stream
unless a hard stop condition triggers.

## Hard Stop Conditions

Stop and ask the Project Owner before continuing if:

- implementation approval is absent or ambiguous;
- source reality contradicts the blueprint in a way that changes semantics;
- a clean quotient edge label conflict appears in an existing README, smoke, or
  test example;
- arbitrary user schemas cannot be applied to reified quotient edges without a
  new semantic decision;
- `state_collapser` public APIs are insufficient to build a one-block quotient
  step without unstable internal dependency;
- switching to clean tower construction changes established smoke counts and the
  difference cannot be immediately explained;
- the actual GitHub `state_collapser` release tag differs from local `v0.7.2`;
- release dependency changes require network or lockfile regeneration that fails
  under the sandbox;
- deleting a supposedly dead helper breaks README, smoke scripts, or public
  exports in a way not covered by this workplan;
- tests show that the clean tower bridge would require editing
  `../state_collapser` directly;
- public documentation would need to link `docs/prime_directive` or internal
  release-prep docs to explain the result;
- the work would require Kan replacement, horn filling, cofibrant replacement
  variants, expanded H witness enumeration, PyPI publication, tagging, or making
  the repository public.

## Execution Principles

- Execute phases in order unless the Project Owner explicitly changes order.
- Preserve unrelated user changes.
- Use `rg` for source searches.
- Use `apply_patch` for manual edits.
- Do not edit `../state_collapser` in this workplan.
- Do not rewrite git history.
- Do not remove raw or generated files unless this workplan explicitly names
  them and a source check confirms they are safe to remove.
- Keep the tower static: no dynamic search-time rebuilding.
- Keep formal identities as simplex-engine devices, not stored graph edges.
- Keep H-loop and H-parallel-edge multiplicity in H-lift accounting.
- Keep zero-count skeleton simplices in public results.
- Run targeted tests after each semantic stream and full tests before closeout.

---

# Phase 0 - Execution Gate, Baseline, And Source Synchronization

## Stage 0.1 - Confirm Authority

### Action 0.1.1 - Verify Explicit Implementation Approval

Target files:

```text
none
```

Procedure:

- Confirm the Project Owner has explicitly requested execution of this workplan.
- Confirm the approval applies to source code changes, tests, docs, and release
  metadata in this repository.
- Confirm the approval does not include direct edits to `../state_collapser`.
- Record the approval phrase in the implementation log once the log exists.

Completion criteria:

- Implementation approval is present.
- Approved repository scope is known.

Stop condition:

- If approval is absent or ambiguous, stop after creating this workplan.

### Action 0.1.2 - Re-read The Controlling Documents

Target files:

```text
code_review/01_002_synthetic_blow_project_review.md
docs/design/synthetic_blow_code_revisions/01_001_synthetic_blow_code_revision_scope.md
docs/design/synthetic_blow_code_revisions/01_002_synthetic_blow_code_revision_blueprint.md
docs/prime_directive/prime_directive.md
docs/prime_directive/common_failure_mode_002_implementation_without_owner_approval.md
docs/prime_directive/common_failure_mode_003_gameplan_rewrite_during_implementation.md
docs/prime_directive/common_failure_mode_005_umbrella_workplan_fragmentation.md
docs/prime_directive/public_release_readiness_protocol.md
```

Procedure:

- Re-read each controlling document before source edits.
- Check that this workplan still matches the blueprint decisions.
- Check that no later PO reply in the report changes a stream.

Completion criteria:

- Source documents have been reread.
- No mismatch is found.

Stop condition:

- If a mismatch is found, update this workplan first and ask for approval.

## Stage 0.2 - Branch And Git State

### Action 0.2.1 - Inspect Git State

Target files:

```text
none
```

Commands:

```bash
git status --short
git branch --show-current
git rev-parse HEAD
```

Procedure:

- Capture current branch.
- Capture current commit.
- Capture modified, deleted, and untracked files.
- Identify unrelated user changes.
- Do not revert unrelated changes.

Completion criteria:

- Dirty worktree state is known.

Stop condition:

- If unrelated dirty files would be overwritten by this implementation, stop and
  ask the Project Owner how to proceed.

### Action 0.2.2 - Create Or Confirm A Dedicated Branch

Target files:

```text
none
```

Command:

```bash
git checkout -b codex/synthetic-blow-code-revisions
```

Procedure:

- Create a dedicated branch before implementation.
- If the branch already exists, inspect it before switching.
- Do not switch branches if doing so would hide uncommitted user work.

Completion criteria:

- Work is on a dedicated branch, or the Project Owner explicitly allows staying
  on the current branch.

Stop condition:

- If branch creation or switching is unsafe, stop.

## Stage 0.3 - Baseline Verification

### Action 0.3.1 - Run Full Baseline Tests

Target files:

```text
none
```

Command:

```bash
uv run pytest
```

Procedure:

- Run the full test suite before source edits.
- Record pass/fail count and runtime in the implementation log.

Completion criteria:

- Baseline test state is known.

Stop condition:

- If baseline tests fail, stop and investigate before revision edits.

### Action 0.3.2 - Run Current Smoke Scripts

Target files:

```text
none
```

Commands:

```bash
uv run python smoke/smoke_001.py
uv run python smoke/smoke_002.py
uv run python smoke/smoke_003.py
uv run python smoke/smoke_004.py
uv run python smoke/smoke_005.py
uv run python smoke/smoke_006.py
uv run python smoke/smoke_007.py
uv run python smoke/smoke_008.py
uv run python smoke/smoke_009.py
uv run python smoke/smoke_010.py
uv run python smoke/smoke_011.py
uv run python smoke/smoke_012.py
uv run python smoke/smoke_013.py
uv run python smoke/smoke_014.py
uv run python smoke/smoke_015.py
uv run python smoke/smoke_016.py
```

Procedure:

- Run every smoke script.
- Record whether each script completes.
- Do not update smoke arguments or expected counts yet.

Completion criteria:

- Baseline smoke state is known.

Stop condition:

- If a smoke script fails at baseline, record it and ask whether to repair
  baseline or continue with known failure.

### Action 0.3.3 - Inspect Adjacent `state_collapser`

Target files:

```text
none
```

Commands:

```bash
git -C ../state_collapser status --short
git -C ../state_collapser tag --list
git -C ../state_collapser remote -v
```

Procedure:

- Confirm adjacent `state_collapser` is clean.
- Confirm tag `v0.7.2` exists locally.
- Confirm remote points to `TYLERSFOSTER/state_collapser`.
- Record results in the implementation log.

Completion criteria:

- Local adjacent state-collapser release facts are known.

Stop condition:

- If tag `v0.7.2` is absent or adjacent repo is dirty in relevant files, stop
  before release dependency work.

## Stage 0.4 - Implementation Log

### Action 0.4.1 - Create Implementation Log

Target files:

```text
docs/design/synthetic_blow_code_revisions/01_004_synthetic_blow_code_revision_implementation_log.md
```

Procedure:

- Create an implementation log.
- Include:
  - approval phrase;
  - branch name;
  - baseline git state;
  - baseline test result;
  - baseline smoke result;
  - adjacent `state_collapser` status.
- Add an empty section for each implementation phase.

Completion criteria:

- The implementation log exists before source edits.

Stop condition:

- If the log cannot be created, stop before source edits.

---

# Phase 1 - Result Model And Public API Boundary

## Stage 1.1 - Add Explicit Result Module

### Action 1.1.1 - Create `results.py`

Target files:

```text
src/jet_simplex_search/results.py
```

Procedure:

- Move the `SearchWithHLiftsResult` dataclass out of `api.py`.
- Import `HLiftDiagnostics`, `SimplexHLiftRecord`,
  `SimplexSearchResult`, and `SkeletonizationResult`.
- Preserve frozen dataclass and `slots=True`.
- Preserve tuple normalization in `__post_init__`.
- Add a type alias:

```python
SearchResult = SimplexSearchResult | SearchWithHLiftsResult
```

Completion criteria:

- `SearchWithHLiftsResult` exists in `results.py`.
- No behavior changes yet.

Stop condition:

- If moving the dataclass causes an import cycle, stop and inspect module
  dependencies before proceeding.

### Action 1.1.2 - Re-export Result Types

Target files:

```text
src/jet_simplex_search/__init__.py
src/jet_simplex_search/api.py
```

Procedure:

- Import `SearchWithHLiftsResult` from `results.py` in `api.py`.
- Keep `SearchWithHLiftsResult` importable from `jet_simplex_search.api` for a
  short compatibility bridge.
- Re-export `SearchWithHLiftsResult` from package root.
- Consider re-exporting `SimplexSearchResult` from package root if it improves
  lower-level API clarity.

Completion criteria:

- Existing imports of `SearchWithHLiftsResult` still pass.
- Package root exports remain accurate.

Stop condition:

- If package root re-export introduces circular imports, keep root export
  minimal and document the result module path.

## Stage 1.2 - Split Public H API From Skeleton API

### Action 1.2.1 - Make `search_simplices` Graph/H-Only

Target files:

```text
src/jet_simplex_search/api.py
```

Procedure:

- Remove the `adapter` parameter from `search_simplices`.
- Require `graph: GraphInput`.
- Keep `contraction_schema`, `k`, and `artifact_config`.
- Return `SearchWithHLiftsResult`, not a union.
- Validate `k` at function entry.
- Run:
  - `skeletonize_graph(graph)`;
  - clean tower adapter construction once Phase 3 exists;
  - until Phase 3 exists, preserve temporary current adapter path only if needed
    behind a TODO-free private helper and remove it when Phase 5 switches.
- Write artifacts only after constructing the combined result.

Completion criteria:

- `search_simplices` has one public meaning: study H.
- No adapter fallback remains in this public function.

Stop condition:

- If immediate clean tower dependency would create a circular import before
  Phase 3, do a minimal temporary private helper and remove it in Phase 5.

### Action 1.2.2 - Make `search_skeleton_simplices` The Lower-Level API

Target files:

```text
src/jet_simplex_search/api.py
```

Procedure:

- Keep `search_skeleton_simplices`.
- Accept exactly one of `adapter` or `graph`.
- If both are provided, raise `TypeError` with a clear message.
- If neither is provided, raise `TypeError` with a clear message.
- If `adapter` is provided, call `run_static_small_object_search`.
- If `graph` is provided, treat it as an already-clean skeleton graph and build
  a tower adapter.
- Initially use existing `StateCollapserStaticTowerAdapter.from_graph`; switch
  to `CleanStaticTowerAdapter.from_graph` in Phase 5.
- Return `SimplexSearchResult`.

Completion criteria:

- Skeleton/tower-only search has one stable return type.
- Ambiguous graph-plus-adapter calls are rejected.

Stop condition:

- If tests or smoke scripts rely on old `search_simplices(adapter=...)`, update
  them in Stage 1.3 rather than restoring the old fallback.

### Action 1.2.3 - Remove Or Privatize Static Search Context

Target files:

```text
src/jet_simplex_search/api.py
tests/test_api.py
```

Procedure:

- Remove `StaticSearchContext` if it is just a thin adapter/k wrapper.
- Remove `build_static_search_context` if it only validates k and constructs an
  adapter.
- Replace with private helper `_resolve_skeleton_adapter` only if needed.
- Update tests that exist only to preserve the deleted helper.

Completion criteria:

- No public no-value context abstraction remains.

Stop condition:

- If README or public examples reference `build_static_search_context`, stop and
  update docs before deletion.

## Stage 1.3 - Update API Tests

### Action 1.3.1 - Update Public API Tests

Target files:

```text
tests/test_api.py
```

Procedure:

- Replace `search_simplices(adapter=FakeStaticTowerAdapter(), k=1)` with
  `search_skeleton_simplices(adapter=FakeStaticTowerAdapter(), k=1)`.
- Assert public `search_simplices(graph=..., k=...)` returns
  `SearchWithHLiftsResult`.
- Assert `search_simplices` rejects or cannot accept `adapter`.
- Assert `search_skeleton_simplices(adapter=..., k=...)` returns
  `SimplexSearchResult`.
- Assert `search_skeleton_simplices(graph=..., k=...)` returns
  `SimplexSearchResult`.
- Assert `search_skeleton_simplices(adapter=..., graph=..., k=...)` raises
  `TypeError`.
- Assert artifact writing works from both public and skeleton-only workflows.

Completion criteria:

- API tests express the split result boundary.

Stop condition:

- If Python signature errors differ from explicit `TypeError` messages, choose
  the clearer public contract and adjust tests accordingly.

### Action 1.3.2 - Run API Tests

Target files:

```text
none
```

Command:

```bash
uv run pytest tests/test_api.py
```

Procedure:

- Run only API tests.
- Record results in the implementation log.

Completion criteria:

- API tests pass.

Stop condition:

- If API tests fail for reasons outside the current phase, stop and
  resynchronize before continuing.

---

# Phase 2 - Artifact Writer Type Discipline

## Stage 2.1 - Replace Duck Typing With Explicit Result Types

### Action 2.1.1 - Update Artifact Type Imports

Target files:

```text
src/jet_simplex_search/artifacts.py
```

Procedure:

- Import `SearchWithHLiftsResult` and `SearchResult` from `results.py`.
- Update function annotations to use explicit result types.
- Remove or stop using `_is_combined_result`.
- Keep `ArtifactWriteError` for unsupported result objects.

Completion criteria:

- Artifact writer depends on declared result classes.

Stop condition:

- If importing `SearchWithHLiftsResult` creates an import cycle, move shared
  result types or artifact imports to break the cycle rather than restoring duck
  typing.

### Action 2.1.2 - Split Payload Builders

Target files:

```text
src/jet_simplex_search/artifacts.py
```

Procedure:

- Implement explicit branch:

```python
if isinstance(result, SearchWithHLiftsResult):
    ...
elif isinstance(result, SimplexSearchResult):
    ...
else:
    raise ArtifactWriteError(...)
```

- Add or update helpers:
  - `_combined_result_payload`;
  - `_simplex_search_payload`;
  - `_combined_manifest_payload`;
  - `_simplex_manifest_payload`;
  - `_combined_diagnostics_payload`;
  - `_diagnostics_payload`.
- Preserve existing single JSON and manifest-table output shapes except for
  adding explicit `result_kind`.

Completion criteria:

- Payload generation is class-based, not attribute-shape based.

Stop condition:

- If output shape changes beyond `result_kind`, update tests and artifact docs
  only after confirming the change is intentional.

### Action 2.1.3 - Remove Unsupported Config Field

Target files:

```text
src/jet_simplex_search/artifacts.py
tests/test_artifacts.py
README.md
docs
```

Procedure:

- Remove `ArtifactConfig.max_expanded_h_lift_witnesses`.
- Keep `include_expanded_h_lift_witnesses`.
- Preserve the `ArtifactWriteError` raised when expanded witness output is
  requested.
- Search for references before deletion.

Completion criteria:

- No unused expanded-witness max field remains.
- Expanded witness request still fails clearly.

Stop condition:

- If a public doc promises `max_expanded_h_lift_witnesses`, stop and update the
  doc with PO-approved limitations language.

## Stage 2.2 - Update Artifact Tests

### Action 2.2.1 - Add Typed Artifact Tests

Target files:

```text
tests/test_artifacts.py
```

Procedure:

- Assert skeleton-only result writes schema version 1.
- Assert skeleton-only manifest includes `result_kind = "simplex_search"`.
- Assert H result writes schema version 2.
- Assert H manifest includes `result_kind = "skeleton_search_with_h_lifts"`.
- Assert passing `object()` to `write_search_artifact` raises
  `ArtifactWriteError`.
- Assert combined diagnostics include:
  - `skeletonization`;
  - `skeleton_search`;
  - `h_lifts`.
- Assert manifest-table row counts match JSONL line counts.
- Assert H-lift face-factor table contains expected loop or non-loop factor rows
  for a simple graph.

Completion criteria:

- Artifact tests prove explicit result handling.

Stop condition:

- If existing artifact consumers rely on the old absence of `result_kind`, stop
  and ask whether to bump schema or keep backwards-compatible optional field.

### Action 2.2.2 - Run Artifact Tests

Target files:

```text
none
```

Command:

```bash
uv run pytest tests/test_artifacts.py
```

Procedure:

- Run artifact tests.
- Record results in the implementation log.

Completion criteria:

- Artifact tests pass.

Stop condition:

- If artifact tests expose a schema ambiguity, resolve before continuing.

---

# Phase 3 - Clean Static Tower Bridge

## Stage 3.1 - Add Clean Tower Data Records

### Action 3.1.1 - Create `clean_tower.py`

Target files:

```text
src/jet_simplex_search/clean_tower.py
```

Procedure:

- Create a new module for clean quotient tower construction.
- Add dataclasses:
  - `CleanTowerConfig`;
  - `CleanTierProjection`;
  - `CleanTowerDiagnostics`;
  - `CleanTower`;
  - `CleanStaticTowerAdapter`.
- Keep dataclasses frozen where possible.
- Normalize mapping and tuple fields in `__post_init__`.
- Add `to_dict` for diagnostics.

Completion criteria:

- Clean tower records exist without changing public workflow yet.

Stop condition:

- If clean tower records duplicate existing record types in a confusing way,
  stop and decide whether to colocate them in `records.py`.

### Action 3.1.2 - Define Clean Tower Error Surface

Target files:

```text
src/jet_simplex_search/errors.py
src/jet_simplex_search/clean_tower.py
```

Procedure:

- Add `CleanTowerConstructionError` if the error taxonomy benefits from a
  dedicated clean-tower construction error.
- Otherwise use `TowerAdapterError` consistently.
- Use the chosen error for:
  - label conflicts in quotient edge realization;
  - missing projection data;
  - invalid clean tier graph realization;
  - unsupported schema behavior.

Completion criteria:

- Clean tower construction failures have one clear error type.

Stop condition:

- If adding a new error breaks public error docs or tests unexpectedly, use
  existing `TowerAdapterError` and document the choice in the log.

## Stage 3.2 - Build Current-Tier State-Collapser Inputs

### Action 3.2.1 - Convert Clean Graph To State-Collapser Objects

Target files:

```text
src/jet_simplex_search/clean_tower.py
```

Procedure:

- Add private helper to convert one clean `GraphInput` into:
  - state-collapser `State` objects;
  - state-collapser `BaseEdge` objects;
  - vertex id to `State` mapping;
  - edge id to `BaseEdge` mapping.
- Use deterministic identities:
  - `("jet-simplex-search", "clean-tower", "vertex", tier, vertex_id)`;
  - `("jet-simplex-search", "clean-tower", "edge", tier, edge_id)`.
- Preserve edge labels.
- Do not add formal identities as state-collapser edges.

Completion criteria:

- A clean tier graph can be converted into temporary state-collapser inputs.

Stop condition:

- If state-collapser object identities affect schema behavior in an unexpected
  way, stop and inspect schema tests before proceeding.

### Action 3.2.2 - Assign Schema Blocks Against Current Graph

Target files:

```text
src/jet_simplex_search/clean_tower.py
```

Procedure:

- Add helper to determine current clean graph schema blocks.
- If `schema is None`, return no blocks.
- If `schema.ordered_blocks()` is nonempty, respect declared order.
- If declared order is empty but `assign_edge` returns blocks, derive
  deterministic block order from current edge assignment order.
- Skip blocks with no assigned current edges.
- Record skipped empty blocks in diagnostics.

Completion criteria:

- Current graph block schedule is deterministic and schema-driven.

Stop condition:

- If a known state-collapser schema cannot be re-applied to current clean edges,
  stop and ask whether that schema is supported in JSS clean tower mode.

### Action 3.2.3 - Add Single-Block Schema Wrapper

Target files:

```text
src/jet_simplex_search/clean_tower.py
```

Procedure:

- Add a private `SingleBlockContractionSchema` wrapper.
- Delegate `assign_edge`.
- Return the selected block only when delegate assignment equals selected block.
- Return `None` for all other edges.
- Return exactly the selected block from `ordered_blocks`.

Completion criteria:

- Temporary state-collapser calls can contract one selected block.

Stop condition:

- If schema block equality is not stable across current graph conversion,
  inspect `SchemaBlockId` semantics before continuing.

## Stage 3.3 - Implement One-Step Clean Quotient Realization

### Action 3.3.1 - Build One Temporary One-Block Tower

Target files:

```text
src/jet_simplex_search/clean_tower.py
```

Procedure:

- Call `build_partition_tower_full` with:
  - current tier states;
  - current tier edges;
  - `current_state=None`;
  - `schema=SingleBlockContractionSchema(...)`.
- Use the resulting one-step tower only to read quotient state cells.
- Do not expose this temporary tower as the final JSS tower.

Completion criteria:

- One block can be contracted from a clean current graph.

Stop condition:

- If `build_partition_tower_full` creates more tiers than expected, inspect the
  wrapper and block scheduling before proceeding.

### Action 3.3.2 - Realize Quotient Vertices

Target files:

```text
src/jet_simplex_search/clean_tower.py
```

Procedure:

- Read quotient state layer from the temporary tower.
- Map each current vertex id to a quotient cell.
- Sort quotient cells by sorted current vertex ids they contain.
- Assign deterministic downstream vertex ids:

```text
cell:{downstairs_tier}:{ordinal}
```

- Store vertex projection:

```text
current vertex id -> downstream vertex id
```

- Store optional member provenance for diagnostics.

Completion criteria:

- Downstream quotient vertices are deterministic.
- Vertex projection is total on current vertices.

Stop condition:

- If any current vertex lacks a quotient cell, stop.

### Action 3.3.3 - Realize Quotient Edges

Target files:

```text
src/jet_simplex_search/clean_tower.py
```

Procedure:

- For every current non-loop edge:
  - project source;
  - project target;
  - if source projection equals target projection, project edge to
    `identity_edge_id(projected_source)` and do not store a downstream non-loop
    edge;
  - otherwise group by projected endpoint pair.
- For each non-loop projected pair:
  - verify all projected current edges have identical labels;
  - create one `InputEdge` with id `tier_simple_edge_id`;
  - store edge projection from every current edge to the clean downstream edge;
  - record collapsed parallel count.
- Sort downstream edges deterministically.

Completion criteria:

- Downstream graph is loop-free and has at most one edge per endpoint pair.
- Edge projection is total on current non-loop edges.

Stop condition:

- If labels conflict, raise clean tower construction error and stop if this
  occurs in existing examples.

### Action 3.3.4 - Build Source-Sensitive Edge-Fiber Targets

Target files:

```text
src/jet_simplex_search/clean_tower.py
```

Procedure:

- For every current vertex, record formal identity projection:
  - upstairs identity at source projects to downstream identity at projected
    source;
  - edge-fiber target includes the same upstairs source for that identity.
- For every current non-loop edge:
  - use computed edge projection;
  - add current target to
    `(downstairs_edge_id, current source)` target set.
- Freeze target sets.

Completion criteria:

- `edge_fiber_targets` is source-sensitive and includes identities.

Stop condition:

- If edge-fiber targets cannot represent a nonidentity edge over a downstairs
  identity, stop because this breaks degenerate lift semantics.

## Stage 3.4 - Implement Full Clean Tower Builder

### Action 3.4.1 - Build `build_clean_static_tower`

Target files:

```text
src/jet_simplex_search/clean_tower.py
```

Procedure:

- Validate the input graph.
- Assert or realize it as clean:
  - no stored loops;
  - no parallel endpoint pairs.
- Initialize tier list with the input graph as `G_0`.
- Iterate schema blocks against the current clean graph.
- For each nonempty block:
  - run one-step quotient realization;
  - append clean downstream graph;
  - append projection record;
  - update diagnostics.
- Stop if:
  - no nonempty block remains;
  - graph has one or zero vertices and `stop_at_singleton=True`;
  - `max_tiers` is reached.

Completion criteria:

- A complete clean static tower can be built before simplex search starts.

Stop condition:

- If repeated schema block derivation causes infinite tiers, enforce
  `max_tiers` and stop for PO decision.

### Action 3.4.2 - Implement `CleanStaticTowerAdapter`

Target files:

```text
src/jet_simplex_search/clean_tower.py
```

Procedure:

- Implement the `StaticTowerAdapterProtocol`.
- Return tier ids as `tuple(range(len(tier_graphs)))`.
- Return tier vertices directly from stored `GraphInput`.
- Return tier non-loop edges directly from stored `GraphInput`.
- Return sources and targets from stored edge lookup.
- Use adjacent `CleanTierProjection` for:
  - `project_vertex`;
  - `project_edge`;
  - `edge_fiber_targets`.
- For identity edge projection, project the identity vertex and return
  downstream identity id.
- `tier0_vertex_id_to_input_vertex_id` returns identity mapping for tier-0
  vertex ids.
- `bottommost_nondegenerate_tier` returns the last tier with more than one
  vertex if present, otherwise last tier.

Completion criteria:

- Clean adapter can be passed to `run_static_small_object_search`.

Stop condition:

- If bottom-tier semantics differ from the existing adapter's behavior in a
  count-changing way, write a focused test and inspect before switching public
  workflow.

## Stage 3.5 - Clean Tower Tests

### Action 3.5.1 - Add Unit Tests For No-Schema And One-Step Cases

Target files:

```text
tests/test_clean_tower.py
```

Procedure:

- Test no schema keeps one tier.
- Test tier graph has no stored loops.
- Test normalization adds formal identities.
- Test single contraction block collapses vertices.
- Test internal contracted edge projects to downstairs identity.
- Test edge fiber over identity includes nonidentity upstairs edge where
  appropriate.

Completion criteria:

- Basic clean tower construction is covered.

Stop condition:

- If no-schema behavior differs from blueprint, revise code or ask before
  changing the design.

### Action 3.5.2 - Add Multi-Step Clean-Tier Regression Test

Target files:

```text
tests/test_clean_tower.py
```

Procedure:

- Construct a graph where:
  - first block creates raw parallel quotient edges;
  - clean realization collapses those parallel edges;
  - second block runs on the cleaned quotient edge.
- Assert intermediate clean tier has exactly one edge for the quotient endpoint
  pair.
- Assert final tier matches expected quotient.
- Assert diagnostics record collapsed parallel edge count.

Completion criteria:

- The reviewed bug class has a regression test.

Stop condition:

- If the test cannot be expressed using existing state-collapser schemas, stop
  and ask whether to add a JSS-local test schema.

### Action 3.5.3 - Add Label Conflict Test

Target files:

```text
tests/test_clean_tower.py
```

Procedure:

- Build a graph where two current-tier edges project to the same quotient pair
  with different labels.
- Assert clean tower construction raises the chosen clean tower error.
- Assert the error message names the endpoint pair and strict v0.1 policy.

Completion criteria:

- Strict label policy is tested at clean quotient realization.

Stop condition:

- If existing examples rely on label union, stop and ask for PO decision.

### Action 3.5.4 - Run Clean Tower Tests

Target files:

```text
none
```

Command:

```bash
uv run pytest tests/test_clean_tower.py
```

Procedure:

- Run clean tower tests.
- Record results in the implementation log.

Completion criteria:

- Clean tower tests pass.

Stop condition:

- If clean tower tests fail due to state-collapser API assumptions, stop and
  resynchronize against adjacent source.

---

# Phase 4 - Public Workflow Switch To Clean Tower

## Stage 4.1 - Switch API Construction

### Action 4.1.1 - Use Clean Adapter In `search_simplices`

Target files:

```text
src/jet_simplex_search/api.py
```

Procedure:

- Replace `StateCollapserStaticTowerAdapter.from_graph` in public H workflow
  with `CleanStaticTowerAdapter.from_graph`.
- Pass `skeletonization.skeleton_graph`.
- Pass `contraction_schema`.
- Keep H-lift computation against tier-0 adapter mapping.
- Keep artifact writing after result construction.

Completion criteria:

- Public H workflow uses the clean tower bridge.

Stop condition:

- If H-lift counts change for tier-0 examples, stop and investigate.

### Action 4.1.2 - Use Clean Adapter For Graph-Based Skeleton Search

Target files:

```text
src/jet_simplex_search/api.py
```

Procedure:

- In `search_skeleton_simplices(graph=...)`, build a `CleanStaticTowerAdapter`.
- In `search_skeleton_simplices(adapter=...)`, keep using the provided adapter.
- Do not skeletonize graph input in `search_skeleton_simplices`; treat it as
  already-clean skeleton graph.

Completion criteria:

- Lower-level graph route has clean tower semantics.
- Adapter route remains available for fake tests and raw adapter integration.

Stop condition:

- If lower-level graph route receives raw H with parallel edges in existing
  tests, update tests to call public H workflow or explicitly skeletonize first.

## Stage 4.2 - Preserve Raw State-Collapser Adapter As Lower-Level Boundary

### Action 4.2.1 - Keep Existing Adapter Tests But Rename Intent If Needed

Target files:

```text
tests/integration/test_state_collapser_static_tower.py
```

Procedure:

- Keep tests that explicitly cover `StateCollapserStaticTowerAdapter`.
- Update names/docstrings to clarify it is the raw state-collapser adapter, not
  the public H workflow tower constructor.
- Do not delete raw adapter unless the PO explicitly approves.

Completion criteria:

- Existing raw adapter behavior remains testable.

Stop condition:

- If raw adapter tests conflict with clean public semantics, split test modules
  instead of weakening either behavior.

### Action 4.2.2 - Add Clean Integration Test

Target files:

```text
tests/integration/test_clean_state_collapser_tower.py
```

Procedure:

- Add an integration test using a real `LabelBlockSchema`.
- Build a clean adapter through the public or clean API.
- Run `search_skeleton_simplices`.
- Assert simplices and fibers are emitted.
- Assert clean intermediate tiers are loop-free and simple.

Completion criteria:

- Clean bridge is tested against real state-collapser schema behavior.

Stop condition:

- If this integration test requires unstable state-collapser internals, stop.

## Stage 4.3 - Run Workflow Tests

### Action 4.3.1 - Run API, Clean Tower, And Integration Tests

Target files:

```text
none
```

Commands:

```bash
uv run pytest tests/test_api.py
uv run pytest tests/test_clean_tower.py
uv run pytest tests/integration/test_state_collapser_static_tower.py
uv run pytest tests/integration/test_clean_state_collapser_tower.py
```

Procedure:

- Run targeted workflow tests.
- Record results in the implementation log.

Completion criteria:

- Public and lower-level workflows pass targeted tests.

Stop condition:

- If public H workflow and raw adapter workflow disagree in unexplained ways,
  stop and inspect before proceeding.

---

# Phase 5 - Witness, Lift, And Semantic Regression Tests

## Stage 5.1 - Add Witness Consistency Tests

### Action 5.1.1 - Create Witness Consistency Test Module

Target files:

```text
tests/test_witness_consistency.py
```

Procedure:

- Add helper to flatten `SimplexSearchResult.simplices_by_tier_degree`.
- Add helper to build normalized graph by tier for an adapter.
- For every simplex:
  - assert witness indices are in range;
  - assert each witness edge exists;
  - assert witness edge source matches source vertex;
  - assert witness edge target matches target vertex.
- For lifted simplices:
  - assert `projection_simplex_id` points to an existing downstairs simplex id
    when tier is not bottom.

Completion criteria:

- Witness truth is tested for fake and clean real adapters.

Stop condition:

- If witness tests fail because `extend_simplex_direct` records too many edge
  ids, stop and inspect whether edge-id filtering must be restored.

### Action 5.1.2 - Add Projection Consistency Assertions

Target files:

```text
tests/test_witness_consistency.py
```

Procedure:

- For each lifted simplex over a downstairs simplex:
  - project every upstairs vertex;
  - compare projected vertex tuple to downstairs vertex tuple;
  - project last-edge ids;
  - assert projected last edges include the downstairs last edge or projected
    identity when appropriate.

Completion criteria:

- Projection consistency is checked at the record level.

Stop condition:

- If current records do not retain enough information for this assertion, stop
  and decide whether to extend records or narrow the test.

## Stage 5.2 - Preserve Missing-Downstairs-Interior Behavior

### Action 5.2.1 - Keep Boundary-No-Interior Regression

Target files:

```text
tests/test_fiber_lift.py
tests/test_clean_tower.py
```

Procedure:

- Preserve the existing fake test where upstairs has a triangle but no
  downstairs 2-simplex record is supplied.
- Add a clean adapter variant if practical.
- Assert no degree-2 upstairs simplex is emitted when no downstairs degree-2
  simplex exists.

Completion criteria:

- The small-object distinction from Kan filling remains tested.

Stop condition:

- If clean tower construction auto-generates the downstairs 2-simplex in the
  test setup, keep the fake adapter test as the authoritative regression.

## Stage 5.3 - Run Semantic Tests

### Action 5.3.1 - Run Lift And Witness Tests

Target files:

```text
none
```

Commands:

```bash
uv run pytest tests/test_fiber_lift.py
uv run pytest tests/test_witness_consistency.py
```

Procedure:

- Run lift and witness tests.
- Record results in the implementation log.

Completion criteria:

- Fiber lifting and witness truth tests pass.

Stop condition:

- If witness truth fails, do not continue to cleanup or release docs.

---

# Phase 6 - Skeleton Label Policy Documentation

## Stage 6.1 - Clarify Source Docstrings

### Action 6.1.1 - Update Label Policy Docstrings

Target files:

```text
src/jet_simplex_search/skeleton.py
src/jet_simplex_search/clean_tower.py
```

Procedure:

- Clarify `SkeletonLabelPolicy.REQUIRE_IDENTICAL` as the v0.1 policy.
- Update `skeletonize_graph` docstring to say parallel H edges may collapse only
  when their label tuples agree exactly.
- Add clean tower label-policy comments/docstrings for quotient edge collapse.
- Do not add new label aggregation behavior.

Completion criteria:

- Source docs state the strict v0.1 policy.

Stop condition:

- If docstrings would duplicate long design discussion, keep them concise and
  put detail in tests/docs.

## Stage 6.2 - Add Label Policy Test Naming

### Action 6.2.1 - Update Skeleton Label Tests

Target files:

```text
tests/test_skeleton.py
```

Procedure:

- Rename or add test:

```python
test_v01_label_policy_requires_exact_parallel_edge_label_agreement
```

- Keep existing pass/fail coverage for identical vs different labels.

Completion criteria:

- Tests name the intended label policy.

Stop condition:

- If renaming tests creates churn without clarity, add one new explicit test
  instead.

### Action 6.2.2 - Run Skeleton Tests

Target files:

```text
none
```

Command:

```bash
uv run pytest tests/test_skeleton.py
```

Procedure:

- Run skeleton tests.
- Record results in implementation log.

Completion criteria:

- Skeleton tests pass.

---

# Phase 7 - Dead Code And Stale Cache Cleanup

## Stage 7.1 - Search Cleanup Candidates

### Action 7.1.1 - Search For Candidate Symbols

Target files:

```text
src
tests
smoke
README.md
docs
```

Command:

```bash
rg -n "fiber_id|_simple_edge_action_ids_cache|_edge_id_to_action_cell|max_expanded_h_lift_witnesses|StaticSearchContext|build_static_search_context" src tests smoke README.md docs
```

Procedure:

- Record every use.
- Classify each use as product behavior, test-only preservation, docs, or stale.

Completion criteria:

- Cleanup impact is known before deletion.

Stop condition:

- If a candidate is used in public README or smoke scripts, update call sites
  before deletion.

## Stage 7.2 - Delete Confirmed Dead Code

### Action 7.2.1 - Delete `fiber_id` If Still Test-Only

Target files:

```text
src/jet_simplex_search/ids.py
tests/test_ids.py
```

Procedure:

- Delete `fiber_id` if no product code uses it.
- Delete or update tests that only preserve `fiber_id`.
- Keep identity, skeleton edge, tier edge, simplex, and H-lift id helpers.

Completion criteria:

- No unused `fiber_id` remains.

Stop condition:

- If artifact schema now uses `fiber_id`, keep it and document the use.

### Action 7.2.2 - Delete Stale Tower Adapter Cache Fields

Target files:

```text
src/jet_simplex_search/tower_adapter.py
```

Procedure:

- Remove `_simple_edge_action_ids_cache` if it is still assigned but unread.
- Remove `_edge_id_to_action_cell` if it is still unused.
- Ensure raw adapter tests still pass.

Completion criteria:

- No stale adapter cache helpers remain.

Stop condition:

- If raw adapter behavior needs action-cell ids after this revision, keep a
  clearly named helper and test it.

### Action 7.2.3 - Delete Static Context Helpers If Still Thin

Target files:

```text
src/jet_simplex_search/api.py
tests/test_api.py
```

Procedure:

- Remove `StaticSearchContext` and `build_static_search_context` if not already
  removed in Phase 1.
- Ensure tests no longer import them.

Completion criteria:

- No public thin context helper remains.

Stop condition:

- If the helper gained real config responsibility during clean tower work, keep
  it and rename it to match that responsibility.

### Action 7.2.4 - Remove Expanded Witness Max Config If Still Present

Target files:

```text
src/jet_simplex_search/artifacts.py
tests/test_artifacts.py
README.md
docs
```

Procedure:

- Remove `max_expanded_h_lift_witnesses` if Phase 2 did not already remove it.
- Keep explicit failure for `include_expanded_h_lift_witnesses=True`.

Completion criteria:

- No unused expanded witness max remains.

## Stage 7.3 - Run Cleanup Tests

### Action 7.3.1 - Run Focused Cleanup Test Set

Target files:

```text
none
```

Commands:

```bash
uv run pytest tests/test_ids.py
uv run pytest tests/test_tower_adapter_fake.py
uv run pytest tests/integration/test_state_collapser_static_tower.py
uv run pytest tests/test_api.py
uv run pytest tests/test_artifacts.py
```

Procedure:

- Run tests affected by cleanup.
- Record results in implementation log.

Completion criteria:

- Cleanup did not remove live behavior.

Stop condition:

- If deletion breaks a live behavior, restore the symbol with a documented
  purpose instead of leaving a half-deleted state.

---

# Phase 8 - Release-Facing Metadata And README

## Stage 8.1 - Update Package Metadata

### Action 8.1.1 - Update `pyproject.toml` Dependency

Target files:

```text
pyproject.toml
```

Procedure:

- Replace local public dependency strategy with GitHub tag dependency:

```toml
"state-collapser @ git+https://github.com/TYLERSFOSTER/state_collapser.git@v0.7.2"
```

- Remove or revise `[tool.uv.sources]` local path override if release metadata
  tests require no local path.
- Keep version `0.1.0` unless PO separately approves a version change.

Completion criteria:

- Public dependency points at actual `state_collapser` GitHub release tag.

Stop condition:

- If lockfile regeneration requires network and fails, request escalation or
  stop according to sandbox instructions.

### Action 8.1.2 - Add Ruff And Metadata Fields If Missing

Target files:

```text
pyproject.toml
```

Procedure:

- Add `ruff` to dev dependencies if missing.
- Add project URLs if missing:
  - Homepage;
  - Repository;
  - Issues.
- Add classifiers suitable for `0.1.0` GitHub-only library pre-release.
- Add `[tool.ruff]` and `[tool.ruff.lint]` sections consistent with repo style.
- Do not add strict tooling that makes the current package impossible to test
  without separate approval.

Completion criteria:

- Package metadata is release-facing and professional.

Stop condition:

- If adding Ruff creates a large formatting/lint scope, stop and ask whether to
  include or defer automatic formatting.

## Stage 8.2 - Update README

### Action 8.2.1 - Fix Installation Section

Target files:

```text
README.md
```

Procedure:

- Keep existing logo and title.
- Replace sibling-checkout primary install path with GitHub pre-release install
  instructions.
- Move local sibling checkout language out of root README or make it clearly
  contributor-only if the PO allows.
- Ensure install commands match `pyproject.toml`.

Completion criteria:

- README no longer presents local path dependency as primary install path.

Stop condition:

- If exact GitHub install command cannot be verified without network, mark it as
  pre-release source install and add a release metadata test later.

### Action 8.2.2 - Update Quick Start For API Split

Target files:

```text
README.md
```

Procedure:

- Keep quick start using `search_simplices(graph=..., ...)`.
- Ensure it imports from current public API.
- Ensure printed fields still exist after result move.
- Update example output only if verified by a test or local run.

Completion criteria:

- README quick start is runnable against current source.

Stop condition:

- If clean tower changes example counts, stop and explain before updating
  output.

### Action 8.2.3 - Remove Internal Continuity Link

Target files:

```text
README.md
```

Procedure:

- Remove the root README link to:

```text
docs/release/engineering_continuity_report.md
```

- Do not replace it with a different internal continuity link.
- Do not link `docs/prime_directive`.
- Do not link release-prep plan.

Completion criteria:

- Root README does not link internal continuity or prime directive docs.

### Action 8.2.4 - Add Known Limitations Section

Target files:

```text
README.md
```

Procedure:

- Add a concise Known Limitations section separate from Release Status.
- Include:
  - Kan replacement not implemented;
  - expanded H witness artifacts not implemented;
  - strict v0.1 label policy;
  - static tower search only;
  - no GPU/tensor/CSR/multiprocessing acceleration;
  - primary public API studies H; lower-level skeleton search exists.

Completion criteria:

- README gives a bounded pre-release claim.

Stop condition:

- If this duplicates Release Status too heavily, consolidate without losing the
  separate Known Limitations heading.

## Stage 8.3 - Release Metadata Tests

### Action 8.3.1 - Add Release Metadata Test

Target files:

```text
tests/test_release_metadata.py
```

Procedure:

- Use `tomllib`.
- Assert package name is `jet-simplex-search`.
- Assert package version matches `jet_simplex_search.__version__`.
- Assert dependencies include `state-collapser`.
- Assert release dependency is not a local path.
- Assert project URLs exist.
- Assert Python version range matches README badges.

Completion criteria:

- Release metadata drift has a test.

Stop condition:

- If local `tool.uv.sources` must remain for development, gate the local-path
  assertion behind an explicit release-mode condition or ask the PO.

### Action 8.3.2 - Add README Quick-Start Test

Target files:

```text
tests/test_readme_quickstart.py
```

Procedure:

- Recreate README quick-start code in a test.
- Run the example graph.
- Assert:
  - result is `SearchWithHLiftsResult`;
  - skeleton diagnostics field exists;
  - H-lift diagnostics field exists;
  - expected counts match README output.
- Keep the test stable; do not fragile-parse Markdown unless necessary.

Completion criteria:

- README example has a regression test.

Stop condition:

- If README output is intentionally illustrative rather than exact, remove
  printed output from README or test only structural behavior.

### Action 8.3.3 - Run Release-Facing Tests

Target files:

```text
none
```

Commands:

```bash
uv run pytest tests/test_release_metadata.py
uv run pytest tests/test_readme_quickstart.py
```

Procedure:

- Run release-facing tests.
- Record results in implementation log.

Completion criteria:

- Release metadata and README quick-start tests pass.

---

# Phase 9 - Repository Hygiene

## Stage 9.1 - Remove Tracked Backup/Temp Image Files

### Action 9.1.1 - Confirm Tracked Backup Files

Target files:

```text
assets/images
```

Command:

```bash
git ls-files | rg 'assets/images/\\.\\$.*\\.(bkp|dtmp)$'
```

Procedure:

- Confirm which backup/temp files are tracked.
- Verify real logo and image files are not selected.

Completion criteria:

- Exact tracked backup/temp file list is known.

Stop condition:

- If the command matches real assets, stop and narrow pattern.

### Action 9.1.2 - Delete Confirmed Backup Files

Target files:

```text
assets/images/.$degens_dark.svg.bkp
assets/images/.$degens_light.svg.bkp
assets/images/.$how_dark.svg.bkp
assets/images/.$logo_dark.svg.bkp
assets/images/.$logo_light.svg.bkp
assets/images/.$logo_light.svg.dtmp
```

Procedure:

- Delete only confirmed tracked backup/temp files.
- Do not delete real SVG assets.

Completion criteria:

- Tracked backup/temp image files are removed.

Stop condition:

- If any file is missing because the user already removed it, record and
  continue.

### Action 9.1.3 - Add Narrow Ignore Rules

Target files:

```text
.gitignore
```

Procedure:

- Add narrow ignore patterns if not already present:

```gitignore
assets/images/.$*.svg.bkp
assets/images/.$*.svg.dtmp
```

- Verify `__pycache__` and `*.py[cod]` are ignored.
- Do not add broad image ignore patterns.

Completion criteria:

- The backup/temp artifact pattern will not be retracked.

## Stage 9.2 - Check Generated Python Bytecode

### Action 9.2.1 - Confirm Bytecode Is Not Tracked

Target files:

```text
src
tests
smoke
```

Command:

```bash
git ls-files | rg '(__pycache__|\\.pyc$)'
```

Procedure:

- Check whether bytecode is tracked.
- If no tracked bytecode exists, do not edit.
- If tracked bytecode exists, remove tracked bytecode and update `.gitignore`.

Completion criteria:

- Tracked generated bytecode is absent.

Stop condition:

- If bytecode removal is unexpectedly broad, stop and ask.

---

# Phase 10 - Full Verification

## Stage 10.1 - Run Targeted Test Matrix

### Action 10.1.1 - Run Targeted Tests

Target files:

```text
none
```

Commands:

```bash
uv run pytest tests/test_api.py
uv run pytest tests/test_artifacts.py
uv run pytest tests/test_clean_tower.py
uv run pytest tests/test_witness_consistency.py
uv run pytest tests/test_skeleton.py
uv run pytest tests/test_fiber_lift.py
uv run pytest tests/test_release_metadata.py
uv run pytest tests/test_readme_quickstart.py
uv run pytest tests/integration/test_state_collapser_static_tower.py
uv run pytest tests/integration/test_clean_state_collapser_tower.py
```

Procedure:

- Run targeted tests one group at a time.
- Record results in the implementation log.

Completion criteria:

- All targeted tests pass.

Stop condition:

- If any targeted test fails, fix or stop before running full verification.

## Stage 10.2 - Run Full Test Suite

### Action 10.2.1 - Run Full Pytest

Target files:

```text
none
```

Command:

```bash
uv run pytest
```

Procedure:

- Run full test suite.
- Record pass/fail count and runtime.

Completion criteria:

- Full test suite passes.

Stop condition:

- If full tests fail, do not claim completion.

## Stage 10.3 - Run Smoke Suite

### Action 10.3.1 - Run All Smoke Scripts

Target files:

```text
none
```

Commands:

```bash
uv run python smoke/smoke_001.py
uv run python smoke/smoke_002.py
uv run python smoke/smoke_003.py
uv run python smoke/smoke_004.py
uv run python smoke/smoke_005.py
uv run python smoke/smoke_006.py
uv run python smoke/smoke_007.py
uv run python smoke/smoke_008.py
uv run python smoke/smoke_009.py
uv run python smoke/smoke_010.py
uv run python smoke/smoke_011.py
uv run python smoke/smoke_012.py
uv run python smoke/smoke_013.py
uv run python smoke/smoke_014.py
uv run python smoke/smoke_015.py
uv run python smoke/smoke_016.py
```

Procedure:

- Run every smoke script after implementation.
- Compare failures or output changes against baseline.
- Update smoke `.md` explanations only if counts changed for a justified reason.

Completion criteria:

- Smoke scripts pass or all intentional changes are documented.

Stop condition:

- If smoke counts change unexpectedly, stop and explain before updating docs.

## Stage 10.4 - Run Build Verification

### Action 10.4.1 - Build Distribution

Target files:

```text
none
```

Command:

```bash
uv build --out-dir /private/tmp/jet-simplex-search-revision-build
```

Procedure:

- Build sdist and wheel to a temporary directory.
- Record result in implementation log.

Completion criteria:

- Package builds locally.

Stop condition:

- If `uv build` is unavailable due to missing dependency or network, record the
  blocker and ask whether to add build tooling.

## Stage 10.5 - Optional Ruff Verification

### Action 10.5.1 - Run Ruff If Added

Target files:

```text
none
```

Commands:

```bash
uv run ruff check .
uv run ruff format --check .
```

Procedure:

- Run Ruff only if it was added to dev dependencies and synced.
- Record results.
- Do not mass-format unrelated files unless the workplan is expanded or PO
  approves.

Completion criteria:

- Ruff status is known.

Stop condition:

- If Ruff reports broad pre-existing issues, stop and ask whether to scope a
  formatting/lint pass.

---

# Phase 11 - Implementation Log Closeout And Final Review

## Stage 11.1 - Update Implementation Log

### Action 11.1.1 - Record Completed Changes

Target files:

```text
docs/design/synthetic_blow_code_revisions/01_004_synthetic_blow_code_revision_implementation_log.md
```

Procedure:

- Record every phase completed.
- Record files changed.
- Record tests and smoke commands run.
- Record any deviations from this workplan.
- Record any stop conditions encountered and how they were resolved.

Completion criteria:

- Implementation log is complete and traceable.

Stop condition:

- If implementation deviated from the workplan without approval, stop and
  resynchronize with the PO before final response.

## Stage 11.2 - Inspect Final Diff

### Action 11.2.1 - Review Git Diff

Target files:

```text
all changed files
```

Commands:

```bash
git status --short
git diff --stat
git diff
```

Procedure:

- Review changed files.
- Confirm no unrelated user changes were reverted.
- Confirm no accidental generated files are staged or left in tracked diff.
- Confirm no public docs link internal Prime Directive or release-prep docs.
- Confirm Abdul Malik attribution remains.

Completion criteria:

- Final diff matches approved workplan.

Stop condition:

- If unrelated changes are mixed in, isolate or ask before final response.

## Stage 11.3 - Final Response Preparation

### Action 11.3.1 - Prepare Completion Report

Target files:

```text
none
```

Procedure:

- Summarize:
  - what changed;
  - tests run;
  - any tests not run;
  - any remaining follow-ups;
  - any blocked release actions.
- Keep response concise.
- Do not claim public release, PyPI publish, tagging, or GitHub visibility
  changes.

Completion criteria:

- Final response accurately reflects repository state.

Stop condition:

- If verification failed, final response must say so directly.

---

# Phase 12 - Deferred Follow-Up Ledger

## Stage 12.1 - Record Deferred State-Collapser Primitive

### Action 12.1.1 - Add Follow-Up Note If Needed

Target files:

```text
docs/design/synthetic_blow_code_revisions/01_004_synthetic_blow_code_revision_implementation_log.md
```

Procedure:

- Record that JSS owns the clean tower bridge for this revision.
- Record that a future `state_collapser` clean quotient tower primitive may
  replace the bridge.
- Do not create a new state-collapser workplan unless the PO asks.

Completion criteria:

- Deferred upstream ownership is documented.

## Stage 12.2 - Record Non-Goals

### Action 12.2.1 - Document Non-Implemented Features

Target files:

```text
docs/design/synthetic_blow_code_revisions/01_004_synthetic_blow_code_revision_implementation_log.md
README.md
```

Procedure:

- Ensure non-goals remain explicit:
  - Kan replacement;
  - horn filling;
  - cofibrant replacement variants beyond current small-object search;
  - expanded H witness enumeration artifacts;
  - GPU/tensor/CSR acceleration;
  - PyPI release;
  - GitHub public visibility change.

Completion criteria:

- Public and internal docs do not overclaim.

---

# Workplan Completion Criteria

The implementation is complete only when:

- `search_simplices` is graph/H-only and returns `SearchWithHLiftsResult`.
- `search_skeleton_simplices` is the lower-level skeleton/tower API and returns
  `SimplexSearchResult`.
- Artifacts accept explicit result classes, not duck-typed objects.
- Public H workflow uses the clean tower bridge.
- Clean quotient tiers are realized before later quotient steps.
- Strict label policy is documented and tested.
- Witness and projection consistency tests pass.
- Missing-downstairs-interior behavior remains tested.
- Dead helpers and stale caches are removed or justified.
- Release-facing dependency and README drift are fixed.
- Tracked backup/temp image files are removed.
- Full tests pass.
- Smoke scripts pass or intentional count changes are documented.
- Implementation log is complete.

## Final Verification Command Set

Minimum final command set:

```bash
uv run pytest
uv run python smoke/smoke_001.py
uv run python smoke/smoke_002.py
uv run python smoke/smoke_003.py
uv run python smoke/smoke_004.py
uv run python smoke/smoke_005.py
uv run python smoke/smoke_006.py
uv run python smoke/smoke_007.py
uv run python smoke/smoke_008.py
uv run python smoke/smoke_009.py
uv run python smoke/smoke_010.py
uv run python smoke/smoke_011.py
uv run python smoke/smoke_012.py
uv run python smoke/smoke_013.py
uv run python smoke/smoke_014.py
uv run python smoke/smoke_015.py
uv run python smoke/smoke_016.py
```

Additional release-facing command set when tooling is available:

```bash
uv build --out-dir /private/tmp/jet-simplex-search-revision-build
uv run ruff check .
uv run ruff format --check .
```
