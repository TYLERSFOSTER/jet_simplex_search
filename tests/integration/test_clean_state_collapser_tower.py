from __future__ import annotations

from state_collapser.tower.partition.schema import LabelBlockSchema

from jet_simplex_search.api import search_skeleton_simplices
from jet_simplex_search.clean_tower import CleanStaticTowerAdapter
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex


def _clean_multi_step_graph() -> GraphInput:
    return GraphInput(
        vertices=(InputVertex("a"), InputVertex("b"), InputVertex("d")),
        edges=(
            InputEdge("ab", "a", "b", labels=("first",)),
            InputEdge("ad", "a", "d", labels=("second",)),
            InputEdge("bd", "b", "d", labels=("second",)),
        ),
    )


def test_clean_bridge_uses_state_collapser_schema_and_keeps_tiers_simple() -> None:
    adapter = CleanStaticTowerAdapter.from_graph(
        _clean_multi_step_graph(),
        schema=LabelBlockSchema.from_labels(("first", "second")),
    )

    assert adapter.tiers() == (0, 1, 2)
    for tier_graph in adapter.clean_tower.tier_graphs:
        endpoint_pairs: set[tuple[str, str]] = set()
        for edge in tier_graph.edges:
            assert edge.source != edge.target
            pair = (edge.source, edge.target)
            assert pair not in endpoint_pairs
            endpoint_pairs.add(pair)


def test_search_skeleton_simplices_graph_route_uses_clean_bridge() -> None:
    result = search_skeleton_simplices(
        graph=_clean_multi_step_graph(),
        contraction_schema=LabelBlockSchema.from_labels(("first", "second")),
        k=2,
    )

    assert result.bottom_tier == 1
    assert result.simplices_by_tier_degree[(1, 1)]
    assert result.simplices_by_tier_degree[(0, 1)]
    assert result.fibers
    assert result.edge_fibers
