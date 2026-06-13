# Updated Public Release Preparation Implementation Log

## Status

Execution log for:

```text
docs/design/release_prep/02_002_public_release_preparation_updated_implementation_workplan.md
```

Release target:

```text
v0.1.0 GitHub-only library pre-release
```

This log records preparation work only. It is not a record of tagging,
publishing, uploading release assets, making the repository public, or
publishing to PyPI.

## Approval

Project Owner approval phrase:

```text
execute `docs/design/release_prep/02_002_public_release_preparation_updated_implementation_workplan.md
```

Interpreted scope:

- Execute release-preparation work.
- Stop before hard-stop release actions:
  - no tag;
  - no release asset upload;
  - no PyPI publication;
  - no repository visibility change;
  - no GitHub release publication.

## Baseline

Branch:

```text
codex/v0.1.0-release-prep
```

Baseline commit:

```text
4085bdbdf075322553cea5a37f7d11a1a67be5f3
```

Baseline git status:

```text
clean
```

Baseline tests:

```text
uv run pytest
111 passed
```

Baseline Ruff:

```text
uv run ruff check .
All checks passed.
```

Baseline build:

```text
uv build --out-dir [temporary build directory]
Successfully built jet_simplex_search-0.1.0.tar.gz
Successfully built jet_simplex_search-0.1.0-py3-none-any.whl
```

Note:

The first sandboxed build attempt hit a local `uv` cache permission error.
The rerun with approved cache access succeeded. This was local execution
friction, not a package build failure.

## Hard Stops

Do not proceed without fresh Project Owner approval before:

- tagging `v0.1.0`;
- uploading release assets;
- publishing to PyPI;
- making the repository public;
- publishing anywhere else;
- rewriting git history;
- editing `state_collapser`;
- changing Abdullah N. Malik attribution;
- weakening the `HGraphML` boundary;
- claiming production readiness;
- claiming benchmark superiority;
- claiming Kan replacement is implemented;
- claiming neural message passing is implemented in this repo.

## Execution Notes

Work begins after this log is created.

## Work Completed

### Branch And Baseline

- Created release-prep branch:

```text
codex/v0.1.0-release-prep
```

- Confirmed baseline was clean before edits.
- Baseline checks passed:
  - `uv run pytest` -> `111 passed`;
  - `uv run ruff check .` -> passed;
  - `uv build --out-dir [temporary build directory]` -> built sdist and wheel
    after approved `uv` cache access.

### Package Metadata

- Added package keywords:
  - `simplicial-complexes`;
  - `directed-graphs`;
  - `quotient-towers`;
  - `graph-algorithms`;
  - `state-collapser`.
- Added `Source` project URL.
- Added `Intended Audience :: Developers`.
- Added `Typing :: Typed`.
- Added `src/jet_simplex_search/py.typed`.
- Extended release metadata tests to cover keywords, Source URL, typed
  classifier, and type marker.
- Verified built wheel metadata includes:
  - package name `jet-simplex-search`;
  - version `0.1.0`;
  - approved `state-collapser` Git dependency;
  - project URLs;
  - keywords;
  - classifiers.

### Public Documentation

- Added `RELEASE_NOTES.md`.
- Added `SECURITY.md`.
- Added `CONTRIBUTING.md`.
- Updated README:
  - added CI badge after adding workflow;
  - added Ruff format and release hygiene commands;
  - updated release-status section;
  - added clean limitation that neural message passing, CinchNET, and PTVNN are
    not implemented in this repo;
  - preserved Malik lineage link;
  - preserved logo and title.
- Adjusted Malik lineage language to avoid a false-positive overclaim phrase.

### GitHub Surfaces

- Added `.github/workflows/test.yml`.
- Added bug report issue template.
- Added feature request issue template.
- Added pull request template with release-claim checklist.

### Release Hygiene

- Added `scripts/release_hygiene.py`.
- Added `tests/test_release_hygiene.py`.
- Hygiene checks include:
  - strict versus warn-only documentation surfaces;
  - machine-local paths;
  - build/cache outputs;
  - generated artifact outputs;
  - large public files;
  - broken Markdown links;
  - badge claims;
  - local `state_collapser` dependency;
  - disallowed public claims;
  - Malik attribution and `HGraphML` framing;
  - obvious secrets;
  - approved `docs/prime_directive` unlinked warning.
- Current hygiene result:

```text
Release hygiene passed.
```

- Expected warnings remain for historical docs containing local command-output
  paths and for the intentionally unlinked `docs/prime_directive`.

### Smoke Regression

- Added missing smoke count arguments:
  - `smoke/smoke_001.md`;
  - `smoke/smoke_002.md`.
- Added smoke documentation coverage test.
- Added smoke stdout snapshot test that compares each public `smoke/smoke_*.py`
  script against the documented output block.

### Formatting And Docstrings

- Ran `uv run ruff format .`.
- Ruff reformatted existing source, test, and smoke files.
- Decision: `v0.1.0` keeps the current light Ruff lint gate plus manual public
  docstring review. Pydocstyle/docstring enforcement is deferred to avoid broad
  unrelated churn during release prep.
- Public API docstrings were reviewed at a high level and remain coherent for
  the first pre-release.

### Distribution Verification

- Built sdist and wheel:

```text
jet_simplex_search-0.1.0.tar.gz
jet_simplex_search-0.1.0-py3-none-any.whl
```

- Wheel inspection:
  - contains only `jet_simplex_search` package files and dist-info;
  - includes `jet_simplex_search/py.typed`;
  - excludes `smoke/`.
- Sdist inspection:
  - includes README, release notes, security policy, contribution guide, docs,
    smoke source, and smoke Markdown.
- Clean installed-wheel verification:
  - created clean temporary virtual environment;
  - installed built wheel;
  - pip resolved `state-collapser` from GitHub tag `v0.7.2` at commit
    `9c18652c6683fe9a554829459d6bdc6a9d69c728`;
  - import smoke passed;
  - README quick-start passed from outside the source checkout.

### Continuity

- Added
  `docs/engineer_continuity/2026/06/13/01_002_release_prep_execution_continuity_report.md`
  for future engineers.

## Final Verification

Final local checks:

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

Installed-wheel quick-start:

```text
{(1, 0): 2, (1, 1): 3, (1, 2): 4, (0, 0): 3, (0, 1): 6, (0, 2): 10}
{0: 3, 1: 3, 2: 1}
```

## Remaining Before Release Action

Still not performed because it requires explicit Project Owner approval or
remote GitHub state:

- no tag was created;
- no GitHub release was created;
- no release assets were uploaded;
- repository visibility was not changed;
- PyPI publication was not attempted;
- remote GitHub Actions was not verified because the branch has not been pushed.

## Current Readiness Summary

Release-prep implementation is complete through local verification.

The repository is locally ready for Project Owner review before any release
action. The next hard gate is explicit approval to push, open a PR, tag, or
publish.

## Deferred Work

- PyPI publication path.
- Benchmark suite and any benchmark-superiority claims.
- Kan replacement design and implementation.
- Expanded H witness assignment artifacts.
- Bitset/CSR/GPU/tensor/multiprocessing acceleration.
- Full HGraphML integration path.
- Hosted documentation, if desired.
- Strict pydocstyle/docstring lint gate.
