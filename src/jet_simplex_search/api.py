"""Small public API for static simplex search."""

from __future__ import annotations

from jet_simplex_search.artifacts import ArtifactConfig, write_search_artifact
from jet_simplex_search.clean_tower import CleanStaticTowerAdapter
from jet_simplex_search.graph import GraphInput
from jet_simplex_search.h_lift import (
    build_h_lift_diagnostics,
    compute_h_lifts_for_tier_zero,
)
from jet_simplex_search.records import SimplexSearchResult
from jet_simplex_search.results import SearchWithHLiftsResult
from jet_simplex_search.search import run_static_small_object_search, validate_k
from jet_simplex_search.skeleton import skeletonize_graph
from jet_simplex_search.tower_adapter import StaticTowerAdapterProtocol


def _resolve_skeleton_adapter(
    *,
    adapter: StaticTowerAdapterProtocol | None = None,
    graph: GraphInput | None = None,
    contraction_schema: object | None = None,
) -> StaticTowerAdapterProtocol:
    """Resolve the lower-level skeleton/tower search adapter."""

    if adapter is not None and graph is not None:
        raise TypeError("Provide either adapter or graph, not both.")
    if adapter is None and graph is None:
        raise TypeError("Either adapter or graph must be provided.")
    if adapter is not None:
        return adapter
    return CleanStaticTowerAdapter.from_graph(
        graph,
        schema=contraction_schema,
    )


def search_simplices(
    *,
    graph: GraphInput,
    contraction_schema: object | None = None,
    k: int,
    artifact_config: ArtifactConfig | None = None,
) -> SearchWithHLiftsResult:
    """Run the public graph-H search workflow."""

    validate_k(k)
    skeletonization = skeletonize_graph(graph)
    real_adapter = CleanStaticTowerAdapter.from_graph(
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


def search_skeleton_simplices(
    *,
    adapter: StaticTowerAdapterProtocol | None = None,
    graph: GraphInput | None = None,
    contraction_schema: object | None = None,
    k: int,
    artifact_config: ArtifactConfig | None = None,
) -> SimplexSearchResult:
    """Run skeleton/tower-only static small-object simplex search."""

    validate_k(k)
    real_adapter = _resolve_skeleton_adapter(
        adapter=adapter,
        graph=graph,
        contraction_schema=contraction_schema,
    )
    result = run_static_small_object_search(real_adapter, k=k)
    if artifact_config is not None:
        write_search_artifact(result, artifact_config)
    return result
