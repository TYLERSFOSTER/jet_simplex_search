"""Release hygiene checks for public pre-release preparation."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


STRICT_ROOT_FILES = (
    "README.md",
    "RELEASE_NOTES.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "llms.txt",
    "pyproject.toml",
)
STRICT_DOC_FILES = (
    "docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md",
    "docs/design/initial_design/01_001_static_tower_small_object_simplex_search.md",
    "docs/design/initial_design/01_002_static_tower_small_object_package_blueprint.md",
    "docs/design/initial_design/01_003_static_tower_small_object_implementation_workplan.md",
)
STRICT_DIRS = (
    ".github",
    "src",
    "tests",
    "smoke",
)
WARN_ONLY_DIRS = (
    "docs/engineer_continuity",
    "docs/design/release_prep",
)
CONTENT_FIXTURE_ALLOWLIST = {
    "tests/test_release_hygiene.py",
}
LOCAL_PATH_RE = re.compile(
    r"("
    r"/Users/[^\s)>'\"]+"
    r"|/private/tmp/[^\s)>'\"]+"
    r"|/private/var/[^\s)>'\"]+"
    r"|[A-Za-z]:[\\/](?:Users|Program Files|ProgramData|Windows|Temp|tmp)[\\/][^\s)>'\"]+"
    r")"
)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
)
GENERATED_ARTIFACT_NAMES = {
    "readout_source.json",
    "skeleton_edge_fibers.jsonl",
    "skeleton_loop_fibers.jsonl",
    "simplex_records.jsonl",
    "simplex_fibers.jsonl",
    "edge_fibers.jsonl",
    "h_lift_records.jsonl",
    "h_lift_face_factors.jsonl",
    "diagnostics.json",
}
LARGE_FILE_LIMIT_BYTES = 1_000_000
DISALLOWED_CLAIMS = (
    "production-ready",
    "production ready",
    "benchmark-validated",
    "statistically validated speedup",
    "statistically validated speed-up",
    "fastest",
    "kan replacement is implemented",
    "neural message passing is implemented",
    "implements cinchnet",
    "implements ptvnn",
    "complete implementation of malik",
)
NEGATION_MARKERS = (
    "no ",
    "not ",
    "do not",
    "does not",
    "is not",
    "without",
    "avoid",
    "deferred",
    "unless",
    "exclude",
    "hard stop",
    "must not",
    "should not",
)


@dataclass(frozen=True, slots=True)
class HygieneMessage:
    """A single release hygiene finding."""

    path: str
    message: str


@dataclass(frozen=True, slots=True)
class HygieneReport:
    """Release hygiene result."""

    failures: tuple[HygieneMessage, ...]
    warnings: tuple[HygieneMessage, ...]

    @property
    def ok(self) -> bool:
        """Return whether no failing findings were produced."""

        return not self.failures


def run_checks(repo_root: Path) -> HygieneReport:
    """Run release hygiene checks and return structured findings."""

    root = repo_root.resolve()
    failures: list[HygieneMessage] = []
    warnings: list[HygieneMessage] = []
    files = _tracked_or_all_files(root)
    strict_files = _strict_files(root, files)
    warn_files = _warn_only_files(root, files, strict_files)

    failures.extend(_check_local_paths(root, strict_files, fail=True))
    warnings.extend(_check_local_paths(root, warn_files, fail=False))
    failures.extend(_check_build_outputs(root, files))
    failures.extend(_check_generated_artifacts(root, files))
    failures.extend(_check_large_files(root, files))
    failures.extend(_check_markdown_links(root, strict_files))
    failures.extend(_check_badges(root))
    failures.extend(_check_dependency_source(root))
    failures.extend(_check_disallowed_claims(root, strict_files))
    failures.extend(_check_secrets(root, strict_files))
    failures.extend(_check_malik_and_hgraphml(root, strict_files))
    warnings.extend(_check_prime_directive_link_policy(root))

    return HygieneReport(failures=tuple(failures), warnings=tuple(warnings))


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    report = run_checks(args.repo_root)

    for warning in report.warnings:
        print(f"WARNING {warning.path}: {warning.message}")
    for failure in report.failures:
        print(f"FAIL {failure.path}: {failure.message}")
    if report.ok:
        print("Release hygiene passed.")
        return 0
    print(f"Release hygiene failed with {len(report.failures)} issue(s).")
    return 1


def _tracked_or_all_files(root: Path) -> tuple[Path, ...]:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return tuple(
            sorted(
                path
                for path in root.rglob("*")
                if path.is_file() and ".git" not in path.parts
            )
        )
    paths = [root / line for line in result.stdout.splitlines() if line]
    if not paths:
        return tuple(
            sorted(
                path
                for path in root.rglob("*")
                if path.is_file() and ".git" not in path.parts
            )
        )
    return tuple(path for path in paths if path.exists() and path.is_file())


def _strict_files(root: Path, files: tuple[Path, ...]) -> frozenset[Path]:
    strict: set[Path] = set()
    for relative in (*STRICT_ROOT_FILES, *STRICT_DOC_FILES):
        path = root / relative
        if path.exists() and path.is_file():
            strict.add(path)
    for path in files:
        relative = path.relative_to(root).as_posix()
        if any(
            relative == directory or relative.startswith(f"{directory}/")
            for directory in STRICT_DIRS
        ):
            strict.add(path)
    return frozenset(strict)


def _warn_only_files(
    root: Path,
    files: tuple[Path, ...],
    strict_files: frozenset[Path],
) -> frozenset[Path]:
    warn: set[Path] = set()
    for path in files:
        if path in strict_files:
            continue
        relative = path.relative_to(root).as_posix()
        if any(
            relative == directory or relative.startswith(f"{directory}/")
            for directory in WARN_ONLY_DIRS
        ):
            warn.add(path)
    return frozenset(warn)


def _check_local_paths(
    root: Path,
    files: frozenset[Path],
    *,
    fail: bool,
) -> tuple[HygieneMessage, ...]:
    messages: list[HygieneMessage] = []
    for path in sorted(files):
        if _relative_path(root, path) in CONTENT_FIXTURE_ALLOWLIST:
            continue
        if not _is_text_like(path):
            continue
        text = _read_text(path)
        for match in LOCAL_PATH_RE.finditer(text):
            kind = (
                "Machine-local path in public surface"
                if fail
                else "Machine-local path in historical surface"
            )
            messages.append(_message(root, path, f"{kind}: {match.group(0)}"))
    return tuple(messages)


def _check_build_outputs(
    root: Path, files: tuple[Path, ...]
) -> tuple[HygieneMessage, ...]:
    forbidden_parts = {"dist", "build", ".pytest_cache", ".ruff_cache"}
    messages: list[HygieneMessage] = []
    for path in files:
        relative_parts = set(path.relative_to(root).parts)
        name = path.name
        if relative_parts & forbidden_parts or name.endswith(".egg-info"):
            messages.append(_message(root, path, "Tracked build/cache output."))
    return tuple(messages)


def _check_generated_artifacts(
    root: Path, files: tuple[Path, ...]
) -> tuple[HygieneMessage, ...]:
    messages: list[HygieneMessage] = []
    for path in files:
        if (
            path.name in GENERATED_ARTIFACT_NAMES
            and "tests" not in path.relative_to(root).parts
        ):
            messages.append(
                _message(root, path, "Generated artifact output should not be tracked.")
            )
    return tuple(messages)


def _check_large_files(
    root: Path, files: tuple[Path, ...]
) -> tuple[HygieneMessage, ...]:
    messages: list[HygieneMessage] = []
    for path in files:
        if path.stat().st_size > LARGE_FILE_LIMIT_BYTES:
            messages.append(
                _message(
                    root, path, f"Tracked file exceeds {LARGE_FILE_LIMIT_BYTES} bytes."
                )
            )
    return tuple(messages)


def _check_markdown_links(
    root: Path, files: frozenset[Path]
) -> tuple[HygieneMessage, ...]:
    messages: list[HygieneMessage] = []
    for path in sorted(files):
        if path.suffix.lower() != ".md":
            continue
        text = _read_text(path)
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = raw_target.strip().strip("<>")
            if _is_external_or_anchor(target):
                continue
            clean_target = unquote(target.split("#", 1)[0].split("?", 1)[0])
            if not clean_target:
                continue
            target_path = (path.parent / clean_target).resolve()
            try:
                target_path.relative_to(root)
            except ValueError:
                messages.append(
                    _message(root, path, f"Markdown link escapes repo: {raw_target}")
                )
                continue
            if not target_path.exists():
                messages.append(
                    _message(root, path, f"Broken Markdown link: {raw_target}")
                )
    return tuple(messages)


def _check_badges(root: Path) -> tuple[HygieneMessage, ...]:
    readme = root / "README.md"
    if not readme.exists():
        return ()
    text = _read_text(readme).lower()
    messages: list[HygieneMessage] = []
    if "badge/pypi" in text or "img.shields.io/pypi" in text:
        messages.append(
            _message(root, readme, "README contains a PyPI badge or badge claim.")
        )
    if "badge/coverage" in text or "codecov" in text or "coveralls" in text:
        messages.append(
            _message(root, readme, "README contains a coverage badge or badge claim.")
        )
    if "readthedocs" in text or "docs badge" in text:
        messages.append(
            _message(root, readme, "README contains a docs-hosting badge claim.")
        )
    if (
        "actions/workflows/test.yml/badge.svg" in text
        and not (root / ".github/workflows/test.yml").exists()
    ):
        messages.append(
            _message(root, readme, "README has CI badge but workflow is missing.")
        )
    if (
        "lint-ruff" in text
        and "ruff" not in _read_text(root / "pyproject.toml").lower()
    ):
        messages.append(
            _message(root, readme, "README has Ruff badge but Ruff is not configured.")
        )
    return tuple(messages)


def _check_dependency_source(root: Path) -> tuple[HygieneMessage, ...]:
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return ()
    text = _read_text(pyproject)
    messages: list[HygieneMessage] = []
    if "../state_collapser" in text:
        messages.append(
            _message(
                root,
                pyproject,
                "Local sibling state_collapser dependency is not release-safe.",
            )
        )
    expected = "git+https://github.com/TYLERSFOSTER/state_collapser.git@v0.7.2"
    if "state-collapser" in text and expected not in text:
        messages.append(
            _message(
                root,
                pyproject,
                "state-collapser dependency is not the approved v0.7.2 GitHub tag.",
            )
        )
    return tuple(messages)


def _check_disallowed_claims(
    root: Path, files: frozenset[Path]
) -> tuple[HygieneMessage, ...]:
    messages: list[HygieneMessage] = []
    for path in sorted(files):
        if _relative_path(root, path) in CONTENT_FIXTURE_ALLOWLIST:
            continue
        if not _is_text_like(path):
            continue
        for line in _read_text(path).splitlines():
            normalized = line.lower()
            if any(marker in normalized for marker in NEGATION_MARKERS):
                continue
            for claim in DISALLOWED_CLAIMS:
                if claim in normalized:
                    messages.append(
                        _message(root, path, f"Disallowed public claim: {line.strip()}")
                    )
    return tuple(messages)


def _check_secrets(root: Path, files: frozenset[Path]) -> tuple[HygieneMessage, ...]:
    messages: list[HygieneMessage] = []
    for path in sorted(files):
        if _relative_path(root, path) in CONTENT_FIXTURE_ALLOWLIST:
            continue
        if not _is_text_like(path):
            continue
        text = _read_text(path)
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                messages.append(_message(root, path, "Possible secret or credential."))
    return tuple(messages)


def _check_malik_and_hgraphml(
    root: Path, files: frozenset[Path]
) -> tuple[HygieneMessage, ...]:
    readme = root / "README.md"
    messages: list[HygieneMessage] = []
    if readme.exists():
        text = _read_text(readme)
        if "Malik" not in text:
            messages.append(
                _message(root, readme, "README is missing Malik attribution.")
            )
        lineage = "docs/design/malik_lineage/01_001_malik_work_progeny_in_jet_simplex_search.md"
        if lineage not in text:
            messages.append(
                _message(root, readme, "README is missing Malik lineage document link.")
            )
    for path in sorted(files):
        if _relative_path(root, path) in CONTENT_FIXTURE_ALLOWLIST:
            continue
        if not _is_text_like(path):
            continue
        for line in _read_text(path).splitlines():
            normalized = line.lower()
            if any(marker in normalized for marker in NEGATION_MARKERS):
                continue
            bad_boundary = (
                "jet_simplex_search implements hgraphml" in normalized
                or "jet_simplex_search implements cinchnet" in normalized
                or "jet_simplex_search implements ptvnn" in normalized
                or "hgraphml is already full cinchnet" in normalized
            )
            if bad_boundary:
                messages.append(
                    _message(root, path, f"Bad Malik/HGraphML framing: {line.strip()}")
                )
    return tuple(messages)


def _check_prime_directive_link_policy(root: Path) -> tuple[HygieneMessage, ...]:
    readme = root / "README.md"
    prime = root / "docs/prime_directive"
    if not readme.exists() or not prime.exists():
        return ()
    if "docs/prime_directive" not in _read_text(readme):
        return (
            _message(
                root,
                prime,
                "docs/prime_directive is present and intentionally unlinked from README.",
            ),
        )
    return ()


def _message(root: Path, path: Path, message: str) -> HygieneMessage:
    return HygieneMessage(path=_relative_path(root, path), message=message)


def _relative_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _is_external_or_anchor(target: str) -> bool:
    split = urlsplit(target)
    return bool(split.scheme or target.startswith("#") or target.startswith("mailto:"))


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def _is_text_like(path: Path) -> bool:
    return path.suffix.lower() in {
        ".cff",
        ".cfg",
        ".ini",
        ".json",
        ".md",
        ".py",
        ".toml",
        ".txt",
        ".yml",
        ".yaml",
    } or path.name in {"LICENSE"}


if __name__ == "__main__":
    sys.exit(main())
