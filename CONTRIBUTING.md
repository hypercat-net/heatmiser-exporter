# Contributing

Thanks for contributing to **heatmiser-exporter**.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
# Until heatmiser-neohub is on PyPI:
pip install "heatmiser-neohub @ git+https://github.com/hypercat-net/heatmiser-neohub@v0.1.0"
pip install -e ".[dev]"
cp .env.example .env   # set NEOHUB_HOST and NEOHUB_TOKEN
```

If you have a sibling checkout of `heatmiser-neohub`, prefer:

```bash
pip install -e ../heatmiser-neohub
pip install -e ".[dev]"
```

## Checks before opening a PR

```bash
pytest
```

## Pull requests

- Keep changes focused and describe *why* in the PR body.
- Prefer small PRs over large mixed ones.
- Do not commit secrets (`.env`, tokens, hub credentials).

## Reporting issues

Use GitHub Issues and include:

- OS / Python version
- Hub firmware or model if known
- Prometheus / exporter version
- Steps to reproduce and any redacted logs
