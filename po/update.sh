#!/usr/bin/env bash
# Regenerate po/adb-tray.pot and merge it into every po/*.po.
# --check: fail if the template or any translation is out of date (used by CI).
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

extract() {
    xgettext -L Python --from-code=UTF-8 --keyword=_ --keyword=ngettext:1,2 \
        --package-name=adb-tray --msgid-bugs-address=https://github.com/aelmen/adb-tray/issues \
        --add-comments=Translators: --omit-header -o - adb-tray.py
    xgettext -L Desktop --keyword=Name --keyword=Comment --omit-header -o - adb-tray.desktop.in
}

msgids() { msgcat --no-location --sort-output "$@" 2>/dev/null | grep -E '^msgid' || true; }

pot="$(mktemp)"
trap 'rm -f "$pot"' EXIT
{
    printf 'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n'
    extract
} | msguniq -o "$pot"

if [[ "${1:-}" == "--check" ]]; then
    status=0
    if [[ "$(msgids "$pot")" != "$(msgids po/adb-tray.pot)" ]]; then
        echo "po/adb-tray.pot is out of date - run po/update.sh" >&2
        status=1
    fi
    for po in po/*.po; do
        if msgfmt --statistics -o /dev/null "$po" 2>&1 | grep -qE 'untranslated|fuzzy'; then
            echo "$po has untranslated or fuzzy strings" >&2
            status=1
        fi
    done
    exit "$status"
fi

msgcat --no-location "$pot" -o po/adb-tray.pot
for po in po/*.po; do
    msgmerge --quiet --update --backup=none --no-location "$po" po/adb-tray.pot
done
echo "Updated po/adb-tray.pot and $(find po -name '*.po' | wc -l) translation(s)."
