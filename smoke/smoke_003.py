from jet_simplex_search.graph import GraphInput, InputVertex
from simplex_table import print_simplex_count_table

# One isolated vertex: only total degeneracies exist in every dimension.

graph = GraphInput(
    vertices=(InputVertex("a"),),
)

print_simplex_count_table(
    graph=graph,
    k=4,
)
