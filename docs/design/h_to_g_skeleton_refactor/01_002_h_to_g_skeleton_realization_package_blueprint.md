# H-To-G Skeletonization And H-Lift Package Blueprint

## Status

Implementation-facing blueprint created on June 13, 2026.

This document expands:

```text
docs/design/h_to_g_skeleton_refactor/01_001_h_to_g_skeleton_realization_refactor.md
```

into a concrete package blueprint for the present `jet_simplex_search` repo and
the adjacent `state_collapser` dependency.

The answer to the Project Owner's question is yes: there is enough information
to blueprint this refactor. The important missing implementation work is not a
mathematical ambiguity anymore. It is a set of code-level boundary changes:

```text
1. Build a simple-reflexive G skeleton from arbitrary H.
2. Ensure state_collapser constructs JSS tower tiers from simple-reflexive
   tier graphs, not from multiplicity-bearing action surfaces.
3. Run the existing static small-object simplex search over G and its quotient
   tower.
4. Compute distinct H-lifts only for G^0 skeleton simplices.
5. Keep skeleton search evidence separate from H edge/loop lift evidence.
```

This is a refactor blueprint, not a second algorithm and not a new framework.

## Attribution

The static quotient-tower simplex search algorithm is PM Abdul Malik's work and
part of his thesis. This includes:

```text
degree-wise simplex enumeration
cached frontier recurrence
degenerate simplex handling through formal identities
static quotient tower construction
small-object fiber-addressed lift search
```

The Project Owner introduced the `H -> G ~= G^0 -> ... -> G^d` refactor:

```text
H:
  arbitrary graph, possibly with loops and parallel edges

G:
  simple-reflexive skeleton used for tower search

H-lift:
  post-search recovery/counting of distinct original H simplices over G^0
```

Codex's role in this document is implementation synthesis: mapping the Project
Owner discussion, the synthetic_blow review, the current `jet_simplex_search`
architecture, and the observed `state_collapser` code into an exact package
blueprint.

## Primary Claim

The refactor should make the package obey this sentence everywhere:

```text
Search simplices in G; lift/count distinct simplices in H.
```

The existing package already has most of the small-object search machinery. The
refactor should not rewrite that machinery. It should put the correct graph
layer under it and the correct H-lift layer above it.

## Current Repositories Inspected

### Present Package

The present `jet_simplex_search` package is flat and should remain flat:

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

The current package strengths:

```text
small module graph
plain dataclass records
deterministic ids
fast pytest suite
direct simplex enumeration
clear tower adapter boundary
simple JSON/JSONL artifacts
```

The current package weaknesses relevant to this refactor:

```text
normalize_graph strips loops but preserves non-loop parallel edges
SimplexRecord witness ids currently come from graph.edge_lookup
graph.edge_lookup can contain multiple ids for one endpoint pair
lift edge fibers are target-only
tower_adapter scans tier edges during edge_fiber_targets queries
StateCollapserStaticTowerAdapter builds the tower from the graph it is handed
```

The intended fix is not to make `SimplexRecord` carry every H edge identity
more cleverly. The intended fix is to stop asking skeleton simplex records to
serve as H multiplicity records.

### state_collapser

The relevant adjacent dependency files inspected:

```text
../state_collapser/src/state_collapser/tower/partition/tower.py
../state_collapser/src/state_collapser/tower/partition/action_layer.py
../state_collapser/src/state_collapser/tower/partition/loop_policy.py
../state_collapser/tests/tower/partition/test_action_layer.py
```

The current `state_collapser` partition tower is built by:

```text
PartitionTower.initialize
  register base graph
  build tier-0 singleton state layer
  build tier-0 action layer from registry
  for each contraction block:
    carry state layer forward
    carry action layer forward
    contract selected edges
    rebuild dirty action cells
    append tier
```

The current action-layer grouping is:

```text
(source_cell, target_cell, primitive_action_identity)
```

This is visible in `ActionPartitionLayer.rebuild_action_cells_for_collection`.
Therefore two primitive actions with the same source cell and target cell but
different identities are currently distinct action cells.

That behavior is correct for some `state_collapser` use cases, and the existing
test suite has a test that expects it:

```text
test_action_cell_grouping_uses_source_target_and_action_identity
```

For `jet_simplex_search`, it is the wrong live graph contract. JSS needs a
simple-reflexive tower mode:

```text
one live non-loop edge/action cell per ordered source-target pair
one formal loop per node
primitive actions and edge ids retained only as provenance/fiber data
```

The current `LoopPolicy` records internal edges, but it does not give each tier
exactly one formal loop per state cell as a graph invariant.

## Non-Negotiable Refactor Invariants

### Invariant 1: H May Be Arbitrary In The Approved Sense

The public graph input `H` may contain:

```text
directed edges
loops
parallel non-loop edges
parallel loops
labels
payloads
```

It must still satisfy the existing basic validation:

```text
vertex ids are unique
edge ids are unique
each edge endpoint references an existing vertex
```

### Invariant 2: G Is Simple Before Tower Search

The skeleton graph `G` has:

```text
same vertex set as H in first scope
no original loops as live non-identity edges
at most one non-loop edge for each ordered pair (s,t), s != t
one H-edge fiber behind every skeleton non-loop edge
one H-loop fiber behind every formal identity vertex
```

Formal identities are added by the existing normalization/search layer. They
are not original H edges.

### Invariant 3: Tower Tiers Used To Construct Later Tiers Are Simple-Reflexive

This is the Project Owner correction and the most important upstream boundary:

```text
At every tier, before constructing the next tier:
  excise/merge multiple non-loop edges
  remove original/internal loop multiplicity from the live edge set
  make sure each node has exactly one formal loop
```

This is stronger than an adapter readout cleanup. If the tower constructs
`G^(r+1)` from a multiplicity-bearing `G^r`, the multiplicity has already
polluted the tower before JSS can hide it.

### Invariant 4: SimplexRecord Is A Skeleton/Tower Record

`SimplexRecord.face_edge_witnesses` should mean:

```text
this face exists in the simple skeleton/tower tier
```

It must not mean:

```text
these are all original H edge witnesses
```

Original H edge and loop witnesses belong in H-lift records.

### Invariant 5: H-Lifts Exist Only At G^0 In First Scope

The Project Owner answered this explicitly.

Compute H-lift counts for:

```text
tier 0 skeleton simplices
```

Do not compute H-lift counts for lower quotient tiers:

```text
G^1, G^2, ..., G^d
```

Those tiers are search/compression machinery and diagnostics, not output spaces
for original H simplices.

### Invariant 6: Degenerate G Simplices Lift To H Only Through H Loops

Formal identities make degenerate addresses visible in G.

Actual H-lifts of degenerate faces require actual loops in H:

```text
G has formal degenerate edge:
  (s, s)

H-lifts:
  all original H loops s -> s
```

If H has no loop at `s`, the skeleton degenerate address remains present, but
its H-lift count is zero.

### Invariant 7: Parallel H Edges Produce Distinct H Simplices

Parallel edges are not search multiplicity. They are H-lift multiplicity.

If:

```text
|H(a,b)| = 2
|H(a,c)| = 3
|H(b,c)| = 5
```

then one skeleton 2-simplex:

```text
(a, b, c)
```

has:

```text
2 * 3 * 5 = 30
```

distinct H-lifts.

The default result should store this in compressed form. Full expansion should
be opt-in and capped.

### Invariant 8: Zero-Count Skeleton Simplices Stay In The Result

The Project Owner answered this explicitly:

```text
Include them. Not including them is forgetting.
```

Therefore a skeleton simplex with zero H-lifts is not deleted. The result should
record:

```text
skeleton_exists = true
h_lift_count = 0
```

Public summaries can separately count positive H-lifted simplex addresses.

## Package Shape After Refactor

Keep the flat package layout. Add two modules:

```text
src/jet_simplex_search/skeleton.py
src/jet_simplex_search/h_lift.py
```

Do not add:

```text
src/jet_simplex_search/pipeline/
src/jet_simplex_search/engines/
src/jet_simplex_search/strategies/
```

The synthetic_blow complaint matters here. This package wants plain data and
direct functions.

## Module Ownership

### graph.py

Current role:

```text
raw public graph dataclasses
small graph_from_edges helper
basic validation
```

Keep:

```text
InputVertex
InputEdge
GraphInput
graph_from_edges
validate_graph_input
vertex_ids
payload_for_vertex
```

Do not move skeletonization here. `graph.py` should stay the raw input shape.

### ids.py

Current role:

```text
identity_edge_id
identity_edge_vertex_id
simplex_id
fiber_id
```

Add deterministic helpers:

```python
def skeleton_edge_id(source: str, target: str) -> str:
    ...

def tier_simple_edge_id(tier: int, source: str, target: str) -> str:
    ...

def h_lift_id(simplex_id: str) -> str:
    ...
```

Design constraints:

```text
ids must not depend on insertion order
ids must escape arbitrary string vertex ids
ids must be stable across runs
```

`fiber_id` appears unused in the present package. Do not expand its usage unless
the implementation actually needs it. Dead id helpers should be deleted in a
separate cleanup if they stay unused after the refactor.

### skeleton.py

New module.

Responsibilities:

```text
collapse H to G
preserve H edge fibers
preserve H loop fibers
validate skeleton invariants
report skeletonization diagnostics
```

Candidate public records:

```python
@dataclass(frozen=True, slots=True)
class SkeletonEdgeFiber:
    source: str
    target: str
    skeleton_edge_id: str
    original_edge_ids: tuple[str, ...]
    labels: tuple[object, ...]


@dataclass(frozen=True, slots=True)
class SkeletonLoopFiber:
    vertex_id: str
    original_loop_edge_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SkeletonizationDiagnostics:
    input_vertex_count: int
    input_edge_count: int
    input_loop_edge_count: int
    input_non_loop_edge_count: int
    skeleton_non_loop_edge_count: int
    collapsed_parallel_non_loop_edge_count: int
    collapsed_loop_edge_count: int
    vertices_with_original_loops: int
    maximum_non_loop_fiber_size: int
    maximum_loop_fiber_size: int
    label_conflict_count: int


@dataclass(frozen=True, slots=True)
class SkeletonizationResult:
    original_graph: GraphInput
    skeleton_graph: GraphInput
    edge_fibers_by_pair: Mapping[tuple[str, str], SkeletonEdgeFiber]
    edge_fibers_by_skeleton_edge_id: Mapping[str, SkeletonEdgeFiber]
    loop_fibers_by_vertex: Mapping[str, SkeletonLoopFiber]
    skeleton_edge_id_by_pair: Mapping[tuple[str, str], str]
    skeleton_edge_id_by_original_edge_id: Mapping[str, str]
    original_loop_vertex_by_edge_id: Mapping[str, str]
    diagnostics: SkeletonizationDiagnostics
```

Candidate functions:

```python
def skeletonize_graph(
    graph: GraphInput,
    *,
    label_policy: SkeletonLabelPolicy = SkeletonLabelPolicy.REQUIRE_IDENTICAL,
) -> SkeletonizationResult:
    ...

def assert_skeleton_graph_invariants(result: SkeletonizationResult) -> None:
    ...
```

Candidate label policy:

```python
class SkeletonLabelPolicy(StrEnum):
    REQUIRE_IDENTICAL = "require_identical"
```

Do not add custom callbacks in first scope. If labels inside a parallel edge
fiber disagree, fail loudly under `REQUIRE_IDENTICAL`.

Rationale:

```text
state_collapser schemas may use labels
silently unioning labels can change contractions
silently choosing one label can hide a mathematical decision
```

### normalize.py

Current behavior:

```text
strip input loops
add formal identities
preserve non-loop parallel edges
build adjacency_targets
build edge_lookup
```

After the refactor:

```text
normalize_graph still performs reflexive search normalization
the graph passed to normalize_graph should usually be skeleton_graph
```

Add an optional assertion helper:

```python
def assert_simple_reflexive_normalized_graph(graph: NormalizedGraph) -> None:
    ...
```

This helper should enforce:

```text
one identity edge per vertex
no original loop edges
len(edge_lookup[(s,t)]) == 1 for every endpoint pair
adjacency includes each vertex itself
```

Do not make `normalize_graph` silently collapse non-loop parallel edges. That
would mix skeletonization and reflexive normalization again.

### records.py

Current role:

```text
FaceEdgeWitness
SimplexRecord
SimplexFiberRecord
EdgeFiberRecord
SimplexSearchResult
```

Keep `SimplexRecord` as the skeleton/tower simplex record.

Modify `EdgeFiberRecord` only if needed for tier simple-edge indexing. If tower
tiers are truly simple by endpoint pair, target-only edge fibers are acceptable
as search fibers. If there is any chance of parallel tier search edges
surviving, then `EdgeFiberRecord` must include edge ids too.

Recommended first-scope stance:

```text
simple-reflexive tier invariant is mandatory
EdgeFiberRecord can remain target-oriented for search
new provenance/fiber records live outside SimplexRecord
```

Add H-lift records either here or in `h_lift.py`. Prefer `h_lift.py` to avoid
turning `records.py` into a dumping ground.

### h_lift.py

New module.

Responsibilities:

```text
take tier-0 skeleton simplices
map tier-0 vertices back to H/G vertex ids
compute H face fibers
compute compressed H-lift counts
optionally enumerate expanded H witness assignments later
```

Use "H-lift" language in code and docs. The earlier word "realization" is
historical context, but "lift" matches the Project Owner's correction better.

Candidate records:

```python
@dataclass(frozen=True, slots=True)
class HFaceLiftFactor:
    source_index: int
    target_index: int
    source_vertex_id: str
    target_vertex_id: str
    skeleton_edge_id: str
    original_edge_ids: tuple[str, ...]
    factor: int
    is_loop_factor: bool


@dataclass(frozen=True, slots=True)
class SimplexHLiftRecord:
    id: str
    simplex_id: str
    tier: int
    degree: int
    skeleton_vertices: tuple[str, ...]
    input_vertices: tuple[str, ...]
    face_factors: tuple[HFaceLiftFactor, ...]
    h_lift_count: int
    has_h_lift: bool


@dataclass(frozen=True, slots=True)
class HLiftDiagnostics:
    simplex_count_by_degree: Mapping[int, int]
    positive_simplex_count_by_degree: Mapping[int, int]
    zero_lift_simplex_count_by_degree: Mapping[int, int]
    total_h_lift_count_by_degree: Mapping[int, int]
    max_h_lift_count_by_degree: Mapping[int, int]
    max_face_factor_by_degree: Mapping[int, int]
```

Candidate functions:

```python
def compute_h_lifts_for_tier_zero(
    *,
    skeletonization: SkeletonizationResult,
    skeleton_search: SimplexSearchResult,
    tier0_vertex_id_to_input_vertex_id: Mapping[str, str],
) -> tuple[SimplexHLiftRecord, ...]:
    ...

def build_h_lift_diagnostics(
    records: Iterable[SimplexHLiftRecord],
) -> HLiftDiagnostics:
    ...
```

Count algorithm:

```text
for each tier-0 skeleton simplex sigma = (v0, ..., vm):
  count = 1
  for each face occurrence (vi -> vj), i < j:
    source = input_vertices[i]
    target = input_vertices[j]

    if source == target:
      original_edge_ids = loop_fibers_by_vertex[source].original_loop_edge_ids
      skeleton_edge_id = identity_edge_id(source)
    else:
      fiber = edge_fibers_by_pair[(source, target)]
      original_edge_ids = fiber.original_edge_ids
      skeleton_edge_id = fiber.skeleton_edge_id

    factor = len(original_edge_ids)
    count *= factor
```

Critical behavior:

```text
missing non-loop fiber:
  invariant error

missing loop fiber:
  should not happen if every vertex has a SkeletonLoopFiber

empty loop fiber:
  factor = 0
  count becomes 0

empty non-loop fiber:
  invariant error
```

### search.py

Current role:

```text
validate k
enumerate zero simplices
extend simplex directly
enumerate direct simplices
run static small-object search across tower
```

Keep the core algorithm.

Add no H-specific logic here.

The only search-layer changes should be:

```text
assert normalized graph is simple-reflexive when appropriate
update docstrings to say SimplexRecord is skeleton/tower evidence
```

`extend_simplex_direct` can continue using:

```python
graph.edge_lookup[(source, target)]
```

because after this refactor the relevant graph lookup should have one edge id
per endpoint pair.

### lift.py

Current role:

```text
lift zero simplices
lift downstairs extensions
lift all simplices from tier r+1 to tier r
record simplex fibers and edge fibers
```

Keep the algorithmic structure:

```text
search only over existing downstairs simplices
for each upstairs prefix over the downstairs prefix
restrict candidate final edge by the downstairs final edge fiber
intersect with prefix frontier
```

Refactor pressure points:

```text
edge_fiber_targets currently calls adapter.edge_fiber_targets
adapter.edge_fiber_targets currently scans tier edges
```

The blueprint fix is:

```text
adapter should build indexed simple-edge fibers once per tier
lift.py should use indexed lookup, not repeated scans
```

Do not add H-lift logic here. This is tower lifting, not H lifting.

### tower_adapter.py

Current role:

```text
StaticTowerAdapterProtocol
normalized_graph_for_tier
StateCollapserStaticTowerAdapter
state cell/action cell id conversion
```

This is the most important JSS-side module to refactor.

Required public/protocol behavior:

```text
tiers()
bottommost_nondegenerate_tier()
tier_vertices(tier)
tier_edges(tier)
edge_source(tier, edge_id)
edge_target(tier, edge_id)
project_vertex(tier, vertex_id)
project_edge(tier, edge_id)
edge_fiber_targets(...)
```

Add or expose:

```python
def tier0_vertex_id_to_input_vertex_id(self) -> Mapping[str, str]:
    ...
```

or:

```python
def input_vertex_id_for_tier0_vertex(self, tier0_vertex_id: str) -> str:
    ...
```

The H-lift stage needs this map because tier-0 vertices are currently strings
such as:

```text
cell:0:0
```

while H fibers are keyed by input vertex ids such as:

```text
a
b
c
```

Recommended adapter internals after refactor:

```python
@dataclass(frozen=True, slots=True)
class TierSimpleEdge:
    id: str
    tier: int
    source: str
    target: str
    action_cell_edge_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TierSimpleView:
    tier: int
    vertices: tuple[str, ...]
    non_identity_edges: tuple[TierSimpleEdge, ...]
    edge_id_by_pair: Mapping[tuple[str, str], str]
    action_edge_ids_by_simple_edge_id: Mapping[str, tuple[str, ...]]
```

However, if `state_collapser` supplies the simple-reflexive tier directly, keep
the adapter thinner:

```text
consume state_collapser's simple tier readout
cache edge source/target/project/fiber indexes
do not rebuild a second semantic tier model unless needed
```

Mandatory adapter indexes:

```text
edge_id_by_pair_by_tier:
  (tier, source, target) -> simple_edge_id

edge_source_target_by_tier_edge:
  (tier, simple_edge_id) -> (source, target)

projected_edge_by_tier_edge:
  (tier, simple_edge_id) -> downstairs_simple_edge_id

edge_fiber_targets_by_downstairs_edge_and_source:
  (upstairs_tier, downstairs_edge_id, upstairs_source_id) -> frozenset[target_id]
```

This removes the current repeated whole-tier scan in `edge_fiber_targets`.

### api.py

Current public API:

```python
def search_simplices(
    *,
    adapter: StaticTowerAdapterProtocol | None = None,
    graph: GraphInput | None = None,
    contraction_schema: object | None = None,
    k: int,
    artifact_config: ArtifactConfig | None = None,
) -> SimplexSearchResult:
    ...
```

Recommended refactor:

```python
@dataclass(frozen=True, slots=True)
class SearchWithHLiftsResult:
    k: int
    skeletonization: SkeletonizationResult
    skeleton_search: SimplexSearchResult
    h_lifts: tuple[SimplexHLiftRecord, ...]
    h_lift_diagnostics: HLiftDiagnostics
```

Public graph-H API:

```python
def search_simplices(
    *,
    graph: GraphInput,
    contraction_schema: object | None = None,
    k: int,
    artifact_config: ArtifactConfig | None = None,
    include_h_lifts: bool = True,
) -> SearchWithHLiftsResult:
    ...
```

Lower-level skeleton/tower API:

```python
def search_skeleton_simplices(
    *,
    adapter: StaticTowerAdapterProtocol,
    k: int,
    artifact_config: ArtifactConfig | None = None,
) -> SimplexSearchResult:
    ...
```

Rationale:

```text
public graph API should be H-aware
internal/advanced adapter API should remain skeleton-only
```

Avoid keeping `StaticSearchContext` unless it starts carrying real state. Right
now it is mostly a one-use object hop.

### artifacts.py

Current artifact contract:

```text
single_json:
  readout_source.json

manifest_tables:
  readout_source.json
  simplex_records.jsonl
  simplex_fibers.jsonl
  edge_fibers.jsonl
  diagnostics.json
```

Refactored artifact contract:

```text
single_json:
  readout_source.json
    manifest
    skeletonization
    skeleton_search
    h_lifts
    diagnostics

manifest_tables:
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

Add artifact config flags:

```python
include_h_fiber_members: bool = True
include_h_lift_face_factors: bool = True
include_expanded_h_lift_witnesses: bool = False
max_expanded_h_lift_witnesses: int = 100_000
```

Do not write expanded H witness assignments by default.

If expanded witness output is later implemented, behavior must be explicit:

```text
if expansion exceeds max_expanded_h_lift_witnesses:
  raise ArtifactWriteError or write explicit truncation metadata
```

Silent truncation is forbidden.

### diagnostics.py

Current role:

```text
SearchDiagnostics
SummaryStats
build_search_diagnostics
```

Add serialization helpers for:

```text
SkeletonizationDiagnostics
HLiftDiagnostics
combined result diagnostics
```

Avoid turning diagnostics into a second result model. Diagnostics should
summarize records, not replace them.

## state_collapser Blueprint

This section names the upstream dependency work needed for the refactor to be
correct.

### Required New Contract

`state_collapser` needs a mode for JSS tower construction:

```text
simple-reflexive tier construction
```

Contract:

```text
At each tier r:
  live non-loop action surface has at most one edge/action cell per ordered
  source-target state-cell pair

  primitive action identities do not split live JSS tier edges

  original/internal loops are not live multiplicity edges

  each state cell has exactly one formal loop in the graph semantics exposed to
  JSS

  primitive/base edge ids remain available as provenance under the one simple
  edge/action cell
```

### Why Adapter-Only Cleanup Is Not Enough

Adapter-only cleanup would do:

```text
state_collapser builds tower with multiplicity
JSS hides multiplicity when reading each tier
```

The PO explicitly rejected that weaker shape by requiring:

```text
before we construct next tier, excise multiple edges and make sure each node has exactly one loop
```

Therefore the simple-reflexive rule must apply at the construction boundary,
not merely at the readout boundary.

### Likely state_collapser Implementation Shape

Do not break existing `state_collapser` default behavior. Add a policy or mode.

Candidate policy:

```python
class ActionCellGroupingPolicy(StrEnum):
    SOURCE_TARGET_ACTION = "source_target_action"
    SOURCE_TARGET = "source_target"
```

or:

```python
@dataclass(frozen=True, slots=True)
class TierGraphPolicy:
    collapse_parallel_by_endpoint: bool
    expose_formal_loop_per_state_cell: bool
```

For synthetic_blow reasons, prefer the smallest concrete option:

```python
simple_reflexive_tiers: bool = False
```

if the only consumer is JSS first scope.

But if `state_collapser` maintainers prefer explicit policy objects, keep the
policy small and concrete.

### Required action_layer.py Change

Current grouping:

```python
grouped: dict[tuple[StateCellId, StateCellId, object], dict[EdgeId, None]]
...
label_key = registry.action_for_edge_id(edge_id).canonical_identity
grouped.setdefault((source_cell, target_cell, label_key), {})[edge_id] = None
```

JSS simple mode grouping:

```python
grouped: dict[tuple[StateCellId, StateCellId], dict[EdgeId, None]]
...
grouped.setdefault((source_cell, target_cell), {})[edge_id] = None
```

The action identities must still be retained as provenance, probably by adding:

```text
label_keys_by_action_cell
primitive_action_identities_by_action_cell
```

or by preserving the existing `edge_ids_by_action_cell`, from which identities
can be recovered through the registry.

### Required Loop Semantics

Current loop/internal behavior:

```text
source_cell == target_cell edges are removed from live collection
internal edge ids are recorded under LoopPolicy
```

JSS required graph semantics:

```text
internal edges are provenance, not live loops
each state cell has exactly one formal loop in search graph semantics
```

Implementation option:

```text
state_collapser does not have to store formal loops as registry BaseEdge ids
if it exposes a tier graph readout that guarantees one formal loop per state
cell.
```

For JSS, formal loops can still be generated by `normalize_graph` from the
simple non-loop tier edges. But the tower-construction side still needs to know
that loops are not multiplicity-bearing action cells for the next tier.

### Required state_collapser Tests

Add upstream tests without deleting existing behavior:

```text
1. Default mode still groups by source, target, and action identity.

2. Simple-reflexive mode groups two actions a -> b into one live action cell.

3. Simple-reflexive grouped action cell retains both primitive edge ids.

4. Contracting a -> b records internal edges but does not expose internal edge
   multiplicity as live loops.

5. Simple-reflexive tier readout exposes exactly one formal loop per state cell.

6. Before constructing tier r+1, tier r's live action surface satisfies:
     one non-loop edge per ordered endpoint pair
     no live original loops
     one formal loop per node in graph semantics
```

## End-To-End Pipeline

### Public Call

The user writes:

```python
result = search_simplices(
    graph=graph_h,
    contraction_schema=schema,
    k=4,
)
```

### Internal Pipeline

The package does:

```text
validate k
validate GraphInput H
skeletonize H -> G plus H fibers
build state_collapser tower from G under simple-reflexive tier mode
run static small-object search over G^bullet
extract tier-0 skeleton simplices
map tier-0 tower vertex ids back to input vertex ids
compute compressed H-lift records
build combined result
write artifacts if requested
```

### Explicit Pseudocode

```python
def search_simplices(
    *,
    graph: GraphInput,
    contraction_schema: object | None = None,
    k: int,
    artifact_config: ArtifactConfig | None = None,
) -> SearchWithHLiftsResult:
    validate_k(k)

    skeletonization = skeletonize_graph(graph)

    adapter = StateCollapserStaticTowerAdapter.from_graph(
        skeletonization.skeleton_graph,
        schema=contraction_schema,
        tier_graph_mode="simple_reflexive",
    )

    skeleton_search = run_static_small_object_search(
        adapter,
        k=k,
    )

    h_lifts = compute_h_lifts_for_tier_zero(
        skeletonization=skeletonization,
        skeleton_search=skeleton_search,
        tier0_vertex_id_to_input_vertex_id=adapter.tier0_vertex_id_to_input_vertex_id(),
    )

    result = SearchWithHLiftsResult(
        k=k,
        skeletonization=skeletonization,
        skeleton_search=skeleton_search,
        h_lifts=h_lifts,
        h_lift_diagnostics=build_h_lift_diagnostics(h_lifts),
    )

    if artifact_config is not None:
        write_search_artifact(result, artifact_config)

    return result
```

## Fiber-Addressed Search Under The Refactor

The small-object speedup remains the same:

```text
never search upstairs over a missing downstairs simplex
```

For a downstairs `(m+1)`-simplex:

```text
tau = (c0, ..., cm, c_{m+1})
```

with prefix:

```text
partial tau = (c0, ..., cm)
```

and last edge:

```text
cm -> c_{m+1}
```

the lift search at tier `r` should only inspect:

```text
upstairs m-simplices over partial tau
upstairs final edges over the last edge of tau
```

Then it intersects:

```text
edge-fiber targets over downstairs last edge
cap
cached frontier of upstairs prefix simplex
```

This means that if downstairs has only a boundary and no interior simplex, the
upstairs search for that interior simplex never starts.

This remains distinct from Kan filling:

```text
small-object version:
  lift only over existing downstairs simplices

Kan version:
  later design, horn/filler semantics
```

## H-Lift Semantics In Detail

### 0-Simplices

For:

```text
sigma = (s)
```

there is one vertex lift in first scope:

```text
s in H
```

H-lift count:

```text
1
```

No edge witness factors exist.

### Nondegenerate 1-Simplices

For:

```text
sigma = (s, t), s != t
```

H-lifts are original edges:

```text
H(s,t)
```

H-lift count:

```text
|H(s,t)|
```

### Degenerate 1-Simplices

For:

```text
sigma = (s, s)
```

H-lifts are original loops:

```text
Loop_H(s)
```

H-lift count:

```text
|Loop_H(s)|
```

This can be zero.

### Nondegenerate 2-Simplices

For:

```text
sigma = (a, b, c)
```

H-lift count:

```text
|H(a,b)| * |H(a,c)| * |H(b,c)|
```

### Left Degenerate 2-Simplices

For:

```text
sigma = (s, s, t)
```

face factors:

```text
(0,1): Loop_H(s)
(0,2): H(s,t)
(1,2): H(s,t)
```

H-lift count:

```text
|Loop_H(s)| * |H(s,t)| * |H(s,t)|
```

### Right Degenerate 2-Simplices

For:

```text
sigma = (s, t, t)
```

face factors:

```text
(0,1): H(s,t)
(0,2): H(s,t)
(1,2): Loop_H(t)
```

H-lift count:

```text
|H(s,t)| * |H(s,t)| * |Loop_H(t)|
```

### Totally Degenerate 2-Simplices

For:

```text
sigma = (s, s, s)
```

face factors:

```text
(0,1): Loop_H(s)
(0,2): Loop_H(s)
(1,2): Loop_H(s)
```

H-lift count:

```text
|Loop_H(s)|^3
```

### Dimension 3 And 4

No special logic should appear for dimensions 3 and 4. The face-occurrence
product rule handles them:

```text
degree m simplex has binomial(m+1, 2) directed face occurrences
each face occurrence gets one H edge/loop fiber
the H-lift count is the product of all factor sizes
```

This is exactly why full expansion must be opt-in.

## Result Semantics

### Skeleton Counts

The existing `SimplexSearchResult` count by tier and degree should be understood
as:

```text
number of skeleton/tower simplex addresses
```

### Positive H-Lifted Address Counts

For tier 0 only:

```text
number of skeleton simplex addresses whose h_lift_count > 0
```

### Total H-Lift Counts

For tier 0 only:

```text
sum of h_lift_count across skeleton simplex addresses
```

One skeleton address can contribute many H-lifts.

### Expanded H-Lift Witness Assignments

Optional future output:

```text
each assignment of original H edge ids to face occurrences is one distinct
H-lifted simplex
```

Do not make this default. It can be enormous.

## Artifact Schema Sketch

### Manifest

```json
{
  "schema_version": 2,
  "package": "jet-simplex-search",
  "result_kind": "skeleton_search_with_h_lifts",
  "k": 4,
  "bottom_tier": 2,
  "artifact_layout": "manifest_tables",
  "include_frontier_members": false,
  "include_full_fiber_members": true,
  "include_h_fiber_members": true,
  "include_expanded_h_lift_witnesses": false
}
```

### skeleton_edge_fibers.jsonl

Each row:

```json
{
  "source": "a",
  "target": "b",
  "skeleton_edge_id": "jss:skeleton-edge:a:b",
  "original_edge_ids": ["e1", "e2"],
  "count": 2,
  "labels": []
}
```

### skeleton_loop_fibers.jsonl

Each row:

```json
{
  "vertex_id": "a",
  "formal_identity_edge_id": "jss:identity:a",
  "original_loop_edge_ids": ["loop_a_1"],
  "count": 1
}
```

### h_lift_records.jsonl

Each row:

```json
{
  "id": "jss:h-lift:...",
  "simplex_id": "jss:simplex:t0:d2:v[a,b,c]",
  "tier": 0,
  "degree": 2,
  "skeleton_vertices": ["cell:0:0", "cell:0:1", "cell:0:2"],
  "input_vertices": ["a", "b", "c"],
  "h_lift_count": 30,
  "has_h_lift": true,
  "face_factor_count": 3
}
```

### h_lift_face_factors.jsonl

Each row:

```json
{
  "h_lift_id": "jss:h-lift:...",
  "simplex_id": "jss:simplex:t0:d2:v[a,b,c]",
  "source_index": 0,
  "target_index": 1,
  "source_vertex_id": "a",
  "target_vertex_id": "b",
  "skeleton_edge_id": "jss:skeleton-edge:a:b",
  "original_edge_ids": ["ab_1", "ab_2"],
  "factor": 2,
  "is_loop_factor": false
}
```

## Testing Blueprint

### Skeletonization Tests

Add:

```text
tests/test_skeleton.py
```

Cases:

```text
1. one vertex no edges
   - skeleton has same vertex
   - skeleton has no non-loop edges
   - loop fiber exists and is empty

2. one non-loop edge
   - skeleton has one edge
   - edge fiber has one original id

3. three parallel non-loop edges
   - skeleton has one edge
   - edge fiber has three original ids
   - collapsed_parallel_non_loop_edge_count == 2

4. one loop
   - skeleton has no non-loop edges
   - loop fiber has one original id

5. parallel loops
   - skeleton has no non-loop edges
   - loop fiber has all original loop ids

6. mixed loops and parallel non-loop edges
   - all fibers correct
   - skeleton graph remains loop-free and simple

7. label conflict under REQUIRE_IDENTICAL
   - raises InvalidGraphError

8. identical labels under REQUIRE_IDENTICAL
   - skeleton edge carries identical label tuple
```

### Normalization Tests

Extend:

```text
tests/test_normalize.py
```

Cases:

```text
1. normalize skeleton graph adds exactly one identity per vertex
2. normalized skeleton edge_lookup has length one for each pair
3. assert_simple_reflexive_normalized_graph rejects non-loop parallel edges
```

### H-Lift Tests

Add:

```text
tests/test_h_lift.py
```

Cases:

```text
1. 0-simplex count is 1
2. nondegenerate edge with M parallel H edges has count M
3. degenerate edge with no H loop has count 0 and remains present
4. degenerate edge with L H loops has count L
5. nondegenerate triangle count is product of three edge fibers
6. (s,s,t) count is |Loop_H(s)| * |H(s,t)|^2
7. (s,t,t) count is |H(s,t)|^2 * |Loop_H(t)|
8. (s,s,s) count is |Loop_H(s)|^3
9. missing non-loop fiber for a skeleton simplex raises invariant error
10. diagnostics separate positive address count from total H-lift count
```

### Tower Adapter Tests

Extend or add:

```text
tests/test_tower_adapter_simple_reflexive.py
```

Cases:

```text
1. tier 0 vertex strings map back to input vertex ids
2. tier_edges has no non-identity loops
3. tier_edges has at most one edge per ordered endpoint pair
4. edge_fiber_targets uses indexed lookup and matches slow reference
5. project_edge is endpoint-determined
```

### state_collapser Integration Tests

Add tests in `state_collapser`, not only JSS:

```text
1. default action grouping behavior is unchanged
2. simple-reflexive mode collapses source-target parallel action identities
3. provenance retains all primitive edges under the one simple action cell
4. internal edges are recorded but not exposed as live loop multiplicity
5. tier construction uses normalized tier graph before next tier
```

### Small-Object Regression Tests

Keep/add:

```text
downstairs boundary without downstairs interior
```

Expected behavior:

```text
if no downstairs 2-simplex exists, no upstairs 2-simplex is searched/emitted
over it, even if upstairs graph has enough edges to form one
```

This remains the central distinction from Kan filling.

### Smoke Scripts

Update smoke output labels:

```text
skeleton simplex counts
positive H-lifted skeleton addresses
total distinct H-lift count
```

Do not mix them in one unlabeled table.

## Migration Plan

### Phase 1: Add Skeletonization

Implement:

```text
src/jet_simplex_search/skeleton.py
ids.skeleton_edge_id
tests/test_skeleton.py
```

Do not yet rewire public `search_simplices`.

Done when:

```text
arbitrary H loops and parallels produce deterministic G
all H fibers are inspectable
label conflicts fail loudly
```

### Phase 2: Strengthen Normalization Assertions

Implement:

```text
assert_simple_reflexive_normalized_graph
normalization tests for skeleton graphs
```

Done when:

```text
the direct search layer can assert it is seeing one edge per endpoint pair
```

### Phase 3: Add H-Lift Computation

Implement:

```text
src/jet_simplex_search/h_lift.py
HFaceLiftFactor
SimplexHLiftRecord
HLiftDiagnostics
compute_h_lifts_for_tier_zero
```

Done when:

```text
all low-dimensional loop/parallel product tests pass
zero-count skeleton simplices are retained
```

### Phase 4: Add Combined Result Model

Implement:

```text
SearchWithHLiftsResult
search_skeleton_simplices lower-level API
public search_simplices graph-H orchestration
```

Done when:

```text
public graph calls return skeleton search plus H-lift records
existing tower-only tests still have a direct lower-level API
```

### Phase 5: state_collapser Simple-Reflexive Mode

Implement upstream:

```text
simple-reflexive tier construction policy/mode
source-target grouping in that mode
formal loop tier semantics
provenance retention
state_collapser tests
```

Done when:

```text
JSS can build a tower where every tier used to create the next tier is already
simple-reflexive
```

This phase may need to happen before Phase 4 is fully wired if adapter tests
show multiplicity leaking through the present tower.

### Phase 6: Adapter Indexing And Tier-0 Vertex Map

Implement:

```text
tier simple-edge indexes
edge_fiber_targets indexed lookup
tier0_vertex_id_to_input_vertex_id
simple-reflexive adapter invariants
```

Done when:

```text
edge_fiber_targets no longer scans all tier edges per query
H-lift stage can map tier-0 simplex vertices back to H vertex ids
```

### Phase 7: Artifact Schema Version 2

Implement:

```text
artifact writer support for SearchWithHLiftsResult
skeleton edge fiber tables
skeleton loop fiber tables
h_lift_records table
h_lift_face_factors table
diagnostics updates
```

Done when:

```text
artifacts can audit skeleton evidence and H-lift evidence separately
```

### Phase 8: Docs And Smoke Refresh

Update:

```text
README examples
smoke/simplex_table.py
smoke scripts
smoke markdown arguments
release-prep notes
```

Done when:

```text
every public example says whether it is displaying skeleton counts,
positive H-lifted address counts, or total H-lift counts
```

## Performance Blueprint

### What Should Stay Cheap

Skeleton search should remain sparse-friendly:

```text
frontier intersections use cached simplex frontiers
extensions are generated from existing simplices
tower lifts are addressed by existing downstairs simplex fibers
```

### What Can Blow Up

H-lift expansion can blow up:

```text
parallel edge products
loop products
dimension m has binomial(m+1, 2) face factors
```

Therefore:

```text
compressed H-lift counts are default
expanded witness assignments are opt-in
expanded witness assignments have a cap
```

### Indexes Required Before Release

Add:

```text
skeleton edge fiber lookup by pair
skeleton edge fiber lookup by skeleton edge id
loop fiber lookup by vertex
tier edge lookup by pair
edge projection lookup by tier edge id
edge fiber targets lookup by (upstairs_tier, downstairs_edge_id, upstairs_source_id)
```

Avoid:

```text
scan all edges for every lift candidate
scan all simplices for every H-lift record
recompute face factors from artifact rows
```

## Error Policy

Use existing package errors where possible.

Recommended:

```text
InvalidGraphError:
  raw H input is invalid
  label conflict under REQUIRE_IDENTICAL

SimplexInvariantError:
  skeletonization result violates its own invariants
  normalized skeleton graph is not simple-reflexive
  H-lift asks for missing non-loop fiber
  tier-0 state cell is not singleton when mapping back to input vertex

TowerAdapterError:
  state_collapser tower does not satisfy simple-reflexive contract
  edge projection cannot be determined by endpoints
```

Do not silently repair invariant failures after skeletonization. Fail at the
boundary where the invariant is broken.

## Documentation Semantics

Public docs should use this language:

```text
jet_simplex_search searches a simple-reflexive skeleton G of an input graph H
using a static quotient tower. It then computes compressed H-lift counts for
tier-0 skeleton simplices, where original loops and parallel edges in H produce
distinct lifted simplices.
```

Avoid:

```text
the tower searches all H simplices directly
```

Avoid:

```text
formal identities are H loops
```

Correct:

```text
formal identities generate degenerate skeleton addresses;
actual H loops lift degenerate faces back to H.
```

## Release Impact

This refactor should land before public release if H loops and parallel edges
are part of the promised package behavior.

Reasons:

```text
it changes public result semantics
it changes artifact schema
it changes README examples
it changes what counts mean
it requires an upstream state_collapser mode
```

Do not release with README language that suggests arbitrary H multiplicity is
fully handled if the package is still searching multiplicity-bearing tower
edges directly.

## Synthetic_Blow Design Audit

### Keep

```text
flat modules
plain dataclasses
direct functions
deterministic ids
small-object lift loop
frontier recurrence
simple artifacts
```

### Delete Or Avoid

```text
one-use context objects unless they carry real state
strategy registries
callback policy hooks
adapter-only cleanup pretending to be tower normalization
ambiguous witness ids
unbounded H witness expansion
silent label merging
```

### Rewrite First

The first deep rewrite should be:

```text
input H skeletonization plus H-lift records
```

The second deep rewrite should be:

```text
state_collapser simple-reflexive tier mode plus indexed adapter fibers
```

## Done Criteria

The refactor is complete when all of these are true:

```text
1. Public search accepts H with loops and parallel edges.

2. H is skeletonized to deterministic simple G before tower construction.

3. G^0 has one non-loop edge per ordered endpoint pair and formal identity
   semantics for degenerates.

4. state_collapser constructs every JSS tower tier from a simple-reflexive
   tier graph, not merely a simple readout view.

5. Direct simplex enumeration and tower lifting operate only on skeleton/tower
   simplex records.

6. Fiber-addressed small-object lifting still only searches over existing
   downstairs simplices.

7. Tier-0 skeleton simplices have compressed H-lift records.

8. Degenerate skeleton simplices lift to H exactly through actual H loops.

9. Parallel H edges produce distinct H-lifted simplices through compressed
   multiplicity products.

10. Zero-count skeleton simplices remain present by default.

11. Artifacts expose skeleton fibers, tower simplex records, and H-lift records
    as separate tables.

12. Tests cover skeletonization, loops, parallel edges, degenerate lifts,
    repeated face products, downstream-boundary/no-interior behavior, adapter
    simple-reflexive invariants, and artifact schema version 2.
```

## Final Blueprint Rule

The package should make this impossible to confuse:

```text
G is where the search happens.
H is where distinct lifted simplices are counted.
The tower never pays for H multiplicity.
The H-lift layer never changes which skeleton simplices were searched.
```

