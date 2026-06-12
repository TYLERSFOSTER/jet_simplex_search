"""Deterministic local id helpers."""

from __future__ import annotations

from urllib.parse import quote, unquote


def _escape(value: object) -> str:
    return quote(str(value), safe="")


def identity_edge_id(vertex_id: str) -> str:
    """Return the canonical formal identity edge id for a vertex."""

    return f"jss:identity:{_escape(vertex_id)}"


def identity_edge_vertex_id(edge_id: str) -> str:
    """Return the vertex id carried by a formal identity edge id."""

    prefix = "jss:identity:"
    if not edge_id.startswith(prefix):
        raise ValueError(f"Not a jet-simplex-search identity edge id: {edge_id!r}.")
    return unquote(edge_id[len(prefix) :])


def simplex_id(tier: int, degree: int, vertices: tuple[str, ...]) -> str:
    """Return a deterministic simplex id."""

    escaped_vertices = ",".join(_escape(vertex) for vertex in vertices)
    return f"jss:simplex:t{tier}:d{degree}:v[{escaped_vertices}]"


def fiber_id(downstairs_simplex_id: str, upstairs_tier: int) -> str:
    """Return a deterministic simplex-fiber id."""

    return f"jss:fiber:t{upstairs_tier}:over:{_escape(downstairs_simplex_id)}"
