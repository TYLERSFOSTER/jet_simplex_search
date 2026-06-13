# Updated Public Release Preparation Implementation Workplan

## Status

Canonical updated implementation workplan for preparing `jet_simplex_search`
for the approved `v0.1.0` GitHub-only library pre-release.

This document supersedes the execution details in:

```text
docs/design/release_prep/01_002_public_release_preparation_implementation_workplan.md
```

It preserves the still-relevant release work from the original workplan and
folds in the current-state corrections from:

```text
docs/design/release_prep/02_001_release_prep_current_relevance_review.md
```

This workplan is not permission to tag, publish, upload release assets, make the
repository public, publish to PyPI, rewrite git history, or edit
`state_collapser`.

## Source Documents

Read these before executing:

- `docs/design/release_prep/01_001_public_release_preparation_plan.md`
- `docs/design/release_prep/02_001_release_prep_current_relevance_review.md`
- `docs/prime_directive/public_release_readiness_protocol.md`
- `docs/engineer_continuity/2026/06/13/01_001_engineering_continuity_report.md`
- `docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md`
- `README.md`
- `pyproject.toml`

## Approved Release Decisions

- Release label: `v0.1.0`.
- Package metadata version: `0.1.0`.
- Release channel: GitHub-only public pre-release.
- Release framing: library pre-release.
- No PyPI claim for `v0.1.0`.
- Smoke scripts: both public examples and regression checks.
- `state_collapser` dependency: GitHub release tag `v0.7.2`.
- Package status classifier: `Development Status :: 3 - Alpha`.
- CI: GitHub Actions with Python `3.11` and `3.12`.
- Tooling: Ruff lint, Ruff format check, and an explicitly decided docstring
  posture.
- Documentation:
  - keep concise README Known Limitations;
  - keep Malik lineage section and link;
  - do not link release-prep docs from README;
  - do not link engineering continuity reports from README;
  - keep `docs/prime_directive` in repo but do not link it from root docs.
- Attribution: preserve Abdullah N. Malik attribution.
- Cross-repo framing:
  - this repo is the bounded simplex-search and quotient-lift package;
  - `HGraphML` is the separate beginning of the quotient-tower-backed graph
    message-passing branch.
- Release hygiene: add `scripts/release_hygiene.py` and tests.
- Artifact policy:
  - keep smoke source examples and count arguments;
  - do not commit generated artifact output directories for `v0.1.0`.
- Security/license:
  - keep MIT license;
  - add `SECURITY.md`;
  - add lightweight `CONTRIBUTING.md`;
  - skip `CODE_OF_CONDUCT.md` for `v0.1.0`.
- GitHub prep:
  - add CI workflow;
  - add issue templates;
  - add PR template;
  - no GitHub Pages for `v0.1.0`.
- Release notes: add `RELEASE_NOTES.md`.

## Current Baseline At Workplan Creation

The current relevance review recorded:

```text
uv run pytest
111 passed
```

```text
uv run ruff check .
All checks passed.
```

```text
uv build --out-dir [temporary build directory]
Successfully built jet_simplex_search-0.1.0.tar.gz
Successfully built jet_simplex_search-0.1.0-py3-none-any.whl
```

Treat those as a baseline snapshot, not as future proof. Re-run the checks
during execution.

## Hard Stop Conditions

Stop and ask the Project Owner before any of the following:

- tagging `v0.1.0`;
- uploading release assets;
- publishing to PyPI;
- making the repository public;
- publishing anywhere else;
- rewriting git history;
- deleting or moving raw artifacts without a verified manifest and bundle;
- editing `state_collapser` directly;
- changing Abdullah N. Malik attribution;
- removing the Malik lineage document or README link;
- weakening the `HGraphML` boundary into an overclaim;
- claiming production readiness;
- claiming benchmark superiority or statistically validated speedups;
- claiming Kan replacement is implemented;
- claiming neural message passing is implemented in this repo;
- replacing the approved `state_collapser` `v0.7.2` dependency decision.

## Execution Principles

- Execute phases in order unless the Project Owner explicitly changes order.
- Preserve unrelated user changes.
- If a step is already complete, verify it and record it rather than duplicating
  it.
- Use a dedicated release-prep branch before implementation.
- Use repo-local tools and tests as reality checks.
- Treat `state_collapser` as the owner of quotient-tower semantics.
- Treat `jet_simplex_search` as owner of simplex enumeration, lifting,
  witnesses, H-to-G skeletonization, H-lift accounting, and artifacts.
- Keep public claims bounded to implemented and verified behavior.
- Prefer failing release gates over silently weakening standards.
- Do not sanitize historical design history by deleting useful records; instead
  define a release hygiene scan scope that distinguishes public-facing docs from
  historical logs.

---

# Phase 0 - Authority, Baseline, Branch, And Execution Log

## Stage 0.1 - Confirm Execution Authority

### Action 0.1.1 - Verify Explicit Execution Approval

Target files:

```text
none
```

Procedure:

- Confirm the Project Owner has explicitly requested execution of this updated
  workplan.
- If the Project Owner has only requested the workplan, stop after creating or
  updating this document.
- Record the exact approval phrase in the implementation log created in
  Action 0.4.1.

Completion criteria:

- Execution approval exists before release implementation edits begin.

Stop condition:

- If approval is absent or ambiguous, stop and ask.

### Action 0.1.2 - Re-read Required Source Documents

Target files:

```text
docs/design/release_prep/01_001_public_release_preparation_plan.md
docs/design/release_prep/02_001_release_prep_current_relevance_review.md
docs/prime_directive/public_release_readiness_protocol.md
docs/engineer_continuity/2026/06/13/01_001_engineering_continuity_report.md
docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md
README.md
pyproject.toml
```

Procedure:

- Re-read the approved release plan.
- Re-read the current relevance review.
- Re-read the public release readiness protocol.
- Re-read the latest continuity report.
- Re-read the Malik lineage document.
- Re-read README and package metadata.
- Confirm that this workplan still matches current repo reality.

Completion criteria:

- No unhandled mismatch exists between release sources and this workplan.

Stop condition:

- If a mismatch exists, update this workplan first and ask for approval before
  implementation.

## Stage 0.2 - Inspect Worktree

### Action 0.2.1 - Capture Git Baseline

Target files:

```text
none
```

Commands:

```bash
git status --short
git branch --show-current
git rev-parse HEAD
```

Procedure:

- Capture current branch.
- Capture current commit.
- Capture modified and untracked files.
- Identify unrelated user changes.
- Do not revert unrelated changes.

Completion criteria:

- Baseline git state is known and recorded in the implementation log.

### Action 0.2.2 - Create Or Confirm Release-Prep Branch

Target files:

```text
none
```

Preferred command:

```bash
git checkout -b codex/v0.1.0-release-prep
```

Procedure:

- Create a dedicated release-prep branch before implementation.
- If the branch already exists, inspect it before switching.
- If branch creation or switching would obscure user work, stop.

Completion criteria:

- Work is on a dedicated release-prep branch or the Project Owner explicitly
  approves continuing on the current branch.

Stop condition:

- Branch operations would hide, overwrite, or confuse user work.

## Stage 0.3 - Baseline Verification

### Action 0.3.1 - Run Baseline Tests

Target files:

```text
none
```

Command:

```bash
uv run pytest
```

Procedure:

- Run the full test suite.
- Record result in the implementation log.

Completion criteria:

- Baseline test status is known.

Stop condition:

- If tests fail before release-prep edits, diagnose the baseline failure before
  changing release surfaces.

### Action 0.3.2 - Run Baseline Ruff Lint

Target files:

```text
none
```

Command:

```bash
uv run ruff check .
```

Procedure:

- Run the currently configured Ruff lint check.
- Record result in the implementation log.

Completion criteria:

- Baseline lint status is known.

### Action 0.3.3 - Run Baseline Build

Target files:

```text
none
```

Command:

```bash
uv build --out-dir [temporary build directory]
```

Procedure:

- Build source distribution and wheel.
- Use a temporary build directory, not a tracked repo path.
- If sandbox/cache permissions block the build, record that as local execution
  friction and rerun with approved cache access.

Completion criteria:

- Baseline build status is known.

Stop condition:

- If the package itself fails to build, fix that before release-prep feature
  work.

## Stage 0.4 - Implementation Log

### Action 0.4.1 - Create Updated Release-Prep Implementation Log

Target files:

```text
docs/design/release_prep/02_003_public_release_preparation_updated_implementation_log.md
```

Procedure:

- Create the implementation log before release-prep edits.
- Include:
  - approval phrase;
  - branch;
  - baseline commit;
  - baseline git status;
  - baseline test result;
  - baseline lint result;
  - baseline build result;
  - hard stop reminders;
  - note that this updated workplan is the controlling release-prep execution
    plan.

Completion criteria:

- Release-prep execution has a current implementation log.

---

# Phase 1 - Release Scope, Claims, And Cross-Repo Framing

## Stage 1.1 - Confirm Release Scope

### Action 1.1.1 - Confirm Version And Channel

Target files:

```text
pyproject.toml
README.md
RELEASE_NOTES.md
```

Procedure:

- Confirm package version is `0.1.0`.
- Confirm release label is `v0.1.0`.
- Confirm release channel is GitHub-only public pre-release.
- Confirm README and release notes do not claim PyPI availability.

Completion criteria:

- Version, tag label, and release channel agree across package metadata and
  public docs.

### Action 1.1.2 - Confirm Library Pre-Release Framing

Target files:

```text
README.md
RELEASE_NOTES.md
pyproject.toml
```

Procedure:

- Keep public framing as "library pre-release".
- Keep status classifier as `Development Status :: 3 - Alpha`.
- Do not claim production readiness.
- Do not claim benchmark-validated speed-ups.

Completion criteria:

- Public docs and metadata describe an alpha/pre-release library accurately.

## Stage 1.2 - Protect Current Correctness Claims

### Action 1.2.1 - Enumerate Implemented Correctness Claims

Target files:

```text
README.md
RELEASE_NOTES.md
docs/design/release_prep/02_003_public_release_preparation_updated_implementation_log.md
```

Procedure:

- Record the claims that public docs may make:
  - bounded directed flag simplex search through `k`;
  - first-class degenerate simplex records;
  - H-to-G skeletonization for loops and parallel edges;
  - compressed H-lift counts;
  - static quotient-tower integration through `state_collapser`;
  - fiber-addressed lifting over existing downstairs simplex records;
  - no upstairs interior search when the corresponding downstairs simplex is
    absent in the current small-object mode;
  - witness consistency coverage;
  - JSON/JSONL artifact output.

Completion criteria:

- Public claims are explicit and match tested behavior.

### Action 1.2.2 - Enumerate Deferred Claims

Target files:

```text
README.md
RELEASE_NOTES.md
```

Procedure:

- Ensure public docs list deferred work accurately:
  - Kan replacement and horn filling are not implemented;
  - full cofibrant/small-object replacement formalism is not exposed;
  - expanded H witness assignment artifacts are not implemented;
  - no neural message passing is implemented in this repo;
  - no CinchNET or PTVNN implementation is present;
  - no bitset, CSR, GPU, tensor, or multiprocessing acceleration exists;
  - no dynamic tower rebuilding occurs during search;
  - no benchmark-superiority claim is made.

Completion criteria:

- Public docs distinguish implemented behavior from deferred work.

## Stage 1.3 - Malik Lineage And `HGraphML` Boundary

### Action 1.3.1 - Preserve Malik Attribution

Target files:

```text
README.md
RELEASE_NOTES.md
docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md
```

Procedure:

- Preserve Abdullah N. Malik attribution in README.
- Preserve the detailed Malik lineage document.
- Ensure release notes mention Malik's role without overclaiming that this
  package implements the entire thesis.
- Use a consistent public name form:
  - preferred: `Abdullah N. Malik`;
  - acceptable in source context: `Abdullah Naeem Malik`.

Completion criteria:

- Attribution is clear, public, and consistent.

Stop condition:

- Any edit weakens, removes, or confuses Malik attribution.

### Action 1.3.2 - Preserve `HGraphML` Boundary

Target files:

```text
README.md
RELEASE_NOTES.md
docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md
```

Procedure:

- Keep this repo framed as:

```text
bounded simplex search and quotient lifting
```

- Keep `HGraphML` framed as:

```text
the separate beginning of quotient-tower-backed graph message passing
```

- Avoid these claims:
  - `jet_simplex_search` implements CinchNET;
  - `jet_simplex_search` implements PTVNN;
  - `jet_simplex_search` implements neural simplicial message passing;
  - `HGraphML` is already full CinchNET.

Completion criteria:

- Public users can tell which repo does simplex search and which repo begins
  message passing.

---

# Phase 2 - Dependency And Package Metadata

## Stage 2.1 - Verify `state_collapser` Dependency

### Action 2.1.1 - Confirm GitHub Tag Dependency

Target files:

```text
pyproject.toml
uv.lock
tests/test_release_metadata.py
```

Procedure:

- Confirm `pyproject.toml` uses:

```toml
"state-collapser @ git+https://github.com/TYLERSFOSTER/state_collapser.git@v0.7.2"
```

- Confirm no active release configuration points to `../state_collapser`.
- Confirm `allow-direct-references = true` remains documented and intentional
  for GitHub-only `v0.1.0`.
- Confirm release metadata tests protect the dependency decision.

Commands:

```bash
uv lock --check
uv sync
uv run python -c "import state_collapser; print(state_collapser.__name__)"
```

Completion criteria:

- A clean sync resolves `state_collapser` from the approved GitHub tag.
- No release path depends on a local sibling checkout.

Stop condition:

- GitHub dependency resolution fails or points at an unexpected revision.

### Action 2.1.2 - Verify Lockfile Source

Target files:

```text
uv.lock
```

Procedure:

- Inspect `uv.lock`.
- Confirm `state-collapser` is locked to the approved GitHub source and tag or
  revision corresponding to `v0.7.2`.
- Record the lock state in the implementation log.

Completion criteria:

- Lockfile supports clean public installation from GitHub.

## Stage 2.2 - Complete Package Metadata

### Action 2.2.1 - Add Or Verify Project URLs

Target files:

```text
pyproject.toml
tests/test_release_metadata.py
```

Procedure:

- Verify URLs include:
  - Homepage;
  - Repository;
  - Issues.
- Add `Source` URL if approved.
- Do not add Documentation URL unless hosted docs exist.

Completion criteria:

- Built metadata contains accurate project URLs.

### Action 2.2.2 - Add Or Verify Keywords

Target files:

```text
pyproject.toml
tests/test_release_metadata.py
```

Procedure:

- Add package keywords unless explicitly deferred:
  - `simplicial-complexes`;
  - `directed-graphs`;
  - `quotient-towers`;
  - `graph-algorithms`;
  - `state-collapser`.

Completion criteria:

- Keywords exist in package metadata or the deferral is recorded in the log.

### Action 2.2.3 - Reconcile Classifiers

Target files:

```text
pyproject.toml
tests/test_release_metadata.py
```

Procedure:

- Verify classifiers include:
  - `Development Status :: 3 - Alpha`;
  - relevant intended audience classifiers;
  - MIT license classifier;
  - Python `3`, `3.11`, and `3.12`;
  - relevant scientific or mathematical topic classifier.
- Decide whether to add `Intended Audience :: Developers`.
- Decide whether to add `Typing :: Typed`.

Typing rule:

- If `Typing :: Typed` is added, also add
  `src/jet_simplex_search/py.typed` and verify it is included in the wheel.
- If `py.typed` is deferred, do not include `Typing :: Typed`.

Completion criteria:

- Classifiers match the package's actual release posture.

### Action 2.2.4 - Verify Metadata By Building

Target files:

```text
none
```

Command:

```bash
uv build --out-dir [temporary build directory]
```

Procedure:

- Build source distribution and wheel.
- Inspect wheel metadata for:
  - name;
  - version;
  - URLs;
  - keywords;
  - classifiers;
  - license;
  - dependency on `state-collapser`.

Completion criteria:

- Built metadata matches release decisions.

---

# Phase 3 - README And Public Documentation

## Stage 3.1 - README Badges And Installation

### Action 3.1.1 - Preserve Logo And Title

Target files:

```text
README.md
```

Procedure:

- Preserve the current logo block unless the Project Owner explicitly asks to
  change it.
- Preserve the title exactly:

```markdown
# **JET- SIMPLEX - SEARCH**
```

Completion criteria:

- Logo and title remain intact.

### Action 3.1.2 - Verify Badges

Target files:

```text
README.md
.github/workflows/test.yml
pyproject.toml
```

Procedure:

- Keep badges only for systems that exist or approved static facts:
  - Python support;
  - MIT license;
  - pytest/tests static badge;
  - Ruff static badge;
  - pre-release status;
  - uv package manager.
- Add CI badge only after `.github/workflows/test.yml` exists.
- Do not add PyPI badge.
- Do not add coverage badge.
- Do not add hosted-docs badge.

Completion criteria:

- README badges do not overclaim.

### Action 3.1.3 - Verify Installation Section

Target files:

```text
README.md
```

Procedure:

- Keep GitHub source pre-release installation instructions.
- Document that `state_collapser` is resolved from GitHub tag `v0.7.2`.
- Do not mention hidden sibling-checkout requirements as the primary path.
- Do not claim `pip install jet-simplex-search` or PyPI availability.

Completion criteria:

- A new user can understand the supported GitHub checkout install path.

## Stage 3.2 - README Scope And Limitations

### Action 3.2.1 - Verify Implemented Feature List

Target files:

```text
README.md
```

Procedure:

- Confirm the feature list includes current release surfaces:
  - graph input records;
  - H-to-G skeletonization;
  - formal identity search edges;
  - directed flag enumeration through `k`;
  - degenerate simplex records;
  - cached frontier recurrence;
  - `state_collapser` static tower integration;
  - fiber-addressed lifting;
  - compressed H-lift counts;
  - JSON/JSONL artifacts;
  - smoke examples.

Completion criteria:

- README describes implemented package behavior.

### Action 3.2.2 - Verify Known Limitations

Target files:

```text
README.md
```

Procedure:

- Keep limitations concise.
- Include:
  - no Kan replacement or horn filling;
  - expanded H witness assignment artifacts deferred;
  - exact label-agreement policy for v0.1;
  - static tower search;
  - no accelerated backend;
  - lower-level skeleton/tower API is separate from `search_simplices`.
- Add no neural message passing in this repo if README context needs it.

Completion criteria:

- Public users can tell what is not implemented.

### Action 3.2.3 - Proofread Public README Text

Target files:

```text
README.md
```

Procedure:

- Fix typos.
- Keep prose professional and bounded.
- Avoid marketing claims stronger than the implementation.
- Confirm all README links resolve.

Completion criteria:

- README is ready to be shown to first external users.

## Stage 3.3 - Documentation Link Policy

### Action 3.3.1 - Enforce Approved Root Link Policy

Target files:

```text
README.md
```

Procedure:

- Do not link release-prep docs from README.
- Do not link engineering continuity reports from README.
- Do not link `docs/prime_directive` from README.
- Keep design spine links.
- Keep Malik lineage link.

Completion criteria:

- README links match approved public posture.

### Action 3.3.2 - Verify Malik Lineage Document Link

Target files:

```text
README.md
docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md
```

Procedure:

- Confirm README link to Malik lineage document resolves.
- Confirm the Malik lineage document has no machine-local thesis path.
- Confirm the document preserves Malik attribution.
- Confirm the document preserves `HGraphML` boundary.

Completion criteria:

- The full provenance link is valid and release-safe.

## Stage 3.4 - Historical Design Docs Hygiene Policy

### Action 3.4.1 - Classify Documentation Surfaces

Target files:

```text
docs/
scripts/release_hygiene.py
```

Procedure:

- Classify docs into:
  - strict public release surfaces;
  - public but historical design logs;
  - internal or unlinked project-operation docs.
- Recommended strict surfaces:
  - `README.md`;
  - `RELEASE_NOTES.md`;
  - `SECURITY.md`;
  - `CONTRIBUTING.md`;
  - `pyproject.toml`;
  - `docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md`;
  - selected high-level design docs linked from README.
- Recommended warn-only surfaces:
  - implementation logs;
  - engineering continuity reports;
  - workplans containing historical command transcripts.

Completion criteria:

- Release hygiene can distinguish public-facing docs from historical logs.

---

# Phase 4 - Release Notes

## Stage 4.1 - Create Release Notes

### Action 4.1.1 - Add `RELEASE_NOTES.md`

Target files:

```text
RELEASE_NOTES.md
```

Implementation:

- Add title:

```markdown
# Release Notes
```

- Add first release section:

```markdown
## v0.1.0 - GitHub Library Pre-Release
```

- Include:
  - GitHub-only library pre-release status;
  - install notes using `state_collapser` GitHub tag `v0.7.2`;
  - implemented features;
  - H-to-G skeletonization;
  - H-lift counts;
  - static quotient-tower integration;
  - missing-downstairs-interior small-object behavior;
  - witness consistency posture;
  - smoke examples and regression checks;
  - artifact support;
  - known limitations;
  - deferred work;
  - verification commands;
  - Abdullah N. Malik attribution;
  - Malik lineage document link;
  - `HGraphML` boundary;
  - design spine links.
- Exclude:
  - PyPI claims;
  - production-ready claims;
  - benchmark-superiority claims;
  - "complete thesis implementation" language;
  - Kan-implemented language;
  - neural-message-passing-in-this-repo language.

Completion criteria:

- Release notes align with README, metadata, and tested behavior.

## Stage 4.2 - Review Release Notes

### Action 4.2.1 - Check Release Notes Against Public Claims

Target files:

```text
RELEASE_NOTES.md
README.md
docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md
```

Procedure:

- Compare release notes to README.
- Confirm no stronger claim appears in release notes than in README.
- Confirm `HGraphML` is mentioned only as a separate related message-passing
  package.
- Confirm the release notes do not describe smoke scripts as benchmarks.

Completion criteria:

- Release notes are factual, bounded, and consistent.

---

# Phase 5 - Ruff, Formatting, And Docstrings

## Stage 5.1 - Decide Tooling Strictness

### Action 5.1.1 - Decide Ruff Rule Expansion

Target files:

```text
pyproject.toml
docs/design/release_prep/02_003_public_release_preparation_updated_implementation_log.md
```

Procedure:

- Review current Ruff config.
- Decide whether `v0.1.0` should:
  - keep current light lint rules; or
  - expand to import sorting, bugbear-style checks, and docstring rules.
- If expanding rules causes broad unrelated churn, stop and ask whether to defer
  strictness.

Completion criteria:

- Tooling strictness is explicit.

### Action 5.1.2 - Decide Typed Package Status

Target files:

```text
pyproject.toml
src/jet_simplex_search/py.typed
tests/test_package.py
```

Procedure:

- Decide whether `v0.1.0` ships as typed.
- If yes:
  - add `src/jet_simplex_search/py.typed`;
  - add `Typing :: Typed` classifier;
  - verify wheel includes `py.typed`.
- If no:
  - keep `Typing :: Typed` absent;
  - record deferral.

Completion criteria:

- Typing metadata and package contents are consistent.

## Stage 5.2 - Enforce Ruff And Formatting

### Action 5.2.1 - Run Ruff Format Check

Target files:

```text
src/
tests/
smoke/
scripts/
```

Command:

```bash
uv run ruff format --check .
```

Procedure:

- Run format check.
- If it fails, decide whether to run:

```bash
uv run ruff format .
```

- Inspect diffs after formatting.

Completion criteria:

- Ruff format check passes or an explicit deferral is approved and recorded.

### Action 5.2.2 - Run Ruff Lint

Target files:

```text
src/
tests/
smoke/
scripts/
```

Command:

```bash
uv run ruff check .
```

Procedure:

- Run lint.
- Fix findings manually where needed.
- Use auto-fix only for mechanical safe changes.
- Do not weaken rules merely to pass unless the rule is clearly inappropriate
  and the deferral is recorded.

Completion criteria:

- Ruff lint passes.

## Stage 5.3 - Public Docstring Review

### Action 5.3.1 - Identify Public Docstring Surface

Target files:

```text
src/jet_simplex_search/*.py
```

Procedure:

- Enumerate public modules, classes, functions, and methods.
- Treat leading-underscore helpers as private unless they are part of public
  behavior or release hygiene.
- Identify missing or weak public docstrings.

Completion criteria:

- Public docstring gap list is known.

### Action 5.3.2 - Improve Public Docstrings

Target files:

```text
src/jet_simplex_search/*.py
```

Implementation:

- Add or improve docstrings for public APIs.
- Explain domain-specific terms where needed:
  - directed flag simplex;
  - degenerate simplex;
  - frontier;
  - simplex fiber;
  - edge fiber;
  - quotient tower adapter;
  - H-to-G skeletonization;
  - H-lift count.
- Do not claim deferred features.
- Keep docstrings concise.

Completion criteria:

- Public API docstrings are coherent for first external readers.

### Action 5.3.3 - Decide Docstring Gate

Target files:

```text
pyproject.toml
```

Procedure:

- Decide whether docstring quality is enforced by Ruff pydocstyle rules in
  `v0.1.0`.
- If yes, configure and pass the gate.
- If no, remove any release-plan claim that docstring rules are a hard gate for
  `v0.1.0` and record the deferral.

Completion criteria:

- The release plan does not promise a docstring gate that the repo does not
  actually run.

---

# Phase 6 - Smoke Regression, README Tests, And Correctness Coverage

## Stage 6.1 - Smoke Script Snapshot Tests

### Action 6.1.1 - Decide Smoke Coverage Scope

Target files:

```text
smoke/
tests/test_smoke_scripts.py
tests/test_smoke_docs.py
```

Procedure:

- Decide whether all `smoke/smoke_*.py` files are public smoke examples.
- Decide whether `smoke_001.py` and `smoke_002.py` require matching Markdown
  count arguments or are explicitly excluded as early/manual examples.
- Record the decision in test names or comments.

Completion criteria:

- Smoke regression scope is unambiguous.

### Action 6.1.2 - Add Smoke Output Snapshot Test

Target files:

```text
tests/test_smoke_scripts.py
```

Implementation:

- Add a test table mapping each public smoke script to expected stdout.
- Execute scripts with the current Python interpreter.
- Set `PYTHONPATH` so local `src/` and `smoke/` imports work.
- Compare stdout exactly.
- Provide useful diffs when output changes.

Completion criteria:

- `uv run pytest tests/test_smoke_scripts.py` passes.

### Action 6.1.3 - Add Smoke Markdown Coverage Test

Target files:

```text
tests/test_smoke_docs.py
smoke/*.md
```

Implementation:

- Add a test that each public smoke script has a matching `.md` explanation, or
  belongs to an explicit excluded set.
- Optionally check each explanation includes:
  - command;
  - output;
  - count argument or explicit error note.

Completion criteria:

- Human-readable smoke count arguments stay paired with public smoke scripts.

## Stage 6.2 - README Quick-Start Test

### Action 6.2.1 - Verify Existing README Quick-Start Test

Target files:

```text
tests/test_readme_quickstart.py
README.md
```

Procedure:

- Confirm test recreates the README quick-start graph.
- Confirm it asserts current counts:

```python
{(1, 0): 2, (1, 1): 3, (1, 2): 4, (0, 0): 3, (0, 1): 6, (0, 2): 10}
```

- Confirm README output matches the test.

Completion criteria:

- README quick-start remains executable and current.

## Stage 6.3 - Protect Core Correctness Tests

### Action 6.3.1 - Verify Required Correctness Tests Exist

Target files:

```text
tests/test_fiber_lift.py
tests/test_witness_consistency.py
tests/test_h_lift.py
tests/test_skeleton.py
tests/integration/test_clean_state_collapser_tower.py
tests/test_readme_quickstart.py
```

Procedure:

- Confirm tests cover:
  - missing downstairs 2-simplex prevents upstairs triangle search;
  - degenerate downstairs simplex can have nondegenerate upstairs lift;
  - source-sensitive edge fibers;
  - witness projection consistency;
  - H-to-G skeletonization;
  - compressed H-lift counts;
  - clean `state_collapser` tower bridge;
  - README quick-start.

Completion criteria:

- Release-critical correctness claims have tests.

### Action 6.3.2 - Run Full Test Suite

Target files:

```text
none
```

Command:

```bash
uv run pytest
```

Completion criteria:

- Full test suite passes.

---

# Phase 7 - CI And GitHub Templates

## Stage 7.1 - GitHub Actions

### Action 7.1.1 - Add CI Workflow

Target files:

```text
.github/workflows/test.yml
```

Implementation:

- Trigger on:
  - pushes to `main`;
  - pull requests to `main`.
- Matrix Python versions:
  - `3.11`;
  - `3.12`.
- Install `uv`.
- Run:
  - `uv sync`;
  - `uv run ruff check .`;
  - `uv run ruff format --check .`;
  - `uv run pytest`;
  - `uv build`.
- Ensure workflow uses the GitHub `state_collapser` tag dependency, not a local
  sibling path.

Completion criteria:

- CI workflow exists and is syntactically valid.

### Action 7.1.2 - Add CI Badge After Workflow Exists

Target files:

```text
README.md
.github/workflows/test.yml
```

Procedure:

- Add CI badge only after workflow file exists.
- Point badge to the actual workflow path/name.
- Do not add coverage or docs-hosting badges.

Completion criteria:

- README CI badge corresponds to a real workflow.

### Action 7.1.3 - Verify CI Commands Locally

Target files:

```text
none
```

Commands:

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv build --out-dir [temporary build directory]
```

Completion criteria:

- Local commands match CI commands and pass.

## Stage 7.2 - GitHub Templates

### Action 7.2.1 - Add Bug Report Template

Target files:

```text
.github/ISSUE_TEMPLATE/bug_report.md
```

Implementation:

- Include:
  - observed behavior;
  - expected behavior;
  - graph/input snippet;
  - `k`;
  - `state_collapser` version/source;
  - Python version;
  - command run;
  - traceback/output.

Completion criteria:

- Bug reports request release-relevant reproduction details.

### Action 7.2.2 - Add Feature Request Template

Target files:

```text
.github/ISSUE_TEMPLATE/feature_request.md
```

Implementation:

- Include:
  - requested behavior;
  - mathematical/graph context;
  - whether it touches deferred features;
  - expected API shape if known.

Completion criteria:

- Feature requests distinguish implemented scope from deferred tracks.

### Action 7.2.3 - Add Pull Request Template

Target files:

```text
.github/pull_request_template.md
```

Implementation:

- Include:
  - summary;
  - tests run;
  - release-claim checklist;
  - attribution-preservation checkbox;
  - no PyPI/benchmark/production-ready overclaim checkbox;
  - no Kan/neural-message-passing overclaim checkbox.

Completion criteria:

- PR template reinforces release discipline.

## Stage 7.3 - Repository Metadata

### Action 7.3.1 - Prepare GitHub Repository Metadata Recommendation

Target files:

```text
docs/design/release_prep/02_003_public_release_preparation_updated_implementation_log.md
```

Procedure:

- Record recommended repository description:

```text
Quotient-tower accelerated search for directed flag simplices in sparse graphs.
```

- Record recommended topics:
  - `python`;
  - `graph-algorithms`;
  - `directed-graphs`;
  - `simplicial-complexes`;
  - `quotient-towers`;
  - `state-collapser`.

Completion criteria:

- Manual GitHub repository settings are documented before public release.

---

# Phase 8 - Release Hygiene Script

## Stage 8.1 - Define Hygiene Scope

### Action 8.1.1 - Define Strict And Warn-Only Surfaces

Target files:

```text
scripts/release_hygiene.py
tests/test_release_hygiene.py
```

Implementation:

- Strict public surfaces should include:
  - `README.md`;
  - `RELEASE_NOTES.md`;
  - `SECURITY.md`;
  - `CONTRIBUTING.md`;
  - `pyproject.toml`;
  - package source under `src/`;
  - tests;
  - smoke source and smoke Markdown;
  - root GitHub templates;
  - Malik lineage document;
  - README-linked design spine docs.
- Warn-only historical surfaces may include:
  - engineering continuity reports;
  - implementation logs;
  - release-prep workplans;
  - design logs with historical command transcripts.

Completion criteria:

- Hygiene script does not accidentally force deletion of useful historical
  records.

### Action 8.1.2 - Document Hygiene Scope

Target files:

```text
scripts/release_hygiene.py
docs/design/release_prep/02_003_public_release_preparation_updated_implementation_log.md
```

Procedure:

- Document which paths are strict.
- Document which paths are warn-only.
- Document any allowlist.

Completion criteria:

- Future maintainers understand hygiene failures and warnings.

## Stage 8.2 - Implement Hygiene Checks

### Action 8.2.1 - Add Script Skeleton

Target files:

```text
scripts/release_hygiene.py
tests/test_release_hygiene.py
```

Implementation:

- Add CLI:

```bash
uv run python scripts/release_hygiene.py --repo-root .
```

- Parse `--repo-root`.
- Return nonzero on failure.
- Print clear pass/fail/warn messages.

Completion criteria:

- Hygiene script runs from repo root.

### Action 8.2.2 - Check Machine-Local Paths

Target files:

```text
scripts/release_hygiene.py
tests/test_release_hygiene.py
```

Implementation:

- Fail on machine-local paths in strict public surfaces:
  - home-directory absolute paths;
  - temporary build/cache absolute paths;
  - platform-specific private cache paths;
  - Windows drive paths.
- Warn on machine-local paths in historical logs unless the Project Owner
  chooses full sanitization.

Completion criteria:

- Release-facing docs are clean of private local paths.

### Action 8.2.3 - Check Build Outputs And Caches

Implementation:

- Use `git ls-files` to inspect tracked files.
- Fail on tracked:
  - `dist/`;
  - `build/`;
  - `.pytest_cache/`;
  - `.ruff_cache/`;
  - `*.egg-info`;
  - temporary build directories.

Completion criteria:

- Tracked local/build byproducts are caught.

### Action 8.2.4 - Check Generated Artifact Outputs

Implementation:

- Fail on generated artifact directories unless explicitly allowlisted.
- Fail on generated `readout_source.json`, JSONL artifact tables, or diagnostic
  output files outside approved fixture paths.
- Keep source smoke examples and Markdown explanations allowed.

Completion criteria:

- Release does not accidentally include generated artifact outputs.

### Action 8.2.5 - Check Large Public Files

Implementation:

- Fail on tracked public files larger than the approved threshold unless
  allowlisted.
- Print file path and size.

Completion criteria:

- Large accidental artifacts are caught.

### Action 8.2.6 - Check Broken Links

Implementation:

- Parse relative Markdown links in README and strict public docs.
- Fail when target file does not exist.
- Respect approved policy:
  - do not require links to continuity reports;
  - do not require links to release-prep docs;
  - do not require links to `docs/prime_directive`.

Completion criteria:

- Public relative links resolve without forcing forbidden links.

### Action 8.2.7 - Check Badge Claims

Implementation:

- Fail if README contains:
  - PyPI badge;
  - coverage badge;
  - docs-hosting badge;
  - CI badge without `.github/workflows/test.yml`;
  - Ruff badge without Ruff dependency/config.

Completion criteria:

- README badges correspond to configured systems.

### Action 8.2.8 - Check Dependency Source

Implementation:

- Fail if release metadata contains a local sibling dependency on
  `state_collapser`.
- Pass only when dependency source uses the approved GitHub `v0.7.2` tag or an
  explicitly approved replacement.

Completion criteria:

- Local sibling dependency cannot survive release hygiene.

### Action 8.2.9 - Check Disallowed Claims

Implementation:

- Fail on public claims such as:
  - production-ready;
  - benchmark-validated;
  - fastest;
  - PyPI install/published;
  - Kan implemented;
  - neural message passing implemented in this repo;
  - CinchNET implemented in this repo;
  - complete thesis implementation.

Completion criteria:

- Public docs remain bounded and safe to quote.

### Action 8.2.10 - Check Malik And `HGraphML` Framing

Implementation:

- Fail if README lacks Malik attribution.
- Fail if README link to the Malik lineage document is broken.
- Fail if strict public docs imply this repo implements `HGraphML`, CinchNET,
  PTVNN, or neural message passing.
- Fail if strict public docs imply `HGraphML` is full CinchNET.

Completion criteria:

- Cross-repo and attribution framing remains correct.

### Action 8.2.11 - Check Secrets And Credentials

Implementation:

- Add lightweight scans for obvious tokens, private keys, generated
  credentials, and accidental environment dumps.
- Keep the scanner conservative enough to avoid noisy false positives.

Completion criteria:

- Obvious secrets are caught before release.

### Action 8.2.12 - Warn On Unlinked Prime Directive

Implementation:

- If `docs/prime_directive` exists and is not linked from README, print a
  warning only.
- Do not fail, because this is the approved posture.

Completion criteria:

- Approved prime-directive posture is represented.

## Stage 8.3 - Test Hygiene Script

### Action 8.3.1 - Add Unit Tests For Hygiene Checks

Target files:

```text
tests/test_release_hygiene.py
```

Implementation:

- Test pass case.
- Test strict local path failure.
- Test warn-only historical local path behavior.
- Test broken link failure.
- Test local `state_collapser` dependency failure.
- Test disallowed claim failure.
- Test missing Malik lineage link failure.
- Test bad `HGraphML`/CinchNET overclaim failure.
- Test prime directive warning does not fail.

Completion criteria:

- Hygiene script behavior is covered.

### Action 8.3.2 - Run Hygiene Script

Target files:

```text
none
```

Command:

```bash
uv run python scripts/release_hygiene.py --repo-root .
```

Completion criteria:

- Release hygiene passes or only approved warnings remain.

---

# Phase 9 - Security, Contribution, License, And Public Support Docs

## Stage 9.1 - Security Policy

### Action 9.1.1 - Add `SECURITY.md`

Target files:

```text
SECURITY.md
```

Implementation:

- State pre-release support posture.
- Give vulnerability/contact instructions appropriate for the repo.
- Ask reporters not to disclose sensitive details publicly.
- Avoid response-time SLAs unless approved.
- Do not imply enterprise support.

Completion criteria:

- Public security reporting path exists.

## Stage 9.2 - Contribution Guide

### Action 9.2.1 - Add `CONTRIBUTING.md`

Target files:

```text
CONTRIBUTING.md
```

Implementation:

- Include setup:
  - `uv sync`;
  - `uv run pytest`;
  - `uv run ruff check .`;
  - `uv run ruff format --check .`;
  - `uv run python scripts/release_hygiene.py --repo-root .`.
- Include package scope:
  - preserve directed flag semantics;
  - preserve first-class degenerates;
  - preserve fiber-addressed lifting;
  - preserve H-to-G skeletonization and H-lift accounting;
  - preserve `state_collapser` tower ownership;
  - preserve Abdullah N. Malik attribution;
  - preserve the `HGraphML` boundary.
- Include release-claim discipline:
  - no benchmark/production/PyPI claims unless true;
  - no Kan/neural-message-passing claims unless implemented.
- Include PR expectations.

Completion criteria:

- Contributors can run local checks and understand scope.

## Stage 9.3 - License And Conduct

### Action 9.3.1 - Verify License

Target files:

```text
LICENSE
pyproject.toml
README.md
```

Procedure:

- Confirm MIT license remains intended.
- Confirm metadata points at the license file.
- Confirm README license badge is correct.

Completion criteria:

- License posture is clear.

### Action 9.3.2 - Confirm Code Of Conduct Is Omitted

Target files:

```text
none
```

Procedure:

- Confirm no `CODE_OF_CONDUCT.md` is added for `v0.1.0`.
- If one exists from user work, do not delete it without explicit instruction;
  record the discrepancy.

Completion criteria:

- Worktree respects approved `v0.1.0` conduct-doc decision.

---

# Phase 10 - Artifact And Example Policy

## Stage 10.1 - Smoke Examples

### Action 10.1.1 - Confirm Smoke Directory Policy

Target files:

```text
smoke/
README.md
RELEASE_NOTES.md
```

Procedure:

- Keep smoke scripts in git as public examples and regression material.
- Keep smoke Markdown count arguments in git.
- Do not describe smoke scripts as benchmarks.

Completion criteria:

- Smoke examples are public, compact, and reproducible.

## Stage 10.2 - Generated Artifacts

### Action 10.2.1 - Confirm Generated Artifacts Are Not Committed

Target files:

```text
none
```

Procedure:

- Search for generated artifact output directories.
- Search for generated JSON/JSONL readout files outside approved tests.
- Remove or ignore accidental generated outputs only after verifying they are
  not user-authored source material.

Completion criteria:

- No generated artifact output is accidentally tracked for `v0.1.0`.

### Action 10.2.2 - Document Artifact Policy

Target files:

```text
README.md
RELEASE_NOTES.md
```

Procedure:

- Say artifact files are generated by users.
- Do not bundle generated artifact examples in `v0.1.0`.
- Keep artifact output filenames documented.

Completion criteria:

- Users know how artifacts are produced without expecting bundled outputs.

---

# Phase 11 - Packaging Content, Build, And Clean Install Verification

## Stage 11.1 - Build Distributions

### Action 11.1.1 - Build Sdist And Wheel

Target files:

```text
none
```

Command:

```bash
uv build --out-dir [temporary build directory]
```

Procedure:

- Build source distribution and wheel.
- Use a temporary build directory outside tracked source.
- Record artifact filenames and hashes if needed for release notes or release
  asset preparation.

Completion criteria:

- Source distribution and wheel build successfully.

## Stage 11.2 - Inspect Distribution Contents

### Action 11.2.1 - Inspect Wheel Contents

Target files:

```text
built wheel
```

Procedure:

- Inspect wheel file list.
- Confirm wheel includes only intended package files.
- Confirm `smoke/` is not included in wheel unless separately approved.
- Confirm `py.typed` inclusion matches typed-package decision.

Completion criteria:

- Wheel contents match release policy.

### Action 11.2.2 - Inspect Sdist Contents

Target files:

```text
built source distribution
```

Procedure:

- Inspect sdist file list.
- Confirm expected public source files are present:
  - README;
  - LICENSE;
  - `pyproject.toml`;
  - `RELEASE_NOTES.md`;
  - `SECURITY.md`;
  - `CONTRIBUTING.md`;
  - package source;
  - tests if approved;
  - smoke source and Markdown explanations if approved;
  - relevant docs.

Completion criteria:

- Sdist is useful for GitHub source-release users.

## Stage 11.3 - Clean Install From Wheel

### Action 11.3.1 - Create Clean Temporary Environment

Target files:

```text
none
```

Procedure:

- Create a clean temporary virtual environment.
- Install the built wheel.
- Do not install from the repository checkout.
- Ensure dependency resolution uses the GitHub `state_collapser` tag.

Completion criteria:

- Built wheel installs in a clean environment.

### Action 11.3.2 - Run Installed Import Smoke

Target files:

```text
installed package
```

Command:

```bash
python -c "from jet_simplex_search import search_simplices; print(search_simplices)"
```

Completion criteria:

- Installed package imports without relying on the source checkout.

### Action 11.3.3 - Run README Quick-Start From Installed Wheel

Target files:

```text
README.md
installed package
```

Procedure:

- Run the README quick-start code in the clean installed environment.
- Confirm output matches README.
- Confirm `state_collapser` imports from the installed dependency, not a local
  sibling checkout.

Completion criteria:

- Public quick-start works from installed wheel.

---

# Phase 12 - Final Local Verification

## Stage 12.1 - Run Final Command Suite

### Action 12.1.1 - Run Full Final Checks

Target files:

```text
none
```

Commands:

```bash
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run python scripts/release_hygiene.py --repo-root .
uv build --out-dir [temporary build directory]
```

Procedure:

- Run commands from a clean working tree as much as practical.
- Record results in the implementation log.
- If any command fails, fix the underlying issue or record the approved deferral.

Completion criteria:

- Final local checks pass.

## Stage 12.2 - Final Public Documentation Review

### Action 12.2.1 - Review Public Docs Together

Target files:

```text
README.md
RELEASE_NOTES.md
SECURITY.md
CONTRIBUTING.md
docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md
```

Procedure:

- Read public docs as an external user would.
- Confirm:
  - installation path is clear;
  - dependency source is clear;
  - Malik attribution is clear;
  - `HGraphML` boundary is clear;
  - known limitations are clear;
  - no PyPI claim appears;
  - no production-ready claim appears;
  - no benchmark-superiority claim appears;
  - no Kan/neural-message-passing overclaim appears;
  - no machine-local paths appear in strict public docs.

Completion criteria:

- Public docs are coherent and bounded.

## Stage 12.3 - GitHub Actions Verification

### Action 12.3.1 - Verify CI Passes Remotely

Target files:

```text
.github/workflows/test.yml
```

Procedure:

- Push release-prep branch only after user approval if needed.
- Verify GitHub Actions passes for Python `3.11` and `3.12`.
- Do not add a passing CI claim until the workflow has actually passed.

Completion criteria:

- CI passes on the release branch or target branch.

Stop condition:

- Remote CI fails and local reproduction is unclear.

---

# Phase 13 - Release Readiness Review And Approval Gate

## Stage 13.1 - Prepare Release Readiness Summary

### Action 13.1.1 - Write Readiness Summary In Implementation Log

Target files:

```text
docs/design/release_prep/02_003_public_release_preparation_updated_implementation_log.md
```

Procedure:

- Summarize:
  - files changed;
  - tests run;
  - build artifacts produced;
  - clean install result;
  - CI result;
  - release hygiene result;
  - known remaining limitations;
  - any approved deferrals.

Completion criteria:

- Project Owner has a compact release readiness summary.

### Action 13.1.2 - Produce Final Release Checklist

Target files:

```text
docs/design/release_prep/02_003_public_release_preparation_updated_implementation_log.md
```

Checklist:

- Package version is `0.1.0`.
- README status is pre-release.
- `RELEASE_NOTES.md` exists.
- `SECURITY.md` exists.
- `CONTRIBUTING.md` exists.
- CI workflow exists.
- Issue templates exist.
- PR template exists.
- Ruff lint passes.
- Ruff format check passes or explicit deferral exists.
- Full pytest suite passes.
- Smoke snapshot tests pass.
- Smoke doc coverage tests pass.
- README quick-start test passes.
- Release hygiene passes.
- Build succeeds.
- Clean wheel install succeeds.
- Installed-wheel README quick-start succeeds.
- Wheel contents match policy.
- Sdist contents match policy.
- `state_collapser` dependency uses GitHub `v0.7.2`.
- No local sibling dependency remains.
- No generated artifact outputs are tracked.
- Public docs preserve Malik attribution.
- Public docs preserve `HGraphML` boundary.
- Public docs do not overclaim Kan, neural message passing, PyPI, production
  readiness, or benchmark superiority.
- Project Owner has explicitly approved release action.

Completion criteria:

- Release readiness is reviewable.

## Stage 13.2 - Ask For Explicit Release Action Approval

### Action 13.2.1 - Request Project Owner Approval

Target files:

```text
none
```

Procedure:

- Present readiness summary to Project Owner.
- Ask explicitly before:
  - tagging;
  - uploading release assets;
  - making repository public;
  - publishing anywhere;
  - creating a GitHub release.

Completion criteria:

- No release action occurs without explicit approval.

Stop condition:

- Approval is absent, ambiguous, or conditional.

---

# Phase 14 - Release Action, Only After Approval

## Stage 14.1 - Tagging

### Action 14.1.1 - Create Release Tag

Target files:

```text
git tag
```

Procedure:

- Only after explicit Project Owner approval, create `v0.1.0` tag.
- Use a non-interactive git command.
- Verify tag points at the intended commit.

Completion criteria:

- Tag exists locally and points at the approved commit.

Stop condition:

- Any uncertainty about commit, branch, or approval.

## Stage 14.2 - GitHub Release

### Action 14.2.1 - Prepare GitHub Release Draft

Target files:

```text
RELEASE_NOTES.md
built distributions
```

Procedure:

- Only after explicit approval, draft GitHub release.
- Use `RELEASE_NOTES.md` as the source.
- Attach approved release assets only.
- Do not publish to PyPI.
- Do not make claims beyond release notes.

Completion criteria:

- GitHub release draft or published release matches approved notes.

Stop condition:

- Project Owner has not approved publishing the GitHub release.

---

# Phase 15 - Post-Release Continuity

## Stage 15.1 - Record Outcome

### Action 15.1.1 - Update Implementation Log

Target files:

```text
docs/design/release_prep/02_003_public_release_preparation_updated_implementation_log.md
```

Procedure:

- Record whether release was:
  - prepared only;
  - tagged;
  - published as GitHub release;
  - made public;
  - deferred.
- Record final commit and tag if any.
- Record final checks and links.

Completion criteria:

- Future engineers can reconstruct what happened.

## Stage 15.2 - Write Engineering Continuity Report

### Action 15.2.1 - Add Release Continuity Report

Target files:

```text
docs/engineer_continuity/
```

Procedure:

- Add a continuity report if release prep involved substantial changes.
- Include:
  - what was changed;
  - what was verified;
  - what remains deferred;
  - release tag or branch if created;
  - any failed checks or approved exceptions.

Completion criteria:

- Release-prep state is preserved for future work.

## Stage 15.3 - File Follow-Up Work

### Action 15.3.1 - Capture Deferred Work

Target files:

```text
docs/design/release_prep/02_003_public_release_preparation_updated_implementation_log.md
```

Procedure:

- Capture deferred tasks:
  - PyPI publication path;
  - benchmark suite;
  - Kan replacement design;
  - expanded H witness artifacts;
  - bitset/CSR acceleration;
  - HGraphML integration path;
  - hosted docs if desired.

Completion criteria:

- Deferred work is visible and not confused with `v0.1.0` release blockers.

## Final Note

This is the complete updated release-prep workplan. It retains the still-valid
content from the original implementation workplan and incorporates the
current-state addendum.

Execute this document instead of `01_002` for future `v0.1.0` release-prep
work.
