# Datacenter Sim

A Python simulator that publishes one data hall of UNS points to MQTT, plus a local page that shows the live values.

It stands in for the hall collectors so brokers, bridges, and screens can be tried before field equipment is online. The point list is `docs/Data_Wing_UNS.md` (2,000 points for one hall). The build notes are in `docs/UNS_Data_Simulator_Build_Plan.md`.

This cut publishes plain UNS JSON. Sparkplug B is not included yet.

## What you need

- Python 3.9 or newer
- An MQTT broker on `127.0.0.1:1883` with no username (HiveMQ Edge is what this was run against)

Broker, wing, and hall are set in `uns-sim/config/site.yaml`.

## Run it

From `uns-sim`:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -u -m sim.main
```

A second window serves the hall page at http://127.0.0.1:8090 :

```powershell
.\.venv\Scripts\python.exe -u -m dashboard.server
```

On Linux or macOS, use `python3 -m venv .venv` and `.venv/bin/python` instead.

Topics look like `Enterprise/Site/Wing01/Hall01/CDU01/ServerGlySupTemp`. Each payload is JSON:

```json
{"value": 80.1, "units": "degF", "quality": 192, "ts": 1791390000000}
```

Setpoint writes go to `.../<Point>/set` as `{"value": 81}`.

## Useful commands

```powershell
.\.venv\Scripts\python.exe -m sim.main --dry-run
.\.venv\Scripts\python.exe -m sim.main --scenario scenarios/cdu_pump_trip.yaml
.\.venv\Scripts\python.exe -m unittest tests.test_catalog
```

`--dry-run` prints the point counts and does not connect to the broker. The pump-trip scenario stops CDU pump 2, raises an alarm, then starts pump 3.
