#!/usr/bin/env bash
set -euo pipefail

pkill -f "adb-tray(\.py)?$" 2>/dev/null || true
rm -f "$HOME/.local/bin/adb-tray" \
      "$HOME/.local/share/applications/adb-tray.desktop" \
      "$HOME/.config/autostart/adb-tray.desktop" \
      "$HOME"/.local/share/locale/*/LC_MESSAGES/adb-tray.mo
echo "adb-tray uninstalled. Settings are kept in ~/.config/adb-tray."
