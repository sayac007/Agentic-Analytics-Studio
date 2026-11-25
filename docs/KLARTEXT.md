# Klartext: verbindliche Schreibregeln

Diese Regeln gelten für jeden Text, den ein Agent in diesem Repository schreibt:
Dokumentation, Statusberichte, Commit-Nachrichten, Pull-Request-Beschreibungen,
Code-Kommentare, Oberflächentexte und Antworten an den Nutzer. Sie gelten sinngemäß
auch für englische Texte.

Grundlage ist die Wikipedia-Seite „Signs of AI writing“ (Stand Abruf November 2026).
Ihre Kernaussage: Die typischen Muster sind Symptome. Das eigentliche Problem sind
leere, ungenaue oder unbelegte Inhalte. Wörter auszutauschen löst nichts; der Inhalt
muss stimmen.

## Inhalt vor Form

1. **Konkret statt groß.** Schreibe die genaue Tatsache: Zahl, Name, Datum, Ergebnis.
   Keine allgemeine Aufwertung wie „spielt eine entscheidende Rolle“ oder „ist ein
   Meilenstein“. Gibt es keine konkrete Tatsache, entfällt der Satz.
2. **Keine Schein-Analyse.** Keine deutenden Nachsätze wie „…, was die Bedeutung
   unterstreicht“ oder „…, und sorgt so für …“. Eine Bewertung steht nur da, wenn sie
   belegt ist und gebraucht wird.
3. **Beziehungen direkt benennen.** „X leitet Y seit 2017“ statt „X steht in
   Verbindung mit Y“.
4. **Keine vagen Quellen.** Nicht „Experten meinen“ oder „mehrere Quellen berichten“,
   wenn es eine oder keine Quelle gibt. Quelle nennen oder Behauptung weglassen.
   Eine Einzelmeinung nicht als allgemeine Ansicht darstellen.
5. **Nichts erfinden, Lücken offen nennen.** Keine ausgedachten Links, Zitate,
   Seitenzahlen, Messwerte oder Testergebnisse. Fehlt eine Information, steht das in
   einem Satz, ohne ausschweifende Absicherungsfloskeln.
6. **Belege prüfen.** Ein Verweis muss das Gesagte wirklich stützen. Eine Quelle bloß
   zu nennen, belegt nichts.

## Sprache

7. **Einfache Wörter, einfache Verben.** „ist“, „hat“, „nutzt“ statt „fungiert als“,
   „verfügt über“, „bedient sich“. Modewörter meiden, etwa „entscheidend“, „zentral“,
   „nahtlos“, „robust“, „Landschaft“ (bildlich), „unterstreichen“, „fördern“,
   „vielschichtig“, „Zeugnis von“; englisch „crucial“, „pivotal“, „seamless“,
   „robust“, „landscape“, „underscore“, „delve“, „testament to“.
8. **Keine Schablonen.** Kein „nicht nur X, sondern auch Y“ und kein „es geht nicht um
   X, sondern um Y“, wenn niemand X behauptet hat. Keine Dreiergruppen nur des Klangs
   wegen. Kein „Trotz Herausforderungen …“-Schluss, kein „Zusammenfassend“, das nur
   wiederholt.
9. **Sachlicher Ton.** Keine Werbesprache, keine Superlative ohne Beleg, keine
   Gefälligkeiten wie „Gute Frage!“ oder „Sie haben völlig recht!“. Keine angehängten
   Angebote wie „Möchten Sie, dass ich …?“, wenn der nächste Schritt schon klar ist.

## Form

10. **Format passend zum Ziel.** Markdown nur, wo es dargestellt wird. Überschriften in
    normaler Schreibung, Fettdruck sparsam, keine Emojis in Überschriften oder Listen.
    Listen nur für echte Aufzählungen, sonst Fließtext.
11. **Keine Werkzeugreste.** Keine internen Marker, Platzhalter wie `[Datum]` oder
    Notizen an den Leser im fertigen Text. Vor dem Abschluss lesen und prüfen.

## Haltung

12. **Symptome nicht verstecken.** Die Regeln dienen guter Arbeit, nicht der Tarnung.
    Wer ein Muster findet, prüft zuerst den Inhalt dahinter.
13. **Niemanden beschuldigen.** Die Muster sind keine Beweise; auch Menschen schreiben
    so. KI-Detektoren und Bauchgefühl sind unzuverlässig. Keine Vorwürfe gegen
    Personen allein wegen ihres Stils.

## Prüfung vor Abgabe

Vor jedem Commit, Bericht oder Pull Request: Text einmal gegen Regeln 1 bis 11 lesen.
Jede Sachbehauptung muss belegt, jede Zahl nachvollziehbar sein. Was nicht geprüft
wurde, steht ausdrücklich als „nicht geprüft“ da.
