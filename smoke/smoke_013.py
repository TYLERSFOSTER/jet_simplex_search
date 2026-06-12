from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

# Two disconnected edges: simplex counts add across components.

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c"), InputVertex("d")),
    edges=(
        InputEdge("ab", "a", "b"),
        InputEdge("cd", "c", "d"),
    ),
)

print_simplex_count_table(
    graph=graph,
    k=4,
)
