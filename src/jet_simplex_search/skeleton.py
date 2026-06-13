"""H-to-G skeletonization for simplex search."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from jet_simplex_search.errors import InvalidGraphError, SimplexInvariantError
from jet_simplex_search.graph import GraphInput, InputEdge, validate_graph_input
from jet_simplex_search.ids import skeleton_edge_id


class SkeletonLabelPolicy(StrEnum):
    """Supported v0.1 policies for labels on collapsed parallel H edges."""

    REQUIRE_IDENTICAL = "require_identical"


@dataclass(frozen=True, slots=True)
class SkeletonEdgeFiber:
    """Original non-loop H edges represented by one skeleton edge."""

    source: str
    target: str
    skeleton_edge_id: str
    original_edge_ids: tuple[str, ...]
    labels: tuple[object, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "original_edge_ids", tuple(self.original_edge_ids))
        object.__setattr__(self, "labels", tuple(self.labels))
        if self.source == self.target:
            raise SimplexInvariantError("SkeletonEdgeFiber requires source != target.")
        if not self.original_edge_ids:
            raise SimplexInvariantError("SkeletonEdgeFiber.original_edge_ids is empty.")


@dataclass(frozen=True, slots=True)
class SkeletonLoopFiber:
    """Original H loops lying over one formal skeleton identity."""

    vertex_id: str
    original_loop_edge_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "original_loop_edge_ids", tuple(self.original_loop_edge_ids)
        )


@dataclass(frozen=True, slots=True)
class SkeletonizationDiagnostics:
    """Count-oriented diagnostics for H-to-G skeletonization."""

    input_vertex_count: int
    input_edge_count: int
    input_loop_edge_count: int
    input_non_loop_edge_count: int
    skeleton_non_loop_edge_count: int
    collapsed_parallel_non_loop_edge_count: int
    collapsed_loop_edge_count: int
    vertices_with_original_loops: int
    maximum_non_loop_fiber_size: int
    maximum_loop_fiber_size: int
    label_conflict_count: int

    def to_dict(self) -> dict[str, int]:
        """Return a JSON-safe diagnostics payload."""

        return {
            "input_vertex_count": self.input_vertex_count,
            "input_edge_count": self.input_edge_count,
            "input_loop_edge_count": self.input_loop_edge_count,
            "input_non_loop_edge_count": self.input_non_loop_edge_count,
            "skeleton_non_loop_edge_count": self.skeleton_non_loop_edge_count,
            "collapsed_parallel_non_loop_edge_count": (
                self.collapsed_parallel_non_loop_edge_count
            ),
            "collapsed_loop_edge_count": self.collapsed_loop_edge_count,
            "vertices_with_original_loops": self.vertices_with_original_loops,
            "maximum_non_loop_fiber_size": self.maximum_non_loop_fiber_size,
            "maximum_loop_fiber_size": self.maximum_loop_fiber_size,
            "label_conflict_count": self.label_conflict_count,
        }


@dataclass(frozen=True, slots=True)
class SkeletonizationResult:
    """Result of preprocessing arbitrary H into simple skeleton G."""

    original_graph: GraphInput
    skeleton_graph: GraphInput
    edge_fibers_by_pair: Mapping[tuple[str, str], SkeletonEdgeFiber]
    edge_fibers_by_skeleton_edge_id: Mapping[str, SkeletonEdgeFiber]
    loop_fibers_by_vertex: Mapping[str, SkeletonLoopFiber]
    skeleton_edge_id_by_pair: Mapping[tuple[str, str], str]
    skeleton_edge_id_by_original_edge_id: Mapping[str, str]
    original_loop_vertex_by_edge_id: Mapping[str, str]
    diagnostics: SkeletonizationDiagnostics

    def __post_init__(self) -> None:
        object.__setattr__(self, "edge_fibers_by_pair", dict(self.edge_fibers_by_pair))
        object.__setattr__(
            self,
            "edge_fibers_by_skeleton_edge_id",
            dict(self.edge_fibers_by_skeleton_edge_id),
        )
        object.__setattr__(
            self, "loop_fibers_by_vertex", dict(self.loop_fibers_by_vertex)
        )
        object.__setattr__(
            self,
            "skeleton_edge_id_by_pair",
            dict(self.skeleton_edge_id_by_pair),
        )
        object.__setattr__(
            self,
            "skeleton_edge_id_by_original_edge_id",
            dict(self.skeleton_edge_id_by_original_edge_id),
        )
        object.__setattr__(
            self,
            "original_loop_vertex_by_edge_id",
            dict(self.original_loop_vertex_by_edge_id),
        )


def skeletonize_graph(
    graph: GraphInput,
    *,
    label_policy: SkeletonLabelPolicy = SkeletonLabelPolicy.REQUIRE_IDENTICAL,
) -> SkeletonizationResult:
    """Collapse H to a simple G using exact label agreement for parallel edges."""

    validate_graph_input(graph)
    if label_policy != SkeletonLabelPolicy.REQUIRE_IDENTICAL:
        raise InvalidGraphError(f"Unsupported skeleton label policy {label_policy!r}.")

    vertices = tuple(sorted(graph.vertices, key=lambda vertex: vertex.id))
    non_loop_groups: dict[tuple[str, str], list[InputEdge]] = {}
    loop_groups: dict[str, list[InputEdge]] = {vertex.id: [] for vertex in vertices}

    for edge in sorted(graph.edges, key=lambda item: item.id):
        if edge.source == edge.target:
            loop_groups.setdefault(edge.source, []).append(edge)
        else:
            non_loop_groups.setdefault((edge.source, edge.target), []).append(edge)

    skeleton_edges: list[InputEdge] = []
    edge_fibers_by_pair: dict[tuple[str, str], SkeletonEdgeFiber] = {}
    edge_fibers_by_skeleton_edge_id: dict[str, SkeletonEdgeFiber] = {}
    skeleton_edge_id_by_pair: dict[tuple[str, str], str] = {}
    skeleton_edge_id_by_original_edge_id: dict[str, str] = {}
    label_conflict_count = 0

    for (source, target), edges in sorted(non_loop_groups.items()):
        label_tuples = {edge.labels for edge in edges}
        if len(label_tuples) != 1:
            label_conflict_count += 1
            raise InvalidGraphError(
                "Parallel H edges with different labels require an explicit "
                f"label policy for endpoint pair {(source, target)!r}."
            )
        labels = next(iter(label_tuples))
        edge_id = skeleton_edge_id(source, target)
        original_edge_ids = tuple(edge.id for edge in edges)
        fiber = SkeletonEdgeFiber(
            source=source,
            target=target,
            skeleton_edge_id=edge_id,
            original_edge_ids=original_edge_ids,
            labels=labels,
        )
        skeleton_edges.append(
            InputEdge(
                id=edge_id,
                source=source,
                target=target,
                labels=labels,
            )
        )
        edge_fibers_by_pair[(source, target)] = fiber
        edge_fibers_by_skeleton_edge_id[edge_id] = fiber
        skeleton_edge_id_by_pair[(source, target)] = edge_id
        for original_edge_id in original_edge_ids:
            skeleton_edge_id_by_original_edge_id[original_edge_id] = edge_id

    loop_fibers_by_vertex = {
        vertex.id: SkeletonLoopFiber(
            vertex_id=vertex.id,
            original_loop_edge_ids=tuple(
                edge.id
                for edge in sorted(
                    loop_groups.get(vertex.id, ()),
                    key=lambda item: item.id,
                )
            ),
        )
        for vertex in vertices
    }
    original_loop_vertex_by_edge_id = {
        edge.id: vertex_id
        for vertex_id, edges in loop_groups.items()
        for edge in sorted(edges, key=lambda item: item.id)
    }

    input_loop_count = sum(len(edges) for edges in loop_groups.values())
    input_non_loop_count = sum(len(edges) for edges in non_loop_groups.values())
    non_loop_fiber_sizes = [len(edges) for edges in non_loop_groups.values()]
    loop_fiber_sizes = [
        len(fiber.original_loop_edge_ids) for fiber in loop_fibers_by_vertex.values()
    ]
    diagnostics = SkeletonizationDiagnostics(
        input_vertex_count=len(vertices),
        input_edge_count=len(graph.edges),
        input_loop_edge_count=input_loop_count,
        input_non_loop_edge_count=input_non_loop_count,
        skeleton_non_loop_edge_count=len(skeleton_edges),
        collapsed_parallel_non_loop_edge_count=input_non_loop_count
        - len(skeleton_edges),
        collapsed_loop_edge_count=input_loop_count,
        vertices_with_original_loops=sum(1 for size in loop_fiber_sizes if size > 0),
        maximum_non_loop_fiber_size=max(non_loop_fiber_sizes, default=0),
        maximum_loop_fiber_size=max(loop_fiber_sizes, default=0),
        label_conflict_count=label_conflict_count,
    )
    result = SkeletonizationResult(
        original_graph=graph,
        skeleton_graph=GraphInput(vertices=vertices, edges=tuple(skeleton_edges)),
        edge_fibers_by_pair=edge_fibers_by_pair,
        edge_fibers_by_skeleton_edge_id=edge_fibers_by_skeleton_edge_id,
        loop_fibers_by_vertex=loop_fibers_by_vertex,
        skeleton_edge_id_by_pair=skeleton_edge_id_by_pair,
        skeleton_edge_id_by_original_edge_id=skeleton_edge_id_by_original_edge_id,
        original_loop_vertex_by_edge_id=original_loop_vertex_by_edge_id,
        diagnostics=diagnostics,
    )
    assert_skeletonization_invariants(result)
    return result


def assert_skeletonization_invariants(result: SkeletonizationResult) -> None:
    """Raise when an H-to-G skeletonization result is internally inconsistent."""

    original_vertex_ids = {vertex.id for vertex in result.original_graph.vertices}
    skeleton_vertex_ids = {vertex.id for vertex in result.skeleton_graph.vertices}
    if original_vertex_ids != skeleton_vertex_ids:
        raise SimplexInvariantError("Skeleton vertices must match original vertices.")

    seen_pairs: set[tuple[str, str]] = set()
    skeleton_edge_ids = {edge.id for edge in result.skeleton_graph.edges}
    for edge in result.skeleton_graph.edges:
        if edge.source == edge.target:
            raise SimplexInvariantError("Skeleton graph must not contain loops.")
        pair = (edge.source, edge.target)
        if pair in seen_pairs:
            raise SimplexInvariantError("Skeleton graph contains parallel edges.")
        seen_pairs.add(pair)
        if pair not in result.edge_fibers_by_pair:
            raise SimplexInvariantError("Skeleton edge is missing endpoint fiber.")
        if edge.id not in result.edge_fibers_by_skeleton_edge_id:
            raise SimplexInvariantError("Skeleton edge is missing id fiber.")

    for pair, fiber in result.edge_fibers_by_pair.items():
        if pair not in seen_pairs:
            raise SimplexInvariantError("Edge fiber has no skeleton edge.")
        if fiber.skeleton_edge_id not in skeleton_edge_ids:
            raise SimplexInvariantError("Edge fiber references unknown skeleton edge.")

    if set(result.loop_fibers_by_vertex) != original_vertex_ids:
        raise SimplexInvariantError("Every original vertex must have a loop fiber.")

    original_non_loop_edge_ids = {
        edge.id for edge in result.original_graph.edges if edge.source != edge.target
    }
    original_loop_edge_ids = {
        edge.id for edge in result.original_graph.edges if edge.source == edge.target
    }
    if set(result.skeleton_edge_id_by_original_edge_id) != original_non_loop_edge_ids:
        raise SimplexInvariantError("Original non-loop edge map is incomplete.")
    if set(result.original_loop_vertex_by_edge_id) != original_loop_edge_ids:
        raise SimplexInvariantError("Original loop edge map is incomplete.")
