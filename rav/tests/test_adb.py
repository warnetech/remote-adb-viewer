from conftest import FakeRunner

from rav.adb import Adb, Result


def test_state_for_serial():
    runner = FakeRunner({("devices",): Result(0, "List of devices attached\n"
                                                 "A\tunauthorized\nB\tdevice\n")})
    assert Adb("A", runner=runner).state() == "unauthorized"
    assert Adb("B", runner=runner).state() == "device"
    assert Adb("C", runner=runner).state() is None


def test_state_without_serial_needs_exactly_one_device():
    one = FakeRunner({("devices",): Result(0, "List of devices attached\nA\tdevice\n")})
    two = FakeRunner({("devices",): Result(0, "List of devices attached\nA\tdevice\nB\tdevice\n")})
    assert Adb(runner=one).state() == "device"
    assert Adb(runner=two).state() is None


def test_connect_checks_the_message():
    # adb connect exits 0 even when it fails.
    bad = FakeRunner({("connect",): Result(0, "failed to connect to '1.2.3.4:5555'\n")})
    good = FakeRunner({("connect",): Result(0, "connected to 1.2.3.4:5555\n")})
    assert Adb(runner=bad).connect("1.2.3.4:5555")[0] is False
    assert Adb(runner=good).connect("1.2.3.4:5555")[0] is True


def test_serial_is_passed_to_device_commands():
    runner = FakeRunner({("shell",): Result(0, "")})
    Adb("XYZ", runner=runner).wake()
    cmd, _ = runner.calls[0]
    assert cmd == ["adb", "-s", "XYZ", "shell", "input", "keyevent", "KEYCODE_WAKEUP"]


def test_wakefulness(healthy_phone):
    assert Adb(runner=healthy_phone).wakefulness() == "Dozing"
