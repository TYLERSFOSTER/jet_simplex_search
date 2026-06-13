# synthetic_blow review

I am reviewing this through a Jonathan-Blow-inspired lens: direct, performance-aware, skeptical of unnecessary abstraction, and focused on reducing complexity. This is not an impersonation or endorsement.

## Verdict

The core package is small enough to understand, and that is its best property. The bad part is that the central promise, fiber-addressed simplex search with truthful lift artifacts, is not fully protected in the implementation. Lifting is indexed by downstairs simplices, which is correct, but the final edge fiber is target-only, and witness construction then falls back to all upstairs edges with the same endpoints. That can emit a simplex whose address is right and whose witness/projection trace is false. For this project, that is not a polish issue. It is the thing that must be fixed before a public release can be trusted.

## Program map

- Entry point: `src/jet_simplex_search/api.py`, `search_simplices`.
- Training loop: not applicable. This is not an RL project.
- Evaluation loop: not applicable.
- Environment boundary: graph/tower boundary through `GraphInput`, `normalize_graph`, and `StaticTowerAdapterProtocol`.
- Model/update code: not applicable. The analogous core algorithm is direct enumeration plus static tower lifting.
- Replay/rollout storage: not applicable. The analogous stored data is `SimplexRecord`, `FaceEdgeWitness`, `SimplexFiberRecord`, and `EdgeFiberRecord`.
- Config: `pyproject.toml`; runtime input is graph, adapter, contraction schema, and `k`.
- Checkpoints/logs: no checkpoints. Artifacts are written through `src/jet_simplex_search/artifacts.py`.
- Tests: `tests/`, currently 58 pytest tests passing.

Important execution path:

- `api.py:45` `search_simplices`
- `search.py:131` `run_static_small_object_search`
- `search.py:100` `enumerate_direct_simplices`
- `lift.py:97` `lift_tier_simplices`
- `lift.py:65` `lift_downstairs_extension`
- `tower_adapter.py:82` `StateCollapserStaticTowerAdapter`
- `artifacts.py:30` `write_search_artifact`

## The real data path

The actual data path is:

```text
GraphInput
  -> normalize_graph
  -> formal identities, edge lookup, adjacency/frontier maps
  -> state_collapser static tower adapter
  -> bottom-tier direct simplex enumeration
  -> upstairs lifting over downstairs simplex fibers
  -> diagnostics and optional artifacts
```

The central data units are strings, tuples, frozen sets, and immutable dataclass records. There is no tensor/RL data path here. The correctness surface is:

- simplex address: tier, degree, vertex tuple;
- face-edge witnesses: every directed face edge used by the simplex;
- last-edge witnesses: final extension edge ids;
- projection simplex id: the downstairs simplex being lifted;
- edge-fiber membership: the upstairs edge must project to the claimed downstairs final edge.

Counts alone are not enough for this package. Counts prove the address set only. The package also promises traceable mathematical evidence, and the witness trace has to be true.

## Highest-severity issues

### Issue 1

- Severity: blocker
- Location: `src/jet_simplex_search/lift.py:65`, `src/jet_simplex_search/search.py:60`, `src/jet_simplex_search/frontier.py:30`
- Problem: fiber lifting filters by target vertex, then `extend_simplex_direct` records every edge id between the same source/target pair. If two upstairs edges share endpoints but project to different downstairs edges, a lifted simplex over downstairs edge `XY` can record a witness edge that actually projects somewhere else.
- Why it matters: the emitted simplex address can be correct while the artifact evidence is wrong. That invalidates traceability, which is one of the package's core claims.
- Fix: make edge fibers return edge ids, not just target vertices. Pass an allowed edge-id set into the extension path. The lifted simplex must record only final-edge witnesses compatible with the downstairs simplex face being lifted. For non-final face witnesses, either keep the current all-edge witness semantics intentionally documented, or filter those witnesses too when the downstairs simplex supplies face-level projection data.

Patch shape:

```text
adapter.edge_fiber_edges(...)
    -> tuple[upstairs_edge_id, ...]

lift_downstairs_extension(...)
    allowed_last_edge_ids = union edge_fiber_edges(...)
    targets = targets of allowed_last_edge_ids intersect upstairs_prefix.frontier
    extend_simplex_direct(..., allowed_last_edge_ids=...)
```

The key rule is that a lifted simplex over a downstairs simplex must not carry witness edges outside that downstairs simplex's edge fibers.

### Issue 2

- Severity: high
- Location: `src/jet_simplex_search/tower_adapter.py:218`
- Problem: `edge_fiber_targets` scans all tier edges for every fiber query. It also calls `tier_edges`, which populates edge caches by walking action cells.
- Why it matters: the package's speed story is that search happens only in meaningful fibers. Repeated broad scans spend the complexity budget in exactly the place the algorithm is supposed to avoid.
- Fix: build a per-tier edge-fiber index once.

Index shape:

```text
(upstairs_tier, downstairs_edge_id, upstairs_source_id)
    -> upstairs edge ids
    -> upstairs target ids
```

The lifting hot path should be indexed lookup plus frontier intersection, not a scan through the tier.

### Issue 3

- Severity: medium
- Location: `src/jet_simplex_search/lift.py:125`
- Problem: the code structurally lifts only over existing downstairs degree records, but there is no regression test for the important case where downstairs has the boundary data that tempts a fill but no downstairs 2-simplex.
- Why it matters: this is the central difference between the current small-object search and a Kan-filling version. If this regresses, the package silently starts doing a different mathematical algorithm.
- Fix: add a fake-tower test where upstairs contains a full 2-simplex but downstairs has no corresponding degree-2 simplex record. Assert no upstairs degree-2 simplex is emitted over that missing downstairs simplex.

The current structural safeguard is good:

```text
for degree in range(1, k + 1):
    for downstairs in downstairs_simplices_by_degree.get(degree, ()):
```

But this is important enough to deserve a named test.

### Issue 4

- Severity: medium
- Location: `README.md:73`, `README.md:238`, `pyproject.toml:25`
- Problem: release-facing surfaces still describe a local-development dependency on `../state_collapser`, and the README contains a stale continuity-report link.
- Why it matters: this is public-release hygiene. Broken links and local-only dependency paths make the project look less serious than the code is.
- Fix: for the release branch, switch to the approved GitHub `state_collapser` tag strategy and remove the stale root README continuity link according to the approved release decisions.

## Abstractions that should justify themselves or die

| abstraction | users | cost | benefit | recommendation |
| --- | ---: | --- | --- | --- |
| `StaticSearchContext` | 1 | extra object hop before doing the obvious call | almost none right now | inline unless it is about to carry real config |
| `StaticTowerAdapterProtocol` | many | protocol boundary and adapter vocabulary | isolates `state_collapser` from the search engine | keep |
| `SimplexRecord` | central | many fields | makes the mathematical invariants visible | keep |
| `EdgeFiberRecord` target-only shape | lift/artifacts | loses edge identity | partial trace only | rewrite to include edge ids |
| `fiber_id` helper | appears unused | dead concept in id namespace | none now | delete or put it to work |
| backup/temp SVG files under `assets/images` | none for package logic | public-release clutter | none | remove before public release |

## RL correctness traps

This is not an RL project. The analogous correctness traps are graph/tower traceability traps:

- witness edges that do not project to the claimed downstairs face;
- generating upstairs interiors over downstairs boundaries;
- formal identities and input loops changing counts invisibly;
- parallel edges collapsing into one address while witnesses still need to remain truthful;
- artifacts presenting evidence that the in-memory search did not actually constrain;
- release docs claiming more than the tests prove.

The package currently handles the "do not search upstairs over a missing downstairs simplex" rule structurally. It does not yet protect witness-edge compatibility strongly enough.

## Performance and feedback loop

The local feedback loop is good:

```text
uv run pytest
58 passed in 0.07s
```

The likely hot path is not good enough yet:

- `lift_tier_simplices` repeatedly asks for final-edge fibers.
- `StateCollapserStaticTowerAdapter.edge_fiber_targets` answers by scanning tier edges.
- The search is conceptually sparse and fiber-addressed, but the adapter has not paid the one-time indexing cost that would make that true mechanically.

Shortest useful profiling plan:

- sparse path graph through a quotient tower;
- transitive chain with many simplices through degree 4;
- graph with repeated same-source-target parallel edges;
- quotient tower where many upstairs edges collapse to identity downstairs;
- measure fiber queries, edge scans, emitted simplices, artifact size, and wall time.

Do not optimize random local Python before fixing the index. The index is the performance design.

## Tests that actually matter

Add these first:

- multiedge same-source-target, different downstairs projections; assert lifted witnesses only use compatible edge ids;
- downstairs boundary/no interior should not lift an upstairs interior;
- edge-fiber index equivalence against the current fake adapter behavior;
- artifact witness projection consistency for every emitted lifted simplex;
- smoke output snapshots for the existing smoke scripts;
- README quick-start regression;
- input-loop stripping and formal identity behavior;
- parallel-edge witness preservation without duplicate simplex addresses.

## What I would delete first

1. `StaticSearchContext`, unless it is about to carry real release configuration.
2. Unused `fiber_id`, unless artifact ids are about to use it.
3. Backup/temp SVG files under `assets/images` before public release.
4. Any README release link that points at internal continuity work or stale paths.

## What I would rewrite first

Rewrite the lifting edge-fiber path.

The adapter should expose edge-fiber records with actual edge ids:

```text
edge_fiber_edges(
    upstairs_tier,
    downstairs_edge_id,
    upstairs_source_id,
) -> tuple[str, ...]
```

Then lifting should:

1. ask for compatible upstairs edge ids over the downstairs final edge;
2. derive target ids from those edge ids;
3. intersect target ids with the prefix frontier;
4. extend the simplex while carrying only the compatible final edge ids;
5. emit an `EdgeFiberRecord` that includes both target ids and edge ids.

This is the smallest rewrite with the highest leverage because it fixes both the traceability bug and the performance shape.

## Final standard

Before this should be trusted as a release candidate, every emitted lifted simplex must prove that its witnesses are compatible with its projection fiber. Passing counts are not enough. Counts say which simplex addresses were emitted. This package also claims mathematical traceability through a static quotient tower, and that trace has to be true.
