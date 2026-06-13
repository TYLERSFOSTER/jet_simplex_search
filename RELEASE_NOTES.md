# Release Notes

## v0.1.0 - GitHub Library Pre-Release

Status: GitHub-only library pre-release.

`jet_simplex_search` is a Python package for bounded directed simplex search in
sparse graph data. It implements a focused release slice of Abdullah N. Malik's
simplicial graph-search program: directed graph data, first-class degenerate
simplices, quotient-tower search, and fiber-addressed lifting.

This release is not published to PyPI. Install from a source checkout:

```bash
git clone https://github.com/TYLERSFOSTER/jet_simplex_search.git
cd jet_simplex_search
uv sync
```

The package depends on `state_collapser` through the GitHub release tag
`v0.7.2`:

```toml
"state-collapser @ git+https://github.com/TYLERSFOSTER/state_collapser.git@v0.7.2"
```

### Implemented

- Sparse graph input records.
- H-to-G skeletonization for input loops and parallel edges.
- Formal identity search edges for degenerate skeleton addresses.
- Directed flag simplex enumeration through a user-provided `k`.
- First-class degenerate simplex records.
- Cached sparse frontier intersections.
- Static quotient-tower integration through `state_collapser`.
- Fiber-addressed lifting over existing downstairs simplex records.
- Regression coverage for the current small-object behavior: if a downstairs
  simplex is absent, upstairs lifting over that simplex address does not run.
- Witness consistency checks for lifted simplex records.
- Compressed H-lift counts for tier-0 skeleton simplices.
- JSON and JSONL artifact output.
- README quick-start regression test.
- Low-dimensional smoke examples through dimension `4`.

### Deferred

- Kan replacement and horn-filling variants.
- Full cofibrant or small-object replacement API.
- Expanded H witness assignment artifacts.
- Bitset, CSR, GPU, tensor, or multiprocessing acceleration.
- Dynamic tower rebuilding during simplex search.
- PyPI publication.
- No benchmark-validated speed-up claims are made.

This package also does not implement neural message passing, CinchNET, or
PTVNN. The separate [`HGraphML`](https://github.com/TYLERSFOSTER/HGraphML)
package is the beginning of the quotient-tower-backed graph message-passing
branch; `jet_simplex_search` is the simplex-search and quotient-lift branch.

### Verification

Recommended local checks:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run python scripts/release_hygiene.py --repo-root .
uv build --out-dir <temporary-build-directory>
```

### Design Record

- [Static tower small-object simplex search](docs/design/initial_design/01_001_static_tower_small_object_simplex_search.md)
- [Package blueprint](docs/design/initial_design/01_002_static_tower_small_object_package_blueprint.md)
- [Implementation workplan](docs/design/initial_design/01_003_static_tower_small_object_implementation_workplan.md)
- [Implementation log](docs/design/initial_design/01_004_static_tower_small_object_implementation_log.md)
- [Malik work progeny in jet_simplex_search](docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md)

### Attribution

The mathematical and algorithmic origin of this package is Abdullah N. Malik's
work on simplicial methods in graph machine learning, especially the
quotient-tower simplex search line described in his thesis and related project
work. This package is a release-oriented implementation track around that
lineage and its `state_collapser` integration.
