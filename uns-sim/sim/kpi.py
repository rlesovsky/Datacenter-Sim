"""Campus KPIs calculated from one hall of live inputs."""

from __future__ import annotations

import math

from sim.hall import Hall
from sim.models import PointState

# Flat energy price for the test. Not a tariff.
RATE_USD_PER_KWH = 0.072
# Planning carbon factor for grid power.
GRID_KG_PER_KWH = 0.386
# Placeholder until tenant apportionment is confirmed.
TENANT_SHARE = 0.72
# Seed the month and year so the page is not a string of zeros.
SEED_MONTH_H = 9 * 24
SEED_YEAR_MONTHS = 9
PUMP_KW = 35.0


def _ripple(t: float, phase: float, amount: float) -> float:
    return amount * math.sin(t / 40.0 + phase)


def _drive(hall: Hall, cell: str, name: str, value: float) -> None:
    point = hall.point(cell, name)
    if point is None:
        return
    if point.kind == "analog":
        point.set_target(value)
    point.value = value


class Campus:
    def __init__(self, catalog: list[dict], deadband_pct: float) -> None:
        self.points = {
            (spec["cell"], spec["name"]): PointState(spec, deadband_pct) for spec in catalog
        }
        self.last_t: float | None = None
        self.month_kwh = 0.0
        self.ytd_kwh = 0.0
        self.produced_kwh = 0.0
        self.co2_kg = 0.0
        self.co2_saved_kg = 0.0
        self.tenant_kwh = 0.0
        self.peak_kw = 0.0
        self.seeded = False

    def point(self, cell: str, name: str) -> PointState | None:
        return self.points.get((cell, name))

    def _set(self, cell: str, name: str, target: float) -> None:
        point = self.point(cell, name)
        if point is not None and point.kind == "analog":
            point.set_target(target)

    def _put(self, cell: str, name: str, value: float) -> None:
        point = self.point(cell, name)
        if point is not None:
            point.value = value


def couple_kpis(halls: dict[tuple[int, int], Hall], campus: Campus, sim_t: float) -> None:
    if not halls or not campus.points:
        return
    hall = next(iter(halls.values()))
    it_kw = 1400.0 + _ripple(sim_t, 0.4, 45.0)
    chiller_kw = float(hall.get("Chiller01", "ActivePowerTot", 180.0) or 0.0)
    air_kw = float(hall.get("AireBlockMCP", "CCUTotKW", 90.0) or 0.0)
    facility_kw = it_kw + chiller_kw + air_kw + PUMP_KW
    power_sp = hall.get("TurboCell01", "PowerSP", 300.0)
    try:
        power_base = float(power_sp)
    except (TypeError, ValueError):
        power_base = 300.0
    power_base = min(334.0, max(40.0, power_base))
    produced_kw = power_base + _ripple(sim_t, 1.1, 12.0)
    grid_kw = max(0.0, facility_kw - produced_kw)
    water_gpm = 5.0 + _ripple(sim_t, 0.6, 0.15)

    _drive(hall, "HallPower", "ITKW", it_kw)
    _drive(hall, "HallPower", "TotalKW", facility_kw)
    _drive(hall, "TurboCell01", "RealPowerKW", produced_kw)
    _drive(hall, "Lineup01", "TotalKW", produced_kw)
    _drive(hall, "UPS01", "LoadPct", 100.0 * it_kw / facility_kw)
    _drive(hall, "UPS01", "BatteryPct", 96.0 + _ripple(sim_t, 1.4, 0.3))
    _drive(hall, "UPS01", "OnBattery", False)
    _drive(hall, "HallPower", "PowerFactor", 0.972 + _ripple(sim_t, 0.3, 0.006))
    _drive(hall, "HallPower", "VoltageLL", 480.0 + _ripple(sim_t, 0.8, 2.5))
    _drive(hall, "TurboCell01", "RunSts", produced_kw > 50.0)
    _drive(hall, "TurboCell01", "Alarm", False)
    _drive(hall, "Lineup01", "OnlineCount", 1.0)
    _drive(hall, "FirePanel", "Trouble", False)
    campus._put("GasPlant", "SupplyPressure", 58.0 + _ripple(sim_t, 0.2, 1.2))
    campus._put("GasPlant", "FlowSCFM", 420.0 + _ripple(sim_t, 0.9, 18.0))
    campus._put("Water", "WaterGPM", water_gpm)
    campus._put("Water", "SupplyPressure", 46.0 + _ripple(sim_t, 1.6, 0.8))

    dt_h = 0.0
    if campus.last_t is not None:
        dt_h = max(0.0, sim_t - campus.last_t) / 3600.0
    campus.last_t = sim_t
    if not campus.seeded:
        campus.month_kwh = grid_kw * SEED_MONTH_H
        campus.ytd_kwh = campus.month_kwh * SEED_YEAR_MONTHS
        campus.produced_kwh = produced_kw * SEED_MONTH_H
        campus.co2_kg = campus.month_kwh * GRID_KG_PER_KWH
        campus.co2_saved_kg = campus.produced_kwh * GRID_KG_PER_KWH
        campus.tenant_kwh = it_kw * SEED_MONTH_H * TENANT_SHARE
        campus.peak_kw = grid_kw
        campus.seeded = True
    else:
        campus.month_kwh += grid_kw * dt_h
        campus.ytd_kwh += grid_kw * dt_h
        campus.produced_kwh += produced_kw * dt_h
        campus.co2_kg += grid_kw * GRID_KG_PER_KWH * dt_h
        campus.co2_saved_kg += produced_kw * GRID_KG_PER_KWH * dt_h
        campus.tenant_kwh += it_kw * TENANT_SHARE * dt_h
        campus.peak_kw = max(campus.peak_kw, grid_kw)

    pue = facility_kw / it_kw if it_kw else 0.0
    cue = grid_kw * GRID_KG_PER_KWH / it_kw if it_kw else 0.0
    # gpm to L/h, divided by kW, is L/kWh.
    wue = water_gpm * 3.785 * 60.0 / it_kw if it_kw else 0.0
    response = 18.0 + 6.0 * math.sin(sim_t / 90.0)
    unavailable = 0
    if hall.get("FirePanel", "Alarm"):
        unavailable += 1
    if hall.get("CDU01", "Level1CommonAlm"):
        unavailable += 1
    if hall.get("TurboCell01", "Alarm"):
        unavailable += 1

    campus._put("ElecPlant", "DemandKW", grid_kw)
    campus._put("ElecPlant", "MonthEnergyKWh", campus.month_kwh)
    campus._put("ElecPlant", "MonthCost", campus.month_kwh * RATE_USD_PER_KWH)
    campus._put("ElecPlant", "YTDEnergyKWh", campus.ytd_kwh)
    campus._put("ElecPlant", "YTDCost", campus.ytd_kwh * RATE_USD_PER_KWH)
    campus._put("ElecPlant", "PeakDemandKW", campus.peak_kw)
    campus._put("Gen", "SiteProducedKW", produced_kw)
    campus._put("Gen", "SiteProducedKWh", campus.produced_kwh)
    campus._put("Gen", "GreenEnergyKWh", campus.produced_kwh)
    campus._put("KPI", "PUE", pue)
    campus._put("KPI", "CUE", cue)
    campus._put("KPI", "WUE", wue)
    campus._put("KPI", "CO2e", campus.co2_kg)
    campus._put("KPI", "CO2Saved", campus.co2_saved_kg)
    campus._put("KPI", "EquipUnavailable", unavailable)
    campus._put("KPI", "TenantMonthKWh", campus.tenant_kwh)
    campus._put("KPI", "AlarmResponseMin", response)
