# Tatsächlich ausgeführte Verifikationen – 29.10.2026 UTC

Basis: `f67546eeee4b09510db32054ab399c7e1717cf31` (`main`, Merge PR38).
Branch: `research/competitors-model-prices`. Keine Änderung der eingefrorenen
Studien, statistischen Verträge oder Produktkomponenten. Keine neue empirische
Modellschätzung. Der neue Kalman-/Interaktionsvergleich ist eine Spezifikation.

Python **3.12.14**, `openpyxl==3.1.5`, `jsonschema==4.26.0`.
Die vollständige Suite verwendet die unveränderten `requirements-empirical.lock`
mit deren Includes, installiert in `/tmp/competitor-venv`.
Keine neue Projektabhängigkeit. Ein erster Versuch mit dem vorinstallierten,
unvollständigen Runtime lief 342 Tests mit einem Fehlerfall und 21 Errors
(u.a. fehlendes statsmodels/HypoForge und abweichende Web-Abhängigkeiten).
Danach wurden die vorhandenen Pins installiert; keine Tests zur Umgehung geändert.

## Erfolgreich beobachtet

```sh
/tmp/competitor-venv/bin/python contracts/validate.py
/tmp/competitor-venv/bin/python -m kba audit
/tmp/competitor-venv/bin/python -m unittest discover -s tests -p test_competition.py -v
/tmp/competitor-venv/bin/python -m competition.derive \
  --raw-dir /workspace/private-competitor-research-20261029/raw
```

- Bestehende Manifest-/CSV-Validierung erfolgreich: sechs Beispielzeilen.
- Bestehender Offline-KBA-Audit erfolgreich; Bestandsdaten unverändert.
- **14 gezielte Tests bestanden**: Zahlen/Symbole, falsche Hashes und Monate,
  falsche Tabellenköpfe/Summen, eigenständige Marken/Januar ohne YTD,
  unverifizierte Minuszeichen, ungültige Preise/Datums-/Quellenbezüge,
  Preis-/Reichweitenarithmetik und gesperrte Paarungen, kein Preis-Forward-Fill,
  höchster Preis versus größte Reichweite, deterministische Exporte,
  manipulierte Quellenbytes und Pfad-/Symlink-Ausbrüche.
- Vollständiger letzter lokaler Lauf erfolgreich: **440 Tests in 200,761 Sekunden**.
  Befehl: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
  /tmp/competitor-venv/bin/python -m unittest discover -s tests -v`.
- **118 Originaldateien** gegen beide Kataloge auf Hash und Länge geprüft:
  72 KBA-Mappen und 46 Preisquellen. Alle bestanden.
- Vier KBA-Ausgaben aus diesen Mappen nach `/tmp/competitor-replay` neu extrahiert;
  anschließend Python-Bytevergleich gegen die versionierten Dateien: **alle gleich**.
- Fünf Preis-/Markenansichten durch `competition.derive --output
  /tmp/competition-views` erneut erzeugt; Python-Bytevergleich: **alle gleich**.
- Alle 13 versionierten Datenprüfsummen und drei Codeprüfsummen in
  `sha256.json` geprüft. `git diff --check` bestanden.

Der Replay verifiziert den Parser und die Ableitungen. Manuell transkribierte
Preisfakten erfordern weiterhin Prüfung der angegebenen Quelle/Fundstelle;
Hashintegrität allein beweist keine richtige fachliche Zuordnung.
270/288 KBA-Summenabgleiche sind vollständig; die übrigen 18 sind wegen
fehlender/unterdrückter Quellzellen ausdrücklich unvollständig bzw. nicht
ausführbar. Acht Jahresranglisten ohne potenziell rangverändernde unbekannte Zeile.
Historische Elektrospaltendefinition bis2020 bleibt trotzdem ungeklärt.

Vollständiger letzter Suite-Lauf und Remote-CI: siehe PR-Beschreibung mit
beobachtetem Commit-/Run-Bezug. GitHub-Actions-Erfolg wird hier nicht aus einem
lokalen Lauf abgeleitet. Kein Azure-Deployment und kein eigenständiger Merge.
