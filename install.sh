#!/usr/bin/env bash
# Install adb-tray for the current user. Use --deps to also apt-install dependencies.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
APP_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"
TARGET="$BIN_DIR/adb-tray"
LOCALE_DIR="$HOME/.local/share/locale"

if [[ "${1:-}" == "--deps" ]]; then
    sudo apt-get install -y adb scrcpy python3-gi gir1.2-gtk-3.0 gir1.2-xapp-1.0 libnotify-bin gettext
fi

for cmd in adb scrcpy python3 notify-send msgfmt; do
    command -v "$cmd" >/dev/null || echo "Warning: '$cmd' is missing (run ./install.sh --deps)" >&2
done

mkdir -p "$BIN_DIR" "$APP_DIR" "$AUTOSTART_DIR"
install -m 755 "$SRC/adb-tray.py" "$TARGET"

if command -v msgfmt >/dev/null; then
    for po in "$SRC"/po/*.po; do
        lang="$(basename "$po" .po)"
        mkdir -p "$LOCALE_DIR/$lang/LC_MESSAGES"
        msgfmt --check -o "$LOCALE_DIR/$lang/LC_MESSAGES/adb-tray.mo" "$po"
    done
    sed "s|@EXEC@|$TARGET|" "$SRC/adb-tray.desktop.in" \
        | msgfmt --desktop --template=/dev/stdin -d "$SRC/po" -o "$APP_DIR/adb-tray.desktop"
else
    sed "s|@EXEC@|$TARGET|" "$SRC/adb-tray.desktop.in" > "$APP_DIR/adb-tray.desktop"
fi

if [[ "${NO_AUTOSTART:-0}" != "1" ]]; then
    cp "$APP_DIR/adb-tray.desktop" "$AUTOSTART_DIR/adb-tray.desktop"
fi

if command -v update-desktop-database >/dev/null; then
    update-desktop-database "$APP_DIR" 2>/dev/null || true
fi

pkill -f "adb-tray(\.py)?$" 2>/dev/null || true
sleep 1
(setsid "$TARGET" >/dev/null 2>&1 &)
echo "adb-tray installed to $TARGET and started."
