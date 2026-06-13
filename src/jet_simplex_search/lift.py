"""Fiber-addressed simplex lifting over a static tower."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from jet_simplex_search.ids import simplex_id
from jet_simplex_search.normalize import NormalizedGraph
from jet_simplex_search.records import (
    EdgeFiberRecord,
    SimplexFiberRecord,
    SimplexRecord,
)
from jet_simplex_search.search import extend_simplex_direct
from jet_simplex_search.tower_adapter import (
    StaticTowerAdapterProtocol,
    normalized_graph_for_tier,
)


@dataclass(frozen=True, slots=True)
class LiftedTierResult:
    """Result of lifting one downstairs tier to one upstairs tier."""

    simplices_by_degree: Mapping[int, tuple[SimplexRecord, ...]]
    simplex_fibers: tuple[SimplexFiberRecord, ...]
    edge_fibers: tuple[EdgeFiberRecord, ...]


def lift_zero_simplex(
    adapter: StaticTowerAdapterProtocol,
    *,
    upstairs_tier: int,
    downstairs_simplex: SimplexRecord,
    upstairs_graph: NormalizedGraph | None = None,
) -> tuple[SimplexRecord, ...]:
    """Lift a downstairs 0-simplex to upstairs vertices."""

    if downstairs_simplex.degree != 0:
        msg = "lift_zero_simplex requires a degree-0 downstairs simplex."
        raise ValueError(msg)
    graph = (
        normalized_graph_for_tier(adapter, upstairs_tier)
        if upstairs_graph is None
        else upstairs_graph
    )
    downstream_vertex = downstairs_simplex.vertices[0]
    emitted: list[SimplexRecord] = []
    for vertex_id in sorted(graph.vertices):
        if adapter.project_vertex(upstairs_tier, vertex_id) != downstream_vertex:
            continue
        vertices = (vertex_id,)
        emitted.append(
            SimplexRecord(
                id=simplex_id(upstairs_tier, 0, vertices),
                tier=upstairs_tier,
                degree=0,
                vertices=vertices,
                face_edge_witnesses=(),
                initial_vertex=vertex_id,
                target_vertex=vertex_id,
                prefix_simplex_id=None,
                last_edge_ids=(),
                frontier=graph.adjacency_targets[vertex_id],
                is_degenerate=False,
                projection_simplex_id=downstairs_simplex.id,
            )
        )
    return tuple(emitted)


def lift_downstairs_extension(
    *,
    adapter: StaticTowerAdapterProtocol,
    upstairs_tier: int,
    upstairs_graph: NormalizedGraph,
    downstairs_simplex: SimplexRecord,
    upstairs_prefix: SimplexRecord,
) -> tuple[SimplexRecord, ...]:
    """Lift one downstairs simplex extension using its final edge fiber."""

    emitted: list[SimplexRecord] = []
    targets: set[str] = set()
    for downstairs_edge_id in downstairs_simplex.last_edge_ids:
        targets.update(
            adapter.edge_fiber_targets(
                upstairs_tier=upstairs_tier,
                downstairs_edge_id=downstairs_edge_id,
                upstairs_source_id=upstairs_prefix.target_vertex,
            )
        )
    for target in sorted(frozenset(targets) & upstairs_prefix.frontier):
        emitted.append(
            extend_simplex_direct(
                upstairs_graph,
                upstairs_prefix,
                target,
                projection_simplex_id=downstairs_simplex.id,
            )
        )
    return tuple(emitted)


def lift_tier_simplices(
    *,
    adapter: StaticTowerAdapterProtocol,
    upstairs_tier: int,
    downstairs_simplices_by_degree: Mapping[int, tuple[SimplexRecord, ...]],
    k: int,
) -> LiftedTierResult:
    """Lift all simplices through degree `k` over one downstairs tier."""

    upstairs_graph = normalized_graph_for_tier(adapter, upstairs_tier)
    by_degree: dict[int, tuple[SimplexRecord, ...]] = {}
    simplex_fiber_ids: dict[str, tuple[str, ...]] = {}
    simplex_by_id: dict[str, SimplexRecord] = {}
    edge_fiber_records: dict[tuple[str, int, str], EdgeFiberRecord] = {}

    zero_simplices: list[SimplexRecord] = []
    for downstairs in downstairs_simplices_by_degree.get(0, ()):
        lifted = lift_zero_simplex(
            adapter,
            upstairs_tier=upstairs_tier,
            downstairs_simplex=downstairs,
            upstairs_graph=upstairs_graph,
        )
        simplex_fiber_ids[downstairs.id] = tuple(simplex.id for simplex in lifted)
        zero_simplices.extend(lifted)
        simplex_by_id.update((simplex.id, simplex) for simplex in lifted)
    by_degree[0] = tuple(sorted(zero_simplices, key=lambda item: item.id))

    for degree in range(1, k + 1):
        emitted_for_degree: dict[str, SimplexRecord] = {}
        for downstairs in downstairs_simplices_by_degree.get(degree, ()):
            if downstairs.prefix_simplex_id is None:
                simplex_fiber_ids[downstairs.id] = ()
                continue
            upstairs_prefix_ids = simplex_fiber_ids.get(
                downstairs.prefix_simplex_id, ()
            )
            lifted_for_downstairs: list[SimplexRecord] = []
            for upstairs_prefix_id in upstairs_prefix_ids:
                upstairs_prefix = simplex_by_id[upstairs_prefix_id]
                for downstairs_edge_id in downstairs.last_edge_ids:
                    edge_targets = adapter.edge_fiber_targets(
                        upstairs_tier=upstairs_tier,
                        downstairs_edge_id=downstairs_edge_id,
                        upstairs_source_id=upstairs_prefix.target_vertex,
                    )
                    edge_fiber_records[
                        (
                            downstairs_edge_id,
                            upstairs_tier,
                            upstairs_prefix.target_vertex,
                        )
                    ] = EdgeFiberRecord(
                        downstairs_edge_id=downstairs_edge_id,
                        upstairs_tier=upstairs_tier,
                        upstairs_source_id=upstairs_prefix.target_vertex,
                        upstairs_target_ids=tuple(sorted(edge_targets)),
                    )
                lifted = lift_downstairs_extension(
                    adapter=adapter,
                    upstairs_tier=upstairs_tier,
                    upstairs_graph=upstairs_graph,
                    downstairs_simplex=downstairs,
                    upstairs_prefix=upstairs_prefix,
                )
                for simplex in lifted:
                    emitted_for_degree.setdefault(simplex.id, simplex)
                    simplex_by_id.setdefault(simplex.id, simplex)
                    lifted_for_downstairs.append(simplex)
            simplex_fiber_ids[downstairs.id] = tuple(
                sorted({simplex.id for simplex in lifted_for_downstairs})
            )
        by_degree[degree] = tuple(
            sorted(
                emitted_for_degree.values(), key=lambda item: (item.vertices, item.id)
            )
        )

    return LiftedTierResult(
        simplices_by_degree=by_degree,
        simplex_fibers=tuple(
            SimplexFiberRecord(
                downstairs_simplex_id=downstairs_id,
                upstairs_tier=upstairs_tier,
                upstairs_simplex_ids=upstairs_ids,
            )
            for downstairs_id, upstairs_ids in sorted(simplex_fiber_ids.items())
        ),
        edge_fibers=tuple(
            edge_fiber_records[key] for key in sorted(edge_fiber_records)
        ),
    )
