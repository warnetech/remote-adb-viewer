import contextlib

from conftest import FakeRunner

from rav.adb import Adb, Result
from rav.config import Device
from rav.doctor import diagnose, format_checks
from rav.session import SessionError

PIXEL = Device("pixel", "tcp", address="100.64.0.5:5555")


def run_doctor(runner, device=PIXEL, reachable=True, which=lambda b: "/usr/bin/" + b):
    return diagnose(device, runner=runner, which=which,
                    can_reach=lambda host, port: reachable)


def statuses(checks):
    return {c.name: c.status for c in checks}


def test_healthy_but_dozing_android_17(healthy_phone):
    checks = run_doctor(healthy_phone)
    assert statuses(checks) == {"adb": "pass", "tainuitech": "pass", "network": "pass",
                                "device": "pass", "android": "pass", "screen": "warn"}
    screen = checks[-1]
    assert "Android 17" in screen.hint
    assert "Dozing" in format_checks(checks)


def test_missing_adb_stops_early():
    checks = run_doctor(FakeRunner({}))
    assert [(c.name, c.status) for c in checks] == [("adb", "fail")]


def test_unreachable_network(healthy_phone):
    checks = run_doctor(healthy_phone, reachable=False)
    assert checks[-1].name == "network" and checks[-1].status == "fail"
    assert "Tailscale" in checks[-1].hint


def test_unauthorized(healthy_phone):
    healthy_phone.responses[("devices",)] = Result(
        0, "List of devices attached\n100.64.0.5:5555\tunauthorized\n")
    checks = run_doctor(healthy_phone)
    assert checks[-1].name == "device" and checks[-1].status == "fail"
    assert "Allow USB debugging" in checks[-1].hint


def test_connect_refused(healthy_phone):
    healthy_phone.responses[("connect",)] = Result(0, "failed to connect to 100.64.0.5:5555\n")
    checks = run_doctor(healthy_phone)
    assert checks[-1].name == "connection" and checks[-1].status == "fail"


def test_missing_tainuitech(healthy_phone):
    checks = run_doctor(healthy_phone, which=lambda b: None)
    assert checks[-1].name == "tainuitech" and checks[-1].status == "fail"


def test_ssh_tunnel_failure(healthy_phone):
    @contextlib.contextmanager
    def broken_session(device, runner):
        raise SessionError("ssh tunnel to me@pi failed")
        yield

    device = Device("lab", "ssh", ssh="me@pi")
    checks = diagnose(device, runner=healthy_phone, which=lambda b: "/x/" + b,
                      session=broken_session)
    assert statuses(checks)["network"] == "pass"
    assert checks[-1].name == "connection" and checks[-1].status == "fail"
