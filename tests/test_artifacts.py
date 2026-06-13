import json

from jet_simplex_search.artifacts import ArtifactConfig, write_search_artifact
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex
from jet_simplex_search.api import search_simplices
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


def test_combined_single_json_artifact_includes_h_lifts(tmp_path) -> None:
    graph = GraphInput(
        vertices=(InputVertex("a"), InputVertex("b")),
        edges=(InputEdge("ab1", "a", "b"), InputEdge("ab2", "a", "b")),
    )
    result = search_simplices(graph=graph, k=1)

    path = write_search_artifact(result, ArtifactConfig(output_dir=tmp_path))
    payload = json.loads(path.read_text())

    assert payload["manifest"]["schema_version"] == 2
    assert payload["skeletonization"]["edge_fibers"]
    assert payload["h_lifts"]
    assert "skeleton_search" in payload


def test_combined_manifest_tables_artifact_writes_h_lift_tables(tmp_path) -> None:
    graph = GraphInput(vertices=(InputVertex("s"),))
    result = search_simplices(graph=graph, k=1)

    path = write_search_artifact(
        result,
        ArtifactConfig(output_dir=tmp_path, layout="manifest_tables"),
    )
    manifest = json.loads(path.read_text())

    assert (tmp_path / "skeleton_loop_fibers.jsonl").exists()
    assert (tmp_path / "h_lift_records.jsonl").exists()
    assert (tmp_path / "h_lift_face_factors.jsonl").exists()
    assert manifest["manifest"]["schema_version"] == 2
    assert manifest["tables"]["h_lift_records"]["count"] > 0
