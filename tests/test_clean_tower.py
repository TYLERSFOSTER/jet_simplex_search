from __future__ import annotations

import pytest
from state_collapser.tower.partition.schema import LabelBlockSchema

from jet_simplex_search.clean_tower import (
    CleanStaticTowerAdapter,
    CleanTowerConfig,
    build_clean_static_tower,
)
from jet_simplex_search.errors import CleanTowerConstructionError
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from jet_simplex_search.ids import identity_edge_id
from jet_simplex_search.search import run_static_small_object_search
from jet_simplex_search.tower_adapter import normalized_graph_for_tier


def _contracting_graph() -> GraphInput:
    return GraphInput(
        vertices=(InputVertex("a"), InputVertex("b"), InputVertex("d")),
        edges=(
            InputEdge("ab", "a", "b", labels=("collapse",)),
            InputEdge("ad", "a", "d"),
            InputEdge("bd", "b", "d"),
        ),
    )


def test_clean_tower_without_schema_keeps_single_clean_tier() -> None:
    graph = _contracting_graph()
    tower = build_clean_static_tower(graph)
    adapter = CleanStaticTowerAdapter(tower)
    normalized = normalized_graph_for_tier(adapter, 0)

    assert adapter.tiers() == (0,)
    assert adapter.bottommost_nondegenerate_tier() == 0
    assert tuple(edge.id for edge in tower.tier_graphs[0].edges) == ("ab", "ad", "bd")
    assert normalized.edge_lookup[("a", "a")] == (identity_edge_id("a"),)


def test_clean_tower_rejects_stored_loops_and_parallel_edges() -> None:
    with pytest.raises(CleanTowerConstructionError, match="must not store loops"):
        build_clean_static_tower(
            GraphInput(
                vertices=(InputVertex("a"),),
                edges=(InputEdge("aa", "a", "a"),),
            )
        )

    with pytest.raises(CleanTowerConstructionError, match="parallel edge pair"):
        build_clean_static_tower(
            GraphInput(
                vertices=(InputVertex("a"), InputVertex("b")),
                edges=(
                    InputEdge("ab0", "a", "b"),
                    InputEdge("ab1", "a", "b"),
                ),
            )
        )


def test_clean_tower_contracts_one_block_to_clean_downstream_graph() -> None:
    adapter = CleanStaticTowerAdapter.from_graph(
        _contracting_graph(),
        schema=LabelBlockSchema.from_labels(("collapse",)),
    )
    downstairs_edge = adapter.tier_edges(1)[0]
    downstairs_source = adapter.project_vertex(0, "a")

    assert adapter.tiers() == (0, 1)
    assert adapter.bottommost_nondegenerate_tier() == 1
    assert adapter.tier_vertices(1) == ("cell:1:0", "cell:1:1")
    assert len(adapter.tier_edges(1)) == 1
    assert adapter.project_edge(0, "ab") == identity_edge_id(downstairs_source)
    assert adapter.edge_fiber_targets(
        upstairs_tier=0,
        downstairs_edge_id=identity_edge_id(downstairs_source),
        upstairs_source_id="a",
    ) == frozenset({"a", "b"})
    assert adapter.edge_fiber_targets(
        upstairs_tier=0,
        downstairs_edge_id=downstairs_edge,
        upstairs_source_id="b",
    ) == frozenset({"d"})


def test_clean_tower_builds_multiple_declared_contraction_steps() -> None:
    graph = GraphInput(
        vertices=(
            InputVertex("a"),
            InputVertex("b"),
            InputVertex("d"),
        ),
        edges=(
            InputEdge("ab", "a", "b", labels=("first",)),
            InputEdge("ad", "a", "d", labels=("second",)),
            InputEdge("bd", "b", "d", labels=("second",)),
        ),
    )

    tower = build_clean_static_tower(
        graph,
        schema=LabelBlockSchema.from_labels(("first", "second")),
    )

    assert tower.diagnostics.vertex_count_by_tier == {0: 3, 1: 2, 2: 1}
    assert tower.diagnostics.edge_count_by_tier == {0: 3, 1: 1, 2: 0}
    assert tower.diagnostics.collapsed_loop_count_by_step == {0: 1, 1: 1}
    assert tower.diagnostics.collapsed_parallel_edge_count_by_step == {0: 1, 1: 0}
    assert len(tower.tier_graphs[1].edges) == 1
    assert tower.tier_graphs[1].edges[0].labels == ("second",)


def test_clean_tower_skips_declared_blocks_without_edges() -> None:
    tower = build_clean_static_tower(
        _contracting_graph(),
        schema=LabelBlockSchema.from_labels(("missing", "collapse")),
    )

    assert len(tower.tier_graphs) == 2
    assert tower.diagnostics.skipped_empty_block_count == 1


def test_clean_tower_label_conflict_is_explicit() -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b"), InputVertex("d")),
        edges=(
            InputEdge("ab", "a", "b", labels=("collapse",)),
            InputEdge("ad", "a", "d", labels=("left",)),
            InputEdge("bd", "b", "d", labels=("right",)),
        ),
    )

    with pytest.raises(CleanTowerConstructionError, match="label conflict"):
        build_clean_static_tower(
            graph,
            schema=LabelBlockSchema.from_labels(("collapse",)),
        )


def test_clean_tower_obeys_max_tiers() -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c")),
        edges=(
            InputEdge("ab", "a", "b", labels=("first",)),
            InputEdge("bc", "b", "c", labels=("second",)),
        ),
    )

    tower = build_clean_static_tower(
        graph,
        schema=LabelBlockSchema.from_labels(("first", "second")),
        config=CleanTowerConfig(max_tiers=2),
    )

    assert len(tower.tier_graphs) == 2


def test_clean_tower_adapter_runs_static_search() -> None:
    adapter = CleanStaticTowerAdapter.from_graph(
        _contracting_graph(),
        schema=LabelBlockSchema.from_labels(("collapse",)),
    )

    result = run_static_small_object_search(adapter, k=1)

    assert result.bottom_tier == 1
    assert result.simplices_by_tier_degree[(1, 1)]
    assert result.simplices_by_tier_degree[(0, 1)]
    assert result.fibers
    assert result.edge_fibers
