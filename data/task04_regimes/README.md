# Task 04 – Datenabgleich vor Modellimplementierung

Stand **29.10.2026, Europe/Berlin**, Protokoll `task-04-regimes/0.1.0-draft`.
Nur beobachtete KBA-Ableitungen und Quellenmetadaten. Keine Fits,
synthetischen Ersatzwerte, analytischen Source-Permits oder neuen Rohdaten im Git.

## Dateien und Nachrechnung

`data_audit.json` bindet drei vorhandene Eingaben mit SHA-256 und den
Ausgangscommit `4afb9d1bfe61f6250923dece8b295af8cb24335a`:

- `data/competition/brand_monthly_2021_2026.csv`
- `data/competition/kba_checks.json`
- `data/competition/kba_sources.json`

69 Monatszeilen übernehmen BEV-/Pkw-Marktwerte aus den Gesamtzeilen in
`kba_checks.json` und Tesla/VW aus der CSV. Jahreswerte sind Monatssummen,
2026 nur Januar–September; sie stimmen mit Dezember-/September-YTD überein.
Benannte BEV-Zahlen werden ohne `SONSTIGE` summiert. Markt minus diese Summe
ergibt `unallocated_BEV`, eine unverteilte Restmenge, keine neue Markenschätzung.

Für jeden fest bezeichneten C17-/C18-/C21-Korb:

1. Untergrenze = Summe aller numerisch bekannten Korbmitglieder.
2. Fehlende Zeile oder leeres Feld bleibt ungeklärt; belegte numerische Null bleibt null.
3. Obergrenze = Untergrenze + unverteilte Restmenge, wenn mindestens ein
   Mitglied ungeklärt ist, sonst genau Untergrenze.
4. Jahresgrenzen = Summe derselben Monatsgrenzen. Keine Verteilung der Restmenge
   auf einzelne Marken; keine Rückdatierung eines Launches aus erster Berichtszeile.

Bei C17 sind **66 von 69 Monaten** ungeklärt; vollständig separat berichtet sind
nur Juli–September 2026. C18/C21 bleiben in allen 69 Monaten unvollständig.
Das beweist weder Abwesenheit noch positive Verkäufe jeder fehlenden Marke.
Ein Punktmodell darf die Untergrenzen nicht als vollständige Zulassungen behandeln.

**Quelle:** Kraftfahrt-Bundesamt, Flensburg, FZ10; eigene Summierung/Abgrenzung,
Datenlizenz Deutschland – Namensnennung – Version 2.0,
<https://www.govdata.de/dl-de/by-2-0>.
Jede Monatszeile nennt die Quell-ID; URL, Originalhash und Abrufpräzision stehen
im bestehenden KBA-Katalog. Monatliche administrative Beobachtungen, keine
historischen Echtzeitvintages. Die Korbdefinition ist analytisch, keine verifizierte
Produktionsland-/Eigentümernationalitätsklassifikation.

## Primärquellen

`primary_sources.json` dokumentiert zwölf erfolgreiche Originalabrufe mit
URL, Ziel-URL, UTC-Abrufzeit, Bytezahl, SHA-256 und konkretem Evidenzumfang;
ein gescheiterter BAFA-Link bleibt als HTTP-404-Versuch sichtbar.
Die Originale bleiben im privaten Rechercheverzeichnis, nicht im Repository.
Für den fachlichen Entwurf stehen insbesondere bereit:

- BMUKN: Förderbekanntgabe 19. Januar 2026, Portalstart/Richtlinie 19. Mai 2026,
  FAQ mit Zielgruppe und Staffelung. Unterschiedliche Datumsrollen erhalten.
- BAFA: tatsächliches Antragsende 18. Dezember 2023, 00:00 Uhr. Noch keine
  vollständige Primärchronik sämtlicher Förderänderungen 2023.
- Weekly Oil Bulletin: Deutschland-Merkblatt beschreibt E5 und Montagsmittel;
  das derzeit verlinkte Merkblatt stammt aus 2018. Keine Behauptung einer
  unabhängig geprüften unveränderten Definition in jedem späteren Jahr.
- KraftStG §3d: aktueller Gesetzestext; historische Änderungs-/Wissensdaten offen.
- Tesla Q1 2025: globaler Model-Y-Produktionswechsel, keine deutsche Monatsausfallreihe.
- Eurostat `nrg_pc_204`: nur Anwendungshülle erreicht; keine Tarifdaten oder
  Filtermetadaten gelesen. HTTP 200 ist hier kein Datenzugriffsnachweis.

Metadaten und kurze Tatsachenzusammenfassungen erlauben keine automatische
Weitergabe der Originale oder analytische Zulassung zusätzlicher Produktreihen.
Frühere private Dieselentscheidungen werden nicht auf Benzin übertragen.

## Tatsächlich ausgeführte Prüfung

Ein gesonderter lokaler, nur lesender Python-Abgleich hat geprüft:
alle drei Eingabehashes, lückenloses 69-Monatsraster, Monatsgesamtwerte,
Tesla/VW, sämtliche Korbgrenzen samt ungeklärten Mitgliedern, nichtnegative
Restgruppen, sechs Jahres-/YTD-Abgleiche und zwölf Original-Byte-/Hashbindungen.
Kein Modell wurde dabei geschätzt. Die anfängliche Entwurfsangabe von sechs
vollständig berichteten C17-Monaten bestand diesen Abgleich nicht und wurde
auf die tatsächlich belegten drei korrigiert; die Eingabedaten wurden nicht verändert.

Bestehende ausführbare Repository-Prüfungen für diesen Datenbereich:

```sh
python3 -m unittest discover -s tests -p test_competition.py -v
python3 contracts/validate.py
python3 -m kba audit
```

Ergebnisse der tatsächlichen Ausführung stehen im Draft-PR; lokale Checks sind
keine Behauptung eines erfolgreichen GitHub-Actions-Laufs. Neue Modelle,
Numeriktests und Abhängigkeiten folgen erst nach fachlicher Protokollfreigabe.

Siehe [Protokollentwurf](../../docs/REGIME_STATE_SPACE_PROTOCOL.md) und
[konkrete Datenlücken/Beschaffungswege](../../docs/TASK_04_DATA_READINESS.md).
