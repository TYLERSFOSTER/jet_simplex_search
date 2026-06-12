from jet_simplex_search.ids import fiber_id, identity_edge_id, simplex_id


def test_identity_edge_id_is_stable_and_prefixed() -> None:
    assert identity_edge_id("s") == identity_edge_id("s")
    assert identity_edge_id("s") != "edge-s"


def test_simplex_id_distinguishes_tier_degree_and_vertices() -> None:
    base = simplex_id(0, 1, ("a", "b"))

    assert base == simplex_id(0, 1, ("a", "b"))
    assert base != simplex_id(1, 1, ("a", "b"))
    assert base != simplex_id(0, 2, ("a", "b", "c"))
    assert base != simplex_id(0, 1, ("b", "a"))


def test_fiber_id_is_stable() -> None:
    assert fiber_id("simplex", 0) == fiber_id("simplex", 0)
    assert fiber_id("simplex", 0) != fiber_id("simplex", 1)

