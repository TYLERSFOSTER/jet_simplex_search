from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

# Input loops are stripped; the formal identity is the only loop used.

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b")),
    edges=(
        InputEdge("aa_input_loop", "a", "a"),
        InputEdge("ab", "a", "b"),
    ),
)

print_simplex_count_table(
    graph=graph,
    k=4,
)
