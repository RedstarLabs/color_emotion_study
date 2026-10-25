# Deployment auf Debian 12

Dieses Dokument beschreibt einen reproduzierbaren Zielaufbau. Es führt keine
Installation oder Migration aus und enthält keine echten Geheimnisse.

## Voraussetzungen

- Debian 12 mit aktuellen Sicherheitsupdates
- eigener DNS-Name und verwaltetes TLS-Zertifikat
- dedizierter Benutzer `rgb-website`
- privates Datenverzeichnis `/var/lib/rgb-website` mit Modus `0700`
- Python 3.14.8, verifiziert aus einer vertrauenswürdigen Quelle
- `uv` in einer kontrollierten Installationsquelle

Die Version ist in [.python-version](../.python-version) festgelegt. Vor der
Installation müssen Herkunft, Hash/Signatur, Patchstand und regelmäßige
Sicherheitsupdates für Python 3.14 auf Debian 12 durch den Betreiber
festgelegt werden. Das Repository behauptet nicht, dass Debian 12 diese
Version im Standardsystem bereitstellt.

## Installation

```bash
sudo useradd --system --home /opt/rgb-website --shell /usr/sbin/nologin rgb-website
sudo install -d -o rgb-website -g rgb-website -m 0750 /opt/rgb-website
sudo install -d -o rgb-website -g rgb-website -m 0700 /var/lib/rgb-website
sudo install -d -o root -g rgb-website -m 0750 /etc/rgb-website
uv sync --locked --no-dev
```

Die Produktionsdatei `/etc/rgb-website/rgb-website.env` muss root gehören,
der Gruppe `rgb-website` gehören und Modus `0640` haben. Sie enthält einen
zufällig erzeugten `ADMIN_API_TOKEN`, eine absolute `DATABASE_URL` und
`APP_ENV=production`. Der Token darf nicht in Git, HTML, JavaScript oder URLs
stehen.

Für die optionale Abschlussbenachrichtigung sind zusätzlich
`NOTIFICATION_ENABLED=true`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_FROM`,
`NOTIFICATION_OPERATOR_RECIPIENT` und
`NOTIFICATION_TECHNICAL_RECIPIENT` zu setzen. Je nach Mailserver werden
außerdem `SMTP_USERNAME` und `SMTP_PASSWORD`, sowie genau eine passende
Kombination aus `SMTP_USE_SSL` und `SMTP_STARTTLS` benötigt. Das
Verbindungs-Timeout wird mit `SMTP_TIMEOUT` begrenzt. Die Zugangsdaten und
Empfängeradressen dürfen ausschließlich in dieser geschützten Datei liegen.
Die Benachrichtigung ist standardmäßig deaktiviert; bei unvollständiger
Konfiguration bleibt die Studienfunktion aktiv und protokolliert den
übersprungenen Versand.

Die Anwendung lehnt in Produktion außerdem einen nichtlokalen `APP_HOST` und
Admin-Tokens mit weniger als 32 Zeichen ab. Ein separates Secret-Management
und eine dokumentierte Rotation bleiben erforderlich.

Vor dem Start muss die gesicherte Datenbank kontrolliert auf Revision
`0005_session_gender` migriert und anschließend `/ready` geprüft werden.
Diese Migration wurde durch den Agenten nicht auf der lokalen Datenbank
ausgeführt.

## systemd und Nginx

[rgb-website.service](../deploy/systemd/rgb-website.service) erzwingt einen
nichtprivilegierten Benutzer, ein festes Arbeitsverzeichnis, lokale Bindung,
restriktive Schreibpfade und keinen Server-Header. Vor Installation:

```bash
systemd-analyze verify deploy/systemd/rgb-website.service
```

[rgb-website.conf](../deploy/nginx/rgb-website.conf) enthält HTTP-zu-HTTPS-
Redirect, TLS-Parameter, Request-Größenlimits, Rate-Limits, Sicherheitsheader
und lokale Weiterleitung. `example.invalid` und die Zertifikatspfade müssen
durch die Betreiber-Domain ersetzt werden. Danach ist mit der installierten
Nginx-Version zu prüfen:

```bash
sudo nginx -t
```

Die direkte Erreichbarkeit von Port 8000 muss durch Firewall und Binding
verhindert werden. Nginx- und Provider-Logs sowie deren Aufbewahrung sind
separat zu konfigurieren und datenschutzrechtlich zu bewerten.

## Backup und Restore

[backup.sh](../deploy/backup.sh) erzeugt mit SQLite `.backup` eine konsistente
Kopie und verwendet restriktive Rechte. [restore.sh](../deploy/restore.sh)
verlangt zwei absolute Pfade, eine vorhandene reguläre Quelldatei und ein
bereits vorhandenes Zielverzeichnis. Symbolische Links als Quelle oder Ziel
werden abgelehnt; ein vorhandenes Ziel wird niemals überschrieben. Quelle und
Ziel müssen verschieden sein.

Das Skript akzeptiert die Quelldatenbank nur, wenn `PRAGMA integrity_check;`
mit dem Ergebnis `ok` und ohne weitere Ausgabe endet. Es erstellt die Kopie
zuerst als 0600-Datei mit zufälligem Namen im Zielverzeichnis, prüft auch
diese temporäre Datei und verknüpft sie anschließend mit `ln` atomar am
Zielpfad. Dadurch bleibt bei einem fehlgeschlagenen Restore keine
unvollständige Zieldatei zurück; konkurrierendes Erzeugen des Zielpfads wird
von `ln` abgewiesen. Das Skript setzt `sqlite3`, `realpath`, `mktemp`, `ln`
und POSIX-Dateirechte voraus. Die Pfade dürfen außerdem kein einfaches
Anführungszeichen enthalten, weil der verwendete SQLite-Dot-Befehl den
temporären Dateinamen quotiert.

Beispiele für erwartete Ablehnungen sind `BACKUP_DB must be an existing regular
file`, `TARGET_DB already exists`, `BACKUP_DB and TARGET_DB must be different
files`, `BACKUP_DB failed integrity_check` und `Database restore failed`.
Beide Skripte sind nur mit temporären oder freigegebenen Zielkopien
auszuführen; der Agent hat keine Produktionsdatenbank verändert.

Vor Livegang sind mindestens ein verschlüsseltes Backup, ein dokumentierter
Aufbewahrungszeitraum, ein Restore-Test und die Rechteprüfung zu
protokollieren.

## Manueller Löschablauf

Die Anwendung implementiert keine automatische Datenbanklöschung und keinen
systemd-Timer. Die Betreiberin führt die Löschung manuell in einem
freigegebenen Wartungsfenster durch. Die Rohdaten dürfen nur so lange wie
nötig gespeichert werden und müssen spätestens zwölf Monate nach ihrer
Erhebung gelöscht werden. Eine längere Speicherung ist nach der bestätigten
Betreiberentscheidung nicht vorgesehen.

Vor jeder planmäßigen Löschung oder individuell geprüften Löschanfrage:

1. Frist, Anfrage und den rechtlichen Prüfstatus feststellen.
2. Betroffene Rohdatensätze und Sitzungen in einer isolierten Arbeitskopie
   identifizieren; keine ungeprüften Löschbefehle auf der Produktionsdatenbank
   ausführen.
3. Erforderliche CSV-Exporte, Backups und technische Logs identifizieren und
   ihre eigene Aufbewahrung und Löschung berücksichtigen.
4. Ein freigegebenes Backup beziehungsweise eine Wiederherstellungsoption
   prüfen, bevor Rohdaten gelöscht werden.
5. Die Löschung in den vorgesehenen Datenbeständen durchführen, soweit sie
   rechtlich und technisch umsetzbar ist.
6. Nachkontrollieren, dass die vorgesehenen Rohdaten nicht mehr vorhanden
   oder für die weitere Verarbeitung gesperrt sind.
7. Ergebnis, Datum, Umfang und offene Einschränkungen datensparsam
   dokumentieren; keine Teilnehmerdaten in das Löschprotokoll übernehmen.

Dieser Ablauf ist eine Betreiber- und Betriebsanweisung, keine implementierte
Anwendungsfunktion. Die konkrete SQL-/Dateioperation, der Zugriff auf
Produktionsdatenbank und Backups sowie die Löschung von Nginx-, Uvicorn-,
systemd- und Provider-Logs müssen vor dem ersten produktiven Einsatz
freigegeben werden. Der Agent hat keine produktiven Daten gelöscht.
