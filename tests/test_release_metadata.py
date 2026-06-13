from __future__ import annotations

import tomllib
from pathlib import Path

import jet_simplex_search


ROOT = Path(__file__).resolve().parents[1]


def _pyproject() -> dict[str, object]:
    return tomllib.loads((ROOT / "pyproject.toml").read_text())


def test_project_metadata_matches_package_version() -> None:
    project = _pyproject()["project"]

    assert project["name"] == "jet-simplex-search"
    assert project["version"] == jet_simplex_search.__version__
    assert project["requires-python"] == ">=3.11,<3.13"


def test_release_dependency_uses_state_collapser_github_tag() -> None:
    data = _pyproject()
    dependencies = data["project"]["dependencies"]
    state_collapser_deps = [
        dependency
        for dependency in dependencies
        if dependency.startswith("state-collapser @")
    ]

    assert state_collapser_deps == [
        "state-collapser @ git+https://github.com/TYLERSFOSTER/state_collapser.git@v0.7.2"
    ]
    assert "sources" not in data.get("tool", {}).get("uv", {})


def test_release_metadata_has_urls_classifiers_and_ruff() -> None:
    data = _pyproject()
    project = data["project"]
    urls = project["urls"]
    dev_dependencies = data["dependency-groups"]["dev"]

    assert urls["Homepage"].endswith("/jet_simplex_search")
    assert urls["Repository"].endswith("/jet_simplex_search")
    assert urls["Issues"].endswith("/jet_simplex_search/issues")
    assert "Development Status :: 3 - Alpha" in project["classifiers"]
    assert "Programming Language :: Python :: 3.11" in project["classifiers"]
    assert "Programming Language :: Python :: 3.12" in project["classifiers"]
    assert any(dependency.startswith("ruff") for dependency in dev_dependencies)


def test_readme_python_badge_matches_python_range() -> None:
    readme = (ROOT / "README.md").read_text()

    assert "python-3.11%20%7C%203.12" in readme
