"""Small public API for static simplex search."""

from __future__ import annotations

from dataclasses import dataclass

from jet_simplex_search.artifacts import ArtifactConfig, write_search_artifact
from jet_simplex_search.graph import GraphInput
from jet_simplex_search.h_lift import (
    HLiftDiagnostics,
    SimplexHLiftRecord,
    build_h_lift_diagnostics,
    compute_h_lifts_for_tier_zero,
)
from jet_simplex_search.records import SimplexSearchResult
from jet_simplex_search.search import run_static_small_object_search, validate_k
from jet_simplex_search.skeleton import SkeletonizationResult, skeletonize_graph
from jet_simplex_search.tower_adapter import (
    StateCollapserStaticTowerAdapter,
    StaticTowerAdapterProtocol,
)


@dataclass(frozen=True, slots=True)
class StaticSearchContext:
    """Context for a static small-object simplex search."""

    adapter: StaticTowerAdapterProtocol
    k: int


@dataclass(frozen=True, slots=True)
class SearchWithHLiftsResult:
    """Public graph-H search result with skeleton search and H-lift records."""

    k: int
    skeletonization: SkeletonizationResult
    skeleton_search: SimplexSearchResult
    h_lifts: tuple[SimplexHLiftRecord, ...]
    h_lift_diagnostics: HLiftDiagnostics

    def __post_init__(self) -> None:
        object.__setattr__(self, "h_lifts", tuple(self.h_lifts))


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
) -> SimplexSearchResult | SearchWithHLiftsResult:
    """Run public graph-H search or lower-level adapter skeleton search."""

    validate_k(k)
    if adapter is None and graph is not None:
        skeletonization = skeletonize_graph(graph)
        real_adapter = StateCollapserStaticTowerAdapter.from_graph(
            skeletonization.skeleton_graph,
            schema=contraction_schema,
        )
        skeleton_search = run_static_small_object_search(real_adapter, k=k)
        h_lifts = compute_h_lifts_for_tier_zero(
            skeletonization=skeletonization,
            skeleton_search=skeleton_search,
            tier0_vertex_id_to_input_vertex_id=real_adapter.tier0_vertex_id_to_input_vertex_id(),
        )
        result = SearchWithHLiftsResult(
            k=k,
            skeletonization=skeletonization,
            skeleton_search=skeleton_search,
            h_lifts=h_lifts,
            h_lift_diagnostics=build_h_lift_diagnostics(h_lifts),
        )
        if artifact_config is not None:
            write_search_artifact(result, artifact_config)
        return result

    return search_skeleton_simplices(
        adapter=adapter,
        graph=graph,
        contraction_schema=contraction_schema,
        k=k,
        artifact_config=artifact_config,
    )


def search_skeleton_simplices(
    *,
    adapter: StaticTowerAdapterProtocol | None = None,
    graph: GraphInput | None = None,
    contraction_schema: object | None = None,
    k: int,
    artifact_config: ArtifactConfig | None = None,
) -> SimplexSearchResult:
    """Run skeleton/tower-only static small-object simplex search."""

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
