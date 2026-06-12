import pytest

from jet_simplex_search.errors import InvalidGraphError
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex, graph_from_edges


def test_constructs_one_vertex_graph() -> None:
    graph = GraphInput(vertices=(InputVertex("s"),))

    assert graph.vertices[0].id == "s"
    assert graph.edges == ()


def test_constructs_one_edge_graph() -> None:
    graph = GraphInput(
        vertices=(InputVertex("s"), InputVertex("t")),
        edges=(InputEdge("e", "s", "t", labels=("x",)),),
    )

    assert graph.edges[0].labels == ("x",)


def test_rejects_duplicate_vertices() -> None:
    with pytest.raises(InvalidGraphError, match="Duplicate vertex"):
        GraphInput(vertices=(InputVertex("s"), InputVertex("s")))


def test_rejects_duplicate_edges() -> None:
    with pytest.raises(InvalidGraphError, match="Duplicate edge"):
        GraphInput(
            vertices=(InputVertex("s"), InputVertex("t")),
            edges=(InputEdge("e", "s", "t"), InputEdge("e", "t", "s")),
        )


def test_rejects_missing_source_or_target() -> None:
    with pytest.raises(InvalidGraphError, match="missing source"):
        GraphInput(vertices=(InputVertex("t"),), edges=(InputEdge("e", "s", "t"),))
    with pytest.raises(InvalidGraphError, match="missing target"):
        GraphInput(vertices=(InputVertex("s"),), edges=(InputEdge("e", "s", "t"),))


def test_graph_from_edges_builds_vertices() -> None:
    graph = graph_from_edges((("b", "a"),))

    assert tuple(vertex.id for vertex in graph.vertices) == ("a", "b")
    assert graph.edges[0].source == "b"

