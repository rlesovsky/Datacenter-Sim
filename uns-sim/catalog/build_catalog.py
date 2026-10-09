"""Parse Data_Wing_UNS.md into one hall's point catalog."""

from __future__ import annotations

import json
import re
from pathlib import Path

SCAN_GROUPS = {
    "fast 500 ms": ("Fast", 0.5),
    "status 1 s": ("Status", 1.0),
    "analog 5 s": ("Analog", 5.0),
    "slow 30 s": ("Slow", 30.0),
    "cov / 1 s": ("Status", 1.0),
}

UNIT_CODE = {
    "°F": "degF",
    "psi": "psi",
    "gpm": "gpm",
    "%": "pct",
    "%rh": "pctRH",
    "rpm": "rpm",
    "A": "A",
    "kW": "kW",
    "V": "V",
    "Hz": "Hz",
    "h": "h",
    "in/WC": "inWC",
    "tons": "tons",
    "lb/ft³": "lb/ft3",
    "BTU/lb": "BTU/lb",
    "lb/s": "lb/s",
    "psi / °F": "psi/degF",
}


def cells_for(heading: str) -> list[str]:
    title = heading.split("(", 1)[0].strip()
    if title.lower().startswith("chiller01"):
        return [f"Chiller{i:02d}" for i in range(1, 11)]
    return [title]


def split_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def value_kind(name: str, units: str, category: str, source: str) -> str:
    src = source.lower()
    if category == "Command":
        return "command"
    if category == "Alarm":
        return "alarm"
    if "packed word" in src:
        return "packed"
    if category == "Setpoint":
        return "setpoint_bool" if "binary" in src else "setpoint"
    if any(token in src for token in ("discrete", "binary", "packed bit", "coil")):
        return "status_bool"
    if name == "MPUE":
        return "analog"
    if category == "Status":
        return "status_enum"
    if units == "h" and "hour" in name.lower():
        return "counter"
    if not units:
        return "status_enum"
    return "analog"


def parse_markdown(path: Path) -> list[dict]:
    heading = ""
    in_table = False
    points: list[dict] = []
    seen: set[tuple[str, str]] = set()

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("### "):
            heading = line[4:].strip()
            in_table = False
            continue
        if not line.startswith("|"):
            in_table = False
            continue
        cols = split_row(line)
        if not cols:
            continue
        if cols[0] == "Point":
            in_table = True
            continue
        if not in_table or set(cols[0]) <= {"-", ":"}:
            continue
        if len(cols) < 7:
            continue

        name = cols[0].strip("`")
        units = cols[2].strip()
        category = cols[4].strip()
        source = cols[5].strip()
        scan_label = cols[6].strip().lower()
        if scan_label not in SCAN_GROUPS:
            raise ValueError(f"Unknown scan group {cols[6]!r} on {name}")
        scan, scan_s = SCAN_GROUPS[scan_label]
        confirm = len(cols) > 7 and "⚑" in cols[7]
        kind = value_kind(name, units, category, source)
        spec = {
            "name": name,
            "description": cols[1].strip(),
            "units": units,
            "units_code": UNIT_CODE.get(units, units),
            "access": cols[3].strip(),
            "category": category,
            "source": source,
            "scan": scan,
            "scan_s": scan_s,
            "confirm": confirm,
            "value_kind": kind,
        }
        for cell in cells_for(heading):
            key = (cell, name)
            if key in seen:
                raise ValueError(f"Duplicate point {cell}/{name}")
            seen.add(key)
            points.append({"cell": cell, **spec})
    return points


def summarize(points: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for point in points:
        counts[point["cell"]] = counts.get(point["cell"], 0) + 1
    return counts


def write_catalog(points: list[dict], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(points, indent=2), encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    source = root / "docs" / "Data_Wing_UNS.md"
    points = parse_markdown(source)
    dest = Path(__file__).resolve().parent / "catalog.json"
    write_catalog(points, dest)
    counts = summarize(points)
    print(f"{len(points)} points -> {dest}")
    for cell, count in counts.items():
        print(f"  {cell}: {count}")


if __name__ == "__main__":
    main()
