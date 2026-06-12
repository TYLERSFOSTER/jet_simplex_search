from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from jet_simplex_search.normalize import normalize_graph
from jet_simplex_search.search import enumerate_direct_simplices


def test_isolated_vertex_emits_degenerates_through_k() -> None:
    graph = normalize_graph(GraphInput(vertices=(InputVertex("s"),)))

    simplices = enumerate_direct_simplices(graph, tier=0, k=2)

    assert [simplex.vertices for simplex in simplices[0]] == [("s",)]
    assert [simplex.vertices for simplex in simplices[1]] == [("s", "s")]
    assert [simplex.vertices for simplex in simplices[2]] == [("s", "s", "s")]


def test_single_edge_emits_identity_and_edge_simplices() -> None:
    graph = normalize_graph(
        GraphInput(
            vertices=(InputVertex("s"), InputVertex("t")),
            edges=(InputEdge("st", "s", "t"),),
        )
    )

    simplices = enumerate_direct_simplices(graph, tier=0, k=1)

    assert {simplex.vertices for simplex in simplices[1]} == {
        ("s", "s"),
        ("s", "t"),
        ("t", "t"),
    }


def test_triangle_emits_directed_two_simplex() -> None:
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


def test_no_degree_above_k_is_emitted() -> None:
    graph = normalize_graph(GraphInput(vertices=(InputVertex("s"),)))

    simplices = enumerate_direct_simplices(graph, tier=0, k=1)

    assert set(simplices) == {0, 1}


def test_records_carry_prefix_target_frontier_and_witnesses() -> None:
    graph = normalize_graph(
        GraphInput(
            vertices=(InputVertex("s"), InputVertex("t")),
            edges=(InputEdge("st", "s", "t"),),
        )
    )

    simplex = next(
        simplex
        for simplex in enumerate_direct_simplices(graph, tier=0, k=1)[1]
        if simplex.vertices == ("s", "t")
    )

    assert simplex.prefix_simplex_id is not None
    assert simplex.target_vertex == "t"
    assert simplex.frontier == frozenset({"t"})
    assert simplex.face_edge_witnesses

