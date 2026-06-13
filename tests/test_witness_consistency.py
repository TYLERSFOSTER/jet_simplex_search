from __future__ import annotations

from collections.abc import Iterable

from state_collapser.tower.partition.schema import LabelBlockSchema

from jet_simplex_search.clean_tower import CleanStaticTowerAdapter
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from jet_simplex_search.records import SimplexRecord, SimplexSearchResult
from jet_simplex_search.search import run_static_small_object_search
from jet_simplex_search.tower_adapter import (
    StaticTowerAdapterProtocol,
    normalized_graph_for_tier,
)

from tests.fakes import FakeStaticTowerAdapter


def _clean_contracting_adapter() -> CleanStaticTowerAdapter:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b"), InputVertex("d")),
        edges=(
            InputEdge("ab", "a", "b", labels=("collapse",)),
            InputEdge("ad", "a", "d"),
            InputEdge("bd", "b", "d"),
        ),
    )
    return CleanStaticTowerAdapter.from_graph(
        graph,
        schema=LabelBlockSchema.from_labels(("collapse",)),
    )


def _all_simplices(result: SimplexSearchResult) -> tuple[SimplexRecord, ...]:
    return tuple(
        simplex
        for (_tier, _degree), simplices in result.simplices_by_tier_degree.items()
        for simplex in simplices
    )


def _simplices_by_id(
    simplices: Iterable[SimplexRecord],
) -> dict[str, SimplexRecord]:
    return {simplex.id: simplex for simplex in simplices}


def _edge_endpoints_by_id(
    adapter: StaticTowerAdapterProtocol,
    tier: int,
) -> dict[str, tuple[str, str]]:
    graph = normalized_graph_for_tier(adapter, tier)
    return {
        edge.id: (edge.source, edge.target)
        for edge in graph.edges
    }


def _assert_witness_edges_match_vertices(
    *,
    adapter: StaticTowerAdapterProtocol,
    result: SimplexSearchResult,
) -> None:
    endpoint_cache = {
        tier: _edge_endpoints_by_id(adapter, tier)
        for tier in adapter.tiers()
    }
    for simplex in _all_simplices(result):
        endpoints_by_id = endpoint_cache[simplex.tier]
        for witness in simplex.face_edge_witnesses:
            assert witness.source_index < len(simplex.vertices)
            assert witness.target_index < len(simplex.vertices)
            expected_source = simplex.vertices[witness.source_index]
            expected_target = simplex.vertices[witness.target_index]
            for edge_id in witness.edge_ids:
                assert endpoints_by_id[edge_id] == (expected_source, expected_target)
        for edge_id in simplex.last_edge_ids:
            assert endpoints_by_id[edge_id] == (
                simplex.vertices[-2],
                simplex.vertices[-1],
            )


def _assert_lifted_projection_records_are_truthful(
    *,
    adapter: StaticTowerAdapterProtocol,
    result: SimplexSearchResult,
) -> None:
    simplices_by_id = _simplices_by_id(_all_simplices(result))
    for simplex in _all_simplices(result):
        if simplex.tier >= result.bottom_tier:
            continue
        assert simplex.projection_simplex_id is not None
        downstairs = simplices_by_id[simplex.projection_simplex_id]
        projected_vertices = tuple(
            adapter.project_vertex(simplex.tier, vertex_id)
            for vertex_id in simplex.vertices
        )
        assert projected_vertices == downstairs.vertices
        if simplex.degree > 0:
            projected_last_edges = {
                adapter.project_edge(simplex.tier, edge_id)
                for edge_id in simplex.last_edge_ids
            }
            assert projected_last_edges & set(downstairs.last_edge_ids)


def test_fake_adapter_witnesses_and_projection_records_are_truthful() -> None:
    adapter = FakeStaticTowerAdapter()
    result = run_static_small_object_search(adapter, k=2)

    _assert_witness_edges_match_vertices(adapter=adapter, result=result)
    _assert_lifted_projection_records_are_truthful(adapter=adapter, result=result)


def test_clean_adapter_witnesses_and_projection_records_are_truthful() -> None:
    adapter = _clean_contracting_adapter()
    result = run_static_small_object_search(adapter, k=2)

    _assert_witness_edges_match_vertices(adapter=adapter, result=result)
    _assert_lifted_projection_records_are_truthful(adapter=adapter, result=result)
