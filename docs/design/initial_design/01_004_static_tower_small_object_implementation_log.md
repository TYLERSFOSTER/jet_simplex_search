# Static Tower Small-Object Implementation Log

## Status

Implementation log for:

```text
docs/design/initial_design/01_003_static_tower_small_object_implementation_workplan.md
```

## Approval

The Project Owner approved execution with:

```text
execute `docs/design/initial_design/01_003_static_tower_small_object_implementation_workplan.md`
```

Approved scope: execute the workplan in order, including local implementation,
artifact support, public API, and real `state_collapser` integration unless a
workplan stop condition triggers.

## Baseline

Date: 2026-06-12

Branch:

```text
main
```

Baseline commit:

```text
c0ae6f0ed8f24cb95f506eaa5cd9ba48bbba3293
```

Baseline git status:

```text
## main...origin/main
```

Baseline command:

```text
uv run pytest
```

Baseline result:

```text
1 passed
```

## Execution Notes

- Phase 0 baseline checks passed before implementation edits.
- The implementation must preserve Abdul Malik attribution in the design docs.
- The implementation must treat `state_collapser` as the owner of tower
  semantics and use local indexes only as derived simplex-search caches.

## Phase Results

### Phase 1 - Core Graph And Error Contracts

Completed.

Implemented package-local error types, sparse graph input records, graph
validation, and deterministic id helpers for identities, simplices, and fibers.

Tests added for graph validation, error inheritance, deterministic identity ids,
simplex ids, and fiber ids.

### Phase 2 - Loop Normalization

Completed.

Implemented first-scope normalization:

- input loops are stripped;
- exactly one formal identity edge is emitted for every vertex;
- original non-loop edges remain distinct from formal identities;
- normalized adjacency includes reflexive targets for degenerates.

Tests verify duplicate rejection, loop stripping, identity insertion, id
collision handling, and normalization invariants.

### Phase 3 - Frontier And Simplex Records

Completed.

Implemented immutable simplex records, face-edge witness records, frontier
intersection helpers, and the inductive recurrence:

```text
F(sigma) = F(partial_m sigma) cap A(tgt sigma)
```

Tests verify the recurrence, directed face witnesses, and first-class
degenerate records.

### Phase 4 - Bottom-Tier Direct Enumeration

Completed.

Implemented direct tier enumeration through `k` by extending known simplices
through cached frontiers. The implementation rejects missing directed flag
faces: for example, `0 -> 1 -> 2` is not emitted as a 2-simplex unless the
face edge `0 -> 2` exists.

Tests verify 0-simplex emission, identity-generated degenerates, directed flag
semantics, and non-emission when required face edges are absent.

### Phase 5 - Fake Static Tower Adapter

Completed.

Implemented the static tower adapter protocol and tier normalization helper.
Added a fake two-tier tower with a nondegenerate upstairs edge over a
downstairs identity edge.

Tests verify tier exposure, formal identity addition at tier views, and
source-sensitive edge fibers.

### Phase 6 - Fiber-Addressed Lifting

Completed.

Implemented degree-zero lifting, higher-degree lifting, simplex-fiber records,
edge-fiber records, and full static search orchestration. Higher-degree
lifting is indexed by known downstairs simplices and their final edge fibers,
rather than by global upstairs candidate enumeration.

Tests verify:

- vertex fibers for degree zero;
- nondegenerate upstairs edges over downstairs identities;
- final-edge fiber targeting;
- full fake-tower static search.

### Phase 7 - Diagnostics And Artifacts

Completed.

Implemented diagnostics, single-JSON artifact writing, and manifest-plus-table
artifact writing. Artifact rows include simplex witnesses, prefix/projection
traceability, fiber rows, edge-fiber rows, and diagnostics.

Tests verify artifact reload, manifest table files, row counts, and optional
count-only fiber rows.

### Phase 8 - Public API

Completed.

Implemented:

- `build_static_search_context`;
- `search_simplices`;
- optional artifact writing;
- deliberate top-level export of `search_simplices`.

Tests verify invalid `k`, fake-adapter search, and artifact writing through
the public API.

### Phase 9 - Real state_collapser Integration

Completed.

Dependency decision:

- `state_collapser` is referenced as a local editable path dependency during
  development:

```toml
[tool.uv.sources]
state-collapser = { path = "../state_collapser", editable = true }
```

Verification command:

```text
uv run python -c "import state_collapser; print(state_collapser.__version__)"
```

Result:

```text
0.7.2
```

Implemented `StateCollapserStaticTowerAdapter` over
`state_collapser.tower.partition.PartitionTower` using
`build_partition_tower_full`. The adapter maps local graph records into
`State`, `PrimitiveAction`, and `BaseEdge` records, exposes static tier
vertices and action-cell edges, and implements vertex projection, edge
projection, bottommost nondegenerate tier selection, and source-sensitive
edge-fiber target queries.

Integration tests verify:

- a tiny graph builds a static partition tower;
- a contraction maps multiple upstairs vertices to one downstairs state cell;
- an upstairs internal edge projects to a downstream identity;
- the downstream identity fiber includes a nonidentity upstairs edge;
- `search_simplices` can run through the real adapter.

Focused result:

```text
uv run pytest tests/integration/test_state_collapser_static_tower.py
4 passed
```

### Phase 10 - Documentation And Examples

Completed.

Updated `README.md` with:

- a minimal `search_simplices` example using `GraphInput` and
  `LabelBlockSchema`;
- links to the source design note, package blueprint, implementation workplan,
  and this implementation log.

### Phase 11 - Final Verification

Completed.

Full suite command:

```text
uv run pytest
```

Full suite result:

```text
58 passed
```

Artifact smoke command generated a manifest-table artifact at:

```text
/private/tmp/jet-simplex-search-artifact-smoke
```

Artifact smoke result:

```text
bottom_tier=1 simplex_records=14 simplex_fibers=5 edge_fibers=7
```

Invariant checklist:

- Abdul Malik attribution remains intact in the design docs.
- `state_collapser` owns tower construction and projection semantics.
- Local caches are derived from the static tower and normalized tier views.
- Graph normalization emits exactly one formal identity per vertex.
- Directed flag semantics require all face edges.
- Degenerate simplices are emitted as first-class records with their full
  arity/address.
- The frontier recurrence is implemented by cached set intersection.
- Bottom-tier enumeration includes degenerates through `k`.
- Tower descent searches over known downstairs simplex fibers.
- Final-edge fiber targeting is enforced by `edge_fiber_targets`.
- Artifacts preserve simplex witnesses, prefix ids, projection ids, simplex
  fibers, edge fibers, and diagnostics.

### Phase 12 - Future Deferral Register

Completed.

Deferred from this first implementation:

- Kan replacement;
- meaningful non-identity input loops;
- one simplex per multigraph witness choice;
- compressed, SQLite, or DuckDB artifact storage;
- bitset, CSR, GPU, or tensor acceleration;
- multiprocessing.
