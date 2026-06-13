import pytest

from jet_simplex_search.errors import (
    ArtifactWriteError,
    InvalidGraphError,
    InvalidKError,
    JetSimplexSearchError,
    SimplexInvariantError,
    TowerAdapterError,
)


@pytest.mark.parametrize(
    "error_type",
    [
        InvalidGraphError,
        InvalidKError,
        TowerAdapterError,
        SimplexInvariantError,
        ArtifactWriteError,
    ],
)
def test_package_errors_share_base(error_type: type[Exception]) -> None:
    assert issubclass(error_type, JetSimplexSearchError)
    with pytest.raises(error_type, match="clear"):
        raise error_type("clear message")
