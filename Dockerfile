# syntax=docker/dockerfile:1
#
# Build the exporter from this repository. heatmiser-neohub is installed from
# PyPI as a normal dependency (not from git).

FROM python:3.13-slim AS build

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.13-slim

LABEL org.opencontainers.image.title="heatmiser-exporter" \
      org.opencontainers.image.description="Prometheus exporter for the IMI Heatmiser NeoHub API" \
      org.opencontainers.image.source="https://github.com/hypercat-net/heatmiser-exporter" \
      org.opencontainers.image.url="https://hub.docker.com/r/hypercat42/heatmiser-exporter" \
      org.opencontainers.image.documentation="https://hypercat-net.github.io/heatmiser-exporter/" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.vendor="Hypercat"

RUN useradd -u 1000 -m exporter

COPY --from=build /install /usr/local

USER exporter

EXPOSE 9780

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:9780/healthz', timeout=4)"

ENTRYPOINT ["heatmiser-exporter"]
CMD []
