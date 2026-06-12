from state_collapser.tower.partition.schema import LabelBlockSchema

from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

# Collapsed transitive triangle: upstairs (a,b,c) lies over downstairs (X,X,c).

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c")),
    edges=(
        InputEdge("ab", "a", "b", labels=("collapse",)),
        InputEdge("ac", "a", "c"),
        InputEdge("bc", "b", "c"),
    ),
)

print_simplex_count_table(
    graph=graph,
    contraction_schema=LabelBlockSchema.from_labels(("collapse",)),
    k=4,
)
