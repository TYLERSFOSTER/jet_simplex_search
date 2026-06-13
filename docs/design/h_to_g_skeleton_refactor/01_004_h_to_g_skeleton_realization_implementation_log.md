# H-To-G Skeletonization And H-Lift Implementation Log

## Status

Implementation started after Project Owner instruction:

```text
execute docs/design/h_to_g_skeleton_refactor/01_003_h_to_g_skeleton_realization_implementation_workplan.md
```

## Initial Scope

Approved scope is interpreted as the full workplan execution for the present
`jet_simplex_search` package, with `state_collapser` work treated as part of the
plan when repository permissions and dependency reality allow it.

## Initial Repository State

Date:

```text
2026-06-13
```

Branch:

```text
main
```

Initial `jet_simplex_search` status:

```text
clean
```

Initial adjacent `state_collapser` status:

```text
clean
```

## Baseline Tests

Command:

```text
uv run pytest
```

Result:

```text
58 passed in 0.08s
```

## Semantic Lock

Implementation must preserve:

- H is skeletonized to simple G before tower search.
- H-lifts are computed only over `G^0`.
- Degenerate G simplices lift to H exactly through actual H loops.
- Parallel H edges produce distinct H-lifted simplices through compressed
  product counts.
- Zero-count skeleton simplices remain present by default.
- The small-object tower lift searches only over existing downstairs simplices.
- Abdul Malik attribution remains intact in public algorithm documentation.

## Progress

### Phase 1 - JSS Skeletonization Core

Completed:

- Added deterministic skeleton edge, tier simple edge, and H-lift id helpers.
- Added `src/jet_simplex_search/skeleton.py`.
- Added explicit skeleton edge fibers, loop fibers, diagnostics, result record,
  skeletonization function, and invariant checks.
- Added tests for loops, parallel edges, identical labels, label conflicts, and
  skeletonization invariants.

Focused test result:

```text
uv run pytest tests/test_ids.py tests/test_skeleton.py
15 passed
```

### Phase 2 - Simple-Reflexive Normalization Assertions

Completed:

- Added `assert_simple_reflexive_normalized_graph`.
- Wired the assertion into direct simplex enumeration.
- Clarified simplex witness docstrings as skeleton/tower evidence.
- Added normalization tests for skeletonized graphs and parallel rejection.

Focused test result:

```text
uv run pytest tests/test_normalize.py tests/test_bottom_tier_enumeration.py tests/test_directed_flag_semantics.py tests/test_static_search_fake_tower.py tests/test_fiber_lift.py
24 passed
```

### Phase 3 - H-Lift Computation

Completed:

- Added `src/jet_simplex_search/h_lift.py`.
- Added compressed H-lift face factors, simplex H-lift records, diagnostics, and
  tier-0 H-lift computation.
- Added tests for degree 0, parallel non-loop edges, zero-loop degenerates,
  loop-supported degenerates, triangle products, left/right degenerates,
  totally degenerate 2-simplices, missing fibers, and diagnostics.

Focused test result:

```text
uv run pytest tests/test_h_lift.py tests/test_skeleton.py tests/test_normalize.py
30 passed
```

### Phase 4 / Phase 7 - Public API And Artifacts

Completed:

- Added `SearchWithHLiftsResult`.
- Preserved lower-level skeleton/tower search through `search_skeleton_simplices`.
- Rewired graph-based `search_simplices` to skeletonize H, search G, and compute
  tier-0 H-lifts.
- Updated artifact writing for schema version 2 combined results.
- Added skeleton fiber and H-lift artifact serialization.
- Updated API and artifact tests.

### Phase 6 - JSS Adapter View And Indexing

Completed:

- Added tier-0 adapter vertex to input vertex mapping.
- Changed JSS adapter tier edges to simple endpoint-pair edges.
- Changed simple tier edge projection to endpoint-determined projection.
- Added lazy indexed `edge_fiber_targets` lookup by
  `(upstairs_tier, downstairs_edge_id, upstairs_source_id)`.

Important upstream note:

```text
The current adjacent state_collapser still groups live action cells by
(source_cell, target_cell, primitive_action_identity). The JSS adapter now
consumes a simple endpoint-pair tier view, which makes the current package tests
and records coherent, but this is not the final upstream construction invariant
required by the blueprint. A state_collapser simple-reflexive tier construction
mode remains a release blocker.
```

Focused test result:

```text
uv run pytest tests/integration/test_state_collapser_static_tower.py tests/test_tower_adapter_fake.py tests/test_fiber_lift.py tests/test_api.py tests/test_artifacts.py
21 passed
```

### Phase 8 / Phase 9 - Regression And Documentation

Completed:

- Added regression for "upstairs triangle exists, but downstairs 2-simplex
  record is absent; do not search/emit upstairs triangle."
- Updated smoke table utility to label skeleton counts separately from H-lift
  counts.
- Updated README semantics and runnable example output for combined graph-H
  results.
- Refreshed smoke Markdown output blocks for `smoke_003` through `smoke_016`.
- Updated parallel-edge and input-loop smoke arguments to explain H-lift counts.

Smoke verification:

```text
uv run python smoke/smoke_001.py
uv run python smoke/smoke_002.py
...
uv run python smoke/smoke_016.py
all completed successfully
```

## Final Verification

Full JSS test command:

```text
uv run pytest
```

Result:

```text
90 passed in 0.09s
```

Build command:

```text
uv build --out-dir /private/tmp/jet-simplex-search-dist
```

Result:

```text
Successfully built /private/tmp/jet-simplex-search-dist/jet_simplex_search-0.1.0.tar.gz
Successfully built /private/tmp/jet-simplex-search-dist/jet_simplex_search-0.1.0-py3-none-any.whl
```

Note:

```text
The first build attempt inside the sandbox failed because uv could not access
its cache. The build was rerun with approved cache access and succeeded.
```

Final build rerun note:

```text
After line-wrap cleanup, uv run pytest was rerun and passed. A second build
rerun hit the same sandbox cache restriction, and the escalation prompt was not
approved. The successful build above was before formatting-only line wrapping.
```

## Deferred / Blocked

Upstream `state_collapser` simple-reflexive tier construction mode remains
deferred in this pass. The JSS adapter now consumes a simple endpoint-pair tier
view and indexes fibers correctly, but the upstream construction invariant from
the blueprint is still required before treating this as final public-release
architecture.

No upstream `state_collapser` source files were edited in this pass.
