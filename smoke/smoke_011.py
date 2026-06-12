from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

# Open diamond: length-2 routes do not count without the closing face a -> d.

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c"), InputVertex("d")),
    edges=(
        InputEdge("ab", "a", "b"),
        InputEdge("ac", "a", "c"),
        InputEdge("bd", "b", "d"),
        InputEdge("cd", "c", "d"),
    ),
)

print_simplex_count_table(
    graph=graph,
    k=4,
)
