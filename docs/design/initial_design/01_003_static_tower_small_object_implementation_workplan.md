# Static Tower Small-Object Implementation Workplan

## Status

Implementation workplan derived from:

```text
docs/design/initial_design/01_001_static_tower_small_object_simplex_search.md
docs/design/initial_design/01_002_static_tower_small_object_package_blueprint.md
```

This document is a Phase.Stage.Action execution plan. It is not code
implementation. Per the repo Prime Directive, this workplan becomes binding only
for an implementation pass explicitly approved by the Project Owner.

## Attribution

The algorithmic content is PM Abdul Malik's work and part of his thesis. This
includes:

- static quotient-tower simplex search;
- degree-wise `Out` construction;
- formal identity loops for degeneracy;
- cached frontier recurrence;
- dimension-preserving lift over downstairs simplices;
- final-edge fiber targeting speedup.

The Project Owner relayed, clarified, and corrected the package semantics in the
June 12, 2026 design discussion.

This workplan is consultant-authored implementation planning. It must not be
treated as the mathematical source of the algorithm.

## Prime Directive Execution Rules

1. Do not implement this workplan until the Project Owner explicitly approves an
   implementation scope.
2. Once approved, execute the approved phases and actions in order unless a
   listed stop condition triggers.
3. Do not silently simplify, reorder, skip, or substitute actions.
4. Do not reinvent `state_collapser` tower semantics.
5. If `state_collapser` reality differs from this workplan, stop and reconstruct
   from actual source/tests/docs before editing.
6. If a patch rejection, missing symbol, unexpected test failure, or semantic
   mismatch occurs, stop local improvisation and re-read the relevant files.
7. Keep design attribution intact.
8. Keep Kan replacement, meaningful non-identity input loops, multigraph
   witness splitting, and large-graph storage optimizations out of first-scope
   implementation unless separately approved.

## Implementation Scope

First-scope implementation target:

```text
Build a small-object/static-tower directed flag simplex enumerator that can
normalize a sparse directed graph, enumerate bottom-tier simplices including
degenerates through k, lift simplices down a static tower by downstairs simplex
fibers, and emit auditable artifacts.
```

First-scope non-goals:

- no Kan replacement implementation;
- no dynamic `TowerRuntime`-driven algorithm;
- no RL learner/training loop;
- no tensor/GPU/vectorized implementation;
- no multiprocessing/out-of-core engine;
- no custom quotient tower implementation;
- no public API broadening beyond the planned small entrypoints;
- no hidden dependency on `state_collapser` internals without adapter isolation.

## Current Baseline

At the time this workplan was written, the package scaffold exists:

```text
pyproject.toml
uv.lock
src/jet_simplex_search/__init__.py
tests/test_package.py
docs/design/initial_design/01_001_static_tower_small_object_simplex_search.md
docs/design/initial_design/01_002_static_tower_small_object_package_blueprint.md
```

Baseline command:

```text
uv run pytest
```

Expected baseline:

```text
tests/test_package.py passes
```

## Phase 0 - Execution Preparation

### Stage 0.1 - Confirm Approved Scope

**Action 0.1.1 - Confirm implementation approval**

Target files:

```text
none
```

Procedure:

- Confirm the Project Owner has approved implementation, not merely planning.
- Confirm which phases are approved.
- Confirm whether `state_collapser` integration is approved in the same pass or
  deferred until local fake-adapter behavior is correct.

Completion:

- Approved phase range is known.
- No source files are edited before approval.

Stop conditions:

- If the Project Owner asks only for planning or review, stop before code edits.
- If approved scope conflicts with this workplan, revise the workplan first.

**Action 0.1.2 - Record execution spine**

Target files:

```text
docs/design/initial_design/01_004_static_tower_small_object_implementation_log.md
```

Procedure:

- Create an implementation log when implementation begins.
- Record approved phase range.
- Record current git branch and commit.
- Record baseline command and result.

Completion:

- Implementation log exists before code changes.

Stop conditions:

- If the log path already exists with unrelated content, inspect and append
  carefully rather than overwriting.

### Stage 0.2 - Baseline Repository Check

**Action 0.2.1 - Inspect git state**

Target files:

```text
none
```

Command:

```text
git status -sb
```

Procedure:

- Record staged, unstaged, and untracked files in the implementation log.
- Distinguish existing PO/user changes from implementation changes.
- Do not revert unrelated changes.

Completion:

- Worktree state is understood.

Stop conditions:

- If files needed for implementation contain unexpected changes, read them and
  adapt without reverting.

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

- Run the current test suite.
- Record pass/fail in the implementation log.
- If failure occurs before implementation edits, treat it as baseline reality.

Completion:

- Baseline test result is known.

Stop conditions:

- If baseline fails, stop and diagnose before implementing.

### Stage 0.3 - Confirm Package Skeleton

**Action 0.3.1 - Verify package metadata**

Target files:

```text
pyproject.toml
uv.lock
```

Procedure:

- Confirm package name is `jet-simplex-search`.
- Confirm Python range is `>=3.11,<3.13`.
- Confirm `uv run pytest` uses the `dev` dependency group.
- Confirm no unnecessary runtime dependencies have been added.

Completion:

- Package metadata supports first implementation.

Stop conditions:

- If dependency metadata is stale or malformed, fix only package metadata and
  rerun `uv run pytest`.

**Action 0.3.2 - Verify source layout**

Target files:

```text
src/jet_simplex_search/__init__.py
tests/test_package.py
```

Procedure:

- Confirm package import works.
- Confirm `__version__` exists.
- Confirm tests import from installed package/source layout.

Completion:

- Current scaffold is ready for module additions.

## Phase 1 - Core Graph And Error Contracts

### Stage 1.1 - Define Package Errors

**Action 1.1.1 - Add package error hierarchy**

Target files:

```text
src/jet_simplex_search/errors.py
tests/test_errors.py
```

Implementation:

- Define `JetSimplexSearchError`.
- Define `InvalidGraphError`.
- Define `InvalidKError`.
- Define `TowerAdapterError`.
- Define `SimplexInvariantError`.
- Define `ArtifactWriteError`.
- Keep classes simple; no extra behavior unless tests require it.

Tests:

- Assert every package error subclasses `JetSimplexSearchError`.
- Assert each error can be raised with a useful message.

Completion:

- Error classes exist and are importable.
- `uv run pytest tests/test_errors.py` passes.

Stop conditions:

- If errors start accumulating implementation-specific state, stop and simplify.

**Action 1.1.2 - Export no broad public API yet**

Target files:

```text
src/jet_simplex_search/__init__.py
```

Implementation:

- Keep top-level exports minimal.
- Do not export all errors at top level unless the Project Owner approves a
  public API expansion.

Tests:

- Existing import smoke still passes.

Completion:

- Error module exists but top-level API remains small.

### Stage 1.2 - Define Input Graph Records

**Action 1.2.1 - Add immutable graph input records**

Target files:

```text
src/jet_simplex_search/graph.py
tests/test_graph.py
```

Implementation:

- Add frozen dataclasses:
  - `InputVertex`
  - `InputEdge`
  - `GraphInput`
- Use string ids for first scope.
- Preserve optional payload fields.
- Preserve edge labels as `tuple[object, ...]`.
- Normalize iterable inputs to tuples in constructors or helper builders only if
  that is done consistently.

Invariants:

- Vertex ids must be unique.
- Edge ids must be unique.
- Edge endpoints must reference known vertices.
- Empty graphs are invalid for search unless explicitly approved later.

Tests:

- Construct a one-vertex graph.
- Construct a one-edge graph.
- Reject duplicate vertex ids.
- Reject duplicate edge ids.
- Reject edge with missing source.
- Reject edge with missing target.
- Confirm labels are stored as tuples.

Completion:

- `GraphInput` is a stable input contract for first-scope tests.

Stop conditions:

- If graph input starts supporting external formats, stop; adapters belong
  later.

**Action 1.2.2 - Add graph validation helper**

Target files:

```text
src/jet_simplex_search/graph.py
tests/test_graph.py
```

Implementation:

- Add `validate_graph_input(graph: GraphInput) -> None`.
- Raise `InvalidGraphError` with explicit messages.
- Call validation from `GraphInput` construction only if using a custom
  constructor; otherwise call from normalization/search entrypoints.

Tests:

- Validation succeeds for a valid sparse graph.
- Validation errors identify duplicate ids or missing endpoint.

Completion:

- Invalid graph states fail early and readably.

### Stage 1.3 - Add Deterministic Id Helpers

**Action 1.3.1 - Add id construction helpers**

Target files:

```text
src/jet_simplex_search/ids.py
tests/test_ids.py
```

Implementation:

- Add helper functions for deterministic ids:
  - `identity_edge_id(vertex_id: str) -> str`
  - `simplex_id(tier: int, degree: int, vertices: tuple[str, ...]) -> str`
  - `fiber_id(downstairs_simplex_id: str, upstairs_tier: int) -> str`
- Keep formatting stable and ASCII-safe.
- Do not use Python object ids or nondeterministic hashing.

Tests:

- Same inputs produce same ids.
- Different tier/degree/vertices produce different simplex ids.
- Identity edge ids cannot collide with simple original edge ids by convention.

Completion:

- All later records can use deterministic local ids.

Stop conditions:

- If ids need escaping for arbitrary user ids, implement explicit escaping and
  tests before continuing.

## Phase 2 - Loop Normalization

### Stage 2.1 - Define Normalization Records

**Action 2.1.1 - Add normalization dataclasses**

Target files:

```text
src/jet_simplex_search/normalize.py
tests/test_normalize.py
```

Implementation:

- Add frozen dataclasses:
  - `NormalizationPolicy`
  - `NormalizedEdge`
  - `NormalizedGraph`
- Use `kind: Literal["original", "identity"]`.
- Include:
  - `vertices`
  - `edges`
  - `adjacency_targets`
  - `edge_lookup`
  - `stripped_loop_edge_ids`

Tests:

- Dataclasses are constructible.
- Identity edge kind is distinguishable from original edge kind.

Completion:

- Normalization output type exists before normalization logic.

### Stage 2.2 - Implement First-Scope Loop Policy

**Action 2.2.1 - Implement `normalize_graph`**

Target files:

```text
src/jet_simplex_search/normalize.py
tests/test_normalize.py
```

Implementation:

- Add:

```python
def normalize_graph(
    graph: GraphInput,
    policy: NormalizationPolicy | None = None,
) -> NormalizedGraph:
    ...
```

- Validate graph before normalization.
- Strip input edges whose `source == target` when `strip_input_loops` is true.
- Record stripped loop edge ids.
- Add exactly one identity edge for every vertex.
- Preserve all non-loop original edges.
- Build `adjacency_targets[s] = {s} union {targets of original non-loop edges}`.
- Build `edge_lookup[(source, target)] -> tuple[edge_ids, ...]`.
- Include identity edges in `edge_lookup[(s, s)]`.
- Sort vertices and edge ids deterministically.

Tests:

- No-loop graph gains exactly one identity per vertex.
- Input loop is stripped and recorded.
- Non-loop edges are preserved.
- `adjacency_targets[s]` includes `s`.
- `adjacency_targets[s]` includes all outgoing original targets.
- A vertex with no original outgoing edges has adjacency `{s}`.
- Multiple original edges with same endpoints are preserved in `edge_lookup`.

Completion:

- First-scope graph normalization is deterministic and tested.

Stop conditions:

- If meaningful non-identity input loops are needed, stop and get new design
  approval. Do not silently preserve them as original loops in first scope.

**Action 2.2.2 - Add normalization invariant checker**

Target files:

```text
src/jet_simplex_search/normalize.py
tests/test_normalize.py
```

Implementation:

- Add `assert_normalized_graph_invariants(graph: NormalizedGraph) -> None`.
- Check exactly one identity edge per vertex.
- Check every identity edge has same source/target.
- Check no original edge is a loop.
- Check adjacency targets and edge lookup agree.

Tests:

- Valid normalized graph passes.
- Manually malformed normalized graph fails with `SimplexInvariantError`.

Completion:

- Later phases can validate normalization before search.

## Phase 3 - Frontier And Simplex Records

### Stage 3.1 - Define Simplex Records

**Action 3.1.1 - Add face-edge witness record**

Target files:

```text
src/jet_simplex_search/records.py
tests/test_records.py
```

Implementation:

- Add frozen `FaceEdgeWitness`.
- Fields:
  - `source_index`
  - `target_index`
  - `edge_ids`
- Validate `source_index < target_index`.
- Validate `edge_ids` is nonempty.

Tests:

- Valid witness constructs.
- Empty edge ids rejected.
- Invalid index order rejected.

Completion:

- Face-edge evidence can be represented before simplex construction.

**Action 3.1.2 - Add simplex and result records**

Target files:

```text
src/jet_simplex_search/records.py
tests/test_records.py
```

Implementation:

- Add frozen dataclasses:
  - `SimplexRecord`
  - `SimplexFiberRecord`
  - `EdgeFiberRecord`
  - `SimplexSearchResult`
- Keep fields aligned with the blueprint.
- Validate:
  - `degree == len(vertices) - 1`;
  - `initial_vertex == vertices[0]`;
  - `target_vertex == vertices[-1]`;
  - every witness index is valid for the vertex tuple;
  - `is_degenerate == (len(set(vertices)) < len(vertices))`.

Tests:

- Valid 0-simplex constructs.
- Valid 1-simplex constructs.
- Degenerate simplex flag is enforced.
- Degree mismatch fails.
- Target mismatch fails.
- Witness index outside vertex tuple fails.

Completion:

- Simplex records are immutable, validated, and artifact-friendly.

### Stage 3.2 - Implement Frontier Operations

**Action 3.2.1 - Implement adjacency frontier functions**

Target files:

```text
src/jet_simplex_search/frontier.py
tests/test_frontier.py
```

Implementation:

- Add:

```python
def initial_frontier(graph: NormalizedGraph, vertex_id: str) -> frozenset[str]:
    ...

def extend_frontier(
    prefix_frontier: frozenset[str],
    target_adjacency: frozenset[str],
) -> frozenset[str]:
    ...
```

- Use set intersection.
- Prefer iterating over the smaller set if manually implemented.
- Return `frozenset`.

Tests:

- `initial_frontier(s) == A(s)`.
- `extend_frontier(A(s), A(t)) == A(s) cap A(t)`.
- Repeated vertex leaves frontier unchanged.
- Extension result equals full recomputation for a 3-vertex tuple.

Completion:

- Cached frontier recurrence is implemented and tested.

**Action 3.2.2 - Add face-edge witness lookup**

Target files:

```text
src/jet_simplex_search/frontier.py
tests/test_directed_flag_semantics.py
```

Implementation:

- Add:

```python
def face_edge_witnesses_for_extension(
    graph: NormalizedGraph,
    prefix_vertices: tuple[str, ...],
    target: str,
) -> tuple[FaceEdgeWitness, ...]:
    ...
```

- For each prefix vertex `s_i`, retrieve edge ids for `(s_i, target)`.
- Use identity edge for `(s_i, s_i)`.
- Fail with `SimplexInvariantError` if target is not actually in every required
  adjacency set.

Tests:

- `0 -> 1 -> 2` without `0 -> 2` cannot produce witnesses for extension to `2`.
- Adding `0 -> 2` produces witnesses for `(0, 1, 2)`.
- `(s, s, t)` uses identity witness for repeated position and original edge for
  `s -> t`.

Completion:

- Directed flag semantics are explicit in witness generation.

## Phase 4 - Bottom-Tier Direct Enumeration

### Stage 4.1 - Implement Search Context

**Action 4.1.1 - Add local bottom-tier search context**

Target files:

```text
src/jet_simplex_search/search.py
tests/test_bottom_tier_enumeration.py
```

Implementation:

- Add an internal context record for direct single-tier enumeration.
- Include:
  - normalized graph;
  - tier id;
  - `k`;
  - simplex index by degree;
  - simplex index by id;
  - frontier by simplex id.
- Validate `k >= 0`; raise `InvalidKError` otherwise.

Tests:

- `k = 0` accepted.
- negative `k` rejected.

Completion:

- Direct enumeration has a controlled state container.

### Stage 4.2 - Emit 0-Simplices

**Action 4.2.1 - Implement 0-simplex creation**

Target files:

```text
src/jet_simplex_search/search.py
tests/test_bottom_tier_enumeration.py
```

Implementation:

- Add function:

```python
def enumerate_zero_simplices(
    graph: NormalizedGraph,
    *,
    tier: int,
) -> tuple[SimplexRecord, ...]:
    ...
```

- Emit one 0-simplex for every vertex.
- Use deterministic ordering.
- Set `frontier = A(s)`.
- Set `prefix_simplex_id = None`.
- Set `last_edge_ids = ()`.
- Set `face_edge_witnesses = ()`.
- Set `projection_simplex_id = None` for bottom-tier direct enumeration.

Tests:

- One vertex emits exactly one 0-simplex.
- Three vertices emit three 0-simplices sorted by id.
- Frontier is attached correctly.

Completion:

- Degree-zero base of induction works.

### Stage 4.3 - Emit Higher Simplices By Frontier Extension

**Action 4.3.1 - Implement one-step simplex extension**

Target files:

```text
src/jet_simplex_search/search.py
tests/test_bottom_tier_enumeration.py
tests/test_directed_flag_semantics.py
```

Implementation:

- Add:

```python
def extend_simplex_direct(
    graph: NormalizedGraph,
    simplex: SimplexRecord,
    target: str,
) -> SimplexRecord:
    ...
```

- Require `target in simplex.frontier`.
- Build new vertex tuple.
- Build new face-edge witnesses from existing witnesses plus witnesses from
  every prior vertex to target.
- Set `prefix_simplex_id` to prior simplex id.
- Set `last_edge_ids` to edge ids from prior target vertex to new target.
- Set new frontier to `simplex.frontier cap A(target)`.
- Set `is_degenerate` from repeated vertices.

Tests:

- Extending `(s)` by `s` emits `(s, s)` with identity witness.
- Extending `(s)` by `t` emits `(s, t)` with original edge witness.
- Extending `(0, 1)` by `2` requires `0 -> 2` and `1 -> 2`.
- New frontier equals inductive recurrence.

Completion:

- One-step direct extension enforces full directed flag semantics.

**Action 4.3.2 - Implement direct enumeration through k**

Target files:

```text
src/jet_simplex_search/search.py
tests/test_bottom_tier_enumeration.py
```

Implementation:

- Add:

```python
def enumerate_direct_simplices(
    graph: NormalizedGraph,
    *,
    tier: int,
    k: int,
) -> Mapping[int, tuple[SimplexRecord, ...]]:
    ...
```

- Enumerate degree 0 first.
- For each degree `m < k`, extend each degree `m` simplex by every target in
  sorted `frontier`.
- Dedupe by `(tier, degree, vertices)`.
- Preserve all face-edge witnesses for the first implementation identity policy.
- Return immutable tuples by degree.

Tests:

- Isolated vertex emits `(s)`, `(s,s)`, `(s,s,s)` through `k=2`.
- Single edge emits identity degenerates and edge simplex.
- Triangle emits expected 2-simplex only when all face edges exist.
- No degree greater than `k` appears.
- Deterministic order is stable across repeated calls.

Completion:

- Bottom-tier direct simplex enumeration works without tower dependency.

Stop conditions:

- If implementation drifts into path-only semantics, stop and correct before
  lifting work begins.

## Phase 5 - Fake Static Tower Adapter

### Stage 5.1 - Define Adapter Protocol

**Action 5.1.1 - Add static tower adapter protocol**

Target files:

```text
src/jet_simplex_search/tower_adapter.py
tests/test_tower_adapter_fake.py
```

Implementation:

- Define a `Protocol` or minimal abstract base for static tower queries.
- Required methods:
  - `tiers()`;
  - `bottommost_nondegenerate_tier()`;
  - `tier_vertices(tier)`;
  - `tier_edges(tier)`;
  - `edge_source(tier, edge_id)`;
  - `edge_target(tier, edge_id)`;
  - `project_vertex(tier, vertex_id)`;
  - `project_edge(tier, edge_id)`;
  - `edge_fiber_targets(upstairs_tier, downstairs_edge_id, upstairs_source_id)`.
- Keep protocol free of `state_collapser` imports for fake tests.

Tests:

- Fake adapter satisfies protocol shape.
- Missing method on fake raises or fails test clearly.

Completion:

- Lift algorithm can depend on a static tower boundary.

**Action 5.1.2 - Implement fake tower adapter for tests**

Target files:

```text
tests/fakes.py
tests/test_tower_adapter_fake.py
```

Implementation:

- Add a tiny fake static tower with explicit:
  - tiers;
  - vertices by tier;
  - edges by tier;
  - edge source/target;
  - vertex projections;
  - edge projections;
  - edge fiber target lookup.
- Include a degenerate downstairs case:
  - downstairs identity `id_C`;
  - upstairs non-identity edge `a -> b` with both endpoints projecting to `C`.

Tests:

- Fake adapter returns source-sensitive edge fibers.
- Fake adapter distinguishes identity and non-identity upstairs edges.

Completion:

- Fiber lift tests can verify Abdul Malik's speedup without real
  `state_collapser` dependency.

### Stage 5.2 - Define Tier-Level Normalized Views

**Action 5.2.1 - Build normalized graph view for a tier**

Target files:

```text
src/jet_simplex_search/tower_adapter.py
tests/test_tower_adapter_fake.py
```

Implementation:

- Add helper:

```python
def normalized_graph_for_tier(
    adapter: StaticTowerAdapterProtocol,
    tier: int,
) -> NormalizedGraph:
    ...
```

- Build a `NormalizedGraph` from tier vertices and edges.
- Preserve identity/formal-loop handling at that tier.
- Use adapter source/target for tier edges.
- Do not infer projections here.

Tests:

- Fake tier view normalizes identities.
- Edge lookup uses adapter edge source/target.

Completion:

- Bottom-tier direct enumeration can run over a tower tier view.

Stop conditions:

- If this helper begins duplicating `state_collapser` contraction logic, stop.
  It should only read static tier data through the adapter.

## Phase 6 - Fiber-Addressed Lifting

### Stage 6.1 - Define Fiber Index Records

**Action 6.1.1 - Add simplex and edge fiber indexes**

Target files:

```text
src/jet_simplex_search/lift.py
tests/test_fiber_lift.py
```

Implementation:

- Add internal indexes:
  - `simplex_fiber_by_downstairs_id`;
  - `edge_fiber_targets_by_downstairs_edge_and_source`;
- Use existing `SimplexFiberRecord` and `EdgeFiberRecord` for output records.
- Keep indexes derived from adapter and emitted simplices.

Tests:

- Downstairs 0-simplex maps to upstairs projected vertices.
- Downstairs 1-simplex maps to upstairs source-sensitive edges.

Completion:

- Lifting has explicit fiber-addressed lookup tables.

### Stage 6.2 - Lift Degree Zero

**Action 6.2.1 - Implement 0-simplex lifting**

Target files:

```text
src/jet_simplex_search/lift.py
tests/test_fiber_lift.py
```

Implementation:

- Add:

```python
def lift_zero_simplex(
    adapter: StaticTowerAdapterProtocol,
    *,
    upstairs_tier: int,
    downstairs_simplex: SimplexRecord,
) -> tuple[SimplexRecord, ...]:
    ...
```

- Require downstairs degree is 0.
- Emit one upstairs 0-simplex for every upstairs vertex projecting to the
  downstairs vertex.
- Attach upstairs tier frontier from the upstairs tier normalized graph.
- Set `projection_simplex_id`.

Tests:

- One downstairs vertex with two upstairs preimages emits two upstairs
  0-simplices.
- Projection simplex id is set.
- Frontiers are computed at upstairs tier.

Completion:

- Base case for tier descent exists.

### Stage 6.3 - Lift Higher-Degree Simplices

**Action 6.3.1 - Implement final-edge addressed extension**

Target files:

```text
src/jet_simplex_search/lift.py
tests/test_fiber_lift.py
```

Implementation:

- Add:

```python
def lift_downstairs_extension(
    *,
    adapter: StaticTowerAdapterProtocol,
    upstairs_tier: int,
    upstairs_graph: NormalizedGraph,
    downstairs_simplex: SimplexRecord,
    upstairs_prefix: SimplexRecord,
) -> tuple[SimplexRecord, ...]:
    ...
```

- Compute `alpha` from `downstairs_simplex.last_edge_ids`.
- Compute `source = upstairs_prefix.target_vertex`.
- Query adapter edge fiber targets for `(alpha, source)`.
- Intersect edge fiber targets with `upstairs_prefix.frontier`.
- Emit only targets in the intersection.
- Build face-edge witnesses at upstairs tier.
- Set `projection_simplex_id = downstairs_simplex.id`.

Tests:

- Candidate outside prefix frontier is rejected.
- Candidate not in final-edge fiber is never emitted.
- Emitted target satisfies both fiber and frontier.
- Last edge of emitted simplex projects to `alpha`.

Completion:

- The speedup is implemented at the action level:

```text
targets = edge_fiber[alpha][tgt(sigma)] cap frontier[sigma]
```

Stop conditions:

- If code enumerates all upstairs targets and projects them afterward, stop and
  rewrite to final-edge fiber targeting.

**Action 6.3.2 - Implement full degree lift over one downstairs tier**

Target files:

```text
src/jet_simplex_search/lift.py
tests/test_fiber_lift.py
```

Implementation:

- Add:

```python
def lift_tier_simplices(
    *,
    adapter: StaticTowerAdapterProtocol,
    upstairs_tier: int,
    downstairs_simplices_by_degree: Mapping[int, tuple[SimplexRecord, ...]],
    k: int,
) -> Mapping[int, tuple[SimplexRecord, ...]]:
    ...
```

- Lift degree 0 first.
- For degree `m > 0`, for each downstairs simplex, use the already-built fiber
  over its prefix.
- Emit upstairs simplices over that exact downstairs simplex.
- Record simplex fibers.
- Preserve deterministic ordering.

Tests:

- Degree 0, 1, and 2 lifts compose in order.
- Downstairs simplex with no upstairs fiber emits empty fiber record, not a
  fabricated simplex.
- Nondegenerate upstairs simplex over degenerate downstairs simplex is emitted.
- Arbitrary upstairs simplex with correct projection but not generated by the
  final-edge fiber path is not discovered through a post-filter path.

Completion:

- One tier descent works through degree `k`.

### Stage 6.4 - Orchestrate Full Static Search

**Action 6.4.1 - Implement end-to-end fake-tower search**

Target files:

```text
src/jet_simplex_search/search.py
tests/test_static_search_fake_tower.py
```

Implementation:

- Add:

```python
def run_static_small_object_search(
    adapter: StaticTowerAdapterProtocol,
    *,
    k: int,
) -> SimplexSearchResult:
    ...
```

- Select `G^ell`.
- Enumerate bottom tier directly.
- Descend tiers toward tier 0 using `lift_tier_simplices`.
- Aggregate records and diagnostics.

Tests:

- Fake tower end-to-end search emits expected bottom and upstairs simplices.
- Search respects `k`.
- Search includes degenerates.
- Search result records fibers and diagnostics.

Completion:

- Core algorithm works without real `state_collapser` dependency.

## Phase 7 - Diagnostics And Artifacts

### Stage 7.1 - Diagnostics

**Action 7.1.1 - Add diagnostics records**

Target files:

```text
src/jet_simplex_search/diagnostics.py
tests/test_diagnostics.py
```

Implementation:

- Add `SummaryStats`.
- Add `SearchDiagnostics`.
- Include:
  - simplex counts by tier and degree;
  - degenerate counts by tier and degree;
  - emitted simplex count;
  - edge fiber query count;
  - frontier size summaries if simple to collect.

Tests:

- Diagnostics from a tiny search report correct counts.
- Degenerate counts are separated from total counts.

Completion:

- Search result contains enough data to debug basic behavior.

### Stage 7.2 - Compact Artifact Writer

**Action 7.2.1 - Implement single-file JSON artifact**

Target files:

```text
src/jet_simplex_search/artifacts.py
tests/test_artifacts.py
```

Implementation:

- Add `ArtifactConfig`.
- Add:

```python
def write_search_artifact(
    result: SimplexSearchResult,
    config: ArtifactConfig,
) -> Path:
    ...
```

- Support `layout="single_json"`.
- Write `readout_source.json`.
- Serialize only JSON-compatible data.
- Include:
  - manifest;
  - tier summaries if available;
  - simplex records;
  - simplex fibers;
  - edge fibers;
  - diagnostics.

Tests:

- Artifact file writes.
- Artifact reloads as JSON.
- Every simplex has required traceability fields.
- No live `state_collapser` object is serialized.

Completion:

- Tiny examples and unit tests can produce a source artifact.

### Stage 7.3 - Manifest-Plus-Table Artifact Layout

**Action 7.3.1 - Implement manifest table writer**

Target files:

```text
src/jet_simplex_search/artifacts.py
tests/test_artifacts.py
```

Implementation:

- Support `layout="manifest_tables"`.
- Write:

```text
readout_source.json
simplex_records.jsonl
simplex_fibers.jsonl
edge_fibers.jsonl
diagnostics.json
```

- Put table paths and counts in `readout_source.json`.
- Sort rows deterministically.

Tests:

- All expected files are written.
- Manifest table paths exist.
- Counts match JSONL row counts.
- Empty fiber tables are represented correctly.

Completion:

- Serious first-scope artifact layout is available.

Stop conditions:

- If artifact writing requires large-storage choices such as compression,
  SQLite, or DuckDB, stop and defer; those are future design tracks.

## Phase 8 - Public API

### Stage 8.1 - Build Search Context API

**Action 8.1.1 - Add `build_static_search_context`**

Target files:

```text
src/jet_simplex_search/api.py
tests/test_api.py
```

Implementation:

- Add a context builder that accepts a `GraphInput`, `k`, and adapter or schema
  dependency appropriate to the phase.
- In fake-adapter phase, it may accept an adapter directly.
- In real integration phase, it should build adapter from graph and
  `state_collapser` schema.

Tests:

- Invalid `k` fails.
- Valid fake context builds.

Completion:

- Public API starts as a thin wrapper over implemented internals.

### Stage 8.2 - Add `search_simplices`

**Action 8.2.1 - Add top-level search function**

Target files:

```text
src/jet_simplex_search/api.py
tests/test_api.py
```

Implementation:

- Add:

```python
def search_simplices(...) -> SimplexSearchResult:
    ...
```

- Keep the signature aligned with the blueprint once real `state_collapser`
  integration exists.
- Delegate to `run_static_small_object_search`.
- Write artifacts only when `artifact_config` is provided.

Tests:

- Search returns `SimplexSearchResult`.
- Search optionally writes artifact.
- Top-level function does not broaden output semantics.

Completion:

- Small public entrypoint exists.

**Action 8.2.2 - Export public API deliberately**

Target files:

```text
src/jet_simplex_search/__init__.py
tests/test_package.py
```

Implementation:

- Export `__version__`.
- Consider exporting `search_simplices` only after API tests pass.
- Keep internal records unexported unless needed.

Tests:

- Import smoke still passes.
- Public API imports pass if exported.

Completion:

- Public API is small and intentional.

## Phase 9 - Real state_collapser Integration

### Stage 9.1 - Add Dependency

**Action 9.1.1 - Decide dependency source**

Target files:

```text
pyproject.toml
uv.lock
docs/design/initial_design/01_004_static_tower_small_object_implementation_log.md
```

Procedure:

- Determine whether `state_collapser` is available as an installable package or
  must be referenced by local path during development.
- Record decision in implementation log.
- Add dependency using `uv` according to repo policy.

Tests:

```text
uv run python -c "import state_collapser; print(state_collapser.__version__)"
uv run pytest
```

Completion:

- `state_collapser` is importable in this package environment.

Stop conditions:

- If dependency resolution requires network or private path approval, request
  approval through the tool escalation path.

### Stage 9.2 - Implement Real Adapter

**Action 9.2.1 - Map graph records to state_collapser records**

Target files:

```text
src/jet_simplex_search/tower_adapter.py
tests/integration/test_state_collapser_static_tower.py
```

Implementation:

- Convert `InputVertex` or normalized vertices into `state_collapser.core.State`.
- Convert normalized edges into `state_collapser.core.BaseEdge`.
- Use stable identities based on local ids.
- Preserve original/identity labels.
- Do not collapse identity and original edge labels.

Tests:

- Tiny graph maps to expected `State` and `BaseEdge` identities.
- Identity edges have distinct labels.

Completion:

- Local graph can become a `state_collapser` graph snapshot.

**Action 9.2.2 - Build static PartitionTower**

Target files:

```text
src/jet_simplex_search/tower_adapter.py
tests/integration/test_state_collapser_static_tower.py
```

Implementation:

- Use `state_collapser` static tower construction APIs.
- Prefer `PartitionTower` / `build_partition_tower_full` surfaces documented by
  `state_collapser`.
- Do not use dynamic `TowerRuntime` as the core algorithm.

Tests:

- Tiny graph builds tower.
- Adapter exposes tier list.
- Adapter exposes vertices and edges for tier.

Completion:

- Real static tower integration works.

Stop conditions:

- If a needed query is absent from `state_collapser`, inspect `state_collapser`
  source/tests before writing any semantic workaround.

**Action 9.2.3 - Implement real projection and edge-fiber queries**

Target files:

```text
src/jet_simplex_search/tower_adapter.py
tests/integration/test_state_collapser_static_tower.py
```

Implementation:

- Implement:
  - `project_vertex`;
  - `project_edge`;
  - `edge_fiber_targets`;
  - `bottommost_nondegenerate_tier`.
- Use `state_collapser` tower data as source of truth.
- Keep local lookup tables as derived caches only.

Tests:

- Simple contraction maps multiple upstairs vertices to one downstairs cell.
- Downstairs identity fiber includes formal identities.
- Downstairs degenerate simplex can have nondegenerate upstairs lift.

Completion:

- Real adapter supports the same tests as fake adapter plus integration
  examples.

## Phase 10 - Documentation And Examples

### Stage 10.1 - README Tiny Example

**Action 10.1.1 - Add minimal usage example**

Target files:

```text
README.md
```

Implementation:

- Add a tiny graph example after API exists.
- Show `k`.
- Show call to `search_simplices`.
- Show count output only; do not overpromise performance.

Tests:

- If example is code-block testable, add a small test or keep it clearly
  illustrative.

Completion:

- README reflects actual implemented API.

### Stage 10.2 - Link Design Docs

**Action 10.2.1 - Add docs index links**

Target files:

```text
README.md
docs/design/initial_design/01_004_static_tower_small_object_implementation_log.md
```

Implementation:

- Link:
  - source design note;
  - package blueprint;
  - implementation workplan;
  - implementation log.

Completion:

- A new engineer can find the execution spine.

## Phase 11 - Final Verification

### Stage 11.1 - Full Test Suite

**Action 11.1.1 - Run full tests**

Target files:

```text
none
```

Command:

```text
uv run pytest
```

Completion:

- Full suite passes.

Stop conditions:

- If tests fail, fix only in-scope failures.
- If failure reveals a design conflict, stop and update docs before code.

### Stage 11.2 - Invariant Review

**Action 11.2.1 - Review implementation against checklist**

Target files:

```text
docs/design/initial_design/01_002_static_tower_small_object_package_blueprint.md
docs/design/initial_design/01_004_static_tower_small_object_implementation_log.md
```

Procedure:

- Verify Abdul Malik attribution remains intact.
- Verify `state_collapser` owns tower semantics.
- Verify graph normalization emits exactly one identity per vertex.
- Verify directed flag condition requires all face edges.
- Verify degenerates are first-class records.
- Verify `F(sigma)` recurrence is used.
- Verify bottom-tier enumeration includes degenerates through `k`.
- Verify tower descent searches only over known downstairs simplex fibers.
- Verify final-edge fiber targeting is enforced.
- Verify artifacts trace every simplex to witnesses and projection/fiber data.

Completion:

- Implementation log records checklist status.

### Stage 11.3 - Artifact Smoke

**Action 11.3.1 - Generate and inspect tiny artifact**

Target files:

```text
artifacts or temporary test output directory
```

Procedure:

- Run a tiny graph search with artifact output.
- Inspect JSON/JSONL source artifact.
- Confirm counts and traceability fields are present.

Completion:

- Artifact format works on a tiny example.

Stop conditions:

- If artifact schema differs from blueprint, either fix code or explicitly
  update design docs with PO approval.

## Phase 12 - Future Deferral Register

### Stage 12.1 - Record Deferred Work

**Action 12.1.1 - Keep deferred tracks out of first implementation**

Target files:

```text
docs/design/initial_design/01_004_static_tower_small_object_implementation_log.md
```

Procedure:

- Record the following as deferred:
  - Kan replacement;
  - meaningful non-identity input loops;
  - one simplex per multigraph witness choice;
  - compressed/SQLite/DuckDB artifact storage;
  - bitset/CSR/GPU/tensor acceleration;
  - multiprocessing.

Completion:

- First implementation scope remains clean.

## Completion Definition

The first implementation is complete when:

- `uv run pytest` passes;
- bottom-tier direct enumeration works through `k`;
- degenerate simplices are emitted as first-class records;
- fake-tower fiber-addressed lifting works;
- real `state_collapser` adapter works if Phase 9 is included in approved
  scope;
- artifacts write and reload;
- README reflects only actual implemented behavior;
- implementation log records verification results.

## Required Stop-And-Reconstruct Events

Stop implementation and reconstruct reality from files/tests/docs if any of the
following occur:

- `state_collapser` API differs from remembered API;
- a tower query gives surprising tier ordering;
- identity loops behave differently at quotient tiers than expected;
- simplex records cannot trace face-edge witnesses;
- fiber lift requires post-filtering to pass tests;
- tests pass only by weakening directed flag semantics;
- artifact writing requires unplanned storage architecture;
- Kan/horn-filling concerns start changing small-object implementation.

