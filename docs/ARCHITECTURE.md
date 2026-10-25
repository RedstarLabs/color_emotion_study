# Architektur

## Geltungsbereich

Dieses Dokument beschreibt die bis Phase 5 implementierte technische
Grundlage. Die Anwendung ist nicht für eine reale Erhebung freigegeben.

## Zielarchitektur und Schichten

- FastAPI stellt HTTP-Schnittstellen und statische Dateien bereit.
- Pydantic validiert externe Eingaben und Ausgaben.
- Die Service-Schicht implementiert Versuchsregeln und Transaktionen.
- Repositories kapseln den SQLAlchemy-Zugriff.
- Alembic verwaltet schemaändernde Migrationen.
- HTML, CSS und JavaScript bilden die schlanke Oberfläche ohne Tracking.
- Die Export-Schicht streamt CSV-Zeilen ohne temporäre Exportdatei.

SQLite dient der lokalen Entwicklung; PostgreSQL ist über `DATABASE_URL` für
den Produktivbetrieb konfigurierbar. Datenbankmodelle und Migrationen bilden RGB-Werte, Positionen, Antworten,
Status, Versuchslänge, Versuchsversion, freiwillige Geschlechtsangabe und
Zeitstempel ab.

## Versuchserzeugung

`experiment.py` erzeugt pro Durchgang jeden RGB-Kanal unabhängig und
gleichverteilt mit `secrets.randbelow(256)`. Die 10 erzeugten Farben
werden als `session_colors` gespeichert. Ihre IDs (`trial-1` usw.), Positionen
und RGB-Werte bleiben nach dem Start unverändert. Zufällige identische
RGB-Tripel sind zulässig; eine kanalweise Gleichverteilung garantiert keine
Gleichverteilung wahrgenommener Farben.

## API und Datenfluss

- `POST /api/experiments` startet immer einen Versuch mit 10 Farben und nimmt
  optional `gender` (`male`, `female`,
  `diverse`, `not_specified`) entgegen. Ohne Auswahl wird `not_specified`
  gespeichert. Zusätzlich müssen `age_confirmed`,
  `information_acknowledged` und `participation_consent` wahr sein; diese
  Startbestätigungen werden nicht gespeichert.
- `GET /api/experiments/{session_id}` liefert Status, Fortschritt und nur die
  nächste Farbe.
- `POST /api/experiments/{session_id}/responses` validiert und speichert eine
  Emotion für die aktuelle Farbe.
- `POST /api/experiments/{session_id}/abandon` beendet einen unvollständigen
  Versuch ausdrücklich als `abandoned`.
- `GET /api/admin/export` liefert nach `X-Admin-Token`-Authentifizierung den
  CSV-Export.
- `GET /health` ist ein einfacher Prozess-Liveness-Check. `GET /ready` prüft
  zusätzlich die Datenbankverbindung und den erwarteten Alembic-Stand
  `0005_session_gender`; der Reverse Proxy darf nur bereite Instanzen mit
  Forschungsverkehr versorgen.

Neue Sitzungen verwenden `random-rgb-2.0` und genau sieben Emotionen:
Wut, Angst, Freude, Traurigkeit, Überraschung, Verachtung und Ekel. Die
frühere Version `random-rgb-1.0` bleibt für historische Daten auswertbar;
dort können `Trauer` und `Vertrauen` unverändert vorkommen. RGB-Werte werden
nie aus Antwortdaten des Clients übernommen. Ein Versuch
wird nach seinem unveränderlichen `trial_count`-Snapshot abgeschlossen.
Doppelte Antworten werden zusätzlich durch Datenbank-Unique-Constraints
verhindert. Antworten und Statusänderung werden in einer Transaktion
gespeichert. Der Abschlussstatus wird nur bei genau `trial_count` Antworten
gesetzt; inkonsistente Status-/Antwortzahlen werden nicht als gültiger
Studienzustand ausgeliefert.

Netzwerkfehler nach einer Antwort lösen im Frontend einen erneuten
Statusabruf aus. Dadurch wird eine bereits gespeicherte Antwort erkannt,
ohne sie erneut zu senden. Wenn der Abruf ebenfalls fehlschlägt, bleibt die
aktuelle Auswahl zur Wiederholung sichtbar. Sitzungsdaten werden nicht in
`localStorage` oder `sessionStorage` gespeichert.

## Admin-Export

Das Admin-Token kommt ausschließlich aus `ADMIN_API_TOKEN` und wird mit
`secrets.compare_digest` verglichen. Fehlt es, bleibt der Export geschlossen.
Der Export ist UTF-8, sortiert nach Sitzung und Durchgang, verwendet
`Cache-Control: no-store` und schützt Textfelder mit führendem `=`, `+`, `-`
oder `@` durch ein Apostroph vor Spreadsheet-Formula-Injection.

Ein API-Token allein ersetzt keine sichere Produktionsbereitstellung:
HTTPS, restriktive Serverkonfiguration, Zugriffsschutz, Rate-Limiting und
angemessene Protokollierung bleiben erforderlich.

Für eine Produktionsumgebung mit SQLite muss `DATABASE_URL` einen absoluten
Pfad verwenden. Ein relativer SQLite-Pfad wird bei `APP_ENV=production`
abgelehnt, damit ein abweichendes Working Directory nicht versehentlich eine
neue leere Forschungsdatenbank erzeugt. Die Datenbank muss vor dem Start auf
den erwarteten Migrationsstand gebracht und der Readiness-Endpunkt geprüft
werden.

Der Zielbetrieb ist mit einem nichtprivilegierten systemd-Service und lokalem
Uvicorn-Binding in [DEPLOYMENT.md](DEPLOYMENT.md) beschrieben. Nginx übernimmt
TLS, HTTP-zu-HTTPS-Redirect, Größenlimits und vorgeschaltete Rate-Limits.

## Datenschutz- und Betriebsgrenzen

Teilnehmende benötigen kein Konto. Namen, E-Mail-Adressen, IP-Adressen und
weitere personenbezogene Daten werden nicht in der Forschungsdatenbank
gespeichert. Die tatsächlichen Hosting-, Logging-, Backup- und
Aufbewahrungsentscheidungen müssen vor dem Livegang festgelegt werden.

Ein Reload beendet die Sitzung im Browser nicht automatisch: Ohne gespeicherte
Sitzungskennung bleibt sie serverseitig `in_progress`, bis eine Antwort
eintrifft oder der Abbruch-Endpunkt verwendet wird. Eine automatische
Wiederaufnahme über Browser-Speicher ist bewusst nicht implementiert.
Offen bleiben insbesondere die wissenschaftliche Freigabe der
Zufallsstrategie, eine mögliche spätere Wiederaufnahme, Rate-Limiting,
Produktionshosting und die rechtliche Prüfung.
