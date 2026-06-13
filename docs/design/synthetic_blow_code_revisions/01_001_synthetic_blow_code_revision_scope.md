# Synthetic Blow Review Code Revision Scope

## Status

This folder carries out the code revisions approved from:

```text
code_review/01_002_synthetic_blow_project_review.md
```

This document is a design index and revision scope. It is not an implementation
patch and not yet a Phase.Stage.Action workplan.

## Source Review

The approved review identified the following revision targets:

1. Move simple-reflexive quotient realization to the correct tower-construction
   boundary.
2. Clarify the public API so the H-input workflow and skeleton/tower workflow do
   not share one ambiguous function shape.
3. Replace artifact duck typing with explicit result records.
4. Fix release-facing dependency and documentation drift.
5. Document the v0.1 skeleton label policy plainly.
6. Delete dead or nearly dead refactor leftovers.
7. Remove tracked backup/temp image files.
8. Add tests that prove witness truth, clean tower semantics, API shape, and
   artifact schema behavior.

## Attribution

The static quotient-tower simplex search algorithm is PM Abdul Malik's work and
part of his thesis. This includes:

- degree-wise simplex enumeration;
- cached frontier recurrence;
- formal identity handling for degenerate skeleton addresses;
- static quotient tower construction;
- small-object fiber-addressed lift search over existing downstairs simplices.

The Project Owner clarified the H-to-G pipeline used by this package:

```text
study H
  -> clean / skeletonize to G
  -> build the clean tower G^bullet
  -> search simplices in G^bullet
  -> perform multiplicity / etale H-lift accounting
```

The Project Owner also clarified that tower tiers must be clean before they are
used to build the next quotient tier. That means cleaning a tier only at adapter
readout is not sufficient as the final architecture.

## Revision Streams

### Stream 1: Clean Tower Construction Boundary

Goal:

Ensure every tier used to construct a next quotient tier is the clean
simple-reflexive realization required by `jet_simplex_search`.

Open architecture choice:

- Put a simple-reflexive quotient-realization mode inside `state_collapser`; or
- make `jet_simplex_search` orchestrate the tower one quotient step at a time,
  cleaning each raw quotient before feeding it to the next step.

Design constraints:

- The final tower must be static, not dynamically rebuilt during simplex search.
- The contraction schema must be expressed against the clean current tier.
- Projection data must survive each clean realization step.
- Tests must include a multi-step case where adapter-side simplification would
  hide a tower-construction error.

### Stream 2: Public API And Result Boundary

Goal:

Make the public function names match the mathematical pipeline.

Target shape:

```text
search_simplices(graph=H, k=k, ...)
  -> SearchWithHLiftsResult

search_skeleton_simplices(adapter=A, k=k, ...)
  -> SimplexSearchResult
```

Design constraints:

- `search_simplices` should mean the H-input package workflow.
- Adapter-based search should remain available for tests, smoke scripts, and
  advanced callers.
- Passing both graph and adapter must be rejected.
- Result dataclasses should live in a records/results module, not hidden in
  `api.py`.

### Stream 3: Artifact Writer Type Discipline

Goal:

Replace object/duck-typed artifact writing with explicit result handling.

Target shape:

```text
write_search_artifact(result: SimplexSearchResult | SearchWithHLiftsResult, ...)
```

Design constraints:

- Artifact output is part of the mathematical evidence path.
- Payload builders should branch on declared result classes, not attribute
  shape.
- Existing artifact behavior should be preserved unless a test proves the old
  behavior was wrong.
- Combined H-to-G artifacts must expose skeleton search and H-lift diagnostics
  clearly.

### Stream 4: Release-Facing Dependency And Documentation Drift

Goal:

Remove stale public-release surfaces.

Approved revisions:

- Replace the local `state_collapser` path dependency before release with the
  actual GitHub release/tag dependency.
- Keep local sibling-checkout instructions out of the primary README install
  path.
- Remove the root README continuity-report link instead of linking to internal
  continuity docs.

Design constraints:

- Internal Prime Directive and continuity documents stay in the repo.
- Internal documents are not linked from root public documentation unless the
  Project Owner explicitly asks for that.

### Stream 5: Skeleton Label Policy Documentation

Goal:

Make the v0.1 label policy explicit without pretending a broader policy family
exists.

Approved interpretation:

If parallel H edges are represented by one skeleton G edge, their labels must
agree. Otherwise the G edge would misrepresent its H fiber.

Design constraints:

- Keep `REQUIRE_IDENTICAL` if it is treated as a deliberately small v0.1 policy.
- Add docstrings and tests that state the current behavior.
- Do not add new label aggregation/projecting behavior in this revision.

### Stream 6: Dead Code And Stale Cache Cleanup

Goal:

Remove code that survived earlier refactors but no longer carries release
behavior.

Initial cleanup candidates:

- `fiber_id`, unless promoted into a real artifact/schema id.
- `_simple_edge_action_ids_cache`, if still assigned but unread.
- `_edge_id_to_action_cell`, if still unused.
- `SearchArtifactConfig.max_expanded_h_lift_witnesses`, until expanded
  witnesses exist.
- `StaticSearchContext`, unless it becomes real runtime configuration.

Design constraints:

- Delete tests that only preserve deleted dead code.
- Do not remove externally useful API without checking README, smoke scripts,
  and tests.

### Stream 7: Repository Hygiene

Goal:

Remove tracked backup/temp artifacts that should not ship.

Initial files:

```text
assets/images/.$degens_dark.svg.bkp
assets/images/.$degens_light.svg.bkp
assets/images/.$how_dark.svg.bkp
assets/images/.$logo_dark.svg.bkp
assets/images/.$logo_light.svg.bkp
assets/images/.$logo_light.svg.dtmp
```

Design constraints:

- Do not remove the real logo files.
- Add a narrow ignore rule for this artifact pattern if needed.

### Stream 8: Regression And Release Tests

Goal:

Prove the new boundaries stay correct.

Required tests:

- Multi-step clean tower construction semantics.
- Public API shape and ambiguous-call rejection.
- Explicit artifact result handling.
- Witness consistency for emitted simplex faces.
- README quick-start import/example behavior.
- Release metadata guard against local path dependencies.

## Proposed Document Sequence

Use this folder for the revision series:

```text
docs/design/synthetic_blow_code_revisions/
  01_001_synthetic_blow_code_revision_scope.md
  01_002_synthetic_blow_code_revision_blueprint.md
  01_003_synthetic_blow_code_revision_implementation_workplan.md
  01_004_synthetic_blow_code_revision_implementation_log.md
```

## Next Step

The next document should be an extremely detailed package blueprint. It should
inspect both the present `jet_simplex_search` codebase and the adjacent
`state_collapser` source before deciding whether Stream 1 is best owned by
`state_collapser`, by `jet_simplex_search` one-step orchestration, or by a
short-term bridge plus a state-collapser follow-up.
