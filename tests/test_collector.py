"""Unit tests for NeoHubCollector metric gating."""

from __future__ import annotations

import pytest

from heatmiser_neohub.models import Device, LiveData
from heatmiser_exporter.collector import NeoHubCollector


def test_zone_metrics_omit_cool_when_heat_only() -> None:
    collector = NeoHubCollector(host="127.0.0.1", token="x")
    heat_only = Device.from_dict(
        {
            "ZONE_NAME": "Lounge",
            "DEVICE_ID": 1,
            "ACTUAL_TEMP": "21.0",
            "SET_TEMP": "20.0",
            "COOL_TEMP": 0,
            "HEAT_ON": True,
            "COOL_ON": False,
            "AVAILABLE_MODES": ["heat"],
        }
    )

    metrics = list(collector._zone_metrics([heat_only]))
    names = {m.name: m for m in metrics}

    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1"} and s.value == 21.0
        for s in names["neohub_temperature_celsius"].samples
        if s.name == "neohub_temperature_celsius"
    )
    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1"} and s.value == 20.0
        for s in names["neohub_setpoint_celsius"].samples
        if s.name == "neohub_setpoint_celsius"
    )
    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1"} and s.value == 1.0
        for s in names["neohub_heat_on"].samples
        if s.name == "neohub_heat_on"
    )
    # Cool series present as families but with no samples for this zone.
    assert not [
        s
        for s in names["neohub_cool_on"].samples
        if s.name == "neohub_cool_on"
    ]
    assert not [
        s
        for s in names["neohub_cool_setpoint_celsius"].samples
        if s.name == "neohub_cool_setpoint_celsius"
    ]


def test_zone_metrics_emit_cool_when_available() -> None:
    collector = NeoHubCollector(host="127.0.0.1", token="x")
    hc = Device.from_dict(
        {
            "ZONE_NAME": "Office",
            "DEVICE_ID": 2,
            "SET_TEMP": "21.0",
            "COOL_TEMP": "18.0",
            "HEAT_ON": False,
            "COOL_ON": True,
            "AVAILABLE_MODES": ["heat", "cool"],
        }
    )

    metrics = list(collector._zone_metrics([hc]))
    names = {m.name: m for m in metrics}

    assert any(
        s.labels == {"zone": "Office", "device_id": "2"} and s.value == 1.0
        for s in names["neohub_cool_on"].samples
        if s.name == "neohub_cool_on"
    )
    assert any(
        s.labels == {"zone": "Office", "device_id": "2"} and s.value == 18.0
        for s in names["neohub_cool_setpoint_celsius"].samples
        if s.name == "neohub_cool_setpoint_celsius"
    )


def test_zone_metrics_emit_extended_live_fields() -> None:
    collector = NeoHubCollector(host="127.0.0.1", token="x")
    device = Device.from_dict(
        {
            "ZONE_NAME": "Lounge",
            "DEVICE_ID": 1,
            "HOLD_TEMP": 18,
            "HOLD_ON": True,
            "ACTIVE_LEVEL": 2,
            "RELATIVE_HUMIDITY": 45,
            "PREHEAT_ACTIVE": True,
            "MODULATION_LEVEL": 3,
            "FLOOR_LIMIT": True,
            "HOLIDAY": True,
            "LOCK": True,
            "HC_MODE": "VENT",
            "FAN_SPEED": "Custom",
            "FAN_CONTROL": "Automatic",
            "AVAILABLE_MODES": ["heat"],
        }
    )

    metrics = list(collector._zone_metrics([device]))
    names = {m.name: m for m in metrics}

    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1"} and s.value == 18.0
        for s in names["neohub_hold_temperature_celsius"].samples
        if s.name == "neohub_hold_temperature_celsius"
    )
    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1"} and s.value == 2.0
        for s in names["neohub_active_level"].samples
        if s.name == "neohub_active_level"
    )
    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1"} and s.value == 45.0
        for s in names["neohub_relative_humidity_percent"].samples
        if s.name == "neohub_relative_humidity_percent"
    )
    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1"} and s.value == 1.0
        for s in names["neohub_preheat_active"].samples
        if s.name == "neohub_preheat_active"
    )
    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1"} and s.value == 3.0
        for s in names["neohub_modulation_level"].samples
        if s.name == "neohub_modulation_level"
    )
    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1"} and s.value == 1.0
        for s in names["neohub_floor_limit"].samples
        if s.name == "neohub_floor_limit"
    )
    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1"} and s.value == 1.0
        for s in names["neohub_holiday"].samples
        if s.name == "neohub_holiday"
    )
    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1"} and s.value == 1.0
        for s in names["neohub_lock"].samples
        if s.name == "neohub_lock"
    )
    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1", "mode": "VENT"} and s.value == 1.0
        for s in names["neohub_hc_mode_info"].samples
        if s.name == "neohub_hc_mode_info"
    )
    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1", "speed": "Custom"}
        and s.value == 1.0
        for s in names["neohub_fan_speed_info"].samples
        if s.name == "neohub_fan_speed_info"
    )
    assert any(
        s.labels == {"zone": "Lounge", "device_id": "1", "control": "Automatic"}
        and s.value == 1.0
        for s in names["neohub_fan_control_info"].samples
        if s.name == "neohub_fan_control_info"
    )


EXPECTED_METRIC_FAMILIES = frozenset(
    {
        "neohub_up",
        "neohub_scrapes_total",
        "neohub_scrape_errors_total",
        "neohub_hub_time",
        "neohub_hub_away",
        "neohub_hub_holiday",
        "neohub_temperature_celsius",
        "neohub_setpoint_celsius",
        "neohub_cool_setpoint_celsius",
        "neohub_heat_on",
        "neohub_cool_on",
        "neohub_standby",
        "neohub_away",
        "neohub_holiday",
        "neohub_offline",
        "neohub_low_battery",
        "neohub_lock",
        "neohub_window_open",
        "neohub_hold_on",
        "neohub_hold_temperature_celsius",
        "neohub_timer_on",
        "neohub_floor_temperature_celsius",
        "neohub_floor_limit",
        "neohub_active_profile",
        "neohub_active_level",
        "neohub_relative_humidity_percent",
        "neohub_preheat_active",
        "neohub_modulation_level",
        "neohub_hc_mode_info",
        "neohub_fan_speed_info",
        "neohub_fan_control_info",
    }
)


def test_collect_metric_family_names_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Golden list of metric family names for the 1.0 freeze."""
    collector = NeoHubCollector(host="127.0.0.1", token="t", timeout=1.0)

    async def fake_scrape() -> LiveData:
        return LiveData.from_dict(
            {
                "HUB_TIME": 1,
                "devices": [{"ZONE_NAME": "Z", "DEVICE_ID": 1, "AVAILABLE_MODES": ["heat"]}],
            }
        )

    monkeypatch.setattr(collector, "_scrape", fake_scrape)
    names = {m.name for m in collector.collect()}
    assert names == EXPECTED_METRIC_FAMILIES


def test_zone_metrics_emit_both_when_modes_unknown() -> None:
    collector = NeoHubCollector(host="127.0.0.1", token="x")
    device = Device.from_dict(
        {
            "ZONE_NAME": "Hall",
            "DEVICE_ID": 3,
            "SET_TEMP": "19.0",
            "COOL_TEMP": "0",
            "HEAT_ON": False,
            "COOL_ON": False,
        }
    )
    assert device.available_modes is None

    metrics = list(collector._zone_metrics([device]))
    names = {m.name: m for m in metrics}

    assert any(
        s.labels.get("zone") == "Hall"
        for s in names["neohub_heat_on"].samples
        if s.name == "neohub_heat_on"
    )
    assert any(
        s.labels.get("zone") == "Hall"
        for s in names["neohub_cool_on"].samples
        if s.name == "neohub_cool_on"
    )
