# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-13

### Added

- Heat/cool metric gating from NeoHub `AVAILABLE_MODES` (via
  `heatmiser-neohub` `Device.supports_mode`)
- Extended zone metrics: hold temperature, humidity, preheat, modulation,
  floor limit, HC/fan info series
- `/healthz` (liveness) and `/readyz` (last-scrape readiness) HTTP endpoints
- Coverage gate (85%) and expanded collector tests

### Changed

- **Breaking:** rename `neohub_scrape_success` → `neohub_scrapes_total`
  (still a cumulative gauge; pairs with `neohub_scrape_errors_total`)
- Require `heatmiser-neohub>=1.0.0`

### Stability

Version 1.0 freezes the metric catalogue documented in the README / metrics
guide and the `/metrics`, `/healthz`, and `/readyz` endpoints. The exporter
remains Docker-first (not published to PyPI).

## [0.1.0] - 2026-07-12

- Initial Prometheus exporter, docs, and Docker image
