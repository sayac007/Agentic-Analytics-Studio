# Codex Masterauftrag — Task 02A–02C: Agentic Analytics Studio MVP in 48 Stunden

**Repository:** https://github.com/sayac007/Agentic-Analytics-Studio  
**Zieltermin:** Montag, 26. Oktober 2026  
**Priorität:** Ein vorführbarer, funktionierender End-to-End-Prototyp, nicht zusätzliche Forschungsinfrastruktur.

## 0. Ziel und harte Grenzen

Baue einen lokalen, im Browser benutzbaren Analytics-Studio-Prototypen, in dem ein Nutzer einen synthetischen Beispieldatensatz auswählen, eine echte statistische Analyse starten, die Ergebnisse visualisieren und einen verständlichen Ergebnisbericht sehen kann. Eine begrenzte natürlichsprachliche Steuerung ist Teil des MVP, darf aber nur geprüfte Tools auslösen.

**Arbeitsweise:** Iterativ in drei getrennten Arbeitspaketen, mit je einem überprüfbaren Zwischenstand. Keine parallele Scheinimplementierung aller Features. Nach jedem Paket: tatsächlich ausführen, Screenshots oder Textnachweise intern prüfen, Tests und CI berichten, Draft-PR aktualisieren. Nicht eigenmächtig mergen.

**Daten:** Die öffentliche Demo arbeitet ausschließlich mit synthetischen, eindeutig gekennzeichneten Daten und bekannter Ground Truth. Keine privaten Tesla-, KBA-, Trends-, Energie- oder Familien-/Kundendaten in App, CI, Logs, Screenshots oder Git. Bestehende wissenschaftliche Protokolle, Datenverträge und private Ergebnisse nicht verändern. Die laufende Task 01L nicht mit Task 02 vermischen.

**Ehrlichkeit:** Keine Platzhalter, die als echte Analysen erscheinen; keine erfundenen CI-Läufe, API-Anbindungen oder Modellkennzahlen. Wenn ein Feature nicht funktioniert, als nicht implementiert kennzeichnen. Verhältnismäßige Dokumentation; keine neue Audit-Datei pro Testlauf.

## 1. Vorbereitender Repo-Check (maximal begrenzt)

1. Aktuelles `main` auschecken und `AGENTS.md`, README, Paketstruktur, bestehende Demo-/Stage-A-Engine, Tests und Workflow lesen.
2. Vorhandene Funktionen und HypoForge-Schnittstellen identifizieren. Nur tatsächlich vorhandene, gepinnte und funktionierende APIs nutzen. Kein Umbau der Kernengine.
3. Eine kurze technische Entscheidung dokumentieren: UI-Framework, Backend, lokale Startbefehle, Tool-API. **Bevorzugter Default:** FastAPI + einfache Weboberfläche (z. B. Streamlit, wenn schnell integrierbar). Keine aufwendige Frontend-Buildkette ohne zwingenden Grund.
4. Eine kleine Architektur wählen: `UI -> kontrollierter Backend-Aufruf -> deterministischer Analytics-Code -> validierte Ergebnisartefakte -> UI`.
5. Keine Cloud-Accounts, API-Keys oder Drittanbieter-Datenzugänge als Voraussetzung für die lokale Demo.

## 2. Task 02A — Walking Skeleton (Tag 1, zuerst fertigstellen)

**User Story:** Ich starte die Anwendung lokal, öffne sie im Browser, wähle `Synthetic MMM Demo`, klicke `Run analysis` und sehe ein tatsächlich berechnetes Ergebnis.

Implementiere:
- Einen dokumentierten Ein-Befehl-Start oder maximal zwei klar dokumentierte Kommandos für Backend und UI.
- Eine einfache Oberfläche mit Datensatz-Auswahl, Datensatzbeschreibung, Start-Button, Laufstatus und Fehlermeldungen.
- Eine echte, reproduzierbare Analyse über vorhandene Statistikfunktionen: mindestens OLS auf synthetischen Daten mit vorab festgelegter Media-Transformation (Adstock/Hill, falls bereits zuverlässig verfügbar).
- Ergebnisdarstellung: n, Modellformel, Koeffizienten, Unsicherheit, Baseline/Media-Beitrag, ein echter Plot, klare Kennzeichnung `SYNTHETIC / NOT EMPIRICAL`.
- Eine kurze, verständliche Interpretation **aus berechneten Kennzahlen**, keine LLM-erfundene Zusammenfassung.
- Einen deterministischen Demo-Seed und reproduzierbare Eingaben; Ground Truth bleibt als separater Vergleich sichtbar, nicht als Estimator-Eingabe.

**Abnahme 02A:** App startet aus frischer Installation; Browser-Workflow funktioniert; der Button löst reale Berechnung aus; Ausgabe verändert sich nachvollziehbar bei erlaubter Änderung der Demo-Konfiguration; ein automatisierter End-to-End-Smoke-Test ist grün. Keine Attrappen.

## 3. Task 02B — Nutzbare Analytics-Oberfläche (Tag 2, erster Teil)

Erweitere nur den funktionierenden Skeleton:
- Zeitreihenplot für Zielgröße, Baseline, simulierten Media-Beitrag und Modellvorhersage.
- Koeffiziententabelle mit Unsicherheitsintervallen; Residuen- oder Fit-Diagnose.
- Vorab definierter zweiter Modelllauf oder ein kontrollierter Vergleich zweier Konfigurationen mit identischem Datensatz.
- Vergleichsansicht mit stabilen Kennzahlen, Warnungen zur Identifizierbarkeit und Response-Kurven auf gleichem Spend-Raster, sofern die vorhandenen Verträge dies unterstützen.
- Export eines kompakten Markdown-Ergebnisberichts aus der Oberfläche (nur synthetische Demoergebnisse).
- Klare Grenzen: `estimated`, `ground truth`, `observed/synthetic`, `not identified`, `extrapolated` dürfen nicht verwechselt werden.

**Abnahme 02B:** Ein nichttechnischer Nutzer versteht innerhalb weniger Minuten, welche Daten benutzt wurden, welches Modell lief, was geschätzt wurde und wie verlässlich die Aussage ist.

## 4. Task 02C — Begrenzter Analytics Agent (Tag 2, zweiter Teil)

Implementiere eine **sichere, demonstrierbare Agentensteuerung**. Für den 48-Stunden-MVP reicht eine regelbasierte natürliche Sprache oder ein optionales LLM, das bei fehlendem Schlüssel auf eine deterministische Steuerung zurückfällt.

Mindestens unterstützte Nutzeranfragen:
- `Zeige den Beispieldatensatz.`
- `Starte die MMM-Analyse.`
- `Vergleiche die beiden Modellläufe.`
- `Erkläre die Warnungen und die Modellgrenzen.`

Der Agent darf ausschließlich eine explizite Allowlist vorhandener Tools verwenden, z. B. `list_datasets`, `describe_dataset`, `run_demo_analysis`, `compare_runs`, `summarize_diagnostics`. Keine Shell-Ausführung, keine beliebigen Python-Ausdrücke, keine externen Datenabrufe und keine selbständigen Modelländerungen. Die numerischen Berechnungen laufen ausschließlich im deterministischen Backend. Jede Agentenantwort muss auf echte Tool-Ausgaben verweisen; fehlende Ergebnisse offen benennen.

**MCP:** Wenn ein vorhandener MCP-Server ohne größeren Umbau eingebunden werden kann, ein Tool darüber demonstrieren. Andernfalls eine dokumentierte, getestete Adaptergrenze bereitstellen und die tatsächliche MCP-Integration auf Task 03 verschieben. Keine fiktive MCP-Verbindung.

**Abnahme 02C:** Mindestens vier vorab festgelegte Nutzeranfragen funktionieren durch echte Tool-Aufrufe; fehlerhafte oder unzulässige Anfragen werden sicher und verständlich abgewiesen.

## 5. Engineering, Tests und CI

- Bestehende Paketstruktur respektieren, neue Abhängigkeiten sparsam und reproduzierbar pinnen.
- Unit-Tests für Daten- und Tool-Verträge, Fehlerfälle und deterministische Modellaufrufe.
- Mindestens ein tatsächlicher End-to-End-Test für den Browser- oder API-Workflow; falls GUI-Automatisierung nicht verfügbar ist, einen realen HTTP-Smoke-Test plus dokumentierte manuelle Browserprüfung durchführen und diese Unterscheidung offen berichten.
- Keine echten privaten Daten in CI. CI testet ausschließlich synthetische Fixtures.
- Laufzeit und Installationsanleitung auf Windows und Linux nachvollziehbar beschreiben, soweit tatsächlich getestet; keine ungetestete Plattformkompatibilität behaupten.
- Die bestehende CI darf nicht beschädigt werden.

## 6. Abnahme und Zeitbudget

**24.10.2026:** Task 02A priorisieren. Wenn 02A nicht läuft, keine UI-Politur oder Agenten-Stubs anfangen.

**25.10.2026:** Task 02B und anschließend 02C auf der funktionierenden Basis umsetzen.

**26.10.2026:** Frische Installation, vollständiger Demo-Durchlauf, gezielte Bugfixes, finale README-Kurzanleitung und kurze Live-Demo-Checkliste.

Das sind **Zieltermine**, keine Behauptung garantierter Fertigstellung. Melde Blocker sofort und schlage eine engere funktionsfähige Alternative vor, statt ungetestete Features vorzutäuschen.

## 7. Explizit NICHT Teil des MVP

- Echte Circana/Nielsen- oder andere Enterprise-Anbindungen.
- Microsoft 365, Power Automate, Dots oder Power BI-Integration.
- Live-Webrecherche und automatisierte Quellenrechtsprüfung.
- Neue KBA-/Tesla-Modelle, VAR/VECM, Geo-Tests oder neue empirische Datenaufnahme.
- PPTX-Generierung, Azure-Deployment, Authentifizierung für mehrere Nutzer, produktionsreife Mandantentrennung.
- Öffentliche Veröffentlichung privater Analyseergebnisse.

Diese Punkte gehören in eine knappe Roadmap, nicht in den ersten Implementierungs-PR.

## 8. Arbeitsmodus und Bericht an den Auftraggeber

Arbeite in einem neuen Branch `feat/task-02-mvp` und einem Draft-PR. Organisiere die Umsetzung in **drei getrennten Commits oder klar abgrenzbaren PR-Abschnitten**: 02A, 02B, 02C. Berichte nach jedem Abschnitt im Chat:

1. Was im Browser/API tatsächlich funktioniert.
2. Welche konkreten Befehle der Nutzer ausführen kann.
3. Welche Tests lokal bestanden haben und welche Remote-CI-Läufe tatsächlich grün sind.
4. Welche Funktionen fehlen oder nur eingeschränkt funktionieren.
5. Nächste kleinste Aufgabe.

**Alle Statusberichte und Ergebnisse direkt als Text im Chat ausgeben. Keine ZIP-Transfers, Azure-Uploads oder Downloadlink-Anforderungen.** Quellcode und Tests gehören in den PR; keine zusätzliche Dateiverschiebung zwischen ChatGPT und Codex.

**Definition of Done:** Ein echter Nutzer kann den Prototyp lokal starten, einen synthetischen Datensatz wählen, eine echte Analyse ausführen, Ergebnisse und Diagnosen sehen, einen zweiten Lauf vergleichen und mindestens vier begrenzte Agentenanfragen ausführen. Der Workflow ist getestet und dokumentiert. Nicht erreichte Punkte ausdrücklich benennen.

**Start now with Task 02A. Do not implement 02B/02C until the walking skeleton is genuinely running.**
