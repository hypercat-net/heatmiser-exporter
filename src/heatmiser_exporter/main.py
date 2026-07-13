"""HTTP entry point for the IMI Heatmiser NeoHub Prometheus exporter."""

from __future__ import annotations

import logging
import threading
import time
from socketserver import ThreadingMixIn
from typing import Callable, Iterable, Optional
from wsgiref.simple_server import WSGIServer, make_server

import typer
from dotenv import load_dotenv
from prometheus_client import REGISTRY, make_wsgi_app

from heatmiser_exporter.collector import NeoHubCollector

load_dotenv()

app = typer.Typer(
    add_completion=False,
    help="Prometheus exporter for the IMI Heatmiser NeoHub API.",
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("heatmiser_exporter")

StartResponse = Callable[..., None]
WsgiApp = Callable[[dict, StartResponse], Iterable[bytes]]


class _ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True


def make_exporter_app(
    registry=REGISTRY,
    *,
    collector: NeoHubCollector | None = None,
) -> WsgiApp:
    """WSGI app for ``/metrics``, ``/healthz``, and ``/readyz``.

    ``/healthz`` is process liveness. ``/readyz`` reflects the last NeoHub
    scrape (503 until the first successful scrape, or after a failed one).
    """
    metrics_app = make_wsgi_app(registry)

    def application(environ: dict, start_response: StartResponse) -> Iterable[bytes]:
        path = environ.get("PATH_INFO", "")
        if path == "/healthz":
            start_response(
                "200 OK",
                [("Content-Type", "text/plain; charset=utf-8")],
            )
            return [b"ok\n"]
        if path == "/readyz":
            if collector is not None and collector.is_ready:
                start_response(
                    "200 OK",
                    [("Content-Type", "text/plain; charset=utf-8")],
                )
                return [b"ok\n"]
            start_response(
                "503 Service Unavailable",
                [("Content-Type", "text/plain; charset=utf-8")],
            )
            if collector is None or collector.last_scrape_ok is None:
                return [b"not ready\n"]
            return [b"unavailable\n"]
        return metrics_app(environ, start_response)

    return application


def start_exporter_server(
    port: int,
    addr: str = "0.0.0.0",
    registry=REGISTRY,
    *,
    collector: NeoHubCollector | None = None,
) -> None:
    """Serve metrics, healthz, and readyz on a background thread."""
    httpd = make_server(
        addr,
        port,
        make_exporter_app(registry, collector=collector),
        _ThreadingWSGIServer,
    )
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()


@app.command()
def serve(
    neohub_host: Optional[str] = typer.Option(
        None, "--neohub-host", envvar="NEOHUB_HOST", help="NeoHub hostname or IP address."
    ),
    neohub_token: Optional[str] = typer.Option(
        None, "--neohub-token", envvar="NEOHUB_TOKEN", help="NeoHub API token."
    ),
    neohub_port: int = typer.Option(
        4243, "--neohub-port", envvar="NEOHUB_PORT", help="NeoHub WSS port."
    ),
    neohub_timeout: float = typer.Option(
        15.0,
        "--neohub-timeout",
        envvar="NEOHUB_TIMEOUT",
        help="Timeout in seconds for each NeoHub scrape.",
    ),
    listen_address: str = typer.Option(
        "0.0.0.0",
        "--listen-address",
        envvar="EXPORTER_LISTEN_ADDRESS",
        help="Address to bind the exporter's HTTP server to.",
    ),
    listen_port: int = typer.Option(
        9780,
        "--listen-port",
        envvar="EXPORTER_PORT",
        help="Port to expose Prometheus metrics on.",
    ),
) -> None:
    """Start the HTTP server that exposes NeoHub metrics for Prometheus to scrape."""
    if not neohub_host:
        typer.secho(
            "NeoHub host is required (set --neohub-host or NEOHUB_HOST).",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
    if not neohub_token:
        typer.secho(
            "NeoHub API token is required (set --neohub-token or NEOHUB_TOKEN).",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    collector = NeoHubCollector(
        host=neohub_host,
        token=neohub_token,
        port=neohub_port,
        timeout=neohub_timeout,
    )
    REGISTRY.register(collector)

    start_exporter_server(listen_port, addr=listen_address, collector=collector)
    logger.info(
        "Serving on %s:%d (/metrics, /healthz, /readyz); scraping %s:%d",
        listen_address,
        listen_port,
        neohub_host,
        neohub_port,
    )

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        logger.info("Shutting down.")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
