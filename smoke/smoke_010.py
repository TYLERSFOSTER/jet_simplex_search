from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

# In-fork: two incoming edges to one target, but no face between sources.

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c")),
    edges=(
        InputEdge("ac", "a", "c"),
        InputEdge("bc", "b", "c"),
    ),
)

print_simplex_count_table(
    graph=graph,
    k=4,
)
