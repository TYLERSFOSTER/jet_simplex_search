"""Small public API for static simplex search."""

from __future__ import annotations

from dataclasses import dataclass

from jet_simplex_search.artifacts import ArtifactConfig, write_search_artifact
from jet_simplex_search.graph import GraphInput
from jet_simplex_search.records import SimplexSearchResult
from jet_simplex_search.search import run_static_small_object_search, validate_k
from jet_simplex_search.tower_adapter import (
    StateCollapserStaticTowerAdapter,
    StaticTowerAdapterProtocol,
)


@dataclass(frozen=True, slots=True)
class StaticSearchContext:
    """Context for a static small-object simplex search."""

    adapter: StaticTowerAdapterProtocol
    k: int


def build_static_search_context(
    *,
    adapter: StaticTowerAdapterProtocol | None = None,
    graph: GraphInput | None = None,
    contraction_schema: object | None = None,
    k: int,
) -> StaticSearchContext:
    """Build a static search context."""

    validate_k(k)
    if adapter is None:
        if graph is None:
            raise TypeError("Either adapter or graph must be provided.")
        adapter = StateCollapserStaticTowerAdapter.from_graph(
            graph,
            schema=contraction_schema,
        )
    return StaticSearchContext(adapter=adapter, k=k)


def search_simplices(
    *,
    adapter: StaticTowerAdapterProtocol | None = None,
    graph: GraphInput | None = None,
    contraction_schema: object | None = None,
    k: int,
    artifact_config: ArtifactConfig | None = None,
) -> SimplexSearchResult:
    """Run static small-object simplex search."""

    context = build_static_search_context(
        adapter=adapter,
        graph=graph,
        contraction_schema=contraction_schema,
        k=k,
    )
    result = run_static_small_object_search(context.adapter, k=context.k)
    if artifact_config is not None:
        write_search_artifact(result, artifact_config)
    return result
