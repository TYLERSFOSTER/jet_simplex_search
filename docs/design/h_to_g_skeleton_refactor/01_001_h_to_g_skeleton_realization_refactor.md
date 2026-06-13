# H-To-G Skeletonization And H-Realization Refactor

## Status

Initial refactor design from the Project Owner discussion on June 13, 2026.

This document records a proposed refactor of `jet_simplex_search` after the
synthetic_blow review in:

```text
code_review/synthetic_blow_project_review.md
```

The key design shift is:

```text
Do not run the tower search directly over an arbitrary multigraph H.
First collapse H to a simple-reflexive search skeleton G.
Run the quotient-tower simplex search over G.
Then post-process tier-0 skeleton simplices back against H multiplicities.
```

This is a refactor of the current package, not a second package and not a new
algorithmic framework.

## Attribution

The static quotient-tower simplex search algorithm is PM Abdul Malik's work and
part of his thesis. This includes the degree-wise frontier recurrence,
degenerate simplex treatment, static tower pipeline, and fiber-addressed
small-object lift search.

The Project Owner introduced the `H -> G ~= G^0 -> ... -> G^d` refactor in the
June 13, 2026 discussion: preprocess an arbitrary graph `H` into a
multiplicity-free and loop-normalized skeleton `G`, search `G`, and then
post-process the found skeleton simplices back against `H`.

Codex's role here is consultant synthesis: translating the refactor discussion
and synthetic_blow complaints into an implementation-facing design note. This
document is not a replacement for the mathematical source of the algorithm.

## Motivation

The current implementation accepts a `GraphInput`, normalizes loops, and then
enumerates directed flag simplices using edge lookup data that may contain
parallel edges. That created a real design tension:

```text
The search should be sparse and address-based.
But the witness records can carry multiplicity-level edge ids.
```

The synthetic_blow review found the dangerous version of this tension:

```text
Simplex address can be correct.
Witness edge evidence can still be false or misleading.
```

The Project Owner's refactor resolves this by separating two concepts that were
previously mixed:

1. The skeleton address search.
2. The original-graph realization count.

The tower search should operate on the simple skeleton `G`, not directly on the
arbitrary graph `H`. Multiplicity belongs in a separate `H`-fiber metadata layer
and in a post-processing realization pass.

## Core Diagram

The intended pipeline is:

```text
H  -- et q -->  G ~= G^0 -> G^1 -> G^2 -> ... -> G^d
```

Where:

- `H` is the arbitrary input graph.
- `H` may have loops.
- `H` may have parallel non-loop edges.
- `q` is the preprocessing quotient map from `H` to the skeleton `G`.
- `G` is the multiplicity-free search graph.
- `G` has one simple non-loop edge for each non-loop endpoint pair appearing in
  `H`.
- `G` has exactly one formal identity at each vertex in the reflexive search
  view.
- `G ~= G^0` is the top tier of the static quotient tower.
- Every exposed `G^r` tier used by simplex search should be simple-reflexive:
  no original loops, no parallel search edges, exactly one formal identity per
  vertex in the search view.

The phrase "simple-reflexive" is used deliberately:

```text
simple:
  at most one non-identity edge for each ordered pair of distinct vertices

reflexive:
  one formal identity option at each vertex for degenerate simplex generation

not included:
  original H loops as ordinary tower/search edges
  parallel H multiplicities as tower/search edges
```

## Design Thesis

The refactor should make the package say one simple thing:

```text
Search addresses in G.
Count realizations in H.
```

This means:

- The quotient tower is built from `G`, not from `H`.
- The direct simplex enumerator sees one edge per endpoint pair.
- The lift engine sees simple tier graphs.
- Multiplicity explosion is delayed until post-processing.
- Post-processing defaults to compressed counts, not full witness expansion.
- The public API can report both skeleton addresses and `H`-realization counts.

## Synthetic_Blow Constraints

The redesign should answer the review complaints without adding needless
machinery.

### Direct Code Over Framework

Add concrete records and functions:

```text
skeletonize_graph
compute_h_realizations
```

Do not add:

```text
SkeletonizationEngine
RealizationManager
MultiplicityStrategyRegistry
PipelineOrchestrator
```

There is one real pipeline. Write it directly.

### Keep Data Visible

The important data should be inspectable:

```text
H edge fibers by endpoint pair
H loop fibers by vertex
simple skeleton graph G
tier simple edge fibers by quotient endpoint pair
skeleton simplex records
H-realization factors per simplex
H-realization count per simplex
```

If a future programmer cannot inspect those tables, the design failed.

### No False Evidence

The package should stop pretending that a skeleton edge witness is the same kind
of object as an original `H` edge witness.

After the refactor:

```text
SimplexRecord.face_edge_witnesses:
  evidence that the skeleton face exists in G or G^r

HRealizationRecord.face_factors:
  evidence/count data for how many H witnesses realize each skeleton face
```

Those are different layers.

### Avoid Eager Multiplicity Explosion

Parallel edges across a simplex multiply. Degenerate repeated faces multiply.
Full expansion can become enormous.

The default result should carry counts and compressed factor tables. Enumerating
every original witness assignment should be opt-in and capped.

## Existing Architecture To Preserve

The current package is small and useful. The refactor should preserve as much of
the direct architecture as possible.

Current modules:

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

Preserve:

- `GraphInput`, `InputVertex`, `InputEdge` as the raw input shape.
- `normalize_graph` as the formal-identity/reflexive search normalizer, but feed
  it a skeleton graph instead of arbitrary `H`.
- `enumerate_direct_simplices` as the direct skeleton enumerator.
- `extend_frontier` and cached frontier recurrence.
- `lift_tier_simplices` as the small-object tower lifting loop.
- `StateCollapserStaticTowerAdapter` as the `state_collapser` boundary.
- `SimplexRecord` as the skeleton simplex record.
- JSON/JSONL artifact support.

Refactor:

- Add an explicit `H -> G` skeletonization stage before tower construction.
- Ensure tier views exposed by the adapter are simple-reflexive.
- Add post-processing records for `H` realization counts.
- Add diagnostics for skeletonization and realization counts.
- Update public API semantics to make skeleton-vs-realization explicit.

Avoid:

- Subpackages unless module size forces them.
- Abstract base classes with one implementation.
- Callback hooks.
- Pluggable realization engines.
- Stringly typed dynamic imports.

## Terminology

### Raw Graph `H`

The user's input graph.

Properties:

- directed;
- sparse preferred;
- may contain loops;
- may contain parallel edges;
- edge ids are unique;
- vertex ids are unique;
- labels and payloads may exist on vertices and edges.

### Skeleton Graph `G`

The graph produced from `H` by the preprocessing quotient `q`.

Properties:

- same vertex set as `H` in first scope;
- at most one non-loop edge for each ordered endpoint pair `(s, t)` with
  `s != t`;
- original loops in `H` are not ordinary non-identity edges in `G`;
- the search view of `G` has exactly one formal identity at each vertex;
- every skeleton non-loop edge has a fiber of one or more original `H` edge ids;
- every skeleton identity has a loop fiber of zero or more original `H` loop ids.

### Reflexive Search View

The graph view used by the simplex engine:

```text
A(s) = {s} union {t : s -> t is a skeleton non-loop edge}
```

This is what `normalize_graph` already approximates by stripping input loops and
adding formal identity edges.

### `H`-Realization

An `H`-realization of a skeleton simplex is a choice of original `H` witness
edge for each directed face occurrence of the skeleton simplex.

For simplex:

```text
sigma = (v_0, ..., v_m)
```

the face occurrences are:

```text
(v_i -> v_j) for all 0 <= i < j <= m
```

Each face occurrence gets a factor:

```text
if v_i != v_j:
  factor = number of original H edges from v_i to v_j

if v_i == v_j:
  factor = number of original H loops at v_i
```

under the default Project Owner interpretation.

The `H`-realization count is:

```text
product of all face occurrence factors
```

## Important Semantic Decision: Degenerate Realizations

The Project Owner said:

```text
allowing degeneracies at loops that happen to be present in H
```

This design treats that as the default realization policy:

```text
Formal identities are search-only.
Original H loops are required for positive H-realization of degenerate faces.
```

Therefore:

```text
H has no loop at s
sigma = (s, s)
G-search emits sigma as a skeleton degenerate address
H-realization count of sigma is 0
```

and:

```text
H has 3 loops at s
sigma = (s, s)
H-realization count of sigma is 3
```

For higher degenerates, face occurrences are independent by default:

```text
sigma = (s, s, s)
faces:
  (0,1): s -> s
  (0,2): s -> s
  (1,2): s -> s

if H has L loops at s:
  count_H(sigma) = L^3
```

This is not the only possible simplicial convention. It is the one that matches
the Project Owner's "loops that happen to be present in H" phrasing and the
synthetic_blow demand for explicit data semantics.

If a later version wants formal simplicial degeneracies to count as one even
without `H` loops, that should be a separate named policy, not an implicit
behavior.

## Multiplicity Examples

### Single Non-Loop Edge Fiber

Input `H`:

```text
a -> b has 5 parallel edges
```

Skeleton `G`:

```text
a -> b has 1 skeleton edge
edge_fiber_H[(a,b)] has 5 original edge ids
```

Skeleton simplex:

```text
(a, b)
```

Realization count:

```text
5
```

### Triangle With Parallel Multiplicities

Input `H`:

```text
|H(a,b)| = 2
|H(a,c)| = 3
|H(b,c)| = 5
```

Skeleton `G` has one edge for each pair.

Skeleton 2-simplex:

```text
(a, b, c)
```

Realization count:

```text
2 * 3 * 5 = 30
```

### Degenerate Edge With Missing Original Loop

Input `H`:

```text
no loop at s
```

Skeleton search view has formal `id_s`.

Skeleton simplex:

```text
(s, s)
```

Realization count:

```text
0
```

The skeleton address exists. It has no positive `H` realization under the default
loop policy.

### Degenerate 2-Simplex With One Loop And Parallel Edge

Input `H`:

```text
|Loop_H(s)| = 2
|H(s,t)|    = 4
```

Skeleton simplex:

```text
(s, s, t)
```

Face occurrences:

```text
(0,1): s -> s
(0,2): s -> t
(1,2): s -> t
```

Realization count:

```text
2 * 4 * 4 = 32
```

This illustrates why the post-processing count can be much larger than the
skeleton simplex count.

### Degenerate 2-Simplex With Repeated Target

Input `H`:

```text
|H(s,t)|    = 4
|Loop_H(t)| = 3
```

Skeleton simplex:

```text
(s, t, t)
```

Face occurrences:

```text
(0,1): s -> t
(0,2): s -> t
(1,2): t -> t
```

Realization count:

```text
4 * 4 * 3 = 48
```

Again, repeated non-loop face occurrences are independent by default.

## High-Level Pipeline

### Current Pipeline

The current implementation effectively does:

```text
GraphInput
  -> normalize_graph
  -> StateCollapserStaticTowerAdapter.from_graph
  -> run_static_small_object_search
  -> SimplexSearchResult
```

That means arbitrary `H` multiplicity can leak into search records.

### Refactored Pipeline

The proposed implementation should do:

```text
GraphInput H
  -> skeletonize_graph(H)
       skeleton GraphInput G_raw
       H edge fibers
       H loop fibers
       q maps from H edges to G edges/formal identities
  -> build tower from G_raw
  -> expose each tower tier as a simple-reflexive tier view
  -> run_static_small_object_search over the simple tier views
  -> extract tier-0 skeleton simplices
  -> compute H-realization records for tier-0 skeleton simplices
  -> return combined result
  -> optionally write combined artifact
```

The tower search remains the same kind of search. The new work is before and
after it.

## Stage 1: Skeletonization Of `H`

### Input

Use the existing `GraphInput`:

```python
GraphInput(
    vertices=(InputVertex(...), ...),
    edges=(InputEdge(...), ...),
)
```

No new raw graph type is required in first scope.

### Output

Add a skeletonization result record.

Candidate:

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
    collapsed_parallel_edge_count: int
    vertices_with_original_loops: int
    label_conflict_count: int

@dataclass(frozen=True, slots=True)
class SkeletonizationResult:
    skeleton_graph: GraphInput
    edge_fibers_by_pair: Mapping[tuple[str, str], SkeletonEdgeFiber]
    loop_fibers_by_vertex: Mapping[str, SkeletonLoopFiber]
    skeleton_edge_id_by_pair: Mapping[tuple[str, str], str]
    skeleton_edge_id_by_original_edge_id: Mapping[str, str]
    formal_identity_vertex_by_original_loop_edge_id: Mapping[str, str]
    diagnostics: SkeletonizationDiagnostics
```

The exact field names can be tightened during implementation, but the data has
to be explicit.

### Skeleton Edge IDs

Skeleton edge ids must be deterministic and collision-resistant.

Candidate:

```text
jss:skeleton-edge:<escaped-source>:<escaped-target>
```

For example:

```text
jss:skeleton-edge:a:b
```

Use the existing escaping helpers in `ids.py` or add a public helper there. Do
not rely on edge insertion order for skeleton ids.

### Loop Handling

For each input edge:

```text
edge.source == edge.target
```

do not put that edge into `skeleton_graph.edges`.

Instead:

```text
loop_fibers_by_vertex[edge.source].original_loop_edge_ids += edge.id
formal_identity_vertex_by_original_loop_edge_id[edge.id] = edge.source
```

The formal identity is added later by `normalize_graph`.

### Non-Loop Multiplicity Handling

For each input edge:

```text
edge.source != edge.target
```

group by:

```text
(edge.source, edge.target)
```

For each nonempty group:

1. Add one skeleton edge to `skeleton_graph`.
2. Store all original edge ids in the `SkeletonEdgeFiber`.
3. Store the map from each original edge id to the skeleton edge id.

### Label Handling

This is the most dangerous detail in preprocessing.

The current package passes labels into `state_collapser` actions. If two
parallel `H` edges have different labels, collapsing them into one skeleton edge
creates an ambiguity:

```text
Which labels should the skeleton edge carry?
```

Do not silently guess.

First-scope policy:

```text
If all non-loop edges in a fiber have identical label tuples:
  skeleton edge uses that label tuple.

If labels differ inside a fiber:
  raise an explicit InvalidGraphError unless the caller provides an explicit
  label merge policy.
```

This is conservative and synthetic_blow-friendly. Silent union or intersection
of labels can change contraction behavior without being obvious.

Future optional policy:

```python
class SkeletonLabelPolicy(Enum):
    REQUIRE_IDENTICAL = "require_identical"
    UNION = "union"
```

Do not add custom callback policy in first scope unless a real use case forces
it. A callback would be a footgun here.

### Vertex Payloads

Keep vertex ids and payloads from `H`.

If duplicate vertex ids exist, existing `GraphInput` validation already rejects
them.

### Skeletonization Invariants

After skeletonization:

```text
for every skeleton edge e:
  e.source != e.target

for every ordered pair (s,t), s != t:
  at most one skeleton edge exists

for every original non-loop edge h:
  skeleton_edge_id_by_original_edge_id[h.id] exists

for every original loop edge h:
  formal_identity_vertex_by_original_loop_edge_id[h.id] exists

for every skeleton edge fiber:
  len(original_edge_ids) >= 1

for every vertex:
  loop_fibers_by_vertex[vertex].original_loop_edge_ids may be empty
```

## Stage 2: Reflexive Normalization Of `G`

The existing `normalize_graph` should still be used, but now its input is
already a skeleton graph.

After normalization:

```text
NormalizedGraph.edges =
  one identity edge per vertex
  one non-loop skeleton edge per non-loop endpoint pair
```

After this refactor, `NormalizedGraph.edge_lookup[(s,t)]` should have:

```text
len(edge_lookup[(s,t)]) == 1
```

for every key in the skeleton search graph, including identities.

This makes direct witness records safe at the skeleton layer. They are skeleton
witnesses, not original `H` witness ids.

### Needed Normalization Test

Add a test:

```text
H has three parallel edges a -> b and two loops at a.
skeletonize_graph(H).skeleton_graph has one non-loop edge a -> b and no loops.
normalize_graph(skeleton_graph) has one formal identity at a and one edge a -> b.
```

## Stage 3: Static Tower Built From `G`

`StateCollapserStaticTowerAdapter.from_graph` should receive `G`, not `H`.

Current high-level public API:

```python
search_simplices(graph=graph_h, contraction_schema=schema, k=k)
```

Refactored orchestration:

```python
skeleton = skeletonize_graph(graph_h)
adapter = StateCollapserStaticTowerAdapter.from_graph(
    skeleton.skeleton_graph,
    schema=contraction_schema,
)
skeleton_result = run_static_small_object_search(adapter, k=k)
realizations = compute_h_realizations(
    skeleton_result=skeleton_result,
    skeletonization=skeleton,
    tier=0,
)
```

The public function can still be named `search_simplices`, but the result should
make clear that the search happened over `G` and the realization counts refer to
`H`.

## Stage 4: Simple Tier Views

Preprocessing only guarantees that `G^0` is simple before building the tower.
After quotienting, multiple action cells may end up between the same quotient
source and quotient target.

The Project Owner's requirement is stronger:

```text
Every G^r exposed to simplex search is multiplicity- and loop-normalized.
```

Therefore the adapter should expose a simple-reflexive tier view, even if the
underlying `state_collapser` tower contains multiple action cells between the
same quotient cells.

### Current Adapter Behavior

Currently `StateCollapserStaticTowerAdapter.tier_edges(tier)` returns action-cell
edge ids:

```text
action:<tier>:<ordinal>
```

Those can behave like multiplicity-level edges from the viewpoint of simplex
search.

### Refactored Adapter Behavior

Add a tier view layer:

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

The adapter can still query `state_collapser` action cells internally. But the
simplex search should see only:

```text
one non-identity edge per ordered source-target pair
one formal identity per vertex through normalize_graph
```

### Tier Simple Edge IDs

Candidate id:

```text
jss:tier-edge:t<tier>:<escaped-source>:<escaped-target>
```

This gives stable ids independent of action-cell ordinal multiplicity.

### Projection Of Simple Tier Edges

For a simple tier edge:

```text
e: u -> v in tier r
```

project endpoints:

```text
u' = project_vertex(r, u)
v' = project_vertex(r, v)
```

Then:

```text
if u' == v':
  project_edge(e) = formal identity at u'
else:
  project_edge(e) = simple tier edge id for (u', v') in tier r + 1
```

This avoids relying on one arbitrary action-cell representative to define the
simple search edge projection.

### Simple Tier View Invariants

For each tier view:

```text
for every non-identity edge:
  source != target

for every ordered pair (source,target), source != target:
  at most one simple tier edge exists

for every action cell edge exposed by state_collapser:
  it belongs to exactly one simple tier edge fiber, or is ignored for a documented reason

for every simple tier edge:
  action_cell_edge_ids is nonempty
```

For projection:

```text
project_edge(simple_edge) is determined by projected endpoints
```

not by arbitrary action-cell identity.

## Stage 5: Skeleton Search

Once every tier view is simple-reflexive, the current search machinery becomes
much less suspicious.

`extend_simplex_direct` can continue to use:

```python
graph.edge_lookup[(source, target)]
```

because in a skeleton/tier view that lookup has at most one edge id.

The witness record now means:

```text
This face exists in the simple skeleton tier.
```

It does not mean:

```text
This is an original H edge witness.
```

That distinction should be stated in code comments/docstrings and artifacts.

### Bottom Tier Enumeration

No conceptual change:

```text
enumerate_direct_simplices(bottom_graph, tier=bottom_tier, k=k)
```

still uses:

```text
F(sigma) = F(partial sigma) cap A(tgt sigma)
```

### Tower Lifting

No conceptual change:

```text
for downstairs simplex tau:
  for upstairs prefix sigma over partial tau:
    restrict candidates by final edge fiber of tau
    intersect with sigma.frontier
```

But the edge fiber now lives between simple tier edges, not action-cell
multiplicities.

The old synthetic_blow complaint that "target-only edge fiber loses edge
identity" is no longer a correctness blocker if the adapter enforces simple tier
views. There is no parallel search edge identity to lose.

The performance complaint still remains:

```text
Do not scan all tier edges on every edge-fiber query.
Index simple tier edge fibers by downstream simple edge and source.
```

## Stage 6: Post-Processing `G^0` Simplices Against `H`

Post-processing should focus on tier `0`, because `H` maps to `G ~= G^0`.
Downstream quotient tier simplices are useful diagnostics and lift machinery,
but they do not have direct `H` endpoint fibers unless a later design defines
quotient-level `H` realization semantics.

### Tier-0 Vertex Identity

Current adapter vertex ids are state-cell strings like:

```text
cell:0:0
```

But `H` fibers are keyed by original vertex ids like:

```text
a
b
c
```

The refactor must provide a deterministic map:

```text
tier0_simple_vertex_id -> skeleton vertex id -> H vertex id
```

Possible implementation:

```python
StateCollapserStaticTowerAdapter.tier0_vertex_payload_id(vertex_id: str) -> str
```

or a map in the result:

```python
tier0_vertex_id_to_input_vertex_id: Mapping[str, str]
```

For tier 0, each state cell should be a singleton over one original skeleton
state. Assert that. If it is not singleton, fail loudly, because `G^0` is no
longer the intended top tier.

### Realization Records

Candidate records:

```python
@dataclass(frozen=True, slots=True)
class FaceRealizationFactor:
    source_index: int
    target_index: int
    source_vertex_id: str
    target_vertex_id: str
    skeleton_edge_id: str
    original_edge_ids: tuple[str, ...]
    factor: int
    is_loop_factor: bool

@dataclass(frozen=True, slots=True)
class SimplexHRealizationRecord:
    simplex_id: str
    tier: int
    degree: int
    skeleton_vertices: tuple[str, ...]
    input_vertices: tuple[str, ...]
    face_factors: tuple[FaceRealizationFactor, ...]
    realization_count: int
    is_realized_in_h: bool
```

`realization_count` should use Python `int`, not `float`.

### Count Algorithm

For each tier-0 skeleton simplex:

```python
count = 1
factors = []

for target_index in range(1, len(vertices)):
    for source_index in range(target_index):
        source = input_vertices[source_index]
        target = input_vertices[target_index]

        if source == target:
            original_ids = loop_fibers_by_vertex[source].original_loop_edge_ids
            is_loop = True
        else:
            original_ids = edge_fibers_by_pair[(source, target)].original_edge_ids
            is_loop = False

        factor = len(original_ids)
        count *= factor
        factors.append(...)
```

The factor lookup should not silently default to one. If a non-loop factor is
missing for a skeleton simplex, that is an invariant error: the skeleton search
found an edge that skeletonization says does not exist.

Loop factors may be zero under the default `REQUIRE_H_LOOP` policy.

### Zero-Count Skeleton Simplices

A skeleton simplex can have:

```text
realization_count == 0
```

This is not a search failure. It is the intended restriction part of the
post-processing stage.

The result should keep zero-count skeleton records by default, because they are
useful evidence:

```text
G allowed this formal degenerate address.
H did not realize it because H had no loop.
```

Public summaries can separately report:

```text
skeleton simplex count
positive H-realized simplex address count
total H witness realization count
```

## Result Model

The current result:

```python
SimplexSearchResult
```

contains skeleton/tower search data.

Do not overload it until it becomes unreadable. First-scope refactor can add a
wrapper result:

```python
@dataclass(frozen=True, slots=True)
class SkeletonRealizationSearchResult:
    skeletonization: SkeletonizationResult
    skeleton_search: SimplexSearchResult
    h_realizations: tuple[SimplexHRealizationRecord, ...]
    realization_diagnostics: RealizationDiagnostics
```

Possible public API:

```python
def search_simplices(
    *,
    graph: GraphInput,
    contraction_schema: object | None = None,
    k: int,
    artifact_config: ArtifactConfig | None = None,
) -> SkeletonRealizationSearchResult:
    ...
```

To preserve existing lower-level tests:

```python
def run_static_small_object_search(
    adapter: StaticTowerAdapterProtocol,
    *,
    k: int,
) -> SimplexSearchResult:
    ...
```

can remain the skeleton/tower core.

This split is direct:

```text
public graph-H API returns H-aware result
internal adapter API returns skeleton-only result
```

No inheritance is needed.

## Diagnostics

Add skeletonization diagnostics:

```text
input vertices
input edges
input loops
input non-loop edges
skeleton non-loop edges
parallel edges collapsed
vertices with loops
label conflicts
```

Add realization diagnostics:

```text
tier-0 skeleton simplex count by degree
positive H-realized simplex address count by degree
zero-count skeleton simplex address count by degree
total H-realization count by degree
maximum simplex realization count by degree
mean positive simplex realization count by degree
maximum face factor by degree
```

Important distinction:

```text
positive H-realized simplex address count:
  number of skeleton simplex addresses with realization_count > 0

total H-realization count:
  sum of realization_count over those addresses
```

For example, one skeleton triangle can contribute 30 total `H` realizations.

## Artifact Contract

Artifacts should make the two layers visible.

For `single_json`:

```json
{
  "manifest": {},
  "skeletonization": {},
  "skeleton_search": {},
  "h_realizations": [],
  "diagnostics": {}
}
```

For `manifest_tables`:

```text
readout_source.json
skeleton_edge_fibers.jsonl
skeleton_loop_fibers.jsonl
simplex_records.jsonl
simplex_fibers.jsonl
edge_fibers.jsonl
h_realizations.jsonl
h_realization_face_factors.jsonl
diagnostics.json
```

Do not write full witness assignment expansions by default.

Optional future expansion artifact:

```text
h_realization_witness_assignments.jsonl
```

should require:

```text
include_expanded_h_witnesses=True
max_expanded_h_witnesses=N
```

and should fail or truncate explicitly if the cap is exceeded.

## Public API Semantics

The package name and main concept remain the same, but documentation must say
what is counted.

Suggested language:

```text
jet_simplex_search searches a simple-reflexive skeleton G of the input graph H
using a static quotient tower. It then computes how each tier-0 skeleton simplex
is realized by the original loops and parallel edges in H.
```

Avoid saying:

```text
The tower searches all H multiplicity witnesses.
```

That is not what the refactor does.

## Module Plan

Keep the flat package layout.

Add:

```text
src/jet_simplex_search/skeleton.py
src/jet_simplex_search/realizations.py
```

Possible responsibilities:

### `skeleton.py`

```text
SkeletonEdgeFiber
SkeletonLoopFiber
SkeletonizationDiagnostics
SkeletonizationResult
skeleton_edge_id
skeletonize_graph
assert_skeletonization_invariants
```

### `realizations.py`

```text
FaceRealizationFactor
SimplexHRealizationRecord
RealizationDiagnostics
compute_h_realizations
summarize_h_realizations
```

Modify:

### `api.py`

- Orchestrate `H -> G -> tower -> G-search -> H-realizations`.
- Keep lower-level adapter path available for tests and advanced users.
- Avoid `StaticSearchContext` unless it starts carrying meaningful state.

### `normalize.py`

- Keep formal identity behavior.
- Add or strengthen invariant tests for skeleton input:

```text
edge_lookup has exactly one edge per endpoint pair
```

when called after skeletonization.

### `tower_adapter.py`

- Build tower from skeleton graph.
- Expose simple tier views.
- Add indexing for simple edge fibers.
- Add tier-0 input vertex mapping.

### `records.py`

- Either keep new realization records in `realizations.py`, or move them here if
  the project prefers one record module. Do not duplicate definitions.

### `artifacts.py`

- Serialize skeletonization and H-realization data.
- Keep old tables for skeleton/tower records.

### `diagnostics.py`

- Add summary builders for skeletonization and realization diagnostics.

## Refactor Impact On Existing Synthetic_Blow Complaints

### Complaint: target-only edge fibers can lie about parallel edge witnesses

Changed.

If the tower and all exposed tier views are simple-reflexive, target-only fibers
inside the tower no longer lose multiplicity-level witness identity. The
multiplicity-level witness identity lives in `H` fibers and the post-processing
realization records.

Remaining requirement:

```text
Assert tier views are actually simple.
```

If tier views can have parallel search edges, the old complaint returns.

### Complaint: edge-fiber lookup scans the tier

Still valid.

Even with simple tier views, repeated scans are the wrong hot-path shape. Add
indexes by:

```text
(downstairs_simple_edge_id, upstairs_source_id)
```

or:

```text
(projected_endpoint_pair, upstairs_source_id)
```

### Complaint: no test for downstairs boundary without interior

Still valid.

The refactor does not change small-object semantics. This test remains important
to distinguish the current search from future Kan filling.

### Complaint: artifacts cannot audit edge identity

Changed.

Artifacts should not try to make skeleton simplex witnesses double as original
`H` witnesses. Instead they should expose:

```text
skeleton witness ids
H realization face factors
original H edge ids inside each factor when requested
```

### Complaint: public release surfaces are local-development shaped

Still valid.

The refactor should happen before release polish, because it changes public
semantics.

## Testing Plan

### Skeletonization Tests

1. Empty edge graph with vertices.
   - `G` has same vertices and no non-loop edges.
   - Search normalization adds identities.
   - Realization counts for degenerate simplices are zero under default loop
     policy.

2. Single non-loop edge.
   - `H` has one edge `a -> b`.
   - `G` has one edge `a -> b`.
   - `edge_fiber_H[(a,b)]` has one id.
   - `(a,b)` realization count is one.

3. Parallel non-loop edges.
   - `H` has three edges `a -> b`.
   - `G` has one edge `a -> b`.
   - `(a,b)` realization count is three.

4. Input loop only.
   - `H` has one loop `s -> s`.
   - `G` has no non-loop edges.
   - normalized search view has formal identity at `s`.
   - `(s,s)` realization count is one.

5. Parallel loops.
   - `H` has `L` loops at `s`.
   - `(s,s)` count is `L`.
   - `(s,s,s)` count is `L^3`.

6. Mixed loops and parallel non-loop edges.
   - `H` has `L` loops at `s` and `M` edges `s -> t`.
   - `(s,s,t)` count is `L * M * M`.
   - `(s,t,t)` count depends on loops at `t`.

7. Label conflict.
   - Parallel edges with different labels fail under default policy.

### Tier View Tests

1. Simple tier view has no non-identity loops.
2. Simple tier view has at most one edge per ordered endpoint pair.
3. Every underlying action-cell edge belongs to one simple tier edge fiber.
4. Projecting a simple tier edge is endpoint-determined.
5. Edge-fiber target lookup over simple tier views matches a slow reference.

### Search Tests

1. Existing directed flag tests still pass.
2. Existing degenerate tests still pass at skeleton layer.
3. Existing fake tower tests are updated to simple tier edge semantics.
4. Downstairs boundary without downstairs interior does not produce upstairs
   interior.

### Realization Tests

1. Nondegenerate edge count.
2. Nondegenerate triangle product count.
3. Degenerate edge with zero loops has zero count.
4. Degenerate edge with loops has loop count.
5. Degenerate 2-simplex with repeated non-loop face multiplies repeated factors.
6. Total realization count by degree is sum of per-address counts.
7. Positive address count excludes zero-count skeleton simplices.

### Artifact Tests

1. Single JSON includes skeletonization and realization sections.
2. Manifest tables include edge fibers, loop fibers, realization records, and
   face factors.
3. Expanded witness assignment output is absent by default.
4. Expanded witness assignment output respects cap when later implemented.

## Migration Strategy

### Phase 1: Add Skeletonization Without Rewiring Search

- Add `skeleton.py`.
- Add skeletonization tests.
- Do not change public API yet.

### Phase 2: Feed Skeleton Graph Into Existing Search

- Update `search_simplices(graph=H, ...)` to skeletonize first.
- Build tower from `skeleton.skeleton_graph`.
- Keep returning old `SimplexSearchResult` temporarily if needed, but attach
  skeletonization in an experimental/internal path.

### Phase 3: Add H-Realization Records

- Add `realizations.py`.
- Compute tier-0 realization records.
- Add realization diagnostics.
- Add tests for multiplicity products and loop restrictions.

### Phase 4: Refactor Result And Artifacts

- Introduce `SkeletonRealizationSearchResult`.
- Update artifact writer.
- Update README examples.
- Keep lower-level skeleton-only search functions for tests.

### Phase 5: Simple Tier Views

- Refactor `StateCollapserStaticTowerAdapter` to expose simple tier views.
- Add simple tier view invariants and tests.
- Add edge-fiber indexes.

Phase 5 can happen before Phase 3 if tower multiplicity problems show up in
tests. The important point is not to publish until both input skeletonization
and tier-view simplicity are true.

## Compatibility Notes

### Existing Smoke Counts

Existing smoke scripts count skeleton simplices. After this refactor, those
counts should still exist, but they need labels:

```text
skeleton count
positive H-realized address count
total H-realization count
```

Some old smoke expectations for degenerates may change if they were implicitly
assuming formal identities count as original loops.

### Existing README

README examples should say whether they print:

```text
skeleton simplex counts
```

or:

```text
H-realization counts
```

Do not mix these in one table without labels.

### Existing Artifacts

Old artifacts exposed simplex witnesses as if edge ids were the whole story.
New artifacts must separate:

```text
skeleton witness
H realization factor
```

## Open Questions

These should be answered by the Project Owner before implementation hardens.

1. Should zero-count skeleton simplices be included in the public default result?

   This design says yes, because they explain the restriction stage. Public
   summaries can hide them if desired.

#### PO Follow-up
> What does this mean?

#### Codex Reply
It means the search over `G` may find a simplex address that has no positive
realization back in `H`.

The basic example is a degenerate edge:

```text
H:
  vertex s
  no original loop s -> s

G search view:
  formal identity id_s exists so the skeleton simplex (s, s) exists
```

Under the default design in this document, `(s, s)` is a valid skeleton simplex
address, but its `H`-realization count is:

```text
0
```

because `H` did not actually contain a loop at `s`.

So the question is whether the public result should include records like:

```text
simplex: (s, s)
skeleton_exists: true
h_realization_count: 0
```

or whether it should omit them by default.

The design currently says to include them by default because they explain the
"restriction" part of the `H -> G -> H-realization` pipeline. The search found
the formal degenerate address in `G`, and post-processing explains that `H`
does not realize it. A summary table can still separately report only positive
`H`-realized addresses.

#### PO Reply
> Include them. Not including them is a forgetting that doesn't make sense.

2. Should formal identities ever count as one `H` realization when no `H` loop
   exists?

   This design says no by default.

#### PO Follow-up
> What does this mean?

#### Codex Reply
It is the convention question for formal identities.

The skeleton search adds one formal identity at every vertex:

```text
id_s : s -> s
```

That identity is needed so the simplex engine can generate degenerate addresses
like:

```text
(s, s)
(s, s, s)
(s, s, t)
```

But `id_s` is not necessarily an edge that existed in the original graph `H`.
So there are two possible meanings when `H` has no actual loop at `s`:

```text
Convention A:
  formal id_s counts as one realization anyway
  so (s, s) has count 1

Convention B:
  formal id_s is search-only
  original H loops are required for H-realization
  so (s, s) has count 0 unless H contains a loop at s
```

This design chooses Convention B because the Project Owner phrasing was
"allowing degeneracies at loops that happen to be present in H." That makes
formal identities part of the skeleton search, not automatic original witnesses
in `H`.

So:

```text
if H has 0 loops at s:
  count_H(s, s) = 0

if H has 4 loops at s:
  count_H(s, s) = 4
```

This is the main way post-processing can restrict the skeleton result.

#### PO Reply
> I don't understand your language. Degenerate simplices whould lift from $G$ to $H$ precisely when there is a loop upstairs.

#### Codex Response
Yes. That is the cleaner language.

The right statement is:

```text
A degenerate simplex in G lifts to H exactly when the corresponding repeated
vertex face is witnessed by an actual loop in H.
```

So for the skeleton degenerate edge:

```text
(s, s) in G
```

the lifts in `H` are:

```text
all loops h: s -> s in H
```

If there are no such loops, then that degenerate simplex has no lift to `H`.
If there are `L` loops at `s`, then it has `L` lifts.

The earlier "formal identity" language was muddier than it needed to be. The
formal identity is only the device that lets the skeleton search in `G` see the
degenerate address. It is not itself a lift in `H`. The actual lift is a loop
upstairs in `H`.

So the design rule should be rewritten as:

```text
G contains formal degeneracy addresses.
H supplies actual lifts of those degeneracies only through actual loops.
```

Examples:

```text
H has 0 loops at s:
  lifts_H(s, s) = empty

H has loops l1, l2, l3 at s:
  lifts_H(s, s) = {l1, l2, l3}
```

For a higher degenerate simplex such as:

```text
(s, s, t)
```

the repeated face:

```text
(0,1): s -> s
```

must lift through an actual loop at `s`, while the two faces:

```text
(0,2): s -> t
(1,2): s -> t
```

lift through actual edges from `s` to `t` in `H`.

3. Should repeated face occurrences choose witnesses independently?

   This design says yes by default, giving products like `|H(s,t)|^2` for
   `(s,s,t)`.

#### PO Follow-up
> What does this mean?

#### Codex Reply
It means each face position in a simplex gets its own witness choice, even if
two face positions have the same endpoint pair.

For example:

```text
sigma = (s, s, t)
```

Its directed face occurrences are:

```text
(0,1): s -> s
(0,2): s -> t
(1,2): s -> t
```

The endpoint pair `s -> t` appears twice, because there are two different face
positions ending at `t`.

If `H` has `M` parallel edges from `s` to `t`, independent witness choices mean:

```text
(0,2) can choose any of M edges
(1,2) can choose any of M edges
```

so the contribution from those two faces is:

```text
M * M = M^2
```

not just `M`.

With loops included, if:

```text
|Loop_H(s)| = L
|H(s,t)| = M
```

then:

```text
count_H(s, s, t) = L * M * M
```

The alternative convention would force repeated endpoint pairs in one simplex
to share the same original edge witness. That would give `L * M` instead. This
document chooses independent face witnesses because a simplex record has
separate face occurrences, and each occurrence should be realized by an original
edge choice unless the Project Owner says repeated faces must be identified.

#### PO Reply
> Parallel edges should result in distinct simplices. Is this the entire issue?

#### Codex Response
Yes, that is the core issue, with one important layer distinction.

In `G`, parallel edges from `H` have been collapsed, so `G` has one skeleton
simplex address. In `H`, parallel edges produce distinct lifted simplices.

For example:

```text
H has two edges a -> b:
  e1: a -> b
  e2: a -> b

G has one edge a -> b
```

The skeleton search finds one 1-simplex address:

```text
(a, b) in G
```

But the lift back to `H` has two distinct 1-simplices:

```text
(a --e1--> b)
(a --e2--> b)
```

For a 2-simplex, the distinct lifts are witness assignments across all faces.
If:

```text
|H(a,b)| = 2
|H(a,c)| = 3
|H(b,c)| = 5
```

then the single skeleton simplex:

```text
(a, b, c) in G
```

has:

```text
2 * 3 * 5 = 30
```

distinct lifted `H`-simplices.

So yes: parallel edges should result in distinct simplices, but they should
become distinct during the `H`-lift/post-processing stage, not inside the tower
search. That is the separation:

```text
G-search:
  find the skeleton simplex address once

H-lift:
  expand or count all distinct H-simplices lying over that address
```

This also means the result model should not only say `realization_count` if the
mathematical output is "distinct simplices." It should treat lifted `H`-simplices
as real objects, with a compressed default representation and an optional
expansion path:

```text
Skeleton simplex:
  (a, b, c)

H-lift record:
  face fibers:
    H(a,b), H(a,c), H(b,c)
  count:
    product of fiber sizes
  optional iterator:
    each tuple of edge witnesses is one distinct H-simplex
```

Counts are the compressed representation of distinct lifted simplices, not a
replacement for the concept.

4. Should parallel edge label disagreement fail by default?

   This design says yes. It is safer than silent union.

#### PO Follow-up
> What does this mean?

#### Codex Reply
It is about contraction schemas and edge labels.

Skeletonization collapses all parallel non-loop edges with the same ordered
endpoints into one skeleton edge:

```text
H:
  e1: a -> b, labels=("red",)
  e2: a -> b, labels=("blue",)

G:
  one skeleton edge a -> b
```

The question is:

```text
what labels should the one skeleton edge carry?
```

This matters because `state_collapser` schemas can use labels to decide what
contracts. If the package silently unions labels:

```text
("red", "blue")
```

or silently chooses the first label:

```text
("red",)
```

then the quotient tower can change in a way that is hard to notice.

So the conservative first-scope rule is:

```text
parallel edges with identical labels:
  OK, collapse them into one skeleton edge with that label tuple

parallel edges with different labels:
  fail loudly unless an explicit policy is provided
```

This is not saying different labels can never be supported. It is saying the
package should not invent a label merge rule silently. If we need a merge rule,
it should be a named option with tests because it changes the tower.

#### PO Response
> Parallel edges should be excised from the tower at all tiers before next tier is created.

#### Codex Response
Yes. That is stronger and cleaner than merely hiding parallel edges from the
simplex search adapter.

The tower itself should advance by simple graphs:

```text
G^r
  -> remove/merge parallel edges and remove non-formal loops
  -> use that simple graph as the input for constructing G^(r+1)
```

So the invariant is not only:

```text
the search view of each tier is simple
```

It is:

```text
the graph used to create the next tier is already simple.
```

That matters because if parallel edges remain inside tower construction, they
can affect the next quotient tier before the adapter ever gets a chance to hide
them. The refactor should not rely on a view-layer cleanup after the fact.

The design should therefore be revised from:

```text
Build a state_collapser tower, then expose simple tier views.
```

to:

```text
At every tower step:
  produce the next quotient data
  excise/merge parallel edges before that data becomes the next graph tier
  expose the resulting tier as G^r
```

There are two implementation possibilities:

1. If `state_collapser` already has a way to build a tower whose action layers
   are simple at each stage, use that directly.

2. If it does not, `jet_simplex_search` needs a static-tower construction
   adapter or pre-pass that asks `state_collapser` for the quotient information
   stage by stage and canonicalizes the edge set before the next stage is
   formed.

The important rule is:

```text
parallel edge multiplicity is never part of G^r -> G^(r+1) tower evolution.
```

Multiplicity belongs to the separate lift data:

```text
H fibers over G^0 edges
possibly action-cell fibers used only as provenance
not as parallel search/tower edges
```

So this changes the earlier "simple tier view" language. A simple view is not
enough if the underlying tower was already built using multiplicity. The tier
must be canonicalized before creating the next tier.

#### PO Reply
> Look in `state_collapser`. At every tier, before we construct next tier, we need to excise multiple edges and make sure each node has exactly one loop.

#### Codex Response
I looked at the relevant `state_collapser` code. This should be treated as a
real upstream tower-construction requirement, not only as a
`jet_simplex_search` adapter cleanup.

The important files are:

```text
../state_collapser/src/state_collapser/tower/partition/tower.py
../state_collapser/src/state_collapser/tower/partition/action_layer.py
../state_collapser/src/state_collapser/tower/partition/loop_policy.py
```

The current partition tower keeps a fixed base registry and carries edge ids
through partition layers. In initialization, `PartitionTower.initialize` does:

```text
register base graph
build tier-0 singleton state layer
build tier-0 action layer from the registry
for each contraction block:
  carry state layer forward
  carry action layer forward
  contract selected edges
  rebuild dirty action cells
  append the tier
```

The key current behavior is in `ActionPartitionLayer.rebuild_action_cells_for_collection`.
It groups live edges by:

```text
(source_cell, target_cell, primitive_action_identity)
```

That means two edges with the same source cell and target cell but different
primitive action identities become two action cells. For this package, that is
still multiplicity at the tier level. It is not the `G^r` we want.

The loop behavior is separate. Edges whose source and target land in the same
state cell are removed from the live outgoing collection and recorded as
internal edges according to `LoopPolicy`. That records the fact that internal
edges became loops, but it does not give the tier graph exactly one canonical
loop at every node. For this package, every tier needs exactly one formal loop
available for degenerate simplex generation, independent of how many internal
edges were recorded.

So the needed invariant is:

```text
Before G^(r+1) is constructed from G^r:
  collapse/excise all parallel non-loop edges in G^r
  remove original/internal loop multiplicity from the live edge set
  add exactly one canonical formal loop at each node
```

This is stronger than "hide multiplicity when reading the tier." It means the
tower construction itself must use the normalized tier as the next tier input.

Concretely, `state_collapser` needs a tier-normalization step at the boundary
where a tier's action surface becomes the graph data for the next tier. In the
current partition implementation, the natural insertion points look like:

```text
ActionPartitionLayer.from_state_layer_and_registry(...)
ActionPartitionLayer.carry_forward_from(...)
ActionPartitionLayer.merge_collections(...)
ActionPartitionLayer.rebuild_action_cells_for_collection(...)
PartitionTower._ensure_tier_exists(...)
PartitionTower.initialize(...)
```

The most direct conceptual change is inside action-cell rebuilding:

```text
current grouping:
  (source_cell, target_cell, primitive_action_identity)

simple tier grouping needed for G^r:
  (source_cell, target_cell)
```

with the primitive action identities and original edge ids retained only as
fiber/provenance data under that one simple edge/action cell.

Then loop handling should be:

```text
source_cell == target_cell:
  not a live multiplicity edge
  record as internal/provenance
  expose exactly one formal loop for that state cell in the simplex-search view
```

The formal loop should not be a pile of all internal edge ids. It is the unique
degeneracy option at that node. The internal edges remain provenance, reward
aggregation input, or later `H`-lift data, depending on context.

This also changes how I would phrase the dependency boundary:

```text
state_collapser should own tier normalization during tower construction:
  no parallel live action edges per source-target pair
  no live original loops
  exactly one formal loop per state cell

jet_simplex_search should consume that normalized tower:
  enumerate simplices
  lift over known downstairs simplex addresses
  compute H-lifts only over G^0
```

If `state_collapser` does not change, then `jet_simplex_search` can still build
a simple readout view, but that would be too late for the PO requirement because
the next tier may already have been constructed from a multiplicity-bearing
action surface.

So the implementation plan should include an upstream `state_collapser` task:

```text
Add a simple-reflexive tier construction mode to PartitionTower.
```

Minimum tests for `state_collapser`:

1. Tier 0 with two different actions from `a` to `b` exposes one live non-loop
   edge/action cell from `a` to `b`, with both primitive edges retained in its
   fiber.

2. After a contraction merges `a` and `b`, internal edges are not live parallel
   loops; the resulting node has exactly one formal loop in the tier graph.

3. Before constructing `G^(r+1)`, the `G^r` action surface satisfies:

```text
one non-loop edge per ordered source-target pair
one formal loop per node
```

4. The quotient/tower result is independent of parallel multiplicity in the
   live tier graph, while provenance fibers still remember the multiplicity.

That is the `state_collapser`-side follow-up for this refactor.

5. Should `H` realization counts be computed for quotient tiers below `G^0`?

   This design says no in first scope.

#### PO Follow-up
> No.

#### Codex Response
Understood. Then the design should stop treating quotient-tier `H` realization
counts as an open question.

First-scope and intended semantics:

```text
H-lifted distinct simplices are computed only over G^0.
Lower quotient tiers are search/compression machinery, not H-realization output.
```

So the public output should distinguish:

```text
G^0 skeleton simplices:
  lift to distinct H-simplices
  have H-lift counts / compressed H-lift records

G^r for r > 0:
  support tower search and diagnostics
  do not receive H-lift counts
```

This keeps the semantics direct. `H` maps to `G^0`, not to every quotient tier
as an output space for original simplices.

## Non-Goals

The refactor should not:

- implement Kan replacement;
- implement horn filling;
- enumerate every `H` witness assignment by default;
- preserve parallel `H` edges inside the quotient tower;
- treat original `H` loops as ordinary non-identity search edges;
- introduce a graph database;
- introduce tensor/GPU acceleration;
- add a framework around one pipeline;
- change `state_collapser` ownership of tower construction.

## Success Criteria

The refactor is successful when:

1. Arbitrary `H` loops and parallel edges are accepted.
2. Skeletonization produces a deterministic simple graph `G`.
3. Tower search runs over `G`, not `H`.
4. Every exposed tier view used by simplex search is simple-reflexive.
5. Tier-0 skeleton simplices carry `H`-realization counts.
6. Degenerate skeleton addresses can have zero `H` realizations when `H` lacks
   loops.
7. Parallel edge multiplicities multiply in post-processing, not during tower
   search.
8. Artifacts make skeleton search and `H` realization data separate.
9. Tests cover loop restriction, parallel multiplication, repeated face
   multiplication, label conflicts, and no-downstairs-interior small-object
   behavior.
10. The code remains small, flat, and readable.

## Final Design Rule

The refactor should make this invariant true everywhere:

```text
Skeleton search never lies about H multiplicity,
because skeleton search never claims to be H multiplicity.

H realization counting never pollutes tower search,
because H multiplicity is counted only after skeleton simplices are found.
```

That is the clean separation the current package needs before release.
