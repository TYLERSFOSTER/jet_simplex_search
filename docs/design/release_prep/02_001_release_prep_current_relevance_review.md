# Release Prep Current Relevance Review

## Status

Second-pass review of `docs/design/release_prep` after the package changed
substantially during the 2026-06-13 work session.

This document answers two questions:

1. Is the original release-prep plan still relevant?
2. What must be added or corrected before executing release prep?

Verdict:

The original release-prep plan is still relevant as the broad release gate. It
should not be executed literally without this addendum. Several items are now
completed, several are stale, and several new release gates are needed because
the repo now has H-to-G skeletonization, H-lift accounting, Malik lineage
documentation, and an explicit `HGraphML` boundary.

## Current Review Inputs

Reviewed local repo state on 2026-06-13.

Primary files checked:

- `docs/design/release_prep/01_001_public_release_preparation_plan.md`
- `docs/design/release_prep/01_002_public_release_preparation_implementation_workplan.md`
- `README.md`
- `pyproject.toml`
- `src/jet_simplex_search/`
- `tests/`
- `smoke/`
- `docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md`
- `docs/engineer_continuity/2026/06/13/01_001_engineering_continuity_report.md`

Commands run during this review:

```bash
uv run pytest
```

Result:

```text
111 passed
```

```bash
uv run ruff check .
```

Result:

```text
All checks passed.
```

```bash
uv build --out-dir [temporary build directory]
```

Result:

```text
Successfully built jet_simplex_search-0.1.0.tar.gz
Successfully built jet_simplex_search-0.1.0-py3-none-any.whl
```

The build initially hit a local sandbox permission issue in the shared `uv`
cache, then succeeded when run with the necessary cache access. That should be
treated as local execution friction, not as a package build failure.

## High-Level Answer

The release-prep folder remains useful and should stay in the repo.

The original plan is still correct about the main release shape:

- `v0.1.0`;
- GitHub-only library pre-release;
- no PyPI claim;
- no production-readiness claim;
- no benchmark-superiority claim;
- `state_collapser` dependency via GitHub release tag;
- smoke examples as both examples and regression material;
- CI, release hygiene, release notes, and public support docs before release.

The original plan is stale in these ways:

- it describes the local editable `state_collapser` dependency as the active
  blocker, but `pyproject.toml` now uses the GitHub `v0.7.2` direct dependency;
- it lists older verification output, while the current test suite has 111
  tests passing;
- it expects a fuller Ruff/docstring gate than is currently configured;
- it expects package metadata fields that are not currently present;
- it predates the H-to-G skeletonization and H-lift release surface;
- it predates the Malik lineage document and README link;
- it predates the `HGraphML` clarification for the message-passing branch;
- it does not account for historical design logs containing temporary local
  paths inside command transcripts.

The release-prep workplan should therefore be updated before execution, or
executed with this addendum open as the controlling correction sheet.

## Current State Snapshot

### Implemented And Verified

The repo now has:

- graph input records;
- H-to-G skeletonization;
- loop and parallel-edge accounting;
- formal identity edges for skeleton degeneracy;
- directed flag simplex enumeration through `k`;
- first-class degenerate simplex records;
- cached frontier recurrence;
- clean static tower construction;
- real `state_collapser` integration;
- source-sensitive edge-fiber lifting;
- missing-downstairs-interior regression coverage;
- witness consistency regression coverage;
- compressed H-lift counts;
- diagnostics;
- JSON/JSONL artifacts;
- README quick-start regression test;
- release metadata tests;
- 111 passing tests;
- Ruff present and passing for the current configured rules;
- successful sdist and wheel build.

### Still Missing

The repo does not yet have:

- `.github/workflows/test.yml`;
- issue templates;
- pull request template;
- `scripts/release_hygiene.py`;
- `tests/test_release_hygiene.py`;
- `RELEASE_NOTES.md`;
- `SECURITY.md`;
- `CONTRIBUTING.md`;
- smoke snapshot tests;
- smoke Markdown coverage tests;
- Ruff format check in CI;
- docstring-quality enforcement;
- clean installed-wheel verification;
- final release asset or release-tag approval.

## Workstream Relevance Review

### Workstream 1 - Release Scope And Versioning

Still relevant.

Keep:

- release label `v0.1.0`;
- package metadata version `0.1.0`;
- GitHub-only public pre-release;
- library pre-release framing.

Add:

- release notes should state that `jet_simplex_search` is the simplex-search and
  quotient-lift package, while `HGraphML` is the separate beginning of the
  quotient-tower-backed message-passing branch.

### Workstream 2 - Dependency Strategy

Mostly completed.

Current `pyproject.toml` uses:

```toml
"state-collapser @ git+https://github.com/TYLERSFOSTER/state_collapser.git@v0.7.2"
```

Keep the release gate that forbids `../state_collapser`.

Add:

- verify clean `uv sync` from a fresh clone;
- verify the lockfile actually resolves `state-collapser` from the GitHub tag;
- keep `allow-direct-references = true` documented as intentional for the
  GitHub-only pre-release.

### Workstream 3 - Package Metadata

Still relevant, partially stale.

Current metadata has:

- version `0.1.0`;
- license file;
- Python `>=3.11,<3.13`;
- development status alpha;
- science/research audience;
- Python classifiers;
- mathematics topic classifier;
- Homepage, Repository, Issues URLs;
- direct Git dependency.

Still missing relative to the original plan:

- `keywords`;
- `Source` project URL;
- `Typing :: Typed` classifier;
- `src/jet_simplex_search/py.typed`.

Correction:

Do not blindly add `Typing :: Typed`. The 2026-06-13 continuity report records
that the classifier was not kept because the package does not yet ship a
`py.typed` marker. The release-prep plan should now treat typing as a decision:

```text
Either add py.typed and the Typing :: Typed classifier together,
or keep both deferred for v0.1.0.
```

Recommended addition:

- add package keywords;
- add `Source` URL if desired;
- decide explicitly on typed-package status.

### Workstream 4 - CI And Badges

Still relevant, not complete.

Current state:

- README has a Ruff badge;
- Ruff is present and `uv run ruff check .` passes;
- no CI workflow exists;
- no CI badge exists;
- no coverage badge exists;
- no PyPI badge exists.

Corrections:

- the current Ruff configuration is light: `E4`, `E7`, `E9`, and `F`;
- docstring-quality rules are not configured;
- `ruff format --check` has not been made a release gate yet.

Add:

- decide whether to expand Ruff rules before `v0.1.0` or keep the v0.1 gate
  intentionally light;
- if keeping it light, update the release plan so it does not promise a
  docstring-quality gate that does not exist;
- add CI only when it can run the same dependency strategy as local release
  checks.

### Workstream 5 - Test And Smoke Verification

Still relevant, partially complete.

Current state:

- 111 pytest tests pass;
- README quick-start regression exists;
- missing-downstairs-interior behavior is tested;
- witness consistency is tested;
- smoke scripts exist through `smoke_016.py`;
- smoke Markdown exists for `smoke_003.md` through `smoke_016.md`.

Still missing:

- pytest smoke snapshot test;
- smoke Markdown coverage test;
- decision about whether `smoke_001.py` and `smoke_002.py` need matching
  Markdown count arguments or are excluded as early/manual examples.

Add:

- smoke snapshot tests should run all public smoke scripts;
- smoke doc coverage should either require all smoke `.py` files to have
  matching `.md` files or explicitly exclude the utility/early smoke scripts;
- release notes should identify smoke scripts as examples, not as a full
  benchmark suite.

### Workstream 6 - Documentation

Still relevant, needs additions.

Current state:

- README has Known Limitations;
- README links to the Malik lineage document;
- README does not link release-prep;
- README does not link `docs/prime_directive`;
- Malik attribution exists in README;
- the larger Malik lineage document now also clarifies `HGraphML`.

Add:

- release-prep should require the Malik lineage link to stay valid;
- release-prep should require public attribution to use a consistent name:
  `Abdullah N. Malik` or `Abdullah Naeem Malik`;
- release-prep should preserve the distinction between:
  - this repo: simplex search and quotient lifting;
  - `HGraphML`: beginning of quotient-tower-backed graph message passing;
- release-prep should prevent public docs from implying that this package
  implements CinchNET, PTVNN, Kan replacement, or neural message passing.

Small README polish discovered during review:

- an image-caption typo was corrected during this review.

### Workstream 7 - Release Hygiene

Still relevant, urgently needed.

Current state:

- no `scripts/release_hygiene.py`;
- no hygiene tests.

New complication:

Historical design logs and release-prep workplans intentionally contain
temporary build paths such as `[temporary build directory]` examples or local
temporary command output. A naive scan of every Markdown file under `docs/`
will either fail on legitimate historical command transcripts or force us to
rewrite useful engineering history.

Add:

- define public hygiene scan scope explicitly;
- scan README, release notes, package metadata, root public docs, and selected
  public-facing design docs strictly;
- allow or warn on local paths inside historical implementation logs;
- fail on machine-local paths in README, release notes, package metadata,
  artifacts, and high-level public provenance docs;
- require the Malik lineage document to avoid local filesystem paths.

This review already corrected the Malik lineage thesis citation to remove the
local thesis PDF path.

### Workstream 8 - Artifact And Example Policy

Still relevant.

Current state:

- no generated artifact directory appears at repo root;
- artifact output support is implemented;
- README documents generated artifact filenames;
- smoke scripts are source examples.

Add:

- release hygiene should reject generated artifact output directories unless
  explicitly allowlisted;
- release notes should say artifact outputs are generated by users, not bundled
  as release artifacts in `v0.1.0`.

### Workstream 9 - Security, License, And Public Safety

Still relevant, not complete.

Current state:

- MIT license exists;
- no `SECURITY.md`;
- no `CONTRIBUTING.md`;
- no `CODE_OF_CONDUCT.md`, which matches the original decision for v0.1.0.

Add:

- keep `SECURITY.md` and `CONTRIBUTING.md` as release blockers if external
  users are expected;
- release hygiene should check for local machine paths, secrets, and accidental
  credentials in public surfaces.

### Workstream 10 - Build And Install Verification

Still relevant, partially complete.

Current state:

- `uv build` succeeded in this review;
- clean installed-wheel verification has not been performed in this review;
- README quick-start test passes in the source checkout, not yet from an
  installed wheel.

Add:

- clean temporary environment install from the built wheel remains a final
  release gate;
- installed-wheel quick-start remains a final release gate;
- sdist contents should be inspected to make sure docs and smoke source files
  are included as intended;
- wheel contents should be inspected to make sure smoke files are excluded
  unless approved.

### Workstream 11 - GitHub Repository Preparation

Still relevant, not complete.

Current state:

- no `.github` directory was found during this review;
- no issue templates;
- no PR template;
- no workflow.

Add:

- GitHub templates and CI should remain release blockers before a public
  repository announcement.

### Workstream 12 - Release Notes

Still relevant, not complete.

Current state:

- no `RELEASE_NOTES.md`.

Add to release notes:

- H-to-G skeletonization;
- H-lift counts;
- missing-downstairs-interior behavior;
- witness consistency;
- Malik lineage document;
- `HGraphML` boundary;
- no Kan replacement;
- no neural message passing in this repo;
- no benchmark-validated speed-up claim.

### Workstream 13 - Final Release Gate

Still relevant, needs additions.

Add these final-gate checks:

- Malik lineage document link from README resolves;
- Malik lineage document contains no machine-local thesis path;
- public docs preserve Malik attribution;
- public docs do not claim this repo implements HGraphML, CinchNET, PTVNN, or
  neural message passing;
- final release notes mention `HGraphML` only as a separate related
  message-passing package;
- final release notes mention direct Git dependency on `state_collapser`
  `v0.7.2`;
- final release notes avoid benchmark superiority.

## New Workstream 14 - Malik Lineage And Cross-Repo Framing

This workstream did not exist when the original release-prep plan was written.
It is now necessary because the repo has a substantial provenance document and
root README link.

### Required Release Position

Public framing should say:

```text
jet_simplex_search implements the bounded simplex-search and quotient-lift
branch of Malik's simplicial graph-search program.
```

It should also say:

```text
HGraphML is the separate beginning of the quotient-tower-backed graph
message-passing branch.
```

It should not say:

```text
jet_simplex_search implements CinchNET.
jet_simplex_search implements PTVNN.
jet_simplex_search implements neural simplicial message passing.
HGraphML is already full CinchNET.
```

### Tasks

- Keep the README Malik Research Lineage section.
- Keep the README link to the Malik lineage document.
- Check that the Malik lineage document has no private local paths.
- Check that public docs consistently distinguish this package from HGraphML.
- Add a release-notes paragraph explaining the relationship without overclaim.
- Consider adding a short `Related Work` or `Lineage` section to
  `RELEASE_NOTES.md`.

### Completion Criteria

- Public users can tell which repo does simplex search.
- Public users can tell which repo begins message passing.
- Malik attribution is clear and preserved.
- No public doc implies this package implements all of Malik's thesis.

## New Workstream 15 - Historical Design Docs Hygiene Scope

This workstream is needed because design docs and continuity reports contain
historical command outputs, temporary build directories, and implementation-log
paths.

### Problem

The original release hygiene plan says to fail on machine-local absolute paths
in public Markdown and JSON surfaces. That remains correct. But the repo also
contains engineering logs whose purpose is to preserve what happened during
local work. Those logs may include temporary build paths.

### Required Decision

Before writing `scripts/release_hygiene.py`, decide one of these policies:

Option A:

- historical design logs are public;
- sanitize every local path in those logs before release.

Option B:

- historical design logs remain in repo but are not treated as public
  release-facing docs;
- hygiene script warns on local paths in logs but fails on root docs, release
  notes, README, package metadata, and high-level design/provenance docs.

Recommended for `v0.1.0`:

Option B.

### Completion Criteria

- Release hygiene has a documented scan scope.
- Historical logs do not accidentally block release.
- Release-facing docs remain clean of machine-local paths.

## New Workstream 16 - Current Correctness Claims

The release-prep plan should now protect the correctness claims introduced by
recent refactors.

### Claims Worth Protecting

- Search is fiber-addressed over existing downstairs simplex records.
- Missing downstairs interiors do not trigger upstairs interior search in the
  current small-object mode.
- Degenerate downstairs simplices may have nondegenerate upstairs lifts.
- Edge witnesses must project consistently.
- H-to-G skeletonization preserves loop and parallel-edge information through
  fibers and H-lift counts.

### Required Tests

These are already present and should remain release blockers:

- `tests/test_fiber_lift.py`
- `tests/test_witness_consistency.py`
- `tests/test_h_lift.py`
- `tests/test_skeleton.py`
- `tests/integration/test_clean_state_collapser_tower.py`
- `tests/test_readme_quickstart.py`

### Completion Criteria

- Future release edits do not remove these tests.
- Release notes phrase these as implemented behavior, not as theoretical
  intent.

## Recommended Immediate Edits

Before executing the release-prep implementation workplan, make these edits:

1. Add an update note to the old release-prep plan and workplan pointing to
   this review.
2. Update the workplan's source inputs to include:
   - the 2026-06-13 continuity report;
   - the Malik lineage document;
   - this current relevance review.
3. Update package-metadata tasks:
   - mark `state_collapser` local path replacement as completed;
   - add missing keywords or explicitly defer them;
   - decide on `py.typed` before adding `Typing :: Typed`.
4. Update docs tasks:
   - preserve the Malik lineage README link;
   - preserve the HGraphML boundary;
   - keep README public prose polished.
5. Update release-hygiene tasks:
   - define scan scope;
   - fail on local paths in public surfaces;
   - warn or allowlist historical logs.
6. Add final-gate checks for:
   - Malik attribution;
   - HGraphML boundary;
   - no neural-message-passing overclaim;
   - no Kan overclaim;
   - no benchmark overclaim.

## Bottom Line

The old release-prep docs are not obsolete. They are still the correct skeleton
for public release preparation.

But the repo has advanced enough that the release-prep folder needs this
addendum. The release plan should now be read as:

```text
01_001 gives the broad release plan.
01_002 gives the original implementation workplan.
02_001 gives the current correction sheet and added workstreams.
02_002 gives the updated complete implementation workplan.
```

Do not execute `01_002` mechanically. Use `02_002` for future `v0.1.0`
release-prep execution.
