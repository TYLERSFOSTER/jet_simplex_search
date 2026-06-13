"""Search diagnostics."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from jet_simplex_search.records import SimplexRecord


@dataclass(frozen=True, slots=True)
class SummaryStats:
    """Small numeric summary for artifact diagnostics."""

    count: int
    minimum: int | None
    maximum: int | None
    mean: float | None

    @classmethod
    def from_values(cls, values: Iterable[int]) -> SummaryStats:
        ordered = tuple(values)
        if not ordered:
            return cls(count=0, minimum=None, maximum=None, mean=None)
        return cls(
            count=len(ordered),
            minimum=min(ordered),
            maximum=max(ordered),
            mean=sum(ordered) / len(ordered),
        )

    def to_dict(self) -> dict[str, int | float | None]:
        return {
            "count": self.count,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "mean": self.mean,
        }


@dataclass(frozen=True, slots=True)
class SearchDiagnostics:
    """Diagnostics for one static simplex search."""

    simplex_counts_by_tier_degree: Mapping[tuple[int, int], int]
    degenerate_counts_by_tier_degree: Mapping[tuple[int, int], int]
    frontier_size_summary: Mapping[tuple[int, int], SummaryStats]
    simplex_fiber_count: int
    edge_fiber_count: int
    emitted_simplex_count: int

    def to_dict(self) -> dict[str, object]:
        return {
            "simplex_counts_by_tier_degree": _mapping_to_dict(
                self.simplex_counts_by_tier_degree
            ),
            "degenerate_counts_by_tier_degree": _mapping_to_dict(
                self.degenerate_counts_by_tier_degree
            ),
            "frontier_size_summary": {
                _tier_degree_key(key): value.to_dict()
                for key, value in sorted(self.frontier_size_summary.items())
            },
            "simplex_fiber_count": self.simplex_fiber_count,
            "edge_fiber_count": self.edge_fiber_count,
            "emitted_simplex_count": self.emitted_simplex_count,
        }


def build_search_diagnostics(
    simplices_by_tier_degree: Mapping[tuple[int, int], tuple[SimplexRecord, ...]],
    *,
    simplex_fiber_count: int,
    edge_fiber_count: int,
) -> SearchDiagnostics:
    """Build count-oriented diagnostics from emitted records."""

    simplex_counts = {
        key: len(records) for key, records in simplices_by_tier_degree.items()
    }
    degenerate_counts = {
        key: sum(1 for record in records if record.is_degenerate)
        for key, records in simplices_by_tier_degree.items()
    }
    frontier_summaries = {
        key: SummaryStats.from_values(len(record.frontier) for record in records)
        for key, records in simplices_by_tier_degree.items()
    }
    return SearchDiagnostics(
        simplex_counts_by_tier_degree=simplex_counts,
        degenerate_counts_by_tier_degree=degenerate_counts,
        frontier_size_summary=frontier_summaries,
        simplex_fiber_count=simplex_fiber_count,
        edge_fiber_count=edge_fiber_count,
        emitted_simplex_count=sum(simplex_counts.values()),
    )


def _tier_degree_key(key: tuple[int, int]) -> str:
    return f"tier:{key[0]}|degree:{key[1]}"


def _mapping_to_dict(mapping: Mapping[tuple[int, int], int]) -> dict[str, int]:
    return {_tier_degree_key(key): value for key, value in sorted(mapping.items())}
