"""Smoke tests for heatmiser-exporter."""

from __future__ import annotations

from typer.testing import CliRunner

from heatmiser_exporter import NeoHubCollector, __version__
from heatmiser_exporter.main import app


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_collector_constructs() -> None:
    collector = NeoHubCollector(
        host="127.0.0.1",
        token="dummy",
        port=4243,
        timeout=1.0,
    )
    assert collector is not None


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "NeoHub" in result.stdout
