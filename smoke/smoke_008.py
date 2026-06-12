from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

# Full 4-chain: complete directed flag complex on a 4-element total order.

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c"), InputVertex("d")),
    edges=(
        InputEdge("ab", "a", "b"),
        InputEdge("ac", "a", "c"),
        InputEdge("ad", "a", "d"),
        InputEdge("bc", "b", "c"),
        InputEdge("bd", "b", "d"),
        InputEdge("cd", "c", "d"),
    ),
)

print_simplex_count_table(
    graph=graph,
    k=4,
)
