# Quellenprüfung: Literatur und Portalstatistiken

Recherchevintage 29.10.2026. Eigene Einordnung mit Links:
[`docs/EV_DEMAND_LITERATURE_AND_PORTALS.md`](../../docs/EV_DEMAND_LITERATURE_AND_PORTALS.md).

- `sources.json`: **79 direkt abgerufene und hash-/längenverifizierte Belege**:
  Portalartikel, Grafik-PDFs, Volltexte und Abstract-/Metadatenseiten. URL,
  tatsächliche Ziel-URL, tatsächlicher UTC-Abrufzeitpunkt. Originale nicht im Git.
- `findings.json`: neun kurze Zahlenbeispiele mit Population, Zeitraum,
  Veröffentlichung, Quelle und Einschränkung. Keine vollständige rekonstruierte
  Portalpreisdatenbank. Modellrelevante Statistiken sind `proxy`.
- `literature.json`: acht kritische Lesebefunde; Volltext, akzeptiertes Manuskript,
  Working Paper und nur gelesenes Abstract getrennt. Keine Parameterübernahme.
- `private_series_metadata.json`: Umfang/Hash des privaten AGPI-Extrakts:
  54 Quellbeobachtungen/31 unterschiedliche Monate Januar 2024–September 2026.
  Oktober/Dezember 2025 fehlen; Original-/Rückrechnungs-Vintages bleiben getrennt.
  Kein kontinuierliches 31-Zeilen-Panel.

## Messung und Extraktion

Euro-Angebotspreis, Prozentniveau, Monatsänderung und Stichprobenumfang sind
verschiedene Einheiten. Umfrageantworten, Anfragen und Inserate sind keine
realisierten Neuwagenverkäufe. Ein Inserat kann über mehrere Monate bestehen.
Datenmonat, Feldzeit und Veröffentlichung werden nicht gleichgesetzt.

AGPI-Monatswerte aus der ausdrücklich beschrifteten Tabellenzeile „Elektro“.
Zwei 13-Monats-Charts anhand gedruckter Datenlabels/Monatsbeschriftungen
transkribiert, keine Pixel-Digitalisierung. Bei problematischer PDF-Textreihenfolge,
Euro-Vorzeichen oder gesperrter Schrift wurde die Zeile separat geprüft.
Die Mai 2024-Tabelle erhält keine dort fehlende Anfragenkennzahl; der Jahresrückblick
wird nicht zum Monatswert. Quellen-Hashes sichern die jeweils konsultierte Vintage.

## Zugriff und Nutzungsstatus

Öffentliche Quellen; keine Anmeldung und kein Zugriff auf lizenzierte Händler-APIs. Der m.Q-Report
war direkt auf der Landingpage verlinkt. Suchtreffer waren Entdeckungshinweise,
keine Volltextbelege. Die Bot-Challenge von Fraunhofer-Publica wurde nicht umgangen.
404, HTML statt PDF oder unpassende Titel werden nicht als behaupteter Volltext
akzeptiert. Keine fremden Rohtexte, Grafiken oder vollständigen Artikel im Git.

Forschungslektüre ist keine Datenfreigabe für das Studio. Die kompilierte
Monatsreihe bleibt **privat und nicht als Modelleingang zugelassen**.
Keine Source-Permits erzeugt oder vorhandenen Zulassungsregeln geändert.

- DAT verlangt die Quellenangabe „Deutsche Automobil Treuhand GmbH (DAT)“;
  kommerzielle Nutzung auch auszugsweise laut Quellhinweis nur nach vorheriger
  Zustimmung. Diese Zustimmung wurde hier nicht eingeholt.
- Für mobile.de/AutoScout 24 wird keine offene Datenbanklizenz oder Erlaubnis
  zur Weitergabe einer rekonstruierten Monatsdatenbank behauptet. Öffentlich
  sind Quellenmetadaten und kurze zitierte Fakten zur wissenschaftlichen Einordnung.
- PNAS nennt CC BY-NC-ND 4.0. Das Aarhus-Manuskript erlaubt private Forschung
  und Verlinkung, untersagt Weiterverteilung/gewerbliche Verwertung im Deckblatt.
  Literatur wird nicht pauschal „Open Data“.

## Tatsächlich geprüfte Nachweise

79 Originalbelege privat gegen SHA-256 und Bytezahl geprüft; sämtliche
Quellenverweise der neun Zahlenbeispiele und acht Literaturbefunde aufgelöst.
54 private Zahlenzeilen auf endliche Werte, Datum und Quelle geprüft;
Vintages nicht zusammengeführt. Die Veröffentlichungsdifferenz für Januar 2025
wurde mit Python/Decimal berechnet; keine daraus konstruierte reale Verteuerung:

```sh
python3 - <<'PY'
from decimal import Decimal
a, b = Decimal('29630'), Decimal('34910')
print(b-a, ((b/a-1)*100).quantize(Decimal('0.01')))
PY
```

Öffentliche JSON-Dateien und Referenzen lokal geprüft. Weitere ausgeführte
Projektprüfungen und tatsächlicher CI-Stand stehen in der PR-Beschreibung.
Kein erfolgreicher Actions-Lauf aus einem lokalen Check abgeleitet.

Ausgeführte bestehende Prüfungen am 29.10.2026:

```sh
/tmp/competitor-venv/bin/python contracts/validate.py
/tmp/competitor-venv/bin/python -m kba audit
/tmp/competitor-venv/bin/python -m unittest discover -s tests -p test_competition.py -v
```

Erfolgreich: bestehende Beispielvalidierung, KBA-Audit und 14 Wettbewerbsdaten-Tests.
Zusätzlich die oben beschriebenen Quellen-/Referenz-/Zahlenprüfungen ausgeführt.
Keine neue Laufzeitlogik, Abhängigkeit oder Testinfrastruktur. Für die PDF-Lektüre
wurde das bereits verfügbare Recherchewerkzeug `pypdf 6.10.0` verwendet; es ist
keine neue Studio-Abhängigkeit.
