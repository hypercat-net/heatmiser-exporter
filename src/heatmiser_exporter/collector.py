"""Prometheus collector that scrapes a IMI Heatmiser NeoHub on every /metrics request."""

from __future__ import annotations

import asyncio
import logging
from typing import Iterable, Iterator, Optional

from prometheus_client.core import GaugeMetricFamily, Metric

from heatmiser_neohub.client import NeoHubClient, NeoHubError
from heatmiser_neohub.models import Device, LiveData

logger = logging.getLogger(__name__)

_ZONE_LABELS = ["zone", "device_id"]


class NeoHubCollector:
    """A prometheus_client custom collector backed by :class:`NeoHubClient`.

    Every time Prometheus scrapes ``/metrics``, :meth:`collect` opens a fresh
    connection to the hub (via ``asyncio.run``), fetches ``GET_LIVE_DATA``, and
    translates it into Prometheus metric families. This keeps the exporter
    stateless between scrapes and always reports current hub state rather
    than a cached snapshot.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        token: Optional[str] = None,
        port: int = 4243,
        *,
        timeout: float = 15.0,
    ) -> None:
        self._host = host
        self._token = token
        self._port = port
        self._timeout = timeout
        self._scrapes_total = 0
        self._scrape_errors_total = 0
        # None until the first /metrics scrape; then True/False for last result.
        self._last_scrape_ok: bool | None = None

    @property
    def last_scrape_ok(self) -> bool | None:
        """Whether the most recent scrape succeeded; ``None`` if none yet."""
        return self._last_scrape_ok

    @property
    def is_ready(self) -> bool:
        """True only after at least one successful NeoHub scrape."""
        return self._last_scrape_ok is True

    def _make_client(self) -> NeoHubClient:
        return NeoHubClient(
            host=self._host,
            token=self._token,
            port=self._port,
            timeout=self._timeout,
        )

    async def _scrape(self) -> LiveData:
        async with self._make_client() as client:
            return await client.get_live_data()

    def collect(self) -> Iterator[Metric]:
        up = GaugeMetricFamily(
            "neohub_up",
            "Whether the last scrape of the NeoHub succeeded (1) or failed (0).",
        )
        scrapes = GaugeMetricFamily(
            "neohub_scrapes_total",
            "Cumulative count of successful NeoHub scrapes.",
        )
        scrape_errors = GaugeMetricFamily(
            "neohub_scrape_errors_total",
            "Cumulative count of failed NeoHub scrapes.",
        )

        try:
            live_data = asyncio.run(self._scrape())
        except (NeoHubError, OSError, asyncio.TimeoutError) as exc:
            logger.warning("NeoHub scrape failed: %s", exc)
            self._scrape_errors_total += 1
            self._last_scrape_ok = False
            up.add_metric([], 0)
            scrapes.add_metric([], self._scrapes_total)
            scrape_errors.add_metric([], self._scrape_errors_total)
            yield up
            yield scrapes
            yield scrape_errors
            return

        self._scrapes_total += 1
        self._last_scrape_ok = True
        up.add_metric([], 1)
        scrapes.add_metric([], self._scrapes_total)
        scrape_errors.add_metric([], self._scrape_errors_total)
        yield up
        yield scrapes
        yield scrape_errors

        yield from self._hub_metrics(live_data)
        yield from self._zone_metrics(live_data.devices)

    def _hub_metrics(self, live_data: LiveData) -> Iterable[Metric]:
        hub_time = GaugeMetricFamily(
            "neohub_hub_time", "Hub clock time (unix epoch seconds)."
        )
        if live_data.hub_time is not None:
            hub_time.add_metric([], float(live_data.hub_time))
        yield hub_time

        hub_away = GaugeMetricFamily(
            "neohub_hub_away", "Whether the hub is in away mode (1) or not (0)."
        )
        hub_away.add_metric([], 1 if live_data.hub_away else 0)
        yield hub_away

        hub_holiday = GaugeMetricFamily(
            "neohub_hub_holiday",
            "Whether the hub is in holiday mode (1) or not (0).",
        )
        hub_holiday.add_metric([], 1 if live_data.hub_holiday else 0)
        yield hub_holiday

    def _zone_metrics(self, devices: list[Device]) -> Iterable[Metric]:
        temperature = GaugeMetricFamily(
            "neohub_temperature_celsius",
            "Actual measured zone temperature.",
            labels=_ZONE_LABELS,
        )
        setpoint = GaugeMetricFamily(
            "neohub_setpoint_celsius",
            "Configured heating setpoint temperature.",
            labels=_ZONE_LABELS,
        )
        cool_setpoint = GaugeMetricFamily(
            "neohub_cool_setpoint_celsius",
            "Configured cooling setpoint temperature.",
            labels=_ZONE_LABELS,
        )
        heat_on = GaugeMetricFamily(
            "neohub_heat_on",
            "Whether the zone is actively calling for heat (1) or not (0).",
            labels=_ZONE_LABELS,
        )
        cool_on = GaugeMetricFamily(
            "neohub_cool_on",
            "Whether the zone is actively calling for cooling (1) or not (0).",
            labels=_ZONE_LABELS,
        )
        standby = GaugeMetricFamily(
            "neohub_standby",
            "Whether the zone is in standby (1) or not (0).",
            labels=_ZONE_LABELS,
        )
        away = GaugeMetricFamily(
            "neohub_away",
            "Whether the zone is in away mode (1) or not (0).",
            labels=_ZONE_LABELS,
        )
        holiday = GaugeMetricFamily(
            "neohub_holiday",
            "Whether the zone is in holiday mode (1) or not (0).",
            labels=_ZONE_LABELS,
        )
        offline = GaugeMetricFamily(
            "neohub_offline",
            "Whether the zone/device is reporting offline (1) or not (0).",
            labels=_ZONE_LABELS,
        )
        low_battery = GaugeMetricFamily(
            "neohub_low_battery",
            "Whether the zone/device reports a low battery (1) or not (0).",
            labels=_ZONE_LABELS,
        )
        lock = GaugeMetricFamily(
            "neohub_lock",
            "Whether the zone controls are locked (1) or not (0).",
            labels=_ZONE_LABELS,
        )
        window_open = GaugeMetricFamily(
            "neohub_window_open",
            "Whether the zone's window-open detection is active (1) or not (0).",
            labels=_ZONE_LABELS,
        )
        hold_on = GaugeMetricFamily(
            "neohub_hold_on",
            "Whether a temporary hold is active for the zone (1) or not (0).",
            labels=_ZONE_LABELS,
        )
        hold_temp = GaugeMetricFamily(
            "neohub_hold_temperature_celsius",
            "Temporary hold setpoint temperature for the zone.",
            labels=_ZONE_LABELS,
        )
        timer_on = GaugeMetricFamily(
            "neohub_timer_on",
            "Whether the zone's timer/schedule is currently active (1) or not (0).",
            labels=_ZONE_LABELS,
        )
        floor_temperature = GaugeMetricFamily(
            "neohub_floor_temperature_celsius",
            "Measured floor temperature, when the zone has a floor sensor.",
            labels=_ZONE_LABELS,
        )
        floor_limit = GaugeMetricFamily(
            "neohub_floor_limit",
            "Whether the zone floor temperature limit is active (1) or not (0).",
            labels=_ZONE_LABELS,
        )
        active_profile = GaugeMetricFamily(
            "neohub_active_profile",
            "Active schedule profile index for the zone.",
            labels=_ZONE_LABELS,
        )
        active_level = GaugeMetricFamily(
            "neohub_active_level",
            "Active comfort level index for the zone.",
            labels=_ZONE_LABELS,
        )
        relative_humidity = GaugeMetricFamily(
            "neohub_relative_humidity_percent",
            "Zone relative humidity percent, when reported.",
            labels=_ZONE_LABELS,
        )
        preheat_active = GaugeMetricFamily(
            "neohub_preheat_active",
            "Whether zone preheat is active (1) or not (0).",
            labels=_ZONE_LABELS,
        )
        modulation_level = GaugeMetricFamily(
            "neohub_modulation_level",
            "Zone modulation level reported by the hub.",
            labels=_ZONE_LABELS,
        )
        hc_mode = GaugeMetricFamily(
            "neohub_hc_mode_info",
            "Heat/cool operating mode reported by the hub (1 for the active mode).",
            labels=[*_ZONE_LABELS, "mode"],
        )
        fan_speed = GaugeMetricFamily(
            "neohub_fan_speed_info",
            "Fan speed setting reported by the hub (1 for the active setting).",
            labels=[*_ZONE_LABELS, "speed"],
        )
        fan_control = GaugeMetricFamily(
            "neohub_fan_control_info",
            "Fan control mode reported by the hub (1 for the active setting).",
            labels=[*_ZONE_LABELS, "control"],
        )

        for device in devices:
            labels = [device.zone_name, self._device_id_label(device)]
            heat = self._supports_mode(device, "heat")
            cool = self._supports_mode(device, "cool")

            if device.actual_temp is not None:
                temperature.add_metric(labels, device.actual_temp)
            if heat and device.set_temp is not None:
                setpoint.add_metric(labels, device.set_temp)
            if cool and device.cool_temp is not None:
                cool_setpoint.add_metric(labels, device.cool_temp)

            if heat:
                heat_on.add_metric(labels, 1 if device.heat_on else 0)
            if cool:
                cool_on.add_metric(labels, 1 if device.cool_on else 0)
            standby.add_metric(labels, 1 if device.standby else 0)
            away.add_metric(labels, 1 if device.away else 0)
            holiday.add_metric(labels, 1 if device.holiday else 0)
            offline.add_metric(labels, 1 if device.offline else 0)
            low_battery.add_metric(labels, 1 if device.low_battery else 0)
            lock.add_metric(labels, 1 if device.lock else 0)
            window_open.add_metric(labels, 1 if device.window_open else 0)
            hold_on.add_metric(labels, 1 if device.hold_on else 0)
            timer_on.add_metric(labels, 1 if device.timer_on else 0)
            floor_limit.add_metric(labels, 1 if device.floor_limit else 0)
            preheat_active.add_metric(
                labels, 1 if self._device_flag(device, "preheat_active", "PREHEAT_ACTIVE") else 0
            )

            if device.hold_temp is not None:
                hold_temp.add_metric(labels, device.hold_temp)
            if device.floor_temp is not None:
                floor_temperature.add_metric(labels, device.floor_temp)
            if device.active_profile is not None:
                active_profile.add_metric(labels, device.active_profile)
            if device.active_level is not None:
                active_level.add_metric(labels, float(device.active_level))

            humidity = self._device_float(device, "relative_humidity", "RELATIVE_HUMIDITY")
            if humidity is not None:
                relative_humidity.add_metric(labels, humidity)

            modulation = self._device_float(device, "modulation_level", "MODULATION_LEVEL")
            if modulation is not None:
                modulation_level.add_metric(labels, modulation)

            mode = self._device_str(device, "hc_mode", "HC_MODE")
            if mode:
                hc_mode.add_metric([*labels, mode], 1)
            speed = self._device_str(device, "fan_speed", "FAN_SPEED")
            if speed:
                fan_speed.add_metric([*labels, speed], 1)
            control = self._device_str(device, "fan_control", "FAN_CONTROL")
            if control:
                fan_control.add_metric([*labels, control], 1)

        yield temperature
        yield setpoint
        yield cool_setpoint
        yield heat_on
        yield cool_on
        yield standby
        yield away
        yield holiday
        yield offline
        yield low_battery
        yield lock
        yield window_open
        yield hold_on
        yield hold_temp
        yield timer_on
        yield floor_temperature
        yield floor_limit
        yield active_profile
        yield active_level
        yield relative_humidity
        yield preheat_active
        yield modulation_level
        yield hc_mode
        yield fan_speed
        yield fan_control

    @staticmethod
    def _supports_mode(device: Device, mode: str) -> bool:
        """Whether to export metrics for ``mode`` (``heat`` / ``cool``).

        Uses :meth:`Device.supports_mode`. When capability data is missing,
        both heat and cool series are still emitted.
        """
        return device.supports_mode(mode)

    @staticmethod
    def _device_flag(device: Device, attr: str, raw_key: str) -> bool:
        if hasattr(device, attr):
            return bool(getattr(device, attr))
        return bool((device.raw or {}).get(raw_key))

    @staticmethod
    def _device_float(device: Device, attr: str, raw_key: str) -> float | None:
        if hasattr(device, attr):
            value = getattr(device, attr)
            if value is not None:
                return float(value)
        raw = (device.raw or {}).get(raw_key)
        if raw is None or raw == "":
            return None
        try:
            return float(raw)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _device_str(device: Device, attr: str, raw_key: str) -> str | None:
        if hasattr(device, attr):
            value = getattr(device, attr)
            if value is not None and str(value).strip():
                return str(value)
        raw = (device.raw or {}).get(raw_key)
        if raw is None:
            return None
        text = str(raw).strip()
        return text or None

    @staticmethod
    def _device_id_label(device: Device) -> str:
        return str(device.device_id) if device.device_id is not None else ""
