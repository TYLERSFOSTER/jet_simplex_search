from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

# Closed diamond: two genuine 2-simplices, but no 3-simplex.

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c"), InputVertex("d")),
    edges=(
        InputEdge("ab", "a", "b"),
        InputEdge("ac", "a", "c"),
        InputEdge("ad", "a", "d"),
        InputEdge("bd", "b", "d"),
        InputEdge("cd", "c", "d"),
    ),
)

print_simplex_count_table(
    graph=graph,
    k=4,
)
