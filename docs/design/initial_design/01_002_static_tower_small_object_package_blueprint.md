# Static Tower Small-Object Package Blueprint

## Status

Implementation blueprint derived from:

```text
docs/design/initial_design/01_001_static_tower_small_object_simplex_search.md
```

This document is build-facing. It translates the initial design note into a
package structure, API plan, data model, algorithms, invariants, tests, and
artifact contracts for the first small-object/static-tower version of
`jet_simplex_search`.

## Attribution

The algorithmic content is PM Abdul Malik's work and part of his thesis. This
includes the static quotient-tower pipeline, the degree-wise `Out` construction,
degenerate simplex handling, and fiber-addressed lift search.

The Project Owner relayed, clarified, and corrected the intended package
semantics in the June 12, 2026 design discussion.

This blueprint is consultant-authored synthesis. It should not be cited as the
source of the mathematical algorithm.

## Package Mission

`jet_simplex_search` finds directed flag simplices in a graph using a static
quotient tower to avoid irrelevant search.

Input:

```text
graph G
positive integer k
state_collapser contraction schema
```

Output:

```text
all m-simplices for 0 <= m <= k, including degenerates,
with tier, projection, fiber, frontier, and face-edge witness data
```

The first implementation is a small-object/static-tower enumerator. It is not a
Kan replacement engine, not an RL loop, and not a dynamic exploration runtime.

## Non-Goals

The first implementation must not:

- reimplement quotient-tower construction already owned by `state_collapser`;
- use `state_collapser.tower.runtime.TowerRuntime` as the core algorithm;
- use RL training abstractions as the core algorithm;
- enumerate arbitrary upstairs candidates and post-filter by projection;
- collapse degenerate simplices to lower-dimensional spines;
- conflate full directed-flag simplex search with future Kan horn filling;
- require a neural/tensor backend;
- optimize for distributed or out-of-core operation before the object model and
  invariants are correct.

## Dependency Boundary

`state_collapser` owns:

```text
State / PrimitiveAction / BaseEdge identities
base graph registry
contraction schema execution
PartitionTower construction
tier structure
state-cell membership
edge/action-cell ownership
source and target relations for tower edges
projection semantics between tiers
```

`jet_simplex_search` owns:

```text
graph loop normalization for simplex degeneracy
directed-flag simplex records
face-edge witness tables
cached frontier intersections
simplex fibers over downstairs simplices
edge-fiber target lookup tables derived from static tower data
small-object simplex enumeration
machine-readable simplex search artifacts
```

Engineering rule:

```text
state_collapser owns the tower.
jet_simplex_search owns simplex enumeration over that tower.
```

The package may create a thin static adapter over `state_collapser` objects, but
that adapter must not reinterpret contraction, projection, cell membership, or
edge source/target semantics.

## First Public API

The first public API should be deliberately small.

Candidate top-level exports:

```python
from jet_simplex_search import __version__
from jet_simplex_search.api import search_simplices
from jet_simplex_search.api import build_static_search_context
```

Candidate main entrypoint:

```python
def search_simplices(
    graph: GraphInput,
    *,
    k: int,
    contraction_schema: object,
    artifact_config: ArtifactConfig | None = None,
) -> SimplexSearchResult:
    ...
```

Expected behavior:

- validate `k >= 0`;
- normalize graph loops for simplex identity arrows;
- build a static `state_collapser` tower;
- choose `G^ell`, the bottommost nondegenerate tier;
- enumerate simplices at `G^ell` directly;
- descend the tower by fiber-addressed lifting;
- return an in-memory `SimplexSearchResult`;
- optionally write machine-readable artifacts.

The first implementation may start with more explicit lower-level functions if
that keeps the code honest:

```python
normalize_graph(...)
build_tower_context(...)
enumerate_bottom_tier(...)
lift_tier_simplices(...)
write_artifact(...)
```

The top-level `search_simplices(...)` can then become a thin orchestration layer.

## Proposed Source Layout

First pass module layout:

```text
src/jet_simplex_search/
  __init__.py
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

Do not introduce subpackages until the module boundaries are stable. The repo is
still small; flat modules are easier to review.

### `ids.py`

Responsibilities:

- define local identifier wrappers or aliases;
- make artifact ids stable and human-readable where practical;
- avoid leaking implementation memory addresses into artifacts.

Candidate ids:

```python
VertexId
EdgeId
TierId
SimplexId
FrontierId
FiberId
```

First implementation can use strings or frozen dataclasses. The important rule
is deterministic artifact identity.

### `graph.py`

Responsibilities:

- define graph input records independent of `state_collapser`;
- support sparse directed graph inputs;
- keep original non-loop edges distinct from formal identity edges;
- provide adjacency lookup material for simplex enumeration.

Candidate records:

```python
@dataclass(frozen=True)
class InputVertex:
    id: str
    payload: object | None = None

@dataclass(frozen=True)
class InputEdge:
    id: str
    source: str
    target: str
    payload: object | None = None
    labels: tuple[object, ...] = ()

@dataclass(frozen=True)
class GraphInput:
    vertices: tuple[InputVertex, ...]
    edges: tuple[InputEdge, ...]
```

Potential later input adapters:

- NetworkX-style edge lists;
- `state_collapser.core.BaseEdge` records;
- JSON graph records;
- CSR-like sparse tables.

These can wait. The core package should first have one explicit input shape.

### `normalize.py`

Responsibilities:

- remove input loops from the first-scope graph semantics;
- add exactly one formal identity edge for every vertex;
- build formal-reflexive adjacency target sets `A(s)`;
- preserve enough metadata to report what was stripped or normalized.

Candidate records:

```python
@dataclass(frozen=True)
class NormalizationPolicy:
    strip_input_loops: bool = True
    add_formal_identities: bool = True

@dataclass(frozen=True)
class NormalizedEdge:
    id: str
    source: str
    target: str
    kind: Literal["original", "identity"]
    original_edge_id: str | None = None

@dataclass(frozen=True)
class NormalizedGraph:
    vertices: tuple[str, ...]
    edges: tuple[NormalizedEdge, ...]
    adjacency_targets: Mapping[str, frozenset[str]]
    edge_lookup: Mapping[tuple[str, str], tuple[str, ...]]
    stripped_loop_edge_ids: tuple[str, ...]
```

Invariants:

- every vertex has exactly one identity edge;
- every identity edge has `source == target`;
- no first-scope original edge has `source == target`;
- `adjacency_targets[s]` includes `s`;
- `adjacency_targets[s]` includes every target of every original edge out of
  `s`;
- if multiple original edges share `(source, target)`, `edge_lookup` preserves
  all witnesses.

### `tower_adapter.py`

Responsibilities:

- convert `NormalizedGraph` into `state_collapser` core records;
- build a static `PartitionTower`;
- expose only the static tower queries simplex search needs;
- avoid reimplementing tower logic.

Candidate adapter:

```python
@dataclass(frozen=True)
class StaticTowerAdapter:
    tower: object
    normalized_graph: NormalizedGraph

    def tiers(self) -> tuple[int, ...]: ...
    def bottommost_nondegenerate_tier(self) -> int: ...
    def tier_vertices(self, tier: int) -> tuple[str, ...]: ...
    def tier_edges(self, tier: int) -> tuple[str, ...]: ...
    def edge_source(self, tier: int, edge_id: str) -> str: ...
    def edge_target(self, tier: int, edge_id: str) -> str: ...
    def project_vertex(self, tier: int, vertex_id: str) -> str: ...
    def project_edge(self, tier: int, edge_id: str) -> str: ...
    def edge_fiber_targets(
        self,
        *,
        upstairs_tier: int,
        downstairs_edge_id: str,
        upstairs_source_id: str,
    ) -> frozenset[str]: ...
```

The concrete implementation should use real `state_collapser` APIs after the
first integration pass. The adapter exists so simplex enumeration can be tested
against a tiny fake tower before the full dependency is wired.

Non-reinvention rule:

```text
Use state_collapser source/docs as the authority for tower semantics.
Do not infer tower semantics from this package's convenience indexes.
```

### `records.py`

Responsibilities:

- define immutable records for simplices, fibers, search results, and summaries;
- keep math-facing fields explicit;
- make artifacts straightforward to serialize.

Candidate records:

```python
@dataclass(frozen=True)
class FaceEdgeWitness:
    source_index: int
    target_index: int
    edge_ids: tuple[str, ...]

@dataclass(frozen=True)
class SimplexRecord:
    id: str
    tier: int
    degree: int
    vertices: tuple[str, ...]
    face_edge_witnesses: tuple[FaceEdgeWitness, ...]
    initial_vertex: str
    target_vertex: str
    prefix_simplex_id: str | None
    last_edge_ids: tuple[str, ...]
    frontier: frozenset[str]
    is_degenerate: bool
    projection_simplex_id: str | None

@dataclass(frozen=True)
class SimplexFiberRecord:
    downstairs_simplex_id: str
    upstairs_tier: int
    upstairs_simplex_ids: tuple[str, ...]

@dataclass(frozen=True)
class EdgeFiberRecord:
    downstairs_edge_id: str
    upstairs_tier: int
    upstairs_source_id: str
    upstairs_target_ids: tuple[str, ...]

@dataclass(frozen=True)
class SimplexSearchResult:
    k: int
    bottom_tier: int
    simplices_by_tier_degree: Mapping[tuple[int, int], tuple[SimplexRecord, ...]]
    fibers: tuple[SimplexFiberRecord, ...]
    diagnostics: SearchDiagnostics
```

Identity rule:

- a simplex record is not only a vertex set;
- it is degree plus ordered vertex address plus face-edge witnesses;
- for simple directed graphs, witnesses may be singleton edge ids;
- for multigraphs, witnesses may contain multiple valid edge ids or the search
  may split them into separate records, but the first implementation must choose
  one policy and test it.

Recommended first policy:

```text
Simplex identity = tier + degree + ordered vertex tuple.
Face-edge witnesses = all matching edge ids for that tuple.
```

This keeps the first implementation compact while preserving witness evidence.
If later mathematics needs one simplex per edge-witness choice in a multigraph,
the artifact already has the witness information needed to identify the change.

### `frontier.py`

Responsibilities:

- compute and cache `F(sigma)`;
- perform sparse intersections;
- keep frontier logic independent from tower lifting.

Core formulas:

```text
A(s) = {s} union outgoing_non_loop_targets(s)
F(s_0, ..., s_m) = A(s_0) cap ... cap A(s_m)
F(sigma) = F(partial_m(sigma)) cap A(tgt(sigma))
```

Candidate functions:

```python
def initial_frontier(graph: NormalizedGraph, vertex_id: str) -> frozenset[str]:
    return graph.adjacency_targets[vertex_id]

def extend_frontier(
    prefix_frontier: frozenset[str],
    target_adjacency: frozenset[str],
) -> frozenset[str]:
    ...
```

Performance rules:

- intersect by iterating over the smaller set;
- preserve deterministic ordering outside the set operation when records are
  emitted;
- cache frontiers on simplex records or a side table keyed by simplex id;
- do not recompute all pairwise face checks for every extension.

### `search.py`

Responsibilities:

- enumerate bottom-tier simplices directly;
- orchestrate tier descent;
- enforce `0 <= degree <= k`;
- collect diagnostics.

Candidate orchestration:

```python
def run_static_small_object_search(context: SearchContext) -> SimplexSearchResult:
    bottom = context.tower.bottommost_nondegenerate_tier()
    enumerate_bottom_tier(context, bottom)
    for tier in descending_tiers_above_base(bottom):
        lift_all_degrees_from_downstairs(context, tier)
    return build_result(context)
```

The exact tier order should match `state_collapser` convention. From the
`state_collapser` docs read during scoping:

```text
tier 0 = finest / total graph
higher tier index = coarser quotient
```

So if `G^ell` is a coarser bottommost nondegenerate tier, descent toward the
original graph moves:

```text
ell - 1, ell - 2, ..., 0
```

The concrete `PartitionTower` adapter must encode this ordering explicitly and
test it against small towers. Do not rely on implicit loop direction or list
ordering in the search code.

### `lift.py`

Responsibilities:

- implement Abdul Malik's fiber-addressed lift search;
- never enumerate arbitrary upstairs extensions and then project-filter them;
- lift dimension-preservingly, including over degenerate downstairs simplices.

Core lifting rule:

Given downstairs simplex:

```text
tau = (c_0, ..., c_m, c_(m+1))
partial tau = (c_0, ..., c_m)
alpha = c_m -> c_(m+1)
```

For every upstairs simplex:

```text
sigma in Fib_r(partial tau)
tgt(sigma) = s_m
```

candidate targets are:

```text
edge_fiber[alpha][s_m] cap F(sigma)
```

Each target emits:

```text
sigma * target
```

as an upstairs simplex over `tau`.

Candidate function:

```python
def lift_downstairs_extension(
    *,
    context: SearchContext,
    upstairs_tier: int,
    downstairs_simplex: SimplexRecord,
    upstairs_prefix: SimplexRecord,
) -> tuple[SimplexRecord, ...]:
    ...
```

Invariants:

- `downstairs_simplex.degree == upstairs_prefix.degree + 1`;
- `upstairs_prefix.projection_simplex_id == downstairs_simplex.prefix_simplex_id`;
- the last edge of every emitted simplex projects to the last edge of
  `downstairs_simplex`;
- the emitted target lies in `F(upstairs_prefix)`;
- emitted simplex degree equals downstairs simplex degree;
- degeneracy is recorded from the emitted ordered vertex tuple and/or identity
  witnesses, not from the nondegenerate spine.

### `artifacts.py`

Responsibilities:

- serialize search results into stable machine-readable artifacts;
- support compact single-file output for tests;
- support manifest-plus-table layout for serious runs;
- avoid serializing unserializable `state_collapser` objects directly.

Candidate config:

```python
@dataclass(frozen=True)
class ArtifactConfig:
    output_dir: Path
    layout: Literal["single_json", "manifest_tables"] = "single_json"
    include_frontier_members: bool = False
    include_full_fiber_members: bool = True
```

Compact test artifact:

```text
readout_source.json
```

Serious artifact layout:

```text
readout_source.json
simplex_records.jsonl
simplex_fibers.jsonl
edge_fibers.jsonl
diagnostics.json
```

Traceability requirement:

Every emitted simplex must be traceable to:

```text
tier
degree
vertex/cell address
face-edge witnesses
projection simplex downstairs
downstairs simplex fiber that caused it to be searched
frontier count
```

### `diagnostics.py`

Responsibilities:

- count emitted simplices by tier and degree;
- count degenerate versus nondegenerate simplices;
- summarize frontier sizes;
- summarize fiber sizes;
- summarize skipped candidates and why, if any;
- track runtime timings when useful.

Candidate record:

```python
@dataclass(frozen=True)
class SearchDiagnostics:
    simplex_counts_by_tier_degree: Mapping[tuple[int, int], int]
    degenerate_counts_by_tier_degree: Mapping[tuple[int, int], int]
    frontier_size_summary: Mapping[tuple[int, int], SummaryStats]
    simplex_fiber_size_summary: Mapping[tuple[int, int], SummaryStats]
    edge_fiber_query_count: int
    emitted_simplex_count: int
```

Do not overbuild metrics in the first pass. The minimum useful diagnostics are
counts and enough fields to debug whether the fiber-addressed search is actually
being used.

### `errors.py`

Responsibilities:

- define package-specific exceptions;
- make invariant failures clear.

Candidate errors:

```python
class JetSimplexSearchError(Exception): ...
class InvalidGraphError(JetSimplexSearchError): ...
class InvalidKError(JetSimplexSearchError): ...
class TowerAdapterError(JetSimplexSearchError): ...
class SimplexInvariantError(JetSimplexSearchError): ...
class ArtifactWriteError(JetSimplexSearchError): ...
```

## Directed Flag Simplex Semantics

First-scope simplex semantics:

```text
An ordered tuple (s_0, ..., s_m) is an m-simplex iff for every i < j,
there exists a directed edge s_i -> s_j.
```

With formal identities:

```text
if s_i == s_j, the edge witness may be id_s
```

This is not merely path enumeration. For example:

```text
0 -> 1 -> 2
```

is not enough for a 2-simplex. The face edge:

```text
0 -> 2
```

must also exist.

Sparse extension works because when appending target `t` to a known simplex
`sigma = (s_0, ..., s_m)`, all new face edges are exactly:

```text
s_0 -> t
s_1 -> t
...
s_m -> t
```

The cached frontier:

```text
F(sigma) = A(s_0) cap ... cap A(s_m)
```

contains precisely the targets satisfying those new face-edge requirements.

## Degeneracy Semantics

Formal identities are part of the one-step arrow set:

```text
Out^1(s) = {id_s} union Out_G(s)
```

Degenerate simplices are generated by ordinary extension:

```text
(s)
(s, s)
(s, s, s)
(s, s, s, s')
```

Degenerate simplices must remain first-class records because:

- arity/degree matters;
- tower lifting is dimension-preserving;
- nondegenerate upstairs simplices can project to degenerate downstairs
  simplices;
- collapsing to a lower-dimensional spine destroys the address needed for fiber
  search.

First implementation degeneracy rule:

```text
is_degenerate = len(set(vertices)) < len(vertices)
```

This is sufficient for the first directed-flag enumerator. Later modes may add
more refined degeneracy provenance if needed.

## Bottom Tier Selection

`G^ell` is the bottommost nondegenerate tier of `G^bullet`.

Operational criterion from the source design:

```text
G^ell is not pi_0, and the next tier is either pi_0 or absent.
```

Implementation sketch:

```python
def bottommost_nondegenerate_tier(adapter: StaticTowerAdapter) -> int:
    for tier in adapter.tiers_from_coarse_to_fine():
        if not adapter.is_pi0(tier):
            return tier
    ...
```

This must be adjusted to `state_collapser`'s tier ordering. The invariant to
preserve is not the loop shape above; it is the mathematical criterion:

```text
select the lowest tier that still has nontrivial simplex structure,
just before the tower becomes pi_0 or ends
```

Tests should pin this with fake and real small towers.

## Bottom-Tier Enumeration Algorithm

At `G^ell`, enumerate directly using the degree-wise `Out` construction.

Pseudo-code:

```text
for each vertex s in tier_vertices(G^ell):
    create 0-simplex (s)
    frontier[(s)] = A(s)

for degree in 0 .. k-1:
    for each simplex sigma in simplices[degree]:
        for each target t in ordered(frontier[sigma]):
            edge_witnesses = face witnesses from each vertex of sigma to t
            create sigma * t
            frontier[sigma * t] = frontier[sigma] cap A(t)
```

Important: for degree 0, this yields:

```text
(s, s) via id_s
(s, t) via original edge s -> t
```

For degree 1, this yields directed triangles only when the long face exists.

Deduplication rule:

- within a tier and degree, dedupe by ordered vertex tuple;
- preserve all face-edge witnesses for that tuple;
- preserve deterministic output ordering.

If multigraph semantics later require one record per witness combination, change
the identity policy deliberately and update artifacts/tests.

## Fiber-Addressed Lift Algorithm

The tower descent algorithm assumes all simplices through degree `k` are already
known at tier `r + 1`. It produces tier `r` simplices only over corresponding
downstairs simplices.

Pseudo-code:

```text
for degree in 0 .. k:
    for each downstairs simplex tau at tier r+1 and degree degree:
        if degree == 0:
            lift vertices over tau
        else:
            prefix_tau = partial(tau)
            alpha = last_edge(tau)
            for each upstairs_prefix in simplex_fiber[prefix_tau] at tier r:
                source = tgt(upstairs_prefix)
                candidates = edge_fiber[alpha][source] cap frontier[upstairs_prefix]
                for target in candidates:
                    emit upstairs_prefix * target over tau
```

Degree-zero lifting:

```text
Fib_r((C)) = vertices/cells at tier r that project to C
```

Degree-one lifting:

```text
Fib_r((C0, C1)) =
  edges at tier r whose source projects to C0 and target projects to C1
```

Higher-degree lifting then uses the prefix/final-edge recurrence.

Do not perform:

```text
all upstairs sigma candidates
  -> project sigma
  -> compare with downstream tau
```

That is the explicitly rejected slow version.

## State And Edge Ordering

Deterministic ordering matters for tests, artifacts, and reproducibility.

Recommended ordering:

- vertices ordered by stable id;
- edges ordered by stable id;
- simplices ordered lexicographically by `(tier, degree, vertices, id)`;
- fibers ordered by downstairs simplex id, then upstairs simplex id;
- artifact files sorted by stable ids, not insertion order from sets.

Set operations can use `frozenset` internally, but emission must be sorted.

## Artifact Contract

First artifact fields:

```text
manifest
  schema_version
  package_version
  state_collapser_version
  input_graph_fingerprint
  k
  contraction_schema
  loop_normalization
  artifact_layout

tier_summary
  tier
  vertex_count
  edge_count
  is_pi0
  is_bottommost_nondegenerate

simplex_records
  id
  tier
  degree
  vertices
  face_edge_witnesses
  initial_vertex
  target_vertex
  prefix_simplex_id
  last_edge_ids
  frontier_count
  frontier_members optional
  is_degenerate
  projection_simplex_id

simplex_fibers
  downstairs_simplex_id
  upstairs_tier
  upstairs_simplex_ids or shard_ref
  count

edge_fibers
  downstairs_edge_id
  upstairs_tier
  upstairs_source_id
  upstairs_target_ids or shard_ref
  count

diagnostics
  counts
  timings optional
  memory optional
```

Artifact invariant:

```text
Every simplex record must be auditable back to face-edge witnesses and, for
non-bottom tiers, to the downstairs simplex fiber that caused the search.
```

## Testing Blueprint

Tests should start small and invariant-heavy.

### `tests/test_package.py`

Already exists as import smoke.

Keep it minimal.

### `tests/test_normalize.py`

Cases:

- graph with no loops gets one identity per vertex;
- graph with input loops strips them under first policy;
- original non-loop edges are preserved;
- adjacency target set contains self plus outgoing targets;
- stripped loop ids are recorded.

### `tests/test_frontier.py`

Cases:

- `F(s) = A(s)`;
- `F(s, t) = A(s) cap A(t)`;
- repeated vertex leaves frontier unchanged;
- frontier extension equals full recomputation;
- intersection output is deterministic at emission.

### `tests/test_directed_flag_semantics.py`

Cases:

- path `0 -> 1 -> 2` without `0 -> 2` does not emit a 2-simplex;
- adding `0 -> 2` emits `(0, 1, 2)`;
- identity edges emit `(s, s)` and `(s, s, s)`;
- `(s, s, t)` requires `s -> t` and uses identity witnesses for repeated
  positions.

### `tests/test_bottom_tier_enumeration.py`

Cases:

- one isolated vertex emits degenerates through `k`;
- one edge emits all expected degenerate and nondegenerate degree-1 records;
- triangle emits expected degree-2 records;
- no degree above `k` is emitted;
- records carry prefix, target, frontier, and witnesses.

### `tests/test_tower_adapter_fake.py`

Use a fake static tower adapter to test search without relying on
`state_collapser` internals.

Cases:

- adapter exposes tiers, projections, and edge fibers;
- degree-zero fibers lift vertices;
- edge fibers are source-sensitive;
- missing query raises `TowerAdapterError`.

### `tests/test_fiber_lift.py`

Cases:

- upstairs search only runs over a known downstairs simplex;
- final downstairs edge selects the upstairs edge fiber;
- candidates are intersected with frontier;
- emitted simplex projects to the downstairs simplex;
- nondegenerate upstairs simplex over degenerate downstairs simplex is emitted;
- arbitrary upstairs candidate that does not sit over the downstairs final edge
  is never considered.

### `tests/test_artifacts.py`

Cases:

- compact JSON artifact writes and reloads;
- every simplex has required traceability fields;
- manifest-plus-table layout writes expected files;
- count-only/shard references are valid for omitted large memberships;
- artifact does not try to serialize live `state_collapser` objects.

### `tests/integration/test_state_collapser_static_tower.py`

This should be added only when `state_collapser` is declared as a dependency.

Cases:

- tiny graph builds a real `PartitionTower`;
- adapter reads real tier vertices and edges;
- simple contraction produces a degenerate downstairs simplex;
- fiber lift emits expected upstairs simplex records.

## Implementation Phases

### Phase 0: Package Skeleton

Already started:

```text
pyproject.toml
src/jet_simplex_search/__init__.py
tests/test_package.py
uv run pytest
```

Next in this phase:

- decide when to add `state_collapser` as a dependency;
- keep package import smoke passing.

### Phase 1: Local Graph And Normalization

Implement:

```text
graph.py
normalize.py
errors.py
```

Tests:

```text
test_normalize.py
```

Done when:

- input graph can be normalized;
- exactly one formal identity exists per vertex;
- adjacency target sets are correct;
- loop policy is tested.

### Phase 2: Simplex Records And Bottom-Tier Enumeration

Implement:

```text
ids.py
records.py
frontier.py
search.py bottom-tier direct enumeration
```

Tests:

```text
test_frontier.py
test_directed_flag_semantics.py
test_bottom_tier_enumeration.py
```

Done when:

- all directed flag simplices through `k` can be enumerated in one normalized
  graph/tier;
- degenerates are emitted;
- face-edge witnesses are present;
- frontier recurrence is tested against full recomputation.

### Phase 3: Fake Tower Adapter And Fiber Lift

Implement:

```text
tower_adapter.py fake/test adapter protocol
lift.py
search.py tier descent orchestration
```

Tests:

```text
test_tower_adapter_fake.py
test_fiber_lift.py
```

Done when:

- tier `r` search is fiber-addressed by tier `r + 1` simplices;
- final-edge fiber targeting is enforced;
- nondegenerate-over-degenerate lift examples pass;
- rejected post-filter search pattern is absent from implementation.

### Phase 4: Real state_collapser Integration

Add dependency and implement real adapter.

Likely `pyproject.toml` dependency shape while local:

```toml
[project]
dependencies = [
  "state-collapser",
]
```

If the package is not published, use a local path during development according
to the repo's dependency policy.

Done when:

- a tiny graph builds a real `state_collapser` static `PartitionTower`;
- adapter consumes real tower data;
- no tower semantics are duplicated;
- integration tests pass.

### Phase 5: Artifacts

Implement:

```text
artifacts.py
diagnostics.py
```

Tests:

```text
test_artifacts.py
```

Done when:

- compact test artifact writes;
- manifest-plus-table artifact writes;
- simplex traceability is complete;
- diagnostics summarize counts by tier and degree.

### Phase 6: Public API

Implement:

```text
api.py
search_simplices(...)
build_static_search_context(...)
```

Done when:

- top-level search path works end to end;
- README can show a tiny example;
- docs link the initial design note and this blueprint;
- public API remains small.

## Performance Notes

Expected hot operations:

```text
frontier intersection
edge_fiber_targets cap frontier
simplex record emission
artifact writing
```

First optimizations:

- represent frontiers as `frozenset` for correctness, maybe sorted tuples for
  deterministic emission;
- intersect smaller set into larger set;
- cache `A(s)` and `F(sigma)`;
- avoid allocating face-edge witness structures until candidate target survives
  frontier and fiber checks;
- keep artifact streaming possible.

Do not prematurely implement:

- bitsets;
- CSR matrix kernels;
- multiprocessing;
- database-backed artifact storage;
- GPU/tensor paths.

Those may come later if the simple implementation proves the invariants.

## Review Checklist

Before merging the first real implementation, verify:

- Abdul Malik attribution is preserved in docs;
- `state_collapser` owns tower semantics;
- graph normalization emits exactly one identity per vertex;
- directed flag condition requires all face edges;
- degenerates are first-class records;
- `F(sigma)` uses the inductive recurrence;
- bottom-tier enumeration includes degenerates through `k`;
- tower descent searches only over known downstairs simplex fibers;
- final-edge fiber targeting is enforced;
- artifacts can trace every simplex to witnesses and projection/fiber data;
- `uv run pytest` passes.

## Future Design Tracks

### Kan Replacement

The Kan version should be designed separately.

Current contrast:

```text
small-object/static version:
  enumerate full directed flag simplices

Kan version:
  enumerate composable paths / horns
  search for inner horn fillers
```

The Kan path should not be mixed into the first implementation.

### Meaningful Non-Identity Input Loops

First scope strips input loops and adds canonical identities. Future graph
formats may need:

```text
id_s                 formal degeneracy arrow
lambda : s -> s      ordinary non-identity loop
```

That requires an explicit loop policy change.

### Multigraph Witness Semantics

First scope can keep one simplex per ordered vertex tuple while recording all
face-edge witnesses. Future modes may require one simplex per witness choice.

That should be a deliberate API/artifact version change.

### Large Graph Artifacts

Manifest-plus-table layout is the first serious path. Very large graphs may
later need:

- compressed JSONL;
- SQLite/DuckDB artifacts;
- count-only summaries with reproducible shard refs;
- sampled human-readable readouts.

Do not build those before first correctness tests pass.
