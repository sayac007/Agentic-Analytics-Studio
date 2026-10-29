# Data policy and Tesla research

## Source classes
- `observed`: source-published measured figures (e.g., KBA Tesla registrations; these are registrations, not manufacturer sell-out).
- `synthetic`: simulated media spend, generated promotions, injected outcome components.
- `proxy`: search interest, reported campaign dates, advertised prices or public promotion announcements, unless verified as directly measured media exposure/spend.

For every variable record: name, class, original publisher, primary URL, retrieval date, geographic scope, frequency, rights/license, method, revisions, known gaps and permissible distribution. Do not imply that publicly viewable data are automatically open-licensed.

## Research backlog (no sources verified yet)
- Official KBA monthly registrations for Tesla Germany, with definitions and time coverage.
- Public evidence of Tesla Germany TV, online or out-of-home campaigns: dates, market, medium, publisher, archived proof; absence of evidence is not proof of no campaign.
- Tesla price cuts, financing offers, model launches and promotions; annotate exact dates and geographic applicability.
- Google Trends series (query specification, region, normalization, retrieval date); label as demand-interest proxy, not spend.
- Holidays and weather from official sources with reuse rights.
- Regulatory or subsidy regime changes as dated context events.

## Modeling warning
Fitting arbitrary synthetic spend against unchanged observed registrations has no planted causal effect and invites false discovery. The first benchmark instead constructs a **new, explicitly semi-synthetic target** with a known injected effect; observed registrations remain a separate reference series. True recovery and uncertainty must be assessed with time-aware validation and simulation replications.
