# Install

## pip

Requires [`heatmiser-neohub`](https://pypi.org/project/heatmiser-neohub/) **0.1.3 or newer**
(declared as `heatmiser-neohub>=0.1.3`).

```bash
pip install .
# installs heatmiser-neohub from PyPI as a dependency
```

## Local development

Sibling checkout of `heatmiser-neohub` with uv:

```bash
uv sync --extra dev
```

Or pip editable installs:

```bash
pip install -e ../heatmiser-neohub
pip install -e ".[dev]"
```

## Configuration

Copy `.env.example` to `.env` and set at least:

| Variable       | Required | Default   |
| -------------- | -------- | --------- |
| `NEOHUB_HOST`  | yes      | —         |
| `NEOHUB_TOKEN` | yes      | —         |
| `NEOHUB_PORT`  | no       | `4243`    |
| `NEOHUB_TIMEOUT` | no     | `15.0`    |
| `EXPORTER_LISTEN_ADDRESS` | no | `0.0.0.0` |
| `EXPORTER_PORT` | no      | `9780`    |

The exporter loads `.env` automatically. Flags override env vars.

```bash
heatmiser-exporter
# → http://localhost:9780/metrics
```

## Docker

Image: [`hypercat42/heatmiser-exporter`](https://hub.docker.com/r/hypercat42/heatmiser-exporter)
(`linux/amd64`, `linux/arm64`). Built from this repo; `heatmiser-neohub` comes
from PyPI (`>=0.1.3`). The image defines a Docker `HEALTHCHECK` against
`http://127.0.0.1:9780/healthz` (liveness only; does not scrape the hub).

```bash
docker run --rm -p 9780:9780 --env-file .env hypercat42/heatmiser-exporter
```

## Compose

[`docker-compose.yml`](https://github.com/hypercat-net/heatmiser-exporter/blob/main/docker-compose.yml)
pulls `hypercat42/heatmiser-exporter:latest` from Docker Hub (no local `build:`).
It publishes port `9780`, loads `.env`, and restarts unless stopped.

```bash
cp .env.example .env
docker compose up -d
```

## Prometheus

```yaml
scrape_configs:
  - job_name: heatmiser-neohub
    static_configs:
      - targets: ["localhost:9780"]
```
