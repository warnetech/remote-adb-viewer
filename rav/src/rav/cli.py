"""rav: view and control a remote Android phone with TainuiTech."""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from rav import __version__, config
from rav.adb import Adb, find_binary
from rav.config import ConfigError, Device
from rav.doctor import diagnose, format_checks
from rav.presets import PROFILES, build_command
from rav.session import SessionError, open_session


def default_binary():
    return os.environ.get("RAV_TAINUITECH", "tainuitech")


def cmd_add(args):
    config.validate_name(args.name)
    if args.tcp:
        device = Device(args.name, "tcp", address=args.tcp)
    elif args.ssh:
        device = Device(args.name, "ssh", ssh=args.ssh, serial=args.serial or "")
    else:
        device = Device(args.name, "usb", serial=args.usb)
    devices = config.load()
    devices[args.name] = device
    config.save(devices)
    print(f"Saved '{args.name}' ({device.transport}). Try: rav doctor {args.name}")
    return 0


def cmd_remove(args):
    devices = config.load()
    if devices.pop(args.name, None) is None:
        print(f"rav: no device named '{args.name}'", file=sys.stderr)
        return 1
    config.save(devices)
    print(f"Removed '{args.name}'.")
    return 0


def cmd_list(args):
    devices = config.load()
    if not devices:
        print("No devices yet. Add one with `rav add <name> --tcp <ip:port>`.")
        return 0
    adb = Adb()
    r = adb.call("devices", device=False)
    states = dict(line.split("\t") for line in r.stdout.splitlines()[1:] if "\t" in line) if r.ok else {}
    for d in devices.values():
        where = {"tcp": d.address, "ssh": d.ssh, "usb": d.serial}[d.transport]
        if d.transport == "ssh":
            status = "(via ssh)"
        else:
            status = states.get(d.adb_serial(), "not connected")
        print(f"{d.name:<16} {d.transport:<4} {where:<28} {status}")
    return 0


def get_device(name):
    devices = config.load()
    if name not in devices:
        raise ConfigError(f"no device named '{name}' (see `rav list`)")
    return devices[name]


def cmd_view(args):
    device = get_device(args.name)
    binary = find_binary(args.binary)
    if not binary:
        print(f"rav: '{args.binary}' not found. Build and install TainuiTech "
              "(doc/build.md), or pass --binary.", file=sys.stderr)
        return 1
    cmd = build_command(binary, device, args.profile, args.headless, args.extra)
    with open_session(device) as adb:
        state = adb.state()
        if state != "device":
            print(f"rav: device is {state or 'not found'}. Run `rav doctor {device.name}`.",
                  file=sys.stderr)
            return 1
        if not args.no_wake and not adb.wake():
            print("rav: warning: could not wake the device", file=sys.stderr)
        print("+ " + " ".join(cmd), file=sys.stderr)
        return subprocess.call(cmd, env=adb.env)


def cmd_doctor(args):
    device = get_device(args.name)
    checks = diagnose(device, binary=args.binary)
    print(f"rav doctor {device.name} ({device.transport})")
    print(format_checks(checks))
    return 1 if any(c.status == "fail" for c in checks) else 0


def cmd_shot(args):
    device = get_device(args.name)
    out = Path(args.output or f"{device.name}-{datetime.now():%Y%m%d-%H%M%S}.png")
    with open_session(device) as adb:
        png = adb.screenshot()
    if png is None:
        print(f"rav: screenshot failed. Run `rav doctor {device.name}`.", file=sys.stderr)
        return 1
    out.write_bytes(png)
    print(out)
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="rav", description=__doc__)
    p.add_argument("--version", action="version", version=f"rav {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("add", help="save a device profile")
    a.add_argument("name")
    how = a.add_mutually_exclusive_group(required=True)
    how.add_argument("--tcp", "--tailscale", metavar="HOST:PORT",
                     help="phone reachable over TCP/IP, e.g. its Tailscale IP")
    how.add_argument("--ssh", metavar="USER@HOST",
                     help="phone plugged into a remote machine reachable by ssh")
    how.add_argument("--usb", metavar="SERIAL", help="phone plugged into this machine")
    a.add_argument("--serial", help="with --ssh: which phone, if several")
    a.set_defaults(func=cmd_add)

    r = sub.add_parser("remove", help="delete a device profile")
    r.add_argument("name")
    r.set_defaults(func=cmd_remove)

    ls = sub.add_parser("list", help="show saved devices")
    ls.set_defaults(func=cmd_list)

    v = sub.add_parser("view", help="view and control a device",
                       epilog="Options after -- are passed to tainuitech.")
    v.add_argument("name")
    v.add_argument("--profile", choices=sorted(PROFILES), default="lan")
    v.add_argument("--headless", action="store_true",
                   help="mirror a virtual display and keep the phone's screen off")
    v.add_argument("--no-wake", action="store_true", help="don't wake the phone first")
    v.add_argument("--binary", default=default_binary(), help="TainuiTech binary")
    v.set_defaults(func=cmd_view)

    d = sub.add_parser("doctor", help="check the connection to a device step by step")
    d.add_argument("name")
    d.add_argument("--binary", default=default_binary(), help="TainuiTech binary")
    d.set_defaults(func=cmd_doctor)

    s = sub.add_parser("shot", help="save a screenshot")
    s.add_argument("name")
    s.add_argument("-o", "--output", help="output file (default: <name>-<time>.png)")
    s.set_defaults(func=cmd_shot)
    return p


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    # Everything after "--" goes to tainuitech untouched.
    extra = []
    if "--" in argv:
        i = argv.index("--")
        argv, extra = argv[:i], argv[i + 1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    if extra and args.command != "view":
        parser.error("options after -- are only accepted by `rav view`")
    args.extra = extra
    try:
        return args.func(args)
    except (ConfigError, SessionError, ValueError) as e:
        print(f"rav: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
