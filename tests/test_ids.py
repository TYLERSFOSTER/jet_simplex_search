from jet_simplex_search.ids import (
    h_lift_id,
    identity_edge_id,
    simplex_id,
    skeleton_edge_id,
    tier_simple_edge_id,
)


def test_identity_edge_id_is_stable_and_prefixed() -> None:
    assert identity_edge_id("s") == identity_edge_id("s")
    assert identity_edge_id("s") != "edge-s"


def test_simplex_id_distinguishes_tier_degree_and_vertices() -> None:
    base = simplex_id(0, 1, ("a", "b"))

    assert base == simplex_id(0, 1, ("a", "b"))
    assert base != simplex_id(1, 1, ("a", "b"))
    assert base != simplex_id(0, 2, ("a", "b", "c"))
    assert base != simplex_id(0, 1, ("b", "a"))


def test_skeleton_edge_id_is_stable_and_escaped() -> None:
    assert skeleton_edge_id("a b", "c/d") == skeleton_edge_id("a b", "c/d")
    assert skeleton_edge_id("a b", "c/d") != skeleton_edge_id("a", "bc/d")


def test_tier_simple_edge_id_distinguishes_tier() -> None:
    assert tier_simple_edge_id(0, "a", "b") == tier_simple_edge_id(0, "a", "b")
    assert tier_simple_edge_id(0, "a", "b") != tier_simple_edge_id(1, "a", "b")


def test_h_lift_id_is_stable() -> None:
    assert h_lift_id("simplex") == h_lift_id("simplex")
    assert h_lift_id("simplex") != h_lift_id("other")
