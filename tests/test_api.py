import pytest

from jet_simplex_search import search_simplices
from jet_simplex_search.api import build_static_search_context
from jet_simplex_search.artifacts import ArtifactConfig
from jet_simplex_search.errors import InvalidKError

from tests.fakes import FakeStaticTowerAdapter


def test_build_static_search_context_validates_k() -> None:
    with pytest.raises(InvalidKError):
        build_static_search_context(adapter=FakeStaticTowerAdapter(), k=-1)


def test_search_simplices_returns_result() -> None:
    result = search_simplices(adapter=FakeStaticTowerAdapter(), k=1)

    assert result.simplices_by_tier_degree


def test_search_simplices_optionally_writes_artifact(tmp_path) -> None:
    search_simplices(
        adapter=FakeStaticTowerAdapter(),
        k=1,
        artifact_config=ArtifactConfig(output_dir=tmp_path),
    )

    assert (tmp_path / "readout_source.json").exists()

