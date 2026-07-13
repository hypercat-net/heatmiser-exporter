# Metrics

All metrics are gauges. Zone metrics carry `zone` and `device_id` labels
(plus an extra label for HC/fan info series).

| Metric | Labels | Description |
| ------ | ------ | ----------- |
| `neohub_up` | | Last scrape succeeded (`1`) or failed (`0`) |
| `neohub_scrape_success` | | Cumulative successful scrapes |
| `neohub_scrape_errors_total` | | Cumulative failed scrapes |
| `neohub_hub_time` | | Hub clock (unix epoch seconds) |
| `neohub_hub_away` | | Hub away mode |
| `neohub_hub_holiday` | | Hub holiday mode |
| `neohub_temperature_celsius` | `zone`, `device_id` | Measured zone temperature |
| `neohub_setpoint_celsius` | `zone`, `device_id` | Heating setpoint (when `heat` is in `AVAILABLE_MODES`) |
| `neohub_cool_setpoint_celsius` | `zone`, `device_id` | Cooling setpoint (when `cool` is in `AVAILABLE_MODES`) |
| `neohub_heat_on` | `zone`, `device_id` | Zone actively heating (when `heat` is available) |
| `neohub_cool_on` | `zone`, `device_id` | Zone actively cooling (when `cool` is available) |
| `neohub_standby` | `zone`, `device_id` | Zone in standby |
| `neohub_away` | `zone`, `device_id` | Zone away mode |
| `neohub_holiday` | `zone`, `device_id` | Zone holiday mode |
| `neohub_offline` | `zone`, `device_id` | Zone/device offline |
| `neohub_low_battery` | `zone`, `device_id` | Low battery |
| `neohub_lock` | `zone`, `device_id` | Zone controls locked |
| `neohub_window_open` | `zone`, `device_id` | Window-open detection active |
| `neohub_hold_on` | `zone`, `device_id` | Temporary hold active |
| `neohub_hold_temperature_celsius` | `zone`, `device_id` | Hold setpoint |
| `neohub_timer_on` | `zone`, `device_id` | Timer/schedule active |
| `neohub_floor_temperature_celsius` | `zone`, `device_id` | Floor temperature (if fitted) |
| `neohub_floor_limit` | `zone`, `device_id` | Floor temperature limit active |
| `neohub_active_profile` | `zone`, `device_id` | Active schedule profile index |
| `neohub_active_level` | `zone`, `device_id` | Active comfort level index |
| `neohub_relative_humidity_percent` | `zone`, `device_id` | Relative humidity percent (when reported) |
| `neohub_preheat_active` | `zone`, `device_id` | Preheat active |
| `neohub_modulation_level` | `zone`, `device_id` | Modulation level |
| `neohub_hc_mode_info` | `zone`, `device_id`, `mode` | HC mode (`1` for the reported mode) |
| `neohub_fan_speed_info` | `zone`, `device_id`, `speed` | Fan speed (`1` for the reported setting) |
| `neohub_fan_control_info` | `zone`, `device_id`, `control` | Fan control (`1` for the reported setting) |

On scrape failure, only `neohub_up`, `neohub_scrape_success`, and
`neohub_scrape_errors_total` are emitted for that request.

Heat and cool series are omitted per zone when the hub's `AVAILABLE_MODES`
list does not include that mode (for example heat-only thermostats skip
cool metrics). If `AVAILABLE_MODES` is missing, both heat and cool series
are still emitted.

## HTTP endpoints

| Path | Purpose |
| ---- | ------- |
| `/metrics` | Prometheus scrape (contacts the NeoHub) |
| `/healthz` | Process liveness (`ok`); does not contact the hub |
| `/readyz` | Ready when the **last** `/metrics` scrape succeeded (`ok`); `503` before the first successful scrape or after a failed one. Does not contact the hub itself. |
