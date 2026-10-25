# Datenwörterbuch

## Status

Die Datenstruktur ist technisch implementiert, aber noch nicht für eine reale
Erhebung wissenschaftlich freigegeben.

## Versuch und Farben

| Feld | Typ | Inhalt und Einschränkung |
| --- | --- | --- |
| `survey_sessions.id` | zufällige Zeichenkette | Nicht sprechende Versuchskennung ohne Personendaten. |
| `survey_sessions.status` | Status | `in_progress`, `completed` oder `abandoned`. |
| `survey_sessions.experiment_version` | Zeichenkette | Version der Versuchsdefinition. |
| `survey_sessions.palette_version` | Zeichenkette | Version der gespeicherten Farbpalette, aktuell `random-rgb-2.0`; historische Sitzungen können ältere Werte enthalten. |
| `survey_sessions.trial_count` | Ganzzahl | Unveränderlicher Snapshot: 10 für neue Sitzungen; 15 bleibt für laufende und historische Sitzungen erhalten. |
| `survey_sessions.gender` | Zeichenkette/null | Freiwillige Selbstauskunft: `male`, `female`, `diverse` oder `not_specified`; bei historischen Sitzungen ohne Angabe bleibt der Wert null. |
| `session_colors.color_id` | Zeichenkette | Positionsbezogene ID wie `trial-1`, keine Farbbezeichnung. |
| `session_colors.position` | Ganzzahl | Position 1 bis 15 innerhalb der Sitzung. |
| `session_colors.color_r/g/b` | Ganzzahlen | Tatsächlich erzeugte Werte, jeweils 0 bis 255. |

Jede Farbe wird serverseitig mit kryptografisch unterstütztem Zufall erzeugt
und dauerhaft gespeichert. RGB-Wiederholungen sind zulässig.

## Antwortdatensatz

| Feld | Typ | Inhalt und Einschränkung |
| --- | --- | --- |
| `id` | technische Kennung | Interne Datenbank-ID. |
| `session_id` | Zeichenkette | Referenz auf die Sitzung. |
| `color_id` | Zeichenkette | Referenz auf eine Farbe dieser Sitzung. |
| `trial_number` | Ganzzahl | Position des Durchgangs, 1 bis 15. |
| `color_r/g/b` | Ganzzahlen | Snapshot der angezeigten RGB-Werte, 0 bis 255. |
| `emotion` | Zeichenkette | Für `random-rgb-2.0`: Wut, Angst, Freude, Traurigkeit, Überraschung, Verachtung oder Ekel. `random-rgb-1.0` kann historisch zusätzlich `Trauer` und `Vertrauen` enthalten. |
| `color_order` | Ganzzahl | Position der Farbe, 1 bis 15. |
| `experiment_version` | Zeichenkette | Version der Versuchsdefinition. |
| `response_timestamp` | Zeitstempel/null | Serverzeit; bei historischen Datensätzen eventuell nicht vorhanden. |

Unique-Constraints verhindern mehrere Antworten für dieselbe Sitzung und
Farbe beziehungsweise denselben Durchgang. Historische Datensätze werden nicht durch erfundene RGB-Werte oder
Zeitstempel ergänzt. Der Zeitstempel ist deshalb nullable modelliert.

`abandoned` kennzeichnet einen ausdrücklich abgebrochenen, unvollständigen
Versuch. Fehlende Antworten werden weder ergänzt noch als abgeschlossen
gezählt. Sitzungen, die lediglich durch einen Browser-Reload verlassen wurden,
bleiben zunächst `in_progress`, bis eine explizite Abbruchaktion erfolgt.

## Emotionskategorien und Versuchsversionen

Neue Sitzungen verwenden `random-rgb-2.0` und exakt diese sieben Werte:
Wut, Angst, Freude, Traurigkeit, Überraschung, Verachtung und Ekel.
`Vertrauen` und die historische Bezeichnung `Trauer` werden für neue
Sitzungen abgelehnt. Historische Antworten werden nicht umgedeutet: Sitzungen
mit `random-rgb-1.0` dürfen beide Werte unverändert enthalten und bleiben über
ihre Versuchsversion unterscheidbar.

`gender` ist eine freiwillige Selbstauskunft. `not_specified` bedeutet, dass
keine Auswahl gemacht wurde; daraus wird nicht automatisch auf das biologische
Geschlecht geschlossen.

Die Startbestätigungen `age_confirmed`, `information_acknowledged` und
`participation_consent` werden nur für die serverseitige Startprüfung
übertragen und nicht in der Forschungsdatenbank gespeichert.

## CSV-Export

Der Export enthält genau diese Spalten in dieser Reihenfolge:

```text
session_id,session_status,experiment_version,gender,trial_count,trial_number,color_id,color_r,color_g,color_b,emotion,response_timestamp
```

Er ist UTF-8-kodiert und verwendet CRLF-Zeilenenden. Es gibt eine Zeile pro
gespeicherter Antwort, sortiert nach Sitzung und Durchgang. Unvollständige
Sitzungen sind durch `session_status` und fehlende Zeilen erkennbar; fehlende
Antworten werden nicht erfunden. Textfelder mit führendem `=`, `+`, `-` oder
`@` werden mit einem Apostroph escaped, um Formelinterpretation in
Tabellenprogrammen zu verhindern.
