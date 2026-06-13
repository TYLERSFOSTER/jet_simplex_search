# Public Release Preparation Plan

## Status

Draft release-preparation design document for `jet_simplex_search`.

This document outlines what must be done before a public release. It is not an
approval to publish, tag, upload assets, push release branches, publish to PyPI,
or make the repository public.

## Source Of Truth Inputs

This plan is grounded in:

- `docs/prime_directive/public_release_readiness_protocol.md`
- `docs/engineer_continuity/2026/06/12/01_001_engineering_continuity_report.md`
- `docs/design/initial_design/01_004_static_tower_small_object_implementation_log.md`
- current `README.md`
- current `pyproject.toml`
- current `src/`, `tests/`, and `smoke/` directories

## Release Goal

Prepare `jet_simplex_search` for an honest public pre-release.

The public release should communicate:

- what the package does now;
- how to install and run it;
- how to verify examples and tests;
- what is intentionally deferred;
- how the package depends on `state_collapser`;
- where the mathematical and implementation design record lives;
- what claims are supported by local tests and smoke examples.

The release must not claim:

- production readiness;
- PyPI availability before publication;
- CI success before CI exists and passes;
- benchmark-validated speedups before approved benchmark evidence exists;
- implemented Kan replacement;
- complete multigraph witness-choice semantics;
- meaningful non-identity loop semantics.

## Current Repository State

Implemented:

- graph input records;
- loop normalization with one formal identity per vertex;
- directed flag simplex enumeration through `k`;
- first-class degenerate simplex records;
- cached frontier recurrence;
- static tower adapter protocol;
- real `state_collapser` `PartitionTower` adapter;
- fiber-addressed lifting;
- diagnostics;
- JSON and JSONL artifact writers;
- public `search_simplices` API;
- pytest suite;
- smoke examples through dimension `4`;
- Markdown count arguments for smoke examples.

Current verified commands recorded by continuity report:

```text
uv run pytest
58 passed
```

```text
uv build --out-dir /private/tmp/jet-simplex-search-readme-build
Successfully built jet_simplex_search-0.1.0.tar.gz
Successfully built jet_simplex_search-0.1.0-py3-none-any.whl
```

Known release blocker:

```toml
[tool.uv.sources]
state-collapser = { path = "../state_collapser", editable = true }
```

That local editable dependency is acceptable for development, but it must be
resolved before a frictionless public release.

## Hard Stop Conditions

Stop and ask the Project Owner before:

- publishing to PyPI;
- tagging a release;
- uploading release assets;
- making the GitHub repository public;
- deleting or moving raw artifacts without a verified manifest and bundle;
- rewriting git history;
- editing `state_collapser` directly;
- changing attribution for PM Abdul Malik's algorithmic contribution;
- claiming benchmark superiority, statistical significance, or production
  readiness.

## Workstream 1 - Release Scope And Versioning

### Decision

Release label:

```text
v0.1.0
```

Release channel:

```text
GitHub-only public pre-release.
```

Smoke script role:

```text
Both public examples and regression checks.
```

Release framing:

```text
Library pre-release.
```

### Tasks

- Decide release label:
  - selected: `v0.1.0`.
- Decide whether this release is:
  - selected: GitHub-only public pre-release.
- Decide whether smoke scripts are public examples, regression checks, or both.
  - selected: both public examples and regression checks.
- Decide whether the release target is "research pre-release" or "library
  pre-release".
  - selected: library pre-release.

### Completion Criteria

- `pyproject.toml` version matches the chosen release label.
- README release-status language matches the chosen scope.
- Changelog/release notes use the same release label.

## Workstream 2 - Dependency Strategy

### Decision

Use the actual GitHub release tag for `state_collapser`, not the local editable
sibling path, for the `v0.1.0` GitHub-only pre-release.

Target tag verified from the local `state_collapser` checkout:

```text
v0.7.2
```

Intended `uv` source form:

```toml
[tool.uv.sources]
state-collapser = { git = "https://github.com/TYLERSFOSTER/state_collapser.git", tag = "v0.7.2" }
```

### Current Problem

`jet_simplex_search` depends on `state_collapser`, but the current development
configuration uses a local editable sibling path.

### Options

Option A: publish or otherwise release `state_collapser` first.

- Best for normal package installation.
- Allows `jet_simplex_search` to declare a regular version constraint.
- Requires `state_collapser` release readiness.

Option B: document sibling-checkout installation for a GitHub-only pre-release.

- Fastest honest release path.
- README already describes this pattern.
- Not suitable for smooth PyPI consumption.

Option C: use a direct Git dependency.

- Avoids PyPI dependency publication.
- Can be fragile for long-term reproducibility.
- May not be appropriate for final public packaging.
- Selected for `v0.1.0` as a GitHub release-tag dependency.

### Tasks

- Decide dependency route.
  - selected: direct GitHub release tag for `state_collapser` `v0.7.2`.
- Replace local editable source if moving beyond local-development release.
- Pin or bound the supported `state_collapser` version.
  - selected: pin to Git tag `v0.7.2` for this pre-release.
- Verify fresh environment install from the documented instructions.

### Completion Criteria

- A new user can follow README installation steps without hidden local paths.
- `uv sync` works from a clean checkout.
- `state_collapser` dependency state is documented in README and release notes.

## Workstream 3 - Package Metadata

### Decision

Approved package metadata updates for `v0.1.0`:

- keep package version as `0.1.0`;
- use GitHub tag `v0.1.0`;
- add project URLs for Homepage, Repository, Issues, and Source;
- add package keywords:
  - `simplicial-complexes`;
  - `directed-graphs`;
  - `quotient-towers`;
  - `graph-algorithms`;
  - `state-collapser`;
- use classifier `Development Status :: 3 - Alpha`;
- include developer and science/research audience classifiers;
- include MIT license classifier;
- include Python `3`, `3.11`, and `3.12` classifiers;
- include `Topic :: Scientific/Engineering`;
- include `Typing :: Typed`;
- add `RELEASE_NOTES.md` for `v0.1.0`.

### Tasks

- Add `project.urls`:
  - Homepage;
  - Repository;
  - Issues;
  - Documentation if applicable.
  - Source.
- Add Python package classifiers if publishing to PyPI.
  - approved for GitHub pre-release metadata as listed above.
- Confirm `license` metadata is accepted by the intended build/publish target.
- Confirm `requires-python` range.
- Decide whether to expose any optional dependency groups beyond `dev`.
- Add `CHANGELOG.md` or `RELEASE_NOTES.md`.
  - selected: `RELEASE_NOTES.md`.
- Decide whether `smoke/` should be included in sdist/wheel or remain
  repository-only examples.

### Completion Criteria

- `uv build` produces a source distribution and wheel.
- Built package metadata contains correct project URLs and license information.
- README renders acceptably as the long description if publishing.

## Workstream 4 - CI And Badges

### Decision

Add CI, Ruff, and docstring-quality gates for `v0.1.0`.

Approved badge posture:

- add a GitHub Actions CI badge now, as part of adding the workflow;
- add a Ruff badge now, as part of adding Ruff configuration;
- keep no coverage badge until coverage is actually configured and reported;
- keep no PyPI badge for the GitHub-only pre-release.

Approved CI/tooling posture:

- add `.github/workflows/test.yml`;
- run on pushes and pull requests to `main`;
- test Python `3.11` and `3.12`;
- install dependencies with `uv`;
- use the GitHub release-tag dependency for `state_collapser` `v0.7.2`;
- run `uv run pytest`;
- run `uv build`;
- add Ruff for linting and formatting;
- run `uv run ruff check .`;
- run `uv run ruff format --check .`;
- add a docstring-quality check before release.

Docstring standard:

- public modules, public classes, and public functions should have clear
  docstrings;
- docstrings should explain domain meaning where names alone are insufficient;
- docstrings should avoid claiming deferred features;
- docstring tooling should be configured so obvious missing public docstrings
  fail before release.

### Current State

README has honest static badges for:

- Python support;
- MIT license;
- pytest;
- pre-release status;
- uv.

There is no CI workflow yet. The CI badge is approved as a target, but the
workflow must be added and verified before release.

### Tasks

- Add GitHub Actions workflow for tests.
- Test on Python `3.11` and `3.12`.
- Decide whether to test with local sibling `state_collapser`, Git dependency,
  or published dependency.
  - selected: GitHub release-tag dependency for `state_collapser` `v0.7.2`.
- Add build verification job.
- Add README CI badge as part of the workflow addition.
- Add Ruff to development tooling.
- Add Ruff badge to README.
- Add Ruff lint check to CI.
- Add Ruff format check to CI.
- Add docstring-quality tooling or Ruff docstring rules.
- Review and improve public Python docstrings.
- Consider adding coverage only after coverage is measured and configured.

### Completion Criteria

- GitHub Actions passes on the release branch.
- Ruff lint passes.
- Ruff format check passes.
- Public docstring quality gate passes.
- README badges reflect actual public signals.
- No badge claims CI, coverage, PyPI, or docs status before those systems exist.

## Workstream 5 - Test And Smoke Verification

### Decision

Approved verification posture for `v0.1.0`:

- smoke scripts are real regression tests, not only examples;
- add a pytest smoke test that runs each `smoke/smoke_*.py`;
- compare smoke stdout against expected snapshots embedded in tests or a stable
  checked-in fixture;
- keep each smoke `.md` file as the human-readable count argument;
- add a README quick-start test;
- run unit tests, integration tests, smoke snapshot tests, and README example
  tests in CI.

### Tasks

- Run full suite:

```bash
uv run pytest
```

- Run real adapter integration suite:

```bash
uv run pytest tests/integration/test_state_collapser_static_tower.py
```

- Run all smoke scripts:

```bash
for file in smoke/smoke_*.py; do uv run python "$file"; done
```

- Review smoke Markdown count arguments.
- Decide whether smoke outputs should become snapshot tests.
  - selected: yes, smoke outputs become regression snapshots.
- Add tests for any public README snippets that are not currently covered.
  - selected: add README quick-start test.
- Add smoke/README verification to CI.

### Completion Criteria

- Tests pass locally.
- Smoke scripts pass locally.
- Smoke count arguments match current outputs.
- Smoke snapshot tests pass.
- README quick-start test passes.
- Any failing smoke case is documented as an error rather than explained away.

## Workstream 6 - Documentation

### Decision

Approved documentation posture for `v0.1.0`:

- do not fix or add README links to the engineering continuity report;
- do not link this release-prep plan from the README;
- keep `docs/prime_directive` in the repository;
- do not link `docs/prime_directive` from root documentation;
- add a shorter README "Known Limitations" section separate from release
  status;
- preserve PM Abdul Malik attribution in README and design docs;
- ensure README examples are runnable.

### Current Documentation

- README is professionalized for pre-release.
- Design spine exists under `docs/design/initial_design`.
- Engineering continuity report exists under `docs/engineer_continuity`.
- Smoke examples include count arguments.

### Tasks

- Fix README links to point to the actual continuity report path.
  - selected: no; do not add or fix root README continuity-report links.
- Add release-prep document link to README or design index if desired.
  - selected: no; do not link release-prep plan from README.
- Add a concise public "Known limitations" section if README release status is
  too long.
  - selected: yes; add concise README "Known Limitations" section.
- Ensure README examples are runnable from a clean checkout.
  - selected: yes.
- Ensure docs preserve PM Abdul Malik attribution.
  - selected: yes.
- Decide whether `docs/prime_directive` should be public-facing or internal.
  - selected: keep in repo, but do not link from root documentation.
- If public, make sure its repository-specific names and examples are
  appropriate for this repo.

### Completion Criteria

- All README links resolve.
- Public docs distinguish implemented behavior from deferred work.
- Public docs do not rewrite design history into a fake clean story.

## Workstream 7 - Release Hygiene

### Decision

Approved release hygiene posture for `v0.1.0`:

- add `scripts/release_hygiene.py`;
- keep the expected command:

```bash
uv run python scripts/release_hygiene.py --repo-root .
```

- fail on machine-local absolute paths in public Markdown and JSON surfaces;
- fail on tracked build outputs such as `dist/`, `.pytest_cache/`,
  `.ruff_cache/`, and `*.egg-info`;
- fail on tracked public artifacts larger than `1 MB` unless explicitly
  allowlisted;
- fail on broken relative links in README and public docs;
- fail on README links to files that do not exist;
- warn, not fail, if `docs/prime_directive` is present but unlinked;
- fail if README has CI, PyPI, coverage, or docs badges that do not correspond
  to configured systems;
- fail if `pyproject.toml` still points `state-collapser` at
  `../state_collapser`;
- fail if README contains disallowed public claims such as production-ready or
  benchmark-validated;
- include a configurable profanity/public-language check using a small explicit
  banned-word list.

### Required Check

The prime-directive release protocol expects:

```bash
uv run python scripts/release_hygiene.py --repo-root .
```

That script does not currently appear in the known package surface.

### Tasks

- Add or adapt `scripts/release_hygiene.py`.
- Check public tracked docs for raw profanity.
  - selected: configurable explicit banned-word list.
- Check public Markdown and readout surfaces for machine-local absolute paths.
- Check for tracked build outputs or local byproducts.
- Check for large raw artifact directories that should be release assets.
  - selected: fail above `1 MB` unless explicitly allowlisted.
- Check for stale public entry points.
- Check for broken relative links in README and docs.
- Check for untracked files that are needed for README rendering, such as logo
  assets.
- Check README badge claims against configured systems.
- Check `state_collapser` dependency is not a local sibling path.
- Check README avoids disallowed public-release claims.

### Completion Criteria

- Release hygiene command exists.
- Release hygiene command passes.
- Any intentional exception is documented.

## Workstream 8 - Artifact And Example Policy

### Decision

Approved artifact/example policy for `v0.1.0`:

- keep all `smoke/*.py` files in git;
- keep all `smoke/*.md` count arguments in git;
- treat `smoke/` as source-only public examples and regression material;
- do not commit generated `readout_source.json`, JSONL tables, or artifact
  directories for `v0.1.0`;
- do not include temporary build output, raw run trees, or event-level traces;
- release hygiene should fail on accidental generated artifacts outside
  explicitly approved paths;
- do not include `smoke/` as wheel package data unless separately approved.

### Tasks

- Decide whether generated artifact examples belong in git.
  - selected: no generated artifact examples for `v0.1.0`.
- Keep compact public examples and manifests in git.
  - selected: source smoke examples and Markdown explanations only.
- Move large raw run trees or event-level traces to release assets if any are
  created.
- Generate a release asset manifest before removing any raw artifact from git.
- Do not include temporary build directories.

### Completion Criteria

- No large accidental artifacts are tracked.
- Public examples are compact and reproducible.
- Release assets, if any, have a manifest.

## Workstream 9 - Security, License, And Public Safety

### Decision

Approved security/license posture for `v0.1.0`:

- keep the existing MIT license;
- add `SECURITY.md` with a simple vulnerability/contact policy;
- add lightweight `CONTRIBUTING.md`;
- do not add `CODE_OF_CONDUCT.md` for `v0.1.0`;
- include public-safety hygiene checks for secrets, tokens, private absolute
  paths, and generated credentials;
- keep `docs/prime_directive` in the repository but unlinked from root docs.

### Tasks

- Confirm MIT license remains intended.
  - selected: yes, keep MIT.
- Confirm copyright holder text.
- Add `SECURITY.md` if public users are expected to report vulnerabilities.
  - selected: yes.
- Add `CONTRIBUTING.md` if external contributions are invited.
  - selected: yes, lightweight contribution guidance.
- Add `CODE_OF_CONDUCT.md` only if the Project Owner wants a public community
  governance surface.
  - selected: no for `v0.1.0`.
- Confirm no secrets, tokens, private paths, or private data are present.

### Completion Criteria

- License is clear.
- Public issue/contribution expectations are clear or intentionally omitted.
- No private operational material leaks into public release surfaces.

## Workstream 10 - Build And Install Verification

### Decision

Approved build/install verification for `v0.1.0`:

- run `uv build`;
- inspect both source distribution and wheel;
- create a clean temporary environment;
- install from the built wheel, not from the repository checkout;
- verify `from jet_simplex_search import search_simplices`;
- run README quick-start from the clean installed wheel environment;
- verify installed dependency resolution uses `state_collapser` from GitHub tag
  `v0.7.2`, not `../state_collapser`;
- verify `smoke/` is not included in the wheel unless separately approved;
- verify the source distribution includes expected docs and smoke source files;
- include these checks in the final release gate.

### Tasks

- Build package:

```bash
uv build
```

- Install built wheel into a clean temporary environment.
  - selected: clean install must use the built wheel, not repo checkout.
- Run a minimal import smoke from the installed wheel:

```bash
python -c "from jet_simplex_search import search_simplices; print(search_simplices)"
```

- Run README quick start from the clean environment.
- Verify installed `state_collapser` comes from GitHub tag `v0.7.2`.
- Verify sdist contains required files.
- Verify wheel contains only intended package files.
  - selected: `smoke/` should not be included in wheel unless separately
    approved.

### Completion Criteria

- Source distribution builds.
- Wheel builds.
- Installed package imports.
- README example works in a clean environment.
- Dependency source is not local sibling path.
- Wheel contents exclude unapproved example/smoke files.
- Source distribution contains expected public docs and smoke source examples.

## Workstream 11 - GitHub Repository Preparation

### Decision

Approved GitHub repository preparation for `v0.1.0`:

- repository URL:

```text
https://github.com/TYLERSFOSTER/jet_simplex_search
```

- default branch: `main`;
- add GitHub Actions workflow from Workstream 4;
- add issue templates:
  - bug report;
  - feature request;
- add pull request template with:
  - summary;
  - tests run;
  - release-claim checklist;
- set repository description:

```text
Quotient-tower accelerated search for directed flag simplices in sparse graphs.
```

- add repository topics:
  - `python`;
  - `graph-algorithms`;
  - `directed-graphs`;
  - `simplicial-complexes`;
  - `quotient-towers`;
  - `state-collapser`;
- do not add GitHub Pages for `v0.1.0`;
- add CI badge once workflow file exists;
- do not add docs-hosting badge.

### Tasks

- Confirm remote URL and repository name.
  - selected: `https://github.com/TYLERSFOSTER/jet_simplex_search`.
- Confirm default branch.
  - selected: `main`.
- Add or verify issue template if desired.
  - selected: bug report and feature request templates.
- Add or verify PR template if desired.
  - selected: summary, tests run, release-claim checklist.
- Add repository description and topics.
  - selected: description and topics listed above.
- Add README badges only for systems that actually exist.
- Decide whether GitHub Pages or hosted docs are in scope.
  - selected: no GitHub Pages for `v0.1.0`.

### Completion Criteria

- Repository landing page is coherent.
- README renders with logo assets.
- Issues and PRs have the intended public posture.

## Workstream 12 - Release Notes

### Decision

Approved release-notes structure for `v0.1.0`:

- create `RELEASE_NOTES.md`;
- title:

```markdown
# Release Notes
```

- first release section:

```markdown
## v0.1.0 - GitHub Library Pre-Release
```

- include:
  - status as GitHub-only library pre-release;
  - installation notes, including `state_collapser` GitHub tag `v0.7.2`;
  - implemented features;
  - smoke examples and regression checks;
  - artifact support;
  - known limitations;
  - deferred work;
  - verification commands;
  - attribution to PM Abdul Malik;
  - no PyPI claim;
  - no benchmark claim;
  - links to design spine.

Approved wording principle:

- keep release notes short, factual, and bounded;
- avoid "fastest", "production-ready", "complete", or benchmark-superiority
  language.

### Tasks

- Write release notes for the first public pre-release.
- Include:
  - what works;
  - what is deferred;
  - how to install;
  - how to run tests;
  - known dependency constraints;
  - attribution;
  - no benchmark-overclaim language.
- Link to design spine and smoke examples.
- Avoid PyPI claims.
- Avoid production-ready or benchmark-superiority language.

### Completion Criteria

- Release notes are reviewed before tagging or publishing.
- Release notes align with README and package metadata.

## Workstream 13 - Final Release Gate

### Decision

Approved final release gate for `v0.1.0`.

Before release, verify:

- `git status --short` is understood and contains no accidental changes.
- `pyproject.toml` uses the `state_collapser` GitHub tag `v0.7.2`.
- `uv sync` works in a clean checkout.
- `uv run ruff check .` passes.
- `uv run ruff format --check .` passes.
- docstring-quality gate passes.
- `uv run pytest` passes.
- smoke snapshot tests pass.
- README quick-start test passes.
- all smoke scripts run successfully.
- smoke scripts pass.
- release hygiene passes.
- README links resolve.
- `uv build` succeeds.
- built wheel imports in a clean environment.
- installed-wheel README quick-start succeeds.
- wheel excludes `smoke/`.
- source distribution includes expected docs and smoke source examples.
- `RELEASE_NOTES.md` exists and matches `v0.1.0`.
- GitHub Actions passes on `main` or release branch.
- README badges correspond to real configured systems.
- PM Abdul Malik attribution is present.
- no PyPI, production-ready, or benchmark-superiority claims are present.
- dependency strategy is explicit.
- public claims are bounded.
- Project Owner explicitly approves the release action.

Hard stop still applies before:

- tagging `v0.1.0`;
- uploading release assets;
- making the repository public;
- publishing anywhere.

## Suggested Execution Order

1. Fix documentation links and continuity report location references.
2. Decide dependency strategy for `state_collapser`.
3. Add package metadata.
4. Add release hygiene script.
5. Add CI.
6. Run tests and smoke scripts.
7. Verify clean install and build artifacts.
8. Write release notes.
9. Review README and public docs.
10. Ask Project Owner for explicit approval before any publishing, tagging,
    asset upload, or public visibility change.

## Open Questions For Project Owner

- Is the first public release GitHub-only, PyPI, or both?
- Should `state_collapser` be released first?
- Should `smoke/` be public examples, tests, or internal validation material?
- Should `docs/prime_directive` ship publicly in this repository?
- Should the first release be `0.1.0`, `0.1.0a1`, or another version?
- Do we want external contributions immediately, or should contribution docs
  wait?
- Do we want CI before making the repo public, or only before tagging a
  release?
