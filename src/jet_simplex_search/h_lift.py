"""Compressed H-lift records for tier-0 skeleton simplices."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from jet_simplex_search.errors import SimplexInvariantError
from jet_simplex_search.ids import h_lift_id, identity_edge_id
from jet_simplex_search.records import SimplexRecord, SimplexSearchResult
from jet_simplex_search.skeleton import SkeletonizationResult


@dataclass(frozen=True, slots=True)
class HFaceLiftFactor:
    """Original H edge choices for one face occurrence of a skeleton simplex."""

    source_index: int
    target_index: int
    source_vertex_id: str
    target_vertex_id: str
    skeleton_edge_id: str
    original_edge_ids: tuple[str, ...]
    factor: int
    is_loop_factor: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "original_edge_ids", tuple(self.original_edge_ids))
        if self.source_index >= self.target_index:
            raise SimplexInvariantError("HFaceLiftFactor requires source_index < target_index.")
        if self.factor != len(self.original_edge_ids):
            raise SimplexInvariantError("HFaceLiftFactor.factor must match edge-id count.")
        if self.is_loop_factor != (self.source_vertex_id == self.target_vertex_id):
            raise SimplexInvariantError("HFaceLiftFactor loop flag does not match endpoints.")


@dataclass(frozen=True, slots=True)
class SimplexHLiftRecord:
    """Compressed distinct H-lifts lying over one tier-0 skeleton simplex."""

    id: str
    simplex_id: str
    tier: int
    degree: int
    skeleton_vertices: tuple[str, ...]
    input_vertices: tuple[str, ...]
    face_factors: tuple[HFaceLiftFactor, ...]
    h_lift_count: int
    has_h_lift: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "skeleton_vertices", tuple(self.skeleton_vertices))
        object.__setattr__(self, "input_vertices", tuple(self.input_vertices))
        object.__setattr__(self, "face_factors", tuple(self.face_factors))
        if self.degree != len(self.input_vertices) - 1:
            raise SimplexInvariantError("H-lift degree must match input vertices.")
        if len(self.skeleton_vertices) != len(self.input_vertices):
            raise SimplexInvariantError("Skeleton and input vertex lengths must match.")
        product = 1
        for factor in self.face_factors:
            product *= factor.factor
        expected_count = 1 if self.degree == 0 else product
        if self.h_lift_count != expected_count:
            raise SimplexInvariantError("H-lift count must equal face-factor product.")
        if self.has_h_lift != (self.h_lift_count > 0):
            raise SimplexInvariantError("H-lift positivity flag is inconsistent.")


@dataclass(frozen=True, slots=True)
class HLiftDiagnostics:
    """Count-oriented diagnostics for compressed H-lift records."""

    simplex_count_by_degree: Mapping[int, int]
    positive_simplex_count_by_degree: Mapping[int, int]
    zero_lift_simplex_count_by_degree: Mapping[int, int]
    total_h_lift_count_by_degree: Mapping[int, int]
    max_h_lift_count_by_degree: Mapping[int, int]
    max_face_factor_by_degree: Mapping[int, int]

    def __post_init__(self) -> None:
        object.__setattr__(self, "simplex_count_by_degree", dict(self.simplex_count_by_degree))
        object.__setattr__(
            self,
            "positive_simplex_count_by_degree",
            dict(self.positive_simplex_count_by_degree),
        )
        object.__setattr__(
            self,
            "zero_lift_simplex_count_by_degree",
            dict(self.zero_lift_simplex_count_by_degree),
        )
        object.__setattr__(
            self,
            "total_h_lift_count_by_degree",
            dict(self.total_h_lift_count_by_degree),
        )
        object.__setattr__(
            self,
            "max_h_lift_count_by_degree",
            dict(self.max_h_lift_count_by_degree),
        )
        object.__setattr__(
            self,
            "max_face_factor_by_degree",
            dict(self.max_face_factor_by_degree),
        )

    def to_dict(self) -> dict[str, dict[str, int]]:
        """Return a JSON-safe diagnostics payload."""

        return {
            "simplex_count_by_degree": _degree_mapping_to_dict(
                self.simplex_count_by_degree
            ),
            "positive_simplex_count_by_degree": _degree_mapping_to_dict(
                self.positive_simplex_count_by_degree
            ),
            "zero_lift_simplex_count_by_degree": _degree_mapping_to_dict(
                self.zero_lift_simplex_count_by_degree
            ),
            "total_h_lift_count_by_degree": _degree_mapping_to_dict(
                self.total_h_lift_count_by_degree
            ),
            "max_h_lift_count_by_degree": _degree_mapping_to_dict(
                self.max_h_lift_count_by_degree
            ),
            "max_face_factor_by_degree": _degree_mapping_to_dict(
                self.max_face_factor_by_degree
            ),
        }


def compute_h_lifts_for_tier_zero(
    *,
    skeletonization: SkeletonizationResult,
    skeleton_search: SimplexSearchResult,
    tier0_vertex_id_to_input_vertex_id: Mapping[str, str],
) -> tuple[SimplexHLiftRecord, ...]:
    """Compute compressed H-lift records for all tier-0 skeleton simplices."""

    emitted: list[SimplexHLiftRecord] = []
    for simplex in _tier_zero_simplices(skeleton_search):
        input_vertices = tuple(
            _input_vertex_for(
                tier0_vertex_id_to_input_vertex_id,
                skeleton_vertex,
            )
            for skeleton_vertex in simplex.vertices
        )
        face_factors = _face_factors_for_simplex(
            skeletonization=skeletonization,
            input_vertices=input_vertices,
        )
        count = 1
        for factor in face_factors:
            count *= factor.factor
        emitted.append(
            SimplexHLiftRecord(
                id=h_lift_id(simplex.id),
                simplex_id=simplex.id,
                tier=simplex.tier,
                degree=simplex.degree,
                skeleton_vertices=simplex.vertices,
                input_vertices=input_vertices,
                face_factors=face_factors,
                h_lift_count=1 if simplex.degree == 0 else count,
                has_h_lift=(1 if simplex.degree == 0 else count) > 0,
            )
        )
    return tuple(sorted(emitted, key=lambda item: (item.degree, item.simplex_id)))


def build_h_lift_diagnostics(records: Iterable[SimplexHLiftRecord]) -> HLiftDiagnostics:
    """Build diagnostics from compressed H-lift records."""

    by_degree: dict[int, list[SimplexHLiftRecord]] = {}
    for record in records:
        by_degree.setdefault(record.degree, []).append(record)
    simplex_counts = {degree: len(items) for degree, items in by_degree.items()}
    positive_counts = {
        degree: sum(1 for item in items if item.has_h_lift)
        for degree, items in by_degree.items()
    }
    zero_counts = {
        degree: sum(1 for item in items if not item.has_h_lift)
        for degree, items in by_degree.items()
    }
    total_counts = {
        degree: sum(item.h_lift_count for item in items)
        for degree, items in by_degree.items()
    }
    max_counts = {
        degree: max((item.h_lift_count for item in items), default=0)
        for degree, items in by_degree.items()
    }
    max_face_factors = {
        degree: max(
            (factor.factor for item in items for factor in item.face_factors),
            default=0,
        )
        for degree, items in by_degree.items()
    }
    return HLiftDiagnostics(
        simplex_count_by_degree=simplex_counts,
        positive_simplex_count_by_degree=positive_counts,
        zero_lift_simplex_count_by_degree=zero_counts,
        total_h_lift_count_by_degree=total_counts,
        max_h_lift_count_by_degree=max_counts,
        max_face_factor_by_degree=max_face_factors,
    )


def _tier_zero_simplices(result: SimplexSearchResult) -> tuple[SimplexRecord, ...]:
    simplices = [
        simplex
        for (tier, _degree), records in result.simplices_by_tier_degree.items()
        if tier == 0
        for simplex in records
    ]
    return tuple(sorted(simplices, key=lambda item: (item.degree, item.id)))


def _input_vertex_for(mapping: Mapping[str, str], skeleton_vertex: str) -> str:
    try:
        return mapping[skeleton_vertex]
    except KeyError as exc:
        raise SimplexInvariantError(
            f"Missing input vertex mapping for tier-0 vertex {skeleton_vertex!r}."
        ) from exc


def _face_factors_for_simplex(
    *,
    skeletonization: SkeletonizationResult,
    input_vertices: tuple[str, ...],
) -> tuple[HFaceLiftFactor, ...]:
    factors: list[HFaceLiftFactor] = []
    for target_index in range(1, len(input_vertices)):
        for source_index in range(target_index):
            source = input_vertices[source_index]
            target = input_vertices[target_index]
            if source == target:
                loop_fiber = skeletonization.loop_fibers_by_vertex.get(source)
                if loop_fiber is None:
                    raise SimplexInvariantError(
                        f"Missing loop fiber for vertex {source!r}."
                    )
                original_edge_ids = loop_fiber.original_loop_edge_ids
                edge_id = identity_edge_id(source)
                is_loop = True
            else:
                edge_fiber = skeletonization.edge_fibers_by_pair.get((source, target))
                if edge_fiber is None:
                    raise SimplexInvariantError(
                        f"Missing non-loop H fiber for edge {source!r} -> {target!r}."
                    )
                original_edge_ids = edge_fiber.original_edge_ids
                if not original_edge_ids:
                    raise SimplexInvariantError(
                        f"Non-loop H fiber is empty for edge {source!r} -> {target!r}."
                    )
                edge_id = edge_fiber.skeleton_edge_id
                is_loop = False
            factors.append(
                HFaceLiftFactor(
                    source_index=source_index,
                    target_index=target_index,
                    source_vertex_id=source,
                    target_vertex_id=target,
                    skeleton_edge_id=edge_id,
                    original_edge_ids=original_edge_ids,
                    factor=len(original_edge_ids),
                    is_loop_factor=is_loop,
                )
            )
    return tuple(factors)


def _degree_mapping_to_dict(mapping: Mapping[int, int]) -> dict[str, int]:
    return {f"degree:{degree}": value for degree, value in sorted(mapping.items())}
