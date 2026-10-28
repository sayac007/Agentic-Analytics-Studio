# Secret-Verzeichnis – nur Metadaten

Projektstandard auf Nutzeranweisung vom **28.10.2026**. Für Zugangsdaten werden
Zweck, Speicherort, Anlage und Änderungen dokumentiert, niemals der Wert.
Ein unbekannter Zeitpunkt wird nicht durch das Datum dieses Dokuments ersetzt.
Dieses Verzeichnis ist kein Passwortmanager; Werte bleiben im Key Vault bzw.
im dafür vorgesehenen privaten System.

## Aktueller Azure-Stand

Ressourcengruppe: `rg-agentic-studio`, Region `polandcentral`.
Key Vault: **`openai-api-key-sayac7`**. Studio:
`https://aas-sayac7-studio.polandcentral.cloudapp.azure.com`.

| Eintrag | Zweck / Verbraucher | Maßgeblicher Speicherort | Anlage / letzte Änderung / Beleg |
|---|---|---|---|
| `studio-login-password` | Browseranmeldung als Benutzer **`studio`**; Caddy prüft einen daraus abgeleiteten Hash | Key Vault → `openai-api-key-sayac7` → Geheimnisse → `studio-login-password` → Version | Bereits vor der erfolgreichen Bereitstellung am 28.10.2026 vorhanden. Nutzer zeigte zuvor Secret-Metadaten: aktiviert, kein Ablaufdatum angezeigt. Genaue Anlage-/Änderungszeit und Anlageweg **noch nicht belegt**; Azure-Metadaten angefordert. |
| `openai-api-key` | Optionaler OpenAI-API-Zugriff des Studios | Schlüssel beim Anbieter OpenAI angelegt; gespeicherte Kopie unter Key Vault → `openai-api-key-sayac7` → Geheimnisse → `openai-api-key` | Vor der erfolgreichen Bereitstellung am 28.10.2026 vorhanden; aktiviert, kein Vault-Ablaufdatum angezeigt. Anbieter-Anlagezeit, Vault-Anlage-/Änderungszeit und tatsächliche Anbieter-Gültigkeit **nicht verifiziert**. Vault-Ablauf und Anbieter-Ablauf sind getrennte Angaben. |

Die Angaben „vorhanden/aktiviert“ beruhen auf den vom Nutzer übermittelten
Metadaten, nicht auf einem eigenen Zugriff auf sein Azure-Konto. Der erfolgreiche
Deployment-Abschluss wurde ebenfalls vom Nutzer gemeldet. Secret-Namen oder
eine erfolgreiche Bereitstellung allein belegen keinen erfolgreichen OpenAI-Aufruf.
Eine verantwortliche Person/Anlageidentität wird erst eingetragen, wenn belegt.

### Wo wurde das Studio-Passwort festgelegt?

Der **Speicherort ist bekannt**, der konkrete frühere Anlagevorgang noch nicht.
Das Bereitstellungsskript fragt bei einem fehlenden Secret verdeckt nach:
`Create studio login password (16-64 ASCII characters; input hidden)`.
Alternativ kann der Benutzer das Secret im Portal angelegt haben. Welche Variante
hier ursprünglich verwendet wurde, ist aus dem bisherigen Verlauf nicht belegt.
Es gibt keinen im Code festgelegten Standard-Passwortwert. Bereits vorhandene
Secrets werden vom Deployer wiederverwendet und nicht überschrieben.

Der Login-Name **`studio`** ist im Caddyfile festgelegt; er ist kein Secret.
Ein Datum der Key-Vault-Speicherung beweist nicht, wann ein externer API-Key
ursprünglich beim Anbieter erzeugt wurde.

Am 28.10.2026 meldete der Nutzer eine erfolgreiche Browseranzeige mit
„OpenAI ist serverseitig konfiguriert“, anschließend einen fehlgeschlagenen
Inference-Aufruf. Im anschließend vom Nutzer ausgeführten reinen Modellmetadaten-
Check meldete OpenAI **HTTP 401, `invalid_api_key`** für den aktuell verwendeten
Runtime-Schlüssel. Die Konfiguration war aktiviert und ein Schlüssel vorhanden.
Das belegt dessen Ablehnung, nicht den Grund (etwa Ablauf, Widerruf oder falsch
gespeicherter Wert). Kein Inference-Aufruf wurde bei dieser Diagnose ausgeführt.
Ein Schlüsselwechsel oder eine erfolgreiche Wiederholungsprüfung ist noch nicht
gemeldet; auf Nutzerwunsch am Folgetag gemeinsam fortsetzen. Exakte Uhrzeit unbekannt.

## Automatisch verwaltete Zugangsmittel

| Zugangsmittel | Erzeugung / Speicherung | Lebenszyklus / Nachweis |
|---|---|---|
| Caddy-Passworthash | Bei Dienststart aus `studio-login-password` erzeugt; privates `/run/aas/caddy.env`, Modus 0600 | Wird bei Dienststart neu abgeleitet; kein zusätzlicher vom Nutzer festgelegter Passwortwert. Tatsächliche letzte Ableitungszeit noch nicht erhoben. Hashwert ebenfalls nicht dokumentieren. |
| OpenAI-Runtimekopie | Bei aktiviertem OpenAI aus dem Vault nach `/run/aas/app.env`, Modus 0600 | Wird bei Dienststart frisch gelesen; nicht als neue Anbieter-Schlüsselerstellung zählen. Keine Env-Datei anzeigen oder ins Repository übernehmen. |
| Managed-Identity-Token | Azure IMDS, während des Secret-Abrufs im Prozessspeicher | Automatisch von Azure verwaltet; keine statischen Azure-Zugriffsschlüssel im Studio hinterlegt. Tokenwerte oder Ablaufbehauptungen nicht erfassen, wenn nicht beobachtet. |
| Temporärer SSH-Schlüssel | Nur beim erstmaligen VM-Aufbau im temporären Cloud-Shell-Verzeichnis, Name `aas-ssh-<zufällige ID>` | Private und öffentliche temporäre Datei werden im `finally`-Block entfernt; VM-Passwortanmeldung ist deaktiviert. Öffentliche VM-Schlüsselkonfiguration bleibt bestehen. Kein dauerhaftes menschliches SSH-Anmeldeverfahren daraus behauptet. |
| HTTPS-/ACME-Schlüssel | Automatisch von Caddy verwaltet, persistente Daten unter `/srv/aas/caddy-data` | Kein manuell gewähltes Passwort. Einzelne Ausstellungs-/Erneuerungszeitpunkte noch nicht erhoben; Schlüsselmaterial bleibt privat. |

Implementierungsbelege: [Secret-Anlage und Wiederverwendung](../deploy/azure/Deploy-Studio.ps1),
[Secret-Abruf und private Runtime-Dateien](../deploy/azure/refresh-secrets.py),
[Dienststart](../deploy/azure/agentic-studio.service),
[Browseranmeldung](../deploy/azure/Caddyfile).

## Zeitpunkte ohne Geheimniswerte ermitteln

Im eigenen Azure-Konto, PowerShell:

```powershell
Get-AzKeyVaultSecret -VaultName 'openai-api-key-sayac7' |
    Select-Object Name, Created, Updated, Enabled, Expires |
    Format-List
```

Dieser Listenabruf fordert Secret-Metadaten an. Keine Werte ausgeben und nicht
`-AsPlainText` verwenden. Zeitpunkte mit Zeitzone/Genauigkeit und dem tatsächlichen
Metadatenbezug übernehmen. Bei Rotation beziehen sich Metadaten gegebenenfalls auf
den aktuellen Secret-/Versionsstand; die erste historische Anlage nicht daraus
erraten. Für historische Versionen deren Metadaten separat prüfen. Die genaue
Anlageperson und der Anlageweg sind ohne weitere Belege ebenfalls unbekannt.

Den Passwortwert bei Bedarf ausschließlich privat im Portal ansehen:
**Key Vault → `openai-api-key-sayac7` → Objekte → Geheimnisse →
`studio-login-password` → aktuelle aktivierte Version → Geheimniswert anzeigen**.
Den Wert nicht in den Chat, Screenshots oder dieses Verzeichnis übernehmen.

## Künftige Anlage, Änderung oder Rotation

Mit jeder Änderung diese Metadaten ergänzen:

```text
Name / Zweck / Verbraucher:
Anbieter und maßgeblicher Speicherort, Secret-Referenz:
Anlagezeit mit Zeitzone und Genauigkeit; Quelle des Belegs:
Anlageweg und verantwortliche Person, soweit bekannt:
Letzte Änderung / Rotation / Stilllegung mit Zeitpunkt und Beleg:
Anbieter-Ablauf und Vault-Ablauf getrennt:
Benötigter Dienstneustart / Übernahmeprüfung / tatsächliches Ergebnis:
Offene Angaben ausdrücklich als unbekannt:
```

Nach einer Änderung im Vault lädt ein Neustart von `agentic-studio` die aktuellen
Secret-Versionen. Bis dahin kann die laufende Instanz noch den vorherigen Wert
verwenden. Eine Rotation ist nur bei Bedarf auszuführen; für den beobachteten
Origin-Fehler ist sie keine Fehlerbehebung. Neustart-Anleitung:
[Azure-Einrichtung](AZURE_PRIVATE_STUDIO.md).
