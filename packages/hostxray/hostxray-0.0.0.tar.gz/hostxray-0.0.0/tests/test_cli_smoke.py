from __future__ import annotations

from hostxray.cli import main


def test_cli_smoke(capsys):
    rc = main(["--format", "json", "--profile", "minimal"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip().startswith("{")
