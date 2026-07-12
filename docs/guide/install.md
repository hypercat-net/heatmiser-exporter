# Install

## pip (until PyPI)

```bash
pip install "heatmiser-neohub @ git+https://github.com/hypercat-net/heatmiser-neohub@v0.1.0"
pip install .
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
(`linux/amd64`, `linux/arm64`).

```bash
docker run --rm -p 9780:9780 --env-file .env hypercat42/heatmiser-exporter
```

## Compose

```bash
cp .env.example .env
docker compose up -d
```

[`compose.yaml`](https://github.com/hypercat-net/heatmiser-exporter/blob/main/compose.yaml)
publishes port `9780`, loads `.env`, and restarts unless stopped.

## Prometheus

```yaml
scrape_configs:
  - job_name: heatmiser-neohub
    static_configs:
      - targets: ["localhost:9780"]
```
