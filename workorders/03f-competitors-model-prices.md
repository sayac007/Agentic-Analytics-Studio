# Wettbewerbsmarken, jährliche BEV-Top-10 und Preis/Reichweite

Nutzerauftrag 29.10.2026. Deutschland, Pkw-Neuzulassungen. Vollständige Jahre
2018–2025 sind der Anschluss an den bisherigen Tesla-Piloten; 2026 nur getrennt
als tatsächlich verfügbare unterjährige Beobachtung. Keine neue Modellschätzung.

1. Den vorhandenen auditierten KBA-Markenbestand vollständig nutzbar machen,
   neue Marken und Abdeckung benennen. Nicht gelistete Marken/Monate nicht ohne
   Definition als null behandeln. Markenzulassungen aller Antriebe und BEV-Zahlen
   ausdrücklich unterscheiden; günstige BEV-Konkurrenz nicht aus ICE-Summen ableiten.
2. Top 10 je Jahr nach tatsächlich veröffentlichten BEV-Zulassungen der KBA-
   Modellreihen auswählen. Gemischte Antriebe: BEV-Teilspalte statt Gesamtsumme.
   Zusammengefasste Modellreihen nicht als einzelne Variante ausgeben. Gleichstände
   transparent und deterministisch behandeln, ohne Preise für die Auswahl zu nutzen.
3. Möglichst viele historische deutsche Bruttopreis-/Reichweitenbelege zu diesen
   Modellreihen sammeln. Datum, Preisart, Variante, Karosserie, Quelle und Messnorm
   erhalten. Einstiegsvariante und höchster Preis sind nicht automatisch maximale
   Reichweite: höchste Preisvariante und Reichweitenmaximum getrennt führen.
   Listenpreis, Aktion, Förderung, Lieferkosten und Transaktionspreis nicht vermischen.
   Ein datierter Preis innerhalb eines Jahres ist kein Jahresdurchschnitt.
4. Destatis auf Preisniveau-/Preisindex- und Reichweitenindikatoren untersuchen.
   Kaufpreis je 100 km deklarierter Reichweite = Preis * 100 / Reichweite;
   das sind keine Fahrt-/Stromkosten pro 100 km. Nur gleiche Variante/Datum/Norm
   paaren. WLTP/NEFZ nicht ohne Umrechnungsbeleg zusammenführen. Keine fehlenden
   Preise aus aktuellen Konfiguratoren in frühere Jahre zurückschreiben.
5. Rohbelege privat speichern, tatsächliche Abrufstatus/Hashes dokumentieren.
   Fakten/Quellen-/Abdeckungsdaten und reproduzierbare Transformationen getrennt
   von geschützten Quelltexten halten. Lücken sichtbar, keine synthetischen Preise.
   Ein fokussierter Draft-PR, keine Änderung eingefrorener Studien oder fremder Repos.

Ergänzung aus der laufenden Nutzerkorrektur: Interaktionen von relativem
Anschaffungspreis, Kraftstoff-/Betriebskosten und neuem Angebot sowie veränderliche
Preisempfindlichkeit als prüfbare Hypothese konkretisieren. State Space/Kalman
als sparsamen Vergleich zu festen Koeffizienten vorsehen; keine vorgegebenen
Käuferphasen, keine Behauptung ständig steigender Benzinpreise und kein neuer Fit
mit dem noch lückenhaften Preispanel.

Stand der Bearbeitung:

- [x] 72 KBA-Originale bezogen; alle verfügbaren Marken/Antriebe extrahiert,
  Januar–September mit gleichem Vorjahresfenster verglichen.
- [x] Acht jährliche Top-10-Auswahlen; alte elektrische Definition bis2020
  ausdrücklich vorläufig, keine rückwirkende BEV-Zulassung erfunden.
- [x] 130 Preis-/Reichweitenbelegzeilen aus46 Quellen dokumentiert;
  Abdeckung23/80 Modelljahre mit exaktem Preis, zehn mit Preis-/Reichweitenpaar.
- [x] Destatis geprüft; kein belegter Preis-je-Reichweite-Indikator gefunden.
- [x] Datenlücken, problematische Angebote und Folgeanalyse konkret dokumentiert.
- [ ] Historisches Einstiegs-/Topvariantenpanel vollständig: bewusst offen.
  Kein vollständiger Monatsindex aus einzelnen Belegen behauptet.

Tatsächliche Verifikationen: `data/competition/VERIFICATION.md`.
