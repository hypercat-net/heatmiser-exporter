"""Smoke tests for heatmiser-exporter."""

from __future__ import annotations

from typer.testing import CliRunner

from heatmiser_exporter import NeoHubCollector, __version__
from heatmiser_exporter.main import app, make_exporter_app


def _invoke(wsgi, path: str) -> tuple[str, bytes]:
    status: dict[str, str] = {}

    def start_response(status_line: str, headers: list[tuple[str, str]]) -> None:
        status["line"] = status_line

    body = b"".join(wsgi({"PATH_INFO": path, "REQUEST_METHOD": "GET"}, start_response))
    return status["line"], body


def test_version() -> None:
    assert __version__ == "1.0.1"


def test_collector_constructs() -> None:
    collector = NeoHubCollector(
        host="127.0.0.1",
        token="dummy",
        port=4243,
        timeout=1.0,
    )
    assert collector is not None
    assert collector.last_scrape_ok is None
    assert collector.is_ready is False


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "NeoHub" in result.stdout


def test_healthz_returns_ok() -> None:
    line, body = _invoke(make_exporter_app(), "/healthz")
    assert line == "200 OK"
    assert body == b"ok\n"


def test_readyz_not_ready_before_scrape() -> None:
    collector = NeoHubCollector(host="127.0.0.1", token="x")
    line, body = _invoke(make_exporter_app(collector=collector), "/readyz")
    assert line.startswith("503")
    assert body == b"not ready\n"


def test_readyz_ok_after_successful_scrape() -> None:
    collector = NeoHubCollector(host="127.0.0.1", token="x")
    collector._last_scrape_ok = True
    line, body = _invoke(make_exporter_app(collector=collector), "/readyz")
    assert line == "200 OK"
    assert body == b"ok\n"


def test_readyz_unavailable_after_failed_scrape() -> None:
    collector = NeoHubCollector(host="127.0.0.1", token="x")
    collector._last_scrape_ok = False
    line, body = _invoke(make_exporter_app(collector=collector), "/readyz")
    assert line.startswith("503")
    assert body == b"unavailable\n"


def test_serve_requires_host_and_token() -> None:
    runner = CliRunner()
    missing_host = runner.invoke(app, ["--neohub-token", "t"], env={"NEOHUB_HOST": ""})
    assert missing_host.exit_code == 1
    assert "host" in missing_host.stderr.lower()

    missing_token = runner.invoke(
        app, ["--neohub-host", "127.0.0.1"], env={"NEOHUB_TOKEN": ""}
    )
    assert missing_token.exit_code == 1
    assert "token" in missing_token.stderr.lower()
