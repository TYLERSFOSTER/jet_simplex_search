<div style="display:flex; align-items:baseline; gap:0.15em; line-height:1;">
  <span style="font-size:7px;">⨻</span>
  <span style="font-size:6px;">←</span>
  <span style="font-size:13px;">⨻</span>
  <span style="font-size:10px;">←</span>
  <span style="font-size:20px;">⨻</span>
  <span style="font-size:15px;">←</span>
  <span style="font-size:30px;">⨻</span>
  <span style="font-size:20px;">←</span>
  <span style="font-size:50px;">⨻</span>
  <span style="font-size:30px;">←</span>
  <span style="font-size:70px;">⨻</span>
  <span style="font-size:40px;">←</span>
  <span style="font-size:80px;">⨻</span>
</div>

# **JET- SIMPLEX - SEARCH**
`jet_simplex_search` searches for directed flag simplices in sparse graphs using
static quotient towers from `state_collapser`. Degenerate simplices are emitted
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
