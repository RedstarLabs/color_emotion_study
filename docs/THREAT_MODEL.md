# Bedrohungsmodell

## Schutzgüter

- Vertraulichkeit und Integrität der Forschungsantworten.
- Verfügbarkeit und korrekte Reihenfolge der Versuchsdurchführung.
- Schutz des Admin-Tokens und der CSV-Exporte.
- Nachvollziehbarkeit von RGB-Snapshots und Datenformat.

## Bedrohungen und Gegenmaßnahmen

| Bedrohung | Gegenmaßnahme |
| --- | --- |
| Unberechtigter Export | `X-Admin-Token`, sichere Vergleichsfunktion, kein Export bei fehlender Konfiguration. |
| Token-Leak in URL, Logs oder Daten | Header statt URL; keine Tokenwerte in Antworten oder Exportzeilen; Token nur im Seitenspeicher. |
| Spreadsheet-Formula-Injection | Führende `=`, `+`, `-`, `@` werden mit Apostroph escaped. |
| Manipulierte RGB- oder Antwortdaten | Browser ist nicht vertrauenswürdig; RGB kommt nur aus `session_colors`, Schemas und DB-Constraints validieren Werte. |
| Doppelübermittlung | Statusprüfung, aktuelle Farbe, Unique-Constraints und Transaktion. |
| Antwort verloren nach Netzwerkfehler | Nach einem fehlgeschlagenen Submit wird der Sitzungsstatus erneut abgerufen; ein bereits gespeicherter Fortschritt wird nicht erneut gesendet. |
| Unvollständiger Export | Exportiert jede gespeicherte Antwort; fehlende Antworten werden nicht fingiert. |
| Verlust oder Änderung der Reihenfolge | RGB, Position und Versuchslänge werden beim Start persistiert. |
| Übermäßige Datenerhebung | Keine Konten, IP-Adressen, Tracking-Skripte oder unnötige Felder. |
| Start ohne Pflichtinformationen | API verlangt Altersbestätigung, Kenntnisnahme und getrennte Teilnahmebestätigung; die Werte werden nicht persistiert. |
| Brute-Force gegen Export | Tokenprüfung mit `secrets.compare_digest` und Nginx-Rate-Limit; zentrale Überwachung bleibt Betriebsaufgabe. |

## Vertrauensgrenzen

Browser und Admin-Client gelten als nicht vertrauenswürdig. Die Grenzen liegen
zwischen Client und API, API und Datenbank sowie Anwendung und Hosting-/Log-
Infrastruktur. Alle fachlichen Prüfungen erfolgen serverseitig.

## Verbleibende Risiken

Ein statisches API-Token ist keine vollständige Produktionsauthentifizierung.
HTTPS, restriktive Serverkonfiguration, Rate-Limiting, Rotation,
Fehlversuchsüberwachung, sichere Backups und Log-Aufbewahrung müssen vor dem
Livegang ergänzt und geprüft werden. Rechtliche und wissenschaftliche
Freigaben sind offen.

`/health` prüft nur die Prozess-Liveness. `/ready` prüft zusätzlich die
Datenbank und den erwarteten Migrationsstand, muss aber durch die
Produktionsumgebung korrekt überwacht und hinter einem ausschließlich lokalen
Uvicorn-Binding sowie einem HTTPS-Reverse-Proxy betrieben werden.

Ein Browser-Reload kann ohne gespeicherte Sitzungskennung nicht automatisch
fortgesetzt werden. Das reduziert lokale Datenspeicherung, hinterlässt aber
unvollständige `in_progress`-Sitzungen, die in der Auswertung gesondert
behandelt werden müssen.

Die Angaben in Impressum und Datenschutzhinweisen sind vorläufige Platzhalter.
Ohne Betreiber, Kontakt, Rechtsgrundlage, Altersgrenze, Aufbewahrungs- und
Löschkonzept bleibt der öffentliche Betrieb blockiert.
