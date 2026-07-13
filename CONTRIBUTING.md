# Contributing

Thanks for contributing to **heatmiser-exporter**.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # set NEOHUB_HOST and NEOHUB_TOKEN
```

For a sibling checkout of `heatmiser-neohub`:

```bash
pip install -e ../heatmiser-neohub
pip install -e ".[dev]"
# or: uv sync --extra dev
```

## Checks before opening a PR

```bash
pytest
```

`pytest` runs with coverage enabled (`pytest-cov`). The suite must stay at or
above the `fail_under` threshold in `pyproject.toml` (currently 85%).

## Pull requests

- Keep changes focused and describe *why* in the PR body.
- Prefer small PRs over large mixed ones.
- Do not commit secrets (`.env`, tokens, hub credentials).

## Releases (Docker)

1. Bump `version` in `pyproject.toml` (and `__version__` if present) to `X.Y.Z`.
2. Commit, push `main`, then tag and push `vX.Y.Z`.

Tagged Docker publishes (`hypercat42/heatmiser-exporter:vX.Y.Z`) re-run Tests
first. Docker `latest` / SHA builds on `main` do not wait on that gate.
The image builds this repo from source and installs `heatmiser-neohub` from
PyPI.

## Reporting issues

Use GitHub Issues and include:

- OS / Python version
- Hub firmware or model if known
- Prometheus / exporter version
- Steps to reproduce and any redacted logs
