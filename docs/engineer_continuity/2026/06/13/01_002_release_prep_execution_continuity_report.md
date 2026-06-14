# Release Prep And Public Release Continuity Report

## Scope

This report originally covered execution of:

```text
docs/design/release_prep/02_002_public_release_preparation_updated_implementation_workplan.md
```

It is now updated through the public `v0.1.0` release and the immediately
following discoverability/README/CI polish commits on `main`.

Release target:

```text
v0.1.0 GitHub library pre-release
```

Original release-prep branch:

```text
codex/v0.1.0-release-prep
```

Original release-prep baseline:

```text
4085bdbdf075322553cea5a37f7d11a1a67be5f3
```

Current `main` at this update:

```text
a84b8e95d59b1842a917203f40ed62379b658729
```

Current `origin/main` at this update:

```text
a84b8e95d59b1842a917203f40ed62379b658729
```

Working tree state before this report update:

```text
clean
```

## Executive Status

The package has moved from local release preparation to a public GitHub
`v0.1.0` release with attached wheel and source distribution.

Important distinction:

```text
v0.1.0 tag/release assets point at a9304ef
current main points at a84b8e9
```

So the released `v0.1.0` artifacts do not include the later root `llms.txt`,
final README badge polish, or workflow display-name cleanup. Those changes are
already on `main` and should be included in the next patch release if the
released artifact itself needs them.

Do not silently retag `v0.1.0`. If Project Owner wants the post-tag
discoverability polish inside a released artifact, create a new patch release
such as `v0.1.1`.

## Public Release State

Annotated tag:

```text
v0.1.0
```

Local tag target:

```text
a9304efa502646e2dcb9cc572194095f186ee877
```

Remote tag object:

```text
3cb03e69a07c955e2008e9548d791ab1c13d8906
```

Remote tag dereferenced commit:

```text
a9304efa502646e2dcb9cc572194095f186ee877
```

GitHub release URL:

```text
https://github.com/TYLERSFOSTER/jet_simplex_search/releases/tag/v0.1.0
```

GitHub release title:

```text
jet_simplex_search v0.1.0 - Static tower simplex search pre-release
```

Published timestamp:

```text
2026-06-13T22:57:02Z
```

GitHub release flags observed through `gh release view`:

```text
isDraft: false
isPrerelease: false
```

This is a release-state mismatch with the intended wording. The title and
documentation call this a pre-release, but the GitHub release object is not
currently marked as a pre-release. Correcting that is a GitHub release metadata
edit, not a code change.

Attached assets:

```text
jet_simplex_search-0.1.0-py3-none-any.whl
sha256:8c8b76d681b981f2218e0a5bc7549d2966691cda80e9f5a01ddc1b8cdab622b7
size: 35972 bytes
```

```text
jet_simplex_search-0.1.0.tar.gz
sha256:330bd79268c006be5d0395f353ea04154d2cadd3473ee7e6cfa96b4c992457fa
size: 327775 bytes
```

## What Changed During Release Prep

Release documentation:

- Added `RELEASE_NOTES.md`.
- Added `SECURITY.md`.
- Added `CONTRIBUTING.md`.
- Updated README with:
  - release hygiene command;
  - Ruff format command;
  - updated release status;
  - neural-message-passing limitation and `HGraphML` boundary;
  - Malik lineage section and link.
- Adjusted Malik lineage wording to avoid a public overclaim phrase.

Package metadata:

- Added package keywords.
- Added `Source` project URL.
- Added `Intended Audience :: Developers`.
- Added `Typing :: Typed`.
- Added `src/jet_simplex_search/py.typed`.
- Extended release metadata tests.
- Confirmed the public dependency uses:

```text
state-collapser @ git+https://github.com/TYLERSFOSTER/state_collapser.git@v0.7.2
```

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

## Release Verification

Final local release-prep verification before tag:

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

Manual installed-wheel smoke after tag/build:

```text
from jet_simplex_search import search_simplices
```

printed a function object successfully from outside the repository checkout.

## Remote CI State

Latest observed GitHub Actions run on current `main`:

```text
displayTitle: README
headSha: a84b8e95d59b1842a917203f40ed62379b658729
status: completed
conclusion: success
createdAt: 2026-06-14T00:31:48Z
url: https://github.com/TYLERSFOSTER/jet_simplex_search/actions/runs/27483568022
```

Recent post-release polish runs also passed:

```text
7f27609 TEST to CI -> success
33d3d20 README badges fix -> success
3fba4d3 llms.txt -> success
```

Historical caveat:

```text
a9304ef v0.1.0 release prep -> remote CI failure
```

That run passed dependency install, Ruff, Ruff format, and pytest on both
Python 3.11 and Python 3.12, then failed at the release-hygiene step. The
failure was superseded by the later `llms.txt` commit, which also corrected a
release-hygiene false positive in Windows-path detection and added a regression
test. Current `main` release hygiene passes.

## Post-Tag Main Commits

The following commits are on `main` after the `v0.1.0` tag:

```text
3fba4d3 llms.txt
33d3d20 README badges fix
7f27609 TEST to CI
a84b8e9 README
```

### `3fba4d3 llms.txt`

- Added root `llms.txt`.
- Mapped the package for humans, LLMs, and retrieval systems.
- Routed readers to README, release notes, contributing/security docs,
  implementation modules, smoke examples, design/provenance docs, and tests.
- Stated boundaries:
  - `state_collapser` owns quotient-tower construction;
  - `jet_simplex_search` owns simplex enumeration, H-to-G skeletonization,
    lifting, H-lift counts, diagnostics, and artifacts;
  - `HGraphML` is separate;
  - Kan replacement and neural message passing are not implemented here.
- Added `llms.txt` to strict release-hygiene scanning.
- Narrowed the Windows absolute-path regex in `scripts/release_hygiene.py` so
  normal smoke-test source strings containing escaped Markdown text-block
  markers are not mistaken for machine-local paths.
- Added a regression test for that false positive.

### `33d3d20 README badges fix`

- Converted the README badge stack from Markdown badges to an HTML badge row
  modeled on `state_collapser`.
- Initially included more badges than desired.

### `7f27609 TEST to CI`

- Changed `.github/workflows/test.yml` display name from `Test` to `CI`.
- The workflow file remains named `test.yml`; the GitHub badge display name is
  controlled by the YAML `name` field.

### `a84b8e9 README`

- Finalized badge presentation for this repo:
  - left-aligned;
  - same functional badge set as `state_collapser`;
  - CI;
  - Python 3.11/3.12;
  - GitHub release;
  - MIT license;
  - Ruff.
- Removed the extra uv and status badges from the README badge row.

## Current Public Documentation Shape

Current root public surfaces:

- `README.md`
- `llms.txt`
- `RELEASE_NOTES.md`
- `SECURITY.md`
- `CONTRIBUTING.md`
- `LICENSE`
- `.github/workflows/test.yml`
- `.github/ISSUE_TEMPLATE/`
- `.github/pull_request_template.md`

Current README boundaries:

- `jet_simplex_search` is a library pre-release.
- It implements directed simplex search, degenerate simplices, static quotient
  tower lifting, H-to-G skeletonization, and compressed H-lift counts.
- It preserves Abdullah N. Malik attribution and links the detailed lineage
  document.
- It does not claim Kan replacement, neural message passing, CinchNET, PTVNN,
  benchmark superiority, or production readiness.
- It links `HGraphML` as the separate graph message-passing branch.

## Expected Release Hygiene Warnings

Release hygiene currently passes with warnings for:

- historical release-prep docs containing local temporary command paths;
- historical engineering continuity reports containing local temporary command
  paths;
- `docs/prime_directive` being present but intentionally unlinked from README.

These are expected under the approved strict/warn-only hygiene scope.

## Current Open Items

Release metadata:

- The GitHub release is titled as a pre-release but is not marked
  `isPrerelease: true`.
- Decide whether to edit the GitHub release metadata to mark it as a
  pre-release.

Version inclusion:

- `llms.txt`, final badge polish, and the `CI` display-name cleanup are on
  `main` but not in the `v0.1.0` tag/artifacts.
- If those should be in a released artifact, create a new patch release rather
  than rewriting `v0.1.0`.

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

Do not retag `v0.1.0`.

Recommended next maintenance move:

1. Edit the existing GitHub `v0.1.0` release to mark it as a pre-release if the
   Project Owner wants GitHub metadata to match the release framing.
2. Leave `v0.1.0` tag and assets as historical release artifacts.
3. Treat current `main` as the starting point for `v0.1.1` if the
   discoverability polish should be included in a tagged release.
