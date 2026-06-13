# Release Prep Execution Continuity Report

## Scope

This report covers execution of:

```text
docs/design/release_prep/02_002_public_release_preparation_updated_implementation_workplan.md
```

Branch:

```text
codex/v0.1.0-release-prep
```

Baseline commit:

```text
4085bdbdf075322553cea5a37f7d11a1a67be5f3
```

Release target:

```text
v0.1.0 GitHub-only library pre-release
```

No release action was performed. No tag, GitHub release, release asset upload,
repository visibility change, or PyPI publication was attempted.

## What Changed

Release documentation:

- Added `RELEASE_NOTES.md`.
- Added `SECURITY.md`.
- Added `CONTRIBUTING.md`.
- Updated README with:
  - CI badge;
  - release hygiene command;
  - Ruff format command;
  - updated release status;
  - neural-message-passing limitation and `HGraphML` boundary.
- Adjusted Malik lineage wording to avoid a public overclaim phrase.

Package metadata:

- Added package keywords.
- Added `Source` project URL.
- Added `Intended Audience :: Developers`.
- Added `Typing :: Typed`.
- Added `src/jet_simplex_search/py.typed`.
- Extended release metadata tests.

GitHub release-prep surfaces:

- Added `.github/workflows/test.yml`.
- Added bug report issue template.
- Added feature request issue template.
- Added pull request template.

Release hygiene:

- Added `scripts/release_hygiene.py`.
- Added `tests/test_release_hygiene.py`.
- Hygiene script distinguishes strict public surfaces from warn-only historical
  logs.
- It checks local paths, generated artifacts, large files, broken links, badge
  claims, dependency source, public overclaims, Malik attribution, `HGraphML`
  framing, obvious secrets, and the approved unlinked prime-directive posture.

Smoke regression:

- Added `smoke/smoke_001.md`.
- Added `smoke/smoke_002.md`.
- Added `tests/test_smoke_docs.py`.
- Added `tests/test_smoke_scripts.py`.
- All public `smoke/smoke_*.py` scripts now have documented outputs and are
  tested against those outputs.

Formatting:

- Ran `uv run ruff format .`.
- Existing source, tests, and smoke files were mechanically reformatted.
- Tests passed after formatting.

Implementation log:

- Added
  `docs/design/release_prep/02_003_public_release_preparation_updated_implementation_log.md`
  with baseline, work completed, final verification, and remaining hard stops.

## Verification

Final local verification:

```text
uv lock --check
passed after approved uv cache access
```

```text
uv sync
passed
```

```text
uv run ruff check .
All checks passed.
```

```text
uv run ruff format --check .
63 files already formatted
```

```text
uv run pytest
137 passed
```

```text
uv run python scripts/release_hygiene.py --repo-root .
Release hygiene passed with expected warnings only
```

```text
uv build --out-dir [temporary build directory]
Successfully built source distribution and wheel after approved uv cache access
```

Clean wheel install:

- Installed the built wheel into a clean temporary virtual environment.
- `pip` resolved `state-collapser` from GitHub tag `v0.7.2`.
- Installed `state-collapser 0.7.2`.
- `from jet_simplex_search import search_simplices` succeeded outside the
  source checkout.
- README quick-start succeeded outside the source checkout.

README quick-start output from installed wheel:

```text
{(1, 0): 2, (1, 1): 3, (1, 2): 4, (0, 0): 3, (0, 1): 6, (0, 2): 10}
{0: 3, 1: 3, 2: 1}
```

Distribution inspection:

- Wheel includes `jet_simplex_search/py.typed`.
- Wheel excludes `smoke/`.
- Sdist includes public docs and smoke source/examples.

## Expected Release Hygiene Warnings

Release hygiene currently passes with warnings for:

- historical release-prep docs containing local temporary command paths;
- historical engineering continuity reports containing local temporary command
  paths;
- `docs/prime_directive` being present but intentionally unlinked from README.

These are expected under the approved strict/warn-only hygiene scope.

## Still Pending

Hard-stop items still require Project Owner approval:

- pushing the branch;
- opening a PR;
- tagging `v0.1.0`;
- uploading release assets;
- creating or publishing a GitHub release;
- making the repository public;
- publishing to PyPI.

Remote state still pending:

- GitHub Actions has not run remotely because the branch has not been pushed.

Deferred beyond `v0.1.0`:

- PyPI publication path;
- benchmark suite;
- Kan replacement;
- expanded H witness assignment artifacts;
- acceleration backends;
- HGraphML integration path;
- hosted docs;
- strict pydocstyle/docstring linting.

## Next Recommended Step

Review the diff on `codex/v0.1.0-release-prep`. If approved, push the branch and
let GitHub Actions verify the workflow before any tag or release action.
