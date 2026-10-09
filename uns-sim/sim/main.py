"""Run the data-hall UNS simulator against an MQTT broker."""

from __future__ import annotations

import argparse
import functools
import queue
import random
import time
from collections import Counter
from pathlib import Path

print = functools.partial(print, flush=True)

import yaml

from catalog.build_catalog import parse_markdown, summarize, write_catalog
from sim.commands import apply_write, parse_write
from sim.hall import Hall
from sim.publish_uns import UnsPublisher
from sim.scenario import Scenario


def load_config(path: Path) -> dict:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    base = path.parent

    def resolve(value):
        if not value:
            return None
        candidate = Path(value)
        if not candidate.is_absolute():
            candidate = (base / candidate).resolve()
        return candidate

    cfg["_config_dir"] = base
    cfg["catalog"] = resolve(cfg.get("catalog"))
    cfg["scenario"] = resolve(cfg.get("scenario"))
    return cfg


def build_halls(cfg: dict, catalog: list[dict]) -> dict[tuple[int, int], Hall]:
    halls = {}
    for wing in cfg["wings"]:
        for number in cfg["halls"]:
            halls[(int(wing), int(number))] = Hall(
                int(wing), int(number), catalog, float(cfg.get("deadband_pct", 0.5))
            )
    return halls


def print_summary(catalog: list[dict], halls: dict) -> None:
    counts = summarize(catalog)
    kinds = Counter(point["value_kind"] for point in catalog)
    print(f"Catalog: {len(catalog)} points per hall, {len(halls)} hall(s)")
    for cell, count in counts.items():
        print(f"  {cell}: {count}")
    print("Kinds: " + ", ".join(f"{name} {count}" for name, count in sorted(kinds.items())))
    sample = next(point for point in catalog if point["cell"] == "CDU01" and point["name"] == "ServerGlySupTemp")
    print(
        "Sample topic: Enterprise/Site/Wing01/Hall01/CDU01/ServerGlySupTemp"
        f"  ({sample['units_code']}, {sample['scan']})"
    )


def route_write(halls: dict, topic: str, payload: bytes, sim_t: float) -> None:
    parts = topic.split("/")
    if len(parts) != 7 or parts[-1] != "set":
        return
    wing_label, hall_label, cell, name = parts[2], parts[3], parts[4], parts[5]
    try:
        wing = int(wing_label.removeprefix("Wing"))
        hall_number = int(hall_label.removeprefix("Hall"))
    except ValueError:
        return
    hall = halls.get((wing, hall_number))
    if hall is None:
        return
    try:
        value = parse_write(payload)
    except ValueError:
        print(f"Bad write payload on {topic}")
        return
    if value is None:
        return
    print(apply_write(hall, cell, name, value, sim_t))


def apply_scenario(halls: dict, scenario: Scenario, sim_t: float) -> None:
    for event in scenario.due(sim_t):
        cell = event["cell"]
        for name, value in (event.get("sets") or {}).items():
            for hall in halls.values():
                if hall.point(cell, name) is None:
                    continue
                hall.apply_set(cell, name, value, lock=True)
                point = hall.point(cell, name)
                point.due_at = 0.0
                print(
                    f"Scenario {scenario.name} t={sim_t:.0f}s "
                    f"Wing{hall.wing:02d}/Hall{hall.hall:02d}/{cell}/{name} = {value}"
                )


def run(cfg: dict, dry_run: bool) -> None:
    catalog_path = cfg["catalog"]
    if catalog_path is None or not catalog_path.exists():
        raise SystemExit(f"Point list not found: {catalog_path}")
    catalog = parse_markdown(catalog_path)
    write_catalog(catalog, Path(__file__).resolve().parents[1] / "catalog" / "catalog.json")
    halls = build_halls(cfg, catalog)
    print_summary(catalog, halls)
    if dry_run:
        hall = next(iter(halls.values()))
        hall.couple(0.0)
        for point in hall.points.values():
            point.step(1.0, 1.0)
        supply = hall.point("CDU01", "ServerGlySupTemp")
        returned = hall.point("CDU01", "ServerGlyRetTemp")
        print(
            f"Dry run CDU supply {supply.publish_value()} {supply.units_code}, "
            f"return {returned.publish_value()} {returned.units_code}"
        )
        return

    scenario = Scenario(cfg["scenario"]) if cfg.get("scenario") else None
    if scenario:
        print(f"Scenario: {scenario.name} ({len(scenario.events)} events)")
    writes: queue.Queue = queue.Queue()
    publisher = UnsPublisher(cfg, halls, writes)
    publisher.connect()
    deadline = time.time() + 15
    while not publisher.connected and time.time() < deadline:
        time.sleep(0.05)
    if not publisher.connected:
        publisher.close()
        raise SystemExit(f"Could not connect to MQTT at {publisher._host}:{publisher._port}")

    sim_t = 0.0
    now = time.monotonic()
    for hall in halls.values():
        hall.couple(0.0)
        for point in hall.points.values():
            point.due_at = now + random.random() * point.scan_s
    print(f"Publishing initial snapshot ({sum(len(h.points) for h in halls.values())} topics)...")
    publisher.publish_all()
    print("Initial snapshot queued. Streaming changes.")

    time_scale = float(cfg.get("time_scale") or 1.0)
    stats_every = float(cfg.get("stats_interval_s") or 10)
    last = now
    next_stats = now + stats_every
    published_mark = publisher.published
    try:
        while True:
            now = time.monotonic()
            dt_real = min(now - last, 1.0)
            last = now
            sim_t += dt_real * time_scale
            while True:
                try:
                    topic, payload = writes.get_nowait()
                except queue.Empty:
                    break
                route_write(halls, topic, payload, sim_t)
            if scenario:
                apply_scenario(halls, scenario, sim_t)
            period_scale = time_scale if time_scale > 0 else 1.0
            for hall in halls.values():
                hall.couple(sim_t)
                for point in hall.points.values():
                    point.step(dt_real * time_scale, sim_t)
                    if now >= point.due_at:
                        point.due_at = now + point.scan_s / period_scale
                        if point.changed():
                            publisher.publish_point(hall, point)
            if now >= next_stats:
                delta = publisher.published - published_mark
                rate = delta / stats_every
                print(
                    f"t={sim_t:.0f}s  published {publisher.published}  "
                    f"{rate:.1f} msg/s  reconnects {publisher.reconnects}"
                )
                published_mark = publisher.published
                next_stats = now + stats_every
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("Stopping.")
    finally:
        publisher.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish a data-hall UNS to MQTT.")
    default_config = Path(__file__).resolve().parents[1] / "config" / "site.yaml"
    parser.add_argument("--config", type=Path, default=default_config)
    parser.add_argument("--dry-run", action="store_true", help="Parse the point list and exit.")
    parser.add_argument("--scenario", type=str, default="", help="Override the scenario YAML path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    if args.scenario:
        candidate = Path(args.scenario)
        if not candidate.is_absolute():
            candidate = (args.config.parent / candidate).resolve()
        cfg["scenario"] = candidate
    run(cfg, args.dry_run)


if __name__ == "__main__":
    main()
