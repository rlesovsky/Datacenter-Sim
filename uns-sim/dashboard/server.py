"""Serve a local hall dashboard fed by the UNS MQTT broker."""

from __future__ import annotations

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import paho.mqtt.client as mqtt
import yaml

STATIC = Path(__file__).resolve().parent / "static"


class Hub:
    def __init__(self) -> None:
        self.values: dict[str, dict] = {}
        self.connected = False
        self._cond = threading.Condition()
        self._clients: list[dict] = []

    def set_connected(self, connected: bool) -> None:
        with self._cond:
            self.connected = connected
            self._cond.notify_all()

    def update(self, key: str, point: dict) -> None:
        with self._cond:
            self.values[key] = point
            for client in self._clients:
                client["pending"][key] = point
            self._cond.notify_all()

    def snapshot(self) -> dict:
        with self._cond:
            return {"connected": self.connected, "points": dict(self.values)}

    def register(self) -> dict:
        client = {"pending": {}}
        with self._cond:
            self._clients.append(client)
        return client

    def unregister(self, client: dict) -> None:
        with self._cond:
            if client in self._clients:
                self._clients.remove(client)

    def wait_batch(self, client: dict, timeout: float = 5.0) -> tuple[dict, bool]:
        with self._cond:
            if not client["pending"]:
                self._cond.wait(timeout)
            batch = client["pending"]
            client["pending"] = {}
            return batch, self.connected


def load_config(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def start_mqtt(cfg: dict, hub: Hub) -> mqtt.Client:
    broker = cfg["broker"]
    enterprise = cfg["enterprise"]
    site = cfg["site"]
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="uns-dash",
        protocol=mqtt.MQTTv311,
    )
    username = broker.get("username") or ""
    if username:
        client.username_pw_set(username, broker.get("password") or None)
    if broker.get("tls"):
        client.tls_set()
    client.reconnect_delay_set(1, 30)

    def on_connect(client, userdata, flags, reason_code, properties):
        failed = bool(reason_code.is_failure) if hasattr(reason_code, "is_failure") else int(reason_code) != 0
        hub.set_connected(not failed)
        if failed:
            print(f"Dashboard MQTT connect failed: {reason_code}", flush=True)
            return
        topic = f"{enterprise}/{site}/#"
        client.subscribe(topic, qos=0)
        print(f"Dashboard subscribed to {topic}", flush=True)

    def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
        hub.set_connected(False)

    def on_message(client, userdata, message):
        parts = message.topic.split("/")
        if len(parts) != 6 or parts[-1] == "set":
            return
        try:
            body = json.loads(message.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return
        if not isinstance(body, dict) or "value" not in body:
            return
        key = "/".join(parts[2:])
        hub.update(
            key,
            {
                "value": body.get("value"),
                "units": body.get("units") or "",
                "quality": body.get("quality"),
                "ts": body.get("ts"),
            },
        )

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    host = broker.get("host") or "127.0.0.1"
    port = int(broker.get("port") or 1883)
    client.connect(host, port, keepalive=30)
    client.loop_start()
    return client


class Handler(BaseHTTPRequestHandler):
    hub: Hub
    mqtt_client: mqtt.Client
    enterprise: str
    site: str

    def log_message(self, fmt: str, *args) -> None:
        if args and "/events" in str(args[0]):
            return
        super().log_message(fmt, *args)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/state":
            self._json(self.hub.snapshot())
            return
        if path == "/events":
            self._events()
            return
        name = { "/": "index.html", "/app.js": "app.js", "/style.css": "style.css" }.get(path)
        if name is None:
            self.send_error(404)
            return
        self._file(STATIC / name)

    def do_POST(self) -> None:
        if self.path.split("?", 1)[0] != "/api/write":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            wing = str(body["wing"])
            hall = str(body["hall"])
            cell = str(body["cell"])
            name = str(body["name"])
            value = body["value"]
        except (KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError):
            self.send_error(400)
            return
        if not _safe(wing) or not _safe(hall) or not _safe(cell) or not _safe(name):
            self.send_error(400)
            return
        topic = f"{self.enterprise}/{self.site}/{wing}/{hall}/{cell}/{name}/set"
        payload = json.dumps({"value": value})
        self.mqtt_client.publish(topic, payload, qos=1)
        self._json({"ok": True, "topic": topic})

    def _events(self) -> None:
        client = self.hub.register()
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            self.wfile.write(b": hello\n\n")
            self.wfile.flush()
            while True:
                batch, connected = self.hub.wait_batch(client)
                if not batch:
                    self.wfile.write(b": ping\n\n")
                else:
                    data = json.dumps({"connected": connected, "points": batch}).encode("utf-8")
                    self.wfile.write(b"data: " + data + b"\n\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            return
        finally:
            self.hub.unregister(client)

    def _json(self, body: dict) -> None:
        raw = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _file(self, path: Path) -> None:
        if not path.exists():
            self.send_error(404)
            return
        raw = path.read_bytes()
        kind = "text/html; charset=utf-8"
        if path.suffix == ".js":
            kind = "text/javascript; charset=utf-8"
        elif path.suffix == ".css":
            kind = "text/css; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def _safe(token: str) -> bool:
    return bool(token) and all(ch.isalnum() or ch in "_-" for ch in token)


def main() -> None:
    parser = argparse.ArgumentParser(description="Hall overview dashboard for the UNS simulator.")
    default_config = Path(__file__).resolve().parents[1] / "config" / "site.yaml"
    parser.add_argument("--config", type=Path, default=default_config)
    parser.add_argument("--http-port", type=int, default=8090)
    args = parser.parse_args()
    cfg = load_config(args.config)
    hub = Hub()
    client = start_mqtt(cfg, hub)
    Handler.hub = hub
    Handler.mqtt_client = client
    Handler.enterprise = cfg["enterprise"]
    Handler.site = cfg["site"]
    server = ThreadingHTTPServer(("127.0.0.1", args.http_port), Handler)
    print(f"Dashboard http://127.0.0.1:{args.http_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping dashboard.", flush=True)
    finally:
        client.loop_stop()
        client.disconnect()
        server.server_close()


if __name__ == "__main__":
    main()
