"""TainuiTech command lines for each viewing preset."""

PROFILES = {
    # Same network: favour quality.
    "lan": ["--video-bit-rate=16M"],
    # Over the internet: cap bandwidth and resolution to keep latency low.
    "wan": ["--video-bit-rate=2M", "--max-size=1024", "--max-fps=30"],
}

# Mirror a separate virtual display and leave the phone's screen off.
# --keep-active stops Android from dozing (which freezes the virtual display
# after about 30 s on Android 17).
HEADLESS = ["--new-display", "--turn-screen-off", "--keep-active"]


def build_command(binary, device, profile="lan", headless=False, extra=()):
    if profile not in PROFILES:
        raise ValueError(f"unknown profile '{profile}' (choose: {', '.join(PROFILES)})")
    cmd = [binary]
    serial = device.adb_serial()
    if serial:
        cmd.append(f"--serial={serial}")
    cmd.append(f"--window-title={device.name}")
    cmd += PROFILES[profile]
    if headless:
        cmd += HEADLESS
    cmd += list(extra)
    return cmd
