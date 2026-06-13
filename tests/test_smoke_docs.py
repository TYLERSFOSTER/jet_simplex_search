from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SMOKE = ROOT / "smoke"


def test_public_smoke_scripts_have_markdown_count_arguments() -> None:
    scripts = sorted(SMOKE.glob("smoke_*.py"))

    assert scripts
    for script in scripts:
        markdown = script.with_suffix(".md")
        assert markdown.exists(), f"Missing count argument for {script.name}"
        text = markdown.read_text()
        assert "Command:" in text
        assert "Output:" in text
        assert "Skeleton simplex counts" in text
        assert "No error found" in text
