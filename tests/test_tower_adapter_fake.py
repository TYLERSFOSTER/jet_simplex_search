from jet_simplex_search.ids import identity_edge_id
from jet_simplex_search.tower_adapter import normalized_graph_for_tier

from tests.fakes import FakeStaticTowerAdapter


def test_fake_adapter_exposes_tiers_and_source_sensitive_edge_fibers() -> None:
    adapter = FakeStaticTowerAdapter()

    assert adapter.tiers() == (0, 1)
    assert adapter.bottommost_nondegenerate_tier() == 1
    assert adapter.edge_fiber_targets(
        upstairs_tier=0,
        downstairs_edge_id=identity_edge_id("C"),
        upstairs_source_id="a",
    ) == frozenset({"a", "b"})
    assert adapter.edge_fiber_targets(
        upstairs_tier=0,
        downstairs_edge_id=identity_edge_id("C"),
        upstairs_source_id="b",
    ) == frozenset({"b"})


def test_normalized_graph_for_tier_adds_identities() -> None:
    graph = normalized_graph_for_tier(FakeStaticTowerAdapter(), 0)

    assert graph.edge_lookup[("a", "a")] == (identity_edge_id("a"),)
    assert graph.edge_lookup[("a", "b")] == ("ab",)
