# rav: Remote ADB Viewer

`rav` opens a [TainuiTech](../README.md) session to an Android phone that isn't on your desk, with one command. It handles the connection (Tailscale, LAN or an SSH tunnel), wakes the phone, picks sensible video settings for the link, and tells you exactly what's wrong when something fails.

```text
$ rav doctor pixel
rav doctor pixel (tcp)
 ✓ adb         Android Debug Bridge version 1.0.41
 ✓ tainuitech  tainuitech 5.0.1
 ✓ network     100.64.0.5:5555
 ✓ device      device
 ✓ android     Android 17 (API 37)
 ! screen      Dozing
               → rav view wakes the phone before starting. On Android 17 a sleeping phone renders a black virtual display otherwise.
```

## Install

You need **adb** (Android platform-tools) and **TainuiTech** built and on your `PATH` (see [doc/build.md](../doc/build.md)). Then:

```bash
pipx install ./rav        # or: uv tool install ./rav
```

`rav` uses only the Python standard library (Python 3.11+).

## Remote phone in 5 minutes with Tailscale

1. **Install [Tailscale](https://tailscale.com/download)** on the phone and on your computer, and sign in to the same account on both. Note the phone's Tailscale IP (`100.x.y.z`) in the Tailscale app.
2. **Enable wireless debugging on the phone.** Go to *Settings → Developer options → Wireless debugging*. If developer options are hidden, tap *Build number* seven times.
3. **Pair once.** Tap *Pair device with pairing code*, then on your computer run:
   ```bash
   adb pair 100.x.y.z:<pairing-port>     # enter the 6-digit code
   ```
4. **Save the phone.** Use the port shown under *IP address & port* on the Wireless debugging screen, not the pairing port:
   ```bash
   rav add pixel --tailscale 100.x.y.z:<port>
   rav doctor pixel
   ```
5. **View it:**
   ```bash
   rav view pixel --profile wan --headless
   ```

The wireless debugging port changes when the phone restarts wireless debugging. If `rav doctor` says the network is unreachable after a reboot, re-run `rav add` with the new port. If the phone is also on USB sometimes, `adb tcpip 5555` makes the port fixed until the next reboot.

**Never forward adb ports on your router.** ADB access means full control of the phone. Tailscale (or SSH) keeps it private and encrypted.

## Phone plugged into another machine (SSH)

If the phone is connected by USB to a home server, Raspberry Pi or another computer you can SSH into:

```bash
rav add lab --ssh me@pi.local            # add --serial <serial> if several phones are attached
rav view lab --profile wan
```

`rav` starts adb on the remote machine and opens the SSH tunnel described in [doc/tunnels.md](../doc/tunnels.md) (local 5038 → remote adb, remote 27183 → local). It closes the tunnel when the window closes. Key-based SSH login must work without a password prompt.

## Commands

| Command | What it does |
|---|---|
| `rav add <name> --tailscale HOST:PORT` | Save a phone reachable over TCP/IP (`--tcp` is the same) |
| `rav add <name> --ssh USER@HOST [--serial S]` | Save a phone plugged into a machine you can SSH into |
| `rav add <name> --usb SERIAL` | Save a phone plugged into this computer |
| `rav list` | Show saved phones and whether adb sees them |
| `rav doctor <name>` | Check adb → TainuiTech → network → device → Android → screen, with a fix for each failure |
| `rav view <name>` | Connect, wake the phone, and open TainuiTech |
| `rav shot <name> [-o file.png]` | Save a screenshot |
| `rav remove <name>` | Delete a saved phone |

### `rav view` options

| Option | Effect |
|---|---|
| `--profile lan` (default) | 16 Mbps video, for the same network |
| `--profile wan` | 2 Mbps, 1024 px, 30 fps, for over the internet |
| `--headless` | Mirror a separate virtual display and keep the phone's own screen off (`--new-display --turn-screen-off --keep-active`) |
| `--no-wake` | Don't send the wake key first |
| `--binary PATH` | Use a specific TainuiTech binary (or set `RAV_TAINUITECH`) |
| `-- <options>` | Pass anything else to TainuiTech, e.g. `rav view pixel -- --no-audio` |

Profiles are stored in `~/.config/rav/devices.toml`; set `RAV_CONFIG` to use another file.

## Development

```bash
cd rav
pytest
```

The tests use a fake `adb`, so no phone is needed.
