# Bidra till adb-tray

Tack för att du vill bidra! Det här dokumentet beskriver hur ändringar tas emot.

## Arbetsflöde

`main` är skyddad. Alla ändringar görs via **pull request** och slås ihop av underhållaren
([@aelmen](https://github.com/aelmen)). Det går inte att pusha direkt till `main`.

1. **Forka** repot (eller skapa en gren om du har skrivrättighet).
2. Skapa en gren från `main` med ett beskrivande namn, till exempel `feat/wifi-qr-pairing` eller
   `fix/offline-device-label`.
3. Gör små, fokuserade commits (se [Commit-meddelanden](#commit-meddelanden)).
4. Kör kontrollerna lokalt (se [Kontroller](#kontroller)).
5. Öppna en pull request mot `main` och fyll i mallen.
6. CI måste vara grönt och underhållaren måste godkänna innan ändringen slås ihop.
   PR:er slås ihop med **squash merge**.

Större ändringar eller nya funktioner: öppna gärna ett ärende först så att vi kan diskutera
upplägget innan du lägger tid på det.

## Utvecklingsmiljö

```bash
sudo apt install adb scrcpy python3-gi gir1.2-gtk-3.0 gir1.2-xapp-1.0 libnotify-bin shellcheck
pipx install ruff        # eller: pip install --user ruff

git clone https://github.com/<ditt-konto>/adb-tray.git
cd adb-tray
```

Kör programmet direkt från källkoden, utan att installera:

```bash
pkill -f 'adb-tray(\.py)?$'   # stoppa en eventuell installerad instans
./adb-tray.py
```

Programmet tillåter bara en instans åt gången (lås i `~/.config/adb-tray/tray.lock`).

## Kontroller

Samma kontroller körs i CI på varje pull request:

```bash
ruff check adb-tray.py
python3 -m py_compile adb-tray.py
shellcheck install.sh uninstall.sh
```

Testa dessutom manuellt i Cinnamon med minst en riktig enhet:

- [ ] Ikonen visas och menyn öppnas med höger- och vänsterklick
- [ ] USB-enhet listas, spegling startar och stoppar
- [ ] Wi-Fi: *Växla till Wi-Fi* och återanslutning via sparad adress
- [ ] `./install.sh` och `./uninstall.sh` fungerar

## Kodstil

- Python 3, standardbiblioteket + PyGObject. Lägg inte till nya beroenden utan att diskutera det först.
- GTK-anrop görs bara i huvudtråden. Blockerande arbete (`adb`, nätverk) körs i en bakgrundstråd via
  `run_bg`, och resultat skickas tillbaka med `GLib.idle_add`.
- Anropa externa program med argumentlistor (`subprocess.run([...])`), aldrig via ett skal med
  sammansatta strängar.
- Texter i gränssnittet är på svenska. Kod, kommentarer och commit-meddelanden på engelska.
- Kommentera *varför*, inte *vad*.

## Commit-meddelanden

Vi använder [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat: add QR code pairing
fix: show offline wifi devices with disconnect option
docs: clarify wireless debugging steps
chore: bump CI actions
```

## Rapportera buggar och önska funktioner

Använd ärendemallarna under **Issues → New issue**. Ta med:

- distribution och version av Cinnamon
- `adb version` och `scrcpy --version`
- enhetens modell och Android-version
- relevanta rader ur `~/.config/adb-tray/scrcpy-*.log` eller utskriften från `./adb-tray.py`

Säkerhetsproblem ska **inte** rapporteras som öppna ärenden – se [SECURITY.md](SECURITY.md).

## Uppförande

Projektet följer [uppförandekoden](CODE_OF_CONDUCT.md). Genom att delta förväntas du följa den.

## Licens

Genom att skicka in ett bidrag godkänner du att det licensieras under projektets [MIT-licens](LICENSE).
