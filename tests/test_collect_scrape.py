"""Collector scrape-path and readiness tests."""

from __future__ import annotations

import pytest

from heatmiser_neohub.client import NeoHubError
from heatmiser_neohub.models import LiveData

from heatmiser_exporter.collector import NeoHubCollector


def test_collect_success_sets_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    collector = NeoHubCollector(host="127.0.0.1", token="t", timeout=1.0)

    async def fake_scrape() -> LiveData:
        return LiveData.from_dict(
            {
                "HUB_TIME": 100,
                "HUB_AWAY": False,
                "HUB_HOLIDAY": True,
                "devices": [
                    {
                        "ZONE_NAME": "Lounge",
                        "DEVICE_ID": 1,
                        "ACTUAL_TEMP": "20",
                        "SET_TEMP": "19",
                        "AVAILABLE_MODES": ["heat"],
                        "HEAT_ON": False,
                    }
                ],
            }
        )

    monkeypatch.setattr(collector, "_scrape", fake_scrape)
    metrics = list(collector.collect())
    names = {m.name for m in metrics}
    assert "neohub_up" in names
    assert "neohub_scrapes_total" in names
    assert "neohub_temperature_celsius" in names
    assert collector.is_ready is True
    assert collector.last_scrape_ok is True
    up = next(m for m in metrics if m.name == "neohub_up")
    assert any(s.value == 1.0 for s in up.samples if s.name == "neohub_up")
    scrapes = next(m for m in metrics if m.name == "neohub_scrapes_total")
    assert any(s.value == 1.0 for s in scrapes.samples if s.name == "neohub_scrapes_total")


def test_collect_failure_marks_not_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    collector = NeoHubCollector(host="127.0.0.1", token="t", timeout=1.0)

    async def fake_scrape() -> LiveData:
        raise NeoHubError("hub down")

    monkeypatch.setattr(collector, "_scrape", fake_scrape)
    metrics = list(collector.collect())
    assert collector.is_ready is False
    assert collector.last_scrape_ok is False
    up = next(m for m in metrics if m.name == "neohub_up")
    assert any(s.value == 0.0 for s in up.samples if s.name == "neohub_up")
    names = {m.name for m in metrics}
    assert "neohub_temperature_celsius" not in names
