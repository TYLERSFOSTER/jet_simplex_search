"""Immutable records for simplex search."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

from jet_simplex_search.errors import SimplexInvariantError

if TYPE_CHECKING:
    from jet_simplex_search.diagnostics import SearchDiagnostics


@dataclass(frozen=True, slots=True)
class FaceEdgeWitness:
    """Skeleton/tower edge witnesses for one directed face."""

    source_index: int
    target_index: int
    edge_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "edge_ids", tuple(self.edge_ids))
        if self.source_index >= self.target_index:
            raise SimplexInvariantError(
                "FaceEdgeWitness requires source_index < target_index."
            )
        if not self.edge_ids:
            raise SimplexInvariantError("FaceEdgeWitness.edge_ids must be nonempty.")


@dataclass(frozen=True, slots=True)
class SimplexRecord:
    """A directed flag simplex address in a skeleton/tower tier."""

    id: str
    tier: int
    degree: int
    vertices: tuple[str, ...]
    face_edge_witnesses: tuple[FaceEdgeWitness, ...]
    initial_vertex: str
    target_vertex: str
    prefix_simplex_id: str | None
    last_edge_ids: tuple[str, ...]
    frontier: frozenset[str]
    is_degenerate: bool
    projection_simplex_id: str | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "vertices", tuple(self.vertices))
        object.__setattr__(self, "face_edge_witnesses", tuple(self.face_edge_witnesses))
        object.__setattr__(self, "last_edge_ids", tuple(self.last_edge_ids))
        object.__setattr__(self, "frontier", frozenset(self.frontier))

        if self.degree != len(self.vertices) - 1:
            raise SimplexInvariantError("Simplex degree must equal len(vertices) - 1.")
        if not self.vertices:
            raise SimplexInvariantError("SimplexRecord.vertices must be nonempty.")
        if self.initial_vertex != self.vertices[0]:
            raise SimplexInvariantError(
                "Simplex initial_vertex must match vertices[0]."
            )
        if self.target_vertex != self.vertices[-1]:
            raise SimplexInvariantError(
                "Simplex target_vertex must match vertices[-1]."
            )
        expected_degenerate = len(set(self.vertices)) < len(self.vertices)
        if self.is_degenerate != expected_degenerate:
            raise SimplexInvariantError(
                "Simplex is_degenerate flag does not match vertices."
            )
        for witness in self.face_edge_witnesses:
            if witness.target_index >= len(self.vertices):
                raise SimplexInvariantError(
                    "FaceEdgeWitness target index is out of range."
                )


@dataclass(frozen=True, slots=True)
class SimplexFiberRecord:
    """Upstairs simplex ids lying over one downstairs simplex."""

    downstairs_simplex_id: str
    upstairs_tier: int
    upstairs_simplex_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "upstairs_simplex_ids", tuple(self.upstairs_simplex_ids)
        )


@dataclass(frozen=True, slots=True)
class EdgeFiberRecord:
    """Upstairs edge-fiber targets for a downstairs edge/source pair."""

    downstairs_edge_id: str
    upstairs_tier: int
    upstairs_source_id: str
    upstairs_target_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "upstairs_target_ids", tuple(self.upstairs_target_ids))


@dataclass(frozen=True, slots=True)
class SimplexSearchResult:
    """In-memory result for a static small-object simplex search."""

    k: int
    bottom_tier: int
    simplices_by_tier_degree: Mapping[tuple[int, int], tuple[SimplexRecord, ...]]
    fibers: tuple[SimplexFiberRecord, ...] = ()
    edge_fibers: tuple[EdgeFiberRecord, ...] = ()
    diagnostics: SearchDiagnostics | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "fibers", tuple(self.fibers))
        object.__setattr__(self, "edge_fibers", tuple(self.edge_fibers))
