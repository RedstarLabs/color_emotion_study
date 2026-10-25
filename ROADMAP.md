# ColorEmotionStudy – Roadmap

## Ziel

Entwicklung einer öffentlich erreichbaren, mobiloptimierten Web-App zur Erhebung von Farb-Emotions-Zuordnungen mit sofortiger Speicherung, sicherem CSV-Export und einer datensparsamen Architektur.

Die Entwicklung erfolgt inkrementell. Jede Phase wird erst abgeschlossen, wenn ihre Akzeptanzkriterien erfüllt und automatisiert getestet sind.

## Phase 0 – Projektgrundlage und Spezifikation

### Aufgaben

- [ ] GitHub-Repository anlegen
- [ ] README.md und ROADMAP.md einchecken
- [x] Python-Projekt mit `pyproject.toml` einrichten
- [x] uv als Paket- und Umgebungsverwaltung verwenden
- [x] Ruff für Linting und Formatierung konfigurieren
- [x] pytest konfigurieren
- [x] `.gitignore` und `.env.example` erstellen
- [x] Architektur in `docs/ARCHITECTURE.md` dokumentieren
- [x] Datenschema und CSV-Format in `docs/DATA_DICTIONARY.md` festlegen
- [x] Vorläufige Datenschutzanforderungen in `docs/PRIVACY.md` festhalten
- [x] Bedrohungsmodell in `docs/THREAT_MODEL.md` erstellen

### Akzeptanzkriterien

- Die Entwicklungsumgebung lässt sich anhand der Dokumentation reproduzieren.
- Geheimnisse und lokale Datenbankdateien werden nicht versioniert.
- Linting und ein minimaler Testlauf funktionieren.
- Technische Entscheidungen sind dokumentiert.

## Phase 1 – Minimales Backend und Datenbank

### Aufgaben

- [x] FastAPI-Anwendung erstellen
- [x] Konfiguration über Umgebungsvariablen einführen
- [x] SQLAlchemy einrichten
- [x] SQLite für lokale Entwicklung konfigurieren
- [x] PostgreSQL-Konfiguration für Produktion vorsehen
- [x] Datenbankmigrationen mit Alembic einrichten
- [x] Datenmodell für Umfragesitzungen erstellen
- [x] Datenmodell für einzelne Antworten erstellen
- [x] Datenbankzugriffe über Repository-Funktionen kapseln
- [x] Health-Endpoint ohne sensible Informationen implementieren

### Akzeptanzkriterien

- [x] Die Anwendung startet lokal.
- [x] Datenbankmigrationen lassen sich anwenden und nachvollziehen.
- [x] Sitzungen und Antworten können gespeichert und gelesen werden.
- [x] Fehlerhafte Daten werden nicht gespeichert.
- [x] Datenbankzugänge sind konfigurierbar und nicht im Quellcode hinterlegt.

## Phase 2 – Versuchslogik und Farbzufall

### Aufgaben

- [x] Sieben Emotionskategorien zentral definieren
- [x] RGB-Datentyp und Wertebereich von 0 bis 255 validieren
- [x] Strategie zur Farbauswahl implementieren
- [x] Genau 10 Farben pro neuer Sitzung erzeugen; bestehende 15er-Sitzungen
  bleiben fortsetzbar.
- [x] Zufallsstrategie und Versuchsparameter versionieren
- [x] Farbwerte und Reihenfolge für jede Sitzung festhalten
- [x] Festlegen, ob identische Farben innerhalb einer Sitzung ausgeschlossen werden
- [x] Festlegen, ob Teilnehmende dieselbe Farbpalette erhalten oder vollständig unabhängige Zufallsfarben
- [ ] Verhalten bei Abbruch und Wiederaufnahme spezifizieren

### Akzeptanzkriterien

- [x] Jede neue Sitzung besitzt genau 15 geplante Durchgänge.
- [x] Jeder RGB-Wert ist gültig.
- [x] Die Reihenfolge lässt sich aus den gespeicherten Daten rekonstruieren.
- [x] Es gibt keine unbemerkte Änderung der Versuchsdefinition während einer Sitzung.
- [x] Die Zufallslogik ist unabhängig von der Darstellungsschicht testbar.

### Wissenschaftlicher Hinweis

Eine zufällige Auswahl aus einer festen Palette und eine Erzeugung zufälliger RGB-Werte sind unterschiedliche Versuchsdesigns. Die Entscheidung muss vor Beginn der Datenerhebung getroffen und dokumentiert werden.

## Phase 3 – Responsive Umfrageoberfläche

### Aufgaben

- [x] Start- und Informationsseite erstellen
- [x] Große, gut sichtbare Farbanzeige implementieren
- [x] Sieben gut bedienbare Emotionsbuttons erstellen
- [x] Fortschrittsanzeige anhand des gespeicherten Sitzungs-Snapshots
  implementieren
- [x] Darstellung für Smartphones und Laptops optimieren
- [x] Tastaturbedienung und zugängliche Beschriftungen berücksichtigen
- [x] Ladezustand während der Speicherung anzeigen
- [x] Doppelte Klicks und Mehrfachübermittlungen verhindern
- [x] Abschlussseite erstellen
- [x] Fehler- und Wiederholungszustände gestalten

### Akzeptanzkriterien

- [x] Auf kleinen und großen Bildschirmen ist die Umfrage benutzbar.
- [x] Es wird jeweils genau eine Farbe angezeigt.
- [x] Eine Antwort kann nicht versehentlich mehrfach gespeichert werden.
- [x] Die nächste Farbe erscheint erst nach bestätigter Speicherung.
- [x] Ein Netzwerkfehler führt nicht zu einem stillschweigenden Verlust der Antwort.

## Phase 4 – Sofortige Speicherung und Sitzungsverwaltung

### Aufgaben

- [x] Endpunkt zum Starten einer Umfragesitzung erstellen
- [x] Antwort-Endpunkt erstellen
- [x] Eingaben mit Pydantic validieren
- [x] Erlaubte Emotionen serverseitig prüfen
- [x] Durchgangsnummer und RGB-Werte serverseitig überprüfen
- [x] Idempotente Speicherung zur Vermeidung doppelter Antworten implementieren
- [x] Sitzungszustand und erlaubte Übergänge definieren
- [ ] Unterbrochene Sitzungen robust behandeln
- [x] Transaktionen und konsistente Fehlerbehandlung implementieren

### Akzeptanzkriterien

- Jede erfolgreich bestätigte Antwort ist dauerhaft in der Datenbank gespeichert.
- Unzulässige oder nachträglich manipulierte Antworten werden abgelehnt.
- Wiederholte Requests erzeugen keine ungewollten doppelten Datensätze.
- Antworten lassen sich eindeutig einer Sitzung und einem Durchgang zuordnen.
- Der Verlust einer HTTP-Antwort führt nicht automatisch zu einer doppelten Speicherung.

## Phase 5 – CSV-Export und Datenqualität

### Aufgaben

- [x] Exportservice implementieren
- [x] CSV-Spalten verbindlich definieren
- [x] UTF-8 und korrekte Behandlung von Umlauten sicherstellen
- [x] Eine Zeile pro Antwort exportieren
- [x] Sitzungskennung, RGB-Werte, Emotion und Versuchsreihenfolge exportieren
- [x] Export vor unberechtigtem Zugriff schützen
- [x] Export mit pandas-kompatibler UTF-8-CSV-Struktur prüfen
- [x] Unvollständige und ausdrücklich abgebrochene Sitzungen dokumentieren
- [x] Dokumentation für wissenschaftliche Auswertungen erstellen

### Akzeptanzkriterien

- Der Export enthält nur die vorgesehenen Spalten.
- RGB-Werte stimmen mit den tatsächlich gezeigten Farben überein.
- Antworten werden nicht stillschweigend ausgelassen.
- Unvollständige Sitzungen sind erkennbar.
- Der Export funktioniert mit pandas und anderen üblichen CSV-Werkzeugen.
- Die Exportdatei ist nicht öffentlich abrufbar.

Phase 5 ergänzt die serverseitige Statuskonsistenzprüfung, das explizite
Abbrechen unvollständiger Sitzungen und die Wiederherstellung nach einem
Netzwerkfehler durch erneuten Statusabruf ohne Browser-Persistenz.

## Phase 6 – Administration und Zugriffsschutz

### Aufgaben

- [x] Separaten Administrationsbereich implementieren
- [x] Sichere Authentifizierung auswählen und umsetzen
- [x] Administratorzugriffe auf Exportfunktionen begrenzen
- [ ] Sichere Session- beziehungsweise Token-Verwaltung festlegen
- [ ] Schutz gegen Brute-Force-Versuche einrichten
- [ ] Rate-Limiting für öffentliche Endpunkte implementieren
- [ ] Sichere Cookie-Einstellungen festlegen, sofern Cookies benötigt werden
- [ ] CSRF-Schutz für relevante authentifizierte Aktionen prüfen
- [ ] Sicherheitsrelevante Ereignisse ohne unnötige personenbezogene Daten protokollieren

### Akzeptanzkriterien

- Öffentliche Nutzer können keine Datenbankabfragen oder Exporte administrativ ausführen.
- Administratorzugänge sind nicht fest im Quellcode hinterlegt.
- Unberechtigte Anfragen erhalten angemessene Fehlerantworten.
- Geheimnisse werden nicht in Logs oder HTTP-Fehlern offengelegt.
- Sicherheitsmaßnahmen sind getestet und dokumentiert.

## Phase 7 – Datenschutz und rechtliche Vorbereitung

### Aufgaben

- [ ] Zweck und Umfang der Datenerhebung dokumentieren
- [ ] Verantwortliche Stelle und Kontaktmöglichkeiten festlegen
- [ ] Rechtsgrundlage der Verarbeitung klären
- [ ] Datenschutzhinweise erstellen
- [ ] Erforderlichkeit und Gestaltung einer Einwilligung prüfen
- [ ] Verfahren für Widerruf und Löschanfragen festlegen, soweit anwendbar
- [ ] Löschfristen für Antworten, Logs und Backups definieren
- [ ] Hosting-Anbieter und Auftragsverarbeitung prüfen
- [ ] Hosting-Logs und mögliche Drittlandtransfers untersuchen
- [ ] HTTPS und sichere Produktionskonfiguration sicherstellen
- [ ] Notwendigkeit einer Datenschutz-Folgenabschätzung oder Ethikprüfung beurteilen
- [ ] Datenschutzprüfung vor dem Livegang dokumentieren

### Akzeptanzkriterien

- Vor Beginn der Erhebung werden die erforderlichen Informationen angezeigt.
- Die tatsächliche Datenverarbeitung entspricht den veröffentlichten Hinweisen.
- Es werden keine unnötigen personenbezogenen Daten erhoben.
- Hosting und Protokollierung sind dokumentiert.
- Datenzugriff, Löschung und Backups sind geregelt.
- Es wird keine ungeprüfte Behauptung vollständiger Anonymität oder garantierter DSGVO-Konformität aufgestellt.

## Phase 8 – Tests, Qualität und Robustheit

### Aufgaben

- [ ] Unit-Tests für Zufallslogik und Validierung
- [ ] Integrationstests für Datenbankzugriffe
- [ ] API-Tests für gültige und ungültige Antworten
- [ ] Tests gegen doppelte Übermittlungen
- [ ] Tests für unterbrochene Verbindungen
- [ ] CSV-Exporttests
- [ ] Berechtigungstests für Administration
- [ ] Sicherheitsprüfungen relevanter Endpunkte
- [ ] Tests mit mehreren parallelen Sitzungen
- [ ] Automatisierte CI-Pipeline mit GitHub Actions
- [ ] Dokumentation der Testabdeckung und bekannter Einschränkungen

### Akzeptanzkriterien

- Alle Tests laufen erfolgreich.
- Kritische Pfade sind durch automatisierte Tests abgesichert.
- Ein sauberer Checkout kann getestet werden.
- CI schlägt bei Fehlern fehl und meldet diese nachvollziehbar.

## Phase 9 – Deployment und Pilotbetrieb

### Aufgaben

- [ ] Geeigneten Hosting-Anbieter auswählen
- [ ] Hosting- und Datenschutzbedingungen prüfen
- [ ] Docker-Konfiguration erstellen
- [ ] Produktionskonfiguration dokumentieren
- [ ] TLS-Zertifikat und HTTPS einrichten
- [ ] Datenbank und Backups absichern
- [ ] Zugriff auf Umgebungsvariablen und Geheimnisse beschränken
- [ ] Sicherheitsupdates und Wartungsprozess festlegen
- [ ] Pilotumfrage mit synthetischen beziehungsweise freiwilligen Testdaten durchführen
- [ ] Smartphone-, Laptop- und Netzwerkfehler testen
- [ ] CSV-Export und Wiederherstellung aus Backup prüfen

### Akzeptanzkriterien

- Die App ist über HTTPS erreichbar.
- Der Administrationsbereich ist geschützt.
- Backups und Wiederherstellung sind überprüft.
- Datenschutzinformationen und tatsächlicher Betrieb stimmen überein.
- Es werden keine echten Teilnehmenden eingeladen, bevor die offenen Datenschutz- und Sicherheitsfragen geklärt sind.

## Phase 10 – Wissenschaftliche Auswertung

### Aufgaben

- [ ] Dokumentation des finalen Versuchsdesigns abschließen
- [ ] CSV-Daten mit pandas einlesen
- [ ] Datenqualität und unvollständige Sitzungen prüfen
- [ ] Verteilung der Emotionsantworten untersuchen
- [ ] RGB-Werte und Emotionen für ML-Experimente aufbereiten
- [ ] Geeignete Validierungsstrategie für das Modell festlegen
- [ ] Datenversion und Modellparameter dokumentieren
- [ ] Explorative Ergebnisse reproduzierbar speichern

### Akzeptanzkriterien

- Die Auswertung ist reproduzierbar.
- Trainings- und Testdaten werden methodisch sinnvoll getrennt.
- Die Zahl der Teilnehmenden und Antworten wird transparent ausgewiesen.
- Schlussfolgerungen berücksichtigen Stichprobengröße und mögliche Verzerrungen.

## Arbeitsweise mit GitHub Copilot

Copilot soll phasenweise arbeiten und nicht die gesamte Roadmap in einem einzigen Schritt implementieren.

Für jede Phase gilt:

1. Relevante Dateien und bestehende Architektur untersuchen.
2. Einen kurzen Implementierungsplan vorlegen.
3. Änderungen in kleinen, zusammenhängenden Schritten durchführen.
4. Automatisierte Tests ergänzen.
5. Tests, Linting und Typprüfungen ausführen, soweit konfiguriert.
6. Ergebnisse und bekannte Einschränkungen dokumentieren.
7. README.md und ROADMAP.md aktualisieren.
8. Änderungen erst nach Prüfung committen.

Copilot darf keine Datenschutzanforderungen eigenständig abschwächen und keine Zugangsdaten, echten Forschungsdaten oder personenbezogenen Informationen in Codebeispiele oder Logs übernehmen.

## Nicht-Ziele der ersten Version

- Keine native Android- oder iOS-App
- Keine Registrierung für Teilnehmende
- Keine Werbe- oder Trackingfunktionen
- Keine automatische Veröffentlichung von Forschungsdaten
- Keine komplexen Benutzerrollen außerhalb der erforderlichen Administration
- Keine ML-Modellinferenz innerhalb der Umfrage
- Keine unnötigen externen Dienste

## Abschlusskriterium für Version 1.0

Die erste produktive Version gilt erst als fertig, wenn eine Person die Umfrage mobil oder am Laptop vollständig durchführen kann, jede Antwort zuverlässig gespeichert wird, der CSV-Export korrekt und geschützt funktioniert und die für den tatsächlichen Hosting-Betrieb erforderlichen Datenschutz- und Sicherheitsprüfungen abgeschlossen sind.
