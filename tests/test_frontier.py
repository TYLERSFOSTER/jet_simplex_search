from jet_simplex_search.frontier import extend_frontier, initial_frontier
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from jet_simplex_search.normalize import normalize_graph


def test_initial_frontier_is_adjacency() -> None:
    graph = normalize_graph(
        GraphInput(
            vertices=(InputVertex("s"), InputVertex("t")),
            edges=(InputEdge("e", "s", "t"),),
        )
    )

    assert initial_frontier(graph, "s") == frozenset({"s", "t"})


def test_extend_frontier_intersects_sets() -> None:
    assert extend_frontier(frozenset({"a", "b"}), frozenset({"b", "c"})) == frozenset(
        {"b"}
    )


def test_repeated_vertex_leaves_frontier_unchanged() -> None:
    graph = normalize_graph(GraphInput(vertices=(InputVertex("s"),)))

    assert extend_frontier(initial_frontier(graph, "s"), initial_frontier(graph, "s")) == (
        initial_frontier(graph, "s")
    )


def test_extension_matches_full_recomputation() -> None:
    graph = normalize_graph(
        GraphInput(
            vertices=(InputVertex("a"), InputVertex("b"), InputVertex("c")),
            edges=(
                InputEdge("ab", "a", "b"),
                InputEdge("ac", "a", "c"),
                InputEdge("bc", "b", "c"),
            ),
        )
    )

    ab_frontier = extend_frontier(initial_frontier(graph, "a"), initial_frontier(graph, "b"))
    abc_frontier = extend_frontier(ab_frontier, initial_frontier(graph, "c"))
    full = (
        initial_frontier(graph, "a")
        & initial_frontier(graph, "b")
        & initial_frontier(graph, "c")
    )

    assert abc_frontier == full

