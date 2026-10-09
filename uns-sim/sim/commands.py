"""Apply R/W topic writes: setpoints stick, commands pulse."""

from __future__ import annotations

import json

from sim.hall import Hall
from sim.models import clamp_write


def parse_write(payload: bytes):
    text = payload.decode("utf-8", errors="replace").strip()
    if not text:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = text
    if isinstance(data, dict):
        if "value" not in data:
            return None
        data = data["value"]
    if isinstance(data, str):
        lowered = data.strip().lower()
        if lowered in ("true", "false"):
            return lowered == "true"
        return float(data)
    return data


def apply_write(hall: Hall, cell: str, name: str, value, sim_t: float) -> str:
    point = hall.point(cell, name)
    if point is None:
        return f"ignored unknown {cell}/{name}"
    if "W" not in point.access:
        return f"ignored read-only {cell}/{name}"

    if point.kind == "command":
        active = bool(value)
        point.value = active
        point.pulse_until = sim_t + 2.0 if active else None
        _command_effects(hall, cell, name, active)
    elif point.kind == "setpoint":
        point.value = clamp_write(name, point.units, float(value))
        point.target = float(point.value)
    elif point.kind == "setpoint_bool":
        point.value = bool(value)
    elif point.kind in ("status_bool", "alarm"):
        point.value = bool(value)
    elif point.kind in ("status_enum", "packed"):
        point.value = int(value)
    else:
        point.value = clamp_write(name, point.units, float(value))
        point.target = float(point.value)
        point.forced = True
    point.due_at = 0.0
    return f"wrote {cell}/{name} = {point.publish_value()}"


def _command_effects(hall: Hall, cell: str, name: str, active: bool) -> None:
    if not active or cell != "CDU01":
        if active and name.startswith("CH") and name.endswith("FaultReset"):
            number = name[2:4]
            hall.apply_set("ChillerMCP", f"CH{number}FailedAlm", False)
        return
    if name == "EmergencyStopCmd":
        hall.apply_set("CDU01", "MasterShutdown", True)
        for index in (1, 2, 3):
            hall.apply_set("CDU01", f"Pump{index}VFDRunSts", False)
            hall.apply_set("CDU01", f"ModbusPump{index}Sts", False)
    elif name == "LocalStartCmd":
        hall.apply_set("CDU01", "MasterShutdown", False)
        for index, running in ((1, True), (2, True), (3, False)):
            hall.apply_set("CDU01", f"Pump{index}VFDRunSts", running)
            hall.apply_set("CDU01", f"ModbusPump{index}Sts", running)
