import pytest

from rav.adb import Result


class FakeRunner:
    """Answers commands by matching the start of their argument list
    (ignoring the binary and -s <serial>)."""

    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, cmd, env=None, timeout=15):
        self.calls.append((cmd, env))
        args = list(cmd[1:])
        if args[:1] == ["-s"]:
            args = args[2:]
        for prefix, result in self.responses.items():
            if tuple(args[:len(prefix)]) == prefix:
                return result
        return Result(1, "", f"unexpected command {cmd}")


DEVICES_OK = Result(0, "List of devices attached\n100.64.0.5:5555\tdevice\n")


@pytest.fixture
def healthy_phone():
    return FakeRunner({
        ("version",): Result(0, "Android Debug Bridge version 1.0.41\n"),
        ("connect",): Result(0, "connected to 100.64.0.5:5555\n"),
        ("devices",): DEVICES_OK,
        ("shell", "getprop", "ro.build.version.release"): Result(0, "17\n"),
        ("shell", "getprop", "ro.build.version.sdk"): Result(0, "37\n"),
        ("shell", "dumpsys", "power"): Result(0, "  mWakefulness=Dozing\n"),
        ("--version",): Result(0, "tainuitech 5.0.1 <https://github.com/warnetech/remote-adb-viewer>\n"),
        ("-o",): Result(0, ""),   # ssh -o BatchMode=yes ...
    })


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    path = tmp_path / "devices.toml"
    monkeypatch.setenv("RAV_CONFIG", str(path))
    return path
