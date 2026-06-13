# H-To-G Skeletonization And H-Lift Implementation Workplan

## Status

Implementation workplan derived from:

```text
docs/design/h_to_g_skeleton_refactor/01_001_h_to_g_skeleton_realization_refactor.md
docs/design/h_to_g_skeleton_refactor/01_002_h_to_g_skeleton_realization_package_blueprint.md
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

The Project Owner introduced and clarified the H-to-G refactor:

```text
H:
  arbitrary input graph, possibly with loops and parallel edges

G:
  simple-reflexive search skeleton

H-lift:
  compressed count / optional expansion of distinct original H simplices over
  tier-0 G simplices
```

The Project Owner also corrected the tower requirement:

```text
At every tier, before constructing the next tier, excise multiple edges and
make sure each node has exactly one loop.
```

This means the simple-reflexive invariant belongs in `state_collapser` tower
construction for JSS mode, not merely in a late JSS adapter readout.

## Prime Directive Execution Rules

1. Do not implement this workplan until the Project Owner explicitly approves
   an implementation scope.
2. Once approved, execute the approved phases and actions in order unless a
   listed stop condition triggers.
3. Do not silently reorder, simplify, skip, or substitute actions.
4. Do not invent Project Owner decisions. If the workplan reveals a real
   semantic choice not settled in the source docs, stop and ask.
5. Verify claims against the actual repo and the adjacent `state_collapser`
   source before editing.
6. If source reality differs from this workplan, stop and resynchronize from
   the source files and tests.
7. Preserve Abdul Malik attribution in design, README, artifact documentation,
   and public-facing algorithm descriptions.
8. Keep Kan replacement, horn filling, and cofibrant-replacement variants out
   of this implementation unless separately approved.
9. Keep zero-count skeleton simplices in the public result by default.
10. Compute H-lifts only for `G^0` in first scope.
11. Treat formal identities as skeleton-search devices. Actual degenerate
    H-lifts require actual loops in `H`.
12. Treat parallel H edges as distinct lifted H-simplices, represented by
    compressed counts by default.

## Implementation Scope

First implementation target:

```text
Refactor jet_simplex_search so arbitrary input H is skeletonized to a simple G,
the static small-object tower search runs over G and simple-reflexive tower
tiers, and tier-0 skeleton simplices receive compressed H-lift records.
```

First-scope deliverables:

```text
src/jet_simplex_search/skeleton.py
src/jet_simplex_search/h_lift.py
ids for skeleton edges and H-lift records
simple-reflexive normalized graph assertions
combined public result model
public graph-H API orchestration
lower-level skeleton/tower API preservation
state_collapser simple-reflexive tier mode plan/patch
indexed adapter edge-fiber lookups
artifact schema version 2
tests for skeletonization, H-lifts, adapter invariants, and artifacts
updated smoke/docs language
```

First-scope non-goals:

- no Kan replacement;
- no horn filling;
- no dynamic tower runtime;
- no custom quotient tower inside `jet_simplex_search`;
- no graph database;
- no tensor/GPU/vectorized implementation;
- no unbounded expansion of H witness assignments;
- no silent label merging;
- no H-lift counts for quotient tiers below `G^0`.

## Current Baseline

Observed package shape at planning time:

```text
src/jet_simplex_search/
  api.py
  artifacts.py
  diagnostics.py
  errors.py
  frontier.py
  graph.py
  ids.py
  lift.py
  normalize.py
  records.py
  search.py
  tower_adapter.py
```

Observed key implementation facts:

```text
normalize_graph currently strips input loops and adds formal identities.
normalize_graph currently preserves non-loop parallel edges.
SimplexRecord is the skeleton/tower simplex record.
extend_simplex_direct records all edge ids in graph.edge_lookup for each face.
lift.py performs small-object lifting over existing downstairs simplex records.
tower_adapter.py currently scans tier edges in edge_fiber_targets.
StateCollapserStaticTowerAdapter currently builds a state_collapser tower from
the graph it is handed.
```

Observed `state_collapser` facts:

```text
PartitionTower.initialize builds tier 0, carries layers forward, contracts
schema edges, rebuilds dirty action cells, and appends tiers.

ActionPartitionLayer.rebuild_action_cells_for_collection currently groups by:
  (source_cell, target_cell, primitive_action_identity)

LoopPolicy records internal edges but does not itself define exactly one formal
loop per state cell for JSS graph semantics.
```

Baseline command:

```text
uv run pytest
```

Expected baseline from recent work:

```text
58 tests pass
```

## Phase 0 - Execution Preparation

### Stage 0.1 - Confirm Approval And Scope

**Action 0.1.1 - Confirm implementation approval**

Target files:

```text
none
```

Procedure:

- Confirm the Project Owner has approved implementation, not only planning.
- Confirm whether the approved scope includes the adjacent `state_collapser`
  repo or only `jet_simplex_search`.
- Confirm whether artifact schema version 2 is in the same implementation pass
  or deferred.
- Confirm whether README/smoke updates are in the same implementation pass or
  deferred.

Completion:

- Approved phase range is known.
- Approved repository set is known.
- No source files are edited before approval.

Stop conditions:

- If the Project Owner asks only for a workplan, stop after creating/updating
  this document.
- If the Project Owner approves only JSS-local work, do not edit
  `../state_collapser`.
- If the requested order differs from this workplan, revise this workplan before
  coding.

**Action 0.1.2 - Create an implementation log**

Target files:

```text
docs/design/h_to_g_skeleton_refactor/01_004_h_to_g_skeleton_realization_implementation_log.md
```

Procedure:

- Create the implementation log before source edits.
- Record approved phases.
- Record current git branch.
- Record current `git status --short`.
- Record baseline test command and result.
- Record whether `state_collapser` edits are approved.

Completion:

- Implementation log exists and contains initial state.

Stop conditions:

- If the log path exists with unrelated content, inspect it and append rather
  than overwriting.

### Stage 0.2 - Baseline Reality Check

**Action 0.2.1 - Inspect repository status**

Target files:

```text
none
```

Command:

```text
git status --short
```

Procedure:

- Identify modified, staged, and untracked files.
- Distinguish current implementation changes from prior Project Owner or
  generated changes.
- Do not revert unrelated changes.
- Record status in the implementation log.

Completion:

- Worktree state is known.

Stop conditions:

- If files required by this implementation have unexpected modifications, read
  them before editing.
- If untracked files overlap intended new paths, inspect before writing.

**Action 0.2.2 - Run baseline tests**

Target files:

```text
none
```

Command:

```text
uv run pytest
```

Procedure:

- Run the current JSS test suite.
- Record pass/fail and test count in the implementation log.
- If tests fail before edits, treat failure as baseline reality.

Completion:

- Baseline test result is known.

Stop conditions:

- If baseline fails, stop implementation and diagnose before changing source.

**Action 0.2.3 - Inspect state_collapser baseline if approved**

Target files:

```text
../state_collapser/pyproject.toml
../state_collapser/src/state_collapser/tower/partition/tower.py
../state_collapser/src/state_collapser/tower/partition/action_layer.py
../state_collapser/src/state_collapser/tower/partition/loop_policy.py
```

Procedure:

- Confirm the adjacent repo path exists.
- Confirm package test command from that repo's metadata or established
  workflow.
- Run or record the approved baseline test command if within scope.
- Record baseline status in the JSS implementation log.

Completion:

- Upstream source and test baseline are known when upstream edits are approved.

Stop conditions:

- If upstream edits are not approved, do not modify `../state_collapser`.
- If upstream tests fail at baseline, stop and report the baseline failure.

### Stage 0.3 - Freeze Source Semantics

**Action 0.3.1 - Re-read source design docs**

Target files:

```text
docs/design/h_to_g_skeleton_refactor/01_001_h_to_g_skeleton_realization_refactor.md
docs/design/h_to_g_skeleton_refactor/01_002_h_to_g_skeleton_realization_package_blueprint.md
```

Procedure:

- Re-read the source docs before implementation.
- Extract non-negotiable semantics into the implementation log.
- Confirm the implementation still matches:
  - H-to-G skeletonization;
  - simple-reflexive tower tiers;
  - H-lifts only for `G^0`;
  - actual H loops required for degenerate lifts;
  - zero-count skeleton simplices retained;
  - parallel edges counted as distinct H-lifts.

Completion:

- Source semantics are revalidated from disk.

Stop conditions:

- If the source docs conflict with this workplan, update the workplan first.

## Phase 1 - JSS Skeletonization Core

### Stage 1.1 - Add Deterministic IDs

**Action 1.1.1 - Add skeleton edge id helper**

Target files:

```text
src/jet_simplex_search/ids.py
tests/test_ids.py
```

Procedure:

- Add `skeleton_edge_id(source: str, target: str) -> str`.
- Use existing escaping behavior.
- Ensure ids are deterministic and independent of input edge insertion order.
- Reject no values only if existing helper style does so; otherwise keep helper
  simple and let graph validation enforce nonempty ids.
- Add tests for ordinary vertex ids and ids requiring escaping.

Completion:

- Tests prove `skeleton_edge_id("a", "b")` is stable.
- Tests prove escaping round trips are safe enough for id uniqueness.

Stop conditions:

- If changing `_escape` would alter existing public ids, stop and choose a new
  helper that preserves existing ids.

**Action 1.1.2 - Add tier simple edge id helper**

Target files:

```text
src/jet_simplex_search/ids.py
tests/test_ids.py
```

Procedure:

- Add `tier_simple_edge_id(tier: int, source: str, target: str) -> str`.
- Use existing escaping behavior.
- Include the tier in the id.
- Add tests proving different tiers produce different ids and same tier/pair
  produces the same id.

Completion:

- Tier edge ids are deterministic and tested.

Stop conditions:

- If the adapter later consumes upstream state_collapser ids directly, keep this
  helper only if it is still used.

**Action 1.1.3 - Add H-lift id helper**

Target files:

```text
src/jet_simplex_search/ids.py
tests/test_ids.py
```

Procedure:

- Add `h_lift_id(simplex_id: str) -> str`.
- Escape the simplex id.
- Add tests for deterministic output.

Completion:

- H-lift records can be keyed without inventing ad hoc ids in `h_lift.py`.

Stop conditions:

- If the chosen result model stores H-lift records by simplex id only, do not
  add an unused helper.

### Stage 1.2 - Add skeleton.py Records

**Action 1.2.1 - Create skeleton module**

Target files:

```text
src/jet_simplex_search/skeleton.py
tests/test_skeleton.py
```

Procedure:

- Add `skeleton.py`.
- Add empty initial tests that import the module.
- Keep the module flat; do not create a subpackage.

Completion:

- `uv run pytest tests/test_skeleton.py` imports the new module.

Stop conditions:

- If import cycles appear, inspect module imports and reduce dependencies.

**Action 1.2.2 - Add SkeletonEdgeFiber**

Target files:

```text
src/jet_simplex_search/skeleton.py
tests/test_skeleton.py
```

Procedure:

- Add frozen slots dataclass `SkeletonEdgeFiber`.
- Fields:
  - `source: str`
  - `target: str`
  - `skeleton_edge_id: str`
  - `original_edge_ids: tuple[str, ...]`
  - `labels: tuple[object, ...]`
- Normalize tuple fields in `__post_init__`.
- Raise `SimplexInvariantError` or `InvalidGraphError` if:
  - `source == target`;
  - `original_edge_ids` is empty.
- Add tests for tuple coercion and loop rejection.

Completion:

- Non-loop edge fibers are explicit and validated.

Stop conditions:

- If the project error pattern prefers only graph validation for records, align
  with existing `records.py` style.

**Action 1.2.3 - Add SkeletonLoopFiber**

Target files:

```text
src/jet_simplex_search/skeleton.py
tests/test_skeleton.py
```

Procedure:

- Add frozen slots dataclass `SkeletonLoopFiber`.
- Fields:
  - `vertex_id: str`
  - `original_loop_edge_ids: tuple[str, ...]`
- Normalize tuple fields.
- Allow `original_loop_edge_ids` to be empty.
- Add tests proving empty loop fibers are valid.

Completion:

- Every vertex can have a loop fiber, including zero-loop vertices.

Stop conditions:

- If later code treats missing loop fiber and empty loop fiber differently, stop
  and normalize to one representation.

**Action 1.2.4 - Add SkeletonizationDiagnostics**

Target files:

```text
src/jet_simplex_search/skeleton.py
tests/test_skeleton.py
```

Procedure:

- Add frozen slots dataclass `SkeletonizationDiagnostics`.
- Include counts:
  - `input_vertex_count`
  - `input_edge_count`
  - `input_loop_edge_count`
  - `input_non_loop_edge_count`
  - `skeleton_non_loop_edge_count`
  - `collapsed_parallel_non_loop_edge_count`
  - `collapsed_loop_edge_count`
  - `vertices_with_original_loops`
  - `maximum_non_loop_fiber_size`
  - `maximum_loop_fiber_size`
  - `label_conflict_count`
- Add `to_dict()` if artifact code needs direct serialization.
- Add tests for count fields in simple cases.

Completion:

- Skeletonization can report useful preprocessing facts.

Stop conditions:

- If diagnostics duplicate another diagnostics module convention, move only
  serialization helper, not the record.

**Action 1.2.5 - Add SkeletonizationResult**

Target files:

```text
src/jet_simplex_search/skeleton.py
tests/test_skeleton.py
```

Procedure:

- Add frozen slots dataclass `SkeletonizationResult`.
- Fields:
  - `original_graph: GraphInput`
  - `skeleton_graph: GraphInput`
  - `edge_fibers_by_pair: Mapping[tuple[str, str], SkeletonEdgeFiber]`
  - `edge_fibers_by_skeleton_edge_id: Mapping[str, SkeletonEdgeFiber]`
  - `loop_fibers_by_vertex: Mapping[str, SkeletonLoopFiber]`
  - `skeleton_edge_id_by_pair: Mapping[tuple[str, str], str]`
  - `skeleton_edge_id_by_original_edge_id: Mapping[str, str]`
  - `original_loop_vertex_by_edge_id: Mapping[str, str]`
  - `diagnostics: SkeletonizationDiagnostics`
- Freeze mutable mapping inputs by copying to plain dicts or mapping proxies
  consistent with local style.
- Add tests for result construction from a minimal hand-built result.

Completion:

- Skeletonization output shape exists before algorithm implementation.

Stop conditions:

- If mapping immutability becomes noisy, follow existing `SimplexSearchResult`
  pattern and freeze tuple fields only.

### Stage 1.3 - Implement skeletonize_graph

**Action 1.3.1 - Add label policy**

Target files:

```text
src/jet_simplex_search/skeleton.py
tests/test_skeleton.py
```

Procedure:

- Add `SkeletonLabelPolicy`.
- First-scope value:
  - `REQUIRE_IDENTICAL = "require_identical"`
- Keep policy minimal.
- Add tests that import and compare the enum/string value.

Completion:

- Label behavior is explicit.

Stop conditions:

- Do not add callback or union policies unless the Project Owner approves them.

**Action 1.3.2 - Group H edges by role**

Target files:

```text
src/jet_simplex_search/skeleton.py
tests/test_skeleton.py
```

Procedure:

- Implement initial `skeletonize_graph(graph, *, label_policy=...)`.
- Call `validate_graph_input(graph)` first.
- Sort vertices deterministically by id for skeleton output.
- Sort input edges deterministically by id.
- Split edges:
  - loops where `edge.source == edge.target`;
  - non-loops where `edge.source != edge.target`.
- Group loops by vertex id.
- Group non-loops by `(source, target)`.
- Add tests for grouping behavior through the public result.

Completion:

- Function can distinguish loop fibers and non-loop edge fibers.

Stop conditions:

- If payload preservation is unclear, preserve existing vertex payloads exactly.

**Action 1.3.3 - Build skeleton non-loop edges**

Target files:

```text
src/jet_simplex_search/skeleton.py
tests/test_skeleton.py
```

Procedure:

- For each non-loop endpoint pair, create one `InputEdge`.
- Use `skeleton_edge_id(source, target)`.
- Set source and target to the endpoint pair.
- Set labels according to `SkeletonLabelPolicy.REQUIRE_IDENTICAL`.
- Preserve no original edge payload in first scope unless a clear deterministic
  payload rule already exists.
- Add tests:
  - single edge produces one skeleton edge;
  - three parallel edges produce one skeleton edge.

Completion:

- `skeleton_graph.edges` is loop-free and has one edge per ordered pair.

Stop conditions:

- If skeleton edge id collides with an input edge id, that is acceptable only if
  skeleton graph is separate from H. If collision causes downstream ambiguity,
  change id prefix.

**Action 1.3.4 - Enforce label conflict behavior**

Target files:

```text
src/jet_simplex_search/skeleton.py
tests/test_skeleton.py
```

Procedure:

- For each non-loop edge group, collect label tuples.
- If all label tuples are identical, use that tuple on the skeleton edge.
- If label tuples differ, raise `InvalidGraphError`.
- Count label conflicts in diagnostics only for successful paths if useful; for
  failing paths, test the exception message.
- Add tests:
  - identical labels pass;
  - different labels fail.

Completion:

- No silent label merge exists.

Stop conditions:

- If current tests rely on parallel edges with different labels passing, update
  tests only after confirming this intended semantic change.

**Action 1.3.5 - Build loop fibers for every vertex**

Target files:

```text
src/jet_simplex_search/skeleton.py
tests/test_skeleton.py
```

Procedure:

- Create one `SkeletonLoopFiber` for every vertex.
- Store original loop edge ids sorted by id.
- Store empty tuple for vertices without loops.
- Populate `original_loop_vertex_by_edge_id`.
- Add tests:
  - no-loop vertex has empty loop fiber;
  - loop-only graph has no skeleton edges and nonempty loop fiber;
  - parallel loops are all retained.

Completion:

- H loop information is never lost.

Stop conditions:

- If a loop references missing vertex, that should already fail in graph
  validation.

**Action 1.3.6 - Build non-loop edge fibers and maps**

Target files:

```text
src/jet_simplex_search/skeleton.py
tests/test_skeleton.py
```

Procedure:

- For each non-loop endpoint group, create a `SkeletonEdgeFiber`.
- Populate:
  - `edge_fibers_by_pair`
  - `edge_fibers_by_skeleton_edge_id`
  - `skeleton_edge_id_by_pair`
  - `skeleton_edge_id_by_original_edge_id`
- Store original edge ids sorted by id.
- Add tests for each map.

Completion:

- Every original non-loop edge maps to exactly one skeleton edge.

Stop conditions:

- If two endpoint pairs produce the same skeleton edge id, stop and fix id
  escaping.

**Action 1.3.7 - Add skeletonization invariant assertion**

Target files:

```text
src/jet_simplex_search/skeleton.py
tests/test_skeleton.py
```

Procedure:

- Add `assert_skeletonization_invariants(result)`.
- Assert:
  - skeleton vertices match original vertices by id;
  - skeleton has no loops;
  - at most one skeleton edge exists per non-loop endpoint pair;
  - every skeleton edge has a nonempty edge fiber;
  - every original non-loop edge appears in exactly one edge map;
  - every original loop edge appears in loop map;
  - every vertex has a loop fiber.
- Call this assertion before returning from `skeletonize_graph`.
- Add a test that corrupts a hand-built result and sees an invariant error.

Completion:

- Skeletonization cannot silently return inconsistent data.

Stop conditions:

- If hand-built result corruption tests are too brittle, keep tests focused on
  public `skeletonize_graph` outputs.

### Stage 1.4 - Export Skeletonization API

**Action 1.4.1 - Update package exports if needed**

Target files:

```text
src/jet_simplex_search/__init__.py
tests/test_package.py
```

Procedure:

- Decide whether skeletonization records/functions should be top-level imports.
- If yes, export:
  - `skeletonize_graph`
  - `SkeletonizationResult`
  - `SkeletonEdgeFiber`
  - `SkeletonLoopFiber`
- If no, leave module import path explicit.
- Update package tests accordingly.

Completion:

- Public or internal status of skeletonization is clear.

Stop conditions:

- If public API stability is uncertain, keep exports minimal and document the
  module path.

## Phase 2 - Simple-Reflexive Normalization Assertions

### Stage 2.1 - Add Assertion Helper

**Action 2.1.1 - Implement simple-reflexive normalized graph assertion**

Target files:

```text
src/jet_simplex_search/normalize.py
tests/test_normalize.py
```

Procedure:

- Add `assert_simple_reflexive_normalized_graph(graph: NormalizedGraph)`.
- Assert:
  - every vertex has exactly one identity edge;
  - every identity edge is a loop;
  - no original edge is a loop;
  - every edge lookup value is nonempty;
  - every edge lookup value has length exactly one;
  - adjacency contains self for every vertex;
  - adjacency agrees with edge lookup.
- Reuse `SimplexInvariantError`.

Completion:

- Code can explicitly check that direct search sees simple-reflexive graph
  semantics.

Stop conditions:

- Do not change `normalize_graph` to collapse non-loop parallels. That belongs
  to `skeletonize_graph`.

**Action 2.1.2 - Add normalize-after-skeleton test**

Target files:

```text
tests/test_normalize.py
```

Procedure:

- Build H with:
  - three parallel `a -> b` edges;
  - two loops at `a`;
  - one vertex `b`.
- Call `skeletonize_graph(H)`.
- Call `normalize_graph(skeleton.skeleton_graph)`.
- Assert:
  - one formal identity at `a`;
  - one formal identity at `b`;
  - one non-loop skeleton edge `a -> b`;
  - each `edge_lookup` entry has length one.

Completion:

- Tests cover the intended `H -> G -> normalized G` path.

Stop conditions:

- If test setup duplicates many helpers, create small local factory functions in
  the test file.

### Stage 2.2 - Guard Search Inputs

**Action 2.2.1 - Assert bottom-tier normalized graph simplicity**

Target files:

```text
src/jet_simplex_search/search.py
tests/test_directed_flag_semantics.py
tests/test_bottom_tier_enumeration.py
```

Procedure:

- Call `assert_simple_reflexive_normalized_graph` inside
  `enumerate_direct_simplices` or just before enumeration in the tower path.
- Choose the least disruptive location:
  - if direct tests intentionally use non-simple normalized graphs, assert only
    in the new public H pipeline;
  - otherwise assert in `enumerate_direct_simplices`.
- Update tests to pass skeleton-normalized graphs.

Completion:

- Direct search no longer quietly accepts multiplicity-bearing normalized graph
  inputs in the refactored path.

Stop conditions:

- If existing tests intentionally verify multiple edge witnesses, stop and
  split old behavior into explicit legacy/internal tests or rewrite tests to
  H-lift semantics.

**Action 2.2.2 - Clarify SimplexRecord witness docstrings**

Target files:

```text
src/jet_simplex_search/records.py
src/jet_simplex_search/search.py
tests/test_records.py
```

Procedure:

- Update `FaceEdgeWitness` docstring to specify skeleton/tower face evidence.
- Update `SimplexRecord` docstring to specify skeleton/tower simplex address.
- Do not change record fields unless tests require it.

Completion:

- Code comments no longer imply H witness semantics.

Stop conditions:

- If docstring-only change triggers lint/doc tests, adjust wording only.

## Phase 3 - H-Lift Computation

### Stage 3.1 - Add H-Lift Records

**Action 3.1.1 - Create h_lift module**

Target files:

```text
src/jet_simplex_search/h_lift.py
tests/test_h_lift.py
```

Procedure:

- Add `h_lift.py`.
- Add import smoke test.
- Keep module independent of `state_collapser`.

Completion:

- H-lift module exists and imports cleanly.

Stop conditions:

- If name conflicts with existing project convention, use `h_lifts.py` only
  after updating this workplan.

**Action 3.1.2 - Add HFaceLiftFactor**

Target files:

```text
src/jet_simplex_search/h_lift.py
tests/test_h_lift.py
```

Procedure:

- Add frozen slots dataclass `HFaceLiftFactor`.
- Fields:
  - `source_index`
  - `target_index`
  - `source_vertex_id`
  - `target_vertex_id`
  - `skeleton_edge_id`
  - `original_edge_ids`
  - `factor`
  - `is_loop_factor`
- Normalize `original_edge_ids` to tuple.
- Validate:
  - `source_index < target_index`;
  - `factor == len(original_edge_ids)`;
  - `is_loop_factor` agrees with equal source/target ids.
- Add unit tests.

Completion:

- Per-face H-lift factors are explicit and self-checking.

Stop conditions:

- If `factor == len(original_edge_ids)` prevents future capped artifacts, keep
  count and member-list semantics separate in a later approved change.

**Action 3.1.3 - Add SimplexHLiftRecord**

Target files:

```text
src/jet_simplex_search/h_lift.py
tests/test_h_lift.py
```

Procedure:

- Add frozen slots dataclass `SimplexHLiftRecord`.
- Fields:
  - `id`
  - `simplex_id`
  - `tier`
  - `degree`
  - `skeleton_vertices`
  - `input_vertices`
  - `face_factors`
  - `h_lift_count`
  - `has_h_lift`
- Validate:
  - degree equals `len(input_vertices) - 1`;
  - skeleton and input vertex tuple lengths match;
  - `has_h_lift == (h_lift_count > 0)`;
  - product of face factor counts equals `h_lift_count`;
  - degree 0 has no face factors and count 1.
- Add tests for degree 0, positive count, and zero count.

Completion:

- Compressed H-lift record exists and preserves zero-count addresses.

Stop conditions:

- If product validation is expensive only for huge dimensions, keep it; `k` is
  first-scope small and correctness matters more.

**Action 3.1.4 - Add HLiftDiagnostics**

Target files:

```text
src/jet_simplex_search/h_lift.py
tests/test_h_lift.py
```

Procedure:

- Add frozen slots dataclass `HLiftDiagnostics`.
- Include:
  - `simplex_count_by_degree`
  - `positive_simplex_count_by_degree`
  - `zero_lift_simplex_count_by_degree`
  - `total_h_lift_count_by_degree`
  - `max_h_lift_count_by_degree`
  - `max_face_factor_by_degree`
- Add `to_dict()` if artifact code needs it.
- Add `build_h_lift_diagnostics(records)`.

Completion:

- Public summaries can separate skeleton address counts from total H-lift
  counts.

Stop conditions:

- If diagnostics are moved to `diagnostics.py`, keep construction logic close
  to H-lift records or explicitly import it.

### Stage 3.2 - Implement H-Lift Algorithm

**Action 3.2.1 - Filter tier-0 skeleton simplices**

Target files:

```text
src/jet_simplex_search/h_lift.py
tests/test_h_lift.py
```

Procedure:

- Implement helper to collect `SimplexRecord` objects at tier 0 from
  `SimplexSearchResult.simplices_by_tier_degree`.
- Preserve degree ordering.
- Preserve simplex id ordering.
- Ignore nonzero tiers for H-lift computation.
- Add tests with a fake `SimplexSearchResult` containing tier 0 and tier 1.

Completion:

- H-lift computation only touches `G^0`.

Stop conditions:

- If the adapter uses a different tier label for `G^0`, stop; first-scope docs
  require H maps to `G^0`.

**Action 3.2.2 - Map tier-0 vertices to input vertices**

Target files:

```text
src/jet_simplex_search/h_lift.py
tests/test_h_lift.py
```

Procedure:

- Accept `tier0_vertex_id_to_input_vertex_id`.
- For each skeleton simplex vertex, look up the input vertex id.
- Raise `SimplexInvariantError` if a vertex is missing.
- Add tests:
  - direct identity map;
  - tower cell id map;
  - missing map entry fails.

Completion:

- H-lift computation can work with both fake tests and real adapter tier-0 ids.

Stop conditions:

- If tier-0 vertex map depends on adapter internals, keep the dependency at the
  API/tower_adapter boundary, not in `h_lift.py`.

**Action 3.2.3 - Compute degree-0 H-lifts**

Target files:

```text
src/jet_simplex_search/h_lift.py
tests/test_h_lift.py
```

Procedure:

- For each tier-0 degree-0 simplex, emit one `SimplexHLiftRecord`.
- Use count 1.
- Use no face factors.
- Add tests for one and multiple vertices.

Completion:

- Vertex simplices lift with count 1.

Stop conditions:

- If Project Owner later introduces vertex multiplicity in H-to-G, revise this
  action before implementation.

**Action 3.2.4 - Compute non-loop face factors**

Target files:

```text
src/jet_simplex_search/h_lift.py
tests/test_h_lift.py
```

Procedure:

- For each face occurrence `(i, j)` with distinct input vertices:
  - look up `SkeletonEdgeFiber` by `(source, target)`;
  - copy original edge ids;
  - factor is `len(original_edge_ids)`;
  - `is_loop_factor` is false.
- Raise `SimplexInvariantError` if the non-loop fiber is missing or empty.
- Add tests:
  - 1-simplex with three parallel H edges has count 3;
  - missing non-loop fiber fails.

Completion:

- Parallel non-loop edges produce multiplicity factors.

Stop conditions:

- If a skeleton simplex contains a non-loop face not present in skeletonization,
  treat this as an invariant violation, not a zero factor.

**Action 3.2.5 - Compute loop face factors**

Target files:

```text
src/jet_simplex_search/h_lift.py
tests/test_h_lift.py
```

Procedure:

- For each face occurrence `(i, j)` with equal input vertices:
  - look up `SkeletonLoopFiber` by vertex;
  - copy original loop edge ids;
  - factor is `len(original_loop_edge_ids)`;
  - `is_loop_factor` is true;
  - skeleton edge id is `identity_edge_id(vertex)`.
- Allow factor zero.
- Add tests:
  - `(s,s)` with no H loops has count 0 and record remains present;
  - `(s,s)` with L loops has count L.

Completion:

- Degenerate H-lifts require actual H loops.

Stop conditions:

- Do not treat formal identities as one H-lift when H has no loop.

**Action 3.2.6 - Compute higher-degree product counts**

Target files:

```text
src/jet_simplex_search/h_lift.py
tests/test_h_lift.py
```

Procedure:

- Iterate all directed face occurrences:
  - for `target_index` from 1 through degree;
  - for `source_index` from 0 to `target_index - 1`.
- Multiply all face factors using Python `int`.
- Add tests:
  - triangle product `|H(a,b)| * |H(a,c)| * |H(b,c)|`;
  - `(s,s,t)` product `|Loop_H(s)| * |H(s,t)|^2`;
  - `(s,t,t)` product `|H(s,t)|^2 * |Loop_H(t)|`;
  - `(s,s,s)` product `|Loop_H(s)|^3`.

Completion:

- Low-dimensional degeneracy and multiplicity behavior is proven.

Stop conditions:

- If Project Owner rejects independent repeated face witnesses, stop and revise
  semantics. Current blueprint says repeated face occurrences are independent.

**Action 3.2.7 - Build compute_h_lifts_for_tier_zero**

Target files:

```text
src/jet_simplex_search/h_lift.py
tests/test_h_lift.py
```

Procedure:

- Implement public function:
  - `skeletonization`
  - `skeleton_search`
  - `tier0_vertex_id_to_input_vertex_id`
- Return tuple of `SimplexHLiftRecord`.
- Sort records deterministically by degree and simplex id.
- Add integration-style unit test from H graph through skeletonization and fake
  simplex records.

Completion:

- H-lift computation works as a single function.

Stop conditions:

- If fake records are too verbose, add small test helpers in `tests/fakes.py`
  without broad abstractions.

## Phase 4 - Public Result And API Refactor

### Stage 4.1 - Add Combined Result Model

**Action 4.1.1 - Add SearchWithHLiftsResult**

Target files:

```text
src/jet_simplex_search/api.py
tests/test_api.py
```

Procedure:

- Add frozen slots dataclass `SearchWithHLiftsResult`.
- Fields:
  - `k`
  - `skeletonization`
  - `skeleton_search`
  - `h_lifts`
  - `h_lift_diagnostics`
- Normalize `h_lifts` to tuple.
- Add tests for construction and basic field access.

Completion:

- Public graph-H API can return both search and lift layers.

Stop conditions:

- If records are moved to a separate module to avoid API imports, update this
  workplan and tests.

**Action 4.1.2 - Preserve skeleton-only lower-level API**

Target files:

```text
src/jet_simplex_search/api.py
tests/test_api.py
tests/test_static_search_fake_tower.py
```

Procedure:

- Add `search_skeleton_simplices(adapter, k, artifact_config=None)` or an
  equivalent explicit lower-level function.
- It should call `run_static_small_object_search`.
- It should return `SimplexSearchResult`.
- Existing fake-adapter tests should use this lower-level path if needed.

Completion:

- Tests and advanced users can still run tower-only skeleton search.

Stop conditions:

- Do not overload `search_simplices(adapter=...)` with H-lift semantics unless
  the return type is unambiguous.

### Stage 4.2 - Rewire Public search_simplices

**Action 4.2.1 - Skeletonize graph input in public API**

Target files:

```text
src/jet_simplex_search/api.py
tests/test_api.py
```

Procedure:

- Change public graph path:
  - validate `k`;
  - call `skeletonize_graph(graph)`;
  - build adapter from `skeletonization.skeleton_graph`.
- Keep adapter-only path either removed from public `search_simplices` or routed
  to `search_skeleton_simplices`.
- Update tests to assert `search_simplices(graph=H, k=...)` returns
  `SearchWithHLiftsResult`.

Completion:

- Public API no longer builds tower directly from arbitrary H.

Stop conditions:

- If too many tests depend on old return type, add compatibility wrapper only if
  the Project Owner approves it.

**Action 4.2.2 - Compute H-lifts in public API**

Target files:

```text
src/jet_simplex_search/api.py
tests/test_api.py
```

Procedure:

- After `skeleton_search`, call `compute_h_lifts_for_tier_zero`.
- Obtain tier-0 vertex map from adapter.
- Build diagnostics with `build_h_lift_diagnostics`.
- Return `SearchWithHLiftsResult`.
- Add API tests:
  - parallel edge H gives one skeleton edge and H-lift count > 1;
  - missing loop gives zero-count degenerate address retained.

Completion:

- Public API returns H-aware results.

Stop conditions:

- If adapter cannot provide tier-0 vertex map yet, temporarily use identity map
  only for direct/fake adapter tests and block real adapter integration until
  Phase 6.

**Action 4.2.3 - Handle artifact writing for combined result**

Target files:

```text
src/jet_simplex_search/api.py
tests/test_api.py
```

Procedure:

- Keep `artifact_config` parameter.
- Route combined results to updated artifact writer only after Phase 7.
- Until Phase 7, either:
  - defer artifact writing tests; or
  - raise a clear error for combined result artifacts.
- Prefer implementing Phase 7 before merging public artifact behavior.

Completion:

- Public API does not silently write incomplete artifacts.

Stop conditions:

- If existing API tests require artifact writing, implement artifact support in
  same pass before changing return type.

## Phase 5 - state_collapser Simple-Reflexive Tier Mode

### Stage 5.1 - Upstream Scope Check

**Action 5.1.1 - Confirm upstream edit approval**

Target files:

```text
../state_collapser/*
```

Procedure:

- Confirm Project Owner approved edits to `../state_collapser`.
- Confirm branch/worktree status in the upstream repo.
- Confirm test command.

Completion:

- Upstream editing is approved and baseline is known.

Stop conditions:

- If not approved, do not modify upstream. Keep this phase as a blocked
  dependency.

### Stage 5.2 - Add Grouping Policy

**Action 5.2.1 - Add action grouping policy**

Target files:

```text
../state_collapser/src/state_collapser/tower/partition/action_layer.py
../state_collapser/tests/tower/partition/test_action_layer.py
```

Procedure:

- Add the smallest explicit policy needed to preserve default behavior and
  support JSS:
  - default: source-target-action identity grouping;
  - JSS mode: source-target grouping.
- Keep default tests passing unchanged.
- Add test proving default mode still creates two action cells for two actions
  from `a` to `b`.

Completion:

- Existing state_collapser behavior remains default.

Stop conditions:

- If this requires broad public API redesign in state_collapser, stop and
  request Project Owner direction.

**Action 5.2.2 - Implement source-target grouping mode**

Target files:

```text
../state_collapser/src/state_collapser/tower/partition/action_layer.py
../state_collapser/tests/tower/partition/test_action_layer.py
```

Procedure:

- In simple-reflexive/JSS mode, group live non-loop edges by:
  - `source_cell`
  - `target_cell`
- Do not include primitive action identity in the grouping key.
- Preserve all primitive edge ids in `edge_ids_by_action_cell`.
- Add test:
  - two primitive actions `a -> b` become one action cell in JSS mode;
  - that action cell contains both primitive edge ids.

Completion:

- Parallel action identities collapse in JSS mode while provenance remains.

Stop conditions:

- If state_collapser invariants assume one label key per action cell, update
  invariants carefully or add separate provenance field.

### Stage 5.3 - Formal Loop Semantics

**Action 5.3.1 - Verify internal edge recording remains provenance**

Target files:

```text
../state_collapser/src/state_collapser/tower/partition/action_layer.py
../state_collapser/src/state_collapser/tower/partition/loop_policy.py
../state_collapser/tests/tower/partition/test_action_layer.py
```

Procedure:

- Confirm internal edges remain recorded when source and target merge.
- Confirm internal edges are not exposed as live action-cell multiplicity in JSS
  mode.
- Add or update tests for contraction that turns a live edge internal.

Completion:

- Internal edge provenance is retained without live loop multiplicity.

Stop conditions:

- Do not delete internal edge records; other state_collapser behavior may rely
  on them.

**Action 5.3.2 - Add simple-reflexive tier readout loop contract**

Target files:

```text
../state_collapser/src/state_collapser/tower/partition/tower.py
../state_collapser/tests/tower/partition/test_tower_initialization.py
```

Procedure:

- Add a readout/query path or documented mode guaranteeing one formal loop per
  state cell for JSS graph semantics.
- The formal loop does not have to be a `BaseEdge`.
- Add tests that every state cell in a JSS-mode tier has one formal loop in the
  exposed graph semantics.

Completion:

- JSS can rely on exactly one loop option per tier node.

Stop conditions:

- If state_collapser maintainers reject formal loops in upstream, JSS must
  generate formal identities from simple non-loop tier edges but upstream still
  must not construct next tiers from loop multiplicity.

### Stage 5.4 - Ensure Tier Construction Uses Simple Surfaces

**Action 5.4.1 - Apply simple-reflexive mode during initialization**

Target files:

```text
../state_collapser/src/state_collapser/tower/partition/tower.py
../state_collapser/src/state_collapser/tower/partition/action_layer.py
../state_collapser/tests/tower/partition/test_tower_initialization.py
```

Procedure:

- Thread the simple-reflexive/JSS mode through:
  - tier-0 action layer construction;
  - carry-forward action layer construction;
  - dirty action-cell rebuilds.
- Ensure the action surface at tier `r` is simple before it is used to create
  tier `r+1`.
- Add tests for a tower with parallel primitive edges.

Completion:

- JSS-mode tower construction never advances from multiplicity-bearing live
  tier graphs.

Stop conditions:

- If this cannot be done in current partition architecture, stop and document
  the minimal upstream architectural change needed.

**Action 5.4.2 - Add upstream invariant report coverage**

Target files:

```text
../state_collapser/src/state_collapser/tower/partition/invariants.py
../state_collapser/tests/tower/partition/*
```

Procedure:

- If existing invariant reports assume action identity grouping, update them to
  account for the grouping policy.
- Add JSS-mode invariant checks:
  - no duplicate live source-target non-loop action cells;
  - no live internal loop multiplicity;
  - provenance edge ids remain assigned.

Completion:

- Upstream invariants protect JSS mode.

Stop conditions:

- If invariant changes affect many unrelated tests, stop and inspect whether
  the mode boundary is too broad.

### Stage 5.5 - Upstream Test Run

**Action 5.5.1 - Run state_collapser tests**

Target files:

```text
../state_collapser/*
```

Command:

```text
uv run pytest
```

Procedure:

- Run from `../state_collapser`.
- Record result in JSS implementation log.
- Fix only failures related to approved upstream changes.

Completion:

- Upstream tests pass or known baseline failures are documented.

Stop conditions:

- If unrelated upstream failures appear, stop and report.

## Phase 6 - JSS Tower Adapter Refactor

### Stage 6.1 - Consume Simple-Reflexive Tower Mode

**Action 6.1.1 - Update StateCollapserStaticTowerAdapter.from_graph**

Target files:

```text
src/jet_simplex_search/tower_adapter.py
tests/integration/test_state_collapser_static_tower.py
```

Procedure:

- Pass the approved state_collapser simple-reflexive/JSS mode when building the
  tower.
- Build from `skeletonization.skeleton_graph` in public API.
- Preserve default behavior for tests that pass custom fake adapters.

Completion:

- Real adapter builds a JSS-compatible tower from G.

Stop conditions:

- If installed state_collapser release lacks the new mode, update dependency
  handling or block release until upstream version exists.

**Action 6.1.2 - Add adapter simple-reflexive invariant assertion**

Target files:

```text
src/jet_simplex_search/tower_adapter.py
tests/test_tower_adapter_fake.py
tests/integration/test_state_collapser_static_tower.py
```

Procedure:

- Add helper that checks each adapter tier:
  - no non-identity loops in `tier_edges`;
  - at most one edge per ordered source-target pair;
  - projection is endpoint-determined.
- Call it in integration tests.
- Consider calling it in real adapter initialization.

Completion:

- Adapter catches multiplicity leakage early.

Stop conditions:

- If fake adapters intentionally violate this, update fakes to represent simple
  tower semantics.

### Stage 6.2 - Add Tier-0 Vertex Map

**Action 6.2.1 - Implement tier0 vertex mapping**

Target files:

```text
src/jet_simplex_search/tower_adapter.py
tests/integration/test_state_collapser_static_tower.py
```

Procedure:

- Add adapter method returning:
  - `Mapping[str, str]` from tier-0 adapter vertex id to original skeleton/input
    vertex id.
- For state_collapser tier 0, assert each state cell has exactly one member.
- Map that member back through `state_by_vertex_id`.
- Add integration tests.

Completion:

- Public API can map tier-0 simplex vertices back to H fibers.

Stop conditions:

- If tier 0 is not singleton, stop; that violates `G ~= G^0`.

**Action 6.2.2 - Add protocol method or helper**

Target files:

```text
src/jet_simplex_search/tower_adapter.py
tests/fakes.py
tests/test_static_search_fake_tower.py
```

Procedure:

- Decide whether `StaticTowerAdapterProtocol` includes the tier-0 map method.
- If included, update fake adapters.
- If not included, keep the method specific to `StateCollapserStaticTowerAdapter`
  and have public API require the real adapter for H-lifts.
- Prefer protocol method if tests and API use fake adapters for H-lift paths.

Completion:

- Type boundary for tier-0 mapping is explicit.

Stop conditions:

- Do not let `h_lift.py` import state_collapser types.

### Stage 6.3 - Index Edge Fiber Targets

**Action 6.3.1 - Build tier edge source-target cache once**

Target files:

```text
src/jet_simplex_search/tower_adapter.py
tests/test_tower_adapter_fake.py
tests/integration/test_state_collapser_static_tower.py
```

Procedure:

- Add cache builder for each tier:
  - edge id -> source;
  - edge id -> target;
  - `(source, target)` -> edge id.
- Populate from simple tier edges.
- Ensure cache is deterministic.

Completion:

- Repeated `edge_source` and `edge_target` do not rebuild whole tier views.

Stop conditions:

- If cache invalidation is needed for dynamic towers, stop. This package uses a
  static tower.

**Action 6.3.2 - Build edge projection cache**

Target files:

```text
src/jet_simplex_search/tower_adapter.py
tests/test_tower_adapter_fake.py
tests/integration/test_state_collapser_static_tower.py
```

Procedure:

- For each non-bottom tier edge:
  - project source vertex;
  - project target vertex;
  - if endpoints collapse, projection is formal identity at projected source;
  - otherwise projection is downstream simple edge id for projected pair.
- Cache `(tier, edge_id) -> downstairs_edge_id`.
- Add tests for non-collapsed and collapsed projections.

Completion:

- `project_edge` becomes endpoint-determined and cached.

Stop conditions:

- If downstream pair has no simple edge id, stop; tower construction invariant
  failed.

**Action 6.3.3 - Build edge_fiber_targets index**

Target files:

```text
src/jet_simplex_search/tower_adapter.py
tests/test_fiber_lift.py
tests/integration/test_state_collapser_static_tower.py
```

Procedure:

- Build mapping:
  - `(upstairs_tier, downstairs_edge_id, upstairs_source_id)`
  - to frozenset of upstairs target ids.
- Include formal identity behavior:
  - identity at upstairs source projects to identity downstairs when endpoint
    projection matches.
- Populate once per tier.
- Update `edge_fiber_targets` to use indexed lookup only.
- Add tests comparing indexed lookup to a slow reference on small fake towers.

Completion:

- Fiber lifting avoids repeated whole-tier edge scans.

Stop conditions:

- If identity projection semantics are ambiguous in a quotient tier, stop and
  re-read the blueprint/source docs.

## Phase 7 - Artifact Schema Version 2

### Stage 7.1 - Add Serialization Helpers

**Action 7.1.1 - Serialize skeletonization records**

Target files:

```text
src/jet_simplex_search/artifacts.py
tests/test_artifacts.py
```

Procedure:

- Add helper for `SkeletonEdgeFiber`.
- Add helper for `SkeletonLoopFiber`.
- Add helper for `SkeletonizationDiagnostics`.
- Respect config flag for including full H fiber members.
- Add tests for JSON-safe output.

Completion:

- Artifacts can expose H-to-G preprocessing.

Stop conditions:

- Do not omit fiber counts when member ids are hidden.

**Action 7.1.2 - Serialize H-lift records**

Target files:

```text
src/jet_simplex_search/artifacts.py
tests/test_artifacts.py
```

Procedure:

- Add helper for `SimplexHLiftRecord`.
- Add helper for `HFaceLiftFactor`.
- Include:
  - count;
  - positive/zero flag;
  - face factor count;
  - member ids only when config allows.
- Add tests for zero-count degenerate records.

Completion:

- Artifacts preserve zero-count skeleton simplex evidence.

Stop conditions:

- Do not expand Cartesian products of H witnesses in default artifact output.

### Stage 7.2 - Update ArtifactConfig

**Action 7.2.1 - Add H-lift artifact flags**

Target files:

```text
src/jet_simplex_search/artifacts.py
tests/test_artifacts.py
```

Procedure:

- Add flags:
  - `include_h_fiber_members: bool = True`
  - `include_h_lift_face_factors: bool = True`
  - `include_expanded_h_lift_witnesses: bool = False`
  - `max_expanded_h_lift_witnesses: int = 100_000`
- Validate that expansion is not implemented unless separately approved.
- If expansion is requested before implementation, raise `ArtifactWriteError`.

Completion:

- Config exposes future-safe H-lift artifact behavior.

Stop conditions:

- Do not silently ignore `include_expanded_h_lift_witnesses=True`.

### Stage 7.3 - Write Combined Artifacts

**Action 7.3.1 - Update single_json writer**

Target files:

```text
src/jet_simplex_search/artifacts.py
tests/test_artifacts.py
```

Procedure:

- Allow `write_search_artifact` to accept `SearchWithHLiftsResult` in addition
  to `SimplexSearchResult`.
- Set schema version 2 for combined results.
- Include:
  - manifest;
  - skeletonization;
  - skeleton search records;
  - simplex fibers;
  - edge fibers;
  - H-lifts;
  - diagnostics.
- Add tests loading JSON and checking top-level keys.

Completion:

- Single JSON artifacts are H-aware.

Stop conditions:

- If circular imports appear between `api.py` and `artifacts.py`, move the
  combined result dataclass to a neutral module.

**Action 7.3.2 - Update manifest_tables writer**

Target files:

```text
src/jet_simplex_search/artifacts.py
tests/test_artifacts.py
```

Procedure:

- Add JSONL tables:
  - `skeleton_edge_fibers.jsonl`
  - `skeleton_loop_fibers.jsonl`
  - `h_lift_records.jsonl`
  - `h_lift_face_factors.jsonl`
- Keep existing:
  - `simplex_records.jsonl`
  - `simplex_fibers.jsonl`
  - `edge_fibers.jsonl`
  - `diagnostics.json`
- Add manifest entries with counts.
- Add tests for file creation and row counts.

Completion:

- Manifest tables distinguish skeleton, tower, and H-lift layers.

Stop conditions:

- If old artifact tests assume exact manifest schema, update them to check
  schema version and relevant keys rather than stale shape.

## Phase 8 - Search And Lift Regression Coverage

### Stage 8.1 - Small-Object Boundary Regression

**Action 8.1.1 - Add no-downstairs-interior test**

Target files:

```text
tests/test_fiber_lift.py
tests/test_static_search_fake_tower.py
```

Procedure:

- Build fake tower where downstairs has enough edges to suggest a boundary but
  no downstairs 2-simplex record in the search result being lifted.
- Ensure upstairs graph could form a 2-simplex if searched ad hoc.
- Assert no upstairs 2-simplex is emitted over the missing downstairs simplex.
- Name the test so it documents small-object semantics.

Completion:

- Regression protects "search only where downstairs simplex exists".

Stop conditions:

- If fake tower cannot express the case, extend fake adapter minimally.

### Stage 8.2 - Existing Smoke Count Preservation

**Action 8.2.1 - Run existing smoke scripts**

Target files:

```text
smoke/*.py
smoke/*.md
```

Procedure:

- Run existing smoke scripts after API changes.
- Record which scripts break because return type changed.
- Do not update expected text until count semantics are decided per script.

Completion:

- Smoke impact is known.

Stop conditions:

- If smoke scripts encode old multiplicity assumptions, revise them with
  explicit skeleton/H-lift labels rather than preserving ambiguous counts.

**Action 8.2.2 - Update smoke table utility**

Target files:

```text
smoke/simplex_table.py
smoke/smoke_*.py
smoke/smoke_*.md
```

Procedure:

- Update table output to distinguish:
  - skeleton simplex count;
  - positive H-lifted address count;
  - total H-lift count.
- Keep old skeleton count tables available if useful.
- Update markdown arguments for each smoke script.

Completion:

- Smoke outputs no longer mix count semantics.

Stop conditions:

- If Project Owner wants smoke scripts skeleton-only for now, keep H-lift
  smoke scripts separate.

## Phase 9 - README And Public Documentation

### Stage 9.1 - Update Public Description

**Action 9.1.1 - Update README semantics**

Target files:

```text
README.md
```

Procedure:

- Preserve logo and title exactly.
- Explain:
  - input graph H may have loops and parallel edges;
  - package builds simple-reflexive skeleton G;
  - tower search runs over G;
  - H-lifts are computed for tier-0 skeleton simplices;
  - zero-count skeleton simplices remain visible;
  - Kan version is future work.
- Preserve Abdul Malik attribution.

Completion:

- README no longer implies tower directly searches H multiplicity.

Stop conditions:

- Do not link prime directive docs from root README.

**Action 9.1.2 - Update README runnable examples**

Target files:

```text
README.md
tests/test_readme_examples.py
```

Procedure:

- Add or update examples using the public `search_simplices(graph=H, k=...)`.
- Ensure example graph includes at most simple behavior unless showing H-lifts.
- Add regression test or smoke check for README code snippets if already
  established in the repo.

Completion:

- README examples are runnable.

Stop conditions:

- If README examples require state_collapser unreleased upstream mode, mark the
  package as unreleased/pre-release until dependency is available.

### Stage 9.2 - Update Design Indexes If Any

**Action 9.2.1 - Update release-prep notes**

Target files:

```text
docs/design/release_prep/01_001_public_release_preparation_plan.md
docs/design/release_prep/01_002_public_release_preparation_implementation_workplan.md
```

Procedure:

- Add a release blocker noting H-to-G refactor and upstream state_collapser
  simple-reflexive mode.
- Do not link prime directive docs in root docs.
- Preserve attribution.

Completion:

- Release prep reflects new semantic blocker.

Stop conditions:

- If release prep docs have been superseded, update the active release prep doc
  only.

## Phase 10 - Full Verification

### Stage 10.1 - Unit Test Verification

**Action 10.1.1 - Run focused tests**

Target files:

```text
tests/test_ids.py
tests/test_skeleton.py
tests/test_normalize.py
tests/test_h_lift.py
tests/test_api.py
tests/test_artifacts.py
tests/test_fiber_lift.py
```

Command:

```text
uv run pytest tests/test_ids.py tests/test_skeleton.py tests/test_normalize.py tests/test_h_lift.py tests/test_api.py tests/test_artifacts.py tests/test_fiber_lift.py
```

Procedure:

- Run focused tests after implementation phases.
- Fix failures by reading failing source/tests.
- Record result in implementation log.

Completion:

- Focused JSS tests pass.

Stop conditions:

- If failures expose semantic ambiguity, stop and ask Project Owner rather than
  guessing.

**Action 10.1.2 - Run full JSS test suite**

Target files:

```text
all JSS source and tests
```

Command:

```text
uv run pytest
```

Procedure:

- Run full suite.
- Record pass/fail and test count.
- Fix only implementation-related failures.

Completion:

- Full JSS suite passes.

Stop conditions:

- If unrelated baseline failures appear, document and report.

### Stage 10.2 - Upstream Verification

**Action 10.2.1 - Run upstream state_collapser tests**

Target files:

```text
../state_collapser/*
```

Command:

```text
uv run pytest
```

Procedure:

- Run from `../state_collapser` if upstream edits were made.
- Record result.
- Fix only approved upstream changes.

Completion:

- Upstream test suite passes or known external failures are documented.

Stop conditions:

- If upstream suite fails for unrelated reasons, stop and report.

### Stage 10.3 - Integration Verification

**Action 10.3.1 - Run integration tests**

Target files:

```text
tests/integration/test_state_collapser_static_tower.py
```

Command:

```text
uv run pytest tests/integration
```

Procedure:

- Verify real state_collapser adapter integration.
- Confirm simple-reflexive tier invariants.
- Confirm tier-0 vertex map.
- Confirm H-lift API path.

Completion:

- Real dependency path works.

Stop conditions:

- If integration fails because installed state_collapser lacks new mode, update
  dependency version/source and rerun.

**Action 10.3.2 - Run smoke scripts**

Target files:

```text
smoke/*.py
```

Procedure:

- Run every smoke script.
- Capture output when markdown arguments need updating.
- Confirm tables label skeleton and H-lift counts.

Completion:

- Smoke scripts run and documentation agrees with output.

Stop conditions:

- If smoke expected counts conflict with H-lift semantics, update the markdown
  argument and explain the correction.

## Phase 11 - Dependency And Release Surface

### Stage 11.1 - state_collapser Dependency

**Action 11.1.1 - Update dependency to approved state_collapser release**

Target files:

```text
pyproject.toml
uv.lock
```

Procedure:

- Use the actual approved `state_collapser` GitHub release/tag.
- Remove local path dependency before public release.
- Run lock/update command using approved project workflow.
- Record the dependency reference in implementation log.

Completion:

- JSS depends on a release that includes simple-reflexive tier mode.

Stop conditions:

- If no upstream release exists yet, do not fake release readiness.

### Stage 11.2 - Packaging Verification

**Action 11.2.1 - Build package**

Target files:

```text
pyproject.toml
src/jet_simplex_search/*
```

Command:

```text
uv build
```

Procedure:

- Build sdist/wheel if dependency state is release-ready.
- Inspect build output for included files.
- Record result.

Completion:

- Package builds locally.

Stop conditions:

- If build command is not part of current approved workflow, use the repo's
  existing build command.

**Action 11.2.2 - Check public exports and docs**

Target files:

```text
src/jet_simplex_search/__init__.py
README.md
pyproject.toml
```

Procedure:

- Confirm public exports match README examples.
- Confirm badges remain appropriate.
- Confirm known limitations mention pre-release/refactor state if relevant.
- Confirm docs preserve Abdul Malik attribution.

Completion:

- Public release surface is coherent.

Stop conditions:

- If release status is still blocked by upstream dependency, mark clearly as
  pre-release/internal.

## Phase 12 - Implementation Closeout

### Stage 12.1 - Final Reality Check

**Action 12.1.1 - Inspect final git status**

Target files:

```text
none
```

Command:

```text
git status --short
```

Procedure:

- Record final modified/untracked files.
- Ensure no unrelated user changes were reverted.
- Ensure generated caches are not accidentally added.

Completion:

- Final worktree state is understood.

Stop conditions:

- If unrelated files changed unexpectedly, inspect before final response.

**Action 12.1.2 - Record implementation log closeout**

Target files:

```text
docs/design/h_to_g_skeleton_refactor/01_004_h_to_g_skeleton_realization_implementation_log.md
```

Procedure:

- Record completed phases/actions.
- Record final test commands and results.
- Record blockers or deferred phases.
- Record upstream dependency status.

Completion:

- Implementation log tells the next engineer exactly what happened.

Stop conditions:

- If implementation did not reach approved scope, state exactly where it stopped
  and why.

### Stage 12.2 - Final Report

**Action 12.2.1 - Report concise outcome to Project Owner**

Target files:

```text
none
```

Procedure:

- Summarize:
  - files changed;
  - semantic changes;
  - tests run;
  - blockers/deferred work;
  - upstream state_collapser status.
- Do not propose unrelated next steps unless asked.

Completion:

- Project Owner receives accurate closeout.

Stop conditions:

- If tests were not run, say so explicitly.

## Phase Dependency Graph

```text
Phase 0:
  required before all implementation

Phase 1:
  required before H-lift computation and public API refactor

Phase 2:
  required before trusting direct search over G

Phase 3:
  required before combined public result

Phase 4:
  requires Phases 1, 2, 3

Phase 5:
  required before real state_collapser-backed release correctness

Phase 6:
  requires Phase 5 for real adapter semantics
  can partially proceed with fake adapters before Phase 5

Phase 7:
  requires Phases 3 and 4

Phase 8:
  requires Phases 3, 4, 6

Phase 9:
  requires public API semantics from Phase 4

Phase 10:
  requires all implemented phases in approved scope

Phase 11:
  requires upstream release availability if public release is in scope

Phase 12:
  required at the end of any approved implementation pass
```

## Semantic Stop Conditions

Stop and resynchronize with the Project Owner if any of these occur:

```text
1. H-lift counts appear to require quotient tiers below G^0.

2. A degenerate G simplex is about to be given one H-lift from a formal identity
   when H has no actual loop.

3. Zero-count skeleton simplices are about to be filtered out by default.

4. Parallel H edges are about to remain as live tower/search multiplicity.

5. state_collapser can only provide adapter-level cleanup after tower
   construction, not simple-reflexive tier construction before the next tier.

6. Label conflicts in parallel H edges are about to be silently merged.

7. Expanded H witness assignments are about to become default output.

8. The implementation needs Kan/horn-filling semantics to pass tests.

9. A test expectation conflicts with the Project Owner's clarified semantics.

10. A source file differs materially from the assumptions in this workplan.
```

## Final Acceptance Criteria

The implementation is accepted only when:

```text
1. H with loops and parallel edges is accepted by public search.

2. H is deterministically skeletonized to simple G before tower construction.

3. G-search and tower lifting use skeleton/tower simplex records only.

4. Every JSS tower tier used to construct a later tier is simple-reflexive in
   the approved state_collapser mode.

5. Direct search still uses cached frontier recurrence.

6. Small-object lifting still searches only over existing downstairs simplices.

7. Tier-0 skeleton simplices receive compressed H-lift records.

8. Degenerate skeleton simplices lift to H exactly through actual H loops.

9. Parallel H edges produce distinct H-lifts through product counts.

10. Zero-count skeleton simplices are retained.

11. Artifacts separate skeletonization, skeleton/tower search, and H-lift
    evidence.

12. README and smoke outputs label skeleton counts, positive H-lifted address
    counts, and total H-lift counts without ambiguity.

13. JSS tests pass.

14. state_collapser tests pass if upstream edits were made.

15. The final implementation log records commands, results, blockers, and
    dependency status.
```

