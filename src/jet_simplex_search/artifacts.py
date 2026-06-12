"""Machine-readable search artifact writers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from jet_simplex_search.errors import ArtifactWriteError
from jet_simplex_search.records import (
    EdgeFiberRecord,
    FaceEdgeWitness,
    SimplexFiberRecord,
    SimplexRecord,
    SimplexSearchResult,
)


@dataclass(frozen=True, slots=True)
class ArtifactConfig:
    """Artifact writing configuration."""

    output_dir: Path
    layout: Literal["single_json", "manifest_tables"] = "single_json"
    include_frontier_members: bool = False
    include_full_fiber_members: bool = True


def write_search_artifact(
    result: SimplexSearchResult,
    config: ArtifactConfig,
) -> Path:
    """Write a search artifact and return the manifest/source path."""

    try:
        config.output_dir.mkdir(parents=True, exist_ok=True)
        if config.layout == "single_json":
            return _write_single_json(result, config)
        if config.layout == "manifest_tables":
            return _write_manifest_tables(result, config)
    except OSError as exc:
        raise ArtifactWriteError(str(exc)) from exc
    raise ArtifactWriteError(f"Unknown artifact layout {config.layout!r}.")


def _write_single_json(result: SimplexSearchResult, config: ArtifactConfig) -> Path:
    path = config.output_dir / "readout_source.json"
    payload = _result_payload(result, config)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _write_manifest_tables(result: SimplexSearchResult, config: ArtifactConfig) -> Path:
    simplex_records = [
        _simplex_to_dict(simplex, include_frontier_members=config.include_frontier_members)
        for _key, records in sorted(result.simplices_by_tier_degree.items())
        for simplex in records
    ]
    simplex_fibers = [
        _simplex_fiber_to_dict(record, include_members=config.include_full_fiber_members)
        for record in result.fibers
    ]
    edge_fibers = [
        _edge_fiber_to_dict(record, include_members=config.include_full_fiber_members)
        for record in result.edge_fibers
    ]

    _write_jsonl(config.output_dir / "simplex_records.jsonl", simplex_records)
    _write_jsonl(config.output_dir / "simplex_fibers.jsonl", simplex_fibers)
    _write_jsonl(config.output_dir / "edge_fibers.jsonl", edge_fibers)
    diagnostics_path = config.output_dir / "diagnostics.json"
    diagnostics_path.write_text(
        json.dumps(_diagnostics_payload(result), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    manifest = {
        "manifest": _manifest_payload(result, config),
        "tables": {
            "simplex_records": {
                "path": "simplex_records.jsonl",
                "count": len(simplex_records),
            },
            "simplex_fibers": {
                "path": "simplex_fibers.jsonl",
                "count": len(simplex_fibers),
            },
            "edge_fibers": {
                "path": "edge_fibers.jsonl",
                "count": len(edge_fibers),
            },
            "diagnostics": {
                "path": "diagnostics.json",
            },
        },
    }
    path = config.output_dir / "readout_source.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _result_payload(result: SimplexSearchResult, config: ArtifactConfig) -> dict[str, object]:
    return {
        "manifest": _manifest_payload(result, config),
        "simplex_records": [
            _simplex_to_dict(simplex, include_frontier_members=config.include_frontier_members)
            for _key, records in sorted(result.simplices_by_tier_degree.items())
            for simplex in records
        ],
        "simplex_fibers": [
            _simplex_fiber_to_dict(record, include_members=config.include_full_fiber_members)
            for record in result.fibers
        ],
        "edge_fibers": [
            _edge_fiber_to_dict(record, include_members=config.include_full_fiber_members)
            for record in result.edge_fibers
        ],
        "diagnostics": _diagnostics_payload(result),
    }


def _manifest_payload(result: SimplexSearchResult, config: ArtifactConfig) -> dict[str, object]:
    return {
        "schema_version": 1,
        "package": "jet-simplex-search",
        "k": result.k,
        "bottom_tier": result.bottom_tier,
        "artifact_layout": config.layout,
        "include_frontier_members": config.include_frontier_members,
        "include_full_fiber_members": config.include_full_fiber_members,
    }


def _diagnostics_payload(result: SimplexSearchResult) -> dict[str, object]:
    if result.diagnostics is None:
        return {}
    return result.diagnostics.to_dict()


def _simplex_to_dict(
    simplex: SimplexRecord,
    *,
    include_frontier_members: bool,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": simplex.id,
        "tier": simplex.tier,
        "degree": simplex.degree,
        "vertices": list(simplex.vertices),
        "face_edge_witnesses": [
            _witness_to_dict(witness) for witness in simplex.face_edge_witnesses
        ],
        "initial_vertex": simplex.initial_vertex,
        "target_vertex": simplex.target_vertex,
        "prefix_simplex_id": simplex.prefix_simplex_id,
        "last_edge_ids": list(simplex.last_edge_ids),
        "frontier_count": len(simplex.frontier),
        "is_degenerate": simplex.is_degenerate,
        "projection_simplex_id": simplex.projection_simplex_id,
    }
    if include_frontier_members:
        payload["frontier_members"] = sorted(simplex.frontier)
    return payload


def _witness_to_dict(witness: FaceEdgeWitness) -> dict[str, object]:
    return {
        "source_index": witness.source_index,
        "target_index": witness.target_index,
        "edge_ids": list(witness.edge_ids),
    }


def _simplex_fiber_to_dict(
    record: SimplexFiberRecord,
    *,
    include_members: bool,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "downstairs_simplex_id": record.downstairs_simplex_id,
        "upstairs_tier": record.upstairs_tier,
        "count": len(record.upstairs_simplex_ids),
    }
    if include_members:
        payload["upstairs_simplex_ids"] = list(record.upstairs_simplex_ids)
    return payload


def _edge_fiber_to_dict(
    record: EdgeFiberRecord,
    *,
    include_members: bool,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "downstairs_edge_id": record.downstairs_edge_id,
        "upstairs_tier": record.upstairs_tier,
        "upstairs_source_id": record.upstairs_source_id,
        "count": len(record.upstairs_target_ids),
    }
    if include_members:
        payload["upstairs_target_ids"] = list(record.upstairs_target_ids)
    return payload

