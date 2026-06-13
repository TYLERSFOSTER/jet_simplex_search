# Public Release Preparation Implementation Workplan

## Status

Implementation workplan for preparing `jet_simplex_search` for the approved
`v0.1.0` GitHub-only library pre-release.

Update note, 2026-06-13:

This workplan should not be executed mechanically without the current relevance
review at
`docs/design/release_prep/02_001_release_prep_current_relevance_review.md`.
The repo now has updated dependency state, H-to-G skeletonization and H-lift
surfaces, a Malik lineage document, and an explicit `HGraphML` boundary that
were not all present when this workplan was drafted. Use
`docs/design/release_prep/02_002_public_release_preparation_updated_implementation_workplan.md`
as the current merged implementation workplan.

This document is derived from:

```text
docs/design/release_prep/01_001_public_release_preparation_plan.md
```

This workplan is not itself permission to execute release actions. It is also
not permission to tag, publish, upload release assets, make the repository
public, or publish to PyPI.

## Approved Release Decisions

- Release label: `v0.1.0`.
- Package metadata version: `0.1.0`.
- Release channel: GitHub-only public pre-release.
- Release framing: library pre-release.
- Smoke scripts: both public examples and regression checks.
- `state_collapser` dependency: GitHub release tag `v0.7.2`.
- Package status classifier: `Development Status :: 3 - Alpha`.
- CI: GitHub Actions with Python `3.11` and `3.12`.
- Tooling: Ruff lint, Ruff format check, and docstring-quality gate.
- Documentation: add concise README Known Limitations section.
- Do not link release-prep plan from README.
- Do not add or fix README links to engineering continuity report.
- Keep `docs/prime_directive` in repo but do not link it from root docs.
- Release hygiene: add `scripts/release_hygiene.py`.
- Artifact policy: no generated artifact outputs committed for `v0.1.0`.
- Security/license: keep MIT, add `SECURITY.md`, add `CONTRIBUTING.md`, skip
  `CODE_OF_CONDUCT.md`.
- GitHub prep: add CI workflow, issue templates, PR template, repo metadata
  recommendations; no GitHub Pages.
- Release notes: add `RELEASE_NOTES.md`.

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
- changing attribution for PM Abdul Malik's algorithmic contribution;
- claiming production readiness;
- claiming benchmark superiority or statistically validated speedups;
- replacing the approved `state_collapser` `v0.7.2` dependency decision.

## Execution Principles

- Execute phases in order unless the Project Owner explicitly changes order.
- Preserve unrelated user changes.
- Use a dedicated release-prep branch before implementation.
- Use repo-local tools and tests as reality checks.
- Treat `state_collapser` as the owner of tower semantics.
- Keep public claims bounded to implemented and verified behavior.
- Prefer failing release gates over silently weakening standards.

---

# Phase 0 - Execution Gate, Baseline, And Branch

## Stage 0.1 - Confirm Authority

### Action 0.1.1 - Verify Explicit Execution Approval

Target files:

```text
none
```

Procedure:

- Confirm the Project Owner has explicitly requested execution of this
  workplan.
- If the Project Owner has only requested the workplan, do not modify release
  implementation files beyond this plan.
- Record the exact approval phrase in the implementation log created in
  Action 0.3.1.

Completion criteria:

- Execution approval is present before any implementation edit.

Stop condition:

- If approval is absent or ambiguous, stop and ask.

### Action 0.1.2 - Re-read Release Source Documents

Target files:

```text
docs/design/release_prep/01_001_public_release_preparation_plan.md
docs/prime_directive/public_release_readiness_protocol.md
docs/engineer_continuity/2026/06/12/01_001_engineering_continuity_report.md
```

Procedure:

- Read the approved release-prep plan.
- Read the public release readiness protocol.
- Read the latest engineering continuity report.
- Confirm all decisions in this workplan still match the approved plan.

Completion criteria:

- No mismatch between approved plan and implementation workplan.

Stop condition:

- If a mismatch exists, update the workplan first and ask the Project Owner to
  approve the correction.

## Stage 0.2 - Branch And Baseline

### Action 0.2.1 - Inspect Git State

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

- Baseline git state is known and recorded.

### Action 0.2.2 - Create Release-Prep Branch

Target files:

```text
none
```

Command:

```bash
git checkout -b codex/v0.1.0-release-prep
```

Procedure:

- Create a dedicated release-prep branch before implementation.
- If the branch already exists, switch to it only after checking that doing so
  will not overwrite current work.

Completion criteria:

- Work is on a dedicated release-prep branch.

Stop condition:

- If branch creation or switching would hide or overwrite user work, stop.

### Action 0.2.3 - Run Baseline Verification

Target files:

```text
none
```

Commands:

```bash
uv run pytest
uv build --out-dir /private/tmp/jet-simplex-search-baseline-build
```

Procedure:

- Run the full test suite.
- Run a temporary build.
- Record results in the release-prep implementation log.

Completion criteria:

- Baseline tests and build results are known.

Stop condition:

- If baseline tests fail, stop and reconstruct before release-prep edits.

## Stage 0.3 - Implementation Log

### Action 0.3.1 - Create Release-Prep Implementation Log

Target files:

```text
docs/design/release_prep/01_003_public_release_preparation_implementation_log.md
```

Procedure:

- Create an implementation log for this release-prep execution.
- Include:
  - approval phrase;
  - branch;
  - baseline commit;
  - baseline git status;
  - baseline test result;
  - baseline build result;
  - hard stop reminders.

Completion criteria:

- Release-prep implementation log exists before implementation edits.

---

# Phase 1 - Dependency And Package Metadata

## Stage 1.1 - Replace Local `state_collapser` Source

### Action 1.1.1 - Update `pyproject.toml` Dependency Source

Target files:

```text
pyproject.toml
uv.lock
```

Implementation:

- Replace the local editable dependency:

```toml
[tool.uv.sources]
state-collapser = { path = "../state_collapser", editable = true }
```

- With the approved GitHub tag dependency:

```toml
[tool.uv.sources]
state-collapser = { git = "https://github.com/TYLERSFOSTER/state_collapser.git", tag = "v0.7.2" }
```

- Keep the dependency name:

```toml
dependencies = [
  "state-collapser",
]
```

Commands:

```bash
uv lock
uv sync
uv run python -c "import state_collapser; print(state_collapser.__version__)"
```

Expected result:

```text
0.7.2
```

Completion criteria:

- `uv.lock` records a Git source for `state-collapser`.
- No active release configuration points to `../state_collapser`.
- Import smoke reports `0.7.2`.

Stop condition:

- If Git dependency resolution fails, stop and inspect whether the GitHub tag is
  accessible before choosing any workaround.

## Stage 1.2 - Add Package Metadata

### Action 1.2.1 - Add Project URLs

Target files:

```text
pyproject.toml
```

Implementation:

- Add:

```toml
[project.urls]
Homepage = "https://github.com/TYLERSFOSTER/jet_simplex_search"
Repository = "https://github.com/TYLERSFOSTER/jet_simplex_search"
Issues = "https://github.com/TYLERSFOSTER/jet_simplex_search/issues"
Source = "https://github.com/TYLERSFOSTER/jet_simplex_search"
```

Completion criteria:

- Built package metadata contains the approved project URLs.

### Action 1.2.2 - Add Keywords

Target files:

```text
pyproject.toml
```

Implementation:

- Add:

```toml
keywords = [
  "simplicial-complexes",
  "directed-graphs",
  "quotient-towers",
  "graph-algorithms",
  "state-collapser",
]
```

Completion criteria:

- Keywords are present in built metadata.

### Action 1.2.3 - Add Classifiers

Target files:

```text
pyproject.toml
```

Implementation:

- Add classifiers:

```toml
classifiers = [
  "Development Status :: 3 - Alpha",
  "Intended Audience :: Developers",
  "Intended Audience :: Science/Research",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Topic :: Scientific/Engineering",
  "Typing :: Typed",
]
```

Completion criteria:

- Classifiers are present in built metadata.

### Action 1.2.4 - Add Type Marker

Target files:

```text
src/jet_simplex_search/py.typed
tests/test_package.py
```

Implementation:

- Add empty `py.typed` marker.
- Add a smoke assertion that the marker exists in the package source tree or
  built wheel inspection phase.

Completion criteria:

- `Typing :: Typed` classifier has a package marker to match it.

## Stage 1.3 - Verify Metadata

### Action 1.3.1 - Build And Inspect Metadata

Target files:

```text
none
```

Commands:

```bash
uv build --out-dir /private/tmp/jet-simplex-search-metadata-build
```

Procedure:

- Build sdist and wheel.
- Inspect wheel metadata for:
  - version `0.1.0`;
  - URLs;
  - keywords;
  - classifiers;
  - license;
  - dependency on `state-collapser`.

Completion criteria:

- Metadata matches approved release decisions.

---

# Phase 2 - README And Release Notes

## Stage 2.1 - README Badges And Dependency Language

### Action 2.1.1 - Add CI And Ruff Badges

Target files:

```text
README.md
```

Implementation:

- Preserve the current logo block exactly.
- Preserve the title exactly:

```markdown
# **JET- SIMPLEX - SEARCH**
```

- Add or update badges:
  - Python `3.11 | 3.12`;
  - MIT license;
  - CI workflow badge;
  - Ruff badge;
  - pre-release status;
  - uv package manager.
- Do not add PyPI, docs-hosting, or coverage badges.

Completion criteria:

- README badges correspond to configured systems or approved static signals.

### Action 2.1.2 - Update Installation For GitHub Tag Dependency

Target files:

```text
README.md
```

Implementation:

- Remove sibling-checkout-only installation as the primary path.
- Document that `state_collapser` resolves from GitHub tag `v0.7.2`.
- Keep GitHub-only pre-release framing.
- Do not claim PyPI installation.

Completion criteria:

- README install instructions do not require hidden local paths.

## Stage 2.2 - README Known Limitations

### Action 2.2.1 - Add Concise Known Limitations Section

Target files:

```text
README.md
```

Implementation:

- Add `## Known Limitations`.
- Include:
  - pre-release API may change;
  - GitHub-only release;
  - no PyPI claim;
  - no Kan replacement yet;
  - expanded H witness assignment artifacts are deferred;
  - upstream `state_collapser` simple-reflexive tier construction mode remains
    a release blocker if not yet available in the dependency release;
  - no benchmark-superiority claim;
  - no accelerated backend claim.
- Keep section short and public-friendly.

Completion criteria:

- Known limitations are clear without burying public users in implementation
  details.

## Stage 2.3 - README Link Policy

### Action 2.3.1 - Enforce Approved README Link Decisions

Target files:

```text
README.md
```

Implementation:

- Do not link the release-prep plan from README.
- Do not add or fix README links to the engineering continuity report.
- Do not link `docs/prime_directive` from README.
- Preserve design spine links already approved for root documentation, except
  links that the Project Owner has explicitly forbidden.

Completion criteria:

- README link policy matches Workstream 6 decisions.

## Stage 2.4 - Release Notes

### Action 2.4.1 - Create `RELEASE_NOTES.md`

Target files:

```text
RELEASE_NOTES.md
```

Implementation:

- Add title:

```markdown
# Release Notes
```

- Add section:

```markdown
## v0.1.0 - GitHub Library Pre-Release
```

- Include:
  - GitHub-only library pre-release status;
  - install notes using `state_collapser` GitHub tag `v0.7.2`;
  - implemented features;
  - smoke examples and regression checks;
  - artifact support;
  - known limitations;
  - deferred work;
  - verification commands;
  - PM Abdul Malik attribution;
  - design spine links.
- Exclude:
  - PyPI claims;
  - production-ready claims;
  - benchmark-superiority claims;
  - "complete" language.

Completion criteria:

- Release notes align with README, package metadata, and approved plan.

---

# Phase 3 - Ruff, Formatting, And Docstring Quality

## Stage 3.1 - Add Ruff Tooling

### Action 3.1.1 - Add Ruff Development Dependency

Target files:

```text
pyproject.toml
uv.lock
```

Implementation:

- Add Ruff to the `dev` dependency group.
- Use `uv` to update lockfile.

Commands:

```bash
uv add --dev ruff
```

Completion criteria:

- `uv run ruff --version` succeeds.

### Action 3.1.2 - Configure Ruff

Target files:

```text
pyproject.toml
```

Implementation:

- Add Ruff configuration.
- Include baseline lint rules for:
  - pycodestyle/pyflakes;
  - import sorting;
  - bugbear-style checks if acceptable;
  - pydocstyle/docstring rules for public modules/classes/functions.
- Keep line length compatible with existing code.
- Avoid choosing rules that would force broad unrelated rewrites.

Completion criteria:

- `uv run ruff check .` runs and reports actionable output.
- `uv run ruff format --check .` runs.

## Stage 3.2 - Fix Ruff Findings

### Action 3.2.1 - Apply Formatting

Target files:

```text
src/
tests/
smoke/
scripts/
```

Commands:

```bash
uv run ruff format .
```

Procedure:

- Apply formatting.
- Inspect diffs.
- Ensure formatting does not alter public semantics.

Completion criteria:

- `uv run ruff format --check .` passes.

### Action 3.2.2 - Fix Lint Findings

Target files:

```text
src/
tests/
smoke/
scripts/
```

Commands:

```bash
uv run ruff check .
```

Procedure:

- Fix lint findings manually where needed.
- Use auto-fix only for mechanical safe changes.
- Do not weaken rules just to pass unless the rule is clearly inappropriate for
  this package.

Completion criteria:

- `uv run ruff check .` passes.

## Stage 3.3 - Public Docstring Review

### Action 3.3.1 - Identify Public Docstring Surface

Target files:

```text
src/jet_simplex_search/*.py
```

Procedure:

- Enumerate public modules, classes, functions, and methods.
- Identify missing or weak docstrings.
- Treat leading-underscore helpers as private unless they are part of the
  artifact surface or release hygiene logic.

Completion criteria:

- Public docstring gap list is known.

### Action 3.3.2 - Improve Public Docstrings

Target files:

```text
src/jet_simplex_search/*.py
```

Implementation:

- Add or improve docstrings for public APIs.
- Explain domain-specific terms:
  - directed flag simplex;
  - degeneracy;
  - frontier;
  - simplex fiber;
  - edge fiber;
  - quotient tower adapter.
- Do not claim deferred features.
- Keep docstrings concise but useful.

Completion criteria:

- Docstring-quality gate passes.
- Public API documentation is coherent for a first external reader.

---

# Phase 4 - Smoke Regression And README Tests

## Stage 4.1 - Make Smoke Outputs Testable

### Action 4.1.1 - Capture Expected Smoke Output

Target files:

```text
tests/test_smoke_scripts.py
```

Implementation:

- Add a test table mapping each smoke script to expected stdout.
- Include all current smoke scripts:
  - `smoke/smoke_001.py`;
  - `smoke/smoke_002.py`;
  - `smoke/smoke_003.py` through `smoke/smoke_016.py`.
- Use exact stdout including newlines.
- Keep expected output in the test or a stable checked-in fixture.

Completion criteria:

- Smoke output expectations are version-controlled.

### Action 4.1.2 - Execute Smoke Scripts In Pytest

Target files:

```text
tests/test_smoke_scripts.py
```

Implementation:

- Use `subprocess.run`.
- Execute scripts with the current Python interpreter.
- Set `PYTHONPATH` so the local source tree and `smoke/` imports work.
- Compare stdout exactly.
- Fail with useful diff output if a smoke table changes.

Completion criteria:

- `uv run pytest tests/test_smoke_scripts.py` passes.

## Stage 4.2 - Preserve Smoke Explanation Docs

### Action 4.2.1 - Check Smoke Markdown Coverage

Target files:

```text
tests/test_smoke_docs.py
smoke/*.md
```

Implementation:

- Add a test that each `smoke/smoke_0NN.py` from `003` through `016` has a
  matching `.md` count argument.
- Optionally check that each `.md` contains:
  - command block;
  - output block;
  - "No error found" or explicit error explanation.

Completion criteria:

- Human-readable count arguments remain paired with smoke scripts.

## Stage 4.3 - README Quick-Start Test

### Action 4.3.1 - Add README Quick-Start Regression Test

Target files:

```text
tests/test_readme_examples.py
```

Implementation:

- Add a test that programmatically executes the README quick-start graph.
- Assert the exact diagnostics mapping:

```python
{(1, 0): 2, (1, 1): 3, (1, 2): 4, (0, 0): 3, (0, 1): 6, (0, 2): 10}
```

Completion criteria:

- README quick-start behavior is tested.

---

# Phase 5 - CI And GitHub Templates

## Stage 5.1 - GitHub Actions

### Action 5.1.1 - Add CI Workflow

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

### Action 5.1.2 - Verify CI Locally Where Possible

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
uv build --out-dir /private/tmp/jet-simplex-search-ci-build
```

Completion criteria:

- Local commands match CI commands and pass.

## Stage 5.2 - GitHub Templates

### Action 5.2.1 - Add Bug Report Template

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

- Bug reports prompt users for release-relevant reproduction details.

### Action 5.2.2 - Add Feature Request Template

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

### Action 5.2.3 - Add Pull Request Template

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
  - no PyPI/benchmark/production-ready overclaim checkbox.

Completion criteria:

- PR template reinforces release discipline.

---

# Phase 6 - Release Hygiene Script

## Stage 6.1 - Implement Hygiene Script

### Action 6.1.1 - Add Script Skeleton

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
- Print clear pass/fail messages.

Completion criteria:

- Hygiene script runs from repo root.

### Action 6.1.2 - Check Local Absolute Paths

Target files:

```text
scripts/release_hygiene.py
tests/test_release_hygiene.py
```

Implementation:

- Scan public Markdown and JSON surfaces.
- Fail on machine-local absolute paths such as:
  - `/Users/`;
  - `/private/tmp/`;
  - `/private/var/`;
  - Windows drive paths if present.
- Allow paths inside fenced command examples only if intentionally allowlisted.

Completion criteria:

- Accidental local paths are caught.

### Action 6.1.3 - Check Build Outputs And Caches

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

### Action 6.1.4 - Check Large Public Artifacts

Implementation:

- Fail on tracked public files larger than `1 MB` unless allowlisted.
- Exclude `.git`.
- Print file path and size.

Completion criteria:

- Large accidental artifacts are caught.

### Action 6.1.5 - Check Broken Links

Implementation:

- Parse relative Markdown links in README and public docs.
- Fail when target file does not exist.
- Respect approved policy:
  - do not require links to continuity report;
  - do not require links to release-prep plan;
  - do not require links to `docs/prime_directive`.

Completion criteria:

- Broken links are caught without forcing forbidden links.

### Action 6.1.6 - Check Badge Claims

Implementation:

- Fail if README contains:
  - PyPI badge;
  - coverage badge;
  - docs-hosting badge;
  - CI badge without `.github/workflows/test.yml`;
  - Ruff badge without Ruff config.

Completion criteria:

- README badges correspond to configured systems.

### Action 6.1.7 - Check Dependency Source

Implementation:

- Fail if `pyproject.toml` contains:

```text
../state_collapser
```

- Pass only when `state-collapser` source uses approved GitHub tag `v0.7.2`.

Completion criteria:

- Local sibling dependency cannot survive release hygiene.

### Action 6.1.8 - Check Disallowed Claims And Public Language

Implementation:

- Fail on disallowed release claims:
  - production-ready;
  - benchmark-validated;
  - fastest;
  - PyPI install/published claim;
  - Kan implemented claim.
- Add small configurable banned-word/public-language list.
- Preserve attribution and meaning if any redaction is needed.

Completion criteria:

- Public docs remain bounded and safe to quote.

### Action 6.1.9 - Warn On Unlinked Prime Directive

Implementation:

- If `docs/prime_directive` exists and is not linked from README, print a
  warning only.
- Do not fail, because this is the approved posture.

Completion criteria:

- Approved prime-directive posture is represented.

## Stage 6.2 - Test Hygiene Script

### Action 6.2.1 - Add Unit Tests For Hygiene Checks

Target files:

```text
tests/test_release_hygiene.py
```

Implementation:

- Test pass case.
- Test local path failure.
- Test broken link failure.
- Test local `state_collapser` dependency failure.
- Test disallowed claim failure.
- Test prime directive warning does not fail.

Completion criteria:

- Hygiene script behavior is covered.

---

# Phase 7 - Security, Contribution, And Public Support Docs

## Stage 7.1 - Security Policy

### Action 7.1.1 - Add `SECURITY.md`

Target files:

```text
SECURITY.md
```

Implementation:

- State pre-release support posture.
- Give vulnerability/contact instructions appropriate for the repo.
- Say not to disclose sensitive details publicly if reporting a vulnerability.
- Avoid promising response SLAs unless approved.

Completion criteria:

- Public security reporting path exists.

## Stage 7.2 - Contribution Guide

### Action 7.2.1 - Add `CONTRIBUTING.md`

Target files:

```text
CONTRIBUTING.md
```

Implementation:

- Include setup:
  - `uv sync`;
  - `uv run pytest`;
  - `uv run ruff check .`;
  - `uv run ruff format --check .`.
- Include package scope:
  - preserve directed flag semantics;
  - preserve first-class degenerates;
  - preserve `state_collapser` tower ownership;
  - preserve PM Abdul Malik attribution.
- Include release-claim discipline:
  - no benchmark/production/PyPI claims unless true.
- Include PR expectations.

Completion criteria:

- Contributors can run local checks and understand scope.

## Stage 7.3 - Confirm Code Of Conduct Is Omitted

### Action 7.3.1 - Verify No `CODE_OF_CONDUCT.md` Is Added

Target files:

```text
none
```

Procedure:

- Confirm no `CODE_OF_CONDUCT.md` was added for `v0.1.0`.
- If one exists from prior user work, do not delete it without explicit
  instruction; record the discrepancy.

Completion criteria:

- Worktree respects approved Workstream 9 decision.

---

# Phase 8 - Packaging Content And Build Verification

## Stage 8.1 - Wheel Content Policy

### Action 8.1.1 - Verify Wheel Excludes `smoke/`

Target files:

```text
pyproject.toml
```

Procedure:

- Build wheel.
- Inspect wheel file list.
- Confirm `smoke/` is not included as package data.
- Confirm `src/jet_simplex_search/py.typed` is included.

Completion criteria:

- Wheel contains intended package files only.

### Action 8.1.2 - Verify Sdist Includes Public Source Examples

Target files:

```text
pyproject.toml
```

Procedure:

- Build sdist.
- Inspect tarball file list.
- Confirm expected files are present:
  - README;
  - LICENSE;
  - RELEASE_NOTES;
  - docs;
  - smoke source files and smoke Markdown;
  - tests if hatchling includes them under current config or if explicitly
    configured.

Completion criteria:

- Sdist is useful for GitHub source-release users.

## Stage 8.2 - Clean Wheel Install

### Action 8.2.1 - Install Built Wheel In Temporary Environment

Target files:

```text
none
```

Procedure:

- Build wheel into `/private/tmp`.
- Create clean temporary virtual environment.
- Install the wheel.
- Ensure install resolves `state_collapser` from GitHub tag `v0.7.2`.

Completion criteria:

- Wheel installs without relying on repo checkout.

### Action 8.2.2 - Run Installed Import Smoke

Command:

```bash
python -c "from jet_simplex_search import search_simplices; print(search_simplices)"
```

Completion criteria:

- Installed package imports successfully.

### Action 8.2.3 - Run README Quick-Start From Installed Wheel

Procedure:

- Run README quick-start in the clean environment.
- Confirm expected diagnostics mapping.

Completion criteria:

- Public quick-start works from installed package.

---

# Phase 9 - Final Documentation Review

## Stage 9.1 - Attribution Review

### Action 9.1.1 - Verify Abdul Malik Attribution

Target files:

```text
README.md
RELEASE_NOTES.md
docs/design/initial_design/01_001_static_tower_small_object_simplex_search.md
docs/design/initial_design/01_002_static_tower_small_object_package_blueprint.md
docs/design/initial_design/01_003_static_tower_small_object_implementation_workplan.md
```

Procedure:

- Search for attribution.
- Confirm the algorithmic content is attributed to PM Abdul Malik.
- Confirm no doc implies the implementation author invented the algorithm.

Completion criteria:

- Attribution is explicit and preserved.

## Stage 9.2 - Public Claim Review

### Action 9.2.1 - Review Bounded Claims

Target files:

```text
README.md
RELEASE_NOTES.md
docs/**/*.md
```

Procedure:

- Check for:
  - production-ready claims;
  - PyPI claims;
  - benchmark-superiority claims;
  - Kan-implemented claims;
  - complete multigraph-witness semantics claims.
- Fix any violation.

Completion criteria:

- Public docs say only what has been implemented and verified.

## Stage 9.3 - Link Review

### Action 9.3.1 - Verify Links Under Approved Policy

Target files:

```text
README.md
docs/**/*.md
```

Procedure:

- Run release hygiene broken-link check.
- Manually inspect README links.
- Confirm README does not link:
  - release-prep plan;
  - engineering continuity report;
  - `docs/prime_directive`.

Completion criteria:

- Links resolve and approved non-links remain unlinked.

---

# Phase 10 - Final Release Gate

## Stage 10.1 - Run Final Local Gate

### Action 10.1.1 - Execute Required Commands

Target files:

```text
none
```

Commands:

```bash
git status --short
uv sync
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run python scripts/release_hygiene.py --repo-root .
uv build --out-dir /private/tmp/jet-simplex-search-final-build
```

Completion criteria:

- Every command passes or any failure is documented and fixed.

### Action 10.1.2 - Run Clean Install Gate

Target files:

```text
none
```

Procedure:

- Install built wheel in clean temporary environment.
- Run import smoke.
- Run README quick-start.
- Verify dependency source.

Completion criteria:

- Clean install gate passes.

## Stage 10.2 - CI Gate

### Action 10.2.1 - Confirm GitHub Actions Passes

Target files:

```text
none
```

Procedure:

- Push branch or open PR only if approved by Project Owner.
- Confirm GitHub Actions passes for Python `3.11` and `3.12`.
- Confirm CI badge target resolves.

Completion criteria:

- CI passes on GitHub.

Stop condition:

- If pushing/opening PR is not approved, record that CI remains locally
  configured but not remotely verified.

## Stage 10.3 - Final Release Approval

### Action 10.3.1 - Prepare Final Release Summary

Target files:

```text
docs/design/release_prep/01_003_public_release_preparation_implementation_log.md
```

Procedure:

- Summarize:
  - changed files;
  - test results;
  - build results;
  - clean install results;
  - release hygiene result;
  - CI result or pending remote verification;
  - remaining hard stops.

Completion criteria:

- Project Owner has a clear release-readiness report.

### Action 10.3.2 - Stop Before Release Actions

Target files:

```text
none
```

Procedure:

- Do not tag.
- Do not upload release assets.
- Do not publish.
- Do not make repository public.
- Ask Project Owner for explicit approval if any release action is desired.

Completion criteria:

- Implementation work ends before release actions.

---

# Completion Definition

This implementation workplan is complete when:

- package dependency uses `state_collapser` GitHub tag `v0.7.2`;
- package metadata is release-ready for `v0.1.0`;
- README has approved badges, install path, Known Limitations, and bounded
  claims;
- `RELEASE_NOTES.md` exists;
- Ruff and docstring gates exist and pass;
- smoke scripts are regression-tested;
- README quick-start is tested;
- GitHub Actions workflow exists;
- issue and PR templates exist;
- release hygiene script exists and passes;
- `SECURITY.md` and `CONTRIBUTING.md` exist;
- wheel and sdist build;
- clean wheel install works;
- public docs preserve PM Abdul Malik attribution;
- final release gate is recorded in implementation log;
- no hard-stop release action has been taken without explicit Project Owner
  approval.

# Non-Goals For This Workplan

- Publishing to PyPI.
- Tagging `v0.1.0`.
- Uploading release assets.
- Making the repository public.
- Implementing Kan replacement.
- Implementing expanded H witness assignment artifacts by default.
- Implementing `state_collapser` upstream release actions without explicit
  Project Owner approval.
- Adding coverage reporting.
- Adding GitHub Pages or hosted documentation.
