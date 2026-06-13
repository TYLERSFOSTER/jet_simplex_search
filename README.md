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
[![Lint](https://img.shields.io/badge/lint-ruff-46a2f1.svg)](https://docs.astral.sh/ruff/)
[![Status](https://img.shields.io/badge/status-pre--release-orange.svg)](#release-status)
[![Package Manager](https://img.shields.io/badge/package%20manager-uv-6f42c1.svg)](https://docs.astral.sh/uv/)

`jet_simplex_search` is an implementation of one of the central algorithms developed by [Abdullah N. Malik](https://abdullahnaeemmalik.github.io/) in [*his work on simplicial graph ML*](https://repository.lib.fsu.edu/islandora/object/fsu:927979). It is a Python package for finding directed simplices in
sparse graphs. It first skeletonizes an input graph `H` with loops or parallel
edges to a simple-reflexive search graph `G`, emits degenerate simplices as
first-class records, and uses static quotient towers from
[`state_collapser`](https://github.com/TYLERSFOSTER/state_collapser) to restrict
higher-tier search to fibers over known downstairs simplices. Tier-0 skeleton
simplices also receive compressed H-lift counts, so original loops and parallel
edges in `H` remain visible without polluting tower search.
<p align="center">
  <picture>
    <source srcset="assets/images/how_dark.svg" media="(prefers-color-scheme: dark)">
    <source srcset="assets/images/how_light.svg" media="(prefers-color-scheme: light)">
    <img src="assets/images/how_light.svg" alt="how" width="420">
  </picture>
</p>

<table align="center">
  <tr>
    <td width="350" align="center">
      <sub><em>The speed-up provided by `jet_simplex_search` is acheived by using a contraction hierarchy to reduce the search space.</em></sub>
    </td>
  </tr>
</table>

The package is currently pre-release software. The core implementation is in
place, but public packaging, CI, and release hygiene are still being prepared.

## Why This Exists

Given a directed graph `H` and a dimension bound `k`, the package builds a
simple skeleton `G` and enumerates directed skeleton simplices through dimension
`k`. A simplex is treated as a directed flag object: every required face edge
must exist in the skeleton. For example, a path
`a -> b -> c` is not a 2-simplex unless the face edge `a -> c` also exists.

Degenerate simplices are not collapsed away. Words such as `(a, a, b)` and
`(a, b, b)` are valid degree-2 simplices over the edge `a -> b`, and they
remain distinct records with their full arity.
<p align="center">
  <picture>
    <source srcset="assets/images/degens_dark.svg" media="(prefers-color-scheme: dark)">
    <source srcset="assets/images/degens_light.svg" media="(prefers-color-scheme: light)">
    <img src="assets/images/degens_light.svg" alt="degens" width="250">
  </picture>
</p>

<table align="center">
  <tr>
    <td width="350" align="center">
      <sub><em>The 4 distinct degenerate 2-simplices, a.k.a. oriented triangles, that lie on a directed edge between two loops.</em></sub>
    </td>
  </tr>
</table>

The tower search is organized so that lifting does not enumerate arbitrary
upstairs candidates and filter afterward. Instead, each lift is indexed by a
known downstairs simplex and the fiber of its final edge.

After tier-0 skeleton simplices are found, the package computes compressed
H-lift counts. Degenerate skeleton faces lift to `H` precisely through actual
loops in `H`; a formal identity in `G` is not counted as an original H loop.
Parallel H edges produce distinct lifted H-simplices through product counts.
$$
H\xrightarrow{\text{red}}\widetilde{H}=: G^{0}\xrightarrow{q^{0}_{1}}G^{1}\xrightarrow{\text{red}}\widetilde{G}^{1}\xrightarrow{q^{1}_{2}}G^{2}\xrightarrow{\text{red}}\widetilde{G}^{2}\xrightarrow{q^{2}_{3}}\cdots
$$

## Features

- Sparse directed graph input via small immutable records.
- H-to-G skeletonization for input loops and parallel edges.
- Formal identity search edges for degenerate skeleton addresses.
- Directed flag simplex enumeration through a user-provided `k`.
- First-class degenerate simplex records.
- Cached frontier recurrence:
  `F(sigma) = F(partial_m sigma) cap A(tgt sigma)`.
- Static tower integration through `state_collapser`.
- Fiber-addressed lifting across quotient tiers.
- Compressed H-lift counts for tier-0 skeleton simplices.
- JSON and JSONL artifact output for downstream inspection.
- Low-dimensional smoke examples with count arguments.

## Installation

This package is currently a GitHub source pre-release. For a local checkout:

```bash
git clone https://github.com/TYLERSFOSTER/jet_simplex_search.git
cd jet_simplex_search
uv sync
```

`state_collapser` is pulled from its GitHub release tag by `pyproject.toml`:

```toml
"state-collapser @ git+https://github.com/TYLERSFOSTER/state_collapser.git@v0.7.2"
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

print(result.skeleton_search.diagnostics.simplex_counts_by_tier_degree)
print(result.h_lift_diagnostics.total_h_lift_count_by_degree)
```

Example output:

```python
{(1, 0): 2, (1, 1): 3, (1, 2): 4, (0, 0): 3, (0, 1): 6, (0, 2): 10}
{0: 3, 1: 3, 2: 1}
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
- `skeleton_edge_fibers.jsonl`
- `skeleton_loop_fibers.jsonl`
- `simplex_records.jsonl`
- `simplex_fibers.jsonl`
- `edge_fibers.jsonl`
- `h_lift_records.jsonl`
- `h_lift_face_factors.jsonl`
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
diamonds, disconnected components, parallel H edges, input-loop H-lifts, and a
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

Run Ruff:

```bash
uv run ruff check .
```

## Release Status

Current status: pre-release.

Implemented and locally tested:

- H-to-G skeletonization;
- compressed tier-0 H-lift counts;
- bottom-tier direct enumeration;
- degenerate simplex records;
- fake-tower and real-`state_collapser` tower lifting;
- diagnostics;
- JSON/JSONL artifacts;
- low-dimensional smoke examples.

Still pending before public release:

- CI workflow;
- release hygiene automation;
- changelog or release notes;
- final source distribution and wheel verification.

## Known Limitations

This is a library pre-release, and the current scope is deliberately narrow:

- Kan replacement and horn-filling variants are not implemented.
- Expanded H witness assignment artifacts are not implemented.
- The v0.1 label policy requires exact label agreement when parallel H edges or
  quotient edges collapse.
- Tower search is static; it does not rebuild the tower during simplex search.
- There is no bitset, CSR, GPU, tensor, or multiprocessing acceleration yet.
- `search_simplices` studies graph `H`; lower-level skeleton/tower search is
  exposed separately as `search_skeleton_simplices`.

## Malik Research Lineage

This package implements a small, release-oriented slice of Abdullah N. Malik's
simplicial graph-search program. Malik's work supplies the mathematical and
algorithmic origin: directed graphs as 1-skeletons of simplicial data,
degenerate simplices as first-class records, and quotient-tower lifting as the
core speed-up for higher simplex search. This repository adds the package
engineering around `state_collapser`, H-to-G skeletonization, witness artifacts,
and release-facing tests.

For the detailed provenance assessment, see
[Malik work progeny in `jet_simplex_search`](docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md).

## Design Spine

- [Static tower small-object simplex search](docs/design/initial_design/01_001_static_tower_small_object_simplex_search.md)
- [Package blueprint](docs/design/initial_design/01_002_static_tower_small_object_package_blueprint.md)
- [Implementation workplan](docs/design/initial_design/01_003_static_tower_small_object_implementation_workplan.md)
- [Implementation log](docs/design/initial_design/01_004_static_tower_small_object_implementation_log.md)
