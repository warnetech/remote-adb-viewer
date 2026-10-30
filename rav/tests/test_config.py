import pytest

from rav import config
from rav.config import ConfigError, Device


def test_round_trip(isolated_config):
    devices = {
        "pixel": Device("pixel", "tcp", address="100.64.0.5:5555"),
        "lab": Device("lab", "ssh", ssh="me@pi.local", serial='odd"serial'),
        "desk": Device("desk", "usb", serial="ABC123"),
    }
    config.save(devices)
    assert config.load() == devices


def test_missing_file_is_empty():
    assert config.load() == {}


def test_invalid_transport_is_rejected(isolated_config):
    isolated_config.write_text('[devices.x]\ntransport = "bluetooth"\n')
    with pytest.raises(ConfigError):
        config.load()


def test_adb_serial():
    assert Device("p", "tcp", address="1.2.3.4:5555").adb_serial() == "1.2.3.4:5555"
    assert Device("p", "usb", serial="ABC").adb_serial() == "ABC"
    assert Device("p", "ssh", ssh="h").adb_serial() == ""


@pytest.mark.parametrize("name", ["", "has space", "a/b", "x.y"])
def test_bad_names(name):
    with pytest.raises(ConfigError):
        config.validate_name(name)
