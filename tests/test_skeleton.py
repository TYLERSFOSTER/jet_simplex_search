import pytest

from jet_simplex_search.errors import InvalidGraphError, SimplexInvariantError
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from jet_simplex_search.ids import skeleton_edge_id
from jet_simplex_search.skeleton import (
    SkeletonEdgeFiber,
    SkeletonLoopFiber,
    SkeletonizationResult,
    assert_skeletonization_invariants,
    skeletonize_graph,
)


def test_skeleton_edge_fiber_rejects_loop_pair() -> None:
    with pytest.raises(SimplexInvariantError, match="source != target"):
        SkeletonEdgeFiber("s", "s", "edge", ("loop",))


def test_loop_fiber_allows_empty_original_loop_ids() -> None:
    fiber = SkeletonLoopFiber("s")

    assert fiber.original_loop_edge_ids == ()


def test_one_vertex_no_edges_has_empty_loop_fiber() -> None:
    graph = GraphInput(vertices=(InputVertex("s"),))

    result = skeletonize_graph(graph)

    assert result.skeleton_graph.vertices == (InputVertex("s"),)
    assert result.skeleton_graph.edges == ()
    assert result.loop_fibers_by_vertex["s"].original_loop_edge_ids == ()
    assert result.diagnostics.input_loop_edge_count == 0


def test_single_non_loop_edge_is_preserved_as_skeleton_edge() -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b")),
        edges=(InputEdge("ab", "a", "b"),),
    )

    result = skeletonize_graph(graph)

    edge_id = skeleton_edge_id("a", "b")
    assert result.skeleton_graph.edges == (InputEdge(edge_id, "a", "b"),)
    assert result.edge_fibers_by_pair[("a", "b")].original_edge_ids == ("ab",)
    assert result.skeleton_edge_id_by_original_edge_id["ab"] == edge_id


def test_parallel_non_loop_edges_collapse_to_one_skeleton_edge() -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b")),
        edges=(
            InputEdge("ab2", "a", "b"),
            InputEdge("ab1", "a", "b"),
            InputEdge("ab3", "a", "b"),
        ),
    )

    result = skeletonize_graph(graph)

    assert len(result.skeleton_graph.edges) == 1
    assert result.edge_fibers_by_pair[("a", "b")].original_edge_ids == (
        "ab1",
        "ab2",
        "ab3",
    )
    assert result.diagnostics.collapsed_parallel_non_loop_edge_count == 2
    assert result.diagnostics.maximum_non_loop_fiber_size == 3


def test_input_loops_are_stored_as_loop_fibers_not_skeleton_edges() -> None:
    graph = GraphInput(
        vertices=(InputVertex("s"),),
        edges=(InputEdge("loop2", "s", "s"), InputEdge("loop1", "s", "s")),
    )

    result = skeletonize_graph(graph)

    assert result.skeleton_graph.edges == ()
    assert result.loop_fibers_by_vertex["s"].original_loop_edge_ids == (
        "loop1",
        "loop2",
    )
    assert result.original_loop_vertex_by_edge_id == {"loop1": "s", "loop2": "s"}
    assert result.diagnostics.collapsed_loop_edge_count == 2
    assert result.diagnostics.maximum_loop_fiber_size == 2


def test_v01_label_policy_allows_exact_parallel_edge_label_agreement() -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b")),
        edges=(
            InputEdge("ab1", "a", "b", labels=("x",)),
            InputEdge("ab2", "a", "b", labels=("x",)),
        ),
    )

    result = skeletonize_graph(graph)

    assert result.skeleton_graph.edges[0].labels == ("x",)
    assert result.edge_fibers_by_pair[("a", "b")].labels == ("x",)


def test_v01_label_policy_requires_exact_parallel_edge_label_agreement() -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b")),
        edges=(
            InputEdge("ab1", "a", "b", labels=("x",)),
            InputEdge("ab2", "a", "b", labels=("y",)),
        ),
    )

    with pytest.raises(InvalidGraphError, match="different labels"):
        skeletonize_graph(graph)


def test_skeletonization_invariant_rejects_missing_loop_fiber() -> None:
    graph = GraphInput(vertices=(InputVertex("s"),))
    result = SkeletonizationResult(
        original_graph=graph,
        skeleton_graph=graph,
        edge_fibers_by_pair={},
        edge_fibers_by_skeleton_edge_id={},
        loop_fibers_by_vertex={},
        skeleton_edge_id_by_pair={},
        skeleton_edge_id_by_original_edge_id={},
        original_loop_vertex_by_edge_id={},
        diagnostics=skeletonize_graph(graph).diagnostics,
    )

    with pytest.raises(SimplexInvariantError, match="loop fiber"):
        assert_skeletonization_invariants(result)
