# synthetic_blow review

I am reviewing this through a Jonathan-Blow-inspired lens: direct, performance-aware, skeptical of unnecessary abstraction, and focused on reducing complexity. This is not an impersonation or endorsement.

Review target: current `jet_simplex_search` worktree.

Review spec: `code_review/synthetic_blow_review_kit/synthetic_blow.md`.

Verification command run during review:

```bash
uv run pytest
```

Observed result:

```text
58 passed in 0.07s
```

## Verdict

The package is small and mostly direct. That is good. The core mathematical design is also present: direct bottom-tier enumeration, static quotient-tower lifting, first-class degenerates, and dimension-preserving search over downstairs simplex fibers. The serious problem is narrower and more dangerous: the code can preserve the correct simplex address while corrupting the witness trace. The lifting path asks the adapter for target vertices in an edge fiber, then reconstructs witnesses from every upstairs edge with the same endpoints. In a multigraph or action-cell tower, that loses the distinction between "this edge lies over the downstairs final edge" and "some edge with the same source and target exists." For a release whose value is traceable simplex search, this is a blocker.

## Detailed explanation of the blocker

The phrase "the final edge fiber is target-only" means this:

```python
def edge_fiber_targets(...) -> frozenset[str]:
```

The adapter API in `src/jet_simplex_search/tower_adapter.py:41` returns only upstairs target vertex ids. The real adapter implementation in `src/jet_simplex_search/tower_adapter.py:218` also returns only target ids. The artifact record in `src/jet_simplex_search/records.py:82` stores only `upstairs_target_ids`.

That means the lift code knows:

```text
from upstairs source a, over downstairs edge alpha, target b is allowed
```

It does not know:

```text
the compatible upstairs edge id is e_alpha
```

Then `lift_downstairs_extension` uses those target ids:

```python
for target in sorted(frozenset(targets) & upstairs_prefix.frontier):
    emitted.append(extend_simplex_direct(..., target, ...))
```

That is `src/jet_simplex_search/lift.py:85`.

The witness construction then falls back to endpoint lookup. `extend_simplex_direct` calls:

```python
face_edge_witnesses_for_extension(graph, simplex.vertices, target)
```

and then sets:

```python
last_edge_ids = graph.edge_lookup.get((simplex.target_vertex, target), ())
```

That is `src/jet_simplex_search/search.py:75` through `src/jet_simplex_search/search.py:93`. The helper in `src/jet_simplex_search/frontier.py:30` does the same thing for every new face edge: it records every edge id in `graph.edge_lookup[(source, target)]`.

This is fine for a simple directed graph where one endpoint pair means one edge. This package allows parallel edges, and the tower adapter is action-cell based, so endpoint pair is not enough.

Concrete failure shape:

```text
Downstairs tier:
  vertices: X, Y
  parallel edges:
    alpha: X -> Y
    beta:  X -> Y

Upstairs tier:
  vertices:
    a over X
    b over Y
  parallel edges:
    e_alpha: a -> b, projects to alpha
    e_beta:  a -> b, projects to beta
```

Now lift the downstairs 1-simplex whose final edge is `alpha`.

The current adapter query can only answer:

```text
edge_fiber_targets(alpha, source=a) = {b}
```

That is enough to produce the upstairs vertex address:

```text
(a, b)
```

But when `extend_simplex_direct` constructs the record, it asks the normalized graph for all edges from `a` to `b`. It records:

```text
last_edge_ids = (e_alpha, e_beta)
```

The emitted simplex says it projects to the downstairs simplex over `alpha`, while one of its last-edge witnesses projects to `beta`. The count is still right. The vertices are still right. The bug lives in the evidence.

The same class of problem can appear in higher degree. When extending `(a0, ..., am)` by `t`, the code checks that `t` is in the prefix frontier, but the new non-final face witnesses `(ai -> t)` are also populated by endpoint lookup. If the downstairs simplex distinguishes parallel face edges, those witnesses need fiber compatibility too, or the artifact needs to explicitly say that witnesses are endpoint-level evidence rather than downstairs-edge-level evidence.

This is why the bug is not cosmetic. The package is not only emitting address sets. It is emitting records that are supposed to explain why those addresses are valid lifts.

#### PO Comment
> Ok I think we need a re-design though before we tackle this. Let me tell you what I havd in mind. There needs to be a pr-processing stage that takes an arbitrary graph, strips it of loops and multipicities, adds loops back in, and then works with that. The way I want to think of it is like this:
> $$ H\xrightarrow{\ \ \text{\'et}\,q\ \ }G\cong G^0\longrightarrow G^1\longrightarrow G^2\longrightarrow\cdots\longrightarrow G^d$$
> Every $G^{m}$ is multipliciy- and loop-free. The package should build $G$ from $H$ in preprocessing, use the tower to find simplices up to dimension $k$ in $G^{0}$, then in post-processing, "lift" the simplicies found in $G$ by increasing counts via multiples in $H$ and allowing degeneracies at loops that happen to be present in $H$. Note that this is simultaneously an increase and restriction, and that the counts can get high when parallel edges are in sequence.
>
> Let me know if this makes sense, if you see the implmentation clearly, and if this changes a lot of the complaints in the report below.

#### Codex Reply
Yes, this makes sense, and I think it is a better design than trying to make the tower/lift engine carry all multiplicity data directly.

The clean separation is:

```text
H  -- et q -->  G ~= G^0 -> G^1 -> ... -> G^d
```

where `H` is the arbitrary input graph, possibly with loops and parallel edges, and `G` is the search graph obtained from `H` by forgetting multiplicity, removing original loops, and then adjoining exactly one formal identity loop at each vertex for the simplex engine. I am reading "every `G^m` is multiplicity- and loop-free" as "no original loops and no parallel edges, with only the canonical formal identity used for degeneracy bookkeeping." If you mean literally no loops even internally, then the formal identities would need to live as a separate reflexive-closure relation rather than as graph edges.

Implementation-wise, this becomes much clearer:

1. Preprocess `H -> G`.
   - Keep the same vertex set, unless later contraction schemas require a vertex relabeling stage.
   - For each non-loop endpoint pair `(s, t)` with at least one edge in `H`, add one edge `(s, t)` to `G`.
   - Store the original edge fiber:

```text
edge_fiber_H[(s, t)] = tuple(original H edge ids from s to t)
```

   - Store original loops separately:

```text
loop_fiber_H[s] = tuple(original H loop edge ids at s)
```

   - Add one formal identity at every vertex in `G` for the simplicial/dependency induction.

2. Build the static quotient tower only from `G`.
   - The tower never sees parallel edges from `H`.
   - The tower never sees original loops from `H`.
   - This means tower search is really over the simple/reflexive skeleton.

3. Find simplices in `G^0` and through the tower exactly as the small-object algorithm wants.
   - The search result is an address-level result over `G`.
   - At this stage, a simplex is something like `(v0, ..., vm)` plus its simple face structure.
   - There is no multiplicity explosion inside the tower.

4. Post-process each simplex of `G` back against `H`.
   - For each face occurrence `(vi -> vj)` with `vi != vj`, the number of possible original witnesses is:

```text
len(edge_fiber_H[(vi, vj)])
```

   - For each degenerate face occurrence `(vi -> vi)`, the number of allowed original witnesses is controlled by:

```text
len(loop_fiber_H[vi])
```

   - If we are counting witness assignments independently per face occurrence, then the realization count is the product over all directed faces:

```text
count_H(sigma) =
  product over 0 <= i < j <= m of witness_count_H(vi, vj)
```

This is exactly where counts can get large. A 2-simplex `(a, b, c)` with parallel multiplicities has count:

```text
|H(a,b)| * |H(a,c)| * |H(b,c)|
```

and a degenerate simplex like `(s, s, t)` has face occurrences:

```text
s -> s
s -> t
s -> t
```

so, under independent face-witness semantics, its count is:

```text
|Loop_H(s)| * |H(s,t)| * |H(s,t)|
```

That last example shows the "simultaneously increase and restriction" point. Parallel non-loop edges increase counts. Missing actual loops in `H` can restrict degenerate realizations back down to zero, even though the formal identity in `G` allowed the degenerate address to exist in the search skeleton.

There is one convention we should pin down before implementation:

```text
When H has no loop at s, does a formal degeneracy at s have:
  count 0 in the H-realization post-process, or
  count 1 as a purely formal simplicial degeneracy?
```

Your phrasing, "allowing degeneracies at loops that happen to be present in H," sounds like the first answer: no original loop in `H` means no `H`-realization for that degenerate face. That is coherent, and it explains why post-processing is both an increase and a restriction. But it is a real mathematical convention, so I would put it explicitly in the design doc and tests.

This redesign changes several complaints in the report below.

The old blocker, "the tower edge fiber is target-only," becomes much less central if the tower is only built from the multiplicity-free graph `G`. In a simple graph, an endpoint pair corresponds to a single non-identity edge, so target-level fiber information is not losing parallel-edge identity inside the tower. The edge identity problem moves out of the tower and into the `H -> G` preprocessing/post-processing layer, where it belongs.

So I would revise the implementation target from:

```text
make the tower adapter carry all edge ids through every lift
```

to:

```text
keep tower search simple over G, then compute H-realization counts from stored H-fibers
```

The report's performance complaint about repeated fiber scans still matters, but it becomes a lower-level adapter optimization rather than the central correctness repair. The new central correctness repair is:

```text
Do not let H multiplicity into the quotient tower.
Do preserve enough H-fiber metadata to compute realization counts after the G-search.
Do test the product/restriction semantics for loops, parallel edges, and repeated face occurrences.
```

The implementation shape I now see is:

```text
RawGraphH
  -> preprocess_h_to_g
       simple_graph_g
       h_edge_fibers_by_pair
       h_loop_fibers_by_vertex
       preprocessing_diagnostics
  -> run_static_small_object_search(simple_graph_g, k)
  -> postprocess_h_realizations(search_result_g, h_fibers)
       same simplex addresses over G
       h_realization_count per simplex
       optional witness-expansion iterators for small cases
```

The important practical point is not to eagerly materialize every `H` witness assignment unless the user asks for it and the count is small. Counts can grow as products over all faces, so the post-processing result should probably default to counts plus compressed witness-fiber references. Full expansion should be an opt-in artifact mode with a cap.

So yes: this makes sense, I see the implementation clearly, and it changes the report materially. The report below should be updated so the first design repair is not "thread edge ids through tower lifting," but "split skeleton search from `H`-realization counting." The former may still be useful internally, but it is no longer the main architectural answer.

## Program map

- Entry point: `src/jet_simplex_search/api.py:45`, `search_simplices`.
- Context construction: `src/jet_simplex_search/api.py:25`, `build_static_search_context`.
- Direct enumeration: `src/jet_simplex_search/search.py:100`, `enumerate_direct_simplices`.
- Direct extension: `src/jet_simplex_search/search.py:60`, `extend_simplex_direct`.
- Frontier recurrence: `src/jet_simplex_search/frontier.py:19`, `extend_frontier`.
- Face witness construction: `src/jet_simplex_search/frontier.py:30`, `face_edge_witnesses_for_extension`.
- Tower orchestration: `src/jet_simplex_search/search.py:131`, `run_static_small_object_search`.
- Fiber lifting: `src/jet_simplex_search/lift.py:97`, `lift_tier_simplices`.
- One-step lift: `src/jet_simplex_search/lift.py:65`, `lift_downstairs_extension`.
- Adapter boundary: `src/jet_simplex_search/tower_adapter.py:14`, `StaticTowerAdapterProtocol`.
- Real adapter: `src/jet_simplex_search/tower_adapter.py:81`, `StateCollapserStaticTowerAdapter`.
- Artifact writer: `src/jet_simplex_search/artifacts.py:30`, `write_search_artifact`.
- Tests: `tests/`, currently 58 tests passing.

Not applicable from the original RL review template:

- Training loop: not applicable.
- Evaluation loop: not applicable.
- Model/update code: not applicable.
- Replay buffer: not applicable.
- Checkpoints: not applicable.

The analogous correctness surface is graph normalization, simplex address generation, face-edge witnesses, projection ids, fiber records, and artifacts.

## The real data path

```text
GraphInput
  -> validate_graph_input
  -> normalize_graph
  -> input loops stripped
  -> one formal identity edge per vertex
  -> NormalizedGraph.edge_lookup and adjacency_targets
  -> state_collapser partition tower adapter
  -> bottommost nondegenerate tier direct simplex enumeration
  -> upstairs lifting over known downstairs simplex records
  -> SimplexRecord / SimplexFiberRecord / EdgeFiberRecord
  -> diagnostics and optional JSON/JSONL artifacts
```

The important records:

- `GraphInput`: sparse directed input with unique vertex ids and edge ids.
- `NormalizedGraph`: normalized vertices, edges, adjacency targets, endpoint edge lookup, stripped input loop ids.
- `SimplexRecord`: tier, degree, vertex tuple, witnesses, frontier, degeneracy flag, projection simplex id.
- `SimplexFiberRecord`: upstairs simplex ids over one downstairs simplex.
- `EdgeFiberRecord`: currently upstairs target ids over a downstairs edge/source pair.

The current code is direct and readable. The bug is not that the program is impossible to follow. The bug is that the data model loses edge identity exactly where the algorithm needs it most.

## Highest-severity issues

### Issue 1: lifted witness traces can be false

- Severity: blocker
- Location: `src/jet_simplex_search/lift.py:65`, `src/jet_simplex_search/search.py:60`, `src/jet_simplex_search/frontier.py:30`, `src/jet_simplex_search/records.py:82`
- Problem: fiber lifting filters by target vertex, then witness construction records every edge id between the relevant endpoints. In parallel-edge cases, a lifted simplex over downstairs edge `alpha` can record an upstairs witness that projects to downstream edge `beta`.
- Why it matters: this invalidates traceability. A reader of the artifact cannot trust that a witness listed in a lifted simplex actually lies in the claimed downstairs fiber.
- Fix: make edge fibers edge-id aware. The lifting path must carry compatible upstairs edge ids into simplex extension, and the resulting `SimplexRecord.last_edge_ids` must be the compatible subset, not every edge with those endpoints.

Minimum patch shape:

```text
StaticTowerAdapterProtocol.edge_fiber_edges(...)
    -> tuple[str, ...]

EdgeFiberRecord
    downstairs_edge_id
    upstairs_tier
    upstairs_source_id
    upstairs_edge_ids
    upstairs_target_ids

lift_downstairs_extension(...)
    compatible_edge_ids = union edge_fiber_edges(...)
    compatible_targets = edge targets of compatible_edge_ids
    for target in compatible_targets intersect upstairs_prefix.frontier:
        extend_simplex_direct(..., allowed_last_edge_ids=compatible_edge_ids_for_target)
```

The test should assert not only emitted vertices, but also:

```text
for edge_id in simplex.last_edge_ids:
    adapter.project_edge(simplex.tier, edge_id) in downstairs.last_edge_ids
```

### Issue 2: non-final face witnesses are also only endpoint-checked

- Severity: high
- Location: `src/jet_simplex_search/frontier.py:30`, `src/jet_simplex_search/search.py:75`
- Problem: when extending a simplex, `face_edge_witnesses_for_extension` records all edge ids from every prefix vertex to the new target. During lifting, only the final edge fiber is consulted. The earlier new face edges are checked by frontier membership, which proves endpoint adjacency but not compatibility with the corresponding downstairs face edge id in a multigraph/action-cell setting.
- Why it matters: in degree 2 and higher, an upstairs simplex can have the right vertex tuple and final edge but still carry face witness ids that do not project to the downstairs simplex's face witnesses.
- Fix: either explicitly define witness semantics as endpoint-level only, or make lifted extension receive per-face allowed edge ids derived from the downstairs simplex's `face_edge_witnesses`. For traceable artifacts, the second option is the right one.

Minimum invariant:

```text
For each lifted simplex over downstream tau,
for each upstairs witness on face (i, j),
project_edge(upstairs_edge_id) must be one of tau's witness edge ids for face (i, j).
```

### Issue 3: edge-fiber lookup scans the whole tier repeatedly

- Severity: high
- Location: `src/jet_simplex_search/tower_adapter.py:218`
- Problem: `edge_fiber_targets` scans `self.tier_edges(upstairs_tier)` for every query and calls `project_edge` on matching-source edges. `tier_edges` itself walks action cells and populates caches.
- Why it matters: the package's advertised speedup is that search is organized by fibers. The adapter should not do repeated broad edge scans in the hot path.
- Fix: build a per-tier edge-fiber index once and query it directly.

Index shape:

```text
edge_fiber_index[upstairs_tier][downstairs_edge_id][upstairs_source_id]
    -> tuple[upstairs_edge_id, ...]

target_fiber_index[upstairs_tier][downstairs_edge_id][upstairs_source_id]
    -> frozenset[upstairs_target_id]
```

The hot lift operation should be:

```text
compatible_edges = index[downstairs_edge_id][upstairs_source_id]
targets = target ids from compatible_edges
targets &= upstairs_prefix.frontier
```

That is the actual fiber-addressed version of the algorithm.

### Issue 4: no regression test for "downstairs boundary but no downstairs interior"

- Severity: medium
- Location: `src/jet_simplex_search/lift.py:125`, `tests/test_fiber_lift.py`
- Problem: the code structurally lifts only over existing downstairs degree records, but no named regression test protects the small-object rule that an upstairs interior is not searched unless a corresponding downstairs simplex exists.
- Why it matters: this is one of the main distinctions between the present small-object version and a future Kan replacement/filling version.
- Current structural safeguard:

```python
for degree in range(1, k + 1):
    for downstairs in downstairs_simplices_by_degree.get(degree, ()):
```

If there is no downstairs degree-2 simplex record, this loop has nothing to lift in degree 2.

- Fix: add a fake tower where the downstairs tier has enough visible boundary data to make the temptation obvious but has no degree-2 simplex record in `downstairs_simplices_by_degree[2]`, while the upstairs graph has a full directed 2-simplex. Assert that no upstairs degree-2 simplex is emitted.

### Issue 5: artifact edge fibers cannot audit edge identity

- Severity: medium
- Location: `src/jet_simplex_search/artifacts.py:197`, `src/jet_simplex_search/records.py:82`
- Problem: `EdgeFiberRecord` only serializes target ids. The artifact can say "from source a over downstairs edge alpha, target b is reachable," but cannot say which upstairs edge ids made that true.
- Why it matters: after the edge-fiber bug is fixed in memory, artifacts also need to expose the fix. Otherwise the machine-readable output still cannot be audited.
- Fix: add `upstairs_edge_ids` to `EdgeFiberRecord` and serialize it in `edge_fibers.jsonl` / `readout_source.json`.

### Issue 6: release-facing surfaces are still local-development shaped

- Severity: medium
- Location: `README.md:69`, `README.md:230`, `pyproject.toml:24`
- Problem: the README still describes a sibling checkout of `state_collapser`, and `pyproject.toml` still points at `../state_collapser`. The README also links an engineering continuity path that does not exist.
- Why it matters: public release polish cannot be fake. A user should not clone two repos and then hit a stale internal link when the release plan already chose a GitHub tag strategy.
- Fix: switch to the approved GitHub `state_collapser` tag strategy before release. Remove the stale continuity link from root documentation according to the already approved release-plan decision.

## Abstractions that should justify themselves or die

| abstraction | users | cost | benefit | recommendation |
| --- | ---: | --- | --- | --- |
| `StaticSearchContext` | one public call path | extra dataclass and object hop before calling `run_static_small_object_search` | almost none right now | inline unless real config is about to live there |
| `StaticTowerAdapterProtocol` | search, lift, fake tests, real adapter | protocol surface has to be maintained | isolates `state_collapser` from the search engine | keep |
| `StateCollapserStaticTowerAdapter` | real integration path | string ids, caches, action-cell translation | necessary boundary to use `state_collapser` | keep, but add indexed fibers |
| `SimplexRecord` | central | many fields | makes invariants and artifacts explicit | keep |
| `EdgeFiberRecord` target-only shape | lift/artifacts | loses edge identity | partial debugging signal | rewrite |
| `fiber_id` helper | appears unused | dead concept in id namespace | none currently | delete or use in artifacts |
| `StaticSearchContext` builder split | public API only | makes the direct path less direct | minor input normalization | collapse unless release config grows |
| backup/temp SVG files under `assets/images` | none | public-release clutter | none | remove before release |

This is not a case where the project is buried under architecture. Most abstractions are legitimate domain records. The one that hurts is the edge-fiber shape because it compresses away the actual data needed for correctness.

## Correctness traps for this project

This section adapts the RL checklist in the review kit to this graph/tower package.

### Handled well

- Input graph validation rejects duplicate vertex ids and duplicate edge ids.
- Input loops are stripped, then exactly one formal identity is added per vertex.
- Directed flag semantics are tested: a path `0 -> 1 -> 2` without `0 -> 2` is not a 2-simplex.
- Degenerate simplices are first-class records.
- Direct enumeration is dimension-bounded by `k`.
- Tower lifting is dimension-preserving over existing downstairs simplex records.
- The fake adapter tests cover a non-identity upstairs edge over a downstairs identity.

### Not protected enough

- Witness projection compatibility is not asserted.
- Parallel edges are allowed, but edge-fiber lifting is target-only.
- Artifacts do not expose the edge ids in edge fibers.
- The no-downstairs-interior rule is structurally present but not protected by a direct regression test.
- Diagnostics count simplices, degenerates, fibers, and frontier sizes, but do not count fiber queries, edge scans, witness projection failures, or filtered candidates.

The dangerous failure mode is not wrong counts. It is correct counts with false evidence.

## Performance and feedback loop

The test loop is excellent: 58 tests pass in well under a second. That is the right feel for a package at this size.

The algorithmic hot path still needs work:

- `lift_tier_simplices` calls `edge_fiber_targets` once to write `EdgeFiberRecord` and then `lift_downstairs_extension` calls it again for the actual lift.
- `edge_fiber_targets` scans tier edges every time.
- The adapter has source/target caches, but not a fiber index.
- Diagnostics do not expose enough counters to see whether the fiber-addressed speedup is actually happening.

Add counters before benchmarking:

- number of edge-fiber queries;
- number of tier-edge scans;
- number of project-edge calls;
- number of target candidates before frontier intersection;
- number of target candidates after frontier intersection;
- number of emitted simplex records;
- number of deduplicated simplex addresses;
- wall time by tier and degree.

Then add smoke benchmarks:

- sparse path graph;
- transitive chain through degree 4;
- graph with many parallel edges between the same endpoints;
- quotient tower with many upstairs internal edges over downstairs identities;
- small tower where upstairs has many potential simplices but downstairs has few.

Do not optimize random Python loops first. Build the edge-fiber index. That is the performance design.

## Tests that actually matter

Add these before release:

1. `test_lift_parallel_edges_records_only_compatible_last_edge_ids`
   - Build a fake adapter with downstairs parallel edges `alpha`, `beta`.
   - Build upstairs parallel edges `e_alpha`, `e_beta` with the same endpoints.
   - Lift over `alpha`.
   - Assert emitted `last_edge_ids == ("e_alpha",)` and does not contain `e_beta`.

2. `test_lift_face_witnesses_project_to_downstairs_face_witnesses`
   - Use a degree-2 downstream simplex with explicit face witness ids.
   - Give upstairs parallel alternatives for one non-final face.
   - Assert every upstairs face witness projects to the corresponding downstairs face witness set.

3. `test_no_upstairs_interior_lifted_without_downstairs_interior`
   - Give the upstairs tier a full directed triangle.
   - Feed `lift_tier_simplices` downstairs records through degree 1 only, or with degree 2 intentionally empty.
   - Assert upstairs degree 2 is empty.

4. `test_edge_fiber_record_serializes_edge_ids`
   - After the record rewrite, assert artifacts include `upstairs_edge_ids`.

5. `test_artifact_witness_projection_consistency`
   - For every emitted lifted simplex, every witness edge id should project into the appropriate downstairs witness set.

6. `test_edge_fiber_index_matches_slow_reference`
   - Keep a slow scan implementation in the test and assert the new index returns identical edge ids.

7. README quick-start regression
   - Execute the README example under `uv run`.
   - Assert the printed counts match the documented output.

8. Smoke snapshot tests
   - Run the smoke scripts and assert their tables match their `.md` count arguments.

## What I would delete first

1. `StaticSearchContext`, unless the release implementation is about to put meaningful config there.
2. `fiber_id`, unless artifacts are about to use explicit fiber ids.
3. Backup/temp SVG files under `assets/images`.
4. The stale root README engineering-continuity link.
5. Any public-release text that still assumes a sibling `../state_collapser` checkout after the GitHub tag strategy is implemented.

## What I would rewrite first

Rewrite the edge-fiber path.

The current API:

```python
edge_fiber_targets(...) -> frozenset[str]
```

should become, or be supplemented by:

```python
edge_fiber_edges(...) -> tuple[str, ...]
```

Then use target ids as a derived view:

```python
edge_fiber_targets(...) = frozenset(edge_target(edge_id) for edge_id in edge_fiber_edges(...))
```

The direct extension function also needs a constrained-witness mode. One possible shape:

```python
extend_simplex_direct(
    graph,
    simplex,
    target,
    projection_simplex_id=downstairs.id,
    allowed_last_edge_ids=compatible_final_edges,
    allowed_face_edge_ids_by_source_index=compatible_face_edges,
)
```

For direct bottom-tier enumeration, those `allowed_*` arguments are omitted, preserving current behavior. For lifted enumeration, they are required whenever the downstairs simplex carries edge-level witness data.

The invariant should be brutally simple:

```text
Every witness edge id in an upstairs lifted simplex must project to one of the corresponding witness edge ids in the downstairs simplex it claims to lift.
```

That invariant belongs in tests and probably in a debug/audit helper.

## Concrete patch plan

1. Extend the adapter protocol.
   - Add `edge_fiber_edges`.
   - Keep `edge_fiber_targets` temporarily as a derived compatibility method.

2. Add edge-fiber indexes to `StateCollapserStaticTowerAdapter`.
   - Cache per upstairs tier.
   - Include formal identities.
   - Include non-identity action-cell edges.
   - Key by downstairs edge id and upstairs source id.

3. Rewrite `EdgeFiberRecord`.
   - Add `upstairs_edge_ids`.
   - Keep `upstairs_target_ids` as derived/summary data.
   - Update artifact serialization.

4. Add constrained witness construction.
   - Final edge: use only edge ids in the selected final-edge fiber.
   - Higher-degree new face edges: use only edge ids compatible with the downstream face witness set.

5. Add projection-audit tests.
   - First for degree 1 parallel edges.
   - Then degree 2 with non-final face witnesses.
   - Then artifact serialization.

6. Add the no-downstairs-interior regression test.
   - Keep it separate and named after the small-object/Kan distinction.

7. Run the existing smoke scripts as snapshot tests.

8. Only after the above, continue release prep.

## Release readiness call

This is not release-ready yet. The package can be made release-ready without a big rewrite, but the witness/fiber issue is central enough that publishing before fixing it would be the wrong standard.

Current status:

- Implementation shape: promising.
- Code size: healthy.
- Tests: fast, but missing the most important projection-trace tests.
- Performance structure: conceptually right, mechanically not indexed yet.
- Artifacts: useful, but edge-fiber evidence is incomplete.
- Public packaging: still local-development shaped.

## Final standard

Before this code should be trusted as a public pre-release, every emitted lifted simplex must be able to pass this audit:

```text
For each upstairs simplex sigma over downstairs simplex tau:
  sigma.degree == tau.degree
  project vertices(sigma) == vertices(tau)
  every witness edge in sigma projects to the corresponding witness edge in tau
  every recorded final edge lies in the final-edge fiber used to generate sigma
```

Passing count tests is not enough. Counts say which addresses appeared. This package also promises evidence for why those addresses are valid over a static quotient tower. That evidence has to be true.
