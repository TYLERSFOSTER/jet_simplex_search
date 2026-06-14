from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "release_hygiene.py"
SPEC = importlib.util.spec_from_file_location("release_hygiene", SCRIPT)
assert SPEC is not None
release_hygiene = importlib.util.module_from_spec(SPEC)
sys.modules["release_hygiene"] = release_hygiene
assert SPEC.loader is not None
SPEC.loader.exec_module(release_hygiene)


def test_release_hygiene_passes_minimal_public_tree(tmp_path: Path) -> None:
    _write_minimal_tree(tmp_path)

    report = release_hygiene.run_checks(tmp_path)

    assert report.ok
    assert report.warnings


def test_release_hygiene_fails_on_strict_local_path(tmp_path: Path) -> None:
    _write_minimal_tree(tmp_path)
    (tmp_path / "README.md").write_text(
        "Malik\n"
        "[lineage](docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md)\n"
        "/Users/example/private\n"
    )

    report = release_hygiene.run_checks(tmp_path)

    assert not report.ok
    assert any("Machine-local path" in failure.message for failure in report.failures)


def test_release_hygiene_allows_escaped_text_block_markers(tmp_path: Path) -> None:
    _write_minimal_tree(tmp_path)
    (tmp_path / "tests" / "test_smoke_scripts.py").write_text(
        'marker = "Output:\\n\\n```text\\n"\n'
    )

    report = release_hygiene.run_checks(tmp_path)

    assert report.ok


def test_release_hygiene_warns_on_historical_local_path(tmp_path: Path) -> None:
    _write_minimal_tree(tmp_path)
    log = tmp_path / "docs" / "engineer_continuity" / "log.md"
    log.parent.mkdir(parents=True)
    log.write_text("historical build path: /Users/example/cache\n")

    report = release_hygiene.run_checks(tmp_path)

    assert report.ok
    assert any("historical" in warning.message for warning in report.warnings)


def test_release_hygiene_fails_on_broken_link(tmp_path: Path) -> None:
    _write_minimal_tree(tmp_path)
    (tmp_path / "README.md").write_text(
        "Malik\n"
        "[lineage](docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md)\n"
        "[missing](docs/missing.md)\n"
    )

    report = release_hygiene.run_checks(tmp_path)

    assert not report.ok
    assert any("Broken Markdown link" in failure.message for failure in report.failures)


def test_release_hygiene_fails_on_local_state_collapser_dependency(
    tmp_path: Path,
) -> None:
    _write_minimal_tree(tmp_path)
    _write_pyproject(tmp_path, dependency='../state_collapser", editable = true')

    report = release_hygiene.run_checks(tmp_path)

    assert not report.ok
    assert any(
        "Local sibling state_collapser" in failure.message
        for failure in report.failures
    )


def test_release_hygiene_fails_on_disallowed_claim(tmp_path: Path) -> None:
    _write_minimal_tree(tmp_path)
    (tmp_path / "README.md").write_text(
        "Malik\n"
        "[lineage](docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md)\n"
        "This package is production-ready.\n"
    )

    report = release_hygiene.run_checks(tmp_path)

    assert not report.ok
    assert any(
        "Disallowed public claim" in failure.message for failure in report.failures
    )


def test_release_hygiene_fails_on_missing_malik_lineage_link(tmp_path: Path) -> None:
    _write_minimal_tree(tmp_path)
    (tmp_path / "README.md").write_text("Malik\n")

    report = release_hygiene.run_checks(tmp_path)

    assert not report.ok
    assert any("lineage" in failure.message for failure in report.failures)


def test_release_hygiene_fails_on_bad_hgraphml_boundary(tmp_path: Path) -> None:
    _write_minimal_tree(tmp_path)
    (tmp_path / "README.md").write_text(
        "Malik\n"
        "[lineage](docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md)\n"
        "jet_simplex_search implements CinchNET.\n"
    )

    report = release_hygiene.run_checks(tmp_path)

    assert not report.ok
    assert any("Bad Malik/HGraphML" in failure.message for failure in report.failures)


def _write_minimal_tree(root: Path) -> None:
    (root / "docs" / "design" / "malik_lineage").mkdir(parents=True)
    (root / "docs" / "prime_directive").mkdir(parents=True)
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / "src").mkdir()
    (root / "tests").mkdir(exist_ok=True)
    (root / "smoke").mkdir()
    (root / "README.md").write_text(
        "Malik\n"
        "[lineage](docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md)\n"
        "[license](LICENSE)\n"
    )
    (root / "RELEASE_NOTES.md").write_text("No production-ready claim.\n")
    (root / "SECURITY.md").write_text("No SLA.\n")
    (root / "CONTRIBUTING.md").write_text("Run tests.\n")
    (root / "LICENSE").write_text("MIT\n")
    (root / ".github" / "workflows" / "test.yml").write_text("name: Test\n")
    (root / "docs" / "prime_directive" / "prime_directive.md").write_text("internal\n")
    lineage = (
        root
        / "docs"
        / "design"
        / "malik_lineage"
        / ("01_001_malik_work_progeny_in_jet_simplex_search.md")
    )
    lineage.write_text("Abdullah N. Malik and HGraphML boundary.\n")
    _write_pyproject(root)


def _write_pyproject(
    root: Path,
    *,
    dependency: str = "state-collapser @ git+https://github.com/TYLERSFOSTER/state_collapser.git@v0.7.2",
) -> None:
    (root / "pyproject.toml").write_text(
        "[project]\n"
        f'dependencies = ["{dependency}"]\n'
        "[dependency-groups]\n"
        'dev = ["ruff>=0.8"]\n'
    )
