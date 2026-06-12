from __future__ import annotations

from dataclasses import dataclass

from jet_simplex_search.ids import identity_edge_id


@dataclass(frozen=True, slots=True)
class FakeStaticTowerAdapter:
    """Tiny static tower used by lift tests.

    Tier 1 is downstairs with vertices C, D and edge C -> D.
    Tier 0 is upstairs with a, b over C and d over D. The edge a -> b lies over
    id_C, so a nondegenerate upstairs edge can sit over a degenerate downstairs
    edge.
    """

    def tiers(self) -> tuple[int, ...]:
        return (0, 1)

    def bottommost_nondegenerate_tier(self) -> int:
        return 1

    def tier_vertices(self, tier: int) -> tuple[str, ...]:
        if tier == 1:
            return ("C", "D")
        if tier == 0:
            return ("a", "b", "d")
        return ()

    def tier_edges(self, tier: int) -> tuple[str, ...]:
        if tier == 1:
            return ("CD",)
        if tier == 0:
            return ("ab", "ad", "bd")
        return ()

    def edge_source(self, tier: int, edge_id: str) -> str:
        return {
            (1, "CD"): "C",
            (0, "ab"): "a",
            (0, "ad"): "a",
            (0, "bd"): "b",
        }[(tier, edge_id)]

    def edge_target(self, tier: int, edge_id: str) -> str:
        return {
            (1, "CD"): "D",
            (0, "ab"): "b",
            (0, "ad"): "d",
            (0, "bd"): "d",
        }[(tier, edge_id)]

    def project_vertex(self, tier: int, vertex_id: str) -> str:
        if tier != 0:
            msg = "fake adapter only projects from tier 0"
            raise KeyError(msg)
        return {"a": "C", "b": "C", "d": "D"}[vertex_id]

    def project_edge(self, tier: int, edge_id: str) -> str:
        if tier != 0:
            msg = "fake adapter only projects edges from tier 0"
            raise KeyError(msg)
        return {
            "ab": identity_edge_id("C"),
            "ad": "CD",
            "bd": "CD",
            identity_edge_id("a"): identity_edge_id("C"),
            identity_edge_id("b"): identity_edge_id("C"),
            identity_edge_id("d"): identity_edge_id("D"),
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
            (identity_edge_id("C"), "a"): frozenset({"a", "b"}),
            (identity_edge_id("C"), "b"): frozenset({"b"}),
            (identity_edge_id("D"), "d"): frozenset({"d"}),
            ("CD", "a"): frozenset({"d"}),
            ("CD", "b"): frozenset({"d"}),
        }
        return lookup.get((downstairs_edge_id, upstairs_source_id), frozenset())

