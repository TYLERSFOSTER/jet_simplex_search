# Public Release Readiness Protocol

## Status

Prime-directive adjunct for preparing `big_boy_benchmarking` public releases.

This document is directed to future Embedded Engineering Consultants working in
this repository.

## Core Rule

Public release work must preserve the open-lab engineering record while making
the current public tree navigable, bounded, and safe to quote.

Do not rewrite design history into a fake clean story.

Do not publish stale public entry points.

Do not invent Project Owner turns.

## Current Beta Framing

Current component:

```text
Big Boy Calibration / Smoke
```

Future component:

```text
Benchmarking
```

The current beta may claim calibration/smoke evidence. It must not claim final
benchmark victory, broad tower superiority, or statistical significance unless
a later approved evaluation supports that claim.

## Public Hygiene Requirements

Before public release, run:

```bash
uv run python scripts/release_hygiene.py --repo-root .
```

The check should fail on:

- raw profanity in public tracked docs;
- machine-local absolute paths in public Markdown or readout source surfaces;
- tracked local/build byproducts;
- large raw artifact files that should be externalized;
- ambiguous old readout commands;
- generated readout placeholders that are not labeled as intentional public
  clarification space.

Use `[XXX]` for public profanity redaction. Preserve attribution and meaning.

## Artifact Policy

Keep these in git:

- public readout READMEs;
- compact result summaries;
- badges;
- methods;
- runbooks;
- artifact indexes;
- root `readout_source.json` files;
- release asset manifests.

Move these to release assets when preparing the public beta:

- raw run trees;
- large event-level traces;
- large nested artifact directories;
- per-step and per-action traces;
- large copied upstream artifacts.

Do not remove raw artifacts from git until a local release asset bundle and
manifest have been generated and verified.

## Stop Conditions

Stop before:

- rewriting git history;
- deleting artifacts without a verified bundle;
- moving or deleting the root TeX paper;
- editing `state_collapser` directly;
- publishing to PyPI;
- tagging a release;
- uploading release assets;
- making the GitHub repository public.

