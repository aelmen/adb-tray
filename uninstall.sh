#!/usr/bin/env bash
set -euo pipefail

pkill -f "adb-tray(\.py)?$" 2>/dev/null || true
rm -f "$HOME/.local/bin/adb-tray" \
      "$HOME/.local/share/applications/adb-tray.desktop" \
      "$HOME/.config/autostart/adb-tray.desktop"
echo "adb-tray avinstallerad. Inställningar finns kvar i ~/.config/adb-tray."
