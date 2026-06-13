import pytest

from jet_simplex_search import search_simplices
from jet_simplex_search.api import SearchWithHLiftsResult, build_static_search_context
from jet_simplex_search.artifacts import ArtifactConfig
from jet_simplex_search.errors import InvalidKError
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex

from tests.fakes import FakeStaticTowerAdapter


def test_build_static_search_context_validates_k() -> None:
    with pytest.raises(InvalidKError):
        build_static_search_context(adapter=FakeStaticTowerAdapter(), k=-1)


def test_search_simplices_returns_result() -> None:
    result = search_simplices(adapter=FakeStaticTowerAdapter(), k=1)

    assert result.simplices_by_tier_degree


def test_search_simplices_with_graph_returns_h_lift_result() -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b")),
        edges=(InputEdge("ab1", "a", "b"), InputEdge("ab2", "a", "b")),
    )

    result = search_simplices(graph=graph, k=1)

    assert isinstance(result, SearchWithHLiftsResult)
    assert result.skeleton_search.simplices_by_tier_degree
    edge_lift = next(record for record in result.h_lifts if record.input_vertices == ("a", "b"))
    assert edge_lift.h_lift_count == 2


def test_search_simplices_optionally_writes_artifact(tmp_path) -> None:
    search_simplices(
        adapter=FakeStaticTowerAdapter(),
        k=1,
        artifact_config=ArtifactConfig(output_dir=tmp_path),
    )

    assert (tmp_path / "readout_source.json").exists()


def test_search_simplices_with_graph_writes_combined_artifact(tmp_path) -> None:
    graph = GraphInput(vertices=(InputVertex("s"),))

    search_simplices(
        graph=graph,
        k=1,
        artifact_config=ArtifactConfig(output_dir=tmp_path),
    )

    assert (tmp_path / "readout_source.json").exists()
