# Remote ADB Viewer — Product Requirements Document

**Status:** Draft for review · **Date:** 2026-10-29 · **Owner:** warnetech

---

## 1. Summary

Remote ADB Viewer (RAV) lets you **see and control an Android phone from somewhere else**: another computer first, then any browser, then AI agents. It is built on a fork of [scrcpy](https://github.com/Genymobile/scrcpy) (v4.1, `dev` branch), which already includes upstream PR #7019 so virtual displays work on Android 17.

We don't build a streaming engine. scrcpy already has excellent ones. RAV adds what scrcpy leaves to the user: **getting connected from far away, safely, with one command**. Later phases add a browser front end and an agent/MCP interface.

### Assumptions (please confirm or correct)

| # | Assumption | Why it matters |
|---|---|---|
| A1 | "Remote" means a different network: you're away from home, or the phone sits on a desk or rack somewhere else. | It drives the networking choice (Tailscale or an SSH tunnel). |
| A2 | You control your own devices. This is not a public multi-tenant service. | It keeps authentication simple in early phases. |
| A3 | The first user is you, technically comfortable, on Linux/macOS/Windows. | A CLI is an acceptable first interface. |
| A4 | It should mostly not disturb the phone's physical screen (`--new-display`, `--turn-screen-off`). | That is why PR #7019 matters. |

---

## 2. Problem

Plain scrcpy over USB is great. Doing it **remotely** today means hand-assembling all of the following:

1. A network path to the phone's ADB (Tailscale, an SSH tunnel to a host with the phone on USB, or wireless debugging plus pairing).
2. The right scrcpy flags for a slow or variable link (bitrate, max size, codec, FPS).
3. Workarounds for Android quirks. Example: on Android 17 a sleeping phone gives a black virtual display (PR #7019), and it dozes again after about 30 s without `--keep-active`.
4. No way to check the setup when it fails ("is it adb, the tunnel, the device, or scrcpy?").
5. No browser access. Every viewer machine needs scrcpy installed.

---

## 3. Research: what already exists

The goal was to reuse rather than rebuild. Ratings are for **fit with RAV**.

### 3.1 Streaming and control engines

| Project | What it is | License | Fit | Notes |
|---|---|---|---|---|
| **scrcpy** (Genymobile) | Native desktop mirroring and control over ADB: video, audio, virtual displays, camera, recording, OTG. v4.1 in our fork. | Apache-2.0 | ★★★ **Core** | Already forked. Has built-in remote-ADB and SSH-tunnel docs (`doc/tunnels.md`): `ADB_SERVER_SOCKET`, `--tunnel-host`, `--tunnel-port`. |
| **Tango / ya-webadb** (yume-chan) | ADB in TypeScript for browsers (WebUSB) and Node, plus a scrcpy client that uses the **unmodified upstream scrcpy server**. Decoding via WebCodecs. Library only, no UI. | MIT | ★★★ **Phase 2 web client** | Follows current scrcpy server versions, which is the key advantage over ws-scrcpy. Chromium-only for WebUSB and WebCodecs. |
| **ws-scrcpy** (NetrisTV) | Complete web app: Node server, browser viewer over WebSocket, multi-touch, plus optional shell, devtools and file listing. | MIT (per mirror, verify) | ★★ Reference or stopgap | Depends on an old modified scrcpy server (`websocket-v1.17.x`). It would not get Android 17 fixes. Good to try out for UX ideas. |
| **ScrcpyOverWebRTC** | Web remote control over WebRTC. | MIT frontend | ★ Watch | Small project. WebRTC is the right long-term transport for poor networks. |
| **DeviceFarmer STF** | Full device-farm web app (successor to OpenSTF). | Apache-2.0 | ★ Too heavy | Slow maintenance. A competitor's blog claims Android 14/15 problems (unverified). Built for labs of many devices. |

### 3.2 Desktop GUIs (reference for UX only)

| Project | Notes |
|---|---|
| **Escrcpy** (Electron, Apache-2.0) | Multi-device window, broadcast input, batch screenshots and APK installs. Some extras are paid. |
| **QtScrcpy** (C++/Qt) | Its own renderer, aimed at batch/multi-device use. |
| **Scrcpy GUI**, **ScrcpyHub**, **guiscrcpy** | Simple front ends. Useful references for a "visual command builder". |

### 3.3 Python libraries (for the RAV CLI and automation)

| Library | Use in RAV | License |
|---|---|---|
| **adbutils** (openatx) | **Phase 1 choice.** Pure-Python ADB client: device list, shell, `connect`, forward, screenshots. No subprocess parsing. | MIT |
| **uiautomator2** (openatx) | UI tree, element taps, text input. Phase 4 agent tools. | MIT |
| **adb-shell** | ADB protocol without an adb server. Fallback option. | Apache-2.0 |
| **py-scrcpy-client** (`scrcpy-client`) | Python frames and control from a scrcpy server. **Targets scrcpy server 1.20**, too old. Avoid unless updated. | MIT |
| **pyscrcpy**, **adbblitz** | Newer Python scrcpy stream readers. Possibly useful for frame grabs in Phase 4. Not evaluated deeply. | — |

### 3.4 MCP servers and AI agents

| Project | Notes | Fit |
|---|---|---|
| **mobile-next/mobile-mcp** | TypeScript MCP server for Android and iOS, real devices and emulators. Accessibility tree first, screenshot fallback. `npx @mobilenext/mobile-mcp`. Apache-2.0, about 0.0.59, actively released. | ★★★ **Phase 4: use it, don't build** |
| Smaller ADB MCP servers (minhalvp, jduartedj, martingeidobler, mcp-adb, …) | Screenshot, tap, swipe and UI-dump tools. Several exist. | ★ Reference only |
| **Mobilerun** (formerly DroidRun) | Python framework for LLM-driven phone control. Needs a Portal APK on the device. MIT. Supports Anthropic, OpenAI, Gemini and more. | ★★ Optional Phase 4 for natural-language tasks |

### 3.5 Network path options

| Option | Verdict |
|---|---|
| **Tailscale** (phone or host on the tailnet, then `adb connect 100.x.y.z:port`) | **Recommended default.** Encrypted, no open ports, stable IPs. Fits single-owner use. |
| **SSH tunnel** to a machine that has the phone on USB (documented in scrcpy `doc/tunnels.md`) | **Second option.** Works anywhere SSH works, and is the most reliable path for USB-attached phones. |
| **Cloudflare Tunnel / Access** | Good for the **Phase 2 web UI** (HTTPS link plus login). Not suitable for raw ADB TCP. |
| Exposing ADB/wireless-debugging ports to the internet | **Never.** ADB access means full device control. |

**Conclusion:** everything RAV needs exists in pieces. The gap is the glue: a one-command, diagnosable remote session, then a browser front end on Tango, then agent access via mobile-mcp.

---

## 4. Goals and non-goals

**Goals**
- G1: Start a remote view/control session with one command, in under 10 seconds once set up.
- G2: When something fails, say exactly which link failed (`rav doctor`).
- G3: Never expose ADB to the public internet.
- G4: Stay close to upstream scrcpy so updates are a merge, not a port.

**Non-goals (for now)**
- Building our own video codec, streaming server or Android APK.
- iOS support.
- A multi-tenant SaaS, billing, or device-farm scheduling.
- Rooted-device features.

---

## 5. Phased plan

### Phase 0: Foundation ✅ done
- scrcpy v4.1 (`dev`) plus PR #7019 forked into this repo, with full history.
- Upstream sync script: `rav/scripts/sync-upstream.sh` (see `rav/UPSTREAM.md`).

### Phase 1: Quick win, the `rav` CLI (about 2–4 days)

**Outcome:** from your laptop anywhere, `rav view pixel` opens a working, low-latency window on the phone without touching its physical screen.

Python 3.11+ CLI (`rav/`, packaged with `uv`/`pipx`) that wraps **stock scrcpy** and uses **adbutils**.

| ID | Requirement | Priority |
|---|---|---|
| P1-1 | `rav add <name> --tailscale <ip:port>` / `--ssh <user@host>` / `--usb <serial>` saves a device profile in `~/.config/rav/devices.toml`. | Must |
| P1-2 | `rav view <name>` connects (Tailscale: `adb connect`; SSH: opens the tunnel the way `doc/tunnels.md` describes), **wakes the device first** (`KEYCODE_WAKEUP`, the Android 17 workaround from PR #7019 that also works on stock scrcpy), then runs scrcpy with the right preset. | Must |
| P1-3 | Presets: `--profile lan` (high bitrate) and `--profile wan` (`-b 2M --max-size 1024 --max-fps 30`, H.265 if supported), plus `--headless` (`--new-display --turn-screen-off --keep-active`). | Must |
| P1-4 | `rav doctor <name>` checks each link in order: adb binary/version → network reachability → `adb devices` state → authorization → Android version → screen/wakefulness (`dumpsys power`) → scrcpy version. It prints pass/fail with a fix hint for each. | Must |
| P1-5 | `rav list` shows saved devices and live status. | Should |
| P1-6 | `rav shot <name>` takes a quick screenshot to a file (adbutils). | Could |
| P1-7 | A README section: "Remote phone in 5 minutes with Tailscale". | Must |

**Acceptance**
- From a different network, `rav view` shows a live, controllable screen in 10 s or less on a working setup.
- With the phone asleep on Android 17, `rav view --headless` still renders (it no longer shows black).
- Unplugging the network, revoking ADB auth or stopping the tunnel each give a specific `rav doctor` message.

**Explicitly out of Phase 1:** browser UI, multiple viewers, recording management, agents.

### Phase 2: Browser viewer (about 1–2 weeks)

**Outcome:** open a URL from any Chromium browser to view and control the phone. Nothing to install on the viewing machine.

- A small Node/TypeScript server next to the phone (or its USB host) using **Tango** (`@yume-chan/adb`, `@yume-chan/scrcpy`) and pushing the **scrcpy server built from this fork**.
- Browser page: video (WebCodecs), touch/mouse/keyboard, rotate, back/home/recents, clipboard.
- Access only through **Tailscale** or **Cloudflare Tunnel + Access** (login wall). No unauthenticated port.
- Spike first (1 day): run ws-scrcpy to compare UX and latency, then commit to Tango.
- Acceptance: latency close to native scrcpy on the same link (within about 50 ms), and a 30-minute session without a drop.

### Phase 3: Daily-driver features (ongoing)
- Several devices on one dashboard, with live thumbnails.
- File push/pull and APK install (drag and drop).
- Session recording (scrcpy `--record`) with a downloads list.
- Audio forwarding in the browser.
- Basic shell panel (read-only by default).
- Optional: a WebRTC transport for bad networks (see ScrcpyOverWebRTC).

### Phase 4: Agents and MCP
- Ship **mobile-mcp** configured against RAV devices so Claude Code or other MCP clients can screenshot, tap, type and read the UI tree remotely. RAV supplies the connection; mobile-mcp supplies the tools.
- Optionally a thin `rav mcp` wrapper adding RAV-specific tools (`rav_wake`, `rav_doctor`, `rav_record`).
- Optional natural-language automation via **Mobilerun**.
- Guardrails: per-device allowlist, an action log, and a confirmation step for installs and settings changes.

---

## 6. Architecture (by Phase 2)

```
 Viewer (laptop / browser)                    Phone-side host (or phone over Wi-Fi)
 ┌────────────────────────┐   Tailscale /     ┌──────────────────────────────┐
 │ Phase 1: rav CLI       │   SSH tunnel      │ adb server                   │
 │   └─ scrcpy (native)   │◀────────────────▶ │   └─ scrcpy-server (fork)    │──USB/Wi-Fi──▶ Android
 │ Phase 2: browser       │   HTTPS via       │ Phase 2: Tango Node server   │
 │   └─ WebCodecs viewer  │◀─ CF Access ────▶ │   (WebSocket video + input)  │
 └────────────────────────┘                   └──────────────────────────────┘
```

---

## 7. Risks

| Risk | Mitigation |
|---|---|
| PR #7019 changes or is rejected upstream | `rav view` also sends its own wake key event, so we don't depend on the PR. `sync-upstream.sh --pr 7019` picks up revisions. |
| Android doze freezes virtual display after about 30 s | `--keep-active` in the headless preset; documented. |
| WAN latency or bandwidth | WAN preset; WebRTC in Phase 3. |
| Security: ADB equals full device control | Tailscale/SSH only; Cloudflare Access in front of the web UI; never bind ADB publicly; agent guardrails in Phase 4. |
| Fork drift from upstream | Merge `upstream/dev` regularly (59 commits behind today; merges cleanly). Keep RAV code in `rav/`, not in scrcpy's sources. |
| Tango is Chromium-only | Acceptable for a personal tool. Note it in the docs. |

---

## 8. Open questions for you

1. **Where does the phone live?** On your desk on Wi-Fi, plugged into a home server or Pi by USB, or in Termux on the phone itself? This decides whether Tailscale or SSH is the Phase 1 default.
2. **One phone or several?** If several, multi-device moves up from Phase 3.
3. **Who views?** Only you, or will you share links with others? Sharing pushes Cloudflare Access into Phase 2 as a requirement.
4. **Do you want agent control (Phase 4) sooner?** mobile-mcp could ship alongside Phase 1 at low cost.
5. **Language:** is Python fine for the Phase 1 CLI (adbutils), or would you rather keep everything in TypeScript from day one to match Phase 2?

---

## 9. Sources
- scrcpy: https://github.com/Genymobile/scrcpy (local: `doc/tunnels.md`, `doc/virtual-display.md`)
- PR #7019: https://github.com/Genymobile/scrcpy/pull/7019
- Tango / ya-webadb: https://github.com/yume-chan/ya-webadb, https://docs.tangoapp.dev/scrcpy
- ws-scrcpy: https://github.com/NetrisTV/ws-scrcpy
- ScrcpyOverWebRTC: https://github.com/hqw700/ScrcpyOverWebRTC
- DeviceFarmer STF: https://github.com/DeviceFarmer/stf
- Escrcpy: https://github.com/viarotel-org/escrcpy · QtScrcpy: https://github.com/barry-ran/QtScrcpy
- py-scrcpy-client: https://github.com/leng-yue/py-scrcpy-client · pyscrcpy: https://pypi.org/project/pyscrcpy · adbblitz: https://pypi.org/project/adbblitz
- adbutils: https://github.com/openatx/adbutils · uiautomator2: https://github.com/openatx/uiautomator2
- mobile-mcp: https://github.com/mobile-next/mobile-mcp
- Mobilerun (DroidRun): https://pypi.org/project/droidrun/ , https://pypi.org/project/mobilerun/
- Tailscale vs Cloudflare Tunnel: https://hometechops.com/guides/home-remote-access-tailscale-vs-cloudflare-tunnel
