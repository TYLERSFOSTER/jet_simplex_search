<p align="left">
  <picture>
    <source srcset="assets/images/logo_dark.svg" media="(prefers-color-scheme: dark)">
    <source srcset="assets/images/logo_light.svg" media="(prefers-color-scheme: light)">
    <img src="assets/images/logo_light.svg" alt="jet_simplex_search" width="340">
  </picture>
</p>

# **JET- SIMPLEX - SEARCH**
`jet_simplex_search` searches for directed flag simplices in sparse graphs using
static quotient towers from [`state_collapser`](https://github.com/TYLERSFOSTER/state_collapser). Degenerate simplices are emitted
as first-class records, and tower descent is restricted to fibers over known
downstairs simplices.

## Tiny Example

```python
from state_collapser.tower.partition.schema import LabelBlockSchema

from jet_simplex_search import search_simplices
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b"), InputVertex("d")),
    edges=(
        InputEdge("ab", "a", "b", labels=("collapse",)),
        InputEdge("ad", "a", "d"),
        InputEdge("bd", "b", "d"),
    ),
)

result = search_simplices(
    graph=graph,
    contraction_schema=LabelBlockSchema.from_labels(("collapse",)),
    k=1,
)

print(result.diagnostics.simplex_counts_by_tier_degree)
```

## Design Spine

- [Static tower small-object simplex search](docs/design/initial_design/01_001_static_tower_small_object_simplex_search.md)
- [Package blueprint](docs/design/initial_design/01_002_static_tower_small_object_package_blueprint.md)
- [Implementation workplan](docs/design/initial_design/01_003_static_tower_small_object_implementation_workplan.md)
- [Implementation log](docs/design/initial_design/01_004_static_tower_small_object_implementation_log.md)
