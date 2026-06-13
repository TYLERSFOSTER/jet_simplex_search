"""Machine-readable search artifact writers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from jet_simplex_search.errors import ArtifactWriteError
from jet_simplex_search.h_lift import HFaceLiftFactor, SimplexHLiftRecord
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
    include_h_fiber_members: bool = True
    include_h_lift_face_factors: bool = True
    include_expanded_h_lift_witnesses: bool = False
    max_expanded_h_lift_witnesses: int = 100_000


def write_search_artifact(
    result: object,
    config: ArtifactConfig,
) -> Path:
    """Write a search artifact and return the manifest/source path."""

    if config.include_expanded_h_lift_witnesses:
        raise ArtifactWriteError("Expanded H-lift witness artifacts are not implemented.")
    try:
        config.output_dir.mkdir(parents=True, exist_ok=True)
        if config.layout == "single_json":
            return _write_single_json(result, config)
        if config.layout == "manifest_tables":
            return _write_manifest_tables(result, config)
    except OSError as exc:
        raise ArtifactWriteError(str(exc)) from exc
    raise ArtifactWriteError(f"Unknown artifact layout {config.layout!r}.")


def _write_single_json(result: object, config: ArtifactConfig) -> Path:
    path = config.output_dir / "readout_source.json"
    payload = _result_payload(result, config)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _write_manifest_tables(result: object, config: ArtifactConfig) -> Path:
    if _is_combined_result(result):
        return _write_combined_manifest_tables(result, config)
    result = _as_simplex_search_result(result)
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


def _result_payload(result: object, config: ArtifactConfig) -> dict[str, object]:
    if _is_combined_result(result):
        skeleton_search = result.skeleton_search
        return {
            "manifest": _manifest_payload(result, config),
            "skeletonization": _skeletonization_to_dict(
                result.skeletonization,
                include_members=config.include_h_fiber_members,
            ),
            "skeleton_search": _simplex_search_payload(skeleton_search, config),
            "h_lifts": [
                _h_lift_to_dict(
                    record,
                    include_fiber_members=config.include_h_fiber_members,
                    include_face_factors=config.include_h_lift_face_factors,
                )
                for record in result.h_lifts
            ],
            "diagnostics": _combined_diagnostics_payload(result),
        }
    result = _as_simplex_search_result(result)
    return _simplex_search_payload(result, config)


def _simplex_search_payload(
    result: SimplexSearchResult,
    config: ArtifactConfig,
) -> dict[str, object]:
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


def _manifest_payload(result: object, config: ArtifactConfig) -> dict[str, object]:
    search_result = result.skeleton_search if _is_combined_result(result) else result
    search_result = _as_simplex_search_result(search_result)
    payload: dict[str, object] = {
        "schema_version": 2 if _is_combined_result(result) else 1,
        "package": "jet-simplex-search",
        "k": search_result.k,
        "bottom_tier": search_result.bottom_tier,
        "artifact_layout": config.layout,
        "include_frontier_members": config.include_frontier_members,
        "include_full_fiber_members": config.include_full_fiber_members,
    }
    if _is_combined_result(result):
        payload["result_kind"] = "skeleton_search_with_h_lifts"
        payload["include_h_fiber_members"] = config.include_h_fiber_members
        payload["include_h_lift_face_factors"] = config.include_h_lift_face_factors
        payload["include_expanded_h_lift_witnesses"] = (
            config.include_expanded_h_lift_witnesses
        )
    return payload


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


def _write_combined_manifest_tables(result: object, config: ArtifactConfig) -> Path:
    skeleton_search = _as_simplex_search_result(result.skeleton_search)
    simplex_records = [
        _simplex_to_dict(simplex, include_frontier_members=config.include_frontier_members)
        for _key, records in sorted(skeleton_search.simplices_by_tier_degree.items())
        for simplex in records
    ]
    simplex_fibers = [
        _simplex_fiber_to_dict(record, include_members=config.include_full_fiber_members)
        for record in skeleton_search.fibers
    ]
    edge_fibers = [
        _edge_fiber_to_dict(record, include_members=config.include_full_fiber_members)
        for record in skeleton_search.edge_fibers
    ]
    skeleton_edge_fibers = [
        _skeleton_edge_fiber_to_dict(fiber, include_members=config.include_h_fiber_members)
        for _key, fiber in sorted(result.skeletonization.edge_fibers_by_pair.items())
    ]
    skeleton_loop_fibers = [
        _skeleton_loop_fiber_to_dict(fiber, include_members=config.include_h_fiber_members)
        for _key, fiber in sorted(result.skeletonization.loop_fibers_by_vertex.items())
    ]
    h_lift_records = [
        _h_lift_to_dict(
            record,
            include_fiber_members=config.include_h_fiber_members,
            include_face_factors=False,
        )
        for record in result.h_lifts
    ]
    h_lift_face_factors = [
        _h_face_factor_to_dict(
            factor,
            h_lift_id=record.id,
            simplex_id=record.simplex_id,
            include_fiber_members=config.include_h_fiber_members,
        )
        for record in result.h_lifts
        for factor in record.face_factors
    ]

    _write_jsonl(config.output_dir / "skeleton_edge_fibers.jsonl", skeleton_edge_fibers)
    _write_jsonl(config.output_dir / "skeleton_loop_fibers.jsonl", skeleton_loop_fibers)
    _write_jsonl(config.output_dir / "simplex_records.jsonl", simplex_records)
    _write_jsonl(config.output_dir / "simplex_fibers.jsonl", simplex_fibers)
    _write_jsonl(config.output_dir / "edge_fibers.jsonl", edge_fibers)
    _write_jsonl(config.output_dir / "h_lift_records.jsonl", h_lift_records)
    _write_jsonl(config.output_dir / "h_lift_face_factors.jsonl", h_lift_face_factors)
    diagnostics_path = config.output_dir / "diagnostics.json"
    diagnostics_path.write_text(
        json.dumps(_combined_diagnostics_payload(result), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    manifest = {
        "manifest": _manifest_payload(result, config),
        "tables": {
            "skeleton_edge_fibers": {
                "path": "skeleton_edge_fibers.jsonl",
                "count": len(skeleton_edge_fibers),
            },
            "skeleton_loop_fibers": {
                "path": "skeleton_loop_fibers.jsonl",
                "count": len(skeleton_loop_fibers),
            },
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
            "h_lift_records": {
                "path": "h_lift_records.jsonl",
                "count": len(h_lift_records),
            },
            "h_lift_face_factors": {
                "path": "h_lift_face_factors.jsonl",
                "count": len(h_lift_face_factors),
            },
            "diagnostics": {
                "path": "diagnostics.json",
            },
        },
    }
    path = config.output_dir / "readout_source.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _skeletonization_to_dict(
    skeletonization: object,
    *,
    include_members: bool,
) -> dict[str, object]:
    return {
        "diagnostics": skeletonization.diagnostics.to_dict(),
        "edge_fibers": [
            _skeleton_edge_fiber_to_dict(fiber, include_members=include_members)
            for _key, fiber in sorted(skeletonization.edge_fibers_by_pair.items())
        ],
        "loop_fibers": [
            _skeleton_loop_fiber_to_dict(fiber, include_members=include_members)
            for _key, fiber in sorted(skeletonization.loop_fibers_by_vertex.items())
        ],
    }


def _skeleton_edge_fiber_to_dict(
    fiber: object,
    *,
    include_members: bool,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "source": fiber.source,
        "target": fiber.target,
        "skeleton_edge_id": fiber.skeleton_edge_id,
        "count": len(fiber.original_edge_ids),
        "labels": list(fiber.labels),
    }
    if include_members:
        payload["original_edge_ids"] = list(fiber.original_edge_ids)
    return payload


def _skeleton_loop_fiber_to_dict(
    fiber: object,
    *,
    include_members: bool,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "vertex_id": fiber.vertex_id,
        "count": len(fiber.original_loop_edge_ids),
    }
    if include_members:
        payload["original_loop_edge_ids"] = list(fiber.original_loop_edge_ids)
    return payload


def _h_lift_to_dict(
    record: SimplexHLiftRecord,
    *,
    include_fiber_members: bool,
    include_face_factors: bool,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "id": record.id,
        "simplex_id": record.simplex_id,
        "tier": record.tier,
        "degree": record.degree,
        "skeleton_vertices": list(record.skeleton_vertices),
        "input_vertices": list(record.input_vertices),
        "h_lift_count": record.h_lift_count,
        "has_h_lift": record.has_h_lift,
        "face_factor_count": len(record.face_factors),
    }
    if include_face_factors:
        payload["face_factors"] = [
            _h_face_factor_to_dict(
                factor,
                h_lift_id=record.id,
                simplex_id=record.simplex_id,
                include_fiber_members=include_fiber_members,
            )
            for factor in record.face_factors
        ]
    return payload


def _h_face_factor_to_dict(
    factor: HFaceLiftFactor,
    *,
    h_lift_id: str,
    simplex_id: str,
    include_fiber_members: bool,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "h_lift_id": h_lift_id,
        "simplex_id": simplex_id,
        "source_index": factor.source_index,
        "target_index": factor.target_index,
        "source_vertex_id": factor.source_vertex_id,
        "target_vertex_id": factor.target_vertex_id,
        "skeleton_edge_id": factor.skeleton_edge_id,
        "factor": factor.factor,
        "is_loop_factor": factor.is_loop_factor,
    }
    if include_fiber_members:
        payload["original_edge_ids"] = list(factor.original_edge_ids)
    return payload


def _combined_diagnostics_payload(result: object) -> dict[str, object]:
    return {
        "skeletonization": result.skeletonization.diagnostics.to_dict(),
        "skeleton_search": _diagnostics_payload(result.skeleton_search),
        "h_lifts": result.h_lift_diagnostics.to_dict(),
    }


def _is_combined_result(result: object) -> bool:
    return all(
        hasattr(result, attribute)
        for attribute in (
            "skeletonization",
            "skeleton_search",
            "h_lifts",
            "h_lift_diagnostics",
        )
    )


def _as_simplex_search_result(result: object) -> SimplexSearchResult:
    if isinstance(result, SimplexSearchResult):
        return result
    raise ArtifactWriteError(f"Unsupported artifact result type {type(result).__name__!r}.")
