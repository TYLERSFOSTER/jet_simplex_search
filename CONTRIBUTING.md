# Contributing

Thanks for helping improve `jet_simplex_search`.

## Setup

```bash
git clone https://github.com/TYLERSFOSTER/jet_simplex_search.git
cd jet_simplex_search
uv sync
```

Run local checks:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run python scripts/release_hygiene.py --repo-root .
```

## Scope

Preserve the core semantics:

- directed flag simplices require all directed face edges;
- degenerate simplices are first-class records;
- lifting is fiber-addressed over existing downstairs simplex records;
- H-to-G skeletonization preserves loop and parallel-edge information through
  fibers and H-lift counts;
- `state_collapser` owns quotient-tower construction;
- `jet_simplex_search` owns simplex enumeration, lifting, witnesses, H-lifts,
  diagnostics, and artifacts.

Preserve Abdullah N. Malik attribution and the distinction between this package
and [`HGraphML`](https://github.com/TYLERSFOSTER/HGraphML): this package handles
bounded simplex search and quotient lifting; HGraphML is the separate beginning
of quotient-tower-backed graph message passing.

For design work on future completion/search modes, use:

```text
docs/design/completion_search_modes
```

Current subtracks include the existing cofibrant small-object mode, weak Kan
inner-horn mode, full Kan all-horn mode, cubical commutative square/cube mode,
and globular test-object mode. Treat these as design tracks until an
implementation workplan is approved and executed.

## Pull Requests

Please include:

- summary of the change;
- tests run;
- any changed public claims;
- any changed artifact format;
- whether the change touches deferred features such as Kan replacement,
  cubical commutativity, globular test objects, expanded H witnesses,
  acceleration backends, or neural message passing.

Do not claim PyPI publication, production readiness, benchmark-validated
speed-ups, Kan replacement, cubical/globular completion, or neural message
passing unless those claims are implemented and verified.
