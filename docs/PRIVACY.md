# Datenschutz

## Vorläufiger Status

Dieses Dokument ist technische Spezifikation und keine Rechtsberatung oder
Bestätigung der DSGVO-Konformität. Die Anwendung ist nicht für eine reale
Datenerhebung freigegeben.

Die öffentlich ausgelieferten Seiten [Impressum](../src/rgb_website/static/impressum.html)
und [Datenschutzhinweise](../src/rgb_website/static/datenschutz.html) enthalten
die aktuell eingetragenen Betreiber- und Kontaktangaben. Die Angaben müssen
vor der Veröffentlichung durch die Betreiberin abschließend bestätigt werden.

## Verantwortliche Stelle und Rollen

Die Studie wird von der Betreiberin betrieben. Sie entscheidet allein über
Zugriff auf, Verwaltung und Nutzung der Forschungsdaten. Der technische
Entwickler übernimmt die technische Umsetzung. Es handelt sich zugleich um ein
Schulprojekt: Die Schule bewertet das fertige Projekt, betreibt die Studie
nach den vorliegenden Angaben jedoch nicht. Daraus wird keine abschließende
rechtliche Haftungs- oder Verantwortlichkeitsbewertung abgeleitet; diese muss
vor Veröffentlichung geprüft werden.

Als Betreiberin ist Elsa Penzold mit der Anschrift Schulstraße 12,
06628 Naumburg eingetragen. Für Support und Datenschutzanfragen ist
farbe-und-gefuehl-support@proton.me eingetragen.

## Zweck, Teilnahme und Einwilligung

Zweck ist die Auswertung, welche Emotionen Teilnehmende mit zufällig erzeugten
RGB-Farben verbinden. Teilnehmen dürfen ausschließlich Personen ab 16 Jahren.
Die Anwendung verlangt `age_confirmed`, `information_acknowledged` und
`participation_consent`; die drei Bestätigungen werden serverseitig geprüft,
aber nicht in der Forschungsdatenbank gespeichert.

Die Teilnahme ist freiwillig. Die konkrete Rechtsgrundlage, die rechtliche
Bedeutung der Einwilligung und der endgültige Einwilligungsprozess sind nicht
aus dem Code ableitbar und müssen durch die Betreiberin vor dem Start der
Erhebung festgelegt und rechtlich geprüft werden.

## Datenminimierung und tatsächlich gespeicherte Forschungsdaten

Gespeichert werden nur zufällige Sitzungskennung, Versuchsversion,
Versuchslänge, Durchgangs- und Positionsnummern, angezeigte RGB-Werte,
Emotion, Reihenfolge, optionaler freiwilliger Selbstauskunft zum Geschlecht,
serverseitiger Antwortzeitpunkt und Sitzungsstatus. Die Session-Farben werden
separat gespeichert; Antworten enthalten zusätzlich die RGB-Werte als
Snapshot. Namen, E-Mail-Adressen, Matrikelnummern, Teilnehmerkonten und
IP-Adressen gehören nicht zur Forschungsdatenbank.

Die Sitzungskennung ist ein technisches Kennzeichen. Die Anwendung weist keine
Anonymität nach; eine Zuordnung über technische Zusatzdaten kann nicht
ausgeschlossen werden. `gender` ist eine freiwillige Selbstauskunft mit den
internen Werten `male`, `female`, `diverse` und `not_specified`. Daraus wird
nicht automatisch auf das biologische Geschlecht geschlossen.

## Speicherdauer, Löschung und Rechte

Nach Betreiberentscheidung sollen Forschungs-Rohdaten nur so lange gespeichert
werden, wie sie für die Verarbeitung erforderlich sind, höchstens jedoch zwölf
Monate. Die Rohdaten werden manuell gelöscht; eine automatische
Datenbanklöschung und ein systemd-Timer sind nicht vorgesehen. Es gibt keinen
Code oder Test, der eine Löschung nach zwölf Monaten automatisch durchführt.

CSV-Exporte, Backups und technische Logs sind getrennte Datenbestände. Für sie
ist jeweils festzulegen, ob und wie sie personenbezogene oder personenbeziehbare
Informationen enthalten, wer Zugriff hat und wann sie gelöscht werden. Die
geplante Rohdatenfrist gilt nicht automatisch für diese Bestände und muss bei
der manuellen Löschung gesondert berücksichtigt werden.

Löschanfragen werden individuell geprüft. Soweit dies rechtlich und technisch
umsetzbar ist, wird eine Löschung durchgeführt. Ein möglicher Abgleich ohne
gespeicherte Teilnehmerkennung und die Dokumentation der Entscheidung müssen
vor Veröffentlichung festgelegt werden.

## Startbestätigungen

Vor dem Start verlangt die API drei getrennte boolesche Angaben:

- `age_confirmed`: Bestätigung der von der Studienleitung festzulegenden
  Altersgrenze;
- `information_acknowledged`: Kenntnisnahme von Ablauf, Freiwilligkeit und
  Abbruchmöglichkeit;
- `participation_consent`: freiwillige Teilnahmebestätigung.

Alle drei Werte werden serverseitig geprüft und nicht in der
Forschungsdatenbank gespeichert. Die öffentlich angezeigte Altersgrenze von
16 Jahren entspricht der Betreiberentscheidung für diese Studie.

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

Die Admin-Route wird im vorgesehenen Deployment durch Nginx begrenzt. Die
Anwendung selbst verwendet keinen IP-basierten In-Memory-Rate-Limiter, weil
Uvicorn hinter dem lokalen Reverse Proxy nicht die externe Client-IP als
`request.client.host` erhält. Zentrale Brute-Force-Überwachung und die
Wirksamkeit des Nginx-Limits bleiben Betriebsaufgaben.

## Hosting, Logs und Auftragsverarbeitung

Als Hostinganbieter ist IONOS vorgesehen. Der Code belegt den vorgesehenen
Anbieter nicht selbst. Vor dem Start muss geprüft werden, welche IONOS-Dienste,
Speicherorte, Unterauftragnehmer und Logs tatsächlich eingesetzt werden und ob
ein Auftragsverarbeitungsvertrag erforderlich ist.

Die Nginx-Vorlage schreibt Access- und Error-Logs. Uvicorn/systemd- und
Provider-Logs können zusätzlich entstehen. Der Anwendungscode enthält keine
automatische Loglöschung. Zugriffe, Inhalte, IP-Verarbeitung und Fristen
müssen in der produktiven Konfiguration geprüft und dokumentiert werden.

## Offene Angaben und interne Freigabe-Checkliste

Vor Veröffentlichung müssen mindestens:

- Betreibername, ladungsfähige Anschrift und Proton-Mail-Adresse durch die
  Betreiberin abschließend bestätigt werden;
- Rechtsgrundlage, Einwilligung und Widerruf festgelegt werden;
- Verfahren für Auskunft, Berichtigung und individuell geprüfte
  Löschanfragen festgelegt werden;
- Rohdaten-, Export-, Backup- und Logfristen beschlossen werden;
- IONOS-Auftragsverarbeitung, Speicherorte und Unterauftragnehmer geprüft
  werden;
- produktive Hosting-, Zugriffsschutz- und Logkonfiguration geprüft werden;
- die manuelle Rohdatenlöschung spätestens nach zwölf Monaten organisatorisch
  nachweisbar kontrolliert werden;
- gegebenenfalls Ethik- oder Datenschutz-Folgenprüfung durchgeführt werden.

### Checkliste für die manuelle Rohdatenlöschung

Bei jeder planmäßigen Löschung oder individuell geprüften Löschanfrage muss
die Betreiberin datensparsam:

1. die maßgebliche Frist oder Anfrage prüfen;
2. die betroffenen Rohdatensätze und Sitzungen identifizieren;
3. erforderliche CSV-Exporte, Backups und technische Logs berücksichtigen;
4. die Löschung in den vorgesehenen Datenbeständen durchführen, soweit sie
   rechtlich und technisch umsetzbar ist;
5. kontrollieren, dass die vorgesehenen Datenbestände nicht mehr vorhanden
   oder für die weitere Verarbeitung gesperrt sind;
6. Ergebnis, Datum, Umfang und offene Einschränkungen ohne unnötige
   Teilnehmerdaten dokumentieren.

Die Anwendung führt diese Checkliste nicht automatisch aus und bietet keinen
automatischen Löschmechanismus.
