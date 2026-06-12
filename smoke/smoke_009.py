from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

# Out-fork: two outgoing edges from one source, but no face between targets.

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c")),
    edges=(
        InputEdge("ab", "a", "b"),
        InputEdge("ac", "a", "c"),
    ),
)

print_simplex_count_table(
    graph=graph,
    k=4,
)
