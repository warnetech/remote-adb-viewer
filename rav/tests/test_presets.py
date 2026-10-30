import pytest

from rav.config import Device
from rav.presets import build_command


def test_wan_headless():
    d = Device("pixel", "tcp", address="100.64.0.5:5555")
    cmd = build_command("tainuitech", d, "wan", headless=True, extra=["--no-audio"])
    assert cmd == ["tainuitech", "--serial=100.64.0.5:5555", "--window-title=pixel",
                   "--video-bit-rate=2M", "--max-size=1024", "--max-fps=30",
                   "--new-display", "--turn-screen-off", "--keep-active", "--no-audio"]


def test_ssh_without_serial_lets_tainuitech_pick():
    cmd = build_command("tainuitech", Device("lab", "ssh", ssh="me@pi"))
    assert not any(a.startswith("--serial") for a in cmd)


def test_unknown_profile():
    with pytest.raises(ValueError):
        build_command("tainuitech", Device("p", "usb"), "satellite")
