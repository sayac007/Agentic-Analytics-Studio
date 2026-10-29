# Repo-Abschluss – Inventur, Zielstruktur und README-Konzept

Stand **29.10.2026, Europe/Berlin**. **PR 1 von drei Aufräum-PRs**:
nur Inventur und Vorschlag. Diese Datei genehmigt ihre eigene Umsetzung nicht.
Basis ist main bei `4afb9d1bfe61f6250923dece8b295af8cb24335a`.
Die [vollständige Inventur](REPOSITORY_INVENTORY.md) enthält alle
367 versionierten Dateien und 56 Unterverzeichnisse.

## 1. Konkrete Entscheidungsvorlage

| Teilbestand | Vorschlag | Grenze |
|---|---|---|
| 319 Dateien | Behalten | Code, Tests, CI, Build, Daten-/Rechte-/Hashnachweise, Verträge und Originalergebnisse bleiben funktionsfähig. |
| 47 Dokumente/Workorders | Archivieren | 22 ältere docs, 24 abgeschlossene Workorders und DATA_SOURCES.md; exakte Liste und Ziele unten. |
| src/README.md | Löschen | Nur veralteter Wegweiser zum vorhandenen Paket; kein Code und kein wissenschaftlicher Befund. |
| Secret-Inventar | Öffentlich kürzen, Details privat | Erst bestätigte private Sicherung; kein öffentliches Archiv der Betriebsdetails. |
| Aktuelles README | Erst PR 3 ersetzen | Erst belegte Kernergebnisse und endgültige Grafiken, keine behaupteten Zustandsraumresultate. |

**Nichts davon wurde verschoben, gekürzt oder gelöscht.** Die Pfade unten sind
die tatsächlich zu genehmigende Liste, keine pauschale Freigabe ganzer Ordner.
Bei geänderten Dateien/Referenzen seit dem Basissnapshot Liste zuerst aktualisieren.

## 2. Was heute abgeschlossen ist – und was nicht

- Task 02 ist ein abgeschlossener **synthetischer Identifizierbarkeitsbenchmark**,
  kein empirischer Tesla-Nachweis. Alle zehn Originaldateien einschließlich
  18.000 Truth-Zeilen, 36.000 Evaluationen und 36 Zusammenfassungen sind dauerhaft
  versioniert. Nullfehler-, Coverage- und Vorzeichenprobleme bleiben sichtbar;
  `mde.csv` enthält nur getestete Gitterschwellen.
- Die private Task-01I.3-Energiestudie ist laut bestehendem Ausführungsnachweis
  abgeschlossen. Ihre privaten Ergebnisse werden weder durch das neue README
  veröffentlicht noch erneut geschätzt.
- Task 04 ist **noch keine abgeschlossene Analyse**. PR #42 enthält einen
  ungefrorenen Protokollentwurf, keine Zustandsraumresultate. Auf Nutzerauftrag
  wird dort die Stufenbegrenzung ergänzt; kein eingefrorenes Protokoll geändert.
- Der private Azure-Betrieb/Browserzugang wurde vom Nutzer als erfolgreich
  getestet gemeldet. Das ist kein eigener neuer Live-Test in diesem Auftrag
  und kein Nachweis eines erfolgreichen OpenAI-Inference-Aufrufs. Die bekannte
  401-Diagnose wird nicht als repariert dargestellt.

## 3. Fachlicher Abschluss vor der Umsetzung

Die Protokollergänzung bleibt im bereits bestehenden
[Draft-PR #42](https://github.com/sayac007/Agentic-Analytics-Studio/pull/42)
und wird nicht mit dem Aufräum-PR vermischt:

1. **Stufe 1:** exakte Markt-/Tesla-Anteilszerlegung und M0/M1/M2 mit
   Kalender, Quartalsende und belegten Förderregimen; G3 Tesla/VW/Rest,
   solange der China-Korb nicht vollständig ist. Kein Kraftstoff, keine Diffusion,
   keine zusätzlichen Preis-/Markenereignis-Koeffizienten.
2. Zwei bis drei Wochen als Umfangs-/Planungsrahmen nach fachlicher Freigabe,
   kein versprochener Hintergrundlauf. Eine offene Antwort beendet den Kern
   ebenso wie eine gestützte oder geschwächte Hypothese.
3. Feste monatliche Zustands-SDs als Entwurfsannahmen:
   Marktniveau 0.10, Steigung 0.01, Anteilsniveau 0.10
   (Varianzen 0.01 / 0.0001 / 0.01). Gemeinsame Halbierung/Verdoppelung als
   vorab benannte Sensitivität, keine Testfehler-Optimierung.
4. Erweiterungen je Rolling-Origin-Fenster gegen dieselbe Basis prüfen;
   Stationaritäts-/Innovationsdiagnostik und alle negativen Befunde erhalten.
   Reine Anpassungsverbesserung ist kein Erkenntnisgewinn.
5. **Stufe 2** Kraftstoff/Diffusion nur nach neuer bewusster Entscheidung.
   Fehlende Benzin-/Bestands-/Preis-/China-Daten verlängern Stufe 1 nicht.
6. Ausgabespalten: **Hypothese | Test | Ergebnis (gestützt / geschwächt / offen)
   | Begründung in einem Satz**. Nicht ausgeführte Varianten heißen
   „offen – nicht untersucht“.

Die Identität Markt × Anteil ist bei geprüften Zählwerten rechnerisch belastbar.
Der Tesla-Rückgang 2025 ist zunächst ein beobachtetes Ereignis, keine erklärte
Ursache. Ein nachhaltiger Kraftstoffeffekt 2026 kann wegen kurzer Reihe,
Förderung und fehlender geprüfter Benzinreihe unentscheidbar bleiben.
Diese Grenze ist kein vorweggenommenes Modellergebnis.

## 4. Vorgeschlagene Zielstruktur

```text
README.md                       Ergebnis zuerst, Englisch + deutsche Kurzfassung
results/
  task02/                       zehn unveränderte Originaldateien am bisherigen Pfad
  figures/                      erst finale Stufe-1-Grafiken als PNG und SVG
  tables/                       erst finale geprüfte Stufe-1-Tabellen/Hypothesentabelle
benchmarks/task02/              unverändertes wissenschaftliches Originalprotokoll
empirical/, studio/, …          bestehende Paketnamen/Importpfade unverändert
data/                          öffentliche Beobachtungen, Manifeste, Rechte, Hashes
contracts/, config/, examples/  bestehende benötigte Pfade unverändert
tests/, scripts/, .github/      vorhandene Prüfungen/CI
deploy/, Dockerfile             bestehender Betrieb ohne Ausbau
docs/
  METHODS.md                    kurze Lesesicht; Links auf normative Originalprotokolle
  DATA.md                       Quellen/Einheiten/Abdeckung/Lücken/Rechte/Vintages
  LIMITATIONS.md                Grenzen und nicht identifizierte Erklärungen
  DEPLOYMENT.md                 generische lokale/Azure-Kurzanleitung
  …                             benötigte normative/aktive Dateien bleiben an Ort
  archive/
    README.md                   Was war es? Warum abgelöst? Welcher Stand?
    docs/                       22 freigegebene historische Dokumente
    workorders/                 24 freigegebene historische Aufträge
    root/                       historische DATA_SOURCES-Paketbeschreibung
```

Vier kurze neue Lesedokumente ersetzen **nicht** die originalen normativen
Verträge, Quellenmanifeste oder Ergebnisdateien. Keine Umbenennung bestehender
Python-Pakete, kein zusätzlicher Analyse-Framework-Unterbau. Zusätzliche
Ergebnisordner entstehen erst, wenn dort tatsächlich geprüfte Ergebnisse liegen.

Besonders zu erhalten:

- `docs/LOCAL_TIMESTAMP_ADMISSION.md`,
  `docs/TESLA_ATTENTION_ECONOMETRIC_PROTOCOL.md` und
  `docs/SCOPED_ENERGY_ECONOMETRIC_PROTOCOL.md`: Runtime-/Hashbindungen.
- `docs/COPILOT_RESULT_PRESENTATION.md`: Produkt liest die Datei;
  Dockerfile und `.dockerignore` führen sie ausdrücklich.
- `workorders/03c-empirical-live.md`: Bestandteil des Docker-Builds und
  methodische Festlegung des bestehenden Piloten.
- `config/`, `contracts/`, `examples/task-01a/`: werden in Tests/Runtime gelesen.
  Der Unterordner `examples/task-01a/private/` enthält synthetische Test-/Beispiel-
  Ground-Truth, keine privaten empirischen Daten.
- Alle Task-02-Originale, inklusive `truth.csv`/`evaluations.csv`;
  zehn Dateien und Originalhashes bleiben vollständig prüfbar.

## 5. Datenrechte und Betriebsdokumentation

`DATA.md` verdichtet die Informationen, erweitert aber keine bestehende
Freigabe. KBA dl-de/by-2-0 mit Quellen-/Änderungsangabe; nationale Destatis-Daten
und ECB-Statistik mit ihren konkreten Quellenbedingungen. Private ECB-FX-/
qualifizierte EC-Diesel-Entscheidungen sind **keine** pauschale öffentliche
Roh-/Derived-Data-Freigabe. EIA/Refinitiv bleibt ungeklärt. Portal-/Trends-
Metadaten sind keine Erlaubnis zur Veröffentlichung kompilierter Privatserien.

Für jede aktive Reihe erhalten bleiben: Definition/Einheit, Zeitraster,
Zeitraum/Lücken, Originalquelle, Vintage/Abrufpräzision, Ableitung, Hashbindung,
Rechte-/Zulassungsumfang und Unsicherheit. Alte blockierte Snapshots nicht
stillschweigend als heute gültigen Status ausgeben oder überschreiben.

`docs/SECRET_INVENTORY.md` künftig öffentlich höchstens:
„Secrets are stored in Azure Key Vault; operational details are private.“
Die vollständigen Metadaten samt unbekannten Zeitpunkten bleiben in einem
bestätigten privaten Betriebsdokument. Private Ablage und verantwortlicher
Zugriff müssen vor Kürzung feststehen; fehlende private Sicherung blockiert
nur diesen Teil. Keine Werte, Passwort-Hashes oder Tokens übernehmen.
AGENTS-/Betriebsverweise entsprechend auf öffentliche Regel und private
Metadatenpflege anpassen. Instanzdetails auch in anderen Betriebsanleitungen
prüfen; eine einzelne gekürzte Datei macht die gesamte Git-Historie nicht privat.

Die aktuelle Textsuche fand OpenAI-Key-Muster nur in Test-/Smoke-Dummies,
E-Mail-Muster nur in negativen URL-Tests und keine Private-Key-Blöcke oder
signierten Credential-URLs nach den verwendeten Mustern. Begrenzte
Arbeitgebernamensuche aus dem vorhandenen Kontext ohne Treffer.
Das ist **keine vollständige Geheimnis-, Urheberrechts- oder Historienprüfung**.
Kein konkreter echter Credentialfund festgestellt, daher kein automatischer
Widerruf und keine Historienumschreibung. Falls echte vertrauliche Inhalte
belegt werden: gesondert melden, nicht durch bloßes Löschen als behoben erklären.

Eine eigene Root-Softwarelizenz ist im inventarisierten Stand nicht vorhanden;
Datenlizenzen ersetzen sie nicht. Keine Softwarelizenz ohne Eigentümerentscheidung
erfinden. Das ist kein Grund, Datenrechte oder wissenschaftliche Ergebnisse umzudeuten.

## 6. Drei getrennte PRs und Abnahme

| PR | Inhalt | Startbedingung |
|---|---|---|
| 1 – dieser Vorschlag | Inventur, genaue Liste, Zielstruktur, README-Konzept | Jetzt; keine Bestandsänderung. |
| 2 – Umsetzung | Nur freigegebene Archivierungen/Löschung, Verdichtung der Lesedokumente und abgesicherte private Metadatenpflege | Ausdrückliche Zustimmung zur konkreten Liste; Stufe-1-Ergebnisabschluss vor tatsächlichem Aufräumen. |
| 3 – README | Kurzes zweisprachiges Ergebnis-README mit finalen Grafiken und belegten Aussagen | Geprüfte Stufe-1-Ergebnisse und überprüfte Zielstruktur. |

Kein automatisches Merge und kein Release-Tag in PR 1. `v1.0-portfolio` erst nach
erfolgreicher Abschlussprüfung/reviewtem Stand, nicht als dekoratives Etikett
einer noch ungeschätzten Studie.

Nach Umsetzung tatsächlich ausführen und getrennt dokumentieren:

- Volle vorhandene Python-Testsuite mit gepinnten Abhängigkeiten, Vertragsprüfung,
  KBA-Audit und `python -m research_benchmark.verify results/task02`.
- Byte-/Hashvergleich aller zehn Task-02-Dateien und eingefrorenen Protokolle
  gegen den freigegebenen Ausgangsstand.
- Lokaler Start mit `python -m demo` und geprüftem Health-Endpunkt; private
  Daten fehlen gegebenenfalls bewusst, kein synthetischer Ersatz für Realmodus.
- Docker-Build mit bestehendem Dockerfile und lokaler Startprüfung; kein
  Azure-Neudeployment und kein kostenpflichtiger KI-Aufruf für Doku-Aufräumen.
- README-/docs-Linkcheck einschließlich Archiv, relativer Links und Anker,
  sowie Pfadreferenzen in AGENTS, Docker und Daten-/Testdateien.
- Erneute private Daten-/Secret-/Arbeitgeber-/Attributionsprüfung.
- GitHub Actions am **finalen exakten Commit** sichtbar grün.
  Ein angekündigter Test oder alter grüner Lauf ist kein aktuelles Ergebnis.

## 7. README-Konzept – erst nach der Strukturentscheidung

Englisch als Hauptsprache, direkt nach Titel/Forschungsfrage 3–4 deutsche Sätze.
Ziel 650–900 Wörter, harte Obergrenze unter 1.000; Methoden-/Quellendetails verlinken.

Reihenfolge:

1. **Question:** “Why did Tesla registrations in Germany fall in 2025 and recover
   in 2026 — market growth or changing brand share?”
2. Drei bis fünf tatsächliche Ergebnis-Sätze. Exakte Zählwertzerlegung von
   modellabhängiger Erklärung trennen; bis zur Ausführung keine erfundenen Befunde.
3. Hauptgrafik: beobachtete Tesla-Entwicklung und Veränderungszerlegung,
   datierte Förderregime und belegte Ereignismarken. Unsicherheit nur für
   Modellgrößen, keine erfundenen Stichprobenintervalle um administrative Zählwerte.
4. Hypothesentabelle mit Test und einer Begründung je Ergebnis.
5. **Höchstens drei weitere Grafiken:** latentes Marktniveau, verfügbare
   Markenniveaus, ursprüngliche Task-02-Erkennungsraten. Keine vollständige
   China-Kurve bei ungeklärten Zuordnungen: Tesla/VW/Rest und eine klare
   Datenlücke statt erfundener vierter Kurve. Task 02 ausdrücklich synthetisch,
   einschließlich schlechter Nullkalibrierung/Coverage/Vorzeichen; kein allgemeines
   Gesetz „Always-on funktioniert nie“.
6. “Why you can trust this”: offizielle gebundene Quellen, keine Ersatzdaten,
   vor dem Fit festgelegtes Protokoll, Fensterberichte und sichtbare Negativbefunde.
   Keine ergebnisblinde Präregistrierung behaupten, wenn die Daten bereits bekannt waren.
7. Drei bis fünf Grenzen: 69 Monate, Liefer-/Quartalsmuster, Preis-/Korb-Lücken,
   noch keine geprüfte Benzinreihe, keine Kausalidentifikation.
8. Drei lokal geprüfte Startkommandos; ein Satz zum privat getesteten Azure-
   Betrieb mit Anmeldung. Keine Instanzadresse, Benutzer- oder Secret-Details.
9. Kurze Repository-Karte.
10. Kurze Attributions-/Rechteübersicht mit Link auf DATA.

Grafikvorschlag: farbenblindfreundliche feste Farben Tesla `#0072B2`,
VW `#E69F00`, China-Korb `#009E73`, Rest `#777777`; direkte Beschriftung,
Achsen mit Einheiten, gleiche Begriffe über alle Abbildungen.
Unter jeder KBA-Grafik “Source: KBA FZ10, own calculation”.
Task-02-Grafik erhält ihre tatsächliche synthetische Quelle statt einer
irreführenden KBA-Zeile. Neue finale Grafiken später als PNG/SVG reproduzierbar
aus einem kleinen Skript; vorhandenes `results/task02/power.png` nicht überschreiben.
Ein erforderlicher SVG-Nachbau wäre eine gesonderte, geprüfte Darstellung der
Originaltabelle, keine Umbenennung oder Veränderung des Originalbilds.

## 8. Exakte Archivierungs- und Löschliste für die Freigabe

Noch keine Umsetzung. Ausgangshashes beziehen sich auf den inventarisierten
main-Stand. Bei nicht eingefrorener historischer Dokumentation sind nach
Freigabe ausschließlich technisch notwendige relative Linkanpassungen erlaubt;
wissenschaftlicher Inhalt/Zahlen bleiben erhalten. Normative eingefrorene
Protokolle und Ergebnisse werden nicht verschoben oder editiert.
Der Archivindex bindet alte Pfade an Ursprungscommit und neue Ziele.

| Alter Pfad | Aktion | Vorgeschlagenes Ziel | SHA-256 des Originals |
|---|---|---|---|
| `DATA_SOURCES.md` | archivieren | `docs/archive/root/DATA_SOURCES.md` | `857a80eb9aafc85cab734caa34192523ebdfe55afb9a586c4c99dace178293b2` |
| `docs/ARCHITECTURE.md` | archivieren | `docs/archive/docs/ARCHITECTURE.md` | `c9e291dabaed8f6482d134bd551b65124973ae5fe0cec25a51c5ec6915e34198` |
| `docs/AUDIT.md` | archivieren | `docs/archive/docs/AUDIT.md` | `6b7fd4bc07c74ef93d65063677a5bd8f14e7d71c439bb875d2e7fa08789b468a` |
| `docs/COMPETITION_DEMAND_RESEARCH.md` | archivieren | `docs/archive/docs/COMPETITION_DEMAND_RESEARCH.md` | `8e4082040c5b3fcb002d647e5e06323b3b83ead64e818b47380e0d10130299a8` |
| `docs/CONVERSATIONAL_AGENT.md` | archivieren | `docs/archive/docs/CONVERSATIONAL_AGENT.md` | `b179c93a857827db6020d8a0c736e4d50b0d11208d2dc6a6006eacc2eb43e104` |
| `docs/DATA_POLICY.md` | archivieren | `docs/archive/docs/DATA_POLICY.md` | `29d81cbd4d2cad561324ab262e16b5cc90686964f66818916cfe0eef0541dc20` |
| `docs/DATA_SOURCES_FUEL_OIL.md` | archivieren | `docs/archive/docs/DATA_SOURCES_FUEL_OIL.md` | `1d2a24e3e9e4005d474f8fea86ddc396223a4e33d58d2ce4745f06cbce4f6d37` |
| `docs/DECISIONS.md` | archivieren | `docs/archive/docs/DECISIONS.md` | `37dbf72715b13cf105de23aca884001c84bc936949cb14e18e55b128b655371a` |
| `docs/FIRST_REAL_ATTENTION_OBSERVATION.md` | archivieren | `docs/archive/docs/FIRST_REAL_ATTENTION_OBSERVATION.md` | `ce9e298df45b4a7327d01399c5b8882506b3bcc5792d453903ce2e56db304289` |
| `docs/GERMAN_FUEL_OIL_ACQUISITION.md` | archivieren | `docs/archive/docs/GERMAN_FUEL_OIL_ACQUISITION.md` | `496f5325dcc02a7d932433de5c35ac2ac265243378029f30217e12ca5e51657a` |
| `docs/GERMAN_MACRO_CONTROLS.md` | archivieren | `docs/archive/docs/GERMAN_MACRO_CONTROLS.md` | `5005c69949df0ca9d54ae7e0f70d89e8fad917043bb18787e5006eb67bfb83db` |
| `docs/GOOGLE_TRENDS_EXTENDED_IMPORT.md` | archivieren | `docs/archive/docs/GOOGLE_TRENDS_EXTENDED_IMPORT.md` | `ccc0972cbb32445c731680e59a69ab6befa6a1f3cda229b574aae2b86e8f4597` |
| `docs/LOCAL_DEMO.md` | archivieren | `docs/archive/docs/LOCAL_DEMO.md` | `39f57dcccf0d72f36800e0526f856ce2911389d4c2fc31e663b4bb0a2ca5f99f` |
| `docs/LOCAL_TIMESTAMP_STATUS.md` | archivieren | `docs/archive/docs/LOCAL_TIMESTAMP_STATUS.md` | `e6e9fb548d960426bacfba008d5472885e93802170d86cb07a11aad9ae961c48` |
| `docs/MULTIBASELINE_RECOVERY_PROTOCOL.md` | archivieren | `docs/archive/docs/MULTIBASELINE_RECOVERY_PROTOCOL.md` | `93dfe5cff53b3fd7bc93e1d7eb8ff51015193d72dace14e8b4b036863b433eee` |
| `docs/ORGANIC_ATTENTION_FEASIBILITY.md` | archivieren | `docs/archive/docs/ORGANIC_ATTENTION_FEASIBILITY.md` | `495da45a419f82eb4cebc0d843a76217e3ca9633ffa8b2e0afd9a9f331cbab24` |
| `docs/PERSISTENT_WORKSPACE.md` | archivieren | `docs/archive/docs/PERSISTENT_WORKSPACE.md` | `5d46d80be521435a60b5f7fb5482caf7724711267e0bdbaf8c79905db61ebcd4` |
| `docs/REAL_ENERGY_DATA_IMPORT.md` | archivieren | `docs/archive/docs/REAL_ENERGY_DATA_IMPORT.md` | `d4e84da398c20fc205f35b2d43d1c49c5be28c93fcf8899f29a0d40e1adf1c43` |
| `docs/ROADMAP.md` | archivieren | `docs/archive/docs/ROADMAP.md` | `b7c3547e44bba0d592f60d6ea74ec49c00259dec65e8a285c5c2f11313764f42` |
| `docs/SOURCE_CATALOG.md` | archivieren | `docs/archive/docs/SOURCE_CATALOG.md` | `e6ee09f22447d9548d795d525da26be768499d7537220e4f581a8da96582cb5e` |
| `docs/TASK_01_READINESS.md` | archivieren | `docs/archive/docs/TASK_01_READINESS.md` | `91bff8845f3ae621836ee02fc82be1ac0009225f580d737ffd11d0a1efdee408` |
| `docs/TESLA_ATTENTION_FIRST_RESULTS.md` | archivieren | `docs/archive/docs/TESLA_ATTENTION_FIRST_RESULTS.md` | `6ec961350d4a1678a332883d92811921b704b812b912918c7bc1ebe89f2debc0` |
| `docs/TESLA_GERMANY_CAMPAIGN_RESEARCH.md` | archivieren | `docs/archive/docs/TESLA_GERMANY_CAMPAIGN_RESEARCH.md` | `3b7b6eca281ea56ba05da5464ba51d14c8d8501d8f6924ee4487853289ae43d6` |
| `src/README.md` | löschen | `— (nur nach Freigabe)` | `cca2c8bd75222bcc9f6733a2b7ce4d1576c2eed575ca1be2f4239568ae81968c` |
| `workorders/00-audit-and-contracts.md` | archivieren | `docs/archive/workorders/00-audit-and-contracts.md` | `09ad54912c10c797b8be96fd1a6b285600fb0b4ca5b6588eec5714c4bcf2f49c` |
| `workorders/01-walking-skeleton.md` | archivieren | `docs/archive/workorders/01-walking-skeleton.md` | `0c0ca9ca0fa53428235ffd1f2f676dac9a804806c616e71fe4dec20d41e0c7b6` |
| `workorders/01b-kba-multibaseline.md` | archivieren | `docs/archive/workorders/01b-kba-multibaseline.md` | `052ad629947688b52ff2be7522385ce5255a18ab3b83209ac8edcada660eb15a` |
| `workorders/01b1-publication-precision.md` | archivieren | `docs/archive/workorders/01b1-publication-precision.md` | `cf5ac0745fb71cec6fb246d68ad452cc9bbb2d46569b316bbb8761ee6e0be56f` |
| `workorders/01d-tesla-campaign-ledger.md` | archivieren | `docs/archive/workorders/01d-tesla-campaign-ledger.md` | `3ae890be88ed7ee74a432d2999b84a2d6c018d08e9e4625fc824739da7606088` |
| `workorders/01e-organic-attention-feasibility.md` | archivieren | `docs/archive/workorders/01e-organic-attention-feasibility.md` | `d2aed38e53011e5fcf5b18f9814a8da705232e094e0f2e323d41238491d0060d` |
| `workorders/01f-first-real-attention-observation.md` | archivieren | `docs/archive/workorders/01f-first-real-attention-observation.md` | `6e63d901f5fe6ead1911f7befaa4ecb5481358f41c31d94eb4f051d39bf42936` |
| `workorders/01f1-extended-trends-import.md` | archivieren | `docs/archive/workorders/01f1-extended-trends-import.md` | `837adde369f8055276e198c00060b28934e92ebc0fe0990c0e3f7ea34ad500d9` |
| `workorders/01g-real-trends-admission-and-diagnostics.md` | archivieren | `docs/archive/workorders/01g-real-trends-admission-and-diagnostics.md` | `f7077b9bf70689fcb3d30410888b5e840195a477db603fe03aca3e8f01173124` |
| `workorders/01g1-local-timestamp-evidence.md` | archivieren | `docs/archive/workorders/01g1-local-timestamp-evidence.md` | `cab2a6412eb12cf631a03c1fa043782dded854247a84e5e59c2d84d60e9e902d` |
| `workorders/01h-m-german-macro-controls.md` | archivieren | `docs/archive/workorders/01h-m-german-macro-controls.md` | `5e438594da5794acba95b5c46c5c1a88986f0765d4fbf76e055b5252d478de59` |
| `workorders/01h-tesla-product-recall-ledger.md` | archivieren | `docs/archive/workorders/01h-tesla-product-recall-ledger.md` | `69874f1e2a8c3f9663970301b35c41abd1f9e99771b0cbf0be68fa798e3ca306` |
| `workorders/01i-fuel-oil-fx.md` | archivieren | `docs/archive/workorders/01i-fuel-oil-fx.md` | `a26793c7c4f2623f1f55b60f779c399449c7e2c88aca5e36da40caacdf687d76` |
| `workorders/01i1-real-energy-integration.md` | archivieren | `docs/archive/workorders/01i1-real-energy-integration.md` | `03b63891752365e287b8e4e868b8037f74d208a3df8204b70bb52669910a9d94` |
| `workorders/01i2-source-rights-admission.md` | archivieren | `docs/archive/workorders/01i2-source-rights-admission.md` | `acf5c8e7ae832f528cac37c5cb1cb9f493f06ddd92c0cb97bdc3ce75fc7320e1` |
| `workorders/01i3-scoped-energy-econometrics.md` | archivieren | `docs/archive/workorders/01i3-scoped-energy-econometrics.md` | `6cc6352ebe1280e62a82d8e92aa4aa7cbaf50bd34f526d4631f7e722418bb5fc` |
| `workorders/02-mvp.md` | archivieren | `docs/archive/workorders/02-mvp.md` | `31451dfdfb3abd48d8b2d777a2a703bfe50bf8db7320149c30c1a2b71ec9da71` |
| `workorders/03a-persistent-workspace.md` | archivieren | `docs/archive/workorders/03a-persistent-workspace.md` | `698f425f354afc4a5cc8c71502a1e759fdd0b8a4c296fcec0c9612ff167b3ed1` |
| `workorders/03b-conversational-agent.md` | archivieren | `docs/archive/workorders/03b-conversational-agent.md` | `11feaa0affca54458b4692f951b9b62201149f1bc5e00c3f10865abf0ad8e2e5` |
| `workorders/03d-business-research-workflow.md` | archivieren | `docs/archive/workorders/03d-business-research-workflow.md` | `a9dcbfd654c77a5171b878416cfdad981fa781967608ddaedac78f872c693625` |
| `workorders/03e-tesla-evidence-review.md` | archivieren | `docs/archive/workorders/03e-tesla-evidence-review.md` | `eb1a6c9d5f643955703d1371daff3a40518d52058c2b5da47c9424b49a6863e4` |
| `workorders/03f-competitors-model-prices.md` | archivieren | `docs/archive/workorders/03f-competitors-model-prices.md` | `170ac3db1fb0779a9e1d34bc155be5e4a0c231734de346412c5fc6881bdb6b45` |
| `workorders/03g-ev-demand-literature-portals.md` | archivieren | `docs/archive/workorders/03g-ev-demand-literature-portals.md` | `84b74c79d8d39a6e4bc2a7ceca9374813c35798a7060a5b90207bb2b984a4184` |
| `workorders/azure-private-studio.md` | archivieren | `docs/archive/workorders/azure-private-studio.md` | `dea51c241f3933bfe4078de1606c1cb7e98055368a169b01664c70e18c0abf5e` |

## 9. Tatsächlich ausgeführte Prüfungen dieser Vorschlagsphase

Keine Aufräum-Abnahme vorwegnehmen: Im aktuellen PR sind nur drei neue
Markdown-Dateien entstanden. Keine neuen Fits, Ergebnisgrafiken oder Änderungen
am README, Deployment, Code, Datenbestand oder eingefrorenen Protokollen.

- Inventurabgleich: **367/367** Basispfade und **56/56** Unterverzeichnisse
  genau einmal in der vollständigen Tabelle; 319/47/1-Entscheidungen konsistent.
- **Alle 367 Bestandsdateien bytegleich mit ihren Git-Blobs** am Basiscommit;
  alle 48 zur Archivierung/Löschung vorgeschlagenen Original-SHA-256 geprüft.
- Neue lokale Dokumentlinks aufgelöst. Zusätzlich README und docs mit statischer
  Inline-Link-/Überschriftenprüfung: **556 lokale Links, keine fehlenden Ziele
  oder ungeklärten Überschriftenanker**. Das umfasst die Inventurtabellen;
  kein externer HTTP- oder vollständiger Markdown-Renderer-Test.
- Bestehender Verifier erfolgreich:
  `python -m research_benchmark.verify results/task02` →
  `Verified synthetic experiment: 18000 truth rows, 36000 fits, 36 summaries`.
  Dieser Befehl liest die gespeicherten Ergebnisse; kein Benchmark neu geschätzt.
- `python contracts/validate.py`: gültiges Manifest/CSV, sechs Beispielzeilen.
- `python -m kba audit`: erfolgreich abgeschlossen.
- Begrenzte Textscreenings wie oben beschrieben: Key-/Passwort-/Token-Literale
  nur als Testkandidaten; Fundstellen in Test-/Dummy-Kontext geprüft. Keine
  Privatschlüsselblöcke/signierten Credential-URLs nach den benutzten Mustern.
- Im separaten PR #42 bei `993a54b` nur drei ungefrorene Entwurfs-/Auftragsdateien
  geändert; alle vier zugehörigen GitHub-Checks sichtbar erfolgreich.
- Volle lokale Testsuite, Demo-Neustart und Docker-Build wurden hier **nicht**
  erneut ausgeführt: keine funktionale Bestandsänderung. Sie sind Pflicht nach
  der später freigegebenen Umsetzung. CI dieses Inventur-PR separat im PR
  dokumentieren; ein grüner PR #42 ist kein Prüfnachweis für diesen PR.
