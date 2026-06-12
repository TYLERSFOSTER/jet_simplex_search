from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

# Parallel edges share the same vertex simplex address; witnesses aggregate.

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b")),
    edges=(
        InputEdge("ab_left", "a", "b"),
        InputEdge("ab_right", "a", "b"),
    ),
)

print_simplex_count_table(
    graph=graph,
    k=4,
)
