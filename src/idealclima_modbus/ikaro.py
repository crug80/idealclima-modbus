"""Comfosplit IKARO HW Modbus device model."""

from __future__ import annotations

from modbus_connection import ModbusUnit
from modbus_connection.model import UpdateReport, enum

from .base import (
    BaseIdealclimaDevice,
    BaseIdealclimaReadings,
    BaseIdealclimaSettings,
)
from .enums import FanSpeed, IkaroMode


class IkaroReadings(BaseIdealclimaReadings):
    """Input registers for Comfosplit IKARO HW."""


class IkaroSettings(BaseIdealclimaSettings):
    """Holding registers for Comfosplit IKARO HW."""

    mode = enum(28302, IkaroMode, signed=True, writable=True, force_fc16=True)


class IkaroHW(BaseIdealclimaDevice[IkaroReadings, IkaroSettings]):
    """Comfosplit IKARO HW fan coil unit."""

    def __init__(self, unit: ModbusUnit) -> None:
        """Initialize an IKARO HW device bound to a ModbusUnit."""
        super().__init__(unit, IkaroReadings(unit), IkaroSettings(unit))
        self._last_fan_speed: FanSpeed = FanSpeed.AUTO
        self._known_fan_speed: FanSpeed | None = None

    def _remember_fan_speed(self, speed: FanSpeed | None) -> None:
        """Remember the last active (non-OFF) fan speed."""
        if speed is not None and speed is not FanSpeed.OFF:
            self._last_fan_speed = speed

    def _record_fan_speed(self, speed: FanSpeed | None) -> None:
        """Update the known fan speed and remember it if active."""
        self._known_fan_speed = speed
        self._remember_fan_speed(speed)

    async def async_update_settings(self) -> UpdateReport:
        """Poll holding registers and remember the active fan speed."""
        report = await super().async_update_settings()
        self._record_fan_speed(self.settings.fan_speed)
        return report

    async def async_update(self) -> UpdateReport:
        """Poll readings and settings and remember the active fan speed."""
        report = await super().async_update()
        self._record_fan_speed(self.settings.fan_speed)
        return report

    async def async_set_fan_speed(self, speed: FanSpeed) -> None:
        """Set the target fan speed (register 28303) and remember it if active."""
        await super().async_set_fan_speed(speed)
        self._record_fan_speed(speed)

    async def async_set_power(
        self,
        enabled: bool,
        *,
        stop_fan: bool = True,
        restore_fan: bool = True,
    ) -> None:
        """Turn the unit on or off; stops/restores the fan by default."""
        self._remember_fan_speed(self._known_fan_speed)
        await self._async_set_power(enabled, stop_fan=stop_fan)
        if not enabled and stop_fan:
            self._known_fan_speed = FanSpeed.OFF
        elif enabled and restore_fan and self._known_fan_speed in (None, FanSpeed.OFF):
            await self.settings.write("fan_speed", self._last_fan_speed)
            self._known_fan_speed = self._last_fan_speed

    async def async_set_mode(self, mode: IkaroMode) -> None:
        """Set the operating mode (register 28302)."""
        await self.settings.write("mode", mode)
