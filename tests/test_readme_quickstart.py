from __future__ import annotations

from state_collapser.tower.partition.schema import LabelBlockSchema

from jet_simplex_search import SearchWithHLiftsResult, search_simplices
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex


def test_readme_quickstart_example_counts_are_current() -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c")),
        edges=(
            InputEdge("ab", "a", "b", labels=("collapse",)),
            InputEdge("ac", "a", "c"),
            InputEdge("bc", "b", "c"),
        ),
    )

    result = search_simplices(
        graph=graph,
        contraction_schema=LabelBlockSchema.from_labels(("collapse",)),
        k=2,
    )

    assert isinstance(result, SearchWithHLiftsResult)
    assert result.skeleton_search.diagnostics is not None
    assert result.skeleton_search.diagnostics.simplex_counts_by_tier_degree == {
        (1, 0): 2,
        (1, 1): 3,
        (1, 2): 4,
        (0, 0): 3,
        (0, 1): 6,
        (0, 2): 10,
    }
    assert result.h_lift_diagnostics.total_h_lift_count_by_degree == {
        0: 3,
        1: 3,
        2: 1,
    }
