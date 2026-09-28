# Säkerhetspolicy

## Versioner som stöds

Endast senaste versionen på `main` får säkerhetsrättningar.

## Rapportera en sårbarhet

Rapportera **inte** säkerhetsproblem som öppna ärenden eller pull requests.

Använd i stället GitHubs privata rapportering: **Security → Report a vulnerability** i repot.
Beskriv problemet, hur det kan återskapas och vilken påverkan du ser.

Du får en bekräftelse inom en vecka. När en rättning finns publiceras den tillsammans med ett
säkerhetsmeddelande, och du krediteras om du vill.

## Omfattning

adb-tray kör `adb` och `scrcpy` med dina användarrättigheter och ansluter till de adresser du anger.
Relevanta problem är till exempel:

- kommandoinjektion via enhetsnamn, serienummer eller adresser
- att filer skrivs utanför `~/.config/adb-tray/` eller bildmappen
- att installationsskripten gör något annat än det som dokumenteras

Säkerheten i själva `adb`-protokollet och i `scrcpy` hanteras av respektive projekt.
