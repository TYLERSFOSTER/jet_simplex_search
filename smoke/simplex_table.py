from __future__ import annotations

from collections.abc import Mapping

from jet_simplex_search import search_simplices
from jet_simplex_search.graph import GraphInput


def print_simplex_count_table(
    graph: GraphInput,
    *,
    k: int,
    contraction_schema: object | None = None,
) -> None:
    result = search_simplices(
        graph=graph,
        contraction_schema=contraction_schema,
        k=k,
    )
    search_result = getattr(result, "skeleton_search", result)
    print("Skeleton simplex counts")
    print(format_simplex_count_table(search_result.diagnostics.simplex_counts_by_tier_degree))
    if hasattr(result, "h_lift_diagnostics"):
        print()
        print("Tier-0 H-lift counts")
        print(
            format_h_lift_count_table(
                positive_counts=result.h_lift_diagnostics.positive_simplex_count_by_degree,
                total_counts=result.h_lift_diagnostics.total_h_lift_count_by_degree,
            )
        )


def format_simplex_count_table(counts: Mapping[tuple[int, int], int]) -> str:
    tiers = sorted({tier for tier, _dimension in counts})
    dimensions = sorted({dimension for _tier, dimension in counts})

    headers = ["tier"] + [f"dim {dimension}" for dimension in dimensions]
    rows = [
        [str(tier)] + [str(counts.get((tier, dimension), 0)) for dimension in dimensions]
        for tier in tiers
    ]

    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]

    lines = [
        " | ".join(header.rjust(widths[index]) for index, header in enumerate(headers)),
        "-+-".join("-" * width for width in widths),
    ]
    lines.extend(
        " | ".join(value.rjust(widths[index]) for index, value in enumerate(row))
        for row in rows
    )
    return "\n".join(lines)


def format_h_lift_count_table(
    *,
    positive_counts: Mapping[int, int],
    total_counts: Mapping[int, int],
) -> str:
    dimensions = sorted(set(positive_counts) | set(total_counts))
    headers = ["metric"] + [f"dim {dimension}" for dimension in dimensions]
    rows = [
        ["positive addresses"]
        + [str(positive_counts.get(dimension, 0)) for dimension in dimensions],
        ["total H-lifts"]
        + [str(total_counts.get(dimension, 0)) for dimension in dimensions],
    ]
    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]
    lines = [
        " | ".join(header.rjust(widths[index]) for index, header in enumerate(headers)),
        "-+-".join("-" * width for width in widths),
    ]
    lines.extend(
        " | ".join(value.rjust(widths[index]) for index, value in enumerate(row))
        for row in rows
    )
    return "\n".join(lines)
