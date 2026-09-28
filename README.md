# adb-tray

[![CI](https://github.com/aelmen/adb-tray/actions/workflows/ci.yml/badge.svg)](https://github.com/aelmen/adb-tray/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**A system tray icon for your Android devices.** Right-click to list connected devices, mirror the screen,
rotate, take screenshots or connect wirelessly – without opening a terminal.

Built for Linux Mint / Cinnamon, on top of [`adb`](https://developer.android.com/tools/adb) and
[`scrcpy`](https://github.com/Genymobile/scrcpy).

```text
[icon] ─┬─ SM-X210  (USB)        ─┬─ Mirror screen
        ├─ ▶ SM-X210  (Wi-Fi)     ├─ Lock portrait / Lock landscape / Auto-rotate
        ├─ Connect via Wi-Fi  ►   ├─ Screenshot
        ├─ Refresh                ├─ Open adb shell
        ├─ Restart adb server     └─ Switch to Wi-Fi / Disconnect
        └─ Quit
```

> **Note:** the menu is currently in Swedish. This README uses English names with the Swedish label in
> parentheses the first time it appears, e.g. *Mirror screen* (*Spegla skärmen*).

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Getting started](#getting-started)
- [Configuration and files](#configuration-and-files)
- [Troubleshooting](#troubleshooting)
- [Uninstall](#uninstall)
- [Contributing](#contributing)
- [License](#license)

## Features

| Area | What you can do |
| --- | --- |
| Devices | Lists USB and Wi-Fi devices with model names, refreshed every 4 seconds. Shows when a device is waiting for authorization or is offline. |
| Mirroring | Start/stop `scrcpy` per device. Active mirrors are marked with ▶. Several devices can be mirrored at once. |
| Rotation | Lock portrait, lock landscape or restore auto-rotate – also while mirroring. |
| Tools | Screenshot to your Pictures folder, `adb shell` in a terminal, restart the adb server. |
| Wi-Fi | *Switch to Wi-Fi* from a USB-connected device, reconnect to previous addresses or a new one, or pair using Android's **Wireless debugging**. |

## Requirements

- Linux Mint / Cinnamon (the icon uses `XApp.StatusIcon`). Other desktops with StatusNotifier support via
  `xapp-sn-watcher` should work but are untested.
- Python 3 with PyGObject
- Packages: `adb`, `scrcpy`, `python3-gi`, `gir1.2-gtk-3.0`, `gir1.2-xapp-1.0`, `libnotify-bin`

## Installation

```bash
git clone https://github.com/aelmen/adb-tray.git
cd adb-tray
./install.sh --deps
```

`--deps` installs the packages above with `apt` (requires sudo). Leave it out if they are already installed.

The installer

- copies the program to `~/.local/bin/adb-tray`
- adds **ADB-enheter** to the application menu
- starts the program at login (skip with `NO_AUTOSTART=1 ./install.sh`)
- starts the icon right away

Run `./install.sh` again after `git pull` to update.

## Getting started

### Over USB

1. On the device: **Settings → About device → Software information**, tap *Build number* seven times to
   unlock developer options.
2. **Developer options → USB debugging** – turn it on.
3. Plug in the cable and tap **Allow** in the dialog on the device (ticking *Always allow* is recommended).
4. The device appears in the menu. Choose **Mirror screen** (*Spegla skärmen*).

### Over Wi-Fi, no cable at all

1. **Developer options → Wireless debugging** – turn it on and choose *Pair device with pairing code*.
2. In the menu: **Connect via Wi-Fi → Pair (wireless debugging)…**
   (*Anslut via Wi-Fi → Para ihop (trådlös felsökning)…*) and enter the pairing address, the code and,
   optionally, the connection address shown under *Wireless debugging*.

### Over Wi-Fi after USB

Choose **Switch to Wi-Fi** (*Växla till Wi-Fi*) on a USB-connected device. The address is saved and can be
picked under *Connect via Wi-Fi* next time. This mode lasts until the device reboots.

## Configuration and files

| Path | Contents |
| --- | --- |
| `~/.local/bin/adb-tray` | The program |
| `~/.config/adb-tray/hosts.json` | Recently used Wi-Fi addresses (max 10) |
| `~/.config/adb-tray/scrcpy-*.log` | Output of the latest mirroring session per device |
| `~/.config/autostart/adb-tray.desktop` | Autostart at login |

The default `scrcpy` flags (`-m 1600 --stay-awake`, plus `-b 6M` over Wi-Fi) are in `SCRCPY_OPTS`
at the top of `adb-tray.py`.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| No icon is shown | Make sure the *Xapp Status Applet* is in your panel. Run `adb-tray` in a terminal and read the output. |
| Device is shown as *godkänn på enheten* (authorize on device) | Tap **Allow** in the dialog on the device. If no dialog appears, choose *Revoke USB debugging authorizations* in developer options and reconnect. |
| Mirroring closes immediately | Read `~/.config/adb-tray/scrcpy-*.log`. Some devices cannot encode full resolution – lower `-m` in `SCRCPY_OPTS`. |
| Wi-Fi connection fails | The device has probably rebooted. Connect over USB and choose *Switch to Wi-Fi* again, or use pairing. |
| Everything seems stuck | Choose **Restart adb server** (*Starta om adb-server*) in the menu. |
| `Failed to load module "xapp-gtk3-module"` | Harmless message, can be ignored. |

## Uninstall

```bash
./uninstall.sh
```

Settings in `~/.config/adb-tray/` are kept.

## Contributing

Contributions are welcome through pull requests. Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.
Report security issues as described in [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) © Anders Elmén
