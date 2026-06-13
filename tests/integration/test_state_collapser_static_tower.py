from state_collapser.tower.partition.schema import LabelBlockSchema

from jet_simplex_search.api import search_simplices
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from jet_simplex_search.ids import identity_edge_id
from jet_simplex_search.tower_adapter import (
    StateCollapserStaticTowerAdapter,
    normalized_graph_for_tier,
)


def _contracting_graph() -> GraphInput:
    return GraphInput(
        vertices=(InputVertex("a"), InputVertex("b"), InputVertex("d")),
        edges=(
            InputEdge("ab", "a", "b", labels=("collapse",)),
            InputEdge("ad", "a", "d"),
            InputEdge("bd", "b", "d"),
        ),
    )


def test_state_collapser_adapter_builds_static_partition_tower() -> None:
    adapter = StateCollapserStaticTowerAdapter.from_graph(
        _contracting_graph(),
        schema=LabelBlockSchema.from_labels(("collapse",)),
    )

    assert adapter.tiers() == (0, 1)
    assert adapter.bottommost_nondegenerate_tier() == 1
    assert adapter.tier_vertices(1)
    assert adapter.tier_edges(0)


def test_state_collapser_adapter_projects_internal_edge_to_downstairs_identity() -> (
    None
):
    adapter = StateCollapserStaticTowerAdapter.from_graph(
        _contracting_graph(),
        schema=LabelBlockSchema.from_labels(("collapse",)),
    )
    graph = normalized_graph_for_tier(adapter, 0)
    ab_edge = next(edge_id for edge_id in graph.edge_lookup[("cell:0:0", "cell:0:1")])
    projected = adapter.project_edge(0, ab_edge)

    assert projected.startswith("jss:identity:")


def test_state_collapser_adapter_edge_fiber_includes_nonidentity_over_identity() -> (
    None
):
    adapter = StateCollapserStaticTowerAdapter.from_graph(
        _contracting_graph(),
        schema=LabelBlockSchema.from_labels(("collapse",)),
    )
    source = "cell:0:0"
    downstairs_source = adapter.project_vertex(0, source)
    targets = adapter.edge_fiber_targets(
        upstairs_tier=0,
        downstairs_edge_id=identity_edge_id(downstairs_source),
        upstairs_source_id=source,
    )

    assert "cell:0:1" in targets


def test_search_simplices_uses_real_state_collapser_adapter() -> None:
    result = search_simplices(
        graph=_contracting_graph(),
        contraction_schema=LabelBlockSchema.from_labels(("collapse",)),
        k=1,
    )

    assert result.skeleton_search.simplices_by_tier_degree
    assert result.skeleton_search.fibers
    assert result.h_lifts


def test_state_collapser_adapter_maps_tier_zero_vertices_to_input_ids() -> None:
    adapter = StateCollapserStaticTowerAdapter.from_graph(_contracting_graph())

    mapping = adapter.tier0_vertex_id_to_input_vertex_id()

    assert set(mapping.values()) == {"a", "b", "d"}
