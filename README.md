# heatmiser-exporter

[![CI](https://github.com/hypercat-net/heatmiser-exporter/actions/workflows/tests.yml/badge.svg)](https://github.com/hypercat-net/heatmiser-exporter/actions/workflows/tests.yml) [![Docs](https://github.com/hypercat-net/heatmiser-exporter/actions/workflows/docs.yml/badge.svg)](https://github.com/hypercat-net/heatmiser-exporter/actions/workflows/docs.yml) [![License](https://img.shields.io/github/license/hypercat-net/heatmiser-exporter)](https://github.com/hypercat-net/heatmiser-exporter/blob/main/LICENSE) [![Docker](https://img.shields.io/docker/v/hypercat42/heatmiser-exporter?label=docker)](https://hub.docker.com/r/hypercat42/heatmiser-exporter)

Prometheus exporter for the [IMI Heatmiser NeoHub](https://www.heatmiser.com/neohub-smart-control/),
built on [`heatmiser-neohub`](https://github.com/hypercat-net/heatmiser-neohub).

[![BuyMeACoffee](https://raw.githubusercontent.com/barcar/buymeacoffee-badges/main/bmc-donate-white.svg)](https://buymeacoffee.com/barcar)

On every scrape of `/metrics`, the exporter opens a fresh connection to the
hub, fetches `GET_LIVE_DATA`, and reports current hub- and zone-level state.
No polling loop or caching: each Prometheus scrape triggers a live hub query.

## Documentation

Published docs (GitHub Pages):
[https://hypercat-net.github.io/heatmiser-exporter/](https://hypercat-net.github.io/heatmiser-exporter/)

## Installation

Until `heatmiser-neohub` is on PyPI, install the library from GitHub, then this
package:

```bash
pip install "heatmiser-neohub @ git+https://github.com/hypercat-net/heatmiser-neohub@v0.1.0"
pip install .
```

For local development against a sibling checkout of `heatmiser-neohub`, use
[uv](https://docs.astral.sh/uv/) (resolves `../heatmiser-neohub` via
`[tool.uv.sources]`):

```bash
uv sync --extra dev
```

Or with pip:

```bash
pip install -e ../heatmiser-neohub
pip install -e ".[dev]"
```

### Docker

Multi-arch image (`linux/amd64`, `linux/arm64`) on Docker Hub as
[`hypercat42/heatmiser-exporter`](https://hub.docker.com/r/hypercat42/heatmiser-exporter):

```bash
cp .env.example .env   # set NEOHUB_HOST and NEOHUB_TOKEN

docker run --rm -p 9780:9780 --env-file .env hypercat42/heatmiser-exporter

# or Compose
docker compose up -d
```

Then scrape `http://localhost:9780/metrics`.

## Configuration

Copy [`.env.example`](.env.example) to `.env`. The exporter loads `.env`
automatically (real environment variables still win).

| Variable                | Flag              | Description                                | Default   |
| ----------------------- | ----------------- | ------------------------------------------ | --------- |
| `NEOHUB_HOST`           | `--neohub-host`   | Hostname or IP of the hub                  | *(required)* |
| `NEOHUB_TOKEN`          | `--neohub-token`  | API token configured on the hub            | *(required)* |
| `NEOHUB_PORT`           | `--neohub-port`   | NeoHub WSS port                            | `4243`    |
| `NEOHUB_TIMEOUT`        | `--neohub-timeout`| Per-scrape timeout, in seconds             | `15.0`    |
| `EXPORTER_LISTEN_ADDRESS` | `--listen-address` | Address the HTTP server binds to         | `0.0.0.0` |
| `EXPORTER_PORT`         | `--listen-port`   | Port for `/metrics`                        | `9780`    |

## Usage

```bash
export NEOHUB_HOST=192.168.0.19
export NEOHUB_TOKEN=your-api-token

heatmiser-exporter
```

Prometheus scrape config:

```yaml
scrape_configs:
  - job_name: heatmiser-neohub
    static_configs:
      - targets: ["localhost:9780"]
```

## Exposed metrics

| Metric                            | Type  | Labels               | Description                                    |
| --------------------------------- | ----- | -------------------- | ---------------------------------------------- |
| `neohub_up`                       | gauge |                      | Last scrape succeeded (1) or failed (0)        |
| `neohub_scrape_success`           | gauge |                      | Cumulative successful scrapes                  |
| `neohub_scrape_errors_total`      | gauge |                      | Cumulative failed scrapes                      |
| `neohub_hub_time`                 | gauge |                      | Hub clock (unix epoch seconds)                 |
| `neohub_hub_away`                 | gauge |                      | Hub away mode                                  |
| `neohub_hub_holiday`              | gauge |                      | Hub holiday mode                               |
| `neohub_temperature_celsius`      | gauge | `zone`, `device_id`  | Measured zone temperature                      |
| `neohub_setpoint_celsius`         | gauge | `zone`, `device_id`  | Heating setpoint                               |
| `neohub_cool_setpoint_celsius`    | gauge | `zone`, `device_id`  | Cooling setpoint                               |
| `neohub_heat_on`                  | gauge | `zone`, `device_id`  | Zone actively heating                          |
| `neohub_cool_on`                  | gauge | `zone`, `device_id`  | Zone actively cooling                          |
| `neohub_standby`                  | gauge | `zone`, `device_id`  | Zone in standby                                |
| `neohub_away`                     | gauge | `zone`, `device_id`  | Zone away mode                                 |
| `neohub_offline`                  | gauge | `zone`, `device_id`  | Zone/device offline                            |
| `neohub_low_battery`              | gauge | `zone`, `device_id`  | Low battery                                    |
| `neohub_window_open`              | gauge | `zone`, `device_id`  | Window-open detection active                   |
| `neohub_hold_on`                  | gauge | `zone`, `device_id`  | Temporary hold active                          |
| `neohub_timer_on`                 | gauge | `zone`, `device_id`  | Timer/schedule active                          |
| `neohub_floor_temperature_celsius`| gauge | `zone`, `device_id`  | Floor temperature (if fitted)                  |
| `neohub_active_profile`           | gauge | `zone`, `device_id`  | Active schedule profile index                  |

## Related links

- [heatmiser-neohub](https://github.com/hypercat-net/heatmiser-neohub) (client library + CLI)
- [neoHub smart control](https://www.heatmiser.com/neohub-smart-control/)
- [IMI Heatmiser Developer Portal](https://dev.heatmiser.com/)

## Development

```bash
pip install -e ../heatmiser-neohub
pip install -e ".[dev]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).
