# heatmiser-exporter

[![CI](https://github.com/hypercat-net/heatmiser-exporter/actions/workflows/tests.yaml/badge.svg)](https://github.com/hypercat-net/heatmiser-exporter/actions/workflows/tests.yaml) [![Pages](https://github.com/hypercat-net/heatmiser-exporter/actions/workflows/pages.yaml/badge.svg)](https://github.com/hypercat-net/heatmiser-exporter/actions/workflows/pages.yaml) [![License](https://img.shields.io/github/license/hypercat-net/heatmiser-exporter)](https://github.com/hypercat-net/heatmiser-exporter/blob/main/LICENSE) [![Docker](https://img.shields.io/docker/v/hypercat42/heatmiser-exporter?label=docker)](https://hub.docker.com/r/hypercat42/heatmiser-exporter)

Prometheus exporter for the [IMI Heatmiser NeoHub](https://www.heatmiser.com/neohub-smart-control/),
built on [`heatmiser-neohub`](https://pypi.org/project/heatmiser-neohub/).

[![BuyMeACoffee](https://raw.githubusercontent.com/barcar/buymeacoffee-badges/main/bmc-donate-white.svg)](https://buymeacoffee.com/barcar)

On every scrape of `/metrics`, the exporter opens a fresh connection to the
hub, fetches `GET_LIVE_DATA`, and reports current hub- and zone-level state.
No polling loop or caching: each Prometheus scrape triggers a live hub query.

## Documentation

Published docs (GitHub Pages):
[https://hypercat-net.github.io/heatmiser-exporter/](https://hypercat-net.github.io/heatmiser-exporter/)

## Installation

```bash
pip install .
# pulls heatmiser-neohub>=1.0.0 from PyPI automatically
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
[`hypercat42/heatmiser-exporter`](https://hub.docker.com/r/hypercat42/heatmiser-exporter).
The image is built from this repository; `heatmiser-neohub>=1.0.0` is installed from
PyPI. A Docker `HEALTHCHECK` probes `/healthz` on port `9780` (process
liveness; does not scrape the hub).

```bash
cp .env.example .env   # set NEOHUB_HOST and NEOHUB_TOKEN

docker run --rm -p 9780:9780 --env-file .env hypercat42/heatmiser-exporter

# or Compose (pulls the Hub image; no local build)
docker compose up -d
```

Then scrape `http://localhost:9780/metrics`. Liveness: `/healthz`. Readiness
(last scrape): `/readyz`.

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
| `neohub_scrapes_total`            | gauge |                      | Cumulative successful scrapes                  |
| `neohub_scrape_errors_total`      | gauge |                      | Cumulative failed scrapes                      |
| `neohub_hub_time`                 | gauge |                      | Hub clock (unix epoch seconds)                 |
| `neohub_hub_away`                 | gauge |                      | Hub away mode                                  |
| `neohub_hub_holiday`              | gauge |                      | Hub holiday mode                               |
| `neohub_temperature_celsius`      | gauge | `zone`, `device_id`  | Measured zone temperature                      |
| `neohub_setpoint_celsius`         | gauge | `zone`, `device_id`  | Heating setpoint (`AVAILABLE_MODES` includes `heat`) |
| `neohub_cool_setpoint_celsius`    | gauge | `zone`, `device_id`  | Cooling setpoint (`AVAILABLE_MODES` includes `cool`) |
| `neohub_heat_on`                  | gauge | `zone`, `device_id`  | Zone actively heating (when `heat` is available)    |
| `neohub_cool_on`                  | gauge | `zone`, `device_id`  | Zone actively cooling (when `cool` is available)    |
| `neohub_standby`                  | gauge | `zone`, `device_id`  | Zone in standby                                |
| `neohub_away`                     | gauge | `zone`, `device_id`  | Zone away mode                                 |
| `neohub_holiday`                  | gauge | `zone`, `device_id`  | Zone holiday mode                              |
| `neohub_offline`                  | gauge | `zone`, `device_id`  | Zone/device offline                            |
| `neohub_low_battery`              | gauge | `zone`, `device_id`  | Low battery                                    |
| `neohub_lock`                     | gauge | `zone`, `device_id`  | Zone controls locked                           |
| `neohub_window_open`              | gauge | `zone`, `device_id`  | Window-open detection active                   |
| `neohub_hold_on`                  | gauge | `zone`, `device_id`  | Temporary hold active                          |
| `neohub_hold_temperature_celsius` | gauge | `zone`, `device_id`  | Hold setpoint                                  |
| `neohub_timer_on`                 | gauge | `zone`, `device_id`  | Timer/schedule active                          |
| `neohub_floor_temperature_celsius`| gauge | `zone`, `device_id`  | Floor temperature (if fitted)                  |
| `neohub_floor_limit`              | gauge | `zone`, `device_id`  | Floor temperature limit active                 |
| `neohub_active_profile`           | gauge | `zone`, `device_id`  | Active schedule profile index                  |
| `neohub_active_level`             | gauge | `zone`, `device_id`  | Active comfort level index                     |
| `neohub_relative_humidity_percent`| gauge | `zone`, `device_id`  | Relative humidity percent (when reported)      |
| `neohub_preheat_active`           | gauge | `zone`, `device_id`  | Preheat active                                 |
| `neohub_modulation_level`         | gauge | `zone`, `device_id`  | Modulation level                               |
| `neohub_hc_mode_info`             | gauge | `zone`, `device_id`, `mode` | HC mode (`1` for reported mode)       |
| `neohub_fan_speed_info`           | gauge | `zone`, `device_id`, `speed` | Fan speed (`1` for reported setting) |
| `neohub_fan_control_info`         | gauge | `zone`, `device_id`, `control` | Fan control (`1` for reported setting) |

Heat/cool series are omitted per zone when `AVAILABLE_MODES` does not list that
mode. If the hub omits `AVAILABLE_MODES`, both heat and cool series are still
emitted. Families with no samples are omitted from the scrape output entirely.

| Metric | heat only | cool only | heat + cool |
| ------ | --------- | --------- | ----------- |
| `neohub_setpoint_celsius` | yes | no | yes |
| `neohub_heat_on` | yes | no | yes |
| `neohub_cool_setpoint_celsius` | no | yes | yes |
| `neohub_cool_on` | no | yes | yes |

See [Metrics](https://hypercat-net.github.io/heatmiser-exporter/guide/metrics/)
for details.

## Related links

- [heatmiser-neohub on PyPI](https://pypi.org/project/heatmiser-neohub/)
- [heatmiser-neohub](https://github.com/hypercat-net/heatmiser-neohub) (client library + CLI)
- [neoHub smart control](https://www.heatmiser.com/neohub-smart-control/)
- [IMI Heatmiser Developer Portal](https://dev.heatmiser.com/)

## Development

```bash
pip install -e ".[dev]"
pytest   # includes coverage; fail_under is configured in pyproject.toml
```

## License

MIT — see [LICENSE](LICENSE).
