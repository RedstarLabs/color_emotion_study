# ColorEmotionStudy

Eine datenschutzbewusste Web-App zur Untersuchung der Zuordnung von Farben und Emotionen.

## Projektziel

ColorEmotionStudy ist eine eigenständige Forschungsanwendung, mit der untersucht wird, welche Emotionen Menschen mit unterschiedlichen Farben verbinden.

Teilnehmende öffnen die Website über einen Link und beurteilen standardmäßig zehn, konfigurierbar fünfzehn, nacheinander angezeigte Farben. Jede Farbe wird durch unabhängig und gleichverteilt erzeugte RGB-Werte definiert. Die Teilnehmenden können vorab freiwillig eine Geschlechtsangabe machen und
wählen für jede Farbe genau eine von sieben vorgegebenen Emotionen aus:
Wut, Angst, Freude, Trauer, Überraschung, Verachtung oder Ekel.

Die Antworten werden unmittelbar gespeichert und können anschließend als CSV-Datei für statistische Analysen und Machine-Learning-Experimente exportiert werden.

Das Projekt ist für die eigenständige Forschung konzipiert und nicht von der Infrastruktur einer Universität abhängig.

## Kernfunktionen

- Öffentlich erreichbare Web-App
- Responsive Benutzeroberfläche für Smartphones, Tablets und Laptops
- Anzeige einer einzelnen Farbe pro Durchgang
- Kryptografisch unterstützte, kanalweise gleichverteilte RGB-Farben pro Umfragesitzung
- Konfigurierbare Versuchslänge von 10 oder 15 Durchgängen
- Speicherung der exakten RGB-Werte jeder gezeigten Farbe
- Sieben feste Emotionskategorien
- Genau eine Emotion pro Durchgang
- Automatische Speicherung jeder Antwort
- Fortschrittsanzeige während der Umfrage
- Fehlerbehandlung bei unterbrochener Verbindung
- Geschützter Administrationsbereich
- CSV-Export der erhobenen Daten
- Keine Registrierung für Teilnehmende
- Keine unnötigen personenbezogenen Daten
- Dokumentierte Datenschutz- und Sicherheitsmaßnahmen
- Automatisierte Tests und nachvollziehbare Releases

## Emotionskategorien und Versuchsversionen

Neue Sitzungen verwenden `random-rgb-2.0` mit:

1. Wut
2. Angst
3. Freude
4. Trauer
5. Überraschung
6. Verachtung
7. Ekel

`Vertrauen` wird in neuen Sitzungen nicht mehr angeboten oder akzeptiert.
Historische Sitzungen der Version `random-rgb-1.0` behalten Antworten mit
`Vertrauen` unverändert.

Die Geschlechtsangabe ist eine freiwillige Selbstauskunft mit den internen
Werten `male`, `female`, `diverse` und `not_specified`. Ohne Auswahl wird
`not_specified` gespeichert; daraus wird nicht automatisch auf das biologische
Geschlecht geschlossen.

## Technischer Stack

### Backend

- Python 3.14, sofern alle verwendeten Abhängigkeiten kompatibel sind
- FastAPI
- Pydantic zur Validierung
- SQLAlchemy 2.x für den Datenbankzugriff
- Alembic für Datenbankmigrationen
- SQLite für die lokale Entwicklung
- PostgreSQL als bevorzugte Datenbank für den öffentlichen Produktivbetrieb
- pytest für automatisierte Tests

### Frontend

- HTML
- CSS
- JavaScript
- Responsive Design
- Keine unnötigen externen JavaScript-Bibliotheken
- Keine Werbe- oder Tracking-Skripte

Die Anwendung soll zunächst als schlanke, serverseitig ausgelieferte Web-App implementiert werden. Ein separates Frontend-Framework ist nur einzuführen, wenn es einen nachweisbaren Vorteil bietet.

### Entwicklung und Betrieb

- Git und GitHub
- uv zur Verwaltung der Python-Umgebung und Abhängigkeiten
- Ruff für Linting und Formatierung
- GitHub Actions für automatisierte Tests
- Docker beziehungsweise Docker Compose für reproduzierbare lokale und serverseitige Umgebungen

## Grundlegender Ablauf

1. Eine Person öffnet die Website.
2. Die Informationsseite erläutert Zweck, Ablauf und Datenschutz.
3. Die Person beginnt freiwillig mit der Umfrage.
4. Das System erzeugt eine zufällige Sitzungskennung.
5. Die Anwendung erzeugt 10 oder 15 RGB-Farben nach der konfigurierten Zufallsstrategie und speichert sie dauerhaft.
6. Eine Farbe wird angezeigt.
7. Die Person wählt eine der sieben Emotionen.
8. Das Backend validiert und speichert die Antwort.
9. Erst nach bestätigter Speicherung wird die nächste Farbe angezeigt.
10. Nach der gespeicherten Anzahl erfolgreicher Antworten wird eine Abschlussseite angezeigt.
11. Ein berechtigter Administrator kann die Daten als CSV exportieren.

Ein unvollständiger Versuch kann ausdrücklich abgebrochen werden und erhält
den Status `abandoned`. Nach einem Reload wird keine Sitzungskennung im Browser
gespeichert; ein nicht explizit abgebrochener Versuch bleibt daher serverseitig
`in_progress` und wird im Export als unvollständig behandelt.

Die Gleichverteilung jedes RGB-Kanals über `0..255` ist keine Gleichverteilung
wahrgenommener Farben. Zufällige identische RGB-Tripel werden nicht nachträglich
entfernt.

## Datenmodell

Jede Antwort wird als eigener Datensatz gespeichert.

Vorgesehene Felder:

- `id`: interne technische Kennung
- `session_id`: zufällige Kennung der Umfragesitzung
- `trial_number`: Durchgang von 1 bis 10 oder 15
- `color_r`: Rotwert von 0 bis 255
- `color_g`: Grünwert von 0 bis 255
- `color_b`: Blauwert von 0 bis 255
- `emotion`: eine der sieben erlaubten Kategorien
- `color_order`: Position der Farbe innerhalb der Sitzung
- `experiment_version`: Version der Versuchsdefinition
- `trial_count`: unveränderlicher Snapshot der Versuchslänge (10 oder 15)
- `response_timestamp`: serverseitiger Zeitstempel; bei historischen Antworten
  kann er fehlen

Ein Erstellungszeitpunkt darf nur aufgenommen werden, wenn er für einen dokumentierten Zweck benötigt wird.

Die endgültige Datenstruktur ist in der technischen Dokumentation festzulegen.

## Datenschutz und Sicherheit

Datenschutz ist eine grundlegende Architekturvoraussetzung und kein nachträglicher Zusatz.

- Keine Namen, E-Mail-Adressen oder Matrikelnummern erheben.
- Keine Benutzerkonten für Teilnehmende verlangen.
- Keine unnötigen Cookies, Tracking-Pixel oder Analyseanbieter einsetzen.
- Keine IP-Adressen in der wissenschaftlichen Datenbank speichern.
- Server- und Proxy-Logs auf notwendige Informationen begrenzen.
- Hosting-Anbieter, Protokollierung, Aufbewahrung und mögliche Drittlandtransfers prüfen.
- HTTPS für den öffentlichen Betrieb verwenden.
- Datenbankzugriffe auf das Backend beschränken.
- Den Administrationsbereich mit sicherer Authentifizierung schützen.
- CSV-Exporte dürfen nicht öffentlich abrufbar sein.
- Zugangsdaten und Geheimnisse niemals im Repository speichern.
- Backups und Löschfristen dokumentieren.
- Datenschutzinformationen vor Beginn der Erhebung bereitstellen.
- Rechtsgrundlage, Verantwortlichkeit und gegebenenfalls Einwilligungsprozess vor der Veröffentlichung klären.

Die Anwendung darf nicht als DSGVO-konform bezeichnet werden, bevor die tatsächliche Bereitstellung, Datenflüsse und rechtlichen Anforderungen geprüft wurden.

## CSV-Export

Der CSV-Export muss folgende Anforderungen erfüllen:

- UTF-8-Kodierung
- Eine Zeile pro Antwort
- Eindeutige Spaltennamen
- Korrekte Behandlung von Umlauten
- Dokumentierte Reihenfolge und Datentypen
- Exakte RGB-Werte
- Keine unnötigen personenbezogenen Daten
- Export nur nach erfolgreicher Administrator-Authentifizierung

Der CSV-Export enthält pro gespeicherter Antwort die dokumentierte Spaltenfolge
und verwendet UTF-8 mit CRLF-Zeilenenden. Textfelder mit führendem `=`, `+`, `-`
oder `@` erhalten ein Apostroph, damit Tabellenprogramme sie nicht als Formel
ausführen. Unvollständige Sitzungen enthalten nur tatsächlich gespeicherte
Antworten.

Die CSV-Datei muss direkt mit Python und pandas verarbeitet werden können.

Beispiel:

```csv
session_id,trial_number,color_r,color_g,color_b,emotion,color_order,experiment_version
example-session,1,217,75,101,Freude,1,1.0
example-session,2,42,130,190,Trauer,2,1.0
```

Die Beispieldaten sind synthetisch und dürfen nicht als echte Forschungsergebnisse interpretiert werden.

## Projektstruktur

```text
ColorEmotionStudy/
├── README.md
├── ROADMAP.md
├── CONTRIBUTING.md
├── .gitignore
├── .env.example
├── pyproject.toml
├── compose.yaml
├── Dockerfile
├── src/
│   └── coloremotionstudy/
│       ├── main.py
│       ├── config.py
│       ├── api/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       ├── repositories/
│       ├── database/
│       ├── security/
│       ├── export/
│       ├── templates/
│       └── static/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── security/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_DICTIONARY.md
│   ├── PRIVACY.md
│   ├── THREAT_MODEL.md
│   └── DEPLOYMENT.md
└── .github/
    └── workflows/
        └── tests.yml
```

Die Struktur ist ein Zielbild. Sie soll schrittweise aufgebaut und nicht vollständig als leeres Gerüst vorab erzeugt werden.

## Qualitätsanforderungen

- Geschäftliche Logik von HTTP-Routen trennen.
- Datenbankzugriffe zentral kapseln.
- Eingaben sowohl syntaktisch als auch fachlich validieren.
- Keine geheimen Schlüssel in Quellcode oder Logs ausgeben.
- Tests für gültige und ungültige Antworten schreiben.
- Fehler dürfen nicht zu stillschweigendem Datenverlust führen.
- Änderungen am Datenmodell über Migrationen verwalten.
- Dokumentation zusammen mit der Implementierung aktualisieren.
- Keine unnötige Komplexität oder nicht benötigten Abhängigkeiten einführen.

## Entwicklungsprinzip

Das Projekt wird anhand der Phasen in `ROADMAP.md` umgesetzt.

Jede Phase muss überprüfbare Akzeptanzkriterien erfüllen. Änderungen erfolgen in kleinen, nachvollziehbaren Schritten. GitHub Copilot soll vorhandenen Code zunächst untersuchen, bestehende Konventionen beachten und vor größeren Architekturänderungen einen Vorschlag machen.

## Status

Projektplanung. Die Anwendung ist noch nicht für eine reale Datenerhebung freigegeben.

Der öffentliche Betrieb beginnt erst nach erfolgreichen Funktionstests, Sicherheitsprüfungen und einer Prüfung des Datenschutzkonzepts.
