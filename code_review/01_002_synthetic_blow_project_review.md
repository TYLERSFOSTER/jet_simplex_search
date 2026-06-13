# synthetic_blow review

I am reviewing this through a Jonathan-Blow-inspired lens: direct, performance-aware, skeptical of unnecessary abstraction, and focused on reducing complexity. I am not impersonating him.

## Verdict

The project is much sharper than the earlier review target. The h-to-g skeleton refactor is present, the lifting path is fiber-addressed instead of broad-search-and-filter, the old target-only edge-fiber problem is fixed, and the test suite is fast: `uv run pytest` reports `90 passed in 0.10s`.

The remaining release risk is not that the code is sprawling. It is that the most important invariant is split across layers. `jet_simplex_search` now realizes a simple-reflexive skeleton view of the input graph, but `state_collapser` is still asked to build the tower through its ordinary graph path. The adapter later reads tier edges as a simple endpoint-pair view. That may be acceptable as an interim bridge, but it is not yet a clean realization of the stated algorithm: "remove loops and collapse parallel edges before the next quotient tier is built."

So the short version is:

- The core package is small and direct.
- The h-to-g lift bookkeeping is real and test-covered.
- The simplex lifting hot path is now indexed enough to match the intended small-object search.
- The public API and artifact layer still have avoidable shape ambiguity.
- The release surface still contains local-path and documentation drift.
- The biggest mathematical risk is whether upstream tower construction is using the same simple-reflexive graph semantics that the adapter exposes downstream.

## Program map

Entry point:

- `src/jet_simplex_search/api.py:66` `search_simplices`

Core graph normalization and simplex enumeration:

- `src/jet_simplex_search/normalize.py:47` `normalize_graph`
- `src/jet_simplex_search/frontier.py:20` `extend_simplex_direct`
- `src/jet_simplex_search/search.py:100` `enumerate_direct_simplices`
- `src/jet_simplex_search/search.py:131` `run_static_small_object_search`

H-to-G skeleton realization:

- `src/jet_simplex_search/skeleton.py:14` `SkeletonLabelPolicy`
- `src/jet_simplex_search/skeleton.py:86` `SkeletonizationResult`
- `src/jet_simplex_search/skeleton.py:125` `skeletonize_graph`
- `src/jet_simplex_search/skeleton.py:239` `assert_skeletonization_invariants`

Tower adapter boundary:

- `src/jet_simplex_search/tower_adapter.py:18` `StaticTowerAdapterProtocol`
- `src/jet_simplex_search/tower_adapter.py:81` `StateCollapserStaticTowerAdapter`
- `src/jet_simplex_search/tower_adapter.py:106` `from_graph`
- `src/jet_simplex_search/tower_adapter.py:171` `tier_edges`
- `src/jet_simplex_search/tower_adapter.py:244` `edge_fiber_targets`
- `src/jet_simplex_search/tower_adapter.py:297` `_ensure_edge_fiber_index`

Fiber lifting:

- `src/jet_simplex_search/lift.py:65` `lift_downstairs_extension`
- `src/jet_simplex_search/lift.py:97` `lift_tier_simplices`

Expanded H-lift accounting:

- `src/jet_simplex_search/h_lift.py:14` `HLiftFaceFactor`
- `src/jet_simplex_search/h_lift.py:60` `HLiftSearchResult`
- `src/jet_simplex_search/h_lift.py:133` `compute_h_lifts_for_tier_zero`
- `src/jet_simplex_search/h_lift.py:232` `_face_factors_for_simplex`

Artifacts:

- `src/jet_simplex_search/artifacts.py:30` `SearchArtifactConfig`
- `src/jet_simplex_search/artifacts.py:35` `write_search_artifact`
- `src/jet_simplex_search/artifacts.py:120` `_result_payload`
- `src/jet_simplex_search/artifacts.py:260` `_write_combined_manifest_tables`

Release-facing metadata:

- `pyproject.toml:1` package metadata
- `README.md:1` public package introduction

Tests:

- `tests/test_h_lift.py:1` h-lift expansion tests
- `tests/test_artifacts.py:1` artifact tests
- `tests/test_lift.py:1` fiber lifting tests
- `tests/test_search.py:1` small-object search tests

There is no RL training loop here. The review kit's RL categories translate to this package as: data path, search path, witness truth, projection consistency, and feedback-loop speed.

## The real data path

The actual path is:

```text
GraphInput H
  -> skeletonize_graph(H)
       G skeleton vertices
       G skeleton edges
       vertex fibers H -> G
       edge fibers H edge ids -> G edge ids
  -> StateCollapserStaticTowerAdapter.from_graph(G)
       static quotient tower
       tier vertex projections
       tier edge projections
       indexed edge fibers
  -> run_static_small_object_search(adapter, k)
       bottom direct simplex enumeration
       upward fiber-addressed lifting
       SimplexSearchResult
  -> compute_h_lifts_for_tier_zero(H, skeletonization, skeleton_search)
       expanded H-lift counts
       face factor products
       per-simplex lift diagnostics
  -> SearchWithHLiftsResult
  -> optional artifact writer
```

The important records are immutable dataclasses and tuples:

- `SimplexRecord`: simplex address, vertices, edges, degeneracy, projection, cached frontier.
- `EdgeRecord`: directed edge id, source, target, identity flag.
- `SkeletonizationResult`: H-to-G vertex and edge fibers.
- `HLiftRecord`: expanded H-lift count and face-factor diagnostics.
- `SimplexSearchResult`: all tiered simplex records and search diagnostics.
- `SearchWithHLiftsResult`: skeletonization plus skeleton search plus expanded H-lift accounting.

The package is currently mostly data-structure code. That is good. The correctness surface is correspondingly unforgiving: if a simplex is emitted, its vertex address, edge witnesses, projection id, and H-lift factors must all agree.

## Highest-severity issues

### High: the simple-reflexive invariant is still adapter-side, not tower-construction-side

Location:

- `src/jet_simplex_search/api.py:79`
- `src/jet_simplex_search/tower_adapter.py:106`
- `src/jet_simplex_search/tower_adapter.py:120`
- `src/jet_simplex_search/tower_adapter.py:171`

`search_simplices(graph=...)` now correctly calls `skeletonize_graph` before building the static tower. That means the graph passed into `StateCollapserStaticTowerAdapter.from_graph` is simple and loop-free at the package boundary.

But the actual tower construction call is still:

```python
tower = build_partition_tower_full(
    graph,
    contraction=contraction,
    max_iters=max_iters,
)
```

After that, `tier_edges` reconstructs a simple endpoint-pair view from the tower action cells. This means `jet_simplex_search` is currently enforcing simple-reflexive semantics at input and readout, but not necessarily inside every quotient construction step in `state_collapser`.

Why this matters:

The algorithmic claim is not just "present a simple graph to the simplex engine." It is "each tier is the simple-reflexive realization of the quotient before the next tier is used." If parallel edges or loops influence a later state-collapser contraction before being excised, then the produced tower may differ from the intended tower even if the adapter later hides the multiplicity.

This is the kind of bug that can pass low-dimensional count tests while still violating the mathematical contract.

Fix:

- Add an explicit state-collapser tower mode or builder policy for simple-reflexive quotient realization.
- The policy should strip non-identity loops and collapse parallel directed edges before each next quotient tier is constructed.
- `StateCollapserStaticTowerAdapter.from_graph` should request that policy explicitly instead of reconstructing it after the fact.
- Add an integration test with at least two quotient steps where parallel multiplicity would change the next tier if not excised.

#### PO Reply
> Why not do something like this: `state_collapser` is used to build tier-$i$ to tier-$i+1$, then something in `jet_simplex_search` cleans the new quotient graph, then feeds it to a new quotient contructor. The only complication is that contraction schema needs to be worked more carefully here. Does this solve the problem? Let me know in detail. Is it beeter to add this capability in `state_collapser`? Am I even understanding the issue?

#### Codex Reply
> Yes, you are understanding the issue. The issue is exactly about *where* the cleaning happens in the tower construction, not about whether the package knows how to view a graph as simple-reflexive once it already has a tier in hand.
>
> Your proposed solution does solve the mathematical problem if it is implemented as the actual tower-building loop:
>
> ```text
> start with H
>   -> skeletonize / realize as clean G_0
>   -> ask state_collapser for one quotient step G_i -> raw Q_{i+1}
>   -> clean raw Q_{i+1} into G_{i+1}
>   -> record the projection G_i -> G_{i+1}
>   -> repeat
> ```
>
> The important point is that `G_{i+1}` must be cleaned *before* it becomes the input to the next contraction step. If `state_collapser` constructs the whole tower internally and only afterward `jet_simplex_search` reads each tier through a simplified adapter view, then multiplicities or loops may already have affected the next contraction. That is the thing I was flagging.
>
> So there are two viable architectures.
>
> Option A: add this capability inside `state_collapser`.
>
> This is cleaner if `state_collapser` is willing to own a "simple-reflexive quotient tower" mode. Then `jet_simplex_search` can say: build me the tower with quotient realization policy `simple_directed_no_nonidentity_loops`, and the adapter can trust that every tier was built under that policy. This keeps the quotient-construction machinery in the package that already owns quotient construction. It is probably the best long-term boundary if other projects will also want this kind of tower.
>
> Option B: make `jet_simplex_search` orchestrate the tower one step at a time.
>
> This is also legitimate. In that design, `state_collapser` is used as a one-step quotient engine, while `jet_simplex_search` owns the semantics of the tower it needs:
>
> ```text
> current clean tier G_i
> contraction schema chooses contractions on G_i
> state_collapser returns raw quotient data
> jet_simplex_search realizes raw quotient as clean G_{i+1}
> jet_simplex_search records vertex and edge projection fibers
> ```
>
> The complication you named is the right one: the contraction schema has to be expressed in a way that survives this loop. If the schema depends only on the current clean tier, this is straightforward. If the schema depends on internal state-collapser tower state, historical action cells, or multiplicities that we intend to discard, then the boundary becomes messy.
>
> My preference:
>
> - If `state_collapser` can expose a one-step quotient API with enough projection data, then `jet_simplex_search` orchestrating the loop is totally reasonable and perhaps more honest for this package.
> - If `state_collapser` already has the right internal extension point for quotient-realization policy, put it there and keep `jet_simplex_search` thinner.
> - Do not let the current adapter-only simplification be the final answer, because that cleans the view of a tower after the tower has already been constructed.
>
> So yes: your proposal addresses the problem. The design decision is ownership. `state_collapser` ownership gives a cleaner shared primitive; `jet_simplex_search` ownership gives tighter control over the exact H-to-G-to-tower semantics. The one unacceptable middle state is "build a possibly non-simple tower, then pretend each tier was simple when we enumerate simplices."

### Medium-high: `search_simplices` has two different public meanings

Location:

- `src/jet_simplex_search/api.py:66`
- `src/jet_simplex_search/api.py:75`
- `src/jet_simplex_search/api.py:79`
- `src/jet_simplex_search/api.py:98`
- `src/jet_simplex_search/api.py:106`

The public API currently does two different jobs:

- With `graph=...`, it skeletonizes H, searches the skeleton tower, and returns `SearchWithHLiftsResult`.
- With `adapter=...`, it skips H-to-G realization and returns `SimplexSearchResult`.

That is too much semantic branching for the top-level public function. It also creates an ambiguity: if a caller passes both `graph` and `adapter`, the adapter path wins and the graph is silently ignored.

Why this matters:

This is a release-facing library. The main function should not change result type based on which optional argument happened to be present. This also spreads into the artifact layer, which now has to inspect object shape instead of receiving one clear result type.

Fix:

- Make `search_simplices(graph=...)` the H-input public API and return one stable combined result type.
- Add a separate internal or explicitly named function for skeleton/tower searches, for example `search_skeleton_simplices(adapter=...)`.
- Reject `graph` plus `adapter` as an invalid call.
- Move `SearchWithHLiftsResult` out of `api.py` and into a records/results module.

#### PO Reply
> I don't quite understand. These aren;t really mutually exclusive, so I'm lost. Look at how I describe the pipeline in other documentation: We are studying $H$, but we first clean it to $G$. The twoer for $G$ is clean at each step. We find simplices there, then at last stage, we do the multiplicity/etale lift. Doesn;t this clarify the whole matter?

#### Codex Reply
> Yes, your pipeline description clarifies the intended mathematics. My complaint is narrower and more API-shaped than the phrase "mutually exclusive" made it sound.
>
> Mathematically, these are not two rival workflows:
>
> ```text
> study H
>   -> clean/skeletonize to G
>   -> build the clean tower G^bullet
>   -> search simplices in G^bullet
>   -> perform multiplicity / etale H-lift accounting
> ```
>
> That is one workflow. I agree with that.
>
> The code-level issue is that the public function currently exposes two entry routes that skip different parts of that workflow:
>
> - `search_simplices(graph=H, ...)` means "run the whole H pipeline."
> - `search_simplices(adapter=A, ...)` means "assume somebody already gave me a tower-like object and only run the skeleton/tower simplex search."
>
> Those are both useful operations, but they are not the same public promise. One returns the H-aware result with skeletonization and H-lift diagnostics. The other returns only the tower simplex result. That is the ambiguity I meant.
>
> Your clarification actually tells us the right API:
>
> ```text
> public:
>   search_simplices(H, k)
>     runs the whole package pipeline
>
> lower-level/internal/testing:
>   search_skeleton_simplices(G_tower_or_adapter, k)
>     runs only the clean tower search
> ```
>
> So the fix is not to deny the pipeline. It is to make the function names match the pipeline. `search_simplices` should probably mean "I am studying H." The adapter route should exist as a lower-level helper because tests, smoke scripts, and advanced users need it, but it should not be the same public function with a different return type.
>
> In other words: your description fixes the conceptual confusion. The code should now be adjusted so the API reflects that concept without making callers infer which stage they are invoking from optional keyword arguments.


### Medium: artifact writing is duck-typed around result shape

Location:

- `src/jet_simplex_search/artifacts.py:35`
- `src/jet_simplex_search/artifacts.py:120`
- `src/jet_simplex_search/artifacts.py:167`
- `src/jet_simplex_search/artifacts.py:260`

`write_search_artifact` accepts `result: object`, then branches on `_is_combined_result`. That is a smell in a package whose core promise is precise mathematical evidence. The artifact writer is part of the evidence path; it should be strongly coupled to declared result records, not to whatever object happens to have certain attributes.

Why this matters:

The code is currently paying an abstraction cost without gaining flexibility. The writer has to know all result shapes anyway, but the type boundary does not say so. That makes refactors riskier and hides schema drift until runtime.

Fix:

- Define explicit result classes in `records.py` or a new `results.py`.
- Type `write_search_artifact` as accepting `SimplexSearchResult | SearchWithHLiftsResult`.
- Use `isinstance` or a discriminant field instead of duck typing.
- Split payload construction into direct functions for each result shape.

#### PO Response
> I approve.

### Medium: release-facing surfaces still point at local or stale paths

Location:

- `pyproject.toml:25`
- `README.md:82`
- `README.md:96`
- `README.md:254`

`pyproject.toml` still declares:

```toml
state-collapser = { path = "../state_collapser", editable = true }
```

The README still documents a sibling-checkout local dependency flow. That may be fine for internal development, but it is not a public release dependency story. The README also links `docs/release/engineering_continuity_report.md`, while the continuity report currently lives under `docs/engineer_continuity/...`.

Why this matters:

Broken links and local path dependencies make the package look unfinished even if the core code is solid. The user already chose "library pre-release" as the framing, so the dependency story can still be honest, but it cannot be stale.

Fix:

- Before release, depend on the actual `state_collapser` GitHub release/tag.
- Keep local path instructions in contributor/developer docs, not the main installation path.
- Per the previously approved README policy, remove the root README continuity-report link rather than fixing it into another internal document.

#### PO Response
> I approve. 

### Medium: the h-to-g skeleton code is good, but the label policy is currently one hard failure mode

Location:

- `src/jet_simplex_search/skeleton.py:14`
- `src/jet_simplex_search/skeleton.py:145`
- `src/jet_simplex_search/skeleton.py:153`
- `src/jet_simplex_search/skeleton.py:177`

The current `SkeletonLabelPolicy` only supports `REQUIRE_IDENTICAL`. That is a defensible release-0 policy, and the implementation is direct. But the enum gives the appearance of a policy surface while only one policy exists.

Why this matters:

This is not a correctness bug. It is an abstraction-pressure warning. If the package is going to support only exact label equality, a boolean or direct function is simpler. If it is going to support label projection policies, the policy contract needs to be spelled out and tested.

Fix:

- Either keep the enum and add a short design comment/test that this is deliberately the only v0.1 policy, or collapse it to direct behavior until a second policy exists.
- Do not let this become a pretend extension point.

#### PO Response
> Do my replies above already fix this?

#### Codex Answer
> Mostly, yes.
>
> Your replies clarify that the package is not trying to offer an open-ended family of label semantics at release time. The intended pipeline is:
>
> ```text
> H has whatever multiplicities and labels it has
>   -> G is the clean skeleton/realization used for tower search
>   -> H-lift accounting remembers the multiplicity and edge-fiber data
> ```
>
> Under that story, requiring identical labels when collapsing multiple H edges into one G edge is a reasonable v0.1 policy. It means: if two parallel H edges are to be represented by one skeleton edge, they must agree on the edge label, because otherwise the skeleton edge would be lying about what it represents.
>
> So the original complaint gets downgraded. It is not a mathematical flaw. It is just an API-design warning:
>
> - If exact label agreement is the only supported release behavior, the code should say that plainly.
> - If future releases may support label projection, label aggregation, unlabeled realization, or user-defined compatibility, then keeping `SkeletonLabelPolicy` is fine, but it should be documented as a deliberately tiny first policy surface.
>
> Your earlier replies do not by themselves change the code, but they do settle the intended meaning. The implementation move can be small: keep `REQUIRE_IDENTICAL`, add a clear docstring/test saying this is the v0.1 skeleton label policy, and avoid pretending there are other policies until we actually implement them.

### Low-medium: dead or nearly dead helpers survived the refactor

Location:

- `src/jet_simplex_search/ids.py:46`
- `src/jet_simplex_search/tower_adapter.py:98`
- `src/jet_simplex_search/tower_adapter.py:195`
- `src/jet_simplex_search/tower_adapter.py:341`
- `src/jet_simplex_search/artifacts.py:32`

Examples:

- `fiber_id` appears to be tested but unused in product code.
- `_simple_edge_action_ids_cache` is assigned but not read.
- `_edge_id_to_action_cell` appears unused after the endpoint-pair tier-edge rewrite.
- `max_expanded_h_lift_witnesses` exists in config, but expanded witnesses intentionally raise `NotImplementedError`.

Why this matters:

Dead helpers are where stale mental models hide. This package is small enough that it does not need museum pieces in the source tree.

Fix:

- Delete unused helpers and their tests if they are not part of the release contract.
- Keep only the artifact ids and caches that are actually used.
- If an id helper is intended for a later artifact schema, mention that in the relevant design document instead of leaving it live in product code.

#### PO Response
> Approved.

### Low: tracked backup/temp image files should not ship

Location:

- `assets/images/.$degens_dark.svg.bkp`
- `assets/images/.$degens_light.svg.bkp`
- `assets/images/.$how_dark.svg.bkp`
- `assets/images/.$logo_dark.svg.bkp`
- `assets/images/.$logo_light.svg.bkp`
- `assets/images/.$logo_light.svg.dtmp`

These files are currently tracked. They are not part of the package behavior, but they make the repository look less professional.

Fix:

- Delete tracked backup/temp image files.
- Add a narrow ignore rule for the editor/export artifacts that created them.

#### PO Response
> Approved.

## Abstractions that should justify themselves or die

| abstraction | users | cost | benefit | recommendation |
| --- | ---: | --- | --- | --- |
| `SimplexRecord` | central | many fields | makes invariants visible | keep |
| `SkeletonizationResult` | central | moderate | records H-to-G fibers and diagnostics | keep |
| `HLiftRecord` / `HLiftSearchResult` | artifact and API | moderate | makes expanded H-lift accounting explicit | keep |
| `StaticTowerAdapterProtocol` | search/lift boundary | moderate | isolates `state_collapser` | keep |
| `SearchWithHLiftsResult` in `api.py` | public graph path | hidden type location | correct concept, wrong module | move to records/results |
| `search_simplices` optional graph-or-adapter shape | public API | ambiguous return type | convenience | split into clear APIs |
| artifact duck typing | artifact writer | runtime schema ambiguity | avoids import/type dependency | replace with explicit union/result protocol |
| `SkeletonLabelPolicy` with one value | skeletonization | pretend extension point | names current rule | either document as v0.1-only or simplify |
| `StaticSearchContext` | thin wrapper | extra object hop | little | inline or make it carry real config |
| `fiber_id` | tests only | stale concept | none today | delete or make artifact-visible |
| `_edge_id_to_action_cell` | appears unused | stale cache path | none today | delete |

## RL correctness traps

This is not an RL project. The equivalent correctness traps are:

- emitting a simplex whose edge witnesses do not project to the claimed downstairs faces;
- building a tower using multiplicity or loops after the simple-reflexive realization is supposed to have removed them;
- generating upstairs interiors over downstairs boundaries with no corresponding downstairs simplex;
- counting expanded H-lifts by endpoint address while losing the actual H edge witnesses;
- treating degenerate simplices as collapsed lower-dimensional addresses;
- letting artifact output diverge from the in-memory records.

The current code handles several of these well:

- `lift_downstairs_extension` searches only over the last edge fiber of an existing downstairs simplex.
- `lift_tier_simplices` iterates over existing downstairs simplex records, so it does not invent upstairs higher-dimensional simplices over missing downstairs records.
- `compute_h_lifts_for_tier_zero` multiplies face factors, including zero factors for missing H loops.
- The tests include direct checks for no upstairs triangle over a missing downstairs triangle.

The remaining trap is tower-construction semantics. The adapter can expose a clean view while the tower underneath may have been built by a different rule. That is the one to kill before claiming the release algorithm is fully realized.

## Performance and feedback loop

The local feedback loop is excellent:

```text
uv run pytest
90 passed in 0.10s
```

The previous edge-fiber complaint has mostly been addressed. `edge_fiber_targets` now uses an indexed structure instead of scanning all tier edges on every query:

- `src/jet_simplex_search/tower_adapter.py:244`
- `src/jet_simplex_search/tower_adapter.py:297`

The hot path now has the right shape:

```text
known downstairs (m+1)-simplex tau
  -> known upstairs m-simplex over partial tau
  -> indexed last-edge fiber lookup
  -> intersect with cached upstairs frontier
  -> emit upstairs simplex over tau
```

That is the important speed-up. The search is addressed by the downstairs simplex. The downstairs simplex is not an after-the-fact validation.

What is still missing:

- A small benchmark script or test fixture for sparse paths, sparse DAGs, and a quotient tower case.
- Counters for fiber queries, edge-fiber index hits, emitted candidates, rejected candidates, and wall time.
- A regression fixture where adapter-side endpoint simplification and upstream tower construction would diverge if multiplicity influenced the next tier.

## Tests that actually matter

Already covered well:

- Direct simplex counts in low dimensions.
- Degenerate simplex handling.
- No upstairs simplex over a missing downstairs simplex.
- H-loop missing factor gives zero expanded H-lifts.
- H multiedge factors multiply expanded lift counts.
- Basic artifact output.

Add these before public release:

- A two-or-more-step tower fixture where parallel quotient edges would affect the next tier unless simple-reflexive realization is applied before the next contraction step.
- Public API shape tests proving `search_simplices` returns one stable type for graph input and rejects ambiguous graph-plus-adapter calls after the API split.
- Artifact schema tests for combined H-to-G results, not just file existence/table fragments.
- Witness consistency tests: every emitted simplex face edge projects to the corresponding downstairs face edge.
- README quick-start test using the documented install/import path.
- A release metadata test or CI job that fails if `pyproject.toml` uses a local path dependency on release branches.

## What I would delete first

- `assets/images/.$*.bkp` and `assets/images/.$*.dtmp`.
- `src/jet_simplex_search/tower_adapter.py:341` `_edge_id_to_action_cell`, if no hidden caller exists.
- `src/jet_simplex_search/tower_adapter.py:98` `_simple_edge_action_ids_cache`, if no next patch needs it.
- `src/jet_simplex_search/ids.py:46` `fiber_id`, unless it becomes visible in artifact schemas.
- `SearchArtifactConfig.max_expanded_h_lift_witnesses`, until expanded witnesses are implemented.
- `StaticSearchContext`, unless it is about to carry real runtime configuration.

## What I would rewrite first

Rewrite the public result/API boundary.

Target shape:

```text
search_simplices(graph=H, k=k, ...)
  -> SearchWithHLiftsResult

search_skeleton_simplices(adapter=A, k=k, ...)
  -> SimplexSearchResult
```

Then update artifacts to accept explicit result classes instead of `object`. This is not cosmetic. It removes ambiguity from the public API, lets the artifact writer become ordinary typed code, and makes the release documentation easier to keep honest.

After that, rewrite the `state_collapser` adapter integration so simple-reflexive quotient realization happens during tower construction, not merely at adapter readout.

## Final standard

Before treating this as a public pre-release, the package should satisfy this standard:

Every emitted simplex record has truthful witnesses; every lift is searched only over an existing downstairs simplex fiber; every expanded H-lift count is traceable to vertex and edge fiber factors; and every quotient tier is constructed from the same simple-reflexive graph semantics that the simplex search assumes.

The current code is close enough that these are tractable fixes. It does not need a grand architecture. It needs the remaining invariants moved to the right boundary, stale convenience removed, and release surfaces made as precise as the math.
