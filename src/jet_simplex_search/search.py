"""Static small-object simplex search."""

from __future__ import annotations

from collections.abc import Mapping

from jet_simplex_search.errors import InvalidKError, SimplexInvariantError
from jet_simplex_search.diagnostics import build_search_diagnostics
from jet_simplex_search.frontier import (
    extend_frontier,
    face_edge_witnesses_for_extension,
    initial_frontier,
)
from jet_simplex_search.ids import simplex_id
from jet_simplex_search.normalize import (
    NormalizedGraph,
    assert_simple_reflexive_normalized_graph,
)
from jet_simplex_search.records import SimplexRecord
from jet_simplex_search.records import SimplexSearchResult
from jet_simplex_search.tower_adapter import (
    StaticTowerAdapterProtocol,
    normalized_graph_for_tier,
)


def validate_k(k: int) -> None:
    """Validate a requested maximum degree."""

    if not isinstance(k, int) or k < 0:
        raise InvalidKError("k must be a nonnegative integer.")


def enumerate_zero_simplices(
    graph: NormalizedGraph,
    *,
    tier: int,
) -> tuple[SimplexRecord, ...]:
    """Emit one 0-simplex for every vertex."""

    simplices: list[SimplexRecord] = []
    for vertex_id in sorted(graph.vertices):
        vertices = (vertex_id,)
        simplices.append(
            SimplexRecord(
                id=simplex_id(tier, 0, vertices),
                tier=tier,
                degree=0,
                vertices=vertices,
                face_edge_witnesses=(),
                initial_vertex=vertex_id,
                target_vertex=vertex_id,
                prefix_simplex_id=None,
                last_edge_ids=(),
                frontier=initial_frontier(graph, vertex_id),
                is_degenerate=False,
                projection_simplex_id=None,
            )
        )
    return tuple(simplices)


def extend_simplex_direct(
    graph: NormalizedGraph,
    simplex: SimplexRecord,
    target: str,
    *,
    projection_simplex_id: str | None = None,
) -> SimplexRecord:
    """Extend a simplex by one target using cached frontier semantics."""

    if target not in simplex.frontier:
        raise SimplexInvariantError(
            f"Target {target!r} is not in frontier for simplex {simplex.id!r}."
        )
    new_vertices = (*simplex.vertices, target)
    new_degree = simplex.degree + 1
    new_witnesses = (
        *simplex.face_edge_witnesses,
        *face_edge_witnesses_for_extension(graph, simplex.vertices, target),
    )
    last_edge_ids = graph.edge_lookup.get((simplex.target_vertex, target), ())
    if not last_edge_ids:
        raise SimplexInvariantError(
            f"Missing last edge from {simplex.target_vertex!r} to {target!r}."
        )
    return SimplexRecord(
        id=simplex_id(simplex.tier, new_degree, new_vertices),
        tier=simplex.tier,
        degree=new_degree,
        vertices=new_vertices,
        face_edge_witnesses=new_witnesses,
        initial_vertex=simplex.initial_vertex,
        target_vertex=target,
        prefix_simplex_id=simplex.id,
        last_edge_ids=last_edge_ids,
        frontier=extend_frontier(simplex.frontier, initial_frontier(graph, target)),
        is_degenerate=len(set(new_vertices)) < len(new_vertices),
        projection_simplex_id=projection_simplex_id,
    )


def enumerate_direct_simplices(
    graph: NormalizedGraph,
    *,
    tier: int,
    k: int,
) -> Mapping[int, tuple[SimplexRecord, ...]]:
    """Enumerate directed flag simplices through degree `k` in one tier."""

    validate_k(k)
    assert_simple_reflexive_normalized_graph(graph)
    by_degree: dict[int, tuple[SimplexRecord, ...]] = {
        0: enumerate_zero_simplices(graph, tier=tier)
    }
    seen: set[tuple[int, int, tuple[str, ...]]] = {
        (tier, 0, simplex.vertices) for simplex in by_degree[0]
    }
    for degree in range(k):
        emitted: list[SimplexRecord] = []
        for simplex in by_degree.get(degree, ()):
            for target in sorted(simplex.frontier):
                candidate = extend_simplex_direct(graph, simplex, target)
                key = (candidate.tier, candidate.degree, candidate.vertices)
                if key in seen:
                    continue
                seen.add(key)
                emitted.append(candidate)
        by_degree[degree + 1] = tuple(
            sorted(emitted, key=lambda item: (item.vertices, item.id))
        )
    return by_degree


def run_static_small_object_search(
    adapter: StaticTowerAdapterProtocol,
    *,
    k: int,
) -> SimplexSearchResult:
    """Run static small-object search over a tower adapter."""

    from jet_simplex_search.lift import lift_tier_simplices

    validate_k(k)
    bottom_tier = adapter.bottommost_nondegenerate_tier()
    bottom_graph = normalized_graph_for_tier(adapter, bottom_tier)
    current_by_degree = enumerate_direct_simplices(bottom_graph, tier=bottom_tier, k=k)

    all_simplices: dict[tuple[int, int], tuple[SimplexRecord, ...]] = {
        (bottom_tier, degree): simplices
        for degree, simplices in current_by_degree.items()
    }
    all_fibers = []
    all_edge_fibers = []

    for upstairs_tier in range(bottom_tier - 1, -1, -1):
        lifted = lift_tier_simplices(
            adapter=adapter,
            upstairs_tier=upstairs_tier,
            downstairs_simplices_by_degree=current_by_degree,
            k=k,
        )
        current_by_degree = lifted.simplices_by_degree
        for degree, simplices in current_by_degree.items():
            all_simplices[(upstairs_tier, degree)] = simplices
        all_fibers.extend(lifted.simplex_fibers)
        all_edge_fibers.extend(lifted.edge_fibers)

    diagnostics = build_search_diagnostics(
        all_simplices,
        simplex_fiber_count=len(all_fibers),
        edge_fiber_count=len(all_edge_fibers),
    )
    return SimplexSearchResult(
        k=k,
        bottom_tier=bottom_tier,
        simplices_by_tier_degree=all_simplices,
        fibers=tuple(all_fibers),
        edge_fibers=tuple(all_edge_fibers),
        diagnostics=diagnostics,
    )
