"""Sparse simplex frontier operations."""

from __future__ import annotations

from jet_simplex_search.errors import SimplexInvariantError
from jet_simplex_search.normalize import NormalizedGraph
from jet_simplex_search.records import FaceEdgeWitness


def initial_frontier(graph: NormalizedGraph, vertex_id: str) -> frozenset[str]:
    """Return `A(vertex_id)`."""

    try:
        return graph.adjacency_targets[vertex_id]
    except KeyError as exc:
        raise SimplexInvariantError(f"Unknown vertex id {vertex_id!r}.") from exc


def extend_frontier(
    prefix_frontier: frozenset[str],
    target_adjacency: frozenset[str],
) -> frozenset[str]:
    """Return an inductive frontier intersection."""

    if len(prefix_frontier) <= len(target_adjacency):
        return frozenset(item for item in prefix_frontier if item in target_adjacency)
    return frozenset(item for item in target_adjacency if item in prefix_frontier)


def face_edge_witnesses_for_extension(
    graph: NormalizedGraph,
    prefix_vertices: tuple[str, ...],
    target: str,
) -> tuple[FaceEdgeWitness, ...]:
    """Return new face-edge witnesses for extending a simplex by `target`."""

    witnesses: list[FaceEdgeWitness] = []
    target_index = len(prefix_vertices)
    for source_index, source in enumerate(prefix_vertices):
        edge_ids = graph.edge_lookup.get((source, target), ())
        if not edge_ids:
            raise SimplexInvariantError(
                f"Missing directed face edge from {source!r} to {target!r}."
            )
        witnesses.append(
            FaceEdgeWitness(
                source_index=source_index,
                target_index=target_index,
                edge_ids=edge_ids,
            )
        )
    return tuple(witnesses)
