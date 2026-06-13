from jet_simplex_search.diagnostics import SummaryStats, build_search_diagnostics
from jet_simplex_search.search import run_static_small_object_search

from tests.fakes import FakeStaticTowerAdapter


def test_summary_stats_handles_values_and_empty() -> None:
    assert SummaryStats.from_values(()).to_dict() == {
        "count": 0,
        "minimum": None,
        "maximum": None,
        "mean": None,
    }
    assert SummaryStats.from_values((1, 3)).to_dict()["mean"] == 2.0


def test_search_diagnostics_counts_simplices_and_degenerates() -> None:
    result = run_static_small_object_search(FakeStaticTowerAdapter(), k=1)
    diagnostics = build_search_diagnostics(
        result.simplices_by_tier_degree,
        simplex_fiber_count=len(result.fibers),
        edge_fiber_count=len(result.edge_fibers),
    )

    assert diagnostics.emitted_simplex_count > 0
    assert diagnostics.simplex_fiber_count == len(result.fibers)
    assert diagnostics.degenerate_counts_by_tier_degree
