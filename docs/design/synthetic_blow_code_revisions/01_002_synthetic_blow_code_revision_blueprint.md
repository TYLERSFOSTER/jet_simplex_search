# Synthetic Blow Review Code Revision Blueprint

## Status

This blueprint derives from:

```text
code_review/01_002_synthetic_blow_project_review.md
docs/design/synthetic_blow_code_revisions/01_001_synthetic_blow_code_revision_scope.md
```

It is a package blueprint for the approved revision work. It is not an
implementation patch and not yet a Phase.Stage.Action implementation workplan.

## Purpose

The approved review says the package is close, but the remaining release risk is
that several important invariants are either enforced too late, exposed through
ambiguous public API surfaces, or preserved by convention instead of explicit
records and tests.

This blueprint turns those review findings into a coherent revision design.

The revision has one governing standard:

```text
Every emitted simplex record has truthful witnesses.
Every lift is searched only over an existing downstairs simplex fiber.
Every expanded H-lift count is traceable to vertex and edge fiber factors.
Every quotient tier used for the next quotient step is clean under the same
simple-reflexive semantics that simplex search assumes.
```

## Attribution

The static quotient-tower simplex search algorithm is PM Abdul Malik's work and
part of his thesis. This includes:

- degree-wise simplex enumeration;
- cached frontier recurrence;
- formal identity handling for degenerate skeleton addresses;
- static quotient tower construction;
- small-object fiber-addressed lift search over existing downstairs simplices.

The Project Owner clarified the package pipeline:

```text
study H
  -> clean / skeletonize to G
  -> build the clean tower G^bullet
  -> search simplices in G^bullet
  -> perform multiplicity / etale H-lift accounting
```

This blueprint keeps that pipeline as the organizing spine.

## Current Reality Snapshot

### Current Package State

The current `jet_simplex_search` package already contains the main pieces:

- `src/jet_simplex_search/api.py`
  - `search_simplices` is the public entry point.
  - `search_skeleton_simplices` already exists as a lower-level helper.
  - `SearchWithHLiftsResult` still lives in `api.py`.
  - `search_simplices` still accepts both `adapter` and `graph` keyword shapes.
  - `search_simplices(adapter=...)` still returns `SimplexSearchResult`.
  - `search_simplices(graph=...)` returns `SearchWithHLiftsResult`.

- `src/jet_simplex_search/skeleton.py`
  - `skeletonize_graph` realizes arbitrary H as a simple loop-free skeleton G.
  - Parallel non-loop H edges collapse by endpoint pair.
  - Input H loops become loop fibers, not skeleton edges.
  - The only label policy is `SkeletonLabelPolicy.REQUIRE_IDENTICAL`.

- `src/jet_simplex_search/tower_adapter.py`
  - `StateCollapserStaticTowerAdapter` adapts `state_collapser`'s
    `PartitionTower`.
  - `from_graph` normalizes a graph and calls
    `state_collapser.tower.partition.tower.build_partition_tower_full`.
  - `tier_edges` exposes a simple endpoint-pair view by collapsing action cells
    after the tower has already been constructed.
  - `edge_fiber_targets` is indexed and no longer performs whole-tier scans on
    every query.

- `src/jet_simplex_search/search.py`
  - `enumerate_direct_simplices` enforces simple-reflexive normalized tier
    graphs.
  - Degenerate simplices are generated uniformly through formal identities.
  - `run_static_small_object_search` enumerates the bottom tier directly and
    lifts upward one tier at a time.

- `src/jet_simplex_search/lift.py`
  - Lifting is fiber-addressed by existing downstairs simplices.
  - A degree `m + 1` upstairs simplex is searched only over a degree `m + 1`
    downstairs simplex.
  - Final-edge fiber lookup is explicit.

- `src/jet_simplex_search/h_lift.py`
  - Tier-0 skeleton simplices receive compressed H-lift counts.
  - Non-loop faces multiply by skeleton edge-fiber size.
  - Degenerate faces multiply by actual H loop-fiber size.
  - Degree-0 simplices have H-lift count 1.

- `src/jet_simplex_search/artifacts.py`
  - Artifact writing supports single JSON and manifest-table layouts.
  - Combined H-to-G results are detected by duck typing.
  - `write_search_artifact` accepts `object`.

- `pyproject.toml`
  - Runtime dependency is `state-collapser`.
  - `tool.uv.sources` still points to `../state_collapser`.
  - Dev dependency group currently includes `pytest`.

- `README.md`
  - README presents the package as pre-release library software.
  - It still documents sibling checkout installation.
  - It still links an internal continuity-report path that does not exist at the
    linked location.

### Current Adjacent `state_collapser` State

The adjacent `state_collapser` checkout is version `0.7.2` and has local tags:

```text
v0.6.0
v0.7.0
v0.7.1
v0.7.2
```

The relevant state-collapser builder is:

```text
state_collapser.tower.partition.tower.build_partition_tower_full
```

Current observed properties:

- `PartitionTower.initialize` registers base states and base edges once.
- `SchemaAssignmentStore` assigns discovered base edge ids to schema blocks.
- The full tower applies schema blocks in order over that persistent base-edge
  registry.
- `ActionPartitionLayer.rebuild_action_cells_for_collection` groups live edges
  by source cell, target cell, and primitive action identity.
- Internal edges are dropped from the live outgoing surface by loop policy.
- The tower can read action-cell members and projected state cells, but it does
  not currently reify a cleaned quotient graph as the input graph for the next
  schema block.

This matters because the JSS algorithm needs a clean quotient tier before the
next quotient step. The current adapter can expose each completed tier as a
simple endpoint-pair view, but the state-collapser tower may already have used
unclean action-cell data while constructing later tiers.

## Target Pipeline

The target package pipeline is:

```text
GraphInput H
  -> validate H
  -> skeletonize H into clean graph G_0
       vertices: same vertex ids as H
       non-loop edges: one edge per ordered endpoint pair
       loops: stored as H loop fibers only
       parallel H edges: stored as H edge fibers only
  -> build clean static quotient tower G^bullet
       every tier G_i is simple and loop-free as stored graph data
       formal identities are added only by the simplex engine
       G_{i+1} is cleaned before constructing G_{i+2}
       projections G_i -> G_{i+1} are recorded explicitly
  -> run static small-object simplex search over G^bullet
       bottom tier direct enumeration
       upward lift search only over existing downstairs simplices
       final-edge fiber lookup cuts candidate targets before frontier check
  -> compute compressed H-lifts for tier-0 skeleton simplices
       input loops and parallel edges reappear as multiplicities
       formal identities do not pretend to be H loops
  -> optionally write typed JSON/JSONL artifacts
```

## Design Decision: Clean Tower Ownership

The approved review left Stream 1 with three possible ownership models:

1. Add simple-reflexive quotient-realization support inside `state_collapser`.
2. Make `jet_simplex_search` orchestrate the tower one quotient step at a time.
3. Use a short-term JSS bridge and follow up with a state-collapser primitive.

### Recommendation

Use option 3.

For this revision, implement a JSS-owned clean tower adapter that uses
`state_collapser` as a one-block quotient engine and explicitly realizes each
quotient tier as a clean JSS graph before the next step.

Separately, record the state-collapser follow-up as a later upstream cleanup:
`state_collapser` should eventually expose this as a first-class simple
quotient-realization tower mode or one-step quotient API.

### Why This Recommendation

The current state-collapser `PartitionTower` is optimized around a persistent
base-edge registry. That is the correct shape for runtime/control use cases, but
it is not the same semantic object as the JSS clean quotient tower.

JSS needs this object:

```text
G_0 -> G_1 -> G_2 -> ... -> G_ell
```

where each `G_i` is a realized simple graph and `G_{i+1}` is computed from the
clean `G_i`, not from the original base graph seen through a later partition.

The current `PartitionTower` instead stores:

```text
base graph registry
  + nested state partition layers
  + nested action partition layers
```

Those layers are useful, but they do not by themselves guarantee that the next
schema block is applied to a cleaned quotient graph.

A JSS bridge is therefore the smallest correct release move:

- It does not require editing the adjacent package during this revision.
- It can preserve the current public dependency on `state_collapser`.
- It can be tested entirely from the JSS repo.
- It gives the PO's intended semantics now.
- It provides an executable specification for a future state-collapser API.

### What The Bridge Must Not Do

The bridge must not merely call the existing full tower and collapse tier edges
afterward. That is the reviewed problem.

The bridge must not silently merge quotient edges with conflicting
schema-relevant labels. If a clean quotient edge cannot be assigned an honest
label payload under the v0.1 policy, it must fail loudly.

The bridge must not make simplex search dynamic. The clean tower is built once,
stored, and then searched statically.

## Stream 1 Blueprint: Clean Static Tower Construction

### Target Module

Add a new module:

```text
src/jet_simplex_search/clean_tower.py
```

This module owns JSS clean quotient tower realization. It should not own
simplex enumeration, H-lift accounting, or artifact writing.

### Target Public/Internal Surface

Proposed classes:

```python
@dataclass(frozen=True, slots=True)
class CleanTowerConfig:
    label_policy: SkeletonLabelPolicy = SkeletonLabelPolicy.REQUIRE_IDENTICAL
    stop_at_singleton: bool = True
    max_tiers: int | None = None


@dataclass(frozen=True, slots=True)
class CleanTierProjection:
    upstairs_tier: int
    downstairs_tier: int
    vertex_projection: Mapping[str, str]
    edge_projection: Mapping[str, str]
    edge_fiber_targets: Mapping[tuple[str, str], frozenset[str]]


@dataclass(frozen=True, slots=True)
class CleanTower:
    tier_graphs: tuple[GraphInput, ...]
    projections: tuple[CleanTierProjection, ...]
    diagnostics: CleanTowerDiagnostics


@dataclass(frozen=True, slots=True)
class CleanStaticTowerAdapter:
    clean_tower: CleanTower
```

The adapter implements `StaticTowerAdapterProtocol`:

```python
tiers() -> tuple[int, ...]
bottommost_nondegenerate_tier() -> int
tier_vertices(tier) -> tuple[str, ...]
tier_edges(tier) -> tuple[str, ...]
edge_source(tier, edge_id) -> str
edge_target(tier, edge_id) -> str
project_vertex(tier, vertex_id) -> str
project_edge(tier, edge_id) -> str
edge_fiber_targets(upstairs_tier, downstairs_edge_id, upstairs_source_id)
tier0_vertex_id_to_input_vertex_id()
```

### Construction Function

Proposed builder:

```python
def build_clean_static_tower(
    graph: GraphInput,
    *,
    schema: object | None = None,
    config: CleanTowerConfig | None = None,
) -> CleanTower:
    ...
```

Proposed adapter constructor:

```python
@classmethod
def from_graph(
    cls,
    graph: GraphInput,
    *,
    schema: object | None = None,
    config: CleanTowerConfig | None = None,
) -> CleanStaticTowerAdapter:
    ...
```

### Tier Data Semantics

Stored tier graphs must be loop-free simple directed graphs.

Formal identities are not stored as graph edges. They are introduced by
`normalize_graph` when simplex search asks for a normalized tier view.

Each stored graph must satisfy:

```text
for every edge e:
  source(e) != target(e)

for every ordered pair (u, v), u != v:
  at most one stored edge u -> v
```

### Tier-0 Semantics

When the public H workflow is used:

```text
H -> skeletonize_graph(H) -> skeleton_graph G_0
```

The clean tower builder receives `G_0`, not raw H.

Tier-0 vertex ids should be stable and should map back to original H vertex ids.
In the default H workflow, this mapping is identity at the payload level:

```text
tier0 adapter vertex id -> H input vertex id
```

The current state-collapser adapter uses `cell:0:n` ids at tier 0. The clean
tower adapter does not have to preserve those ids. It may use original vertex ids
directly at tier 0, which is simpler and more transparent. If it does so,
`tier0_vertex_id_to_input_vertex_id` is exactly:

```text
{vertex_id: vertex_id for vertex_id in G_0.vertices}
```

This would simplify H-lift mapping and artifacts.

### One-Step Quotient Semantics

For each contraction step:

1. Start with clean current graph `G_i`.
2. Convert vertices of `G_i` to state-collapser `State` objects.
3. Convert non-loop edges of `G_i` to state-collapser `BaseEdge` objects.
4. Select exactly one contraction block for this step.
5. Build a temporary state-collapser tower for that single block.
6. Read the quotient state partition at the next tier.
7. Project each current vertex into its quotient state cell.
8. Project each current edge by projected endpoints.
9. If projected endpoints are equal, record edge projection to the formal
   identity of the quotient vertex and do not store a non-loop quotient edge.
10. If projected endpoints are different, group edge images by ordered quotient
    endpoint pair.
11. Clean grouped quotient edges into one quotient graph edge per endpoint pair.
12. Record edge-fiber targets for lifting from `G_i` to `G_{i+1}`.
13. Repeat using the cleaned quotient graph as the next current graph.

### Schema Block Planning

This is the hard part and must be explicit.

State-collapser schemas assign edges to blocks:

```python
schema.assign_edge(edge_id, registry) -> SchemaBlockId | None
schema.ordered_blocks() -> tuple[SchemaBlockId, ...]
```

In the clean tower builder, schema assignment must happen against the current
clean graph at each step, not against the original tier-0 graph for all time.

Proposed helper module section:

```python
def schema_blocks_for_current_graph(
    schema: ContractionSchema | None,
    current_edges: tuple[BaseEdge, ...],
    registry: BaseGraphRegistry,
) -> tuple[SchemaBlockId, ...]:
    ...
```

Rules:

- If `schema is None`, there are no contraction blocks.
- If `schema.ordered_blocks()` is nonempty, use those blocks in declared order.
- If `schema.ordered_blocks()` is empty but `assign_edge` returns blocks, derive
  deterministic discovered blocks from current edge assignment order.
- Skip a block for a tier if it schedules no current clean edges, unless a later
  test proves empty-block carry-forward tiers are useful.
- Stop when no block schedules any edge.
- Stop if the current clean graph has one or zero vertices and
  `stop_at_singleton=True`.

### One-Block Schema Wrapper

The temporary state-collapser tower should receive a schema wrapper that
contracts only the selected current block.

Concept:

```python
@dataclass(frozen=True, slots=True)
class SingleBlockContractionSchema:
    delegate: ContractionSchema
    selected_block_id: SchemaBlockId

    def assign_edge(self, edge_id, registry):
        block_id = self.delegate.assign_edge(edge_id, registry)
        if block_id == self.selected_block_id:
            return self.selected_block_id
        return None

    def ordered_blocks(self):
        return (self.selected_block_id,)
```

This lets state-collapser perform exactly one quotient step while JSS owns the
cleaning and reification between steps.

### Quotient Vertex Ids

Quotient vertex ids should be deterministic and stable.

Recommended id shape:

```text
jss:tier-vertex:t{tier}:members[{escaped member ids...}]
```

But this may get long. A simpler release-safe shape is:

```text
cell:{tier}:{ordinal}
```

The important requirement is not human readability. It is stable ordering,
projection traceability, and no accidental collisions.

Recommended compromise:

- Use `cell:{tier}:{ordinal}` for ids.
- Store diagnostics or optional provenance mapping from each quotient vertex id
  to its previous-tier member vertex ids.
- Sort quotient cells by sorted previous-tier member vertex ids before assigning
  ordinals.

### Quotient Edge Ids

Use the existing helper:

```python
tier_simple_edge_id(tier, source, target)
```

This keeps tier edge ids endpoint-addressed and stable.

### Projection Records

For each adjacent tier pair, store:

```text
upstairs_tier = i
downstairs_tier = i + 1
vertex_projection[upstairs_vertex_id] = downstairs_vertex_id
edge_projection[upstairs_edge_id] = downstairs_edge_id or identity_edge_id(downstairs_vertex_id)
edge_fiber_targets[(downstairs_edge_id, upstairs_source_id)] = frozenset(upstairs target ids)
```

This directly supports the existing lift engine:

```text
for known downstairs simplex tau:
  for upstairs prefix sigma over partial tau:
    targets =
      edge_fiber_targets[(last_edge(tau), tgt(sigma))]
      intersect sigma.frontier
```

### Label Compatibility Policy For Clean Quotient Edges

Release v0.1 should keep the strict policy:

```text
When multiple current-tier edges project to one quotient endpoint pair, their
labels must be identical.
```

If labels differ, fail with a clear error:

```text
Clean quotient edge label conflict for quotient pair (U, V).
Edges e1, e2 project to the same clean edge but have different labels.
The v0.1 clean tower builder requires identical labels for collapsed quotient
edges. Use a schema/label policy that keeps this quotient edge unambiguous.
```

Why strictness is correct for this release:

- It matches the current H-to-G skeleton label policy.
- It prevents a clean quotient edge from lying about what it represents.
- It avoids silently destroying schema-relevant label data.
- It forces the contraction-schema complication into the open instead of
  encoding an accidental aggregation rule.

Future possible policies, explicitly not in this revision:

- label union;
- label intersection;
- schema-relevant label projection;
- user callback aggregation;
- unlabeled quotient realization.

### Diagnostics

Add `CleanTowerDiagnostics`:

```python
@dataclass(frozen=True, slots=True)
class CleanTowerDiagnostics:
    tier_count: int
    vertex_count_by_tier: Mapping[int, int]
    edge_count_by_tier: Mapping[int, int]
    collapsed_loop_count_by_step: Mapping[int, int]
    collapsed_parallel_edge_count_by_step: Mapping[int, int]
    maximum_edge_fiber_size_by_step: Mapping[int, int]
    skipped_empty_block_count: int
    stopped_because_singleton: bool
```

Diagnostics should be JSON-safe via `to_dict`.

### Adapter Relationship To Existing `StateCollapserStaticTowerAdapter`

Do not delete `StateCollapserStaticTowerAdapter` in the first implementation
pass. It is useful as:

- an integration harness for current state-collapser partition tower behavior;
- a comparison adapter while the clean tower builder is introduced;
- a fallback for tests explicitly exercising the raw adapter boundary.

But the public H workflow should switch to the clean adapter:

```text
search_simplices(graph=H, ...)
  -> skeletonize H
  -> CleanStaticTowerAdapter.from_graph(skeleton_graph, schema=...)
  -> run_static_small_object_search
```

The lower-level skeleton/tower workflow can accept either adapter type because
it depends on `StaticTowerAdapterProtocol`.

### Tests For Stream 1

Add tests in:

```text
tests/test_clean_tower.py
tests/integration/test_clean_state_collapser_tower.py
```

Required cases:

1. No schema:
   - input clean graph remains one tier;
   - tier 0 vertices and edges match input;
   - identities are not stored but appear through `normalized_graph_for_tier`.

2. Single contraction block:
   - edge `a -> b` in block collapses `a` and `b`;
   - non-loop projected edge `a -> d` and `b -> d` collapse to one quotient edge
     if labels agree;
   - internal edge `a -> b` projects to identity downstairs;
   - edge fiber over downstairs identity includes nonidentity upstairs edge.

3. Multi-step clean quotient:
   - first block creates a quotient tier with parallel raw edges;
   - clean realization collapses them before the second block;
   - second block runs on the cleaned quotient graph;
   - emitted tier sequence differs from raw adapter-side simplification if raw
     multiplicity would have survived.

4. Label conflict:
   - two edges project to the same quotient endpoint pair with different labels;
   - builder raises the JSS graph/tower error;
   - error message names endpoint pair and policy.

5. Edge fiber targets:
   - for each projection step, `edge_fiber_targets` is source-sensitive;
   - querying a downstream edge from an unrelated upstairs source returns empty.

6. Static search integration:
   - `run_static_small_object_search(CleanStaticTowerAdapter, k=2)` works;
   - the missing-downstairs-interior invariant still holds.

7. H workflow integration:
   - `search_simplices(graph=H, ...)` uses clean tower semantics;
   - tier-0 H-lift counts are unchanged by the adapter switch.

## Stream 2 Blueprint: Public API And Result Boundary

### Target Module

Add:

```text
src/jet_simplex_search/results.py
```

Move:

```text
SearchWithHLiftsResult
```

out of `api.py` into `results.py`.

### Target Result Types

`results.py` should contain:

```python
@dataclass(frozen=True, slots=True)
class SearchWithHLiftsResult:
    k: int
    skeletonization: SkeletonizationResult
    skeleton_search: SimplexSearchResult
    h_lifts: tuple[SimplexHLiftRecord, ...]
    h_lift_diagnostics: HLiftDiagnostics
```

Optional but useful:

```python
SearchResult = SimplexSearchResult | SearchWithHLiftsResult
```

### Public Function Contract

`search_simplices` should mean the full H workflow.

Target signature:

```python
def search_simplices(
    *,
    graph: GraphInput,
    contraction_schema: object | None = None,
    k: int,
    artifact_config: ArtifactConfig | None = None,
) -> SearchWithHLiftsResult:
    ...
```

Rules:

- `graph` is required.
- `adapter` is not accepted.
- The function always returns `SearchWithHLiftsResult`.
- It runs skeletonization, clean tower construction, skeleton search, H-lift
  computation, and optional artifact writing.

### Lower-Level Function Contract

`search_skeleton_simplices` remains available for tests and advanced use.

Target signature:

```python
def search_skeleton_simplices(
    *,
    adapter: StaticTowerAdapterProtocol | None = None,
    graph: GraphInput | None = None,
    contraction_schema: object | None = None,
    k: int,
    artifact_config: ArtifactConfig | None = None,
) -> SimplexSearchResult:
    ...
```

Rules:

- Exactly one of `adapter` or `graph` must be provided.
- If `adapter` is provided, use it directly.
- If `graph` is provided, treat it as an already-clean skeleton graph and build
  a clean static tower adapter from it.
- The function always returns `SimplexSearchResult`.
- It never computes H-lifts.

### Context Helper Decision

Delete `StaticSearchContext` and `build_static_search_context` unless tests or
smoke scripts prove they are externally useful.

Current reality:

- `StaticSearchContext` just stores adapter and k.
- `build_static_search_context` mostly validates k and constructs an adapter.
- It is not a meaningful abstraction yet.

Replacement:

```python
def _resolve_skeleton_adapter(...):
    ...
```

Keep this helper private if needed.

### Compatibility And Deprecation

Because this is still pre-release, it is acceptable to make the API sharper
without a long deprecation period.

However, README, smoke scripts, and tests must be updated together.

Expected break:

```python
search_simplices(adapter=FakeStaticTowerAdapter(), k=1)
```

Replacement:

```python
search_skeleton_simplices(adapter=FakeStaticTowerAdapter(), k=1)
```

### Tests For Stream 2

Update:

```text
tests/test_api.py
```

Required cases:

1. `search_simplices(graph=..., k=...)` returns `SearchWithHLiftsResult`.
2. `search_simplices` without graph raises `TypeError`.
3. `search_simplices(adapter=...)` raises `TypeError` because `adapter` is not a
   valid keyword.
4. `search_skeleton_simplices(adapter=..., k=...)` returns `SimplexSearchResult`.
5. `search_skeleton_simplices(graph=..., k=...)` returns `SimplexSearchResult`.
6. `search_skeleton_simplices(adapter=..., graph=..., k=...)` raises a clear
   `TypeError`.
7. Artifact writing works for both public and skeleton-only workflows.

## Stream 3 Blueprint: Artifact Writer Type Discipline

### Target Change

Change:

```python
def write_search_artifact(result: object, config: ArtifactConfig) -> Path:
```

to:

```python
def write_search_artifact(
    result: SimplexSearchResult | SearchWithHLiftsResult,
    config: ArtifactConfig,
) -> Path:
```

### Result Branching

Replace:

```python
_is_combined_result(result)
```

with:

```python
isinstance(result, SearchWithHLiftsResult)
```

Keep:

```python
isinstance(result, SimplexSearchResult)
```

for skeleton-only results.

### Artifact Function Split

Current `artifacts.py` mixes object handling with payload generation.

Target helpers:

```python
def _result_payload(
    result: SimplexSearchResult | SearchWithHLiftsResult,
    config: ArtifactConfig,
) -> dict[str, object]:
    ...

def _combined_result_payload(
    result: SearchWithHLiftsResult,
    config: ArtifactConfig,
) -> dict[str, object]:
    ...

def _simplex_search_payload(
    result: SimplexSearchResult,
    config: ArtifactConfig,
) -> dict[str, object]:
    ...
```

Target manifest helpers:

```python
def _manifest_payload(
    result: SimplexSearchResult | SearchWithHLiftsResult,
    config: ArtifactConfig,
) -> dict[str, object]:
    ...

def _simplex_manifest_payload(...)
def _combined_manifest_payload(...)
```

Target diagnostics helpers:

```python
def _combined_diagnostics_payload(result: SearchWithHLiftsResult) -> dict[str, object]
def _diagnostics_payload(result: SimplexSearchResult) -> dict[str, object]
```

### Expanded H-Lift Witness Config

Current:

```python
include_expanded_h_lift_witnesses: bool = False
max_expanded_h_lift_witnesses: int = 100_000
```

`include_expanded_h_lift_witnesses=True` raises. The max field is unused.

Revision options:

1. Delete `max_expanded_h_lift_witnesses` until expanded witnesses exist.
2. Keep it but only if a test confirms it is intentionally reserved and appears
   in manifest metadata.

Recommendation:

Delete it for now. It is not release behavior.

### Artifact Schema Versions

Keep schema behavior:

```text
schema_version = 1 for SimplexSearchResult
schema_version = 2 for SearchWithHLiftsResult
```

Add explicit `result_kind` for both:

```text
simplex_search
skeleton_search_with_h_lifts
```

This makes downstream artifact consumers less dependent on schema version alone.

### Tests For Stream 3

Update:

```text
tests/test_artifacts.py
```

Required cases:

1. Passing `SimplexSearchResult` writes schema version 1.
2. Passing `SearchWithHLiftsResult` writes schema version 2.
3. Passing an arbitrary object raises `ArtifactWriteError`.
4. Manifest-table layout includes all expected combined tables.
5. Combined diagnostics include skeletonization, skeleton search, and H-lifts.
6. `include_expanded_h_lift_witnesses=True` still raises.
7. Deleted config field is not referenced by tests or docs.

## Stream 4 Blueprint: Release-Facing Dependency And Documentation Drift

### Dependency Target

Current:

```toml
[tool.uv.sources]
state-collapser = { path = "../state_collapser", editable = true }
```

Observed adjacent state-collapser version:

```text
0.7.2
```

Observed adjacent local tag:

```text
v0.7.2
```

Target release dependency:

```toml
dependencies = [
  "state-collapser @ git+https://github.com/TYLERSFOSTER/state_collapser.git@v0.7.2",
]
```

Or, if the package is published to PyPI before JSS release:

```toml
dependencies = [
  "state-collapser==0.7.2",
]
```

This blueprint recommends the GitHub tag form because the Project Owner already
asked to use the actual state-collapser release on GitHub.

### Development Dependency Target

Keep local-development instructions out of the primary install path.

If local source overrides are needed for development, move them to a
contributor/development note, for example:

```text
docs/development/local_state_collapser_source.md
```

or leave them as an optional comment in release-prep docs, not root README.

### README Target

Root README should:

- keep the existing logo and title;
- keep the professional package framing;
- document public install path;
- keep quick start runnable;
- remove the root engineering continuity report link;
- not link `docs/prime_directive`;
- not link the release-prep plan;
- preserve PM Abdul Malik attribution;
- include a short Known Limitations section separate from release status.

### Pyproject Target

Add or verify:

- project URLs;
- classifiers;
- `ruff` dev dependency;
- ruff config;
- package metadata stays version `0.1.0` unless release version changes are
  separately approved.

Keep Python range:

```toml
requires-python = ">=3.11,<3.13"
```

unless tests prove a wider range.

### Tests For Stream 4

Add:

```text
tests/test_release_metadata.py
tests/test_readme_quickstart.py
```

Required cases:

1. `pyproject.toml` has no local path dependency under release mode.
2. `README.md` does not link the old continuity report path.
3. README quick-start imports work.
4. README quick-start result shape is current.
5. Package version in `__init__.py` matches `pyproject.toml`.

## Stream 5 Blueprint: Skeleton Label Policy Documentation

### Current Behavior

`SkeletonLabelPolicy.REQUIRE_IDENTICAL` is the only supported policy.

Current behavior:

- Parallel H edges with identical labels collapse to one skeleton edge.
- Parallel H edges with different labels raise `InvalidGraphError`.

### Target Behavior

Keep current behavior.

Make the policy explicit in:

- `SkeletonLabelPolicy` docstring;
- `skeletonize_graph` docstring;
- README known limitations or API notes;
- tests.

### Target Text Semantics

The policy means:

```text
If multiple H edges are represented by one skeleton G edge, the skeleton edge
may carry labels only when all represented H edges carry the exact same label
tuple. Otherwise JSS refuses to choose a label for the quotient edge.
```

This is a correctness choice, not a missing convenience feature.

### Tests For Stream 5

Existing tests already cover:

- identical labels pass;
- different labels fail.

Add or update one test name/docstring to say this is the v0.1 label policy.

Possible test:

```python
def test_v01_label_policy_requires_exact_parallel_edge_label_agreement() -> None:
    ...
```

## Stream 6 Blueprint: Dead Code And Stale Cache Cleanup

### Cleanup Candidates

Delete unless current source reality changes before implementation:

```text
src/jet_simplex_search/ids.py:fiber_id
src/jet_simplex_search/tower_adapter.py:_simple_edge_action_ids_cache
src/jet_simplex_search/tower_adapter.py:_edge_id_to_action_cell
ArtifactConfig.max_expanded_h_lift_witnesses
StaticSearchContext
build_static_search_context
```

### Deletion Discipline

Before deleting each symbol:

1. Search `src`, `tests`, `smoke`, `README.md`, and `docs`.
2. If the only usage is a test preserving the symbol itself, delete the test.
3. If a smoke script or README uses the symbol, update the public usage first.
4. If the symbol has become useful during Stream 1 or Stream 2, keep it and
   document its purpose.

### Tests For Stream 6

No dedicated tests are needed for deletion, but the full test suite must pass.

Add a lightweight hygiene test only if deletion leaves ambiguous public exports.

## Stream 7 Blueprint: Repository Hygiene

### Tracked Backup Files

Remove:

```text
assets/images/.$degens_dark.svg.bkp
assets/images/.$degens_light.svg.bkp
assets/images/.$how_dark.svg.bkp
assets/images/.$logo_dark.svg.bkp
assets/images/.$logo_light.svg.bkp
assets/images/.$logo_light.svg.dtmp
```

Do not remove:

```text
assets/images/degens_dark.svg
assets/images/degens_light.svg
assets/images/how_dark.svg
assets/images/how_light.svg
assets/images/logo_dark.svg
assets/images/logo_light.svg
```

### Ignore Rule

Add a narrow ignore pattern if these files are not already ignored:

```gitignore
assets/images/.$*.svg.bkp
assets/images/.$*.svg.dtmp
```

Do not add broad patterns that might hide real image assets.

### Generated Python Bytecode

The repo currently shows `__pycache__` entries in local filesystem scans.
Confirm whether they are tracked. If untracked, do not spend release-revision
time on them unless a release hygiene test fails.

If tracked, remove them and add or verify:

```gitignore
__pycache__/
*.py[cod]
```

## Stream 8 Blueprint: Regression And Release Tests

### Witness Consistency Tests

Add:

```text
tests/test_witness_consistency.py
```

For every emitted simplex in a small fake tower and a clean real tower:

- every `FaceEdgeWitness.source_index` and `target_index` addresses the simplex
  vertices correctly;
- every witness edge exists in the normalized tier graph;
- witness edge source equals the source vertex;
- witness edge target equals the target vertex;
- for lifted simplices, `projection_simplex_id` points to an existing downstairs
  simplex id when degree is greater than or equal to 0 and tier is not bottom.

For every lifted simplex over a downstairs simplex:

- projected vertices equal downstairs vertices;
- each last edge projects to one of downstairs last edge ids;
- identity projections are allowed only when endpoints project to the same
  downstairs vertex.

### Clean Tower Semantics Tests

The key regression is not "tier_edges looks simple." It is:

```text
cleaning happens before the next quotient step
```

Test shape:

```text
tier 0:
  a -> b labeled collapse-1
  a -> d labeled collapse-2
  b -> d labeled collapse-2

step 1:
  collapse a -> b
  raw quotient has two C -> d representatives
  clean quotient has one C -> d edge

step 2:
  collapse C -> d once from the cleaned quotient edge
```

The test should assert:

- the clean tower has exactly one non-loop edge between the quotient pair at
  the intermediate tier;
- the second step sees the cleaned edge, not two raw representatives;
- the final tier is the expected singleton or expected quotient;
- edge-fiber diagnostics record the collapsed raw multiplicity.

If labels differ in the raw quotient pair, a companion test should assert a
policy error instead of silent merging.

### API Tests

Update `tests/test_api.py` so public and lower-level workflows are separate:

- public H workflow uses `search_simplices`;
- skeleton/tower workflow uses `search_skeleton_simplices`;
- ambiguous old usage is rejected.

### Artifact Schema Tests

Update `tests/test_artifacts.py` so typed result handling is proved:

- no duck-typed arbitrary object accepted;
- combined result artifact contains manifest result kind;
- skeleton-only result artifact contains manifest result kind;
- manifest-table row counts match written JSONL lines;
- H-lift face-factor table contains expected loop/non-loop factors.

### README Quick-Start Test

Keep the test small.

Possible implementation:

- store the README quick-start as an importable snippet in a test helper, or
  keep a matching test that uses the same code;
- do not parse markdown in a fragile way unless a release hygiene script already
  supports it.

### Release Metadata Test

Use Python standard library `tomllib` to inspect `pyproject.toml`.

Assertions:

- package name is `jet-simplex-search`;
- dependency includes `state-collapser`;
- release mode does not use local path source;
- Python version range matches README badges;
- URLs are present.

Because local development may still need `tool.uv.sources`, the test should
either:

- run only under a release flag; or
- assert that the release dependency itself is public while allowing local
  `tool.uv.sources` only if a separate development flag is set.

The implementation workplan must settle this before writing the test.

## Error Types

Current errors should be reused where sensible:

- `InvalidGraphError`
- `SimplexInvariantError`
- `TowerAdapterError`
- `ArtifactWriteError`
- `InvalidKError`

Potential new error:

```python
class CleanTowerConstructionError(Exception):
    ...
```

Recommendation:

Add a JSS-specific `CleanTowerConstructionError` or reuse `TowerAdapterError`.

Use `TowerAdapterError` if the failure is about adapting tower data to the
search protocol.

Use `CleanTowerConstructionError` if the failure is about constructing the
clean tower itself.

The strict label conflict during clean quotient realization is construction
failure, so it should use the new error if added.

## File-Level Revision Map

### New Files

```text
src/jet_simplex_search/clean_tower.py
src/jet_simplex_search/results.py
tests/test_clean_tower.py
tests/test_witness_consistency.py
tests/test_release_metadata.py
tests/test_readme_quickstart.py
```

Possible new file:

```text
tests/integration/test_clean_state_collapser_tower.py
```

### Modified Files

```text
src/jet_simplex_search/__init__.py
src/jet_simplex_search/api.py
src/jet_simplex_search/artifacts.py
src/jet_simplex_search/errors.py
src/jet_simplex_search/ids.py
src/jet_simplex_search/skeleton.py
src/jet_simplex_search/tower_adapter.py
pyproject.toml
README.md
.gitignore
tests/test_api.py
tests/test_artifacts.py
tests/test_ids.py
tests/test_skeleton.py
tests/integration/test_state_collapser_static_tower.py
```

### Removed Files

```text
assets/images/.$degens_dark.svg.bkp
assets/images/.$degens_light.svg.bkp
assets/images/.$how_dark.svg.bkp
assets/images/.$logo_dark.svg.bkp
assets/images/.$logo_light.svg.bkp
assets/images/.$logo_light.svg.dtmp
```

Remove generated `__pycache__` files only if they are tracked.

## Public API After Revision

Root package exports:

```python
from jet_simplex_search import (
    SearchWithHLiftsResult,
    search_simplices,
    search_skeleton_simplices,
    skeletonize_graph,
)
```

Recommended additional exports:

```python
from jet_simplex_search import SimplexSearchResult
```

Only export `CleanStaticTowerAdapter` if the PO wants the clean tower as a
public lower-level API. Otherwise keep it importable from its module but not in
the root package.

## Artifact Contract After Revision

Single JSON skeleton-only result:

```json
{
  "manifest": {
    "schema_version": 1,
    "result_kind": "simplex_search",
    "package": "jet-simplex-search",
    "k": 2,
    "bottom_tier": 0,
    "artifact_layout": "single_json"
  },
  "simplex_records": [],
  "simplex_fibers": [],
  "edge_fibers": [],
  "diagnostics": {}
}
```

Single JSON H result:

```json
{
  "manifest": {
    "schema_version": 2,
    "result_kind": "skeleton_search_with_h_lifts",
    "package": "jet-simplex-search",
    "k": 2,
    "bottom_tier": 0,
    "artifact_layout": "single_json"
  },
  "skeletonization": {},
  "skeleton_search": {},
  "h_lifts": [],
  "diagnostics": {
    "skeletonization": {},
    "skeleton_search": {},
    "h_lifts": {}
  }
}
```

Manifest-table H result should continue writing:

```text
readout_source.json
skeleton_edge_fibers.jsonl
skeleton_loop_fibers.jsonl
simplex_records.jsonl
simplex_fibers.jsonl
edge_fibers.jsonl
h_lift_records.jsonl
h_lift_face_factors.jsonl
diagnostics.json
```

## README Contract After Revision

The README quick start should still look like:

```python
from state_collapser.tower.partition.schema import LabelBlockSchema

from jet_simplex_search import search_simplices
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c")),
    edges=(
        InputEdge("ab", "a", "b", labels=("collapse",)),
        InputEdge("ac", "a", "c"),
        InputEdge("bc", "b", "c"),
    ),
)

result = search_simplices(
    graph=graph,
    contraction_schema=LabelBlockSchema.from_labels(("collapse",)),
    k=2,
)
```

But installation should no longer tell ordinary users to rely on a sibling
checkout as the primary path.

Known limitations should explicitly say:

- Kan replacement is not implemented.
- Expanded H witness artifacts are not implemented.
- v0.1 label policy requires exact label agreement when collapsing parallel H
  edges or clean quotient edges.
- The release uses static towers; it does not dynamically search/retrain while
  enumerating simplices.
- Low-level skeleton search is available, but the primary public API studies H.

## Performance Instrumentation

The review asked for a feedback-loop improvement around hot-path measurement.

Do not build a large benchmarking framework in this revision.

Add lightweight counters to diagnostics if easy:

- edge-fiber query count;
- edge-fiber nonempty result count;
- lifted candidate count before frontier intersection;
- lifted emitted simplex count.

If this touches too much code, defer to a later performance workstream and only
add tests that preserve the indexed edge-fiber lookup.

The implementation workplan should decide whether diagnostics changes fit the
revision or would distract from correctness cleanup.

## Backward Compatibility

This package is pre-release. Correctness and clean API are more important than
preserving every early helper.

Allowed breaking changes:

- `search_simplices(adapter=...)` stops working.
- `SearchWithHLiftsResult` moves from `api.py` to `results.py`, while remaining
  re-exported from `jet_simplex_search.api` or package root for a short bridge.
- dead id helpers are removed.
- artifact writer rejects arbitrary duck-typed objects.

Not allowed:

- changing simplex counts without a mathematical explanation;
- dropping degenerate simplex records;
- treating formal identities as original H loops;
- losing PM Abdul Malik attribution;
- hiding internal design docs by deleting them;
- rewriting design history into a fake clean story.

## Implementation Pass Ordering

This is not the Phase.Stage.Action workplan, but the revision should be
implemented in this order:

1. Add result typing and split public API.
2. Update artifact writer to use explicit result classes.
3. Add the clean tower builder and adapter.
4. Switch public H workflow to the clean tower adapter.
5. Add clean tower and witness consistency tests.
6. Clean up dead helpers and stale caches.
7. Update README and pyproject release surfaces.
8. Remove tracked backup/temp files.
9. Run full tests and smoke checks.
10. Update implementation log.

Why this order:

- API and result typing make artifact and test changes clearer.
- Clean tower construction is the deepest semantic change and should happen
  after the public result boundary is no longer moving.
- Dead-code cleanup is safer after replacements exist.
- Release docs should describe the final code shape, not an intermediate one.

## Verification Matrix

Minimum verification:

```bash
uv run pytest
```

Targeted verification:

```bash
uv run pytest tests/test_api.py
uv run pytest tests/test_artifacts.py
uv run pytest tests/test_clean_tower.py
uv run pytest tests/test_witness_consistency.py
uv run pytest tests/test_skeleton.py
uv run pytest tests/integration/test_state_collapser_static_tower.py
```

Smoke verification:

```bash
uv run python smoke/smoke_001.py
uv run python smoke/smoke_002.py
...
uv run python smoke/smoke_016.py
```

Release verification:

```bash
uv run python -m build
```

If `build` is not available in the dev dependencies, add it as part of release
metadata cleanup or run the repository's already-approved build command if
available.

## Stop Conditions For Implementation

Stop and ask the PO before implementation continues if:

- clean quotient edge label conflicts appear in existing smoke or README
  examples;
- arbitrary user schemas cannot be applied to reified quotient edges without a
  new PO decision;
- state-collapser public APIs are insufficient to build a one-block quotient
  step without relying on unstable internals;
- switching to clean tower construction changes established smoke counts and
  the difference cannot be immediately explained;
- the actual GitHub state-collapser release tag differs from the local `v0.7.2`
  assumption;
- release dependency changes require network access or lockfile regeneration
  that fails under the sandbox;
- deleting a supposedly dead helper breaks README, smoke scripts, or public
  exports in a way not covered by this blueprint.

## Non-Goals

This revision does not implement:

- Kan replacement;
- horn filling;
- cofibrant replacement variants beyond the current small-object search;
- expanded H witness enumeration artifacts;
- GPU, tensor, CSR, bitset, multiprocessing, SQLite, or DuckDB storage;
- a new state-collapser release;
- PyPI publishing;
- repository visibility changes.

## Blueprint Acceptance Criteria

This blueprint is ready to become a Phase.Stage.Action implementation workplan
when the PO accepts these decisions:

1. Stream 1 uses a JSS-owned clean tower bridge for this revision.
2. A state-collapser upstream clean-tower primitive is deferred.
3. The v0.1 clean quotient edge label policy is exact label agreement.
4. `search_simplices` becomes graph/H-only.
5. `search_skeleton_simplices` becomes the lower-level adapter/skeleton API.
6. Artifact writing becomes explicitly typed.
7. Local `state_collapser` path dependency is removed from public release
   metadata.

Once those are accepted, the next document should be:

```text
docs/design/synthetic_blow_code_revisions/01_003_synthetic_blow_code_revision_implementation_workplan.md
```

That workplan should be Phase.Stage.Action formatted and should treat this
blueprint as the controlling design source.
