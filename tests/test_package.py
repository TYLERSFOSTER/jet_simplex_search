from pathlib import Path

import jet_simplex_search
from jet_simplex_search import __version__


def test_package_imports() -> None:
    assert __version__ == "0.1.0"


def test_package_ships_type_marker() -> None:
    package_root = Path(jet_simplex_search.__file__).resolve().parent

    assert (package_root / "py.typed").is_file()
