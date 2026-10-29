# Studio: fachliche Aufgabenblöcke und Ergebnisübergabe

Nutzerauftrag vom 28.10.2026: Das Studio soll Business, Sales und Operations durch
eine nachvollziehbare Analyse führen. Tesla bleibt der vorhandene reale Pilot,
nicht die Zielgruppe des Produkts. Keine weitere Azure-/Schlüsselprüfung heute.

## Umfang

1. Fachlichen Datenauftrag privat speichern: Frage, Empfänger, Entscheidung,
   benötigte Schnittstellen, Verantwortliche und Aktualisierung als Beschreibung.
2. Notwendige Baseline-Treiber benennen und mit tatsächlich enthaltenen Modell-
   termen abgleichen. Kalender/Dynamik bleiben die feste Mindestbasis. Ein Muss-
   Häkchen ist keine automatische Implementierung oder Datenbeschaffung.
3. Vorhandene Quellen, Einheiten, Hashbindung und Lücken über die bestehende
   Datenaufnahme zeigen. Keine generische Schnittstelle oder neue Vintage behaupten.
4. Bestehende acht vorab definierte Modelle und Pflichtdiagnostik unverändert nutzen.
5. Lokale Evidenzcheckliste und explizit freigegebene KI-Kommentare für Datenverständnis,
   Ergebnisinterpretation und kritische Qualitätssicherung anbieten. Keine automatische
   Datenkorrektur, Parametersuche oder KI-Abnahme.
6. Lesbare private Ergebnisübergabe samt ausführlicher Microsoft-Copilot-Anleitung
   bereitstellen. Kein automatischer Versand, keine Rohdateien oder privaten Permits.

## Grenzen und Prüfung

Auftragsmetadaten leben in der bestehenden privaten SQLite-Projektmetadatenstruktur;
keine neue Datenbankmigration. Sie verändern weder eingefrorene Protokolle noch
Ergebnisbytes. Kontextfreigaben sind auch an den gespeicherten Auftrag und seine
Muss-Treiber gebunden. Bei Änderungen ist eine neue Vorschau nötig.

Prüfen: Persistenz nach Prozessneustart, offene Muss-Treiber, Lücken, fehlerhafte
Vergleiche, gescheiterte Fits, negative Ergebnisse, Präzision und Geheimnisschutz;
echtes HTTP und Browserablauf mit ausdrücklich konstruierten Software-Fixtures.
Keine neuen realen Modellfits oder echten Provider-Aufrufe nötig. Ein Draft-PR,
kein automatischer Merge und kein unbeobachtetes Azure-Deployment.

UX-Ergänzung auf Nutzerwunsch vom 28.10.2026: geführte Einzelansicht je Aufgabe,
klare nächste Schritte, Tastaturbedienung, lokale Speichermöglichkeit am Treiberschritt,
Erhalt ungespeicherter Eingaben und offene Qualitätspunkte vor technischen Details.
Statistische Verfahren, Daten und Provider-Konfiguration bleiben unverändert.
