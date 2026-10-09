"""Point behaviors: analogs lag toward a target, everything else holds."""

from __future__ import annotations

import math
import random
import zlib

_BAD_STATUS = (
    "alm",
    "fail",
    "fault",
    "lost",
    "shutdown",
    "offline",
    "error",
    "crossed",
    "notinsync",
    "discharged",
    "retransfer",
)


def _phase(name: str) -> float:
    return (zlib.adler32(name.encode("utf-8")) % 1000) / 1000.0 * math.tau


def _enum_default(name: str) -> int:
    if "Count" in name:
        return 1
    digits = "".join(ch for ch in name if ch.isdigit())
    if "Priority" in name and digits:
        return int(digits[-2:])
    if any(token in name for token in ("Mode", "Type", "Selection", "Source", "Lead")):
        return 1
    return 0


def normal_status(spec: dict) -> bool:
    name = spec["name"]
    lowered = name.lower()
    if any(token in lowered for token in _BAD_STATUS):
        return False
    if "pump3" in lowered:
        return False
    if "source2" in lowered:
        return False
    return True


def nominal_number(spec: dict) -> float:
    name = spec["name"]
    units = spec["units"]
    if spec["value_kind"] == "counter":
        return 1500.0
    if units == "°F":
        if "ServerGlySupTemp" in name:
            return 80.0
        if "SP" in name and ("SupAir" in name or "Room" in name or "Control" in name):
            return 72.0
        if "SP" in name and "OA" in name:
            return 65.0
        if "SP" in name:
            return 70.0
        if "OA" in name or "Ambient" in name or "Outside" in name:
            return 82.0
        if any(token in name for token in ("ColdAisle", "Room", "Space")):
            return 72.0
        if "Ret" in name and "Air" in name:
            return 90.0
        if "Sup" in name and "Air" in name:
            return 68.0
        if "Ret" in name:
            return 88.0
        if "Sup" in name or "Outlet" in name:
            return 60.0 if name.startswith("ChillerGly") or "CHW" in name else 80.0
        if "Panel" in name:
            return 90.0
        return 75.0
    if units == "psi":
        return 12.0 if "DP" in name else 35.0
    if units == "gpm":
        if "Server" in name:
            return 800.0
        if "Header" in name:
            return 400.0
        return 220.0
    if units == "%":
        if "Pump3" in name:
            return 0.0
        if "Min" in name:
            return 20.0
        return 55.0
    if units == "%rh":
        return 45.0
    if units == "rpm":
        if "Comp" in name:
            return 5000.0
        if "Fan" in name:
            return 900.0
        return 1750.0
    if units == "A":
        return 40.0
    if units == "kW":
        if "Fan" in name:
            return 3.0
        if "Tot" in name or "Active" in name or "Capacity" in name:
            return 180.0
        return 40.0
    if units == "V":
        return 480.0
    if units == "Hz":
        return 60.0
    if units == "in/WC":
        return 0.05 if "SP" in name else 0.04
    if units == "tons":
        return 25.0
    if units == "lb/ft³":
        return 62.4
    if units == "BTU/lb":
        return 0.95
    if units == "lb/s":
        return 12.0
    if name == "MPUE":
        return 1.15
    return float(_enum_default(name))


def _band(spec: dict, nominal: float) -> tuple[float, float]:
    units = spec["units"]
    if units == "°F":
        return nominal - 30.0, nominal + 30.0
    if units == "%":
        return 0.0, 100.0
    if units == "%rh":
        return 10.0, 90.0
    if units == "Hz":
        return 59.0, 61.0
    if units == "V":
        return 430.0, 520.0
    if units in ("psi", "gpm", "rpm", "A", "kW", "in/WC", "tons", "lb/s"):
        return 0.0, max(nominal * 2.5, 1.0)
    return nominal - abs(nominal), nominal + abs(nominal) + 1.0


def _digits(spec: dict) -> int:
    units = spec["units"]
    if units == "in/WC":
        return 3
    if units == "Hz" or spec["value_kind"] == "counter":
        return 2
    if units in ("V", "rpm"):
        return 0
    if not units and spec["value_kind"] == "analog":
        return 2
    return 1


def _wander(spec: dict) -> float:
    units = spec["units"]
    if spec["value_kind"] != "analog":
        return 0.0
    return {
        "°F": 0.8,
        "psi": 0.8,
        "gpm": 22.0,
        "%": 4.0,
        "%rh": 2.0,
        "rpm": 70.0,
        "A": 1.2,
        "kW": 4.0,
        "V": 2.0,
        "Hz": 0.04,
        "in/WC": 0.004,
        "tons": 1.2,
        "lb/ft³": 0.15,
        "BTU/lb": 0.02,
        "lb/s": 0.6,
    }.get(units, 0.05)


def _deadband(spec: dict, nominal: float, deadband_pct: float) -> float:
    if spec["value_kind"] == "counter":
        return 0.01
    floors = {
        "°F": 0.15,
        "psi": 0.05,
        "gpm": 1.0,
        "%": 0.3,
        "%rh": 0.3,
        "rpm": 5.0,
        "A": 0.1,
        "kW": 0.2,
        "V": 0.5,
        "Hz": 0.01,
        "in/WC": 0.001,
        "tons": 0.1,
    }
    floor = floors.get(spec["units"], 0.01)
    return max(floor, abs(nominal) * deadband_pct / 100.0)


def clamp_write(name: str, units: str, value: float) -> float:
    if name == "ServerGlySupTempSP":
        return min(90.0, max(75.0, value))
    if units == "°F":
        return min(100.0, max(40.0, value))
    if units in ("%", "%rh"):
        return min(100.0, max(0.0, value))
    if units == "psi":
        return min(100.0, max(0.0, value))
    if units == "in/WC":
        return min(1.0, max(0.0, value))
    if units == "gpm":
        return max(0.0, value)
    return value


class PointState:
    def __init__(self, spec: dict, deadband_pct: float) -> None:
        self.spec = spec
        self.cell = spec["cell"]
        self.name = spec["name"]
        self.kind = spec["value_kind"]
        self.units = spec["units"]
        self.units_code = spec["units_code"]
        self.category = spec["category"]
        self.access = spec["access"]
        self.scan_s = float(spec["scan_s"])
        self.digits = _digits(spec)
        self.phase = _phase(f"{self.cell}/{self.name}")
        self.tau = 18.0 if spec["scan"] == "Slow" else 8.0
        self.wander_amp = _wander(spec)
        self.wander_period = 28.0 + (self.phase / math.tau) * 40.0
        self.forced = False
        self.pulse_until: float | None = None
        self.last_published = None
        self.due_at = 0.0

        if self.kind in ("alarm", "command"):
            self.value = False
        elif self.kind in ("status_bool", "setpoint_bool"):
            self.value = normal_status(spec) if self.kind == "status_bool" else False
        elif self.kind in ("status_enum", "packed"):
            self.value = 0 if self.kind == "packed" else _enum_default(self.name)
        else:
            number = nominal_number(spec)
            self.value = number
            self.lo, self.hi = _band(spec, number)
            self.deadband = _deadband(spec, number, deadband_pct)
            if self.kind == "analog":
                self.target = number
        if self.kind not in ("analog", "setpoint", "counter"):
            self.target = None
            self.deadband = 0.0
            self.lo, self.hi = 0.0, 0.0
        elif self.kind in ("setpoint", "counter"):
            self.target = float(self.value)
            self.lo, self.hi = _band(spec, float(self.value))
            self.deadband = _deadband(spec, float(self.value), deadband_pct)

    def set_target(self, target: float) -> None:
        if self.kind == "analog" and not self.forced:
            self.target = min(self.hi, max(self.lo, target))

    def step(self, dt: float, sim_t: float) -> None:
        if self.kind == "counter":
            self.value = float(self.value) + dt / 3600.0
            return
        if self.kind == "command" and self.pulse_until is not None and sim_t >= self.pulse_until:
            self.value = False
            self.pulse_until = None
            return
        if self.kind != "analog":
            return
        wander = self.wander_amp * math.sin(math.tau * sim_t / self.wander_period + self.phase)
        wander += 0.35 * self.wander_amp * math.sin(math.tau * sim_t / (self.wander_period * 0.45) + self.phase * 1.7)
        goal = min(self.hi, max(self.lo, self.target + wander))
        self.value += (goal - float(self.value)) * min(1.0, dt / self.tau)

    def publish_value(self):
        if isinstance(self.value, float):
            return round(self.value, self.digits)
        return self.value

    def changed(self) -> bool:
        current = self.publish_value()
        if self.last_published is None:
            return True
        if isinstance(current, float):
            return abs(current - float(self.last_published)) >= self.deadband
        return current != self.last_published

    def mark_published(self) -> None:
        self.last_published = self.publish_value()
