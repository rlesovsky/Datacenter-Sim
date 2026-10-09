# Data Wing UNS (Unified Namespace)

Draft 2026-10-07. One namespace per data hall, all 11 halls rolling up into one UNS per data wing on the wing broker. The hierarchy stops at the cell (one controller); every data point is a leaf topic under its cell.

## Hierarchy (ISA-95)

| Level | ISA-95 | Example | What it is |
| --- | --- | --- | --- |
| 1 | Enterprise | `Enterprise` | Owner (placeholder) |
| 2 | Site | `Site` | Campus (placeholder) |
| 3 | Area | `Wing01` to `Wing04` | Data wing. Each wing is its own UNS on its own broker. |
| 4 | Line | `Hall01` to `Hall11` | Data hall namespace |
| 5 | Cell | `CDU01`, `Chiller03` | One controller. Deepest hierarchy level. |
| Leaf | Point | `ServerGlySupTemp` | One data point |

Topic form:

```
Enterprise/Site/<Wing>/<Hall>/<Cell>/<Point>
Enterprise/Site/Wing01/Hall01/CDU01/ServerGlySupTemp

```

- **Hall namespace:** `Enterprise/Site/WingNN/HallNN/#`
- **Wing UNS:** `Enterprise/Site/WingNN/#` (all 11 halls)

## Cells per data hall

| Cell | Controller | Protocol | Polled by | Points |
| --- | --- | --- | --- | --- |
| `ChillerMCP` | Chiller Master Control Panel | Modbus TCP/IP | Primary + Secondary | 86 |
| `Chiller01 to Chiller10` | Individual Chiller | Modbus TCP/IP | Primary only | 149 x 10 = 1490 |
| `CDU01` | Coolant Distribution Unit | Modbus TCP/IP | Primary + Secondary | 94 |
| `AireBlockMCP` | Data Hall AireBlock MCP | Modbus TCP/IP | Primary + Secondary | 225 |
| `MiniAireBlock01` | Mini AireBlock (CCU) | BACnet/IP | Primary only | 105 |
| **Total per hall** |  |  |  | **2,000** |
| **Total per wing (11 halls)** |  |  |  | **22,000** |

## Naming rules

- PascalCase, no spaces or special characters.
- No units in the name. Units, quality and timestamp ride in the payload.
- Abbreviations: Temp, DP, SP, Cmd, Fb, Sup, Ret, Gly, CHW, HX, Comp, Cond, Evap, Econ, EXV, LBV, OA, Alm, Sts, Avg, Tot.
- SI duplicate registers are not published.
- Packed status words are decoded into named bits where the spec names the bits.
- Sub-equipment reported by a controller stays under that controller with a prefix instead of adding a level: `AireBlockMCP/CCU01SupAirTemp`, `ChillerMCP/CH03Mode`.
- Chiller MCP registers for chillers 11 to 13 are not published (10 chillers per hall).

## Payload (plain MQTT)

```json
{
  "value": 80.1,
  "units": "degF",
  "quality": "Good",
  "ts": 1791390000000
}

```

## Sparkplug B mapping

If the collectors publish with Ignition MQTT Transmission, the topic follows the Sparkplug form and the UNS path is carried in the IDs and metric names. MQTT Engine on the backend rebuilds the same tree.

| Sparkplug field | Value | Example |
| --- | --- | --- |
| Group ID | Wing | `Wing01` |
| Edge Node ID | Collector | `FD01-TCA` |
| Device ID | Hall + Cell | `Hall01_CDU01` |
| Metric | Point | `ServerGlySupTemp` |
| Topic |  | `spBv1.0/Wing01/DDATA/FD01-TCA/Hall01_CDU01` |

## Point lists by cell

Topic prefix for every row: `Enterprise/Site/<Wing>/<Hall>/<Cell>/`. A ⚑ in the Confirm column means the address, bit position or name was inferred and needs confirmation from ALC.

### ChillerMCP (Chiller Master Control Panel, Modbus TCP/IP)

| Point | Description | Units | Access | Category | Source | Scan | Confirm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `CH01FaultReset` | Chiller 01 Fault Reset |  | R/W | Command | Coil 1 | Status 1 s |  |
| `CH02FaultReset` | Chiller 02 Fault Reset |  | R/W | Command | Coil 2 | Status 1 s |  |
| `CH03FaultReset` | Chiller 03 Fault Reset |  | R/W | Command | Coil 3 | Status 1 s |  |
| `CH04FaultReset` | Chiller 04 Fault Reset |  | R/W | Command | Coil 4 | Status 1 s |  |
| `CH05FaultReset` | Chiller 05 Fault Reset |  | R/W | Command | Coil 5 | Status 1 s |  |
| `CH06FaultReset` | Chiller 06 Fault Reset |  | R/W | Command | Coil 6 | Status 1 s |  |
| `CH07FaultReset` | Chiller 07 Fault Reset |  | R/W | Command | Coil 7 | Status 1 s |  |
| `CH08FaultReset` | Chiller 08 Fault Reset |  | R/W | Command | Coil 8 | Status 1 s |  |
| `CH09FaultReset` | Chiller 09 Fault Reset |  | R/W | Command | Coil 9 | Status 1 s |  |
| `CH10FaultReset` | Chiller 10 Fault Reset |  | R/W | Command | Coil 10 | Status 1 s |  |
| `ResetRemoteMasterHeartbeatFailAlm` | Reset Remote Master Heartbeat Fail Alarm |  | R/W | Command | Coil 14 | Status 1 s |  |
| `MasterCHWSupTemp` | Master Chilled Water Supply Temperature | °F | R | Process | Input Register 30001 | Analog 5 s |  |
| `MasterCHWRetTemp` | Master Chilled Water Return Temperature | °F | R | Process | Input Register 30003 | Analog 5 s |  |
| `ExpansionTankPress` | Expansion Tank Pressure | psi | R | Process | Input Register 30005 | Analog 5 s |  |
| `DPSensorA` | Differential Pressure Sensor A | psi | R | Process | Input Register 30007 | Analog 5 s |  |
| `DPSensorB` | Differential Pressure Sensor B | psi | R | Process | Input Register 30009 | Analog 5 s |  |
| `MasterGlyFlowSensor` | Master Glycol Flow Sensor | gpm | R | Process | Input Register 30011 | Analog 5 s |  |
| `MasterOATempSensor` | Master Outside Air Temperature Sensor | °F | R | Process | Input Register 30013 | Slow 30 s |  |
| `TotizedFlowFromAllChillers` | Totalized Flow from All Chillers | gpm | R | Process | Input Register 30015 | Analog 5 s |  |
| `RunChillersAvgCHWSupTemp` | Running Chillers Avg Chilled Water Supply Temp | °F | R | Process | Input Register 30017 | Analog 5 s |  |
| `RunChillersAvgCHWRetTemp` | Running Chillers Avg Chilled Water Return Temp | °F | R | Process | Input Register 30019 | Analog 5 s |  |
| `ChillersAvgAmbientTemp` | Chillers Average Ambient Temperature | °F | R | Process | Input Register 30021 | Slow 30 s |  |
| `MinFlowSPForBypassValveControl` | Minimum Flow Setpoint for Bypass Valve Control | gpm | R | Process | Input Register 30023 | Slow 30 s |  |
| `MasterOAHumSensor` | Master Outside Air Humidity Sensor | %rh | R | Process | Input Register 30025 | Slow 30 s |  |
| `BypassValveFb` | Bypass Valve Feedback | % | R | Process | Input Register 30027 | Analog 5 s |  |
| `BypassValveCmd` | Bypass Valve Command | % | R | Process | Input Register 30029 | Analog 5 s |  |
| `PumpMinSpd` | Pump Minimum Speed | % | R | Process | Input Register 30031 | Slow 30 s |  |
| `MinRunChillerSP` | Minimum Running Chiller Setpoint |  | R | Process | Input Register 30033 | Slow 30 s |  |
| `CH01Priority` | Chiller 01 Priority |  | R | Process | Input Register 30035 | Slow 30 s | ⚑ |
| `CH02Priority` | Chiller 02 Priority |  | R | Process | Input Register 30036 | Slow 30 s | ⚑ |
| `CH03Priority` | Chiller 03 Priority |  | R | Process | Input Register 30037 | Slow 30 s | ⚑ |
| `CH04Priority` | Chiller 04 Priority |  | R | Process | Input Register 30038 | Slow 30 s | ⚑ |
| `CH05Priority` | Chiller 05 Priority |  | R | Process | Input Register 30039 | Slow 30 s | ⚑ |
| `CH06Priority` | Chiller 06 Priority |  | R | Process | Input Register 30040 | Slow 30 s | ⚑ |
| `CH07Priority` | Chiller 07 Priority |  | R | Process | Input Register 30041 | Slow 30 s | ⚑ |
| `CH08Priority` | Chiller 08 Priority |  | R | Process | Input Register 30042 | Slow 30 s | ⚑ |
| `CH09Priority` | Chiller 09 Priority |  | R | Process | Input Register 30043 | Slow 30 s | ⚑ |
| `CH10Priority` | Chiller 10 Priority |  | R | Process | Input Register 30044 | Slow 30 s | ⚑ |
| `CH01Mode` | Chiller 01 Mode |  | R | Status | Input Register 30048 | Status 1 s | ⚑ |
| `CH02Mode` | Chiller 02 Mode |  | R | Status | Input Register 30049 | Status 1 s | ⚑ |
| `CH03Mode` | Chiller 03 Mode |  | R | Status | Input Register 30050 | Status 1 s | ⚑ |
| `CH04Mode` | Chiller 04 Mode |  | R | Status | Input Register 30051 | Status 1 s | ⚑ |
| `CH05Mode` | Chiller 05 Mode |  | R | Status | Input Register 30052 | Status 1 s | ⚑ |
| `CH06Mode` | Chiller 06 Mode |  | R | Status | Input Register 30053 | Status 1 s | ⚑ |
| `CH07Mode` | Chiller 07 Mode |  | R | Status | Input Register 30054 | Status 1 s | ⚑ |
| `CH08Mode` | Chiller 08 Mode |  | R | Status | Input Register 30055 | Status 1 s | ⚑ |
| `CH09Mode` | Chiller 09 Mode |  | R | Status | Input Register 30056 | Status 1 s | ⚑ |
| `CH10Mode` | Chiller 10 Mode |  | R | Status | Input Register 30057 | Status 1 s | ⚑ |
| `MasterPumpSpdCmd` | Master Pump Speed Command | % | R | Process | Input Register 30061 | Analog 5 s |  |
| `CH01Enable` | Chiller 01 Enable |  | R | Status | Input Register (packed bit) 30062 (PackedStatus_1) | Status 1 s | ⚑ |
| `CH02Enable` | Chiller 02 Enable |  | R | Status | Input Register (packed bit) 30062 (PackedStatus_1) | Status 1 s | ⚑ |
| `CH03Enable` | Chiller 03 Enable |  | R | Status | Input Register (packed bit) 30062 (PackedStatus_1) | Status 1 s | ⚑ |
| `CH04Enable` | Chiller 04 Enable |  | R | Status | Input Register (packed bit) 30062 (PackedStatus_1) | Status 1 s | ⚑ |
| `CH05Enable` | Chiller 05 Enable |  | R | Status | Input Register (packed bit) 30062 (PackedStatus_1) | Status 1 s | ⚑ |
| `CH06Enable` | Chiller 06 Enable |  | R | Status | Input Register (packed bit) 30062 (PackedStatus_1) | Status 1 s | ⚑ |
| `CH07Enable` | Chiller 07 Enable |  | R | Status | Input Register (packed bit) 30062 (PackedStatus_1) | Status 1 s | ⚑ |
| `CH08Enable` | Chiller 08 Enable |  | R | Status | Input Register (packed bit) 30062 (PackedStatus_1) | Status 1 s | ⚑ |
| `CH09Enable` | Chiller 09 Enable |  | R | Status | Input Register (packed bit) 30062 (PackedStatus_1) | Status 1 s | ⚑ |
| `CH10Enable` | Chiller 10 Enable |  | R | Status | Input Register (packed bit) 30062 (PackedStatus_1) | Status 1 s | ⚑ |
| `CH01FailedAlm` | Chiller 01 Failed Alarm |  | R | Alarm | Input Register (packed bit) 30062 (PackedStatus_1) | Status 1 s | ⚑ |
| `CH02FailedAlm` | Chiller 02 Failed Alarm |  | R | Alarm | Input Register (packed bit) 30062 (PackedStatus_1) | Status 1 s | ⚑ |
| `CH03FailedAlm` | Chiller 03 Failed Alarm |  | R | Alarm | Input Register (packed bit) 30062 (PackedStatus_1) | Status 1 s | ⚑ |
| `CH04FailedAlm` | Chiller 04 Failed Alarm |  | R | Alarm | Input Register (packed bit) 30063 (PackedStatus_2) | Status 1 s | ⚑ |
| `CH05FailedAlm` | Chiller 05 Failed Alarm |  | R | Alarm | Input Register (packed bit) 30063 (PackedStatus_2) | Status 1 s | ⚑ |
| `CH06FailedAlm` | Chiller 06 Failed Alarm |  | R | Alarm | Input Register (packed bit) 30063 (PackedStatus_2) | Status 1 s | ⚑ |
| `CH07FailedAlm` | Chiller 07 Failed Alarm |  | R | Alarm | Input Register (packed bit) 30063 (PackedStatus_2) | Status 1 s | ⚑ |
| `CH08FailedAlm` | Chiller 08 Failed Alarm |  | R | Alarm | Input Register (packed bit) 30063 (PackedStatus_2) | Status 1 s | ⚑ |
| `CH09FailedAlm` | Chiller 09 Failed Alarm |  | R | Alarm | Input Register (packed bit) 30063 (PackedStatus_2) | Status 1 s | ⚑ |
| `CH10FailedAlm` | Chiller 10 Failed Alarm |  | R | Alarm | Input Register (packed bit) 30063 (PackedStatus_2) | Status 1 s | ⚑ |
| `CH01CommSts` | Chiller 01 Comm Status |  | R | Status | Input Register (packed bit) 30063 (PackedStatus_2) | Status 1 s | ⚑ |
| `CH02CommSts` | Chiller 02 Comm Status |  | R | Status | Input Register (packed bit) 30063 (PackedStatus_2) | Status 1 s | ⚑ |
| `CH03CommSts` | Chiller 03 Comm Status |  | R | Status | Input Register (packed bit) 30063 (PackedStatus_2) | Status 1 s | ⚑ |
| `CH04CommSts` | Chiller 04 Comm Status |  | R | Status | Input Register (packed bit) 30063 (PackedStatus_2) | Status 1 s | ⚑ |
| `CH05CommSts` | Chiller 05 Comm Status |  | R | Status | Input Register (packed bit) 30063 (PackedStatus_2) | Status 1 s | ⚑ |
| `CH06CommSts` | Chiller 06 Comm Status |  | R | Status | Input Register (packed bit) 30063 (PackedStatus_2) | Status 1 s | ⚑ |
| `CH07CommSts` | Chiller 07 Comm Status |  | R | Status | Input Register (packed bit) 30064 (PackedStatus_3) | Status 1 s | ⚑ |
| `CH08CommSts` | Chiller 08 Comm Status |  | R | Status | Input Register (packed bit) 30064 (PackedStatus_3) | Status 1 s | ⚑ |
| `CH09CommSts` | Chiller 09 Comm Status |  | R | Status | Input Register (packed bit) 30064 (PackedStatus_3) | Status 1 s | ⚑ |
| `CH10CommSts` | Chiller 10 Comm Status |  | R | Status | Input Register (packed bit) 30064 (PackedStatus_3) | Status 1 s | ⚑ |
| `EffectiveSystemMode` | Effective System Mode |  | R | Status | Input Register (packed bit) 30064 (PackedStatus_3) | Status 1 s | ⚑ |
| `ChillerPriorityError` | Chiller Priority Error |  | R | Alarm | Input Register (packed bit) 30064 (PackedStatus_3) | Status 1 s | ⚑ |
| `PriorityUpdate` | Priority Update |  | R | Status | Input Register (packed bit) 30064 (PackedStatus_3) | Status 1 s | ⚑ |
| `RemoteMCPHeartbeatFailAlm` | Remote MCP Heartbeat Fail Alarm |  | R | Alarm | Input Register (packed bit) 30064 (PackedStatus_3) | Status 1 s | ⚑ |
| `RotateChillerPriority` | Rotate Chiller Priority |  | R | Status | Input Register (packed bit) 30064 (PackedStatus_3) | Status 1 s | ⚑ |
| `DPSP` | Differential Pressure Setpoint | psi | R/W | Setpoint | Holding Register 40001 | Slow 30 s |  |
| `GlySupWaterTempSP` | Glycol Supply Water Temperature Setpoint | °F | R/W | Setpoint | Holding Register 40003 | Slow 30 s |  |

### Chiller01 to Chiller10 (Individual Chiller, Modbus TCP/IP)

One template, repeated for Chiller01 to Chiller10.

| Point | Description | Units | Access | Category | Source | Scan | Confirm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `GlyRetValveFb` | Glycol Return Valve Feedback | % | R | Process | Input Register 30001 | Analog 5 s |  |
| `GlyBypassValveFb` | Glycol Bypass Valve Feedback | % | R | Process | Input Register 30003 | Analog 5 s |  |
| `CondFan1VFDSpdCmd` | Condenser Fan 1 VFD Speed Command | % | R | Process | Input Register 30005 | Analog 5 s | ⚑ |
| `CondFan2VFDSpdCmd` | Condenser Fan 2 VFD Speed Command | % | R | Process | Input Register 30007 | Analog 5 s | ⚑ |
| `CondFan3VFDSpdCmd` | Condenser Fan 3 VFD Speed Command | % | R | Process | Input Register 30009 | Analog 5 s | ⚑ |
| `CondFan4VFDSpdCmd` | Condenser Fan 4 VFD Speed Command | % | R | Process | Input Register 30011 | Analog 5 s | ⚑ |
| `CondFan5VFDSpdCmd` | Condenser Fan 5 VFD Speed Command | % | R | Process | Input Register 30013 | Analog 5 s | ⚑ |
| `CondFan6VFDSpdCmd` | Condenser Fan 6 VFD Speed Command | % | R | Process | Input Register 30015 | Analog 5 s | ⚑ |
| `CondFan7VFDSpdCmd` | Condenser Fan 7 VFD Speed Command | % | R | Process | Input Register 30017 | Analog 5 s | ⚑ |
| `CondFan8VFDSpdCmd` | Condenser Fan 8 VFD Speed Command | % | R | Process | Input Register 30019 | Analog 5 s | ⚑ |
| `CondFan9VFDSpdCmd` | Condenser Fan 9 VFD Speed Command | % | R | Process | Input Register 30021 | Analog 5 s | ⚑ |
| `CondFan10VFDSpdCmd` | Condenser Fan 10 VFD Speed Command | % | R | Process | Input Register 30023 | Analog 5 s | ⚑ |
| `CondFan11VFDSpdCmd` | Condenser Fan 11 VFD Speed Command | % | R | Process | Input Register 30025 | Analog 5 s | ⚑ |
| `CondFan12VFDSpdCmd` | Condenser Fan 12 VFD Speed Command | % | R | Process | Input Register 30027 | Analog 5 s | ⚑ |
| `CondFan13VFDSpdCmd` | Condenser Fan 13 VFD Speed Command | % | R | Process | Input Register 30029 | Analog 5 s | ⚑ |
| `CondFan14VFDSpdCmd` | Condenser Fan 14 VFD Speed Command | % | R | Process | Input Register 30031 | Analog 5 s | ⚑ |
| `CondFan15VFDSpdCmd` | Condenser Fan 15 VFD Speed Command | % | R | Process | Input Register 30033 | Analog 5 s | ⚑ |
| `CondFan16VFDSpdCmd` | Condenser Fan 16 VFD Speed Command | % | R | Process | Input Register 30035 | Analog 5 s | ⚑ |
| `CondFan17VFDSpdCmd` | Condenser Fan 17 VFD Speed Command | % | R | Process | Input Register 30037 | Analog 5 s | ⚑ |
| `CondFan18VFDSpdCmd` | Condenser Fan 18 VFD Speed Command | % | R | Process | Input Register 30039 | Analog 5 s | ⚑ |
| `GlyPump1VFDSpdCmd` | Glycol Pump 1 VFD Speed Command | % | R | Process | Input Register 30041 | Analog 5 s |  |
| `GlyPump2VFDSpdCmd` | Glycol Pump 2 VFD Speed Command | % | R | Process | Input Register 30043 | Analog 5 s |  |
| `LTCircuitMainEXV1Cmd` | LT Circuit Main Expansion Valve 1 Command | % | R | Process | Input Register 30045 | Analog 5 s |  |
| `LTCircuitLBV2Cmd` | LT Circuit Load Balancing Valve 2 Command | % | R | Process | Input Register 30047 | Analog 5 s |  |
| `LTComp3EconEXVCmd` | LT Compressor 3 Economizer Expansion Valve Command | % | R | Process | Input Register 30049 | Analog 5 s |  |
| `LTComp4EconEXVCmd` | LT Compressor 4 Economizer Expansion Valve Command | % | R | Process | Input Register 30051 | Analog 5 s |  |
| `HTComp1EconEXVCmd` | HT Compressor 1 Economizer Expansion Valve Command | % | R | Process | Input Register 30053 | Analog 5 s |  |
| `HTComp2EconEXVCmd` | HT Compressor 2 Economizer Expansion Valve Command | % | R | Process | Input Register 30055 | Analog 5 s |  |
| `GlyRetValveCmd` | Glycol Return Valve Command | % | R | Process | Input Register 30057 | Analog 5 s |  |
| `HTCircuitMainEXV2Cmd` | HT Circuit Main Expansion Valve 2 Command | % | R | Process | Input Register 30059 | Analog 5 s |  |
| `HTCircuitLBV1Cmd` | HT Circuit Load Balancing Valve 1 Command | % | R | Process | Input Register 30061 | Analog 5 s |  |
| `GlyBypassValveCmd` | Glycol Bypass Valve Command | % | R | Process | Input Register 30063 | Analog 5 s |  |
| `HTComp1Demand` | HT Compressor 1 Demand | % | R | Process | Input Register 30065 | Analog 5 s |  |
| `HTComp2Demand` | HT Compressor 2 Demand | % | R | Process | Input Register 30067 | Analog 5 s |  |
| `LTComp3Demand` | LT Compressor 3 Demand | % | R | Process | Input Register 30069 | Analog 5 s |  |
| `LTComp4Demand` | LT Compressor 4 Demand | % | R | Process | Input Register 30071 | Analog 5 s |  |
| `HTComp1ActualSpd` | HT Compressor 1 Actual Speed | rpm | R | Process | Input Register 30073 | Analog 5 s |  |
| `HTComp2ActualSpd` | HT Compressor 2 Actual Speed | rpm | R | Process | Input Register 30075 | Analog 5 s |  |
| `LTComp3ActualSpd` | LT Compressor 3 Actual Speed | rpm | R | Process | Input Register 30077 | Analog 5 s |  |
| `LTComp4ActualSpd` | LT Compressor 4 Actual Speed | rpm | R | Process | Input Register 30079 | Analog 5 s |  |
| `HTComp1DesiredSpd` | HT Compressor 1 Desired Speed | rpm | R | Process | Input Register 30081 | Analog 5 s | ⚑ |
| `HTComp2DesiredSpd` | HT Compressor 2 Desired Speed | rpm | R | Process | Input Register 30083 | Analog 5 s | ⚑ |
| `LTComp3DesiredSpd` | LT Compressor 3 Desired Speed | rpm | R | Process | Input Register 30085 | Analog 5 s | ⚑ |
| `LTComp4DesiredSpd` | LT Compressor 4 Desired Speed | rpm | R | Process | Input Register 30087 | Analog 5 s | ⚑ |
| `HTComp1MotorAmps` | HT Compressor 1 Motor Amps | A | R | Process | Input Register 30089 | Analog 5 s | ⚑ |
| `HTComp2MotorAmps` | HT Compressor 2 Motor Amps | A | R | Process | Input Register 30091 | Analog 5 s | ⚑ |
| `LTComp3MotorAmps` | LT Compressor 3 Motor Amps | A | R | Process | Input Register 30093 | Analog 5 s | ⚑ |
| `LTComp4MotorAmps` | LT Compressor 4 Motor Amps | A | R | Process | Input Register 30095 | Analog 5 s | ⚑ |
| `HTComp1SuctionSuperheatTemp` | HT Compressor 1 Suction Superheat Temperature | °F | R | Process | Input Register 30097 | Analog 5 s | ⚑ |
| `HTComp2SuctionSuperheatTemp` | HT Compressor 2 Suction Superheat Temperature | °F | R | Process | Input Register 30099 | Analog 5 s | ⚑ |
| `LTComp3SuctionSuperheatTemp` | LT Compressor 3 Suction Superheat Temperature | °F | R | Process | Input Register 30101 | Analog 5 s | ⚑ |
| `LTComp4SuctionSuperheatTemp` | LT Compressor 4 Suction Superheat Temperature | °F | R | Process | Input Register 30103 | Analog 5 s | ⚑ |
| `HTComp1IGVPos` | HT Compressor 1 IGV Position | % | R | Process | Input Register 30105 | Analog 5 s | ⚑ |
| `HTComp2IGVPos` | HT Compressor 2 IGV Position | % | R | Process | Input Register 30107 | Analog 5 s | ⚑ |
| `LTComp3IGVPos` | LT Compressor 3 IGV Position | % | R | Process | Input Register 30109 | Analog 5 s | ⚑ |
| `LTComp4IGVPos` | LT Compressor 4 IGV Position | % | R | Process | Input Register 30111 | Analog 5 s | ⚑ |
| `HTComp1ActualPower` | HT Compressor 1 Actual Power | kW | R | Process | Input Register 30113 | Analog 5 s | ⚑ |
| `HTComp2ActualPower` | HT Compressor 2 Actual Power | kW | R | Process | Input Register 30115 | Analog 5 s | ⚑ |
| `LTComp3ActualPower` | LT Compressor 3 Actual Power | kW | R | Process | Input Register 30117 | Analog 5 s | ⚑ |
| `LTComp4ActualPower` | LT Compressor 4 Actual Power | kW | R | Process | Input Register 30119 | Analog 5 s | ⚑ |
| `HTComp1PressRatio` | HT Compressor 1 Pressure Ratio |  | R | Process | Input Register 30121 | Analog 5 s | ⚑ |
| `HTComp2PressRatio` | HT Compressor 2 Pressure Ratio |  | R | Process | Input Register 30123 | Analog 5 s | ⚑ |
| `LTComp3PressRatio` | LT Compressor 3 Pressure Ratio |  | R | Process | Input Register 30125 | Analog 5 s | ⚑ |
| `LTComp4PressRatio` | LT Compressor 4 Pressure Ratio |  | R | Process | Input Register 30127 | Analog 5 s | ⚑ |
| `GlyPump1Amps` | Glycol Pump 1 Amps | A | R | Process | Input Register 30129 | Analog 5 s | ⚑ |
| `GlyPump2Amps` | Glycol Pump 2 Amps | A | R | Process | Input Register 30131 | Analog 5 s | ⚑ |
| `GlyPump1Spd` | Glycol Pump 1 Speed | rpm | R | Process | Input Register 30133 | Analog 5 s | ⚑ |
| `GlyPump2Spd` | Glycol Pump 2 Speed | rpm | R | Process | Input Register 30135 | Analog 5 s | ⚑ |
| `GlyPump1ActualPower` | Glycol Pump 1 Actual Power | kW | R | Process | Input Register 30137 | Analog 5 s | ⚑ |
| `GlyPump2ActualPower` | Glycol Pump 2 Actual Power | kW | R | Process | Input Register 30139 | Analog 5 s | ⚑ |
| `MPUE` | MPUE |  | R | Process | Input Register 30141 | Analog 5 s |  |
| `Source1AvgVoltLL` | Source 1 Average Voltage L-L | V | R | Process | Input Register 30143 | Analog 5 s | ⚑ |
| `Source2AvgVoltLL` | Source 2 Average Voltage L-L | V | R | Process | Input Register 30145 | Analog 5 s | ⚑ |
| `ChillerRuntimeHours` | Chiller Runtime Hours | h | R | Process | Input Register 30147 | Slow 30 s |  |
| `ActivePowerTot` | Active Power Total | kW | R | Process | Input Register 30149 | Analog 5 s |  |
| `TotCoolingCapacity` | Total Cooling Capacity | kW | R | Process | Input Register 30151 | Analog 5 s | ⚑ |
| `FluidCoolerCoolingCapacity` | Fluid Cooler Cooling Capacity | kW | R | Process | Input Register 30153 | Analog 5 s | ⚑ |
| `MechanicalCoolingCapacity` | Mechanical Cooling Capacity | kW | R | Process | Input Register 30155 | Analog 5 s | ⚑ |
| `OperatingMode` | Operating Mode |  | R | Status | Input Register 30157 | Status 1 s |  |
| `ChillerMode` | Chiller Mode |  | R | Status | Input Register 30158 | Status 1 s |  |
| `LTCircuitLeadComp` | LT Circuit Lead Compressor |  | R | Process | Input Register 30159 | Slow 30 s |  |
| `ChillerOATempSource` | Chiller Outside Air Temperature Source |  | R | Process | Input Register 30160 | Slow 30 s |  |
| `MasterGlySPPriority` | Master Glycol Setpoint Priority |  | R | Process | Input Register 30161 | Slow 30 s |  |
| `HTCircuitLeadComp` | HT Circuit Lead Compressor |  | R | Process | Input Register 30162 | Slow 30 s |  |
| `GlyFlow` | Glycol Flow | gpm | R | Process | Input Register 30163 | Analog 5 s |  |
| `ChillerGlyInletTemp` | Chiller Glycol Inlet Temperature | °F | R | Process | Input Register 30165 | Analog 5 s | ⚑ |
| `ChillerGlyOutletTemp` | Chiller Glycol Outlet Temperature | °F | R | Process | Input Register 30167 | Analog 5 s | ⚑ |
| `GlySupTempSP` | Glycol Supply Temperature Setpoint | °F | R | Process | Input Register 30169 | Slow 30 s |  |
| `HT_Comp12_PT01` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 1 of 14 | psi / °F | R | Process | Input Register 30171 | Analog 5 s | ⚑ |
| `HT_Comp12_PT02` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 2 of 14 | psi / °F | R | Process | Input Register 30173 | Analog 5 s | ⚑ |
| `HT_Comp12_PT03` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 3 of 14 | psi / °F | R | Process | Input Register 30175 | Analog 5 s | ⚑ |
| `HT_Comp12_PT04` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 4 of 14 | psi / °F | R | Process | Input Register 30177 | Analog 5 s | ⚑ |
| `HT_Comp12_PT05` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 5 of 14 | psi / °F | R | Process | Input Register 30179 | Analog 5 s | ⚑ |
| `HT_Comp12_PT06` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 6 of 14 | psi / °F | R | Process | Input Register 30181 | Analog 5 s | ⚑ |
| `HT_Comp12_PT07` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 7 of 14 | psi / °F | R | Process | Input Register 30183 | Analog 5 s | ⚑ |
| `HT_Comp12_PT08` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 8 of 14 | psi / °F | R | Process | Input Register 30185 | Analog 5 s | ⚑ |
| `HT_Comp12_PT09` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 9 of 14 | psi / °F | R | Process | Input Register 30187 | Analog 5 s | ⚑ |
| `HT_Comp12_PT10` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 10 of 14 | psi / °F | R | Process | Input Register 30189 | Analog 5 s | ⚑ |
| `HT_Comp12_PT11` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 11 of 14 | psi / °F | R | Process | Input Register 30191 | Analog 5 s | ⚑ |
| `HT_Comp12_PT12` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 12 of 14 | psi / °F | R | Process | Input Register 30193 | Analog 5 s | ⚑ |
| `HT_Comp12_PT13` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 13 of 14 | psi / °F | R | Process | Input Register 30195 | Analog 5 s | ⚑ |
| `HT_Comp12_PT14` | HT Compressor 1/2 Discharge/Suction Pressure or Temperature, value 14 of 14 | psi / °F | R | Process | Input Register 30197 | Analog 5 s | ⚑ |
| `HTCondRefrigerantOutletPress` | HT Condenser Refrigerant Outlet Pressure | psi | R | Process | Input Register 30199 | Analog 5 s | ⚑ |
| `HTCondRefrigerantOutletTemp` | HT Condenser Refrigerant Outlet Temperature | °F | R | Process | Input Register 30201 | Analog 5 s | ⚑ |
| `HTCondRefrigerantSaturatedTemp` | HT Condenser Refrigerant Saturated Temperature | °F | R | Process | Input Register 30203 | Analog 5 s | ⚑ |
| `HT_Evap_T01` | HT Evaporator Approach/Inlet Temperature, value 1 of 5 | °F | R | Process | Input Register 30205 | Analog 5 s | ⚑ |
| `HT_Evap_T02` | HT Evaporator Approach/Inlet Temperature, value 2 of 5 | °F | R | Process | Input Register 30207 | Analog 5 s | ⚑ |
| `HT_Evap_T03` | HT Evaporator Approach/Inlet Temperature, value 3 of 5 | °F | R | Process | Input Register 30209 | Analog 5 s | ⚑ |
| `HT_Evap_T04` | HT Evaporator Approach/Inlet Temperature, value 4 of 5 | °F | R | Process | Input Register 30211 | Analog 5 s | ⚑ |
| `HT_Evap_T05` | HT Evaporator Approach/Inlet Temperature, value 5 of 5 | °F | R | Process | Input Register 30213 | Analog 5 s | ⚑ |
| `LT_Comp34_PT01` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 1 of 14 | psi / °F | R | Process | Input Register 30217 | Analog 5 s | ⚑ |
| `LT_Comp34_PT02` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 2 of 14 | psi / °F | R | Process | Input Register 30219 | Analog 5 s | ⚑ |
| `LT_Comp34_PT03` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 3 of 14 | psi / °F | R | Process | Input Register 30221 | Analog 5 s | ⚑ |
| `LT_Comp34_PT04` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 4 of 14 | psi / °F | R | Process | Input Register 30223 | Analog 5 s | ⚑ |
| `LT_Comp34_PT05` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 5 of 14 | psi / °F | R | Process | Input Register 30225 | Analog 5 s | ⚑ |
| `LT_Comp34_PT06` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 6 of 14 | psi / °F | R | Process | Input Register 30227 | Analog 5 s | ⚑ |
| `LT_Comp34_PT07` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 7 of 14 | psi / °F | R | Process | Input Register 30229 | Analog 5 s | ⚑ |
| `LT_Comp34_PT08` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 8 of 14 | psi / °F | R | Process | Input Register 30231 | Analog 5 s | ⚑ |
| `LT_Comp34_PT09` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 9 of 14 | psi / °F | R | Process | Input Register 30233 | Analog 5 s | ⚑ |
| `LT_Comp34_PT10` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 10 of 14 | psi / °F | R | Process | Input Register 30235 | Analog 5 s | ⚑ |
| `LT_Comp34_PT11` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 11 of 14 | psi / °F | R | Process | Input Register 30237 | Analog 5 s | ⚑ |
| `LT_Comp34_PT12` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 12 of 14 | psi / °F | R | Process | Input Register 30239 | Analog 5 s | ⚑ |
| `LT_Comp34_PT13` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 13 of 14 | psi / °F | R | Process | Input Register 30241 | Analog 5 s | ⚑ |
| `LT_Comp34_PT14` | LT Compressor 3/4 Discharge/Suction Pressure or Temperature, value 14 of 14 | psi / °F | R | Process | Input Register 30243 | Analog 5 s | ⚑ |
| `LTCondRefrigerantOutletPress` | LT Condenser Refrigerant Outlet Pressure | psi | R | Process | Input Register 30245 | Analog 5 s | ⚑ |
| `LTCondRefrigerantOutletTemp` | LT Condenser Refrigerant Outlet Temperature | °F | R | Process | Input Register 30247 | Analog 5 s | ⚑ |
| `LTCondRefrigerantSaturatedTemp` | LT Condenser Refrigerant Saturated Temperature | °F | R | Process | Input Register 30249 | Analog 5 s | ⚑ |
| `LT_Evap_T01` | LT Evaporator Approach/Inlet Temperature, value 1 of 5 | °F | R | Process | Input Register 30251 | Analog 5 s | ⚑ |
| `LT_Evap_T02` | LT Evaporator Approach/Inlet Temperature, value 2 of 5 | °F | R | Process | Input Register 30253 | Analog 5 s | ⚑ |
| `LT_Evap_T03` | LT Evaporator Approach/Inlet Temperature, value 3 of 5 | °F | R | Process | Input Register 30255 | Analog 5 s | ⚑ |
| `LT_Evap_T04` | LT Evaporator Approach/Inlet Temperature, value 4 of 5 | °F | R | Process | Input Register 30257 | Analog 5 s | ⚑ |
| `LT_Evap_T05` | LT Evaporator Approach/Inlet Temperature, value 5 of 5 | °F | R | Process | Input Register 30259 | Analog 5 s | ⚑ |
| `PumpGlyInletPress` | Pump Glycol Inlet Pressure | psi | R | Process | Input Register 30261 | Analog 5 s | ⚑ |
| `PumpGlyOutletPress` | Pump Glycol Outlet Pressure | psi | R | Process | Input Register 30263 | Analog 5 s | ⚑ |
| `PowerPanelTemp` | Power Panel Temperature | °F | R | Process | Input Register 30265 | Slow 30 s |  |
| `OATempMechanicalCoolingEnableSP` | OA Temp Mechanical Cooling Enable Setpoint | °F | R | Process | Input Register 30267 | Slow 30 s | ⚑ |
| `OATempPartialFreeCoolingEnableSP` | OA Temp Partial Free Cooling Enable Setpoint | °F | R | Process | Input Register 30269 | Slow 30 s | ⚑ |
| `FluidCoolerApproach` | Fluid Cooler Approach | °F | R | Process | Input Register 30271 | Analog 5 s |  |
| `ChillerGlyOutletPress` | Chiller Glycol Outlet Pressure | psi | R | Process | Input Register 30273 | Analog 5 s |  |
| `ControlPanelTemp` | Control Panel Temperature | °F | R | Process | Input Register 30275 | Slow 30 s |  |
| `PackedSts1` | PackedStatus_1 (bits include: EEV Faults, HP Alarms (all 4 compressors), UPS Alarm, ATS Alarms, Pump Status) |  | R | Status | Input Register (packed word) 30277 | Fast 500 ms | ⚑ |
| `PackedSts2` | PackedStatus_2 (bits include: Redundant Power, Cabinet Coolers, Condenser Fan 1 to 13 Faults) |  | R | Status | Input Register (packed word) 30278 | Status 1 s | ⚑ |
| `PackedSts3` | PackedStatus_3 (bits include: Condenser Fan 14 to 18 Faults, Pump VFD Faults, Compressor Status / Fault / Interlock) |  | R | Status | Input Register (packed word) 30279 | Status 1 s | ⚑ |
| `PackedSts4` | PackedStatus_4 (bits include: Compressor Interlocks, Stage Valve Commands, Common Alarms L1 to L4) |  | R | Status | Input Register (packed word) 30280 | Status 1 s | ⚑ |
| `PackedSts5` | PackedStatus_5 (bits include: Master Comm Failures, Glycol Temp Alarms, Evaporator Temp Alarms, Economizer Alarms) |  | R | Status | Input Register (packed word) 30281 | Status 1 s | ⚑ |
| `PackedSts6` | PackedStatus_6 (bits include: Condenser Temp Alarms, Superheat Low Alarms, OA / Panel Temp Alarms, Water Heating / Flow Alarms) |  | R | Status | Input Register (packed word) 30282 | Status 1 s | ⚑ |
| `PackedSts7` | PackedStatus_7 (bits include: Pump VFD Faults, Compressor Fault Alarms, SMD Board Alarms, Valve Signal Alarms) |  | R | Status | Input Register (packed word) 30283 | Status 1 s | ⚑ |
| `PackedSts8` | PackedStatus_8 (bits include: Economizer Pressure Alarms, Condenser Pressure Alarms, Glycol Pressure Alarms, Compressor Alarms / Comm Loss) |  | R | Status | Input Register (packed word) 30284 | Status 1 s | ⚑ |
| `PackedSts9` | PackedStatus_9 (bits include: HT Compressor Alarms / Comm Loss, Chiller Status, Phase / Voltage Issues, Enable Command) |  | R | Status | Input Register (packed word) 30285 | Fast 500 ms | ⚑ |

### CDU01 (Coolant Distribution Unit, Modbus TCP/IP)

| Point | Description | Units | Access | Category | Source | Scan | Confirm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `LocalStartCmd` | CDU Local Start Command |  | R/W | Command | Coil 1 | Fast 500 ms |  |
| `EmergencyStopCmd` | CDU Emergency Stop Command |  | R/W | Command | Coil 2 | Fast 500 ms |  |
| `Pump1VFDRunSts` | CDU Pump 1 VFD Running Status |  | R | Status | Discrete Input 10001 | Fast 500 ms |  |
| `Pump2VFDRunSts` | CDU Pump 2 VFD Running Status |  | R | Status | Discrete Input 10002 | Fast 500 ms |  |
| `Pump3VFDRunSts` | CDU Pump 3 VFD Running Status |  | R | Status | Discrete Input 10003 | Fast 500 ms |  |
| `StsOutputCmd` | CDU Status Output Command |  | R | Status | Discrete Input 10004 | Status 1 s |  |
| `MasterShutdown` | CDU Master Shutdown |  | R | Alarm | Discrete Input 10005 | Fast 500 ms |  |
| `CommToPriCDULost` | CDU Comm to Primary CDU Lost |  | R | Alarm | Discrete Input 10006 | Status 1 s |  |
| `CommToSecCDULost` | CDU Comm to Secondary CDU Lost |  | R | Alarm | Discrete Input 10007 | Status 1 s |  |
| `Level1CommonAlm` | CDU Level 1 Common Alarm |  | R | Alarm | Discrete Input 10008 | Status 1 s |  |
| `Level2CommonAlm` | CDU Level 2 Common Alarm |  | R | Alarm | Discrete Input 10009 | Status 1 s |  |
| `Level3CommonAlm` | CDU Level 3 Common Alarm |  | R | Alarm | Discrete Input 10010 | Status 1 s |  |
| `Level4CommonAlm` | CDU Level 4 Common Alarm |  | R | Alarm | Discrete Input 10011 | Status 1 s |  |
| `ModbusPump1Sts` | CDU Modbus Pump 1 Status |  | R | Status | Discrete Input 10012 | Fast 500 ms |  |
| `ModbusPump2Sts` | CDU Modbus Pump 2 Status |  | R | Status | Discrete Input 10013 | Fast 500 ms |  |
| `ModbusPump3Sts` | CDU Modbus Pump 3 Status |  | R | Status | Discrete Input 10014 | Fast 500 ms |  |
| `PowerSource1ConnectedSts` | CDU Power Source 1 Connected Status |  | R | Status | Discrete Input 10015 | Fast 500 ms |  |
| `ManualReTransferSts` | CDU Manual Re-Transfer Status |  | R | Status | Discrete Input 10016 | Fast 500 ms |  |
| `Source1Sts` | CDU Source 1 Status |  | R | Status | Discrete Input 10017 | Fast 500 ms |  |
| `AutomaticModeSts` | CDU Automatic Mode Status |  | R | Status | Discrete Input 10018 | Status 1 s |  |
| `VoltSourceNotInSync` | CDU Voltage Source Not in Sync |  | R | Alarm | Discrete Input 10019 | Fast 500 ms |  |
| `PowerSource2ConnectedSts` | CDU Power Source 2 Connected Status |  | R | Status | Discrete Input 10020 | Fast 500 ms |  |
| `ManualAutoModeSts` | CDU Manual / Auto Mode Status |  | R | Status | Discrete Input 10021 | Status 1 s |  |
| `LocalRemoteModeSts` | CDU Local / Remote Mode Status |  | R | Status | Discrete Input 10022 | Status 1 s |  |
| `PhasesCrossedSts` | CDU Phases Crossed Status |  | R | Alarm | Discrete Input 10023 | Fast 500 ms |  |
| `Source2Sts` | CDU Source 2 Status |  | R | Status | Discrete Input 10024 | Fast 500 ms |  |
| `OperationModeSts` | CDU Operation Mode Status |  | R | Status | Discrete Input 10025 | Status 1 s |  |
| `TSUUnitCharged` | TSU Unit Charged |  | R | Status | Discrete Input 10026 | Status 1 s |  |
| `TSUUnitDischarged` | TSU Unit Discharged |  | R | Status | Discrete Input 10027 | Status 1 s |  |
| `TSUCompEnabled` | TSU Compressor Enabled |  | R | Status | Discrete Input 10028 | Status 1 s |  |
| `TSUHXOutletValveEnabled` | TSU Heat Exchanger Outlet Valve Enabled |  | R | Status | Discrete Input 10029 | Status 1 s |  |
| `TSUUnitAlm` | TSU Unit Alarm |  | R | Alarm | Discrete Input 10030 | Status 1 s |  |
| `TSUPumpEnabled` | TSU Pump Enabled |  | R | Status | Discrete Input 10031 | Status 1 s |  |
| `TSULowFlowAlm` | TSU Low Flow Alarm |  | R | Alarm | Discrete Input 10032 | Status 1 s |  |
| `TSUControlMode` | TSU Control Mode |  | R | Status | Discrete Input 10033 | Status 1 s |  |
| `HXStrainerDP` | CDU Heat Exchanger Strainer Differential Pressure | psi | R | Process | Input Register 30001 | Analog 5 s |  |
| `Pump1DP` | CDU Pump 1 Differential Pressure | psi | R | Process | Input Register 30003 | Analog 5 s | ⚑ |
| `Pump2DP` | CDU Pump 2 Differential Pressure | psi | R | Process | Input Register 30005 | Analog 5 s | ⚑ |
| `Pump3DP` | CDU Pump 3 Differential Pressure | psi | R | Process | Input Register 30007 | Analog 5 s | ⚑ |
| `HX1NetworkDP` | CDU HX1 Network Differential Pressure | psi | R | Process | Input Register 30009 | Analog 5 s |  |
| `PriGlySupPress` | CDU Primary Glycol Supply Pressure | psi | R | Process | Input Register 30011 | Analog 5 s | ⚑ |
| `SecGlySupPress` | CDU Secondary Glycol Supply Pressure | psi | R | Process | Input Register 30013 | Analog 5 s | ⚑ |
| `PriGlyFlowMeter` | CDU Primary Glycol Flow Meter | gpm | R | Process | Input Register 30015 | Analog 5 s |  |
| `ServerGlySupFlow` | CDU Server Glycol Supply Flow | gpm | R | Process | Input Register 30017 | Fast 500 ms |  |
| `PriGlyRetTemp` | CDU Primary Glycol Return Temperature | °F | R | Process | Input Register 30019 | Analog 5 s | ⚑ |
| `ServerGlyRetTemp` | CDU Server Glycol Return Temperature | °F | R | Process | Input Register 30021 | Analog 5 s | ⚑ |
| `ServerGlyRetPress` | CDU Server Glycol Return Pressure | psi | R | Process | Input Register 30023 | Analog 5 s |  |
| `PriGlyValvePosFb` | CDU Primary Glycol Valve Position Feedback | % | R | Process | Input Register 30025 | Analog 5 s |  |
| `HeaderADP` | CDU Header A Differential Pressure | psi | R | Process | Input Register 30027 | Fast 500 ms | ⚑ |
| `HeaderBDP` | CDU Header B Differential Pressure | psi | R | Process | Input Register 30029 | Fast 500 ms | ⚑ |
| `HeaderAFlowMeter` | CDU Header A Flow Meter | gpm | R | Process | Input Register 30031 | Analog 5 s | ⚑ |
| `HeaderBFlowMeter` | CDU Header B Flow Meter | gpm | R | Process | Input Register 30033 | Analog 5 s | ⚑ |
| `PriGlySupTemp` | CDU Primary Glycol Supply Temperature | °F | R | Process | Input Register 30035 | Analog 5 s | ⚑ |
| `ServerGlySupTemp` | CDU Server Glycol Supply Temperature | °F | R | Process | Input Register 30037 | Analog 5 s | ⚑ |
| `Pump1SpdCmd` | CDU Pump 1 Speed Command | % | R | Process | Input Register 30039 | Analog 5 s | ⚑ |
| `Pump2SpdCmd` | CDU Pump 2 Speed Command | % | R | Process | Input Register 30040 | Analog 5 s | ⚑ |
| `Pump3SpdCmd` | CDU Pump 3 Speed Command | % | R | Process | Input Register 30041 | Analog 5 s | ⚑ |
| `PriGlyRetValveCmd` | CDU Primary Glycol Return Valve Command | % | R | Process | Input Register 30042 | Analog 5 s |  |
| `PriCondensedWaterRetDensity` | CDU Primary Condensed Water Return Density | lb/ft³ | R | Process | Input Register 30043 | Slow 30 s | ⚑ |
| `PriCondensedWaterRetSpecificHeat` | CDU Primary Condensed Water Return Specific Heat | BTU/lb | R | Process | Input Register 30045 | Slow 30 s | ⚑ |
| `PriCondensedWaterRetFlowRate` | CDU Primary Condensed Water Return Flow Rate | lb/s | R | Process | Input Register 30047 | Slow 30 s | ⚑ |
| `SecCondensedWaterRetDensity` | CDU Secondary Condensed Water Return Density | lb/ft³ | R | Process | Input Register 30049 | Slow 30 s | ⚑ |
| `SecCondensedWaterRetSpecificHeat` | CDU Secondary Condensed Water Return Specific Heat | BTU/lb | R | Process | Input Register 30051 | Slow 30 s | ⚑ |
| `SecCondensedWaterRetFlowRate` | CDU Secondary Condensed Water Return Flow Rate | lb/s | R | Process | Input Register 30053 | Slow 30 s | ⚑ |
| `Source1LineToLineVoltAvg` | CDU Source 1 Line to Line Voltage Average | V | R | Process | Input Register 30055 | Analog 5 s | ⚑ |
| `Source2LineToLineVoltAvg` | CDU Source 2 Line to Line Voltage Average | V | R | Process | Input Register 30057 | Analog 5 s | ⚑ |
| `CurrentTotHarmonicDistortionAvg` | CDU Current Total Harmonic Distortion Average | % | R | Process | Input Register 30059 | Analog 5 s |  |
| `Source1Freq` | CDU Source 1 Frequency | Hz | R | Process | Input Register 30061 | Analog 5 s | ⚑ |
| `Source2Freq` | CDU Source 2 Frequency | Hz | R | Process | Input Register 30063 | Analog 5 s | ⚑ |
| `ControllerOperationType` | CDU Controller Operation Type |  | R | Status | Input Register 30065 | Slow 30 s |  |
| `SystemEnableModeSP` | CDU System Enable Mode Setpoint |  | R | Status | Input Register 30066 | Status 1 s |  |
| `ActiveDPSelection` | CDU Active Differential Pressure Selection |  | R | Status | Input Register 30067 | Status 1 s |  |
| `TSUHXGlyOutletTemp` | TSU Heat Exchanger Glycol Outlet Temperature | °F | R | Process | Input Register 30068 | Analog 5 s |  |
| `TSUHXCWSTemp` | TSU Heat Exchanger CWS Temperature | °F | R | Process | Input Register 30070 | Analog 5 s |  |
| `TSUPumpOutletGlyTemp` | TSU Pump Outlet Glycol Temperature | °F | R | Process | Input Register 30072 | Analog 5 s |  |
| `TSUTankOutletTemp` | TSU Tank Outlet Temperature | °F | R | Process | Input Register 30074 | Analog 5 s |  |
| `TSUValveInletTemp` | TSU Valve Inlet Temperature | °F | R | Process | Input Register 30076 | Analog 5 s |  |
| `TSUTankBottomOutletTemp` | TSU Tank Bottom Outlet Temperature | °F | R | Process | Input Register 30078 | Analog 5 s |  |
| `TSUSecFlowMeterFromCDU` | TSU Secondary Flow Meter from CDU | gpm | R | Process | Input Register 30082 | Analog 5 s |  |
| `TSUTank3WayValveFb` | TSU Tank 3-Way Valve Feedback | % | R | Process | Input Register 30084 | Analog 5 s | ⚑ |
| `TSUTank3WayValveCmd` | TSU Tank 3-Way Valve Command | % | R | Process | Input Register 30086 | Analog 5 s | ⚑ |
| `TSURemoteCWSSP` | TSU Remote CWS Setpoint | °F | R | Process | Input Register 30088 | Slow 30 s | ⚑ |
| `TSULocalCWSSP` | TSU Local CWS Setpoint | °F | R | Process | Input Register 30090 | Slow 30 s | ⚑ |
| `PumpFixedSpdSP` | CDU Pump Fixed Speed Setpoint | % | R | Process | Input Register 30092 | Slow 30 s |  |
| `PumpSpdCmdLead` | CDU Pump Speed Command (Lead CDU) | % | R | Process | Input Register 30094 | Analog 5 s |  |
| `TotPriCoolingLoadLead` | CDU Total Primary Cooling Load (Lead CDU) | kW | R | Process | Input Register 30096 | Analog 5 s | ⚑ |
| `TotSecCoolingLoadLead` | CDU Total Secondary Cooling Load (Lead CDU) | kW | R | Process | Input Register 30098 | Analog 5 s | ⚑ |
| `TotModbusPumpPowerLead` | CDU Total Modbus Pump Power (Lead CDU) | kW | R | Process | Input Register 30100 | Analog 5 s |  |
| `OnlineCountLead` | CDU Online Count (Lead CDU) |  | R | Process | Input Register 30102 | Slow 30 s |  |
| `TotCDUInstalledCountLead` | CDU Total CDU Installed Count (Lead CDU) |  | R | Process | Input Register 30104 | Slow 30 s |  |
| `TotSubordinateCDUsLead` | CDU Total Subordinate CDUs (Lead CDU) |  | R | Process | Input Register 30106 | Slow 30 s |  |
| `LowestCHWHeaderDPLead` | CDU Lowest Chilled Water Header DP (Lead CDU) | psi | R | Process | Input Register 30108 | Fast 500 ms |  |
| `ServerGlySupTempSP` | CDU Server Glycol Supply Temperature Setpoint | °F | R/W | Setpoint | Holding Register 40001 | Slow 30 s |  |
| `CHWHeaderDPSPLead` | CDU Chilled Water Header DP Setpoint (Lead CDU) | psi | R/W | Setpoint | Holding Register 40005 | Slow 30 s |  |

### AireBlockMCP (Data Hall AireBlock MCP, Modbus TCP/IP)

| Point | Description | Units | Access | Category | Source | Scan | Confirm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Zone1AHotAisleDP` | 1A Hot Aisle Differential Pressure | in/WC | R | Process | Input Register 30001 | Analog 5 s | ⚑ |
| `Zone2AHotAisleDP` | 2A Hot Aisle Differential Pressure | in/WC | R | Process | Input Register 30003 | Analog 5 s | ⚑ |
| `Zone1AColdAisleTemp` | 1A Cold Aisle Temperature | °F | R | Process | Input Register 30005 | Analog 5 s |  |
| `Zone1AColdAisleHum` | 1A Cold Aisle Humidity | %rh | R | Process | Input Register 30007 | Analog 5 s |  |
| `Zone2AColdAisleTemp` | 2A Cold Aisle Temperature | °F | R | Process | Input Register 30009 | Analog 5 s |  |
| `Zone2AColdAisleHum` | 2A Cold Aisle Humidity | %rh | R | Process | Input Register 30011 | Analog 5 s |  |
| `CHWSupTempA` | Chilled Water Supply Temperature A | °F | R | Process | Input Register 30013 | Analog 5 s |  |
| `Zone1BHotAisleDP` | 1B Hot Aisle Differential Pressure | in/WC | R | Process | Input Register 30015 | Analog 5 s | ⚑ |
| `Zone2BHotAisleDP` | 2B Hot Aisle Differential Pressure | in/WC | R | Process | Input Register 30017 | Analog 5 s | ⚑ |
| `Zone1BColdAisleTemp` | 1B Cold Aisle Temperature | °F | R | Process | Input Register 30019 | Analog 5 s |  |
| `Zone1BColdAisleHum` | 1B Cold Aisle Humidity | %rh | R | Process | Input Register 30021 | Analog 5 s |  |
| `Zone2BColdAisleTemp` | 2B Cold Aisle Temperature | °F | R | Process | Input Register 30023 | Analog 5 s |  |
| `Zone2BColdAisleHum` | 2B Cold Aisle Humidity | %rh | R | Process | Input Register 30025 | Analog 5 s |  |
| `CHWSupTempB` | Chilled Water Supply Temperature B | °F | R | Process | Input Register 30027 | Analog 5 s |  |
| `CCUSupTempAvg` | CCU Supply Temperature Average | °F | R | Process | Input Register 30029 | Analog 5 s |  |
| `ColdAisleAvgTemp` | Cold Aisle Average Temperature | °F | R | Process | Input Register 30031 | Analog 5 s |  |
| `DPMinControlValue` | Differential Pressure Min Control Value | in/WC | R | Process | Input Register 30033 | Analog 5 s | ⚑ |
| `DPMaxControlValue` | Differential Pressure Max Control Value | in/WC | R | Process | Input Register 30035 | Analog 5 s | ⚑ |
| `DPAAvg` | Differential Pressure A Average | in/WC | R | Process | Input Register 30037 | Analog 5 s | ⚑ |
| `DPBAvg` | Differential Pressure B Average | in/WC | R | Process | Input Register 30039 | Analog 5 s | ⚑ |
| `CCUTotKW` | CCU Total kW | kW | R | Process | Input Register 30041 | Analog 5 s |  |
| `CCUTotTons` | CCU Total Tons | tons | R | Process | Input Register 30043 | Analog 5 s |  |
| `CCU01CHWValveFlow` | CCU 01 Chilled Water Valve Flow | gpm | R | Process | Input Register 30045 | Analog 5 s | ⚑ |
| `CCU01FanSpd` | CCU 01 Fan Speed | rpm | R | Process | Input Register 30047 | Analog 5 s | ⚑ |
| `CCU01CWRetTemp` | CCU 01 CW Return Temperature | °F | R | Process | Input Register 30049 | Analog 5 s | ⚑ |
| `CCU01RetAirTemp` | CCU 01 Return Air Temperature | °F | R | Process | Input Register 30051 | Analog 5 s | ⚑ |
| `CCU01SupAirTemp` | CCU 01 Supply Air Temperature | °F | R | Process | Input Register 30053 | Analog 5 s | ⚑ |
| `CCU01CWValvePos` | CCU 01 CW Valve Position | % | R | Process | Input Register 30055 | Analog 5 s | ⚑ |
| `CCU01FanSpdFb` | CCU 01 Fan Speed Feedback | % | R | Process | Input Register 30057 | Analog 5 s | ⚑ |
| `CCU02CHWValveFlow` | CCU 02 Chilled Water Valve Flow | gpm | R | Process | Input Register 30059 | Analog 5 s | ⚑ |
| `CCU02FanSpd` | CCU 02 Fan Speed | rpm | R | Process | Input Register 30061 | Analog 5 s | ⚑ |
| `CCU02CWRetTemp` | CCU 02 CW Return Temperature | °F | R | Process | Input Register 30063 | Analog 5 s | ⚑ |
| `CCU02RetAirTemp` | CCU 02 Return Air Temperature | °F | R | Process | Input Register 30065 | Analog 5 s | ⚑ |
| `CCU02SupAirTemp` | CCU 02 Supply Air Temperature | °F | R | Process | Input Register 30067 | Analog 5 s | ⚑ |
| `CCU02CWValvePos` | CCU 02 CW Valve Position | % | R | Process | Input Register 30069 | Analog 5 s | ⚑ |
| `CCU02FanSpdFb` | CCU 02 Fan Speed Feedback | % | R | Process | Input Register 30071 | Analog 5 s | ⚑ |
| `CCU03CHWValveFlow` | CCU 03 Chilled Water Valve Flow | gpm | R | Process | Input Register 30073 | Analog 5 s | ⚑ |
| `CCU03FanSpd` | CCU 03 Fan Speed | rpm | R | Process | Input Register 30075 | Analog 5 s | ⚑ |
| `CCU03CWRetTemp` | CCU 03 CW Return Temperature | °F | R | Process | Input Register 30077 | Analog 5 s | ⚑ |
| `CCU03RetAirTemp` | CCU 03 Return Air Temperature | °F | R | Process | Input Register 30079 | Analog 5 s | ⚑ |
| `CCU03SupAirTemp` | CCU 03 Supply Air Temperature | °F | R | Process | Input Register 30081 | Analog 5 s | ⚑ |
| `CCU03CWValvePos` | CCU 03 CW Valve Position | % | R | Process | Input Register 30083 | Analog 5 s | ⚑ |
| `CCU03FanSpdFb` | CCU 03 Fan Speed Feedback | % | R | Process | Input Register 30085 | Analog 5 s | ⚑ |
| `CCU04CHWValveFlow` | CCU 04 Chilled Water Valve Flow | gpm | R | Process | Input Register 30087 | Analog 5 s | ⚑ |
| `CCU04FanSpd` | CCU 04 Fan Speed | rpm | R | Process | Input Register 30089 | Analog 5 s | ⚑ |
| `CCU04CWRetTemp` | CCU 04 CW Return Temperature | °F | R | Process | Input Register 30091 | Analog 5 s | ⚑ |
| `CCU04RetAirTemp` | CCU 04 Return Air Temperature | °F | R | Process | Input Register 30093 | Analog 5 s | ⚑ |
| `CCU04SupAirTemp` | CCU 04 Supply Air Temperature | °F | R | Process | Input Register 30095 | Analog 5 s | ⚑ |
| `CCU04CWValvePos` | CCU 04 CW Valve Position | % | R | Process | Input Register 30097 | Analog 5 s | ⚑ |
| `CCU04FanSpdFb` | CCU 04 Fan Speed Feedback | % | R | Process | Input Register 30099 | Analog 5 s | ⚑ |
| `CCU05CHWValveFlow` | CCU 05 Chilled Water Valve Flow | gpm | R | Process | Input Register 30101 | Analog 5 s | ⚑ |
| `CCU05FanSpd` | CCU 05 Fan Speed | rpm | R | Process | Input Register 30103 | Analog 5 s | ⚑ |
| `CCU05CWRetTemp` | CCU 05 CW Return Temperature | °F | R | Process | Input Register 30105 | Analog 5 s | ⚑ |
| `CCU05RetAirTemp` | CCU 05 Return Air Temperature | °F | R | Process | Input Register 30107 | Analog 5 s | ⚑ |
| `CCU05SupAirTemp` | CCU 05 Supply Air Temperature | °F | R | Process | Input Register 30109 | Analog 5 s | ⚑ |
| `CCU05CWValvePos` | CCU 05 CW Valve Position | % | R | Process | Input Register 30111 | Analog 5 s | ⚑ |
| `CCU05FanSpdFb` | CCU 05 Fan Speed Feedback | % | R | Process | Input Register 30113 | Analog 5 s | ⚑ |
| `CCU06CHWValveFlow` | CCU 06 Chilled Water Valve Flow | gpm | R | Process | Input Register 30115 | Analog 5 s | ⚑ |
| `CCU06FanSpd` | CCU 06 Fan Speed | rpm | R | Process | Input Register 30117 | Analog 5 s | ⚑ |
| `CCU06CWRetTemp` | CCU 06 CW Return Temperature | °F | R | Process | Input Register 30119 | Analog 5 s | ⚑ |
| `CCU06RetAirTemp` | CCU 06 Return Air Temperature | °F | R | Process | Input Register 30121 | Analog 5 s | ⚑ |
| `CCU06SupAirTemp` | CCU 06 Supply Air Temperature | °F | R | Process | Input Register 30123 | Analog 5 s | ⚑ |
| `CCU06CWValvePos` | CCU 06 CW Valve Position | % | R | Process | Input Register 30125 | Analog 5 s | ⚑ |
| `CCU06FanSpdFb` | CCU 06 Fan Speed Feedback | % | R | Process | Input Register 30127 | Analog 5 s | ⚑ |
| `CCU07CHWValveFlow` | CCU 07 Chilled Water Valve Flow | gpm | R | Process | Input Register 30129 | Analog 5 s | ⚑ |
| `CCU07FanSpd` | CCU 07 Fan Speed | rpm | R | Process | Input Register 30131 | Analog 5 s | ⚑ |
| `CCU07CWRetTemp` | CCU 07 CW Return Temperature | °F | R | Process | Input Register 30133 | Analog 5 s | ⚑ |
| `CCU07RetAirTemp` | CCU 07 Return Air Temperature | °F | R | Process | Input Register 30135 | Analog 5 s | ⚑ |
| `CCU07SupAirTemp` | CCU 07 Supply Air Temperature | °F | R | Process | Input Register 30137 | Analog 5 s | ⚑ |
| `CCU07CWValvePos` | CCU 07 CW Valve Position | % | R | Process | Input Register 30139 | Analog 5 s | ⚑ |
| `CCU07FanSpdFb` | CCU 07 Fan Speed Feedback | % | R | Process | Input Register 30141 | Analog 5 s | ⚑ |
| `CCU08CHWValveFlow` | CCU 08 Chilled Water Valve Flow | gpm | R | Process | Input Register 30143 | Analog 5 s | ⚑ |
| `CCU08FanSpd` | CCU 08 Fan Speed | rpm | R | Process | Input Register 30145 | Analog 5 s | ⚑ |
| `CCU08CWRetTemp` | CCU 08 CW Return Temperature | °F | R | Process | Input Register 30147 | Analog 5 s | ⚑ |
| `CCU08RetAirTemp` | CCU 08 Return Air Temperature | °F | R | Process | Input Register 30149 | Analog 5 s | ⚑ |
| `CCU08SupAirTemp` | CCU 08 Supply Air Temperature | °F | R | Process | Input Register 30151 | Analog 5 s | ⚑ |
| `CCU08CWValvePos` | CCU 08 CW Valve Position | % | R | Process | Input Register 30153 | Analog 5 s | ⚑ |
| `CCU08FanSpdFb` | CCU 08 Fan Speed Feedback | % | R | Process | Input Register 30155 | Analog 5 s | ⚑ |
| `CCU09CHWValveFlow` | CCU 09 Chilled Water Valve Flow | gpm | R | Process | Input Register 30157 | Analog 5 s | ⚑ |
| `CCU09FanSpd` | CCU 09 Fan Speed | rpm | R | Process | Input Register 30159 | Analog 5 s | ⚑ |
| `CCU09CWRetTemp` | CCU 09 CW Return Temperature | °F | R | Process | Input Register 30161 | Analog 5 s | ⚑ |
| `CCU09RetAirTemp` | CCU 09 Return Air Temperature | °F | R | Process | Input Register 30163 | Analog 5 s | ⚑ |
| `CCU09SupAirTemp` | CCU 09 Supply Air Temperature | °F | R | Process | Input Register 30165 | Analog 5 s | ⚑ |
| `CCU09CWValvePos` | CCU 09 CW Valve Position | % | R | Process | Input Register 30167 | Analog 5 s | ⚑ |
| `CCU09FanSpdFb` | CCU 09 Fan Speed Feedback | % | R | Process | Input Register 30169 | Analog 5 s | ⚑ |
| `CCU10CHWValveFlow` | CCU 10 Chilled Water Valve Flow | gpm | R | Process | Input Register 30171 | Analog 5 s | ⚑ |
| `CCU10FanSpd` | CCU 10 Fan Speed | rpm | R | Process | Input Register 30173 | Analog 5 s | ⚑ |
| `CCU10CWRetTemp` | CCU 10 CW Return Temperature | °F | R | Process | Input Register 30175 | Analog 5 s | ⚑ |
| `CCU10RetAirTemp` | CCU 10 Return Air Temperature | °F | R | Process | Input Register 30177 | Analog 5 s | ⚑ |
| `CCU10SupAirTemp` | CCU 10 Supply Air Temperature | °F | R | Process | Input Register 30179 | Analog 5 s | ⚑ |
| `CCU10CWValvePos` | CCU 10 CW Valve Position | % | R | Process | Input Register 30181 | Analog 5 s | ⚑ |
| `CCU10FanSpdFb` | CCU 10 Fan Speed Feedback | % | R | Process | Input Register 30183 | Analog 5 s | ⚑ |
| `CCU11CHWValveFlow` | CCU 11 Chilled Water Valve Flow | gpm | R | Process | Input Register 30185 | Analog 5 s | ⚑ |
| `CCU11FanSpd` | CCU 11 Fan Speed | rpm | R | Process | Input Register 30187 | Analog 5 s | ⚑ |
| `CCU11CWRetTemp` | CCU 11 CW Return Temperature | °F | R | Process | Input Register 30189 | Analog 5 s | ⚑ |
| `CCU11RetAirTemp` | CCU 11 Return Air Temperature | °F | R | Process | Input Register 30191 | Analog 5 s | ⚑ |
| `CCU11SupAirTemp` | CCU 11 Supply Air Temperature | °F | R | Process | Input Register 30193 | Analog 5 s | ⚑ |
| `CCU11CWValvePos` | CCU 11 CW Valve Position | % | R | Process | Input Register 30195 | Analog 5 s | ⚑ |
| `CCU11FanSpdFb` | CCU 11 Fan Speed Feedback | % | R | Process | Input Register 30197 | Analog 5 s | ⚑ |
| `CCU12CHWValveFlow` | CCU 12 Chilled Water Valve Flow | gpm | R | Process | Input Register 30199 | Analog 5 s | ⚑ |
| `CCU12FanSpd` | CCU 12 Fan Speed | rpm | R | Process | Input Register 30201 | Analog 5 s | ⚑ |
| `CCU12CWRetTemp` | CCU 12 CW Return Temperature | °F | R | Process | Input Register 30203 | Analog 5 s | ⚑ |
| `CCU12RetAirTemp` | CCU 12 Return Air Temperature | °F | R | Process | Input Register 30205 | Analog 5 s | ⚑ |
| `CCU12SupAirTemp` | CCU 12 Supply Air Temperature | °F | R | Process | Input Register 30207 | Analog 5 s | ⚑ |
| `CCU12CWValvePos` | CCU 12 CW Valve Position | % | R | Process | Input Register 30209 | Analog 5 s | ⚑ |
| `CCU12FanSpdFb` | CCU 12 Fan Speed Feedback | % | R | Process | Input Register 30211 | Analog 5 s | ⚑ |
| `MasterControlMode` | Master Control Mode |  | R | Status | Input Register 30213 | Status 1 s |  |
| `Zone1AColdAisleTempFailAlm` | Zone 1A Cold Aisle Temperature Fail Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `Zone1ADPFailAlm` | Zone 1A Differential Pressure Fail Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `Zone2AColdAisleTempFailAlm` | Zone 2A Cold Aisle Temperature Fail Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `Zone2ADPFailAlm` | Zone 2A Differential Pressure Fail Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `Zone1BColdAisleTempFailAlm` | Zone 1B Cold Aisle Temperature Fail Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `Zone1BDPFailAlm` | Zone 1B Differential Pressure Fail Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `Zone2BColdAisleTempFailAlm` | Zone 2B Cold Aisle Temperature Fail Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `Zone2BDPFailAlm` | Zone 2B Differential Pressure Fail Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU01RetAirTempFail` | CCU 01 Return Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU01Offline` | CCU 01 Offline |  | R | Status | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU01FanStsFail` | CCU 01 Fan Status Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU01FanCommonAlm` | CCU 01 Fan Common Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU01UPSPowerFail` | CCU 01 UPS Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU01BackupPowerFail` | CCU 01 Backup Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU01MechanicalAPowerFail` | CCU 01 Mechanical A Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU01MechanicalBPowerFail` | CCU 01 Mechanical B Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU01SupAirTempFail` | CCU 01 Supply Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU02RetAirTempFail` | CCU 02 Return Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU02Offline` | CCU 02 Offline |  | R | Status | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU02FanStsFail` | CCU 02 Fan Status Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU02FanCommonAlm` | CCU 02 Fan Common Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU02UPSPowerFail` | CCU 02 UPS Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU02BackupPowerFail` | CCU 02 Backup Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU02MechanicalAPowerFail` | CCU 02 Mechanical A Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU02MechanicalBPowerFail` | CCU 02 Mechanical B Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU02SupAirTempFail` | CCU 02 Supply Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU03RetAirTempFail` | CCU 03 Return Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU03Offline` | CCU 03 Offline |  | R | Status | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU03FanStsFail` | CCU 03 Fan Status Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU03FanCommonAlm` | CCU 03 Fan Common Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU03UPSPowerFail` | CCU 03 UPS Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU03BackupPowerFail` | CCU 03 Backup Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU03MechanicalAPowerFail` | CCU 03 Mechanical A Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU03MechanicalBPowerFail` | CCU 03 Mechanical B Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU03SupAirTempFail` | CCU 03 Supply Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU04RetAirTempFail` | CCU 04 Return Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU04Offline` | CCU 04 Offline |  | R | Status | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU04FanStsFail` | CCU 04 Fan Status Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU04FanCommonAlm` | CCU 04 Fan Common Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU04UPSPowerFail` | CCU 04 UPS Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU04BackupPowerFail` | CCU 04 Backup Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU04MechanicalAPowerFail` | CCU 04 Mechanical A Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU04MechanicalBPowerFail` | CCU 04 Mechanical B Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU04SupAirTempFail` | CCU 04 Supply Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU05RetAirTempFail` | CCU 05 Return Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU05Offline` | CCU 05 Offline |  | R | Status | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU05FanStsFail` | CCU 05 Fan Status Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU05FanCommonAlm` | CCU 05 Fan Common Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU05UPSPowerFail` | CCU 05 UPS Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU05BackupPowerFail` | CCU 05 Backup Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU05MechanicalAPowerFail` | CCU 05 Mechanical A Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU05MechanicalBPowerFail` | CCU 05 Mechanical B Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU05SupAirTempFail` | CCU 05 Supply Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU06RetAirTempFail` | CCU 06 Return Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU06Offline` | CCU 06 Offline |  | R | Status | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU06FanStsFail` | CCU 06 Fan Status Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU06FanCommonAlm` | CCU 06 Fan Common Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU06UPSPowerFail` | CCU 06 UPS Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU06BackupPowerFail` | CCU 06 Backup Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU06MechanicalAPowerFail` | CCU 06 Mechanical A Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU06MechanicalBPowerFail` | CCU 06 Mechanical B Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU06SupAirTempFail` | CCU 06 Supply Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU07RetAirTempFail` | CCU 07 Return Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU07Offline` | CCU 07 Offline |  | R | Status | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU07FanStsFail` | CCU 07 Fan Status Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU07FanCommonAlm` | CCU 07 Fan Common Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU07UPSPowerFail` | CCU 07 UPS Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU07BackupPowerFail` | CCU 07 Backup Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU07MechanicalAPowerFail` | CCU 07 Mechanical A Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU07MechanicalBPowerFail` | CCU 07 Mechanical B Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU07SupAirTempFail` | CCU 07 Supply Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU08RetAirTempFail` | CCU 08 Return Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU08Offline` | CCU 08 Offline |  | R | Status | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU08FanStsFail` | CCU 08 Fan Status Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU08FanCommonAlm` | CCU 08 Fan Common Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU08UPSPowerFail` | CCU 08 UPS Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU08BackupPowerFail` | CCU 08 Backup Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU08MechanicalAPowerFail` | CCU 08 Mechanical A Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU08MechanicalBPowerFail` | CCU 08 Mechanical B Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU08SupAirTempFail` | CCU 08 Supply Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU09RetAirTempFail` | CCU 09 Return Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU09Offline` | CCU 09 Offline |  | R | Status | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU09FanStsFail` | CCU 09 Fan Status Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU09FanCommonAlm` | CCU 09 Fan Common Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU09UPSPowerFail` | CCU 09 UPS Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU09BackupPowerFail` | CCU 09 Backup Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU09MechanicalAPowerFail` | CCU 09 Mechanical A Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU09MechanicalBPowerFail` | CCU 09 Mechanical B Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU09SupAirTempFail` | CCU 09 Supply Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU10RetAirTempFail` | CCU 10 Return Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU10Offline` | CCU 10 Offline |  | R | Status | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU10FanStsFail` | CCU 10 Fan Status Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU10FanCommonAlm` | CCU 10 Fan Common Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU10UPSPowerFail` | CCU 10 UPS Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU10BackupPowerFail` | CCU 10 Backup Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU10MechanicalAPowerFail` | CCU 10 Mechanical A Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU10MechanicalBPowerFail` | CCU 10 Mechanical B Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU10SupAirTempFail` | CCU 10 Supply Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU11RetAirTempFail` | CCU 11 Return Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU11Offline` | CCU 11 Offline |  | R | Status | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU11FanStsFail` | CCU 11 Fan Status Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU11FanCommonAlm` | CCU 11 Fan Common Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU11UPSPowerFail` | CCU 11 UPS Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU11BackupPowerFail` | CCU 11 Backup Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU11MechanicalAPowerFail` | CCU 11 Mechanical A Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU11MechanicalBPowerFail` | CCU 11 Mechanical B Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU11SupAirTempFail` | CCU 11 Supply Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU12RetAirTempFail` | CCU 12 Return Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU12Offline` | CCU 12 Offline |  | R | Status | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU12FanStsFail` | CCU 12 Fan Status Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU12FanCommonAlm` | CCU 12 Fan Common Alarm |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU12UPSPowerFail` | CCU 12 UPS Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU12BackupPowerFail` | CCU 12 Backup Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU12MechanicalAPowerFail` | CCU 12 Mechanical A Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU12MechanicalBPowerFail` | CCU 12 Mechanical B Power Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCU12SupAirTempFail` | CCU 12 Supply Air Temp Fail |  | R | Alarm | Input Register (packed bit) 30215 to 30222 | Status 1 s | ⚑ |
| `CCUSupAirTempSP` | CCU Supply Air Temperature Setpoint | °F | R/W | Setpoint | Holding Register 40001 | Slow 30 s |  |
| `DPSP` | Differential Pressure Setpoint | in/WC | R/W | Setpoint | Holding Register 40003 | Slow 30 s |  |

### MiniAireBlock01 (Mini AireBlock (CCU), BACnet/IP)

| Point | Description | Units | Access | Category | Source | Scan | Confirm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ValveFb` | Valve Feedback | % | R | Process | Analog Input 101 (CV-1 Feedback) | Analog 5 s |  |
| `AirDP` | Air Differential Pressure |  | R | Process | Analog Input 103 (ADPS_1_Pressure) | Analog 5 s | ⚑ |
| `RetAirTemp` | Return Air Temperature | °F | R | Process | Analog Input 107 (Return_Air_Temperature) | Analog 5 s |  |
| `DischargeAirTemp` | Discharge Air Temperature | °F | R | Process | Analog Input 108 (Discharge_Air_Temperature) | Analog 5 s |  |
| `CHWSTemp` | CHWS Temperature | °F | R | Process | Analog Input 111 (CHWS_Temperature) | Analog 5 s |  |
| `CHWRTemp` | CHWR Temperature | °F | R | Process | Analog Input 112 (CHWR_Temperature) | Analog 5 s |  |
| `SpaceTempComStat` | Space Temperature (Com Stat) | °F | R | Process | Analog Input 5011 (ComSensor 1 SpaceTemp) | Analog 5 s |  |
| `SpaceHumComStat` | Space Humidity (Com Stat) | %rh | R | Process | Analog Input 5012 (ComSensor 1 Humidity) | Analog 5 s |  |
| `Fan1SpdOutput0To100` | Fan 1 Speed Output 0 to 100% | % | R/W | Setpoint | Analog Output 110 (Fan_1_Speed) | Analog 5 s | ⚑ |
| `Fan2SpdOutput0To100` | Fan 2 Speed Output 0 to 100% | % | R/W | Setpoint | Analog Output 111 (Fan_2_Speed) | Analog 5 s | ⚑ |
| `ControlValveCmdSignalOut` | Control Valve Command Signal Out | % | R/W | Setpoint | Analog Output 112 (CV-1_Cmd) | Analog 5 s | ⚑ |
| `RoomTemp` | Room Temperature | °F | R | Process | Analog Value 1 (Space_Temperature) | Analog 5 s |  |
| `RoomTempSP` | Room Temperature Setpoint | °F | R/W | Setpoint | Analog Value 2 (Space_Temperature_Setpoint) | Slow 30 s | ⚑ |
| `NormalModeFanSpdSP` | Normal Mode Fan Speed Setpoint | % | R/W | Setpoint | Analog Value 6 (Normal_Speed_Setpoint) | Slow 30 s | ⚑ |
| `RetTempSP` | Return Temperature Setpoint | °F | R/W | Setpoint | Analog Value 7 (Return_Temperature_Setpoint) | Slow 30 s | ⚑ |
| `ControlTemp` | Control Temperature | °F | R | Process | Analog Value 8 (Control_Temperature) | Analog 5 s |  |
| `ControlTempSP` | Control Temperature Setpoint | °F | R/W | Setpoint | Analog Value 9 (Control_Temperature_Setpoint) | Slow 30 s | ⚑ |
| `RetTempCalc` | Return Temperature (Calc) | °F | R | Process | Analog Value 10 (Return_Air_Temperature_Calc) | Analog 5 s |  |
| `DischargeTempCalc` | Discharge Temperature (Calc) | °F | R | Process | Analog Value 11 (Discharge_Air_Temperature_Calc) | Analog 5 s |  |
| `FanFailedSpdSP` | Fan Failed Speed Setpoint | % | R/W | Setpoint | Analog Value 20 (Failed_Speed_Setpoint) | Slow 30 s | ⚑ |
| `RoomHum` | Room Humidity | %rh | R | Process | Analog Value 21 (Space_Humidity) | Analog 5 s |  |
| `CHWSTempCalc` | CHWS Temperature (Calc) | °F | R | Process | Analog Value 22 (Chws_Temperature_Calc) | Analog 5 s |  |
| `CHWRTempCalc` | CHWR Temperature (Calc) | °F | R | Process | Analog Value 23 (Chwr_Temperature_Calc) | Analog 5 s |  |
| `Fan1TotRunHours` | Fan 1 Total Run Hours | h | R | Process | Analog Value 501 (FAN1_TOTAL_RUN_HRS) | Slow 30 s |  |
| `Fan1ActualSpd` | Fan 1 Actual Speed | rpm | R | Process | Analog Value 502 (FAN1_ACTUAL_SPD) | Analog 5 s |  |
| `Fan1MaxKW` | Fan 1 Maximum kW | kW | R | Process | Analog Value 503 (FAN1_MAX_KW) | Slow 30 s |  |
| `Fan1KW` | Fan 1 kW | kW | R | Process | Analog Value 504 (FAN1_KW) | Analog 5 s |  |
| `Fan2TotRunHours` | Fan 2 Total Run Hours | h | R | Process | Analog Value 601 (FAN2_TOTAL_RUN_HRS) | Slow 30 s |  |
| `Fan2ActualSpd` | Fan 2 Actual Speed | rpm | R | Process | Analog Value 602 (FAN2_ACTUAL_SPD) | Analog 5 s |  |
| `Fan2MaxKW` | Fan 2 Maximum kW | kW | R | Process | Analog Value 603 (FAN2_MAX_KW) | Slow 30 s |  |
| `Fan2KW` | Fan 2 kW | kW | R | Process | Analog Value 604 (FAN2_KW) | Analog 5 s |  |
| `ControlValveFlowRate` | Control Valve Flow Rate | gpm | R | Process | Analog Value 701 (CV_FLOW_RATE) | Analog 5 s | ⚑ |
| `Fan1HardwareAlmContact` | Fan 1 Hardware Alarm Contact |  | R | Alarm | Binary Input 102 (FAN_1_Alarm_Status) | COV / 1 s |  |
| `WaterLeakDetectorAlm` | Water Leak Detector Alarm |  | R | Alarm | Binary Input 104 (Water_LD) | COV / 1 s |  |
| `UPSDCPowerSourceAlm` | UPS DC Power Source Alarm |  | R | Alarm | Binary Input 105 (24VDC_PWR_ALARM_A_OR_B) | COV / 1 s |  |
| `AMechanicalPowerRunState` | A Mechanical Power Running State |  | R | Status | Binary Input 106 (A_Mech_Power_Running) | COV / 1 s |  |
| `Fan2HardwareAlmContact` | Fan 2 Hardware Alarm Contact |  | R | Alarm | Binary Input 109 (FAN_2_Alarm_Status) | COV / 1 s |  |
| `BMechanicalPowerRunState` | B Mechanical Power Running State |  | R | Status | Binary Input 110 (B_Mech_Power_Running) | COV / 1 s |  |
| `UnitModeEnable` | Unit Mode Enable |  | R | Status | Binary Value 7 (Unit_Enable) | COV / 1 s |  |
| `UnitOperatingMode` | Unit Operating Mode |  | R | Status | Binary Value 8 (Unit_Mode) | COV / 1 s |  |
| `ControlTempSelection` | Control Temperature Selection |  | R | Status | Binary Value 9 (Rm_Space_Switch) | COV / 1 s |  |
| `SpaceTempFailAlm` | Space Temperature Fail Alarm |  | R | Alarm | Binary Value 10 (Space_Temperature_Fail) | COV / 1 s |  |
| `FbFailAlm` | Feedback Fail Alarm |  | R | Alarm | Binary Value 11 (CV-1 Feedback_Fail) | COV / 1 s |  |
| `RetTempFailAlm` | Return Temperature Fail Alarm |  | R | Alarm | Binary Value 12 (Return_Air_Temperature_Fail) | COV / 1 s |  |
| `DischargeTempFailAlm` | Discharge Temperature Fail Alarm |  | R | Alarm | Binary Value 13 (Discharge_Air_Temperature_Fail) | COV / 1 s |  |
| `AlmInhibit` | Alarm Inhibit |  | R/W | Setpoint | Binary Value 14 (Alarm_Inhibit) | COV / 1 s | ⚑ |
| `SpaceTempHighAlm` | Space Temperature High Alarm |  | R | Alarm | Binary Value 15 (Space_Temperature_Hi_Alarm) | COV / 1 s |  |
| `RetTempHighAlm` | Return Temperature High Alarm |  | R | Alarm | Binary Value 17 (Return_Temperature_Hi_Alarm) | COV / 1 s |  |
| `UnitFailSts` | Unit Fail Status |  | R | Alarm | Binary Value 19 (Unit_Fail_Status) | COV / 1 s |  |
| `ValveFailToOpen` | Valve Fail to Open |  | R | Alarm | Binary Value 22 (Valve_Fail_To_Open) | COV / 1 s |  |
| `ValveFailToClose` | Valve Fail to Close |  | R | Alarm | Binary Value 23 (Valve_Fail_To_Close) | COV / 1 s |  |
| `SpaceHumFailAlm` | Space Humidity Fail Alarm |  | R | Alarm | Binary Value 24 (Space_Humidity_Fail) | COV / 1 s |  |
| `CHWSTempFailAlm` | CHWS Temperature Fail Alarm |  | R | Alarm | Binary Value 25 (Chws_Temperature_Fail) | COV / 1 s |  |
| `CHWRTempFailAlm` | CHWR Temperature Fail Alarm |  | R | Alarm | Binary Value 26 (Chwr_Temperature_Fail) | COV / 1 s |  |
| `LossOfUPSBackedControlPower` | Loss of UPS Backed Control Power |  | R | Alarm | Binary Value 27 (LOSS_OF_UPS_BACKED_PS) | COV / 1 s |  |
| `LossOfAMechanicalPowerSource` | Loss of A Mechanical Power Source |  | R | Alarm | Binary Value 28 (LOSS_OF_A_MECH_POWER) | COV / 1 s |  |
| `LossOfBMechanicalPowerSource` | Loss of B Mechanical Power Source |  | R | Alarm | Binary Value 29 (LOSS_OF_B_MECH_POWER) | COV / 1 s |  |
| `Fan1Alm` | Fan 1 Alarm |  | R | Alarm | Binary Value 30 (FAN_1_Alarm) | COV / 1 s |  |
| `Fan2Alm` | Fan 2 Alarm |  | R | Alarm | Binary Value 31 (FAN_2_Alarm) | COV / 1 s |  |
| `Fan1SpdFail` | Fan 1 Speed Fail |  | R | Alarm | Binary Value 501 (FAN1_SPD_FAIL) | COV / 1 s |  |
| `Fan1PhaseFailure` | Fan 1 Phase Failure |  | R | Alarm | Binary Value 502 (name TBC) | COV / 1 s | ⚑ |
| `Fan1Overheat` | Fan 1 Overheat |  | R | Alarm | Binary Value 503 (name TBC) | COV / 1 s | ⚑ |
| `Fan1CommError` | Fan 1 Comm Error |  | R | Alarm | Binary Value 504 (name TBC) | COV / 1 s | ⚑ |
| `Fan1GeneralError` | Fan 1 General Error |  | R | Alarm | Binary Value 505 (name TBC) | COV / 1 s | ⚑ |
| `Fan1MotorOverheat` | Fan 1 Motor Overheat |  | R | Alarm | Binary Value 506 (name TBC) | COV / 1 s | ⚑ |
| `Fan1CommonAlm` | Fan 1 Common Alarm |  | R | Alarm | Binary Value 507 (name TBC) | COV / 1 s | ⚑ |
| `Fan1HallSensorError` | Fan 1 Hall Sensor Error |  | R | Alarm | Binary Value 508 (name TBC) | COV / 1 s | ⚑ |
| `Fan1MotorBlocked` | Fan 1 Motor Blocked |  | R | Alarm | Binary Value 509 (name TBC) | COV / 1 s | ⚑ |
| `Fan1DCLinkUndervoltage` | Fan 1 DC Link Undervoltage |  | R | Alarm | Binary Value 510 (name TBC) | COV / 1 s | ⚑ |
| `Fan1CurrentLimit` | Fan 1 Current Limit |  | R | Alarm | Binary Value 511 (name TBC) | COV / 1 s | ⚑ |
| `Fan1LineImpedanceHigh` | Fan 1 Line Impedance High |  | R | Alarm | Binary Value 512 (name TBC) | COV / 1 s | ⚑ |
| `Fan1PowerLimiter` | Fan 1 Power Limiter |  | R | Alarm | Binary Value 513 (name TBC) | COV / 1 s | ⚑ |
| `Fan1OutputStageTempHigh` | Fan 1 Output Stage Temp High |  | R | Alarm | Binary Value 514 (name TBC) | COV / 1 s | ⚑ |
| `Fan1MotorTempHigh` | Fan 1 Motor Temp High |  | R | Alarm | Binary Value 515 (name TBC) | COV / 1 s | ⚑ |
| `Fan1ElectronicsTempHigh` | Fan 1 Electronics Temp High |  | R | Alarm | Binary Value 516 (name TBC) | COV / 1 s | ⚑ |
| `Fan1DCLinkVoltLow` | Fan 1 DC Link Voltage Low |  | R | Alarm | Binary Value 517 (name TBC) | COV / 1 s | ⚑ |
| `Fan1Braking` | Fan 1 Braking |  | R | Alarm | Binary Value 518 (name TBC) | COV / 1 s | ⚑ |
| `Fan1SpdBelowLimit` | Fan 1 Speed Below Limit |  | R | Alarm | Binary Value 519 (name TBC) | COV / 1 s | ⚑ |
| `Fan1OpenCircuit` | Fan 1 Open Circuit |  | R | Alarm | Binary Value 520 (name TBC) | COV / 1 s | ⚑ |
| `Fan1DCLinkVoltHigh` | Fan 1 DC Link Voltage High |  | R | Alarm | Binary Value 521 (name TBC) | COV / 1 s | ⚑ |
| `Fan1LineVoltHigh` | Fan 1 Line Voltage High |  | R | Alarm | Binary Value 522 (name TBC) | COV / 1 s | ⚑ |
| `Fan1SheddingActive` | Fan 1 Shedding Active |  | R | Alarm | Binary Value 523 (FAN1_LRF) | COV / 1 s |  |
| `Fan2SpdFail` | Fan 2 Speed Fail |  | R | Alarm | Binary Value 601 (FAN2_SPD_FAIL) | COV / 1 s |  |
| `Fan2PhaseFailure` | Fan 2 Phase Failure |  | R | Alarm | Binary Value 602 (name TBC) | COV / 1 s | ⚑ |
| `Fan2Overheat` | Fan 2 Overheat |  | R | Alarm | Binary Value 603 (name TBC) | COV / 1 s | ⚑ |
| `Fan2CommError` | Fan 2 Comm Error |  | R | Alarm | Binary Value 604 (name TBC) | COV / 1 s | ⚑ |
| `Fan2GeneralError` | Fan 2 General Error |  | R | Alarm | Binary Value 605 (name TBC) | COV / 1 s | ⚑ |
| `Fan2MotorOverheat` | Fan 2 Motor Overheat |  | R | Alarm | Binary Value 606 (name TBC) | COV / 1 s | ⚑ |
| `Fan2CommonAlm` | Fan 2 Common Alarm |  | R | Alarm | Binary Value 607 (name TBC) | COV / 1 s | ⚑ |
| `Fan2HallSensorError` | Fan 2 Hall Sensor Error |  | R | Alarm | Binary Value 608 (name TBC) | COV / 1 s | ⚑ |
| `Fan2MotorBlocked` | Fan 2 Motor Blocked |  | R | Alarm | Binary Value 609 (name TBC) | COV / 1 s | ⚑ |
| `Fan2DCLinkUndervoltage` | Fan 2 DC Link Undervoltage |  | R | Alarm | Binary Value 610 (name TBC) | COV / 1 s | ⚑ |
| `Fan2CurrentLimit` | Fan 2 Current Limit |  | R | Alarm | Binary Value 611 (name TBC) | COV / 1 s | ⚑ |
| `Fan2LineImpedanceHigh` | Fan 2 Line Impedance High |  | R | Alarm | Binary Value 612 (name TBC) | COV / 1 s | ⚑ |
| `Fan2PowerLimiter` | Fan 2 Power Limiter |  | R | Alarm | Binary Value 613 (name TBC) | COV / 1 s | ⚑ |
| `Fan2OutputStageTempHigh` | Fan 2 Output Stage Temp High |  | R | Alarm | Binary Value 614 (name TBC) | COV / 1 s | ⚑ |
| `Fan2MotorTempHigh` | Fan 2 Motor Temp High |  | R | Alarm | Binary Value 615 (name TBC) | COV / 1 s | ⚑ |
| `Fan2ElectronicsTempHigh` | Fan 2 Electronics Temp High |  | R | Alarm | Binary Value 616 (name TBC) | COV / 1 s | ⚑ |
| `Fan2DCLinkVoltLow` | Fan 2 DC Link Voltage Low |  | R | Alarm | Binary Value 617 (name TBC) | COV / 1 s | ⚑ |
| `Fan2Braking` | Fan 2 Braking |  | R | Alarm | Binary Value 618 (name TBC) | COV / 1 s | ⚑ |
| `Fan2SpdBelowLimit` | Fan 2 Speed Below Limit |  | R | Alarm | Binary Value 619 (name TBC) | COV / 1 s | ⚑ |
| `Fan2OpenCircuit` | Fan 2 Open Circuit |  | R | Alarm | Binary Value 620 (name TBC) | COV / 1 s | ⚑ |
| `Fan2DCLinkVoltHigh` | Fan 2 DC Link Voltage High |  | R | Alarm | Binary Value 621 (name TBC) | COV / 1 s | ⚑ |
| `Fan2LineVoltHigh` | Fan 2 Line Voltage High |  | R | Alarm | Binary Value 622 (name TBC) | COV / 1 s | ⚑ |
| `Fan2SheddingActive` | Fan 2 Shedding Active |  | R | Alarm | Binary Value 623 (FAN2_LRF) | COV / 1 s |  |
