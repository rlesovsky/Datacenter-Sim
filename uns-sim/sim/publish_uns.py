"""Plain UNS publisher: one retained JSON topic per point."""

from __future__ import annotations

import functools
import json
import time

import paho.mqtt.client as mqtt

print = functools.partial(print, flush=True)

from sim.hall import Hall


class UnsPublisher:
    def __init__(self, cfg: dict, halls: dict[tuple[int, int], Hall], writes, campus=None) -> None:
        broker = cfg["broker"]
        self.enterprise = cfg["enterprise"]
        self.site = cfg["site"]
        self.halls = halls
        self.campus = campus
        self.writes = writes
        self.connected = False
        self.reconnects = 0
        self.published = 0
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=broker.get("client_id") or "uns-sim",
            protocol=mqtt.MQTTv311,
        )
        username = broker.get("username") or ""
        password = broker.get("password") or ""
        if username:
            self.client.username_pw_set(username, password or None)
        if broker.get("tls"):
            self.client.tls_set()
        self.client.reconnect_delay_set(1, 30)
        self.client.max_queued_messages_set(0)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self._host = broker.get("host") or "127.0.0.1"
        self._port = int(broker.get("port") or 1883)

    def connect(self) -> None:
        self.client.connect(self._host, self._port, keepalive=30)
        self.client.loop_start()

    def close(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()

    def _on_connect(self, client, userdata, flags, reason_code, properties) -> None:
        if hasattr(reason_code, "is_failure"):
            failed = bool(reason_code.is_failure)
        else:
            failed = int(reason_code) != 0
        if failed:
            print(f"MQTT connect failed: {reason_code}")
            return
        self.connected = True
        topic = f"{self.enterprise}/{self.site}/+/+/+/+/set"
        client.subscribe(topic, qos=1)
        print(f"Connected to {self._host}:{self._port}, listening for writes on {topic}")

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties) -> None:
        self.connected = False
        self.reconnects += 1
        print(f"MQTT disconnected ({reason_code})")

    def _on_message(self, client, userdata, message) -> None:
        if message.topic.endswith("/set"):
            self.writes.put((message.topic, bytes(message.payload)))

    def topic_for(self, hall: Hall, point) -> str:
        return (
            f"{self.enterprise}/{self.site}/Wing{hall.wing:02d}/"
            f"Hall{hall.hall:02d}/{point.cell}/{point.name}"
        )

    def topic_for_campus(self, point) -> str:
        return f"{self.enterprise}/{self.site}/Campus/{point.cell}/{point.name}"

    def _publish(self, topic: str, point) -> None:
        body = {
            "value": point.publish_value(),
            "units": point.units_code,
            "quality": 192,
            "ts": int(time.time() * 1000),
        }
        qos = 1 if point.category in ("Alarm", "Setpoint", "Command") else 0
        self.client.publish(topic, json.dumps(body, separators=(",", ":")), qos=qos, retain=True)
        point.mark_published()
        self.published += 1

    def publish_point(self, hall: Hall, point) -> None:
        self._publish(self.topic_for(hall, point), point)

    def publish_campus(self, point) -> None:
        self._publish(self.topic_for_campus(point), point)

    def publish_all(self) -> None:
        for hall in self.halls.values():
            for point in hall.points.values():
                self.publish_point(hall, point)
        if self.campus is not None:
            for point in self.campus.points.values():
                self.publish_campus(point)
