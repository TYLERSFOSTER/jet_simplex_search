import pytest

from jet_simplex_search.errors import SimplexInvariantError
from jet_simplex_search.records import FaceEdgeWitness, SimplexRecord


def test_face_edge_witness_validates_indices_and_edges() -> None:
    witness = FaceEdgeWitness(0, 1, ("e",))

    assert witness.edge_ids == ("e",)
    with pytest.raises(SimplexInvariantError, match="source_index"):
        FaceEdgeWitness(1, 1, ("e",))
    with pytest.raises(SimplexInvariantError, match="nonempty"):
        FaceEdgeWitness(0, 1, ())


def test_simplex_record_validates_shape() -> None:
    simplex = SimplexRecord(
        id="s",
        tier=0,
        degree=1,
        vertices=("a", "b"),
        face_edge_witnesses=(FaceEdgeWitness(0, 1, ("e",)),),
        initial_vertex="a",
        target_vertex="b",
        prefix_simplex_id="a",
        last_edge_ids=("e",),
        frontier=frozenset({"b"}),
        is_degenerate=False,
        projection_simplex_id=None,
    )

    assert simplex.degree == 1
    with pytest.raises(SimplexInvariantError, match="degree"):
        SimplexRecord(
            id="bad",
            tier=0,
            degree=2,
            vertices=("a", "b"),
            face_edge_witnesses=(),
            initial_vertex="a",
            target_vertex="b",
            prefix_simplex_id=None,
            last_edge_ids=(),
            frontier=frozenset(),
            is_degenerate=False,
            projection_simplex_id=None,
        )


def test_simplex_record_validates_degenerate_flag() -> None:
    with pytest.raises(SimplexInvariantError, match="is_degenerate"):
        SimplexRecord(
            id="bad",
            tier=0,
            degree=1,
            vertices=("a", "a"),
            face_edge_witnesses=(FaceEdgeWitness(0, 1, ("id",)),),
            initial_vertex="a",
            target_vertex="a",
            prefix_simplex_id=None,
            last_edge_ids=("id",),
            frontier=frozenset({"a"}),
            is_degenerate=False,
            projection_simplex_id=None,
        )
