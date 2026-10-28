# Erste gemeinsame Übung: ein KBA-Monatsnachtrag

Diese Übung verwendet **ausschließlich echte, bereits versionierte KBA-Werte**.
Sie spielt einen Nachtrag für Dezember 2025 nach; sie ist keine neue Beschaffung
und enthält keine künstlich eingebauten Fehler oder synthetischen Beobachtungen.
Die zwei Dateien dürfen gemeinsam mit diesem Quellenhinweis verwendet werden.

## Dateien und Herkunft

- [`historie_bis_2025-11.csv`](historie_bis_2025-11.csv): 23 Tesla-Monate, Januar
  2024 bis November 2025.
- [`lieferung_2025-10_bis_2025-12.csv`](lieferung_2025-10_bis_2025-12.csv): drei
  Monate, Oktober bis Dezember 2025. Die zwei Überlappungen sind beabsichtigt.

Quelle: **Kraftfahrt-Bundesamt, FZ 10**, Abruf des Originalbestands 22.10.2026;
[dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0), eigene Darstellung durch
Zeilenfilterung der [versionierten Beobachtungstabelle](../../../data/kba/derived/observations.csv).
Original-Datensatz-URLs und Versionen stehen im [Quellenkatalog](../../../data/kba/sources.json),
Zellnachweise in [`locations.json`](../../../data/kba/derived/locations.json).
Alle sechs Felder jeder ausgewählten Zeile bleiben unverändert. Der Wert ist die
deutsche Pkw-Neuzulassungsanzahl der Marke TESLA über alle Antriebe.

| Spalte | Bedeutung / Importtyp |
|---|---|
| `period` | Berichtsmonat, Text `YYYY-MM` |
| `value` | Monatsanzahl, nichtnegative ganze Zahl |
| `series` | `brand:TESLA`, Text |
| `powertrain` | `all`, Text; nicht mit einer BEV-Teilreihe vermischen |
| `source` | ID des monatlichen KBA-Originals, Text |
| `vintage` | SHA-256 des zugrunde liegenden Original-Workbooks, Text; kein Datum |

## In Excel / Power Query gemeinsam durchführen

Die Menübezeichnungen können je Excel-Version abweichen. Diese Bedienfolge ist
eine Arbeitsanleitung; sie wurde hier nicht in Excel ausgeführt.

1. In einer neuen Arbeitsmappe beide CSV-Dateien getrennt über **Daten → Aus
   Text/CSV → Daten transformieren** laden. UTF-8 und Komma als Trennzeichen
   verwenden. Abfragen `Historie` und `Lieferung` nennen. `period` ausdrücklich als
   Text, `value` als ganze Zahl und die übrigen Spalten als Text einstellen.
2. In beiden Abfragen Pflichtfelder und Konvertierungsfehler prüfen. Jeweils eine
   **Referenz** der Abfrage für die Dublettenprüfung anlegen. Über **Gruppieren nach
   → Erweitert** nach `period`, `series`, `powertrain` gruppieren, Zeilen zählen
   und auf Anzahl größer 1 filtern. Die Ursprungstabellen dabei erhalten.
3. Eine neue Zusammenführung von `Lieferung` mit `Historie` erstellen. In beiden
   Tabellen die drei Schlüsselspalten in derselben Reihenfolge markieren.
   **Linker Anti-Join** ergibt die neuen Monate. Die Quelldaten nicht vorher
   zusammenhängen oder pauschal deduplizieren.
4. Eine zweite Zusammenführung mit **innerem Join** erstellen; aus `Historie`
   `value`, `source` und `vintage` erweitern. Neue und historische Werte vergleichen,
   Herkunftsänderungen ebenfalls ausweisen. Hier müssen die beiden überlappenden
   Monatswerte und ihre Herkunft identisch sein.
5. Wenn die Prüfungen stimmen, `Historie` und ausschließlich die neuen Zeilen
   **als neue Abfrage anfügen**, nach `period` sortieren. Das ergibt 24 Monate.
   Im Ergebnis jeden Monat von 2024-01 bis 2025-12 gegen einen vollständigen
   Monatskalender prüfen; eine Zeilenzahl allein beweist keine Lückenfreiheit.
6. Dezember 2025 mit November 2025 und Dezember 2024 vergleichen. Prozentänderung
   jeweils `(neuer Wert / Vergleichswert - 1) × 100`. Prozentformat bei einem
   Quotienten ohne `× 100` ergibt dieselbe Anzeige. Die Originalwerte behalten.
7. Abfragen, Kontrollergebnisse und kurzen Abschlussvermerk speichern. Erneut
   aktualisieren und prüfen, dass dieselben Ergebnisse entstehen. Offene Schritte
   für den nächsten gemeinsamen Durchgang notieren.

## Kontrollwerte

| Prüfung | Tatsächliches Soll aus den vorhandenen KBA-Zeilen |
|---|---:|
| Zeilen Historie / Lieferung | 23 / 3 |
| Doppelte fachliche Schlüssel innerhalb einer Datei | 0 / 0 |
| Fehlende Pflichtfelder / ungültige Anzahlen in beiden Dateien | 0 / 0 |
| Identische Überlappungen | 2: Oktober und November 2025 |
| Geänderte historische Werte / Herkunftsänderungen | 0 / 0 |
| Neue Monate | 1: Dezember 2025 |
| Neuer Gesamtbestand / Monatslücken | 24 / 0 |
| Oktober / November / Dezember 2025 | 750 / 1.763 / 2.032 |
| Dezember 2024 | 3.905 |
| Dezember 2025 gegenüber November 2025 | +15,258083 % |
| Dezember 2025 gegenüber Dezember 2024 | −47,964149 % |

Die Prozentangaben sind für die Anzeige gerundet; die CSV-Anzahlen sind unverändert.
Monatsanstieg und Vorjahresrückgang widersprechen sich nicht: Sie haben verschiedene
Vergleichsbasen. Daraus folgen weder ein Datenfehler noch eine Ursache oder ein
statistisch signifikanter Effekt. Weil hier kein echter Fehler eingebaut ist,
beweist das Bestehen der Übung noch nicht, dass jede Fehlerart sicher erkannt wird.
Bei der nächsten echten Lieferung prüfen wir auch den Umgang mit tatsächlichen
Revisionen oder Auffälligkeiten, falls solche auftreten.

## Byte-Nachweis für die betreuende Person

Die Dateien sind UTF-8-CSV mit LF-Zeilenenden. Diese SHA-256-Werte beziehen sich auf
die Dateien im Repository, nicht auf eine von Excel neu gespeicherte Exportdatei:

```text
0878d67823b44b62b6d56016a0c899ec46150b9a3935aa6d74eed74c4c3ab36d  data/kba/derived/observations.csv
271baedf18ebed302bb3a3f6029514b5bdfef305618778903d7e5899b5b4997c  historie_bis_2025-11.csv
a9f074343f96290b11689a837ebe6a31a115c9e402aaaa904e81ffb1a943e4eb  lieferung_2025-10_bis_2025-12.csv
```

Optional auf einem dafür freigegebenen Windows-Rechner: `Get-FileHash -Algorithm
SHA256 -LiteralPath '.\historie_bis_2025-11.csv'`. Eine nachträgliche Änderung der
Zeilenenden ändert den Dateihash, auch wenn die Zellwerte gleich aussehen.

[Zur gesamten Übergabe](../../DATA_UPDATE_HANDOVER.md)
