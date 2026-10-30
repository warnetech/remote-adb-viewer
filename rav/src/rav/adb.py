"""Thin wrapper over the adb command line."""

import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class Result:
    returncode: int
    stdout: str
    stderr: str = ""

    @property
    def ok(self):
        return self.returncode == 0


def run(cmd, env=None, timeout=15):
    """Run a command and capture its output. A missing binary or a timeout is
    reported as a failed Result rather than an exception."""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, env=env,
                           timeout=timeout)
    except FileNotFoundError:
        return Result(127, "", f"{cmd[0]}: not found")
    except subprocess.TimeoutExpired:
        return Result(124, "", f"{cmd[0]}: timed out after {timeout}s")
    return Result(p.returncode, p.stdout, p.stderr)


class Adb:
    def __init__(self, serial="", env=None, runner=run, binary="adb"):
        self.serial = serial
        self.env = env        # carries ADB_SERVER_SOCKET for ssh tunnels
        self.runner = runner
        self.binary = binary

    def _cmd(self, *args, device=True):
        cmd = [self.binary]
        if device and self.serial:
            cmd += ["-s", self.serial]
        return cmd + list(args)

    def call(self, *args, device=True, timeout=15):
        return self.runner(self._cmd(*args, device=device), env=self.env,
                           timeout=timeout)

    def version(self):
        r = self.call("version", device=False)
        return r.stdout.splitlines()[0] if r.ok and r.stdout else None

    def connect(self, address):
        r = self.call("connect", address, device=False)
        # adb connect exits 0 even on failure; the message tells.
        text = (r.stdout + r.stderr).lower()
        return r.ok and ("connected to" in text), (r.stdout + r.stderr).strip()

    def state(self):
        """Return the device state from `adb devices`: device, unauthorized,
        offline, ..., or None if it is not listed."""
        r = self.call("devices", device=False)
        if not r.ok:
            return None
        rows = [line.split("\t") for line in r.stdout.splitlines()[1:] if "\t" in line]
        if self.serial:
            for serial, state in rows:
                if serial == self.serial:
                    return state
            return None
        return rows[0][1] if len(rows) == 1 else None

    def shell(self, *args, timeout=15):
        return self.call("shell", *args, timeout=timeout)

    def getprop(self, name):
        r = self.shell("getprop", name)
        return r.stdout.strip() if r.ok else ""

    def wakefulness(self):
        """Awake, Asleep, Dozing or Dreaming, from dumpsys power."""
        r = self.shell("dumpsys", "power")
        for line in r.stdout.splitlines():
            line = line.strip()
            if line.startswith("mWakefulness="):
                return line.split("=", 1)[1]
        return None

    def wake(self):
        # KEYCODE_WAKEUP never toggles: it does nothing if already awake.
        return self.shell("input", "keyevent", "KEYCODE_WAKEUP").ok

    def screenshot(self):
        try:
            r = subprocess.run(self._cmd("exec-out", "screencap", "-p"),
                               capture_output=True, env=self.env, timeout=30)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
        return r.stdout if r.returncode == 0 and r.stdout.startswith(b"\x89PNG") else None


def find_binary(name):
    return shutil.which(name)
