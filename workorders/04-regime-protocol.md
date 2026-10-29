# Task 04 – Protokollentwurf vor Implementierung

Auftrag aus der Nutzerdatei `ChatGPT_Instruktion_Regime_Zustandsraum_Tesla_VW_China.md`.
Zuerst Protokoll und fehlende Daten mit Beschaffungsweg; Code/Schätzung erst danach.

- Aktuelles main einschließlich PR41 als Ausgangspunkt.
- Marktsummen, Korbdefinition und vorhandene Quellen prüfen; Zahlen der Anlage
  sind zu überprüfende Angaben, keine ungeprüften Modellinputs.
- Markt/Markenwahl, konstante/variable Kraftstoffwirkung, bekannte Förderregime,
  Prognoseinformation, Diagnostik, Priors, Abbruch und Interpretation konkretisieren.
- Hypothese und konkurrierende Erklärungen gleichberechtigt, keine Kausalbehauptung.
- Datenbeschaffung planen und zentrale neue Primärfakten verifizieren.
- Keine Modellimplementierung, neuen Fits oder Änderung eingefrorener Protokolle.
- Ergänzung auf Nutzerauftrag zum Repo-Abschluss: zuerst Stufe 1 (Markt/Anteil,
  Kalender/Quartalsende/Förderung), Planungsrahmen 2–3 Wochen; Kraftstoff und
  Diffusion nur optionale Stufe 2. Feste Zustandsvarianzen, Vergleich pro
  Prognosefenster und Hypothesentabelle; keine behaupteten neuen Ergebnisse.

Entwurf: `docs/REGIME_STATE_SPACE_PROTOCOL.md`.
Datenbedarf: `docs/TASK_04_DATA_READINESS.md`.
Audit/Quellen: `data/task04_regimes/`. Draft-PR zur menschlichen Prüfung, kein Merge.
