from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SMOKE = ROOT / "smoke"


@pytest.mark.parametrize("script", sorted(SMOKE.glob("smoke_*.py")))
def test_smoke_script_stdout_matches_documented_snapshot(script: Path) -> None:
    expected = _documented_output(script.with_suffix(".md"))
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [
            str(ROOT / "src"),
            str(SMOKE),
            env.get("PYTHONPATH", ""),
        ]
    )

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )

    assert result.stdout == expected
    assert result.stderr == ""


def _documented_output(markdown: Path) -> str:
    text = markdown.read_text()
    marker = "Output:\n\n```text\n"
    start = text.index(marker) + len(marker)
    end = text.index("\n```", start)
    return text[start:end] + "\n"
