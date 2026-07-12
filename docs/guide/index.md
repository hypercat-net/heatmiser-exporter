# heatmiser-exporter

Prometheus exporter for the [IMI Heatmiser NeoHub](https://www.heatmiser.com/neohub-smart-control/),
built on [`heatmiser-neohub`](https://github.com/hypercat-net/heatmiser-neohub).

On every scrape of `/metrics`, the exporter opens a fresh WebSocket connection
to the hub, runs `GET_LIVE_DATA`, and exposes hub- and zone-level gauges.
There is no background poller: Prometheus drives the refresh rate.

## Guides

- [Install](install.html) — pip, uv, Docker, and Compose
- [Metrics](metrics.html) — full metric catalogue

## Quick start

```bash
cp .env.example .env   # set NEOHUB_HOST and NEOHUB_TOKEN
docker compose up -d
curl -s http://localhost:9780/metrics | head
```

## Related links

- [GitHub repository](https://github.com/hypercat-net/heatmiser-exporter)
- [Docker Hub](https://hub.docker.com/r/hypercat42/heatmiser-exporter)
- [heatmiser-neohub on PyPI](https://pypi.org/project/heatmiser-neohub/)
- [heatmiser-neohub docs](https://hypercat-net.github.io/heatmiser-neohub/)
- [IMI Heatmiser Developer Portal](https://dev.heatmiser.com/)
