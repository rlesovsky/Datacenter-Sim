"""One data hall: point instances plus the couplings that tie them together."""

from __future__ import annotations

import math

from sim.models import PointState, clamp_write


def _ripple(t: float, phase: float, amount: float) -> float:
    slow = math.sin(t / 22.0 + phase)
    fast = math.sin(t / 9.0 + phase * 1.8)
    return amount * (0.75 * slow + 0.25 * fast)


class Hall:
    def __init__(self, wing: int, hall: int, catalog: list[dict], deadband_pct: float) -> None:
        self.wing = wing
        self.hall = hall
        self.points = {
            (spec["cell"], spec["name"]): PointState(spec, deadband_pct)
            for spec in catalog
        }
        self._phase = (wing * 11 + hall) * 0.35

    def get(self, cell: str, name: str, default=None):
        point = self.points.get((cell, name))
        if point is None:
            return default
        return point.value

    def point(self, cell: str, name: str) -> PointState | None:
        return self.points.get((cell, name))

    def apply_set(self, cell: str, name: str, value, lock: bool = False) -> None:
        point = self.points.get((cell, name))
        if point is None:
            return
        if point.kind in ("analog", "setpoint", "counter"):
            number = float(value)
            if point.kind == "setpoint":
                number = clamp_write(name, point.units, number)
            point.value = number
            point.target = number
            point.forced = lock or point.kind != "analog"
            return
        if point.kind in ("status_enum", "packed"):
            point.value = int(value)
            return
        point.value = bool(value)
        if lock:
            point.forced = True

    def couple(self, sim_t: float) -> None:
        t = sim_t + self._phase * 40.0
        self._couple_cdu(t)
        self._couple_chillers(t)
        self._couple_aire(t)

    def _set(self, cell: str, name: str, target: float) -> None:
        point = self.points.get((cell, name))
        if point is not None:
            point.set_target(target)

    def _cdu_pump_on(self, t: float, index: int) -> bool:
        point = self.point("CDU01", f"Pump{index}VFDRunSts")
        if point is not None and point.forced:
            return bool(point.value)
        if bool(self.get("CDU01", "MasterShutdown", False)):
            return False
        # Two pumps run. The standby pump moves about once a minute.
        standby = 3 - (int(t // 45) % 3)
        return index != standby

    def _couple_cdu(self, t: float) -> None:
        supply_sp = float(self.get("CDU01", "ServerGlySupTempSP", 80.0))
        running = []
        for index in (1, 2, 3):
            on = self._cdu_pump_on(t, index)
            if on:
                running.append(index)
            for name in (f"Pump{index}VFDRunSts", f"ModbusPump{index}Sts"):
                point = self.point("CDU01", name)
                if point is not None and not point.forced:
                    point.value = on
        pumps = len(running)
        flow = 400.0 * pumps
        flow *= 1.0 + 0.06 * math.sin(t / 28.0)
        load_kw = 480.0 + 140.0 * math.sin(t / 180.0) + _ripple(t, 0.4, 35.0)
        if flow > 50.0:
            delta_t = load_kw * 6.824 / flow
        else:
            delta_t = 0.0
        dp_sp = self.get("CDU01", "CHWHeaderDPSPLead")
        if dp_sp is None:
            header_dp = 3.0 + 6.0 * pumps + _ripple(t, 1.2, 0.8)
        else:
            header_dp = float(dp_sp) + _ripple(t, 1.2, 0.35)
        split = 0.06 * math.sin(t / 16.0)
        self._set("CDU01", "ServerGlySupTemp", supply_sp)
        self._set("CDU01", "ServerGlyRetTemp", supply_sp + delta_t)
        self._set("CDU01", "PriGlySupTemp", supply_sp - 1.5 + _ripple(t, 0.6, 0.4))
        self._set("CDU01", "PriGlyRetTemp", supply_sp + delta_t + 1.0)
        self._set("CDU01", "ServerGlySupFlow", flow)
        self._set("CDU01", "PriGlyFlowMeter", flow * 0.55)
        self._set("CDU01", "HeaderAFlowMeter", flow * (0.5 + split))
        self._set("CDU01", "HeaderBFlowMeter", flow * (0.5 - split))
        self._set("CDU01", "HeaderADP", header_dp + _ripple(t, 0.3, 0.45))
        self._set("CDU01", "HeaderBDP", header_dp * 0.96 + _ripple(t, 1.7, 0.45))
        self._set("CDU01", "LowestCHWHeaderDPLead", min(header_dp, header_dp * 0.96))
        self._set("CDU01", "TotSecCoolingLoadLead", load_kw)
        self._set("CDU01", "TotPriCoolingLoadLead", load_kw * 1.08 + _ripple(t, 2.0, 20.0))
        self._set("CDU01", "PriGlyValvePosFb", 58.0 + _ripple(t, 0.2, 7.0))
        self._set("CDU01", "PriGlyRetValveCmd", 61.0 + _ripple(t, 0.9, 6.0))
        self._set("CDU01", "HXStrainerDP", 3.1 + _ripple(t, 1.4, 0.35))
        self._set("CDU01", "ServerGlyRetPress", 18.0 + _ripple(t, 0.5, 1.4))
        for index in (1, 2, 3):
            if index in running:
                speed = 70.0 + _ripple(t, index * 0.8, 6.0)
                pump_dp = 16.0 + _ripple(t, index, 1.5)
            else:
                speed = 0.0
                pump_dp = 0.4
            self._set("CDU01", f"Pump{index}SpdCmd", speed)
            self._set("CDU01", f"Pump{index}DP", pump_dp)

    def _couple_chillers(self, t: float) -> None:
        outside = 80.0 + 4.0 * math.sin(t / 150.0)
        self._set("ChillerMCP", "MasterOATempSensor", outside)
        self._set("ChillerMCP", "ChillersAvgAmbientTemp", outside + _ripple(t, 0.4, 0.4))
        self._set("ChillerMCP", "MasterOAHumSensor", 48.0 + _ripple(t, 1.1, 3.0))
        self._set("ChillerMCP", "BypassValveFb", 42.0 + _ripple(t, 0.7, 8.0))
        self._set("ChillerMCP", "BypassValveCmd", 45.0 + _ripple(t, 1.3, 7.0))
        outlets = []
        for index in range(1, 11):
            cell = f"Chiller{index:02d}"
            enabled = bool(self.get("ChillerMCP", f"CH{index:02d}Enable", True))
            failed = bool(self.get("ChillerMCP", f"CH{index:02d}FailedAlm", False))
            running = enabled and not failed
            phase = index * 0.55
            supply_sp = float(self.get("ChillerMCP", "GlySupWaterTempSP", 56.0) or 56.0)
            outlet = (supply_sp if running else outside) + (_ripple(t, phase, 0.8) if running else 0.0)
            inlet = outlet + ((10.0 + _ripple(t, phase + 0.4, 0.6)) if running else 0.5)
            outlets.append(outlet if running else None)
            capacity = 520.0 + _ripple(t, phase, 40.0) if running else 0.0
            self._set(cell, "ChillerGlyOutletTemp", outlet)
            self._set(cell, "ChillerGlyInletTemp", inlet)
            self._set(cell, "GlyFlow", 240.0 + _ripple(t, phase, 22.0) if running else 0.0)
            self._set(cell, "ActivePowerTot", 165.0 + _ripple(t, phase + 1.0, 14.0) if running else 2.0)
            self._set(cell, "TotCoolingCapacity", capacity)
            self._set(cell, "FluidCoolerCoolingCapacity", capacity * 0.58 + _ripple(t, phase, 12.0) if running else 0.0)
            self._set(cell, "MechanicalCoolingCapacity", capacity * 0.42 + _ripple(t, phase + 0.5, 10.0) if running else 0.0)
            self._set(cell, "MPUE", 1.13 + _ripple(t, phase, 0.04) if running else 0.0)
            self._set(cell, "FluidCoolerApproach", 6.2 + _ripple(t, phase, 0.6) if running else 0.0)
            self._set(cell, "GlyRetValveFb", 55.0 + _ripple(t, phase, 8.0))
            self._set(cell, "GlyRetValveCmd", 57.0 + _ripple(t, phase + 0.2, 7.0))
            self._set(cell, "GlyBypassValveFb", 12.0 + _ripple(t, phase + 1.0, 6.0) if running else 0.0)
            self._set(cell, "GlyBypassValveCmd", 14.0 + _ripple(t, phase + 1.2, 5.0) if running else 0.0)
            for comp, prefix in ((1, "HTComp1"), (2, "HTComp2"), (3, "LTComp3"), (4, "LTComp4")):
                self._set(cell, f"{prefix}ActualSpd", 4900.0 + comp * 80.0 + _ripple(t, phase + comp, 140.0) if running else 0.0)
                self._set(cell, f"{prefix}ActualPower", 36.0 + _ripple(t, phase + comp, 5.0) if running else 0.0)
                self._set(cell, f"{prefix}Demand", 55.0 + _ripple(t, phase + comp * 0.6, 8.0) if running else 0.0)
            for fan in range(1, 19):
                self._set(cell, f"CondFan{fan}VFDSpdCmd", 50.0 + _ripple(t, phase + fan * 0.35, 14.0) if running else 0.0)
        live = [value for value in outlets if value is not None]
        if live:
            supply = sum(live) / len(live)
            self._set("ChillerMCP", "MasterCHWSupTemp", supply)
            self._set("ChillerMCP", "RunChillersAvgCHWSupTemp", supply)
            self._set("ChillerMCP", "MasterCHWRetTemp", supply + 10.0 + _ripple(t, 0.2, 0.5))
            self._set("ChillerMCP", "RunChillersAvgCHWRetTemp", supply + 10.0)
            self._set("ChillerMCP", "MasterGlyFlowSensor", 240.0 * len(live) + _ripple(t, 0.8, 40.0))

    def _couple_aire(self, t: float) -> None:
        supply_sp = float(self.get("AireBlockMCP", "CCUSupAirTempSP", 68.0))
        cold = 72.5 + 1.1 * math.sin(t / 45.0)
        self._set("AireBlockMCP", "CCUSupTempAvg", supply_sp + _ripple(t, 0.3, 0.45))
        self._set("AireBlockMCP", "ColdAisleAvgTemp", cold)
        total_kw = 0.0
        for index in range(1, 13):
            supply = supply_sp + _ripple(t, index * 0.4, 0.55)
            fan = 980.0 + _ripple(t, index * 0.5, 90.0)
            self._set("AireBlockMCP", f"CCU{index:02d}SupAirTemp", supply)
            self._set("AireBlockMCP", f"CCU{index:02d}RetAirTemp", supply + 18.0 + _ripple(t, index, 0.8))
            self._set("AireBlockMCP", f"CCU{index:02d}FanSpd", fan)
            self._set("AireBlockMCP", f"CCU{index:02d}FanSpdFb", 62.0 + _ripple(t, index * 0.3, 6.0))
            self._set("AireBlockMCP", f"CCU{index:02d}CWValvePos", 48.0 + _ripple(t, index * 0.2, 8.0))
            self._set("AireBlockMCP", f"CCU{index:02d}CHWValveFlow", 36.0 + _ripple(t, index, 5.0))
            total_kw += 8.0 + max(fan, 0.0) / 280.0
        self._set("AireBlockMCP", "CCUTotKW", total_kw)
        self._set("AireBlockMCP", "CCUTotTons", total_kw / 3.5)
        zones = ("1A", "2A", "1B", "2B")
        for offset, zone in enumerate(zones):
            self._set("AireBlockMCP", f"Zone{zone}ColdAisleTemp", cold + _ripple(t, offset, 0.7))
            self._set("AireBlockMCP", f"Zone{zone}ColdAisleHum", 45.0 + _ripple(t, offset + 0.5, 2.5))
            self._set("AireBlockMCP", f"Zone{zone}HotAisleDP", 0.05 + _ripple(t, offset + 1.2, 0.006))
        self._set("AireBlockMCP", "DPAAvg", 0.055 + _ripple(t, 0.2, 0.004))
        self._set("AireBlockMCP", "DPBAvg", 0.052 + _ripple(t, 1.1, 0.004))
        room_sp = float(self.get("MiniAireBlock01", "RoomTempSP", 72.0))
        discharge = supply_sp + _ripple(t, 0.8, 0.7)
        self._set("MiniAireBlock01", "DischargeAirTemp", discharge)
        self._set("MiniAireBlock01", "RetAirTemp", discharge + 14.0 + _ripple(t, 0.4, 0.6))
        self._set("MiniAireBlock01", "RoomTemp", room_sp + _ripple(t, 0.15, 0.55))
        self._set("MiniAireBlock01", "ControlTemp", room_sp + _ripple(t, 0.9, 0.4))
        self._set("MiniAireBlock01", "RoomHum", 46.0 + _ripple(t, 1.3, 2.2))
        self._set("MiniAireBlock01", "ValveFb", 46.0 + _ripple(t, 0.6, 7.0))
        self._set("MiniAireBlock01", "ControlValveCmdSignalOut", 48.0 + _ripple(t, 1.0, 6.0))
        self._set("MiniAireBlock01", "ControlValveFlowRate", 34.0 + _ripple(t, 0.5, 4.0))
        self._set("MiniAireBlock01", "CHWSTemp", 58.0 + _ripple(t, 0.3, 0.6))
        self._set("MiniAireBlock01", "CHWRTemp", 68.0 + _ripple(t, 0.7, 0.7))
        self._set("MiniAireBlock01", "AirDP", 0.28 + _ripple(t, 1.4, 0.04))
        for index in (1, 2):
            self._set("MiniAireBlock01", f"Fan{index}ActualSpd", 1100.0 + _ripple(t, index * 0.8, 80.0))
            self._set("MiniAireBlock01", f"Fan{index}KW", 3.2 + _ripple(t, index, 0.35))
