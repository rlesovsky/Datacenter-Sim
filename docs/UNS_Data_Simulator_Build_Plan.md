# UNS Data Simulator: Build Plan

Draft 2026-10-07. A Python program that publishes realistic data for the data hall UNS to an MQTT broker, so the brokers, bridges, Ignition MQTT Engine, historian and screens can be tested before any field equipment is online.

## 1. Goal and scope

- Publish every point in `Data_Wing_UNS.md` (2,000 per hall, 22,000 per wing) to a broker.
- Two output modes:
  - **Plain UNS:** one topic per point, JSON payload.
  - **Sparkplug B:** birth, data and death messages, as the Ignition collectors would send them.
- Scale from 1 hall to 1 wing (11 halls) to the full campus (44 halls) with a config change.
- Values behave like the real plant: analogs drift near setpoint, statuses mostly sit normal, and alarms fire during scripted events.
- Optionally accept setpoint writes and commands, so screen write paths can be tested.

**Out of scope:** Modbus or BACnet simulation. The simulator stands in for the collectors and publishes straight to MQTT.

## 2. Quick alternatives

Check these before building, because they may cover the first round of testing:

| Option | What it gives you | Limits |
| --- | --- | --- |
| Ignition Programmable Device Simulator + MQTT Transmission | Real Sparkplug output from an actual Ignition Edge gateway, using real UDTs | Simple waveforms only, no coupled behavior or scripted events, slow to set up for 2,000 points |
| HiveMQ Edge simulation adapter | Built-in test data source on the hall broker | Generic values, not your point list |
| **Python simulator (this plan)** | Exact UNS tree, realistic behavior, failure scenarios, campus scale | Needs to be built |

A sensible path is to use the Python simulator for broker, bridge and load testing, and Ignition's own simulator once the UDTs exist.

## 3. Architecture

```
points list (xlsx)  ──>  model builder  ──>  point models  ──>  publisher  ──>  broker
                                               ^                  |
                                    scenario engine        plain UNS or Sparkplug B

```

1. **Point catalog.** Generated from the points list workbook, the single source of truth. Each point has a topic, data type, units, category, normal band, scan group and access (R or R/W).
2. **Model builder.** Instantiates the catalog for each wing, hall and cell from the config.
3. **Point models.** One behavior class per kind of point (see section 4).
4. **Scenario engine.** Runs scripted events on a timeline, such as a pump trip at minute 5.
5. **Publisher.** Applies report-by-exception with deadbands, then sends in either mode.
6. **Command listener.** Subscribes to write topics and applies setpoint changes and commands.

## 4. How values are generated

| Point kind | Behavior |
| --- | --- |
| Process analog (temps, pressures, flows) | Tracks a target with first-order lag plus small noise, kept inside its normal band |
| Coupled analogs | Simple relationships, e.g. CDU return temp = supply temp + load / flow; header DP falls when a pump stops |
| Setpoints | Fixed until written; writes clamped to the spec range (e.g. 75 to 90 °F) |
| Commands (fault reset, start, E-stop) | Momentary; trigger the matching status change |
| Status bits and enums | Hold state; change only on scenario events or commands |
| Alarm bits | Normally false; set by scenarios or when an analog leaves its band |
| Counters (run hours) | Increment with simulated time |
| Packed status words | Built from the simulated bits |

**Scan groups:** Fast 500 ms, Status 1 s, Analog 5 s and Slow 30 s, the same groups as the points list.

## 5. Scenarios (failure library)

Each scenario is a short YAML script that can run against one hall or many.

- **Normal day:** load swing and outside air temperature curve
- **CDU pump trip:** pump 2 stops, then header DP drops, flow drops and an alarm fires; pump 3 starts after a delay
- **Chiller fault:** a chiller fails, the others ramp up, and the failed alarm latches until reset
- **Power transfer:** source 1 is lost, the transfer bits toggle, then the source returns
- **Collector loss:** a hall stops publishing (Sparkplug death message sent), then rejoins with a rebirth
- **Broker outage:** disconnect for N minutes, then reconnect and catch up, to test reconnect bursts and bridge queues
- **Alarm flood:** many alarms at once, to test alarm handling and screen load

## 6. Output modes in detail

**Plain UNS (build first)**

- Topic: `Enterprise/Site/Wing01/Hall01/CDU01/ServerGlySupTemp`
- Payload: `{"value": 80.1, "units": "degF", "quality": "Good", "ts": 1791390000000}`
- Retained last value, QoS 0 for data, QoS 1 for alarms and setpoints
- Writes come in on `.../<Point>/set`

**Sparkplug B (build second)**

- One edge node per collector (e.g. `FD01-TCA`). Devices are `Hall01_CDU01` and so on, and metrics are the point names.
- Must handle:
  - Birth messages with metric aliases
  - Sequence numbers
  - The bdSeq death certificate
  - Rebirth requests from the host
  - The Primary Host STATE topic: pause publishing when the host is offline
- Optional: also publish a duplicate Secondary collector stream for the critical cells, to mirror the redundant design.
- Protobuf definitions come from the Eclipse Tahu project (`sparkplug_b.proto`).

## 7. Technology

| Need | Choice |
| --- | --- |
| Language | Python 3.12 |
| MQTT client | `paho-mqtt` 2.x (MQTT 3.1.1 and 5, TLS) |
| Sparkplug payloads | `protobuf` with Tahu's `sparkplug_b.proto` |
| Config and scenarios | YAML (`pyyaml`), validated with `pydantic` |
| Point catalog import | `openpyxl` reading the points list workbook |
| Concurrency | `asyncio` scheduler; one process per wing for campus scale |
| Packaging | Docker image, so it runs next to the brokers in the lab |
| Monitoring | Console stats plus an optional Prometheus endpoint (messages/s, bytes/s, reconnects) |

## 8. Project layout

```
uns-sim/
  config/
    site.yaml            # broker, TLS, wings, halls, mode, rates, deadbands
    scenarios/*.yaml     # failure scripts
  catalog/
    build_catalog.py     # points list xlsx -> catalog.json
    catalog.json
  sim/
    models.py            # analog, setpoint, status, alarm, counter, packed word
    hall.py              # cells and coupling rules for one hall
    scenario.py          # timeline engine
    publish_uns.py       # plain MQTT JSON publisher
    publish_spb.py       # Sparkplug B publisher (birth, data, death, STATE, rebirth)
    commands.py          # write handling
    main.py              # CLI: run, list-scenarios, dry-run
  tests/
  Dockerfile

```

Example config:

```yaml
broker: { host: hivemq-edge-h01, port: 8883, tls: true, client_id: uns-sim-w1 }
mode: uns            # uns | sparkplug
enterprise: Enterprise
site: Site
wings: [1]
halls: [1, 2, 3]
chillers_per_hall: 10
time_scale: 1.0      # 10.0 = run 10x real time
deadband_pct: 0.5
scenario: scenarios/cdu_pump_trip.yaml

```

## 9. Build phases

| Phase | Deliverable | Rough effort |
| --- | --- | --- |
| 1 | Catalog import, plain UNS publisher, one hall at steady state | 1 to 2 days |
| 2 | Realistic models, coupling, deadbands, setpoint writes | 2 to 3 days |
| 3 | Scenario engine and the failure library | 2 days |
| 4 | Sparkplug B publisher with birth/death, aliases, STATE and rebirth | 2 to 3 days |
| 5 | Wing and campus scale, Docker, metrics, load test report | 1 to 2 days |
| **Total** |  | **About 8 to 12 working days** |

The effort is a planning estimate. Phase 4 carries the most risk, because Sparkplug behavior has to be proven against Ignition MQTT Engine.

## 10. How it gets tested

1. Phase 1: subscribe with MQTT Explorer and confirm the topic tree matches `Data_Wing_UNS.md`.
2. Phase 4: point Ignition MQTT Engine at the broker and confirm the tags build correctly, writes work and rebirths recover.
3. Run one wing (11 halls) through the HiveMQ Edge to Enterprise bridge. Measure messages/s and bytes/s against the throughput estimate (about 150 to 200 updates/s per hall realistic, 1,700 worst case).
4. Run the broker outage scenario to measure reconnect bursts and the catch-up flush.

## 11. Decisions needed before building

1. Plain UNS first, or Sparkplug B first? Plain UNS is faster to stand up; Sparkplug B is what production will use.
2. Which hall basis: the points list hall (about 2,000 points) or the scope narrative hall (about 8,400)? The catalog importer handles either.
3. Should the simulator accept writes, or publish only?
4. Where it runs: a lab VM next to the dev gateway, or a laptop against a test broker.
