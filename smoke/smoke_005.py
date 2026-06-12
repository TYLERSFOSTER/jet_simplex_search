from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

# One directed edge: degeneracies over a single nonidentity 1-simplex.

graph = GraphInput(
    vertices=(InputVertex("a"), InputVertex("b")),
    edges=(InputEdge("ab", "a", "b"),),
)

print_simplex_count_table(
    graph=graph,
    k=4,
)
