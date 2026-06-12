"""Loop normalization for small-object simplex search."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from jet_simplex_search.errors import InvalidGraphError, SimplexInvariantError
from jet_simplex_search.graph import GraphInput, validate_graph_input, vertex_ids
from jet_simplex_search.ids import identity_edge_id


@dataclass(frozen=True, slots=True)
class NormalizationPolicy:
    """First-scope loop normalization policy."""

    strip_input_loops: bool = True
    add_formal_identities: bool = True


@dataclass(frozen=True, slots=True)
class NormalizedEdge:
    """Edge after loop normalization."""

    id: str
    source: str
    target: str
    kind: Literal["original", "identity"]
    original_edge_id: str | None = None
    labels: tuple[object, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "labels", tuple(self.labels))


@dataclass(frozen=True, slots=True)
class NormalizedGraph:
    """Normalized graph with formal identity arrows."""

    vertices: tuple[str, ...]
    edges: tuple[NormalizedEdge, ...]
    adjacency_targets: dict[str, frozenset[str]]
    edge_lookup: dict[tuple[str, str], tuple[str, ...]]
    stripped_loop_edge_ids: tuple[str, ...]


def normalize_graph(
    graph: GraphInput,
    policy: NormalizationPolicy | None = None,
) -> NormalizedGraph:
    """Strip input loops and add canonical formal identities."""

    validate_graph_input(graph)
    effective_policy = NormalizationPolicy() if policy is None else policy
    vertices = tuple(sorted(vertex_ids(graph)))

    normalized_edges: list[NormalizedEdge] = []
    stripped_loop_ids: list[str] = []
    used_edge_ids: set[str] = set()

    for edge in sorted(graph.edges, key=lambda item: item.id):
        if edge.source == edge.target:
            if effective_policy.strip_input_loops:
                stripped_loop_ids.append(edge.id)
                continue
            raise InvalidGraphError(
                "First-scope normalization requires input loops to be stripped."
            )
        if edge.id in used_edge_ids:
            raise InvalidGraphError(f"Duplicate normalized edge id: {edge.id!r}.")
        used_edge_ids.add(edge.id)
        normalized_edges.append(
            NormalizedEdge(
                id=edge.id,
                source=edge.source,
                target=edge.target,
                kind="original",
                original_edge_id=edge.id,
                labels=edge.labels,
            )
        )

    if effective_policy.add_formal_identities:
        for vertex_id in vertices:
            edge_id = identity_edge_id(vertex_id)
            if edge_id in used_edge_ids:
                raise InvalidGraphError(
                    f"Input edge id collides with formal identity id {edge_id!r}."
                )
            used_edge_ids.add(edge_id)
            normalized_edges.append(
                NormalizedEdge(
                    id=edge_id,
                    source=vertex_id,
                    target=vertex_id,
                    kind="identity",
                    original_edge_id=None,
                    labels=("jss:identity",),
                )
            )

    normalized_edges = sorted(normalized_edges, key=lambda item: item.id)
    adjacency_mut: dict[str, set[str]] = {vertex_id: {vertex_id} for vertex_id in vertices}
    edge_lookup_mut: dict[tuple[str, str], list[str]] = {}
    for edge in normalized_edges:
        edge_lookup_mut.setdefault((edge.source, edge.target), []).append(edge.id)
        adjacency_mut.setdefault(edge.source, set()).add(edge.target)
        adjacency_mut.setdefault(edge.target, adjacency_mut.get(edge.target, {edge.target}))

    normalized = NormalizedGraph(
        vertices=vertices,
        edges=tuple(normalized_edges),
        adjacency_targets={
            vertex_id: frozenset(targets) for vertex_id, targets in adjacency_mut.items()
        },
        edge_lookup={
            key: tuple(sorted(values)) for key, values in edge_lookup_mut.items()
        },
        stripped_loop_edge_ids=tuple(sorted(stripped_loop_ids)),
    )
    assert_normalized_graph_invariants(normalized)
    return normalized


def assert_normalized_graph_invariants(graph: NormalizedGraph) -> None:
    """Raise when normalized graph invariants are violated."""

    vertices = set(graph.vertices)
    identity_count_by_vertex = {vertex_id: 0 for vertex_id in graph.vertices}
    edge_ids: set[str] = set()

    for edge in graph.edges:
        if edge.id in edge_ids:
            raise SimplexInvariantError(f"Duplicate normalized edge id {edge.id!r}.")
        edge_ids.add(edge.id)
        if edge.source not in vertices or edge.target not in vertices:
            raise SimplexInvariantError(
                f"Normalized edge {edge.id!r} references an unknown endpoint."
            )
        if edge.kind == "identity":
            if edge.source != edge.target:
                raise SimplexInvariantError(
                    f"Identity edge {edge.id!r} must be a loop."
                )
            identity_count_by_vertex[edge.source] += 1
        elif edge.source == edge.target:
            raise SimplexInvariantError(
                f"Original edge {edge.id!r} must not be a loop in first scope."
            )

    for vertex_id, count in identity_count_by_vertex.items():
        if count != 1:
            raise SimplexInvariantError(
                f"Vertex {vertex_id!r} must have exactly one identity edge; got {count}."
            )
        if vertex_id not in graph.adjacency_targets:
            raise SimplexInvariantError(f"Missing adjacency targets for {vertex_id!r}.")
        if vertex_id not in graph.adjacency_targets[vertex_id]:
            raise SimplexInvariantError(f"Adjacency for {vertex_id!r} must include itself.")

    for (source, target), lookup_edge_ids in graph.edge_lookup.items():
        if source not in vertices or target not in vertices:
            raise SimplexInvariantError("Edge lookup contains an unknown endpoint.")
        if not lookup_edge_ids:
            raise SimplexInvariantError("Edge lookup contains an empty edge-id tuple.")
        for edge_id in lookup_edge_ids:
            if edge_id not in edge_ids:
                raise SimplexInvariantError(
                    f"Edge lookup references unknown edge id {edge_id!r}."
                )
        if target not in graph.adjacency_targets[source]:
            raise SimplexInvariantError(
                f"Adjacency for {source!r} is missing target {target!r}."
            )

