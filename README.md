<p align="left">
  <picture>
    <source srcset="assets/images/logo_dark.svg" media="(prefers-color-scheme: dark)">
    <source srcset="assets/images/logo_light.svg" media="(prefers-color-scheme: light)">
    <img src="assets/images/logo_light.svg" alt="jet_simplex_search" width="340">
  </picture>
</p>

# **JET- SIMPLEX - SEARCH**

[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-pytest-blue.svg)](tests)
[![Status](https://img.shields.io/badge/status-pre--release-orange.svg)](#release-status)
[![Package Manager](https://img.shields.io/badge/package%20manager-uv-6f42c1.svg)](https://docs.astral.sh/uv/)

`jet_simplex_search` is a Python package for finding directed flag simplices in
sparse graphs. It emits degenerate simplices as first-class records and uses
static quotient towers from [`state_collapser`](https://github.com/TYLERSFOSTER/state_collapser)
to restrict higher-tier search to fibers over known downstairs simplices.

The package is currently pre-release software. The core implementation is in
place, but public packaging, CI, and release hygiene are still being prepared.

## Why This Exists

Given a directed graph `G` and a dimension bound `k`, the package enumerates
directed simplices through dimension `k`. A simplex is treated as a directed
flag object: every required face edge must exist. For example, a path
`a -> b -> c` is not a 2-simplex unless the face edge `a -> c` also exists.

Degenerate simplices are not collapsed away. Words such as `(a, a, b)` and
`(a, b, b)` are valid degree-2 simplices over the edge `a -> b`, and they
remain distinct records with their full arity.

The tower search is organized so that lifting does not enumerate arbitrary
upstairs candidates and filter afterward. Instead, each lift is indexed by a
known downstairs simplex and the fiber of its final edge.

## Features

- Sparse directed graph input via small immutable records.
- First-scope loop normalization: input loops are stripped, then one formal
  identity is added at every vertex.
- Directed flag simplex enumeration through a user-provided `k`.
- First-class degenerate simplex records.
- Cached frontier recurrence:
  `F(sigma) = F(partial_m sigma) cap A(tgt sigma)`.
- Static tower integration through `state_collapser`.
- Fiber-addressed lifting across quotient tiers.
- JSON and JSONL artifact output for downstream inspection.
- Low-dimensional smoke examples with count arguments.

## Installation

This repository currently expects a sibling checkout of `state_collapser` while
public packaging is being prepared:

```bash
git clone https://github.com/TYLERSFOSTER/state_collapser.git
git clone https://github.com/TYLERSFOSTER/jet_simplex_search.git
cd jet_simplex_search
uv sync
```

The local dependency is recorded in `pyproject.toml` as:

```toml
[tool.uv.sources]
state-collapser = { path = "../state_collapser", editable = true }
```

## Quick Start

```python
from state_collapser.tower.partition.schema import LabelBlockSchema

from jet_simplex_search import search_simplices
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c")),
    edges=(
        InputEdge("ab", "a", "b", labels=("collapse",)),
        InputEdge("ac", "a", "c"),
        InputEdge("bc", "b", "c"),
    ),
)

result = search_simplices(
    graph=graph,
    contraction_schema=LabelBlockSchema.from_labels(("collapse",)),
    k=2,
)

print(result.diagnostics.simplex_counts_by_tier_degree)
```

Example output:

```python
{(1, 0): 2, (1, 1): 3, (1, 2): 4, (0, 0): 3, (0, 1): 6, (0, 2): 10}
```

## Artifact Output

Search results can be written as a compact JSON artifact:

```python
from pathlib import Path

from jet_simplex_search.artifacts import ArtifactConfig

result = search_simplices(
    graph=graph,
    contraction_schema=LabelBlockSchema.from_labels(("collapse",)),
    k=2,
    artifact_config=ArtifactConfig(output_dir=Path("artifacts/example")),
)
```

For table-oriented inspection, use the manifest-table layout:

```python
ArtifactConfig(
    output_dir=Path("artifacts/example"),
    layout="manifest_tables",
)
```

That writes:

- `readout_source.json`
- `simplex_records.jsonl`
- `simplex_fibers.jsonl`
- `edge_fibers.jsonl`
- `diagnostics.json`

## Smoke Examples

The `smoke/` directory contains small examples through dimension `4`.

Run one example:

```bash
uv run python smoke/smoke_007.py
```

The matching Markdown file explains why the output table is correct:

```text
smoke/smoke_007.md
```

These examples cover isolated vertices, paths, transitive triangles, forks,
diamonds, disconnected components, parallel edges, input-loop stripping, and a
small quotient-tower contraction.

## Development

Run the test suite:

```bash
uv run pytest
```

Run the real `state_collapser` integration tests:

```bash
uv run pytest tests/integration/test_state_collapser_static_tower.py
```

Build the Python package locally:

```bash
uv build
```

## Release Status

Current status: pre-release.

Implemented and locally tested:

- bottom-tier direct enumeration;
- degenerate simplex records;
- fake-tower and real-`state_collapser` tower lifting;
- diagnostics;
- JSON/JSONL artifacts;
- low-dimensional smoke examples.

Still pending before public release:

- CI workflow;
- public dependency strategy for `state_collapser`;
- release hygiene automation;
- package classifiers and project URLs;
- changelog or release notes;
- final source distribution and wheel verification.

Not currently implemented:

- Kan replacement;
- meaningful non-identity input loops;
- one simplex per multigraph witness choice;
- compressed, SQLite, or DuckDB artifact storage;
- bitset, CSR, GPU, tensor, or multiprocessing acceleration.

## Attribution

The quotient-tower simplex search algorithm recorded in the design documents is
PM Abdul Malik's work and part of his thesis. This package is an implementation
track around that algorithmic content and its `state_collapser` integration.

## Design Spine

- [Static tower small-object simplex search](docs/design/initial_design/01_001_static_tower_small_object_simplex_search.md)
- [Package blueprint](docs/design/initial_design/01_002_static_tower_small_object_package_blueprint.md)
- [Implementation workplan](docs/design/initial_design/01_003_static_tower_small_object_implementation_workplan.md)
- [Implementation log](docs/design/initial_design/01_004_static_tower_small_object_implementation_log.md)
- [Engineering continuity report](docs/release/engineering_continuity_report.md)
