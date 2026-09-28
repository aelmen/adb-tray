# adb-tray

[![CI](https://github.com/aelmen/adb-tray/actions/workflows/ci.yml/badge.svg)](https://github.com/aelmen/adb-tray/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**En ikon vid klockan för dina Android-enheter.** Högerklicka för att se anslutna enheter, spegla skärmen,
rotera, ta skärmdumpar eller ansluta trådlöst – utan att öppna en terminal.

Byggt för Linux Mint / Cinnamon, ovanpå [`adb`](https://developer.android.com/tools/adb) och
[`scrcpy`](https://github.com/Genymobile/scrcpy).

```text
[ikon] ─┬─ SM-X210  (USB)       ─┬─ Spegla skärmen
        ├─ ▶ SM-X210  (Wi-Fi)    ├─ Lås porträtt / Lås landskap / Autorotation
        ├─ Anslut via Wi-Fi  ►   ├─ Skärmdump
        ├─ Uppdatera             ├─ Öppna adb shell
        ├─ Starta om adb-server  └─ Växla till Wi-Fi / Koppla från
        └─ Avsluta
```

## Innehåll

- [Funktioner](#funktioner)
- [Krav](#krav)
- [Installation](#installation)
- [Kom igång](#kom-igång)
- [Konfiguration och filer](#konfiguration-och-filer)
- [Felsökning](#felsökning)
- [Avinstallation](#avinstallation)
- [Bidra](#bidra)
- [Licens](#licens)

## Funktioner

| Område | Vad du kan göra |
| --- | --- |
| Enheter | Listar USB- och Wi-Fi-enheter med modellnamn, uppdateras var 4:e sekund. Visar om en enhet väntar på godkännande eller är offline. |
| Spegling | Starta/stoppa `scrcpy` per enhet. Pågående spegling markeras med ▶. Flera enheter kan speglas samtidigt. |
| Rotation | Lås porträtt, lås landskap eller återställ autorotation – även under pågående spegling. |
| Verktyg | Skärmdump till bildmappen, `adb shell` i en terminal, omstart av adb-servern. |
| Wi-Fi | *Växla till Wi-Fi* från en USB-ansluten enhet, anslut till tidigare adresser eller en ny adress, eller parning via Androids **Trådlös felsökning**. |

## Krav

- Linux Mint / Cinnamon (ikonen använder `XApp.StatusIcon`). Andra skrivbord med StatusNotifier-stöd via
  `xapp-sn-watcher` bör fungera men är inte testade.
- Python 3 med PyGObject
- Paket: `adb`, `scrcpy`, `python3-gi`, `gir1.2-gtk-3.0`, `gir1.2-xapp-1.0`, `libnotify-bin`

## Installation

```bash
git clone https://github.com/aelmen/adb-tray.git
cd adb-tray
./install.sh --deps
```

`--deps` installerar paketen ovan med `apt` (kräver sudo). Utelämna flaggan om de redan finns.

Installationen

- kopierar programmet till `~/.local/bin/adb-tray`
- lägger till **ADB-enheter** i programmenyn
- startar programmet vid inloggning (hoppa över med `NO_AUTOSTART=1 ./install.sh`)
- startar ikonen direkt

Kör `./install.sh` igen efter `git pull` för att uppdatera.

## Kom igång

### Via USB

1. På enheten: **Inställningar → Om enheten → Programvaruinformation**, tryck sju gånger på
   *Versionsnummer* för att låsa upp utvecklaralternativ.
2. **Utvecklaralternativ → USB-felsökning** – slå på.
3. Anslut kabeln och tryck **Tillåt** i dialogen på enheten (bocka gärna i *Tillåt alltid*).
4. Enheten dyker upp i menyn. Välj **Spegla skärmen**.

### Via Wi-Fi, helt utan kabel

1. **Utvecklaralternativ → Trådlös felsökning** – slå på och välj *Para ihop enhet med parningskod*.
2. I menyn: **Anslut via Wi-Fi → Para ihop (trådlös felsökning)…** och fyll i parningsadress, kod och
   (valfritt) anslutningsadressen som visas under *Trådlös felsökning*.

### Via Wi-Fi efter USB

Välj **Växla till Wi-Fi** på en USB-ansluten enhet. Adressen sparas och kan väljas under
*Anslut via Wi-Fi* nästa gång. Läget gäller tills enheten startas om.

## Konfiguration och filer

| Sökväg | Innehåll |
| --- | --- |
| `~/.local/bin/adb-tray` | Programmet |
| `~/.config/adb-tray/hosts.json` | Senast använda Wi-Fi-adresser (max 10) |
| `~/.config/adb-tray/scrcpy-*.log` | Utdata från senaste speglingen per enhet |
| `~/.config/autostart/adb-tray.desktop` | Autostart vid inloggning |

Standardflaggorna för `scrcpy` (`-m 1600 --stay-awake`, plus `-b 6M` över Wi-Fi) finns i `SCRCPY_OPTS`
överst i `adb-tray.py`.

## Felsökning

| Symptom | Åtgärd |
| --- | --- |
| Ingen ikon syns | Kontrollera att *Xapp Status Applet* finns i panelen. Starta `adb-tray` i en terminal och läs utskriften. |
| Enheten visas som *godkänn på enheten* | Tryck **Tillåt** i dialogen på enheten. Syns ingen dialog: välj *Återkalla USB-felsökningsbehörigheter* i utvecklaralternativen och anslut igen. |
| Speglingen stängs direkt | Läs `~/.config/adb-tray/scrcpy-*.log`. Vissa enheter klarar inte full upplösning – sänk `-m` i `SCRCPY_OPTS`. |
| Wi-Fi-anslutningen misslyckas | Enheten har troligen startats om. Anslut via USB och välj *Växla till Wi-Fi* igen, eller använd parning. |
| Allt verkar hänga | Välj **Starta om adb-server** i menyn. |
| `Failed to load module "xapp-gtk3-module"` | Ofarligt meddelande, kan ignoreras. |

## Avinstallation

```bash
./uninstall.sh
```

Inställningarna i `~/.config/adb-tray/` lämnas kvar.

## Bidra

Bidrag tas emot via pull requests. Läs [CONTRIBUTING.md](CONTRIBUTING.md) först.
Säkerhetsproblem rapporteras enligt [SECURITY.md](SECURITY.md).

## Licens

[MIT](LICENSE) © Anders Elmén
