"""Read and update the broker host, port, username, and password in site.yaml."""

from __future__ import annotations

import json
import re
from pathlib import Path

_LINE = {
    "host": re.compile(r"^([ \t]*host:[ \t]*).*$", re.MULTILINE),
    "port": re.compile(r"^([ \t]*port:[ \t]*).*$", re.MULTILINE),
    "username": re.compile(r"^([ \t]*username:[ \t]*).*$", re.MULTILINE),
    "password": re.compile(r"^([ \t]*password:[ \t]*).*$", re.MULTILINE),
}


def broker_identity(broker: dict) -> tuple[str, int, str, str]:
    host = str(broker.get("host") or "127.0.0.1").strip()
    port = int(broker.get("port") or 1883)
    username = str(broker.get("username") or "")
    password = str(broker.get("password") or "")
    return host, port, username, password


def read_broker(path: Path) -> dict:
    import yaml

    cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    broker = cfg.get("broker") or {}
    host, port, username, password = broker_identity(broker)
    return {
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "tls": bool(broker.get("tls")),
        "client_id": broker.get("client_id") or "",
    }


def yaml_scalar(value: str) -> str:
    if value == "":
        return '""'
    if re.fullmatch(r"[A-Za-z0-9_./:@+-]+", value):
        return value
    return json.dumps(value)


def check_broker(host: str, port: int, username: str, password: str) -> str | None:
    if not host or len(host) > 253 or any(ch.isspace() for ch in host):
        return "Enter a broker IP or hostname."
    if any(ch not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-:" for ch in host):
        return "The broker address has a character that is not allowed."
    if port < 1 or port > 65535:
        return "Port must be from 1 to 65535."
    for label, value in (("Username", username), ("Password", password)):
        if len(value) > 128 or any(ch in value for ch in "\r\n\x00"):
            return f"{label} is too long or has a line break."
    return None


def write_broker(path: Path, host: str, port: int, username: str, password: str) -> None:
    text = path.read_text(encoding="utf-8")
    replacements = {
        "host": host,
        "port": str(int(port)),
        "username": yaml_scalar(username),
        "password": yaml_scalar(password),
    }
    for key, value in replacements.items():
        pattern = _LINE[key]
        if not pattern.search(text):
            raise ValueError(f"site.yaml has no broker {key} line")
        text = pattern.sub(lambda match, value=value: f"{match.group(1)}{value}", text, count=1)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)
