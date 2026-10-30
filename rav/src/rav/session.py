"""Opening a connection to a device: adb connect, or an SSH tunnel."""

import contextlib
import os
import socket
import subprocess
import time

from rav.adb import Adb, run

SSH_ADB_PORT = 5038       # local port forwarded to the remote adb server (5037)
TUNNEL_PORT = 27183       # tainuitech's default video/control tunnel port


class SessionError(Exception):
    pass


def port_open(host, port, timeout=3.0):
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False


def split_address(address):
    host, sep, port = address.rpartition(":")
    if not sep or not port.isdigit():
        raise SessionError(f"address '{address}' must be host:port (e.g. 100.64.0.5:5555)")
    return host, int(port)


def ssh_tunnel_cmd(target):
    # As documented in doc/tunnels.md: local 5038 -> remote adb server,
    # remote 27183 -> local (the device connects back through it).
    return ["ssh", "-CN", "-o", "ExitOnForwardFailure=yes",
            "-L", f"{SSH_ADB_PORT}:localhost:5037",
            "-R", f"{TUNNEL_PORT}:localhost:{TUNNEL_PORT}", target]


@contextlib.contextmanager
def open_session(device, runner=run, popen=subprocess.Popen, wait=10.0):
    """Yield an Adb bound to the device, with any tunnel kept open meanwhile."""
    if device.transport == "ssh":
        r = runner(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5",
                    device.ssh, "adb", "start-server"], timeout=20)
        if not r.ok:
            raise SessionError(f"cannot start adb on {device.ssh} over ssh: "
                               f"{r.stderr.strip() or 'ssh failed'}")
        proc = popen(ssh_tunnel_cmd(device.ssh), stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + wait
            while not port_open("127.0.0.1", SSH_ADB_PORT, timeout=0.5):
                if proc.poll() is not None:
                    err = proc.stderr.read().decode(errors="replace").strip()
                    raise SessionError(f"ssh tunnel to {device.ssh} failed: {err}")
                if time.monotonic() > deadline:
                    raise SessionError(f"ssh tunnel to {device.ssh} did not come up")
                time.sleep(0.2)
            env = dict(os.environ, ADB_SERVER_SOCKET=f"tcp:localhost:{SSH_ADB_PORT}")
            yield Adb(device.adb_serial(), env=env, runner=runner)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        return

    adb = Adb(device.adb_serial(), runner=runner)
    if device.transport == "tcp":
        ok, message = adb.connect(device.address)
        if not ok:
            raise SessionError(f"adb connect {device.address} failed: {message}")
    yield adb
