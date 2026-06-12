from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

# Transitive triangle: one genuine nondegenerate 2-simplex plus degeneracies.

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c")),
    edges=(
        InputEdge("ab", "a", "b"),
        InputEdge("ac", "a", "c"),
        InputEdge("bc", "b", "c"),
    ),
)

print_simplex_count_table(
    graph=graph,
    k=4,
)
