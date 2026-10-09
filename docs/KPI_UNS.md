# KPI test namespace

One hall of inputs plus the campus totals from Div 25 Schedule 1 and the PUE, CUE, and WUE graphics. The full hall register list stays in `Data_Wing_UNS.md` and is not published by this catalog.

Hall topic: `DataCenter/Site/<Wing>/<Hall>/<Cell>/<Point>`

Campus topic: `DataCenter/Site/Campus/<Cell>/<Point>`

Calculated points are produced in the simulator from the live inputs. Energy cost uses a flat $0.072/kWh. On-site generation is treated as the green source. Tenant apportionment is a placeholder 72% of IT energy until the owner standard is confirmed.

### CDU01 (Coolant Distribution Unit)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `ServerGlySupTemp` | Server glycol supply temperature | °F | R | Process | Sim | Analog 5 s |
| `ServerGlyRetTemp` | Server glycol return temperature | °F | R | Process | Sim | Analog 5 s |
| `ServerGlySupFlow` | Server glycol supply flow | gpm | R | Process | Sim | Analog 5 s |
| `LowestCHWHeaderDPLead` | Lowest header differential pressure | psi | R | Process | Sim | Analog 5 s |
| `TotSecCoolingLoadLead` | Secondary cooling load | kW | R | Process | Sim | Analog 5 s |
| `Level1CommonAlm` | CDU common alarm |  | R | Alarm | Discrete | Status 1 s |
| `ServerGlySupTempSP` | Server glycol supply temperature setpoint | °F | R/W | Setpoint | Holding | Analog 5 s |
| `CHWHeaderDPSPLead` | Header differential pressure setpoint | psi | R/W | Setpoint | Holding | Analog 5 s |
| `PriGlyValvePosFb` | Primary glycol valve position | % | R | Process | Sim | Analog 5 s |
| `Pump1VFDRunSts` | Pump 1 running |  | R | Status | Discrete | Status 1 s |
| `Pump2VFDRunSts` | Pump 2 running |  | R | Status | Discrete | Status 1 s |
| `Pump3VFDRunSts` | Pump 3 running |  | R | Status | Discrete | Status 1 s |
| `Pump1SpdCmd` | Pump 1 speed | % | R | Process | Sim | Analog 5 s |
| `Pump2SpdCmd` | Pump 2 speed | % | R | Process | Sim | Analog 5 s |
| `Pump3SpdCmd` | Pump 3 speed | % | R | Process | Sim | Analog 5 s |

### ChillerMCP (Chiller plant)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `MasterCHWSupTemp` | Master chilled water supply temperature | °F | R | Process | Sim | Analog 5 s |
| `MasterCHWRetTemp` | Master chilled water return temperature | °F | R | Process | Sim | Analog 5 s |
| `MasterGlyFlowSensor` | Master glycol flow | gpm | R | Process | Sim | Analog 5 s |
| `GlySupWaterTempSP` | Glycol supply water temperature setpoint | °F | R/W | Setpoint | Holding | Analog 5 s |

### Chiller01 (One chiller)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `ChillerGlyOutletTemp` | Glycol outlet temperature | °F | R | Process | Sim | Analog 5 s |
| `ActivePowerTot` | Chiller active power | kW | R | Process | Sim | Analog 5 s |
| `CondFan1VFDSpdCmd` | Condenser fan 1 speed | % | R | Process | Sim | Analog 5 s |
| `CondFan2VFDSpdCmd` | Condenser fan 2 speed | % | R | Process | Sim | Analog 5 s |
| `CondFan3VFDSpdCmd` | Condenser fan 3 speed | % | R | Process | Sim | Analog 5 s |
| `CondFan4VFDSpdCmd` | Condenser fan 4 speed | % | R | Process | Sim | Analog 5 s |
| `CondFan5VFDSpdCmd` | Condenser fan 5 speed | % | R | Process | Sim | Analog 5 s |
| `CondFan6VFDSpdCmd` | Condenser fan 6 speed | % | R | Process | Sim | Analog 5 s |
| `CondFan7VFDSpdCmd` | Condenser fan 7 speed | % | R | Process | Sim | Analog 5 s |
| `CondFan8VFDSpdCmd` | Condenser fan 8 speed | % | R | Process | Sim | Analog 5 s |
| `CondFan9VFDSpdCmd` | Condenser fan 9 speed | % | R | Process | Sim | Analog 5 s |
| `CondFan10VFDSpdCmd` | Condenser fan 10 speed | % | R | Process | Sim | Analog 5 s |
| `CondFan11VFDSpdCmd` | Condenser fan 11 speed | % | R | Process | Sim | Analog 5 s |
| `CondFan12VFDSpdCmd` | Condenser fan 12 speed | % | R | Process | Sim | Analog 5 s |

### AireBlockMCP (Air side)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `ColdAisleAvgTemp` | Cold aisle average, the space environmental KPI | °F | R | Process | Sim | Analog 5 s |
| `CCUSupTempAvg` | CCU supply air temperature average | °F | R | Process | Sim | Analog 5 s |
| `DPAAvg` | Hot aisle differential pressure average | in/WC | R | Process | Sim | Analog 5 s |
| `CCUTotKW` | CCU electrical total | kW | R | Process | Sim | Analog 5 s |
| `CCUSupAirTempSP` | CCU supply air temperature setpoint | °F | R/W | Setpoint | Holding | Analog 5 s |

### MiniAireBlock01 (Mini CCU)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `RoomTemp` | Room temperature | °F | R | Process | Sim | Analog 5 s |
| `RoomHum` | Room humidity | %rh | R | Process | Sim | Analog 5 s |
| `DischargeAirTemp` | Discharge air temperature | °F | R | Process | Sim | Analog 5 s |
| `RoomTempSP` | Room temperature setpoint | °F | R/W | Setpoint | Holding | Analog 5 s |

### HallPower (Hall electrical)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `TotalKW` | Hall electrical consumption | kW | R | Process | Sim | Analog 5 s |
| `ITKW` | IT electrical load, the PUE denominator | kW | R | Process | Sim | Analog 5 s |
| `PowerFactor` | Hall power factor | pf | R | Process | Sim | Analog 5 s |
| `VoltageLL` | Average line-to-line voltage | V | R | Process | Sim | Analog 5 s |

### UPS01 (One UPS)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `LoadPct` | UPS load | % | R | Process | Sim | Analog 5 s |
| `BatteryPct` | Battery state of charge | % | R | Process | Sim | Analog 5 s |
| `OnBattery` | UPS is on battery |  | R | Status | Discrete | Status 1 s |

### TurboCell01 (One TurboCell)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `RealPowerKW` | Unit real power | kW | R | Process | Sim | Analog 5 s |
| `RunSts` | Unit running |  | R | Status | Discrete | Status 1 s |
| `PowerSP` | Real power setpoint | kW | R/W | Setpoint | Holding | Analog 5 s |
| `Alarm` | Unit alarm |  | R | Alarm | Discrete | Status 1 s |

### Lineup01 (One lineup)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `TotalKW` | Lineup real power | kW | R | Process | Sim | Analog 5 s |
| `OnlineCount` | Units online in the lineup | count | R | Process | Sim | Analog 5 s |

### FirePanel (Summary)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `Alarm` | Panel alarm |  | R | Alarm | Discrete | Status 1 s |
| `Trouble` | Panel trouble |  | R | Alarm | Discrete | Status 1 s |
| `Supervisory` | Panel supervisory |  | R | Alarm | Discrete | Status 1 s |

### Campus/ElecPlant (Utility meter)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `DemandKW` | Building demand at the utility meter | kW | R | KPI | Calculated | Analog 5 s |
| `MonthEnergyKWh` | Building energy consumption this month | kWh | R | KPI | Calculated | Slow 30 s |
| `MonthCost` | Building energy cost this month | $ | R | KPI | Calculated | Slow 30 s |
| `YTDEnergyKWh` | Building year-to-date energy consumption | kWh | R | KPI | Calculated | Slow 30 s |
| `YTDCost` | Building year-to-date energy cost | $ | R | KPI | Calculated | Slow 30 s |
| `PeakDemandKW` | Year-to-date peak demand | kW | R | KPI | Calculated | Slow 30 s |

### Campus/GasPlant (Site gas)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `SupplyPressure` | Gas supply pressure | psi | R | KPI | Calculated | Analog 5 s |
| `FlowSCFM` | Gas flow | scfm | R | KPI | Calculated | Analog 5 s |

### Campus/Water (Site water)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `WaterGPM` | Site water use, the WUE input | gpm | R | KPI | Calculated | Analog 5 s |
| `SupplyPressure` | Site water pressure | psi | R | KPI | Calculated | Analog 5 s |

### Campus/Gen (On-site generation)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `SiteProducedKW` | Site produced power | kW | R | KPI | Calculated | Analog 5 s |
| `SiteProducedKWh` | Site produced energy | kWh | R | KPI | Calculated | Slow 30 s |
| `GreenEnergyKWh` | Green energy consumption, equal to on-site generation in this test | kWh | R | KPI | Calculated | Slow 30 s |

### Campus/KPI (Schedule 1 and performance)

| Point | Description | Units | Access | Category | Source | Scan |
| --- | --- | --- | --- | --- | --- | --- |
| `PUE` | Power usage effectiveness, facility electrical divided by IT | ratio | R | KPI | Calculated | Analog 5 s |
| `CUE` | Carbon usage effectiveness | kg/kWh | R | KPI | Calculated | Analog 5 s |
| `WUE` | Water usage effectiveness | L/kWh | R | KPI | Calculated | Analog 5 s |
| `CO2e` | CO2 equivalent from utility energy this month | kg | R | KPI | Calculated | Slow 30 s |
| `CO2Saved` | CO2 avoided by on-site generation this month | kg | R | KPI | Calculated | Slow 30 s |
| `EquipUnavailable` | Equipment not available for service | count | R | KPI | Calculated | Status 1 s |
| `TenantMonthKWh` | Tenant billable energy this month, 72% of IT until apportionment is confirmed | kWh | R | KPI | Calculated | Slow 30 s |
| `AlarmResponseMin` | Current month alarm response time | min | R | KPI | Calculated | Slow 30 s |
