"""Timeline of scripted writes against one hall."""

from __future__ import annotations

from pathlib import Path

import yaml


class Scenario:
    def __init__(self, path: Path) -> None:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        self.name = data.get("name", path.stem)
        self.events = sorted(data.get("events") or [], key=lambda event: float(event["at_s"]))
        self._index = 0

    def due(self, sim_t: float) -> list[dict]:
        ready = []
        while self._index < len(self.events) and float(self.events[self._index]["at_s"]) <= sim_t:
            ready.append(self.events[self._index])
            self._index += 1
        return ready
