from state_collapser.tower.partition.schema import LabelBlockSchema

from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from simplex_table import print_simplex_count_table

graph = GraphInput(
    vertices=(
        InputVertex("0"), 
        InputVertex("1"), 
        InputVertex("2"), 
        InputVertex("3"), 
        InputVertex("4"),
        InputVertex("5"), 
        InputVertex("6"), 
        InputVertex("7"), 
        InputVertex("8"), 
        InputVertex("9"),
        InputVertex("10"), 
        InputVertex("11"), 
        InputVertex("12"), 
        InputVertex("13"),
        InputVertex("14"), 
        InputVertex("15")
              ),
    edges=(
        InputEdge("01", "0", "1", labels=("collapse",)),
        InputEdge("12", "1", "2"),  
        InputEdge("23", "2", "3", labels=("collapse",)),
        InputEdge("34", "3", "4"),
        InputEdge("45", "4", "5", labels=("collapse",)),
        InputEdge("56", "5", "6"),
        InputEdge("67", "6", "7", labels=("collapse",)),
        InputEdge("78", "7", "8"),
        InputEdge("89", "8", "9", labels=("collapse",)),
        InputEdge("9 10", "9", "10"),
        InputEdge("10 11", "10", "11", labels=("collapse",)),
        InputEdge("11 12", "11", "12"),
        InputEdge("12 13", "12", "13", labels=("collapse",)),
        InputEdge("13 14", "13", "14"),
        InputEdge("14 15", "14", "15", labels=("collapse",)),
    ),
)

print_simplex_count_table(
    graph=graph,
    contraction_schema=LabelBlockSchema.from_labels(("collapse",)),
    k=4,
)
