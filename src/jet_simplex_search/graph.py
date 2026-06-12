"""Sparse directed graph input records."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from jet_simplex_search.errors import InvalidGraphError


@dataclass(frozen=True, slots=True)
class InputVertex:
    """Input graph vertex with a stable string id."""

    id: str
    payload: object | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise InvalidGraphError("InputVertex.id must be a nonempty string.")


@dataclass(frozen=True, slots=True)
class InputEdge:
    """Input graph directed edge with a stable string id."""

    id: str
    source: str
    target: str
    payload: object | None = None
    labels: tuple[object, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id:
            raise InvalidGraphError("InputEdge.id must be a nonempty string.")
        if not isinstance(self.source, str) or not self.source:
            raise InvalidGraphError("InputEdge.source must be a nonempty string.")
        if not isinstance(self.target, str) or not self.target:
            raise InvalidGraphError("InputEdge.target must be a nonempty string.")
        object.__setattr__(self, "labels", tuple(self.labels))


@dataclass(frozen=True, slots=True)
class GraphInput:
    """First-scope sparse directed graph input."""

    vertices: tuple[InputVertex, ...]
    edges: tuple[InputEdge, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "vertices", tuple(self.vertices))
        object.__setattr__(self, "edges", tuple(self.edges))
        validate_graph_input(self)


def graph_from_edges(
    edges: Iterable[tuple[str, str]],
    *,
    vertex_payloads: dict[str, object] | None = None,
) -> GraphInput:
    """Build a `GraphInput` from a small edge list."""

    payloads = {} if vertex_payloads is None else vertex_payloads
    vertex_ids: dict[str, None] = {}
    input_edges: list[InputEdge] = []
    for index, (source, target) in enumerate(edges):
        vertex_ids.setdefault(source, None)
        vertex_ids.setdefault(target, None)
        input_edges.append(InputEdge(id=f"e{index}", source=source, target=target))
    vertices = tuple(
        InputVertex(id=vertex_id, payload=payloads.get(vertex_id))
        for vertex_id in sorted(vertex_ids)
    )
    return GraphInput(vertices=vertices, edges=tuple(input_edges))


def validate_graph_input(graph: GraphInput) -> None:
    """Validate first-scope graph invariants."""

    if not graph.vertices:
        raise InvalidGraphError("GraphInput must contain at least one vertex.")

    vertex_ids: dict[str, None] = {}
    for vertex in graph.vertices:
        if vertex.id in vertex_ids:
            raise InvalidGraphError(f"Duplicate vertex id: {vertex.id!r}.")
        vertex_ids[vertex.id] = None

    edge_ids: dict[str, None] = {}
    for edge in graph.edges:
        if edge.id in edge_ids:
            raise InvalidGraphError(f"Duplicate edge id: {edge.id!r}.")
        edge_ids[edge.id] = None
        if edge.source not in vertex_ids:
            raise InvalidGraphError(
                f"Edge {edge.id!r} references missing source {edge.source!r}."
            )
        if edge.target not in vertex_ids:
            raise InvalidGraphError(
                f"Edge {edge.id!r} references missing target {edge.target!r}."
            )


def vertex_ids(graph: GraphInput) -> tuple[str, ...]:
    """Return vertex ids in graph order."""

    return tuple(vertex.id for vertex in graph.vertices)


def payload_for_vertex(graph: GraphInput, vertex_id: str) -> Any:
    """Return a vertex payload, falling back to its id."""

    for vertex in graph.vertices:
        if vertex.id == vertex_id:
            return vertex.id if vertex.payload is None else vertex.payload
    raise InvalidGraphError(f"Unknown vertex id: {vertex_id!r}.")

