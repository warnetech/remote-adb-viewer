import pytest
from conftest import FakeRunner

from rav.adb import Result
from rav.config import Device
from rav.session import SessionError, open_session, split_address, ssh_tunnel_cmd


def test_tcp_session_connects_first(healthy_phone):
    with open_session(Device("p", "tcp", address="100.64.0.5:5555"), runner=healthy_phone) as adb:
        assert adb.serial == "100.64.0.5:5555"
    assert healthy_phone.calls[0][0] == ["adb", "connect", "100.64.0.5:5555"]


def test_tcp_connect_failure():
    runner = FakeRunner({("connect",): Result(0, "failed to connect\n")})
    with pytest.raises(SessionError, match="adb connect"):
        with open_session(Device("p", "tcp", address="1.2.3.4:5555"), runner=runner):
            pass


def test_ssh_start_server_failure():
    runner = FakeRunner({("-o",): Result(255, "", "Permission denied (publickey)")})
    with pytest.raises(SessionError, match="Permission denied"):
        with open_session(Device("lab", "ssh", ssh="me@pi"), runner=runner):
            pass


def test_ssh_tunnel_matches_tunnels_doc():
    assert ssh_tunnel_cmd("me@pi") == [
        "ssh", "-CN", "-o", "ExitOnForwardFailure=yes",
        "-L", "5038:localhost:5037", "-R", "27183:localhost:27183", "me@pi"]


@pytest.mark.parametrize("bad", ["100.64.0.5", "host:", "host:port"])
def test_split_address_rejects(bad):
    with pytest.raises(SessionError):
        split_address(bad)
