# Datenschutz

## Vorläufiger Status

Dieses Dokument ist technische Spezifikation und keine Rechtsberatung oder
Bestätigung der DSGVO-Konformität. Die Anwendung ist nicht für eine reale
Datenerhebung freigegeben.

## Datenminimierung

Gespeichert werden nur zufällige Sitzungskennung, Versuchsversion,
Versuchslänge, Durchgang, angezeigte RGB-Werte, Emotion, Reihenfolge,
optionale freiwillige Selbstauskunft zum Geschlecht und optionaler
serverseitiger Antwortzeitpunkt sowie der Sitzungsstatus. Namen, E-Mail-Adressen,
Matrikelnummern, Teilnehmerkonten und IP-Adressen gehören nicht zur
Forschungsdatenbank.

Die Geschlechtsfrage ist freiwillig: `male`, `female`, `diverse` oder
`not_specified` (keine Auswahl). Die Angabe beschreibt die Selbstauskunft und
erlaubt keinen automatischen Schluss auf das biologische Geschlecht.

Die RGB-Erzeugung ist kanalweise gleichverteilt über `0..255`; das ist keine
gleichmäßige Verteilung wahrgenommener Farben. Zufällige RGB-Wiederholungen
werden nicht entfernt, um die Verteilung nicht nachträglich zu verändern.

## Export und Zugangsschutz

CSV wird ausschließlich über `GET /api/admin/export` und ein in der Umgebung
gesetztes `ADMIN_API_TOKEN` ausgeliefert. Das Token wird nicht in URLs,
Antworten, Logs oder exportierten Daten gespeichert. Die Admin-Seite hält es
nur im Arbeitsspeicher und leert das Eingabefeld nach einem Export.
`Cache-Control: no-store` reduziert das Risiko lokaler Cacheablage. Der Export
enthält keine zusätzlichen personenbezogenen Daten. Formula-Injection-Schutz
verhindert die automatische Ausführung führender Formeln in Tabellenprogrammen.

Ein Browser-Reload speichert keine Sitzungskennung. Dadurch wird keine
zusätzliche Wiederaufnahmekennung in Browser-Speichern oder URLs abgelegt.
Ein unvollständiger Versuch bleibt bis zum expliziten Abbruch oder einer
späteren Antwort als `in_progress` erhalten und muss bei der Auswertung als
unvollständig behandelt werden.

Ein API-Token ersetzt keine HTTPS-Pflicht, restriktive Serverkonfiguration,
Zugriffskontrollen oder sichere Betriebs- und Backup-Prozesse.

## Offene Entscheidungen

Vor Veröffentlichung müssen verantwortliche Stelle, Kontakt, Rechtsgrundlage,
Einwilligung, Widerruf und Löschanfragen, Aufbewahrung, Hosting,
Auftragsverarbeitung, Logs, Backups, Drittlandtransfers und gegebenenfalls
Ethik- oder Datenschutz-Folgenprüfung geklärt werden.
