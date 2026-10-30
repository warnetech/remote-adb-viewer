"""Check each link between this computer and the phone, in order."""

from dataclasses import dataclass

from rav.adb import Adb, find_binary, run
from rav.session import SessionError, open_session, port_open, split_address

ANDROID_17_SDK = 37


@dataclass
class Check:
    name: str
    status: str            # pass, warn, fail
    detail: str
    hint: str = ""


def diagnose(device, binary="tainuitech", runner=run, which=find_binary,
             session=open_session, can_reach=port_open):
    """Return the list of checks. Stops at the first failure, since later
    checks depend on earlier links."""
    checks = []

    def add(name, status, detail, hint=""):
        checks.append(Check(name, status, detail, hint))
        return status != "fail"

    version = Adb(runner=runner).version()
    if not add("adb", "pass" if version else "fail", version or "adb not found",
               "Install Android platform-tools and put adb on your PATH."):
        return checks

    path = which(binary)
    if path:
        r = runner([path, "--version"])
        add("tainuitech", "pass", (r.stdout.splitlines() or [path])[0])
    elif not add("tainuitech", "fail", f"'{binary}' not found",
                 "Build and install TainuiTech (doc/build.md), or pass --binary."):
        return checks

    if device.transport == "tcp":
        try:
            host, port = split_address(device.address)
        except SessionError as e:
            add("network", "fail", str(e), "Fix the address with `rav add`.")
            return checks
        if not add("network", "pass" if can_reach(host, port) else "fail",
                   f"{host}:{port}",
                   "Unreachable. Is Tailscale up on both ends, and wireless "
                   "debugging (or `adb tcpip 5555`) enabled on the phone?"):
            return checks
    elif device.transport == "ssh":
        r = runner(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5",
                    device.ssh, "true"], timeout=15)
        if not add("network", "pass" if r.ok else "fail", f"ssh {device.ssh}",
                   "SSH login failed. Check the host and that key-based login "
                   "works (`ssh " + device.ssh + "`)."):
            return checks

    try:
        with session(device, runner=runner) as adb:
            _device_checks(adb, device, add)
    except SessionError as e:
        add("connection", "fail", str(e),
            "Check that the phone accepts adb connections on that port.")
    return checks


def _device_checks(adb, device, add):
    state = adb.state()
    hints = {
        None: "The phone is not listed by `adb devices`. Plug it in or reconnect, "
              "and for ssh make sure it is attached to the remote host.",
        "unauthorized": "Accept the 'Allow USB debugging' prompt on the phone.",
        "offline": "Reconnect the phone (toggle wireless debugging or replug USB).",
    }
    if not add("device", "pass" if state == "device" else "fail",
               state or "not found", hints.get(state, "")):
        return

    release = adb.getprop("ro.build.version.release")
    sdk = adb.getprop("ro.build.version.sdk")
    add("android", "pass", f"Android {release} (API {sdk})")

    wake = adb.wakefulness()
    if wake == "Awake":
        add("screen", "pass", "Awake")
    else:
        hint = "rav view wakes the phone before starting."
        if sdk.isdigit() and int(sdk) >= ANDROID_17_SDK:
            hint += " On Android 17 a sleeping phone renders a black virtual display otherwise."
        add("screen", "warn", wake or "unknown", hint)


def format_checks(checks):
    marks = {"pass": "✓", "warn": "!", "fail": "✗"}
    lines = []
    for c in checks:
        lines.append(f" {marks[c.status]} {c.name:<11} {c.detail}")
        if c.hint and c.status != "pass":
            lines.append(f"   {'':<11} → {c.hint}")
    return "\n".join(lines)
