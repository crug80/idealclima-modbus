# idealclima-modbus

Async Python library for controlling Idealclima Modbus fan coil units ([**Comfosplit IKARO HW**](https://www.idealclima.eu/it/radiantori/terminali-idronici/ikaro) and [**Radiantore SKUDO DC Inverter**](https://www.idealclima.eu/it/radiantori/terminali-idronici/radiantore-skudo-dc-inverter)), built on [`modbus-connection`](https://github.com/home-assistant-libs/modbus-connection) for Home Assistant Core integrations and standalone use.

## Requirements & Notes

- **Modbus Unit Address**: Units ship with default Modbus address `15`, which only allows changing the address. **You must assign a unique address** (`1–32`) to each unit before using this library.
- **Serial Settings**: `9600 bps`, `8N1`.
- **Write Function**: Both models only support Modbus function `0x10` (Write Multiple Registers), which is enforced automatically via `force_fc16=True`.

## Installation

For Home Assistant or when providing your own `ModbusUnit`:

```bash
pip install idealclima-modbus
```

For standalone usage with `tmodbus`:

```bash
pip install "idealclima-modbus[tmodbus]"
```

## Usage

```python
import asyncio
from modbus_connection import ModbusSerialParams
from modbus_connection.tmodbus import ModbusConnection
from idealclima_modbus import FanSpeed, IkaroHW, IkaroMode

async def main() -> None:
    conn = ModbusConnection(
        ModbusSerialParams(device="/dev/ttyUSB0", baudrate=9600)
    )
    async with conn:
        unit = conn.for_unit(20)
        ikaro = IkaroHW(unit)
        await ikaro.async_update()
        print(ikaro.readings.ambient_temperature)
        await ikaro.async_set_mode(IkaroMode.COOL)
        await ikaro.async_set_fan_speed(FanSpeed.LOW)
        await ikaro.async_set_power(True)

asyncio.run(main())
```

## Supported Models & Exposed Registers

- **`IkaroHW`** (`Comfosplit IKARO HW`):
  - `readings` (`0x04`): `ambient_temperature` (`46801`)
  - `settings` (`0x03`/`0x10`): `power` (`28301`), `mode` (`28302`), `fan_speed` (`28303`), `target_temp_cool` (`28310`), `target_temp_heat` (`28311`)
  - `async_set_power(enabled, *, stop_fan=True, restore_fan=True)`: when turning off, `stop_fan=True` also sets register `28303` to `FanSpeed.OFF`; when turning on, `restore_fan=True` restores the last active fan speed (defaulting to `FanSpeed.AUTO` if unknown) whenever register `28303` is `None` or `FanSpeed.OFF`.
- **`SkudoDCInverter`** (`Radiantore SKUDO DC Inverter`):
  - `readings` (`0x04`): `ambient_temperature` (`46801`), `coil_temperature` (`46802`), `fan_rpm` (`46804`), `valve_command` (`46805`), `power_state` (`46806`), `running_mode` (`46807`: `SkudoRunningMode.COOL`/`HEAT`), `motor_alarm` (`46808`), `ambient_sensor_alarm` (`46809`), `coil_sensor_alarm` (`46810`)
  - `settings` (`0x03`/`0x10`): `power` (`28301`), `mode` (`28302`), `fan_speed` (`28303`), `key_lock` (`28304`), `sleep` (`28305`), `timer_off_hours` (`28306`), `timer_on_hours` (`28307`), `max_target_temp` (`28308`), `min_target_temp` (`28309`), `target_temp_cool` (`28310`), `target_temp_heat` (`28311`), `target_temp_auto_cool` (`28312`), `target_temp_auto_heat` (`28313`), `anti_draft_threshold` (`28314`), `anti_draft_enabled` (`28315`), `super_silence_enabled` (`28316`), `valve_present` (`28317`), `temperature_unit` (`28319`), `key_lock_enabled` (`28322`), `remote_enabled_with_key_lock` (`28323`), `password_enabled` (`28324`), `fan_intermittent` (`28327`)
