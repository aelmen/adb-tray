#!/usr/bin/env python3
"""System tray icon for adb devices and scrcpy mirroring (Cinnamon / XApp)."""
import contextlib
import fcntl
import gettext
import json
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("XApp", "1.0")
from gi.repository import GLib, Gtk, XApp  # noqa: E402

DOMAIN = "adb-tray"
_LOCALE_DIR = Path.home() / ".local" / "share" / "locale"
# gettext picks the language from LANGUAGE / LC_ALL / LC_MESSAGES / LANG, like the rest of the desktop.
_translation = gettext.translation(
    DOMAIN, localedir=_LOCALE_DIR if gettext.find(DOMAIN, _LOCALE_DIR) else None, fallback=True)
_ = _translation.gettext
ngettext = _translation.ngettext

APP = _("ADB Devices")
ICON = "scrcpy"
POLL_SECONDS = 4
TCP_PORT = 5555
CONFIG_DIR = Path.home() / ".config" / "adb-tray"
HOSTS_FILE = CONFIG_DIR / "hosts.json"
LEGACY_IP_FILE = Path.home() / ".config" / "tablet-mirror" / "ip"
SCRCPY_OPTS = ["-m", "1600", "--stay-awake"]


def adb(*args, serial=None, timeout=15):
    cmd = ["adb"] + (["-s", serial] if serial else []) + list(args)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return r.returncode, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return 1, "timeout"


def notify(msg):
    subprocess.Popen(["notify-send", "-i", ICON, APP, msg])


def list_devices():
    _rc, out = adb("devices", "-l", timeout=10)
    devices = []
    for line in out.splitlines():
        if not line.strip() or line.startswith(("List of", "*")):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        info = dict(p.split(":", 1) for p in parts[2:] if ":" in p)
        serial = parts[0]
        devices.append({
            "serial": serial,
            "state": parts[1],
            "model": info.get("model", "").replace("_", "-"),
            "wifi": ":" in serial or serial.startswith("adb-"),
        })
    return devices


def load_hosts():
    hosts = []
    with contextlib.suppress(OSError, ValueError):
        hosts = json.loads(HOSTS_FILE.read_text())
    if LEGACY_IP_FILE.exists():
        legacy = f"{LEGACY_IP_FILE.read_text().strip()}:{TCP_PORT}"
        if legacy not in hosts:
            hosts.append(legacy)
    return hosts


def save_host(host):
    hosts = [h for h in load_hosts() if h != host]
    hosts.insert(0, host)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    HOSTS_FILE.write_text(json.dumps(hosts[:10], indent=2))


def connect_host(host):
    _rc, out = adb("connect", host, timeout=10)
    ok = "connected to" in out and "failed" not in out
    if ok:
        save_host(host)
        notify(_("Connected to {host}").format(host=host))
    else:
        notify(_("Could not connect to {host}").format(host=host) + f"\n{out}")


class Tray:
    def __init__(self):
        self.icon = XApp.StatusIcon()
        self.icon.set_name("adb-tray")
        self.icon.set_icon_name(ICON)
        self.icon.set_tooltip_text(APP)
        self.mirrors = {}
        self.devices = []
        self.signature = None
        self.menu = None
        self.polling = False
        self.rebuild()
        self.poll()
        GLib.timeout_add_seconds(POLL_SECONDS, self.poll)

    # ---- polling -------------------------------------------------------
    def poll(self):
        if not self.polling:
            self.polling = True
            threading.Thread(target=self._poll_worker, daemon=True).start()
        return True

    def _poll_worker(self):
        devices = list_devices()
        GLib.idle_add(self.on_devices, devices)

    def on_devices(self, devices):
        self.polling = False
        self.devices = devices
        self.mirrors = {s: p for s, p in self.mirrors.items() if p.poll() is None}
        ready = [d for d in devices if d["state"] == "device"]
        tooltip = f"{APP}: " + ngettext("{n} device connected", "{n} devices connected",
                                         len(ready)).format(n=len(ready))
        if self.mirrors:
            tooltip += ", " + ngettext("{n} mirroring", "{n} mirroring",
                                       len(self.mirrors)).format(n=len(self.mirrors))
        self.icon.set_tooltip_text(tooltip)
        signature = (tuple((d["serial"], d["state"], d["model"]) for d in devices),
                     tuple(sorted(self.mirrors)), tuple(load_hosts()))
        if signature != self.signature and not (self.menu and self.menu.get_visible()):
            self.signature = signature
            self.rebuild()
        return False

    def run_bg(self, fn, *args):
        def worker():
            fn(*args)
            GLib.idle_add(self.poll)
        threading.Thread(target=worker, daemon=True).start()

    # ---- menu ----------------------------------------------------------
    @staticmethod
    def item(label, callback=None, *args, sensitive=True):
        mi = Gtk.MenuItem(label=label)
        mi.set_sensitive(callback is not None and sensitive)
        if callback:
            mi.connect("activate", lambda _w: callback(*args))
        return mi

    def rebuild(self):
        menu = Gtk.Menu()
        if not self.devices:
            menu.append(self.item(_("No devices connected")))
        for dev in self.devices:
            menu.append(self.device_item(dev))

        menu.append(Gtk.SeparatorMenuItem())
        wifi = Gtk.MenuItem(label=_("Connect via Wi-Fi"))
        sub = Gtk.Menu()
        connected = {d["serial"] for d in self.devices}
        for host in load_hosts():
            sub.append(self.item(host, self.run_bg, connect_host, host, sensitive=host not in connected))
        if load_hosts():
            sub.append(Gtk.SeparatorMenuItem())
        sub.append(self.item(_("New address..."), self.dialog_connect))
        sub.append(self.item(_("Pair (wireless debugging)..."), self.dialog_pair))
        wifi.set_submenu(sub)
        menu.append(wifi)

        menu.append(self.item(_("Refresh"), self.poll))
        menu.append(self.item(_("Restart adb server"), self.run_bg, self.restart_server))
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(self.item(_("Quit"), Gtk.main_quit))
        menu.show_all()

        self.menu = menu
        self.icon.set_primary_menu(menu)
        self.icon.set_secondary_menu(menu)

    def device_item(self, dev):
        serial = dev["serial"]
        name = dev["model"] or serial
        label = f"{name}  ({'Wi-Fi' if dev['wifi'] else 'USB'})"
        if serial in self.mirrors:
            label = "▶ " + label
        state_text = {"unauthorized": _("authorize on device"), "offline": _("offline")}
        if dev["state"] != "device":
            label += " – " + state_text.get(dev["state"], dev["state"])

        top = Gtk.MenuItem(label=label)
        sub = Gtk.Menu()
        if dev["state"] == "device":
            if serial in self.mirrors:
                sub.append(self.item(_("Stop mirroring"), self.stop_mirror, serial))
            else:
                sub.append(self.item(_("Mirror screen"), self.start_mirror, dev))
            sub.append(Gtk.SeparatorMenuItem())
            sub.append(self.item(_("Lock portrait"), self.run_bg, self.set_rotation, serial, 0))
            sub.append(self.item(_("Lock landscape"), self.run_bg, self.set_rotation, serial, 1))
            sub.append(self.item(_("Auto-rotate"), self.run_bg, self.set_rotation, serial, None))
            sub.append(Gtk.SeparatorMenuItem())
            sub.append(self.item(_("Screenshot"), self.run_bg, self.screenshot, dev))
            sub.append(self.item(_("Open adb shell"), self.open_shell, serial))
            if dev["wifi"]:
                sub.append(self.item(_("Disconnect"), self.run_bg, self.disconnect, serial))
            else:
                sub.append(self.item(_("Switch to Wi-Fi"), self.run_bg, self.switch_to_wifi, serial))
        elif dev["state"] == "unauthorized":
            sub.append(self.item(_("Tap 'Allow' in the dialog on the device")))
        if dev["wifi"] and dev["state"] != "device":
            sub.append(self.item(_("Disconnect"), self.run_bg, self.disconnect, serial))
        sub.append(Gtk.SeparatorMenuItem())
        sub.append(self.item(_("Serial number: {serial}").format(serial=serial)))
        top.set_submenu(sub)
        return top

    # ---- actions -------------------------------------------------------
    def start_mirror(self, dev):
        serial = dev["serial"]
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        log = CONFIG_DIR / f"scrcpy-{re.sub(r'[^A-Za-z0-9]', '_', serial)}.log"
        cmd = ["scrcpy", "-s", serial, "--window-title", dev["model"] or serial, *SCRCPY_OPTS]
        if dev["wifi"]:
            cmd += ["-b", "6M"]
        with open(log, "w") as fh:
            proc = subprocess.Popen(cmd, stdout=fh, stderr=subprocess.STDOUT)
        self.mirrors[serial] = proc
        started = time.monotonic()

        def watch():
            code = proc.wait()
            if code != 0 and time.monotonic() - started < 10:
                notify(_("scrcpy exited with an error ({code}). See {log}").format(code=code, log=log))
            GLib.idle_add(self.poll)

        threading.Thread(target=watch, daemon=True).start()
        self.poll()

    def stop_mirror(self, serial):
        proc = self.mirrors.get(serial)
        if proc and proc.poll() is None:
            proc.terminate()

    @staticmethod
    def set_rotation(serial, rotation):
        if rotation is None:
            adb("shell", "settings", "put", "system", "accelerometer_rotation", "1", serial=serial)
            return
        adb("shell", "settings", "put", "system", "accelerometer_rotation", "0", serial=serial)
        adb("shell", "settings", "put", "system", "user_rotation", str(rotation), serial=serial)

    @staticmethod
    def screenshot(dev):
        pictures = Path(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_PICTURES) or Path.home())
        target = pictures / f"{dev['model'] or 'android'}-{datetime.now().astimezone():%Y%m%d-%H%M%S}.png"
        r = subprocess.run(["adb", "-s", dev["serial"], "exec-out", "screencap", "-p"],
                           capture_output=True, timeout=30, check=False)
        if r.returncode != 0 or not r.stdout:
            notify(_("Screenshot failed"))
            return
        target.write_bytes(r.stdout)
        notify(_("Screenshot saved: {path}").format(path=target))

    @staticmethod
    def open_shell(serial):
        term = shutil.which("x-terminal-emulator") or shutil.which("gnome-terminal")
        if not term:
            notify(_("No terminal emulator found"))
            return
        subprocess.Popen([term, "-e", shlex.join(["adb", "-s", serial, "shell"])])

    @staticmethod
    def switch_to_wifi(serial):
        _rc, out = adb("shell", "ip", "-f", "inet", "addr", "show", "wlan0", serial=serial)
        match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", out)
        if not match:
            notify(_("The device does not seem to be connected to Wi-Fi"))
            return
        adb("tcpip", str(TCP_PORT), serial=serial)
        time.sleep(2)
        connect_host(f"{match.group(1)}:{TCP_PORT}")

    @staticmethod
    def disconnect(serial):
        adb("disconnect", serial)
        notify(_("Disconnected: {serial}").format(serial=serial))

    @staticmethod
    def restart_server():
        adb("kill-server")
        adb("start-server")
        notify(_("The adb server has been restarted"))

    # ---- dialogs -------------------------------------------------------
    @staticmethod
    def ask(title, fields):
        dialog = Gtk.Dialog(title=title, flags=Gtk.DialogFlags.MODAL)
        dialog.add_buttons(_("Cancel"), Gtk.ResponseType.CANCEL, _("OK"), Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_keep_above(True)
        grid = Gtk.Grid(column_spacing=8, row_spacing=6, margin=12)
        entries = []
        for row, (caption, default) in enumerate(fields):
            grid.attach(Gtk.Label(label=caption, xalign=0), 0, row, 1, 1)
            entry = Gtk.Entry(text=default, activates_default=True, width_chars=24)
            grid.attach(entry, 1, row, 1, 1)
            entries.append(entry)
        dialog.get_content_area().add(grid)
        dialog.show_all()
        ok = dialog.run() == Gtk.ResponseType.OK
        values = [e.get_text().strip() for e in entries]
        dialog.destroy()
        return values if ok else None

    def dialog_connect(self):
        hosts = load_hosts()
        values = self.ask(_("Connect via Wi-Fi"), [(_("Address (IP:port)"), hosts[0] if hosts else "")])
        if values and values[0]:
            host = values[0] if ":" in values[0] else f"{values[0]}:{TCP_PORT}"
            self.run_bg(connect_host, host)

    def dialog_pair(self):
        values = self.ask(_("Pair - wireless debugging"), [
            (_("Pairing address (IP:port)"), ""),
            (_("Pairing code"), ""),
            (_("Connection address (optional)"), ""),
        ])
        if not values or not values[0] or not values[1]:
            return

        def pair(address, code, connect_to):
            _rc, out = adb("pair", address, code, timeout=20)
            if "Successfully paired" not in out:
                notify(_("Pairing failed") + f"\n{out}")
                return
            notify(_("Pairing succeeded"))
            if connect_to:
                connect_host(connect_to)

        self.run_bg(pair, *values)


def main():
    if not shutil.which("adb"):
        print(_("adb is not installed"), file=sys.stderr)
        sys.exit(1)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # Kept open for the process lifetime; the flock is the single-instance guard.
    lock = open(CONFIG_DIR / "tray.lock", "w")  # noqa: SIM115
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print(_("adb-tray is already running"), file=sys.stderr)
        sys.exit(0)
    adb("start-server")
    Tray()
    Gtk.main()


if __name__ == "__main__":
    main()
