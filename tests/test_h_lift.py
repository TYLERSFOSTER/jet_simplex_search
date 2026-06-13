from dataclasses import replace

import pytest

from jet_simplex_search.errors import SimplexInvariantError
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from jet_simplex_search.h_lift import (
    HFaceLiftFactor,
    SimplexHLiftRecord,
    build_h_lift_diagnostics,
    compute_h_lifts_for_tier_zero,
)
from jet_simplex_search.normalize import normalize_graph
from jet_simplex_search.records import SimplexSearchResult
from jet_simplex_search.search import enumerate_direct_simplices
from jet_simplex_search.skeleton import SkeletonizationResult, skeletonize_graph


def test_h_face_lift_factor_validates_factor_count() -> None:
    with pytest.raises(SimplexInvariantError, match="factor"):
        HFaceLiftFactor(
            source_index=0,
            target_index=1,
            source_vertex_id="a",
            target_vertex_id="b",
            skeleton_edge_id="ab",
            original_edge_ids=("ab1",),
            factor=2,
            is_loop_factor=False,
        )


def test_simplex_h_lift_record_preserves_zero_count() -> None:
    factor = HFaceLiftFactor(
        source_index=0,
        target_index=1,
        source_vertex_id="s",
        target_vertex_id="s",
        skeleton_edge_id="id",
        original_edge_ids=(),
        factor=0,
        is_loop_factor=True,
    )

    record = SimplexHLiftRecord(
        id="lift",
        simplex_id="simplex",
        tier=0,
        degree=1,
        skeleton_vertices=("s", "s"),
        input_vertices=("s", "s"),
        face_factors=(factor,),
        h_lift_count=0,
        has_h_lift=False,
    )

    assert record.h_lift_count == 0
    assert not record.has_h_lift


def test_degree_zero_h_lift_count_is_one() -> None:
    skeleton, search = _search_h(GraphInput(vertices=(InputVertex("s"),)), k=0)

    records = compute_h_lifts_for_tier_zero(
        skeletonization=skeleton,
        skeleton_search=search,
        tier0_vertex_id_to_input_vertex_id={"s": "s"},
    )

    assert len(records) == 1
    assert records[0].degree == 0
    assert records[0].h_lift_count == 1


def test_parallel_non_loop_edges_give_distinct_edge_lifts() -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b")),
        edges=(
            InputEdge("ab1", "a", "b"),
            InputEdge("ab2", "a", "b"),
            InputEdge("ab3", "a", "b"),
        ),
    )
    skeleton, search = _search_h(graph, k=1)

    record = _h_lift_for_vertices(skeleton, search, ("a", "b"))

    assert record.h_lift_count == 3
    assert record.face_factors[0].original_edge_ids == ("ab1", "ab2", "ab3")


def test_degenerate_edge_without_h_loop_has_zero_lifts() -> None:
    skeleton, search = _search_h(GraphInput(vertices=(InputVertex("s"),)), k=1)

    record = _h_lift_for_vertices(skeleton, search, ("s", "s"))

    assert record.h_lift_count == 0
    assert not record.has_h_lift
    assert record.face_factors[0].is_loop_factor


def test_degenerate_edge_with_h_loops_counts_loops() -> None:
    graph = GraphInput(
        vertices=(InputVertex("s"),),
        edges=(InputEdge("loop1", "s", "s"), InputEdge("loop2", "s", "s")),
    )
    skeleton, search = _search_h(graph, k=1)

    record = _h_lift_for_vertices(skeleton, search, ("s", "s"))

    assert record.h_lift_count == 2
    assert record.face_factors[0].original_edge_ids == ("loop1", "loop2")


def test_non_degenerate_triangle_count_is_product_of_edge_fibers() -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c")),
        edges=(
            InputEdge("ab1", "a", "b"),
            InputEdge("ab2", "a", "b"),
            InputEdge("ac1", "a", "c"),
            InputEdge("ac2", "a", "c"),
            InputEdge("ac3", "a", "c"),
            InputEdge("bc1", "b", "c"),
            InputEdge("bc2", "b", "c"),
            InputEdge("bc3", "b", "c"),
            InputEdge("bc4", "b", "c"),
            InputEdge("bc5", "b", "c"),
        ),
    )
    skeleton, search = _search_h(graph, k=2)

    record = _h_lift_for_vertices(skeleton, search, ("a", "b", "c"))

    assert record.h_lift_count == 2 * 3 * 5


def test_left_degenerate_two_simplex_repeats_non_loop_factor() -> None:
    graph = GraphInput(
        vertices=(InputVertex("s"), InputVertex("t")),
        edges=(
            InputEdge("loop1", "s", "s"),
            InputEdge("loop2", "s", "s"),
            InputEdge("st1", "s", "t"),
            InputEdge("st2", "s", "t"),
            InputEdge("st3", "s", "t"),
        ),
    )
    skeleton, search = _search_h(graph, k=2)

    record = _h_lift_for_vertices(skeleton, search, ("s", "s", "t"))

    assert record.h_lift_count == 2 * 3 * 3


def test_right_degenerate_two_simplex_repeats_non_loop_factor() -> None:
    graph = GraphInput(
        vertices=(InputVertex("s"), InputVertex("t")),
        edges=(
            InputEdge("st1", "s", "t"),
            InputEdge("st2", "s", "t"),
            InputEdge("loop_t1", "t", "t"),
            InputEdge("loop_t2", "t", "t"),
            InputEdge("loop_t3", "t", "t"),
        ),
    )
    skeleton, search = _search_h(graph, k=2)

    record = _h_lift_for_vertices(skeleton, search, ("s", "t", "t"))

    assert record.h_lift_count == 2 * 2 * 3


def test_totally_degenerate_two_simplex_counts_loop_cubed() -> None:
    graph = GraphInput(
        vertices=(InputVertex("s"),),
        edges=(InputEdge("loop1", "s", "s"), InputEdge("loop2", "s", "s")),
    )
    skeleton, search = _search_h(graph, k=2)

    record = _h_lift_for_vertices(skeleton, search, ("s", "s", "s"))

    assert record.h_lift_count == 2**3


def test_missing_non_loop_fiber_is_invariant_error() -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b")),
        edges=(InputEdge("ab", "a", "b"),),
    )
    skeleton, search = _search_h(graph, k=1)
    corrupted = replace(
        skeleton,
        edge_fibers_by_pair={},
        edge_fibers_by_skeleton_edge_id={},
        skeleton_edge_id_by_pair={},
    )

    with pytest.raises(SimplexInvariantError, match="Missing non-loop"):
        _h_lift_for_vertices(corrupted, search, ("a", "b"))


def test_h_lift_diagnostics_separate_positive_and_total_counts() -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b")),
        edges=(InputEdge("ab1", "a", "b"), InputEdge("ab2", "a", "b")),
    )
    skeleton, search = _search_h(graph, k=1)
    records = compute_h_lifts_for_tier_zero(
        skeletonization=skeleton,
        skeleton_search=search,
        tier0_vertex_id_to_input_vertex_id={"a": "a", "b": "b"},
    )

    diagnostics = build_h_lift_diagnostics(records)

    assert diagnostics.simplex_count_by_degree[1] == 3
    assert diagnostics.zero_lift_simplex_count_by_degree[1] == 2
    assert diagnostics.positive_simplex_count_by_degree[1] == 1
    assert diagnostics.total_h_lift_count_by_degree[1] == 2


def _search_h(graph: GraphInput, *, k: int) -> tuple[SkeletonizationResult, SimplexSearchResult]:
    skeleton = skeletonize_graph(graph)
    normalized = normalize_graph(skeleton.skeleton_graph)
    simplices_by_degree = enumerate_direct_simplices(normalized, tier=0, k=k)
    return skeleton, SimplexSearchResult(
        k=k,
        bottom_tier=0,
        simplices_by_tier_degree={
            (0, degree): simplices for degree, simplices in simplices_by_degree.items()
        },
    )


def _h_lift_for_vertices(
    skeleton: SkeletonizationResult,
    search: SimplexSearchResult,
    vertices: tuple[str, ...],
) -> SimplexHLiftRecord:
    records = compute_h_lifts_for_tier_zero(
        skeletonization=skeleton,
        skeleton_search=search,
        tier0_vertex_id_to_input_vertex_id={
            vertex.id: vertex.id for vertex in skeleton.original_graph.vertices
        },
    )
    for record in records:
        if record.input_vertices == vertices:
            return record
    raise AssertionError(f"Missing H-lift record for {vertices!r}.")
