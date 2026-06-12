from jet_simplex_search.graph import GraphInput, InputVertex
from simplex_table import print_simplex_count_table

# Two isolated vertices: total degeneracies at each vertex, no edge support.

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b")),
)

print_simplex_count_table(
    graph=graph,
    k=4,
)
