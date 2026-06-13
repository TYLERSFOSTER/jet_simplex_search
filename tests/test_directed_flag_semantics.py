import pytest

from jet_simplex_search.errors import SimplexInvariantError
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from jet_simplex_search.normalize import normalize_graph
from jet_simplex_search.search import enumerate_direct_simplices, extend_simplex_direct


def test_path_without_long_face_does_not_emit_two_simplex() -> None:
    graph = normalize_graph(
        GraphInput(
            vertices=(InputVertex("0"), InputVertex("1"), InputVertex("2")),
            edges=(InputEdge("01", "0", "1"), InputEdge("12", "1", "2")),
        )
    )

    simplices = enumerate_direct_simplices(graph, tier=0, k=2)

    assert ("0", "1", "2") not in {simplex.vertices for simplex in simplices[2]}


def test_long_face_allows_two_simplex() -> None:
    graph = normalize_graph(
        GraphInput(
            vertices=(InputVertex("0"), InputVertex("1"), InputVertex("2")),
            edges=(
                InputEdge("01", "0", "1"),
                InputEdge("02", "0", "2"),
                InputEdge("12", "1", "2"),
            ),
        )
    )

    simplices = enumerate_direct_simplices(graph, tier=0, k=2)

    assert ("0", "1", "2") in {simplex.vertices for simplex in simplices[2]}


def test_extension_outside_frontier_fails() -> None:
    graph = normalize_graph(GraphInput(vertices=(InputVertex("0"), InputVertex("1"))))
    simplex = enumerate_direct_simplices(graph, tier=0, k=0)[0][0]

    with pytest.raises(SimplexInvariantError, match="not in frontier"):
        extend_simplex_direct(graph, simplex, "1")


def test_degenerate_extension_uses_identity_witness() -> None:
    graph = normalize_graph(
        GraphInput(
            vertices=(InputVertex("s"), InputVertex("t")),
            edges=(InputEdge("st", "s", "t"),),
        )
    )
    simplices = enumerate_direct_simplices(graph, tier=0, k=2)
    degenerate = next(
        simplex for simplex in simplices[2] if simplex.vertices == ("s", "s", "t")
    )

    edge_ids = tuple(
        edge_id
        for witness in degenerate.face_edge_witnesses
        for edge_id in witness.edge_ids
    )
    assert "st" in edge_ids
    assert any(edge_id.startswith("jss:identity") for edge_id in edge_ids)
