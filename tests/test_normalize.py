import pytest

from jet_simplex_search.errors import InvalidGraphError, SimplexInvariantError
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from jet_simplex_search.ids import identity_edge_id
from jet_simplex_search.normalize import (
    NormalizedEdge,
    NormalizedGraph,
    assert_normalized_graph_invariants,
    assert_simple_reflexive_normalized_graph,
    normalize_graph,
)
from jet_simplex_search.skeleton import skeletonize_graph


def test_no_loop_graph_gains_one_identity_per_vertex() -> None:
    graph = GraphInput(vertices=(InputVertex("s"), InputVertex("t")))

    normalized = normalize_graph(graph)

    assert normalized.edge_lookup[("s", "s")] == (identity_edge_id("s"),)
    assert normalized.edge_lookup[("t", "t")] == (identity_edge_id("t"),)
    assert normalized.adjacency_targets["s"] == frozenset({"s"})


def test_input_loop_is_stripped_and_recorded() -> None:
    graph = GraphInput(vertices=(InputVertex("s"),), edges=(InputEdge("loop", "s", "s"),))

    normalized = normalize_graph(graph)

    assert normalized.stripped_loop_edge_ids == ("loop",)
    assert normalized.edge_lookup[("s", "s")] == (identity_edge_id("s"),)


def test_non_loop_edges_are_preserved_in_adjacency_and_lookup() -> None:
    graph = GraphInput(
        vertices=(InputVertex("s"), InputVertex("t")),
        edges=(InputEdge("e", "s", "t"),),
    )

    normalized = normalize_graph(graph)

    assert "t" in normalized.adjacency_targets["s"]
    assert normalized.edge_lookup[("s", "t")] == ("e",)


def test_parallel_edges_are_preserved_in_lookup() -> None:
    graph = GraphInput(
        vertices=(InputVertex("s"), InputVertex("t")),
        edges=(InputEdge("e1", "s", "t"), InputEdge("e2", "s", "t")),
    )

    normalized = normalize_graph(graph)

    assert normalized.edge_lookup[("s", "t")] == ("e1", "e2")


def test_identity_id_collision_is_rejected() -> None:
    graph = GraphInput(
        vertices=(InputVertex("s"), InputVertex("t")),
        edges=(InputEdge(identity_edge_id("s"), "s", "t"),),
    )

    with pytest.raises(InvalidGraphError, match="collides"):
        normalize_graph(graph)


def test_invariant_checker_rejects_missing_identity() -> None:
    graph = NormalizedGraph(
        vertices=("s",),
        edges=(),
        adjacency_targets={"s": frozenset({"s"})},
        edge_lookup={},
        stripped_loop_edge_ids=(),
    )

    with pytest.raises(SimplexInvariantError, match="exactly one identity"):
        assert_normalized_graph_invariants(graph)


def test_invariant_checker_rejects_original_loop() -> None:
    graph = NormalizedGraph(
        vertices=("s",),
        edges=(
            NormalizedEdge(identity_edge_id("s"), "s", "s", "identity"),
            NormalizedEdge("loop", "s", "s", "original", "loop"),
        ),
        adjacency_targets={"s": frozenset({"s"})},
        edge_lookup={("s", "s"): (identity_edge_id("s"), "loop")},
        stripped_loop_edge_ids=(),
    )

    with pytest.raises(SimplexInvariantError, match="must not be a loop"):
        assert_normalized_graph_invariants(graph)


def test_simple_reflexive_checker_rejects_parallel_edges() -> None:
    graph = GraphInput(
        vertices=(InputVertex("s"), InputVertex("t")),
        edges=(InputEdge("e1", "s", "t"), InputEdge("e2", "s", "t")),
    )
    normalized = normalize_graph(graph)

    with pytest.raises(SimplexInvariantError, match="exactly one edge"):
        assert_simple_reflexive_normalized_graph(normalized)


def test_normalized_skeleton_graph_is_simple_reflexive() -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b")),
        edges=(
            InputEdge("ab1", "a", "b"),
            InputEdge("ab2", "a", "b"),
            InputEdge("loop_a_1", "a", "a"),
            InputEdge("loop_a_2", "a", "a"),
        ),
    )

    skeleton = skeletonize_graph(graph)
    normalized = normalize_graph(skeleton.skeleton_graph)

    assert_simple_reflexive_normalized_graph(normalized)
    assert normalized.edge_lookup[("a", "a")] == (identity_edge_id("a"),)
    assert normalized.edge_lookup[("b", "b")] == (identity_edge_id("b"),)
    assert len(normalized.edge_lookup[("a", "b")]) == 1
