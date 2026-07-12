# Metrics

All metrics are gauges. Zone metrics carry `zone` and `device_id` labels.

| Metric | Labels | Description |
| ------ | ------ | ----------- |
| `neohub_up` | | Last scrape succeeded (`1`) or failed (`0`) |
| `neohub_scrape_success` | | Cumulative successful scrapes |
| `neohub_scrape_errors_total` | | Cumulative failed scrapes |
| `neohub_hub_time` | | Hub clock (unix epoch seconds) |
| `neohub_hub_away` | | Hub away mode |
| `neohub_hub_holiday` | | Hub holiday mode |
| `neohub_temperature_celsius` | `zone`, `device_id` | Measured zone temperature |
| `neohub_setpoint_celsius` | `zone`, `device_id` | Heating setpoint |
| `neohub_cool_setpoint_celsius` | `zone`, `device_id` | Cooling setpoint |
| `neohub_heat_on` | `zone`, `device_id` | Zone actively heating |
| `neohub_cool_on` | `zone`, `device_id` | Zone actively cooling |
| `neohub_standby` | `zone`, `device_id` | Zone in standby |
| `neohub_away` | `zone`, `device_id` | Zone away mode |
| `neohub_offline` | `zone`, `device_id` | Zone/device offline |
| `neohub_low_battery` | `zone`, `device_id` | Low battery |
| `neohub_window_open` | `zone`, `device_id` | Window-open detection active |
| `neohub_hold_on` | `zone`, `device_id` | Temporary hold active |
| `neohub_timer_on` | `zone`, `device_id` | Timer/schedule active |
| `neohub_floor_temperature_celsius` | `zone`, `device_id` | Floor temperature (if fitted) |
| `neohub_active_profile` | `zone`, `device_id` | Active schedule profile index |

On scrape failure, only `neohub_up`, `neohub_scrape_success`, and
`neohub_scrape_errors_total` are emitted for that request.
