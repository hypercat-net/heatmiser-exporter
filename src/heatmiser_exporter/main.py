"""HTTP entry point for the IMI Heatmiser NeoHub Prometheus exporter."""

from __future__ import annotations

import logging
import time
from typing import Optional

import typer
from dotenv import load_dotenv
from prometheus_client import REGISTRY, start_http_server

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

    start_http_server(listen_port, addr=listen_address)
    logger.info(
        "Serving NeoHub metrics on %s:%d (scraping %s:%d)",
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
