from jet_simplex_search.search import run_static_small_object_search

from tests.fakes import FakeStaticTowerAdapter


def test_static_search_runs_over_fake_tower() -> None:
    result = run_static_small_object_search(FakeStaticTowerAdapter(), k=1)

    assert result.bottom_tier == 1
    assert (1, 1) in result.simplices_by_tier_degree
    assert (0, 1) in result.simplices_by_tier_degree
    assert result.fibers
    assert result.edge_fibers


def test_static_search_respects_k() -> None:
    result = run_static_small_object_search(FakeStaticTowerAdapter(), k=0)

    assert all(degree == 0 for _tier, degree in result.simplices_by_tier_degree)

