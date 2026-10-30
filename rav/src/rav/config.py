"""Device profiles, stored in ~/.config/rav/devices.toml."""

import json
import os
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

TRANSPORTS = ("tcp", "ssh", "usb")
NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class ConfigError(Exception):
    pass


@dataclass
class Device:
    name: str
    transport: str          # tcp (Tailscale or LAN), ssh, or usb
    address: str = ""       # tcp: host:port
    ssh: str = ""           # ssh: user@host of the machine with the phone
    serial: str = ""        # usb, or a specific phone on the ssh host

    def adb_serial(self):
        """The serial adb uses for this device, or "" to let adb pick."""
        if self.transport == "tcp":
            return self.address
        return self.serial


def config_path():
    if "RAV_CONFIG" in os.environ:
        return Path(os.environ["RAV_CONFIG"])
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "rav" / "devices.toml"


def load(path=None):
    path = path or config_path()
    if not path.exists():
        return {}
    try:
        data = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{path}: {e}") from e
    devices = {}
    for name, fields in data.get("devices", {}).items():
        if fields.get("transport") not in TRANSPORTS:
            raise ConfigError(f"{path}: device '{name}' has an invalid transport")
        devices[name] = Device(name=name, **{k: str(v) for k, v in fields.items()
                                             if k in ("transport", "address", "ssh", "serial")})
    return devices


def save(devices, path=None):
    path = path or config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for d in sorted(devices.values(), key=lambda d: d.name):
        lines.append(f"[devices.{d.name}]")
        for key in ("transport", "address", "ssh", "serial"):
            value = getattr(d, key)
            if value:
                # JSON string escaping is valid TOML basic-string escaping.
                lines.append(f"{key} = {json.dumps(value)}")
        lines.append("")
    path.write_text("\n".join(lines))


def validate_name(name):
    if not NAME_RE.match(name):
        raise ConfigError(f"invalid device name '{name}' (use letters, digits, - and _)")
