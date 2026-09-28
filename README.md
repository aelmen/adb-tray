# adb-tray

En ikon i systemfältet (Linux Mint / Cinnamon) för Android-enheter via `adb`, med skärmspegling via [scrcpy](https://github.com/Genymobile/scrcpy).

## Funktioner

- Listar anslutna enheter (USB och Wi-Fi) och uppdateras automatiskt
- Per enhet: spegla skärmen / stoppa spegling, lås porträtt/landskap, autorotation,
  skärmdump (sparas i Bilder), öppna `adb shell`, växla USB → Wi-Fi, koppla från
- Anslut via Wi-Fi till tidigare använda adresser eller ny adress
- Parning med Androids *Trådlös felsökning* (IP:port + kod)
- Starta om adb-servern

## Krav

- Cinnamon (XApp.StatusIcon). Andra skrivbord med StatusNotifier-stöd via `xapp-sn-watcher` bör fungera.
- `adb`, `scrcpy`, `python3-gi`, `gir1.2-gtk-3.0`, `gir1.2-xapp-1.0`, `libnotify-bin`

## Installation

```bash
git clone https://github.com/aelmen/adb-tray.git
cd adb-tray
./install.sh --deps     # --deps installerar beroenden med apt (kräver sudo)
```

Programmet installeras i `~/.local/bin/adb-tray`, läggs i menyn som **ADB-enheter** och startas vid inloggning.
Sätt `NO_AUTOSTART=1` för att hoppa över autostart. Avinstallera med `./uninstall.sh`.

## Använd

1. Aktivera **USB-felsökning** i utvecklaralternativen på enheten och anslut med kabel.
2. Godkänn dialogen på enheten. Enheten dyker upp i menyn.
3. Välj **Växla till Wi-Fi** för att fortsätta utan kabel (gäller tills enheten startas om),
   eller använd **Para ihop (trådlös felsökning)** för att ansluta helt utan kabel.

Inställningar och loggar ligger i `~/.config/adb-tray/`.

## Licens

MIT
