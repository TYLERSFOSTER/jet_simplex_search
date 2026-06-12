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
    print(format_simplex_count_table(result.diagnostics.simplex_counts_by_tier_degree))


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
