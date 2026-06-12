"""Static tower adapter boundary."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from jet_simplex_search.errors import TowerAdapterError
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from jet_simplex_search.ids import identity_edge_id, identity_edge_vertex_id
from jet_simplex_search.normalize import NormalizedGraph, normalize_graph


class StaticTowerAdapterProtocol(Protocol):
    """Protocol for static tower queries used by simplex search."""

    def tiers(self) -> tuple[int, ...]:
        """Return available tiers."""

    def bottommost_nondegenerate_tier(self) -> int:
        """Return `G^ell`, the bottommost nondegenerate tier."""

    def tier_vertices(self, tier: int) -> tuple[str, ...]:
        """Return tier-local vertex/cell ids."""

    def tier_edges(self, tier: int) -> tuple[str, ...]:
        """Return tier-local non-identity edge ids."""

    def edge_source(self, tier: int, edge_id: str) -> str:
        """Return the tier-local source of an edge."""

    def edge_target(self, tier: int, edge_id: str) -> str:
        """Return the tier-local target of an edge."""

    def project_vertex(self, tier: int, vertex_id: str) -> str:
        """Project a vertex from `tier` to `tier + 1`."""

    def project_edge(self, tier: int, edge_id: str) -> str:
        """Project an edge from `tier` to `tier + 1`."""

    def edge_fiber_targets(
        self,
        *,
        upstairs_tier: int,
        downstairs_edge_id: str,
        upstairs_source_id: str,
    ) -> frozenset[str]:
        """Return upstairs edge targets over a downstairs edge from one source."""


def normalized_graph_for_tier(
    adapter: StaticTowerAdapterProtocol,
    tier: int,
) -> NormalizedGraph:
    """Build the normalized graph view of one static tower tier."""

    vertices = tuple(InputVertex(vertex_id) for vertex_id in adapter.tier_vertices(tier))
    edges = tuple(
        InputEdge(
            id=edge_id,
            source=adapter.edge_source(tier, edge_id),
            target=adapter.edge_target(tier, edge_id),
        )
        for edge_id in adapter.tier_edges(tier)
    )
    return normalize_graph(GraphInput(vertices=vertices, edges=edges))


def state_cell_id_string(tier: int, ordinal: int) -> str:
    """Return the local string id for a state cell."""

    return f"cell:{tier}:{ordinal}"


def action_cell_edge_id(tier: int, ordinal: int) -> str:
    """Return the local string edge id for an action cell."""

    return f"action:{tier}:{ordinal}"


@dataclass(slots=True)
class StateCollapserStaticTowerAdapter:
    """Static adapter over `state_collapser`'s `PartitionTower`."""

    tower: object
    normalized_graph: NormalizedGraph
    state_by_vertex_id: dict[str, object]
    base_edge_by_normalized_id: dict[str, object]
    _edge_source_cache: dict[tuple[int, str], str] = field(default_factory=dict)
    _edge_target_cache: dict[tuple[int, str], str] = field(default_factory=dict)

    @classmethod
    def from_graph(
        cls,
        graph: GraphInput,
        *,
        schema: object | None = None,
    ) -> StateCollapserStaticTowerAdapter:
        """Build a real static tower adapter from a graph input."""

        from state_collapser.core.action import PrimitiveAction
        from state_collapser.core.edges import BaseEdge
        from state_collapser.core.state import State
        from state_collapser.tower.partition.tower import build_partition_tower_full

        normalized = normalize_graph(graph)
        state_by_vertex_id = {
            vertex_id: State(
                payload=vertex_id,
                identity=("jet-simplex-search", "vertex", vertex_id),
            )
            for vertex_id in normalized.vertices
        }
        base_edge_by_normalized_id = {}
        for edge in normalized.edges:
            action = PrimitiveAction(
                payload=edge.id,
                identity=("jet-simplex-search", "edge", edge.id),
                labels=edge.labels,
            )
            base_edge_by_normalized_id[edge.id] = BaseEdge(
                source=state_by_vertex_id[edge.source],
                action=action,
                target=state_by_vertex_id[edge.target],
                labels=(*edge.labels, f"jss:{edge.kind}"),
            )
        tower = build_partition_tower_full(
            states=tuple(state_by_vertex_id.values()),
            edges=tuple(base_edge_by_normalized_id.values()),
            current_state=None,
            schema=schema,
        )
        return cls(
            tower=tower,
            normalized_graph=normalized,
            state_by_vertex_id=state_by_vertex_id,
            base_edge_by_normalized_id=base_edge_by_normalized_id,
        )

    def tiers(self) -> tuple[int, ...]:
        return tuple(range(len(self.tower.state_layers)))  # type: ignore[attr-defined]

    def bottommost_nondegenerate_tier(self) -> int:
        for tier in reversed(self.tiers()):
            if not self._is_pi0(tier):
                return tier
        tiers = self.tiers()
        return tiers[-1] if tiers else 0

    def tier_vertices(self, tier: int) -> tuple[str, ...]:
        layer = self.tower.state_layers[tier]  # type: ignore[attr-defined]
        return tuple(
            self._state_cell_to_string(cell_id)
            for cell_id in layer.all_cell_ids()
        )

    def tier_edges(self, tier: int) -> tuple[str, ...]:
        action_layer = self.tower.action_layers[tier]  # type: ignore[attr-defined]
        edge_ids: list[str] = []
        for state_cell_id in self.tower.state_layers[tier].all_cell_ids():  # type: ignore[attr-defined]
            for action_cell_id in self.tower.outgoing_action_cells(tier, state_cell_id):  # type: ignore[attr-defined]
                target_cell_id = action_layer.target_cell_by_action_cell.get(action_cell_id)
                if target_cell_id is None:
                    continue
                edge_id = self._action_cell_to_edge_id(action_cell_id)
                self._edge_source_cache[(tier, edge_id)] = self._state_cell_to_string(
                    state_cell_id
                )
                self._edge_target_cache[(tier, edge_id)] = self._state_cell_to_string(
                    target_cell_id
                )
                edge_ids.append(edge_id)
        return tuple(sorted(edge_ids))

    def edge_source(self, tier: int, edge_id: str) -> str:
        if edge_id.startswith("jss:identity:"):
            return identity_edge_vertex_id(edge_id)
        self._ensure_edge_cache(tier)
        return self._edge_source_cache[(tier, edge_id)]

    def edge_target(self, tier: int, edge_id: str) -> str:
        if edge_id.startswith("jss:identity:"):
            return identity_edge_vertex_id(edge_id)
        self._ensure_edge_cache(tier)
        return self._edge_target_cache[(tier, edge_id)]

    def project_vertex(self, tier: int, vertex_id: str) -> str:
        if tier + 1 >= len(self.tower.state_layers):  # type: ignore[attr-defined]
            raise KeyError(f"Tier {tier!r} has no downstairs projection.")
        cell_id = self._string_to_state_cell(vertex_id)
        members = self.tower.state_layers[tier].members(cell_id)  # type: ignore[attr-defined]
        if not members:
            raise KeyError(f"State cell {vertex_id!r} has no members.")
        downstairs_cell = self.tower.state_layers[tier + 1].cell_of(members[0])  # type: ignore[attr-defined]
        return self._state_cell_to_string(downstairs_cell)

    def project_edge(self, tier: int, edge_id: str) -> str:
        if edge_id.startswith("jss:identity:"):
            projected_source = self.project_vertex(tier, identity_edge_vertex_id(edge_id))
            return identity_edge_id(projected_source)
        action_cell_id = self._edge_id_to_action_cell(edge_id)
        members = self.tower.action_cell_members(tier, action_cell_id)  # type: ignore[attr-defined]
        if not members:
            raise KeyError(f"Action cell edge {edge_id!r} has no members.")
        representative = members[0]
        projected_source = self.project_vertex(tier, self.edge_source(tier, edge_id))
        projected_target = self.project_vertex(tier, self.edge_target(tier, edge_id))
        if projected_source == projected_target:
            return identity_edge_id(projected_source)
        downstairs_action_cell = self.tower.action_cell_for_edge(tier + 1, representative)  # type: ignore[attr-defined]
        if downstairs_action_cell is None:
            raise TowerAdapterError(
                f"Edge {edge_id!r} projects from {projected_source!r} to "
                f"{projected_target!r}, but no downstream action cell was found."
            )
        return self._action_cell_to_edge_id(downstairs_action_cell)

    def edge_fiber_targets(
        self,
        *,
        upstairs_tier: int,
        downstairs_edge_id: str,
        upstairs_source_id: str,
    ) -> frozenset[str]:
        targets: set[str] = set()
        identity_id = identity_edge_id(upstairs_source_id)
        if self.project_edge(upstairs_tier, identity_id) == downstairs_edge_id:
            targets.add(upstairs_source_id)
        for edge_id in self.tier_edges(upstairs_tier):
            if self.edge_source(upstairs_tier, edge_id) != upstairs_source_id:
                continue
            if self.project_edge(upstairs_tier, edge_id) == downstairs_edge_id:
                targets.add(self.edge_target(upstairs_tier, edge_id))
        return frozenset(targets)

    def _is_pi0(self, tier: int) -> bool:
        return len(self.tower.state_layers[tier].all_cell_ids()) <= 1  # type: ignore[attr-defined]

    def _ensure_edge_cache(self, tier: int) -> None:
        for edge_id in self.tier_edges(tier):
            if (tier, edge_id) not in self._edge_source_cache:
                raise KeyError(f"Missing cached edge {edge_id!r} at tier {tier}.")

    @staticmethod
    def _state_cell_to_string(cell_id: object) -> str:
        return state_cell_id_string(cell_id.tier, cell_id.ordinal)  # type: ignore[attr-defined]

    @staticmethod
    def _string_to_state_cell(value: str) -> object:
        from state_collapser.tower.partition.ids import StateCellId

        prefix, tier, ordinal = value.split(":")
        if prefix != "cell":
            raise KeyError(f"Not a state-cell id: {value!r}.")
        return StateCellId(tier=int(tier), ordinal=int(ordinal))

    @staticmethod
    def _action_cell_to_edge_id(action_cell_id: object) -> str:
        return action_cell_edge_id(action_cell_id.tier, action_cell_id.ordinal)  # type: ignore[attr-defined]

    @staticmethod
    def _edge_id_to_action_cell(edge_id: str) -> object:
        from state_collapser.tower.partition.ids import ActionCellId

        prefix, tier, ordinal = edge_id.split(":")
        if prefix != "action":
            raise KeyError(f"Not an action-cell edge id: {edge_id!r}.")
        return ActionCellId(tier=int(tier), ordinal=int(ordinal))
