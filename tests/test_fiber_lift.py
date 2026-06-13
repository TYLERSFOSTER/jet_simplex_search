from jet_simplex_search.ids import identity_edge_id
from jet_simplex_search.lift import lift_downstairs_extension, lift_tier_simplices
from jet_simplex_search.search import enumerate_direct_simplices
from jet_simplex_search.tower_adapter import normalized_graph_for_tier

from tests.fakes import FakeStaticTowerAdapter


def test_lift_zero_simplices_maps_downstairs_vertex_to_upstairs_preimages() -> None:
    adapter = FakeStaticTowerAdapter()
    downstairs = enumerate_direct_simplices(
        normalized_graph_for_tier(adapter, 1),
        tier=1,
        k=0,
    )[0]

    lifted = lift_tier_simplices(
        adapter=adapter,
        upstairs_tier=0,
        downstairs_simplices_by_degree={0: downstairs},
        k=0,
    )

    c_fiber = next(
        fiber for fiber in lifted.simplex_fibers if "C" in fiber.downstairs_simplex_id
    )
    assert len(c_fiber.upstairs_simplex_ids) == 2


def test_final_downstairs_edge_selects_upstairs_edge_fiber() -> None:
    adapter = FakeStaticTowerAdapter()
    downstairs_graph = normalized_graph_for_tier(adapter, 1)
    upstairs_graph = normalized_graph_for_tier(adapter, 0)
    downstairs = enumerate_direct_simplices(downstairs_graph, tier=1, k=1)
    lifted_zero = lift_tier_simplices(
        adapter=adapter,
        upstairs_tier=0,
        downstairs_simplices_by_degree={0: downstairs[0]},
        k=0,
    )
    c_prefix = next(
        simplex
        for simplex in lifted_zero.simplices_by_degree[0]
        if simplex.vertices == ("a",)
    )
    cd_simplex = next(simplex for simplex in downstairs[1] if simplex.vertices == ("C", "D"))

    lifted = lift_downstairs_extension(
        adapter=adapter,
        upstairs_tier=0,
        upstairs_graph=upstairs_graph,
        downstairs_simplex=cd_simplex,
        upstairs_prefix=c_prefix,
    )

    assert {simplex.vertices for simplex in lifted} == {("a", "d")}


def test_non_degenerate_upstairs_edge_over_degenerate_downstairs_edge_is_emitted() -> None:
    adapter = FakeStaticTowerAdapter()
    downstairs = enumerate_direct_simplices(
        normalized_graph_for_tier(adapter, 1),
        tier=1,
        k=1,
    )

    lifted = lift_tier_simplices(
        adapter=adapter,
        upstairs_tier=0,
        downstairs_simplices_by_degree=downstairs,
        k=1,
    )

    downstairs_degenerate = next(
        simplex for simplex in downstairs[1] if simplex.vertices == ("C", "C")
    )
    fiber = next(
        fiber
        for fiber in lifted.simplex_fibers
        if fiber.downstairs_simplex_id == downstairs_degenerate.id
    )
    lifted_simplices = {
        simplex.id: simplex
        for simplex in lifted.simplices_by_degree[1]
    }

    assert any(
        lifted_simplices[simplex_id].vertices == ("a", "b")
        for simplex_id in fiber.upstairs_simplex_ids
    )


def test_candidate_must_be_in_frontier_and_edge_fiber() -> None:
    adapter = FakeStaticTowerAdapter()
    downstairs = enumerate_direct_simplices(
        normalized_graph_for_tier(adapter, 1),
        tier=1,
        k=1,
    )

    lifted = lift_tier_simplices(
        adapter=adapter,
        upstairs_tier=0,
        downstairs_simplices_by_degree=downstairs,
        k=1,
    )

    cd_fiber = next(
        fiber
        for fiber in lifted.simplex_fibers
        if any(
            simplex.vertices == ("C", "D")
            and simplex.id == fiber.downstairs_simplex_id
            for simplex in downstairs[1]
        )
    )
    lifted_edges = {
        simplex.id: simplex.vertices
        for simplex in lifted.simplices_by_degree[1]
    }

    assert {lifted_edges[simplex_id] for simplex_id in cd_fiber.upstairs_simplex_ids} == {
        ("a", "d"),
        ("b", "d"),
    }


def test_missing_downstairs_two_simplex_prevents_upstairs_triangle_search() -> None:
    adapter = TriangleOverBoundaryAdapter()
    downstairs_all = enumerate_direct_simplices(
        normalized_graph_for_tier(adapter, 1),
        tier=1,
        k=2,
    )
    downstairs_without_interiors = {
        0: downstairs_all[0],
        1: downstairs_all[1],
        2: (),
    }

    lifted = lift_tier_simplices(
        adapter=adapter,
        upstairs_tier=0,
        downstairs_simplices_by_degree=downstairs_without_interiors,
        k=2,
    )

    assert lifted.simplices_by_degree[2] == ()


class TriangleOverBoundaryAdapter:
    """Fake tower where upstairs has a triangle but no downstairs 2-record is supplied."""

    def tiers(self) -> tuple[int, ...]:
        return (0, 1)

    def bottommost_nondegenerate_tier(self) -> int:
        return 1

    def tier_vertices(self, tier: int) -> tuple[str, ...]:
        if tier == 1:
            return ("C", "D", "E")
        if tier == 0:
            return ("a", "b", "c")
        return ()

    def tier_edges(self, tier: int) -> tuple[str, ...]:
        if tier == 1:
            return ("CD", "CE", "DE")
        if tier == 0:
            return ("ab", "ac", "bc")
        return ()

    def edge_source(self, tier: int, edge_id: str) -> str:
        return {
            (1, "CD"): "C",
            (1, "CE"): "C",
            (1, "DE"): "D",
            (0, "ab"): "a",
            (0, "ac"): "a",
            (0, "bc"): "b",
        }[(tier, edge_id)]

    def edge_target(self, tier: int, edge_id: str) -> str:
        return {
            (1, "CD"): "D",
            (1, "CE"): "E",
            (1, "DE"): "E",
            (0, "ab"): "b",
            (0, "ac"): "c",
            (0, "bc"): "c",
        }[(tier, edge_id)]

    def project_vertex(self, tier: int, vertex_id: str) -> str:
        if tier != 0:
            raise KeyError("fake adapter only projects tier 0")
        return {"a": "C", "b": "D", "c": "E"}[vertex_id]

    def project_edge(self, tier: int, edge_id: str) -> str:
        if tier != 0:
            raise KeyError("fake adapter only projects tier 0")
        return {
            "ab": "CD",
            "ac": "CE",
            "bc": "DE",
            identity_edge_id("a"): identity_edge_id("C"),
            identity_edge_id("b"): identity_edge_id("D"),
            identity_edge_id("c"): identity_edge_id("E"),
        }[edge_id]

    def edge_fiber_targets(
        self,
        *,
        upstairs_tier: int,
        downstairs_edge_id: str,
        upstairs_source_id: str,
    ) -> frozenset[str]:
        if upstairs_tier != 0:
            return frozenset()
        lookup = {
            ("CD", "a"): frozenset({"b"}),
            ("CE", "a"): frozenset({"c"}),
            ("DE", "b"): frozenset({"c"}),
            (identity_edge_id("C"), "a"): frozenset({"a"}),
            (identity_edge_id("D"), "b"): frozenset({"b"}),
            (identity_edge_id("E"), "c"): frozenset({"c"}),
        }
        return lookup.get((downstairs_edge_id, upstairs_source_id), frozenset())
