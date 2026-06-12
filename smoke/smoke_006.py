from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

# Two-step path with no skip edge: no nondegenerate 2-simplex is allowed.

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c")),
    edges=(
        InputEdge("ab", "a", "b"),
        InputEdge("bc", "b", "c"),
    ),
)

print_simplex_count_table(
    graph=graph,
    k=4,
)
