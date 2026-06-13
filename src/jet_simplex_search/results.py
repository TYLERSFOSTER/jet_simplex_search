"""Public result records for simplex search workflows."""

from __future__ import annotations

from dataclasses import dataclass

from jet_simplex_search.h_lift import HLiftDiagnostics, SimplexHLiftRecord
from jet_simplex_search.records import SimplexSearchResult
from jet_simplex_search.skeleton import SkeletonizationResult


@dataclass(frozen=True, slots=True)
class SearchWithHLiftsResult:
    """Public graph-H result with skeleton search and compressed H-lift records."""

    k: int
    skeletonization: SkeletonizationResult
    skeleton_search: SimplexSearchResult
    h_lifts: tuple[SimplexHLiftRecord, ...]
    h_lift_diagnostics: HLiftDiagnostics

    def __post_init__(self) -> None:
        object.__setattr__(self, "h_lifts", tuple(self.h_lifts))


SearchResult = SimplexSearchResult | SearchWithHLiftsResult
