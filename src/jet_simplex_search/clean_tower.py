"""Clean static quotient towers for simplex search."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from jet_simplex_search.errors import CleanTowerConstructionError
from jet_simplex_search.graph import GraphInput, InputEdge, InputVertex, validate_graph_input
from jet_simplex_search.ids import identity_edge_id, tier_simple_edge_id


@dataclass(frozen=True, slots=True)
class CleanTowerConfig:
    """Configuration for JSS-owned clean quotient tower construction."""

    stop_at_singleton: bool = True
    max_tiers: int | None = None

    def __post_init__(self) -> None:
        if self.max_tiers is not None and self.max_tiers <= 0:
            raise CleanTowerConstructionError("CleanTowerConfig.max_tiers must be positive.")


@dataclass(frozen=True, slots=True)
class CleanTierProjection:
    """Projection data from one clean tier to the next."""

    upstairs_tier: int
    downstairs_tier: int
    vertex_projection: Mapping[str, str]
    edge_projection: Mapping[str, str]
    edge_fiber_targets: Mapping[tuple[str, str], frozenset[str]]
    vertex_members: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "vertex_projection", dict(self.vertex_projection))
        object.__setattr__(self, "edge_projection", dict(self.edge_projection))
        object.__setattr__(
            self,
            "edge_fiber_targets",
            {
                key: frozenset(value)
                for key, value in self.edge_fiber_targets.items()
            },
        )
        object.__setattr__(
            self,
            "vertex_members",
            {key: tuple(value) for key, value in self.vertex_members.items()},
        )


@dataclass(frozen=True, slots=True)
class CleanTowerDiagnostics:
    """Count-oriented diagnostics for clean quotient tower construction."""

    tier_count: int
    vertex_count_by_tier: Mapping[int, int]
    edge_count_by_tier: Mapping[int, int]
    collapsed_loop_count_by_step: Mapping[int, int]
    collapsed_parallel_edge_count_by_step: Mapping[int, int]
    maximum_edge_fiber_size_by_step: Mapping[int, int]
    skipped_empty_block_count: int
    stopped_because_singleton: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "vertex_count_by_tier", dict(self.vertex_count_by_tier))
        object.__setattr__(self, "edge_count_by_tier", dict(self.edge_count_by_tier))
        object.__setattr__(
            self,
            "collapsed_loop_count_by_step",
            dict(self.collapsed_loop_count_by_step),
        )
        object.__setattr__(
            self,
            "collapsed_parallel_edge_count_by_step",
            dict(self.collapsed_parallel_edge_count_by_step),
        )
        object.__setattr__(
            self,
            "maximum_edge_fiber_size_by_step",
            dict(self.maximum_edge_fiber_size_by_step),
        )

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe diagnostics payload."""

        return {
            "tier_count": self.tier_count,
            "vertex_count_by_tier": _int_mapping_to_dict(self.vertex_count_by_tier),
            "edge_count_by_tier": _int_mapping_to_dict(self.edge_count_by_tier),
            "collapsed_loop_count_by_step": _int_mapping_to_dict(
                self.collapsed_loop_count_by_step
            ),
            "collapsed_parallel_edge_count_by_step": _int_mapping_to_dict(
                self.collapsed_parallel_edge_count_by_step
            ),
            "maximum_edge_fiber_size_by_step": _int_mapping_to_dict(
                self.maximum_edge_fiber_size_by_step
            ),
            "skipped_empty_block_count": self.skipped_empty_block_count,
            "stopped_because_singleton": self.stopped_because_singleton,
        }


@dataclass(frozen=True, slots=True)
class CleanTower:
    """Static tower whose stored tiers are clean directed graphs."""

    tier_graphs: tuple[GraphInput, ...]
    projections: tuple[CleanTierProjection, ...]
    diagnostics: CleanTowerDiagnostics

    def __post_init__(self) -> None:
        object.__setattr__(self, "tier_graphs", tuple(self.tier_graphs))
        object.__setattr__(self, "projections", tuple(self.projections))
        if not self.tier_graphs:
            raise CleanTowerConstructionError("CleanTower requires at least one tier.")


@dataclass(frozen=True, slots=True)
class CleanStaticTowerAdapter:
    """Static tower adapter backed by JSS clean quotient graphs."""

    clean_tower: CleanTower
    _edge_by_tier_id: dict[tuple[int, str], InputEdge] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        edge_by_tier_id = {}
        for tier, graph in enumerate(self.clean_tower.tier_graphs):
            for edge in graph.edges:
                edge_by_tier_id[(tier, edge.id)] = edge
        object.__setattr__(self, "_edge_by_tier_id", edge_by_tier_id)

    @classmethod
    def from_graph(
        cls,
        graph: GraphInput,
        *,
        schema: object | None = None,
        config: CleanTowerConfig | None = None,
    ) -> CleanStaticTowerAdapter:
        """Build a clean static tower adapter from an already-clean graph."""

        return cls(build_clean_static_tower(graph, schema=schema, config=config))

    def tiers(self) -> tuple[int, ...]:
        return tuple(range(len(self.clean_tower.tier_graphs)))

    def bottommost_nondegenerate_tier(self) -> int:
        for tier in reversed(range(len(self.clean_tower.tier_graphs))):
            if len(self.clean_tower.tier_graphs[tier].vertices) > 1:
                return tier
        return 0

    def tier_vertices(self, tier: int) -> tuple[str, ...]:
        return tuple(vertex.id for vertex in self.clean_tower.tier_graphs[tier].vertices)

    def tier_edges(self, tier: int) -> tuple[str, ...]:
        return tuple(edge.id for edge in self.clean_tower.tier_graphs[tier].edges)

    def edge_source(self, tier: int, edge_id: str) -> str:
        if edge_id.startswith("jss:identity:"):
            from jet_simplex_search.ids import identity_edge_vertex_id

            return identity_edge_vertex_id(edge_id)
        return self._edge_by_tier_id[(tier, edge_id)].source

    def edge_target(self, tier: int, edge_id: str) -> str:
        if edge_id.startswith("jss:identity:"):
            from jet_simplex_search.ids import identity_edge_vertex_id

            return identity_edge_vertex_id(edge_id)
        return self._edge_by_tier_id[(tier, edge_id)].target

    def project_vertex(self, tier: int, vertex_id: str) -> str:
        return self.clean_tower.projections[tier].vertex_projection[vertex_id]

    def project_edge(self, tier: int, edge_id: str) -> str:
        if edge_id.startswith("jss:identity:"):
            from jet_simplex_search.ids import identity_edge_vertex_id

            projected_vertex = self.project_vertex(tier, identity_edge_vertex_id(edge_id))
            return identity_edge_id(projected_vertex)
        return self.clean_tower.projections[tier].edge_projection[edge_id]

    def edge_fiber_targets(
        self,
        *,
        upstairs_tier: int,
        downstairs_edge_id: str,
        upstairs_source_id: str,
    ) -> frozenset[str]:
        return self.clean_tower.projections[upstairs_tier].edge_fiber_targets.get(
            (downstairs_edge_id, upstairs_source_id),
            frozenset(),
        )

    def tier0_vertex_id_to_input_vertex_id(self) -> dict[str, str]:
        return {vertex.id: vertex.id for vertex in self.clean_tower.tier_graphs[0].vertices}


@dataclass(frozen=True, slots=True)
class _CurrentTierObjects:
    states: tuple[object, ...]
    edges: tuple[object, ...]
    state_by_vertex_id: Mapping[str, object]
    edge_by_edge_id: Mapping[str, object]
    registry: object


@dataclass(frozen=True, slots=True)
class _CleanStepResult:
    graph: GraphInput
    projection: CleanTierProjection
    collapsed_loop_count: int
    collapsed_parallel_edge_count: int
    maximum_edge_fiber_size: int


@dataclass(frozen=True, slots=True)
class _SingleBlockContractionSchema:
    delegate: object
    selected_block_id: object

    def assign_edge(self, edge_id: object, registry: object) -> object | None:
        block_id = self.delegate.assign_edge(edge_id, registry)
        return self.selected_block_id if block_id == self.selected_block_id else None

    def ordered_blocks(self) -> tuple[object, ...]:
        return (self.selected_block_id,)


def build_clean_static_tower(
    graph: GraphInput,
    *,
    schema: object | None = None,
    config: CleanTowerConfig | None = None,
) -> CleanTower:
    """Build a static tower whose quotient tiers are cleaned between steps."""

    config = CleanTowerConfig() if config is None else config
    _assert_clean_graph(graph)

    tier_graphs: list[GraphInput] = [graph]
    projections: list[CleanTierProjection] = []
    collapsed_loop_count_by_step: dict[int, int] = {}
    collapsed_parallel_count_by_step: dict[int, int] = {}
    max_edge_fiber_size_by_step: dict[int, int] = {}
    skipped_empty_block_count = 0
    stopped_because_singleton = False

    if schema is not None:
        declared_blocks = tuple(schema.ordered_blocks())
        if declared_blocks:
            block_cursor = iter(declared_blocks)
            while True:
                current_graph = tier_graphs[-1]
                if config.stop_at_singleton and len(current_graph.vertices) <= 1:
                    stopped_because_singleton = True
                    break
                if config.max_tiers is not None and len(tier_graphs) >= config.max_tiers:
                    break
                try:
                    block_id = next(block_cursor)
                except StopIteration:
                    break
                current_objects = _current_tier_objects(current_graph, tier=len(tier_graphs) - 1)
                if not _block_has_edges(schema, block_id, current_objects):
                    skipped_empty_block_count += 1
                    continue
                step = _realize_clean_quotient_step(
                    current_graph,
                    schema=schema,
                    block_id=block_id,
                    upstairs_tier=len(tier_graphs) - 1,
                )
                projections.append(step.projection)
                tier_graphs.append(step.graph)
                collapsed_loop_count_by_step[step.projection.upstairs_tier] = (
                    step.collapsed_loop_count
                )
                collapsed_parallel_count_by_step[step.projection.upstairs_tier] = (
                    step.collapsed_parallel_edge_count
                )
                max_edge_fiber_size_by_step[step.projection.upstairs_tier] = (
                    step.maximum_edge_fiber_size
                )
        else:
            while True:
                current_graph = tier_graphs[-1]
                if config.stop_at_singleton and len(current_graph.vertices) <= 1:
                    stopped_because_singleton = True
                    break
                if config.max_tiers is not None and len(tier_graphs) >= config.max_tiers:
                    break
                current_objects = _current_tier_objects(current_graph, tier=len(tier_graphs) - 1)
                blocks = _assigned_blocks(schema, current_objects)
                if not blocks:
                    break
                step = _realize_clean_quotient_step(
                    current_graph,
                    schema=schema,
                    block_id=blocks[0],
                    upstairs_tier=len(tier_graphs) - 1,
                )
                projections.append(step.projection)
                tier_graphs.append(step.graph)
                collapsed_loop_count_by_step[step.projection.upstairs_tier] = (
                    step.collapsed_loop_count
                )
                collapsed_parallel_count_by_step[step.projection.upstairs_tier] = (
                    step.collapsed_parallel_edge_count
                )
                max_edge_fiber_size_by_step[step.projection.upstairs_tier] = (
                    step.maximum_edge_fiber_size
                )

    diagnostics = CleanTowerDiagnostics(
        tier_count=len(tier_graphs),
        vertex_count_by_tier={
            tier: len(tier_graph.vertices)
            for tier, tier_graph in enumerate(tier_graphs)
        },
        edge_count_by_tier={
            tier: len(tier_graph.edges)
            for tier, tier_graph in enumerate(tier_graphs)
        },
        collapsed_loop_count_by_step=collapsed_loop_count_by_step,
        collapsed_parallel_edge_count_by_step=collapsed_parallel_count_by_step,
        maximum_edge_fiber_size_by_step=max_edge_fiber_size_by_step,
        skipped_empty_block_count=skipped_empty_block_count,
        stopped_because_singleton=stopped_because_singleton,
    )
    return CleanTower(
        tier_graphs=tuple(tier_graphs),
        projections=tuple(projections),
        diagnostics=diagnostics,
    )


def _realize_clean_quotient_step(
    graph: GraphInput,
    *,
    schema: object,
    block_id: object,
    upstairs_tier: int,
) -> _CleanStepResult:
    from state_collapser.tower.partition.tower import build_partition_tower_full

    current_objects = _current_tier_objects(graph, tier=upstairs_tier)
    tower = build_partition_tower_full(
        states=current_objects.states,
        edges=current_objects.edges,
        current_state=None,
        schema=_SingleBlockContractionSchema(schema, block_id),
    )
    if len(tower.state_layers) < 2:  # type: ignore[attr-defined]
        raise CleanTowerConstructionError("One-block quotient tower did not create a quotient tier.")

    downstairs_tier = upstairs_tier + 1
    downstream_layer = tower.state_layers[1]  # type: ignore[attr-defined]
    vertex_projection, vertex_members = _realize_vertices(
        graph,
        current_objects=current_objects,
        downstream_layer=downstream_layer,
        downstairs_tier=downstairs_tier,
    )
    (
        downstream_edges,
        edge_projection,
        edge_fiber_targets,
        collapsed_loop_count,
        collapsed_parallel_edge_count,
        maximum_edge_fiber_size,
    ) = _realize_edges(
        graph,
        vertex_projection=vertex_projection,
        downstairs_tier=downstairs_tier,
    )
    downstream_graph = GraphInput(
        vertices=tuple(
            InputVertex(vertex_id)
            for vertex_id in sorted(vertex_members)
        ),
        edges=downstream_edges,
    )
    _assert_clean_graph(downstream_graph)
    return _CleanStepResult(
        graph=downstream_graph,
        projection=CleanTierProjection(
            upstairs_tier=upstairs_tier,
            downstairs_tier=downstairs_tier,
            vertex_projection=vertex_projection,
            edge_projection=edge_projection,
            edge_fiber_targets=edge_fiber_targets,
            vertex_members=vertex_members,
        ),
        collapsed_loop_count=collapsed_loop_count,
        collapsed_parallel_edge_count=collapsed_parallel_edge_count,
        maximum_edge_fiber_size=maximum_edge_fiber_size,
    )


def _current_tier_objects(graph: GraphInput, *, tier: int) -> _CurrentTierObjects:
    from state_collapser.core.action import PrimitiveAction
    from state_collapser.core.edges import BaseEdge
    from state_collapser.core.state import State
    from state_collapser.tower.partition.base_registry import BaseGraphRegistry

    state_by_vertex_id = {
        vertex.id: State(
            payload=vertex.id,
            identity=("jet-simplex-search", "clean-tower", "vertex", tier, vertex.id),
        )
        for vertex in graph.vertices
    }
    edge_by_edge_id = {}
    for edge in graph.edges:
        action = PrimitiveAction(
            payload=edge.id,
            identity=("jet-simplex-search", "clean-tower", "edge", tier, edge.id),
            labels=edge.labels,
        )
        edge_by_edge_id[edge.id] = BaseEdge(
            source=state_by_vertex_id[edge.source],
            action=action,
            target=state_by_vertex_id[edge.target],
            labels=edge.labels,
        )
    registry = BaseGraphRegistry()
    states = tuple(state_by_vertex_id[vertex.id] for vertex in graph.vertices)
    edges = tuple(edge_by_edge_id[edge.id] for edge in graph.edges)
    registry.register_delta(states, edges)
    return _CurrentTierObjects(
        states=states,
        edges=edges,
        state_by_vertex_id=state_by_vertex_id,
        edge_by_edge_id=edge_by_edge_id,
        registry=registry,
    )


def _assigned_blocks(schema: object, current_objects: _CurrentTierObjects) -> tuple[object, ...]:
    assigned: dict[object, None] = {}
    for edge_id in current_objects.registry.edge_ids:  # type: ignore[attr-defined]
        block_id = schema.assign_edge(edge_id, current_objects.registry)
        if block_id is not None:
            assigned.setdefault(block_id, None)
    return tuple(assigned)


def _block_has_edges(
    schema: object,
    block_id: object,
    current_objects: _CurrentTierObjects,
) -> bool:
    return any(
        schema.assign_edge(edge_id, current_objects.registry) == block_id
        for edge_id in current_objects.registry.edge_ids  # type: ignore[attr-defined]
    )


def _realize_vertices(
    graph: GraphInput,
    *,
    current_objects: _CurrentTierObjects,
    downstream_layer: object,
    downstairs_tier: int,
) -> tuple[dict[str, str], dict[str, tuple[str, ...]]]:
    cell_members: dict[object, list[str]] = {}
    for vertex in graph.vertices:
        state = current_objects.state_by_vertex_id[vertex.id]
        state_id = current_objects.registry.state_id_by_state[state]  # type: ignore[attr-defined]
        cell_id = downstream_layer.cell_of(state_id)
        cell_members.setdefault(cell_id, []).append(vertex.id)

    ordered_cells = sorted(
        cell_members.items(),
        key=lambda item: tuple(sorted(item[1])),
    )
    vertex_id_by_cell = {
        cell_id: f"cell:{downstairs_tier}:{ordinal}"
        for ordinal, (cell_id, _members) in enumerate(ordered_cells)
    }
    vertex_projection = {}
    vertex_members = {}
    for cell_id, members in ordered_cells:
        downstream_vertex = vertex_id_by_cell[cell_id]
        member_tuple = tuple(sorted(members))
        vertex_members[downstream_vertex] = member_tuple
        for member in member_tuple:
            vertex_projection[member] = downstream_vertex
    return vertex_projection, vertex_members


def _realize_edges(
    graph: GraphInput,
    *,
    vertex_projection: Mapping[str, str],
    downstairs_tier: int,
) -> tuple[
    tuple[InputEdge, ...],
    dict[str, str],
    dict[tuple[str, str], frozenset[str]],
    int,
    int,
    int,
]:
    edge_projection: dict[str, str] = {}
    projected_edges_by_pair: dict[tuple[str, str], list[InputEdge]] = {}
    edge_fiber_targets: dict[tuple[str, str], set[str]] = {}

    for source in vertex_projection:
        downstream_source = vertex_projection[source]
        identity_id = identity_edge_id(downstream_source)
        edge_fiber_targets.setdefault((identity_id, source), set()).add(source)

    collapsed_loop_count = 0
    for edge in graph.edges:
        projected_source = vertex_projection[edge.source]
        projected_target = vertex_projection[edge.target]
        if projected_source == projected_target:
            projected_edge_id = identity_edge_id(projected_source)
            collapsed_loop_count += 1
        else:
            projected_edge_id = tier_simple_edge_id(
                downstairs_tier,
                projected_source,
                projected_target,
            )
            projected_edges_by_pair.setdefault(
                (projected_source, projected_target),
                [],
            ).append(edge)
        edge_projection[edge.id] = projected_edge_id
        edge_fiber_targets.setdefault((projected_edge_id, edge.source), set()).add(edge.target)

    downstream_edges: list[InputEdge] = []
    collapsed_parallel_edge_count = 0
    maximum_edge_fiber_size = 0
    for (source, target), edges in sorted(projected_edges_by_pair.items()):
        label_tuples = {edge.labels for edge in edges}
        if len(label_tuples) != 1:
            raise CleanTowerConstructionError(
                "Clean quotient edge label conflict for quotient pair "
                f"{(source, target)!r}; v0.1 requires exact label agreement."
            )
        edge_id = tier_simple_edge_id(downstairs_tier, source, target)
        labels = next(iter(label_tuples))
        downstream_edges.append(InputEdge(id=edge_id, source=source, target=target, labels=labels))
        collapsed_parallel_edge_count += max(0, len(edges) - 1)
        maximum_edge_fiber_size = max(maximum_edge_fiber_size, len(edges))

    frozen_edge_fiber_targets = {
        key: frozenset(value)
        for key, value in edge_fiber_targets.items()
    }
    return (
        tuple(downstream_edges),
        edge_projection,
        frozen_edge_fiber_targets,
        collapsed_loop_count,
        collapsed_parallel_edge_count,
        maximum_edge_fiber_size,
    )


def _assert_clean_graph(graph: GraphInput) -> None:
    validate_graph_input(graph)
    seen_pairs: set[tuple[str, str]] = set()
    for edge in graph.edges:
        if edge.source == edge.target:
            raise CleanTowerConstructionError("Clean tower graphs must not store loops.")
        pair = (edge.source, edge.target)
        if pair in seen_pairs:
            raise CleanTowerConstructionError(
                f"Clean tower graphs must not store parallel edge pair {pair!r}."
            )
        seen_pairs.add(pair)


def _int_mapping_to_dict(mapping: Mapping[int, int]) -> dict[str, int]:
    return {str(key): value for key, value in sorted(mapping.items())}
