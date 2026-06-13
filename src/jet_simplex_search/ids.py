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


def skeleton_edge_id(source: str, target: str) -> str:
    """Return the canonical skeleton edge id for an ordered endpoint pair."""

    return f"jss:skeleton-edge:{_escape(source)}:{_escape(target)}"


def tier_simple_edge_id(tier: int, source: str, target: str) -> str:
    """Return the canonical simple edge id for one tower tier endpoint pair."""

    return f"jss:tier-edge:t{tier}:{_escape(source)}:{_escape(target)}"


def simplex_id(tier: int, degree: int, vertices: tuple[str, ...]) -> str:
    """Return a deterministic simplex id."""

    escaped_vertices = ",".join(_escape(vertex) for vertex in vertices)
    return f"jss:simplex:t{tier}:d{degree}:v[{escaped_vertices}]"


def h_lift_id(simplex_id: str) -> str:
    """Return the canonical H-lift record id for a skeleton simplex id."""

    return f"jss:h-lift:{_escape(simplex_id)}"
