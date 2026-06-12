import json

from jet_simplex_search.artifacts import ArtifactConfig, write_search_artifact
from jet_simplex_search.search import run_static_small_object_search

from tests.fakes import FakeStaticTowerAdapter


def test_single_json_artifact_writes_and_reloads(tmp_path) -> None:
    result = run_static_small_object_search(FakeStaticTowerAdapter(), k=1)

    path = write_search_artifact(result, ArtifactConfig(output_dir=tmp_path))
    payload = json.loads(path.read_text())

    assert path.name == "readout_source.json"
    assert payload["simplex_records"]
    assert "diagnostics" in payload
    assert all("face_edge_witnesses" in row for row in payload["simplex_records"])


def test_manifest_tables_artifact_writes_expected_files(tmp_path) -> None:
    result = run_static_small_object_search(FakeStaticTowerAdapter(), k=1)

    path = write_search_artifact(
        result,
        ArtifactConfig(output_dir=tmp_path, layout="manifest_tables"),
    )
    manifest = json.loads(path.read_text())

    assert (tmp_path / "simplex_records.jsonl").exists()
    assert (tmp_path / "simplex_fibers.jsonl").exists()
    assert (tmp_path / "edge_fibers.jsonl").exists()
    assert (tmp_path / "diagnostics.json").exists()
    assert manifest["tables"]["simplex_records"]["count"] == len(
        (tmp_path / "simplex_records.jsonl").read_text().splitlines()
    )


def test_count_only_fiber_artifact_omits_members(tmp_path) -> None:
    result = run_static_small_object_search(FakeStaticTowerAdapter(), k=1)

    path = write_search_artifact(
        result,
        ArtifactConfig(output_dir=tmp_path, include_full_fiber_members=False),
    )
    payload = json.loads(path.read_text())

    assert "upstairs_simplex_ids" not in payload["simplex_fibers"][0]
    assert "count" in payload["simplex_fibers"][0]

