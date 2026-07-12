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
        self._scrape_success_total = 0
        self._scrape_errors_total = 0

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
        scrape_success = GaugeMetricFamily(
            "neohub_scrape_success",
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
            up.add_metric([], 0)
            scrape_success.add_metric([], self._scrape_success_total)
            scrape_errors.add_metric([], self._scrape_errors_total)
            yield up
            yield scrape_success
            yield scrape_errors
            return

        self._scrape_success_total += 1
        up.add_metric([], 1)
        scrape_success.add_metric([], self._scrape_success_total)
        scrape_errors.add_metric([], self._scrape_errors_total)
        yield up
        yield scrape_success
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
        active_profile = GaugeMetricFamily(
            "neohub_active_profile",
            "Active schedule profile index for the zone.",
            labels=_ZONE_LABELS,
        )

        for device in devices:
            labels = [device.zone_name, self._device_id_label(device)]

            if device.actual_temp is not None:
                temperature.add_metric(labels, device.actual_temp)
            if device.set_temp is not None:
                setpoint.add_metric(labels, device.set_temp)
            if device.cool_temp is not None:
                cool_setpoint.add_metric(labels, device.cool_temp)

            heat_on.add_metric(labels, 1 if device.heat_on else 0)
            cool_on.add_metric(labels, 1 if device.cool_on else 0)
            standby.add_metric(labels, 1 if device.standby else 0)
            away.add_metric(labels, 1 if device.away else 0)
            offline.add_metric(labels, 1 if device.offline else 0)
            low_battery.add_metric(labels, 1 if device.low_battery else 0)
            window_open.add_metric(labels, 1 if device.window_open else 0)
            hold_on.add_metric(labels, 1 if device.hold_on else 0)
            timer_on.add_metric(labels, 1 if device.timer_on else 0)

            if device.floor_temp is not None:
                floor_temperature.add_metric(labels, device.floor_temp)
            if device.active_profile is not None:
                active_profile.add_metric(labels, device.active_profile)

        yield temperature
        yield setpoint
        yield cool_setpoint
        yield heat_on
        yield cool_on
        yield standby
        yield away
        yield offline
        yield low_battery
        yield window_open
        yield hold_on
        yield timer_on
        yield floor_temperature
        yield active_profile

    @staticmethod
    def _device_id_label(device: Device) -> str:
        return str(device.device_id) if device.device_id is not None else ""
