from state_collapser.tower.partition.schema import LabelBlockSchema

from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b"), InputVertex("d")),
    edges=(
        InputEdge("ab", "a", "b", labels=("collapse",)),
        InputEdge("ad", "a", "d"),
        InputEdge("bd", "b", "d"),
    ),
)

print_simplex_count_table(
    graph=graph,
    contraction_schema=LabelBlockSchema.from_labels(("collapse",)),
    k=2,
)
