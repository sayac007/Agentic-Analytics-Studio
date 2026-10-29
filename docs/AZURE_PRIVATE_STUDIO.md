# Studio im eigenen Azure-Abonnement

Konkrete Secret-Namen, Speicherorte, bekannte Zeitpunkte und offene Angaben:
[Secret-Verzeichnis](SECRET_INVENTORY.md). Für jede künftige Anlage oder Änderung
diese Metadaten ergänzen; niemals den Wert dokumentieren.

Diese Bereitstellung richtet eine einzelne Ubuntu-VM für einen Besitzer ein.
Das Studio läuft hinter Caddy mit HTTPS und Passwortschutz. Der Arbeitsstand
liegt auf der lokalen verwalteten VM-Festplatte; SQLite wird nicht auf Azure
Files/SMB/NFS verschoben. Es gibt keinen öffentlichen Port 8000 und keinen
freigegebenen SSH-Port. Verwaltung erfolgt über Azure Run Command.

**Status:** Die Bereitstellungsdateien sind vorbereitet. Eine erfolgreiche
Bereitstellung im persönlichen Azure-Abonnement und ein echter OpenAI-Aufruf
sind **NOT VERIFIED**. Hier wurden keine Azure-Ressourcen angelegt und keine
API-Schlüssel gesetzt. Lokale Prüfungen stehen weiter unten.

Die Adresse ist öffentlich erreichbar, der gesamte Studio-Zugriff verlangt eine
Anmeldung. Ein privates Azure-Abonnement bedeutet keine private Netzwerkadresse.
Dies ist eine geschützte Einzelnutzer-Demo, kein Mehrbenutzerdienst mit Entra-SSO.
Die Hauptansicht ist der [empirische Studio-Pilot](EMPIRICAL_STUDIO.md): reale
Registrierungen und geprüfte Makro-/Energie-Beobachtungen, feste Modellvergleiche,
Stationaritätsdiagnostik und Restfehler-Recherche. Private Snapshots/Ergebnisse
werden erst auf der geschützten VM eingerichtet; sie sind nicht im öffentlichen
Git-Repository oder Docker-Image enthalten. Die lizenzierte, bereits öffentliche
KBA-Tabelle und Quellenmetadaten gehören zum Codepaket. Das synthetische
Entwicklungsarchiv bleibt unter `/archive/synthetic` getrennt erreichbar.

## 1. Azure Cloud Shell öffnen und den Plan ansehen

### Einstieg über einen externen Link

Der Browser kennzeichnet das Öffnen eines Links aus einem Chat als
`Sec-Fetch-Site: cross-site`. Die ursprüngliche Origin-Prüfung wies auch diesen
normalen Seitenaufruf mit `Only requests from the configured same origin are
allowed` ab. Als Soforthilfe die HTTPS-Adresse in einem neuen Tab direkt in die
Adresszeile eingeben.

Die korrigierte Prüfung erlaubt ausschließlich originlose GET-Navigationen zu
`/` und `/archive/synthetic`, mit `Sec-Fetch-Mode: navigate` und
`Sec-Fetch-Dest: document`. Host-Prüfung, API-Zugriffe, Frames und verändernde
Anfragen erhalten ihre bisherigen Grenzen; keine Freigabe beliebiger Origins
oder ungeprüfter Forwarded-Header. Nach einer Codeaktualisierung muss die VM mit
dem neuen gepinnten `-SourceCommit` erneut bereitgestellt werden.

### Wenn der OpenAI-Aufruf fehlschlägt

„Serverseitig konfiguriert“ bestätigt nur die Konfiguration, nicht die
Anbieter-Gültigkeit des Schlüssels, Abrechnung oder Modellzugriff. Die lange
JSON-Anzeige bei „Kontext prüfen“ ist die lokale Freigabevorschau und noch keine
OpenAI-Antwort. Keine automatischen Wiederholungen nach einem Fehler.

Der korrigierte Client unterscheidet sicher HTTP 401 (Authentifizierung),
403 (Berechtigung), 404 (Modellzugriff), 429 mit `insufficient_quota` oder
Rate-Limit sowie abgelehnte Anfrageparameter. Rohantworten und deren
Fehlermeldungstexte können sensible Inhalte enthalten und werden nie ausgegeben.
Nur fest erlaubte Fehlercodes/Parameternamen werden übernommen. Netz-/TLS- und
Timeoutfehler bleiben getrennt. Fehlgeschlagene Calls behalten die bisherige
vorsichtige Kostenreservierung; kein automatisches Retry.

`demo/provider_diagnostics.py` kann im laufenden App-Container eine einzelne
GET-Anfrage auf die Modellmetadaten ausführen. Es nutzt den bestehenden
Runtime-Schlüssel, übermittelt keine Projektergebnisse und erzeugt keine
kostenpflichtige Textgenerierung. Die Ausgabe enthält nur sichere Statusfelder.
Auch HTTP 200 bestätigt damit **weder** einen Responses-Aufruf **noch** verfügbare
Abrechnung oder gültige Anfrageparameter. Bei einem bereits laufenden älteren
Image kann das geprüfte Skript separat über Azure Run Command im App-Container
ausgeführt werden; Quellcommit und Datei-SHA-256 vor Ausführung binden.

1. Im [Azure-Portal](https://portal.azure.com/) oben auf **Cloud Shell** (`>_`)
   klicken und **PowerShell** auswählen.
2. Das gewünschte private Abonnement ermitteln:

   ```powershell
   Get-AzSubscription | Select-Object Name, Id, State
   ```

3. Das öffentliche Repository auschecken. Vor dem Merge eines noch offenen
   Bereitstellungs-PRs dessen Branch verwenden; die folgenden Befehle beziehen
   sich auf den geprüften Stand nach dem Merge:

   ```powershell
   git clone https://github.com/sayac007/Agentic-Analytics-Studio.git
   Set-Location Agentic-Analytics-Studio
   $subscriptionId = '<ID aus der obigen Liste>'
   $dnsLabel = '<eigener eindeutiger Name, z.B. aas-kulikov-2026>'
   $sourceCommit = (git rev-parse HEAD).Trim()
   ./deploy/azure/Deploy-Studio.ps1 -SubscriptionId $subscriptionId -DnsLabel $dnsLabel -SourceCommit $sourceCommit
   ```

Dieser letzte Befehl zeigt den Plan. Erst **`-Deploy`** legt Ressourcen an.
Abonnement-ID und DNS-Name sind keine Zugangsschlüssel. Ein Azure-Benutzer mit
Rechten zur Ressourcenanlage und zur Vergabe von Rollen ist erforderlich; reine
Contributor-Rechte reichen für die Key-Vault-Rollenzuweisungen nicht aus.

Standard: West Europe; mit `-Location` ist die Region ausdrücklich wählbar,
beispielsweise `-Location polandcentral`. Ubuntu, `Standard_B2als_v2` (2 vCPU, 4 GiB), Standard SSD,
statische öffentliche IPv4, Key Vault. Die konkrete VM-Verfügbarkeit und das
Kontingent hängen vom Abonnement ab; es wird nicht automatisch auf eine teurere
VM ausgewichen.

Als ausdrückliche Alternative akzeptiert `-VMSize Standard_B2s` die ältere
BS-Familie mit ebenfalls 2 vCPU und 4 GiB RAM. Der Standard bleibt
`Standard_B2als_v2`. Andere Größen sind nicht zugelassen; es gibt keine
automatische Auswahl, Vergrößerung oder Änderung einer vorhandenen VM.

### Einen bereits eingerichteten Key Vault verwenden

Ist `openai-api-key` bereits in einem RBAC-Vault in `rg-agentic-studio`
gespeichert, diesen Vault ausdrücklich angeben:

```powershell
$existingVaultName = '<Name deines bestehenden Key Vaults>'
./deploy/azure/Deploy-Studio.ps1 -SubscriptionId $subscriptionId -DnsLabel $dnsLabel -SourceCommit $sourceCommit -ExistingVaultName $existingVaultName -EnableOpenAI
```

Auch das ist zunächst nur ein Plan. Der Vault und die Ressourcengruppe müssen
bereits im gewählten Abonnement existieren. Ihre Tags dürfen leer sein; eine
Kennzeichnung für eine andere Anwendung wird abgewiesen. Das Skript ändert
weder diese Tags noch die vorhandenen menschlichen Rollenzuweisungen und fragt
keine Benutzer-ID über Microsoft Graph ab. Deine vorhandene Berechtigung zum
Auflisten und Anlegen von Secrets ist erforderlich.

Der vorhandene OpenAI-Key wird anhand der Secret-Metadaten wiedererkannt und
weder erneut angefordert noch überschrieben. Fehlt er bei `-EnableOpenAI`,
bricht dieser Modus vor neuen Ressourcen ab. Neue Netzwerk- und VM-Ressourcen
unterliegen weiterhin sämtlichen Eigentums- und Sicherheitsprüfungen.

Die Region der Ressourcengruppe betrifft ihre Verwaltungsmetadaten. Auch eine
Gruppe in einer anderen Region kann die hier vorgesehenen VM-Ressourcen in
der ausgewählten Region enthalten; ein vorhandener Vault wird nicht verschoben.

### Wenn Azure die Region ablehnt (`locationineligible` / 403)

Die Meldung „selected region is currently not accepting new customers“ betrifft
die regionale Zulassung des Abonnements. Ein erneutes Setzen des API-Keys oder
eine Änderung seiner RBAC-Rolle löst diesen Fehler nicht. Zuerst nur lesen:

```powershell
Get-AzResource -ResourceGroupName rg-agentic-studio |
    Select-Object Name, ResourceType, Location

Get-AzComputeResourceSku -Location polandcentral |
    Where-Object { $_.ResourceType -eq 'virtualMachines' -and $_.Name -eq 'Standard_B2als_v2' } |
    Select-Object Name, Locations, @{Name='Restrictions';Expression={ $_.Restrictions | ConvertTo-Json -Depth 6 -Compress }}
```

Ein vorhandener Key Vault oder ein Eintrag im allgemeinen Regionskatalog ist
kein Nachweis, dass VM-/Netzwerkressourcen dort zulässig sind. Auch die SKU-Liste
ist keine Reservierung oder Garantie für die spätere Bereitstellung. Die
Kontofreigabe und Kapazität müssen zur tatsächlichen Bereitstellung passen.

Ist bislang nur der bestehende Key Vault vorhanden, kann die ausgewählte andere
Region mit dem aktualisierten, gepinnten Quellstand ausdrücklich versucht werden:

```powershell
./deploy/azure/Deploy-Studio.ps1 -SubscriptionId $subscriptionId -DnsLabel $dnsLabel -SourceCommit $sourceCommit -ExistingVaultName $existingVaultName -Location polandcentral -EnableOpenAI -Deploy
```

Die Adresse lautet dann `https://<dnsLabel>.polandcentral.cloudapp.azure.com`.
Die Region wird konsistent für Netzwerk, VM, DNS und private Startkonfiguration
verwendet. Vorhandene Secrets bleiben erhalten. Es gibt keinen automatischen
Regionswechsel, keinen Wechsel auf eine größere VM und keine automatische Löschung.
Bereits vorhandene gleichnamige VM-/Netzwerkressourcen in einer anderen Region
führen vor weiteren Secret-/Rollen-/Netzwerkänderungen zum Abbruch; ihre Daten
und etwaigen laufenden Kosten müssen dann ausdrücklich geprüft werden.

## 2. Bewusst bereitstellen

Für das Studio mit optionaler OpenAI-Unterhaltung:

```powershell
./deploy/azure/Deploy-Studio.ps1 -SubscriptionId $subscriptionId -DnsLabel $dnsLabel -SourceCommit $sourceCommit -Deploy -EnableOpenAI
```

Bei einem bereits eingerichteten Vault stattdessen denselben geprüften Plan
mit `-ExistingVaultName` und zusätzlich `-Deploy` ausführen:

```powershell
./deploy/azure/Deploy-Studio.ps1 -SubscriptionId $subscriptionId -DnsLabel $dnsLabel -SourceCommit $sourceCommit -ExistingVaultName $existingVaultName -EnableOpenAI -Deploy
```

Das Skript fragt verdeckt nach dem **Studio-Anmeldepasswort** und bei einem
neuen Vault nach dem noch fehlenden **OpenAI-API-Schlüssel**. Beides wird als Key-Vault-Secret gespeichert. Die
Passwörter nicht als Befehlsparameter, in YAML oder im Chat eintragen.
Für das Studio-Passwort 16–64 ASCII-Zeichen verwenden, vorzugsweise ein neu
erzeugtes zufälliges Passwort aus dem Passwortmanager.
Der Studio-Benutzername ist **`studio`**; das Anmeldepasswort ist unabhängig vom
Azure-Passwort und vom OpenAI-Schlüssel.

Ohne `-EnableOpenAI` funktionieren reale Datenansicht und feste Berechnungen
ohne OpenAI-Schlüssel. Die VM verursacht trotzdem Azure-Kosten.
Wurde zunächst ohne OpenAI bereitgestellt, später denselben Bereitstellungsbefehl
mit `-Deploy -EnableOpenAI` ausführen. Das bloße Anlegen eines Secrets aktiviert
die externe Unterhaltung nicht. Bereits vorhandene Secrets werden wiederverwendet.

Der Quellstand wird vor der Bereitstellung auf einen vollständigen Git-Commit
aufgelöst. Genau dieser Stand wird auf der VM gebaut. Die VM nutzt ihre eigene
Managed Identity, um Secrets aus dem Vault zu lesen; es gibt keinen zusätzlichen
Azure-Zugangsschlüssel in der Anwendung. Nach dem ersten Start können
Rollenverteilung, Image-Build und HTTPS-Zertifikat einige Minuten benötigen.
Die obigen Befehle binden Plan und Ausführung an denselben ausgecheckten Commit;
der GitHub-Quellbaum muss vor jeder Azure-Änderung die benötigten Dateien enthalten.

### Wenn das VM-Familienkontingent null ist

Ein verfügbarer SKU-Eintrag ohne `Restrictions` bestätigt kein freies
vCPU-Kontingent. Azure prüft sowohl das regionale Gesamtkontingent (`cores`)
als auch die VM-Familie: `standardBasv2Family` für B2als v2,
`standardBSFamily` für B2s. Beide hier zugelassenen Größen benötigen 2 vCPUs.

Der Deployer prüft diese beiden Kontingente für eine neue VM lesend vor
Secret-/Rollen-/Netzwerkänderungen; fehlende Angaben oder weniger als zwei freie
vCPUs führen zum Abbruch. Eine vorhandene VM wird nicht als neue Allokation
gezählt. Kontingentwerte sind Momentaufnahmen und keine Kapazitätsreservierung.
Die Auswahl einer anderen Größe als der vorhandenen VM wird abgewiesen.

Hat Basv2 Limit 0, kann der Besitzer mindestens 2 vCPUs dafür beantragen oder
eine bereits freigegebene Alternative ausdrücklich wählen. Vor B2s sind dessen
eigener regionaler SKU-Status, die beiden Kontingente und der Preis zu prüfen:

```powershell
Get-AzVMUsage -Location polandcentral |
    Where-Object { $_.Name.Value -in @('cores', 'standardBSFamily', 'standardBasv2Family') } |
    Select-Object Name, CurrentValue, Limit
Get-AzComputeResourceSku -Location polandcentral |
    Where-Object { $_.ResourceType -eq 'virtualMachines' -and $_.Name -eq 'Standard_B2s' } |
    Select-Object Name, Family, Locations, Restrictions
./deploy/azure/Deploy-Studio.ps1 -SubscriptionId $subscriptionId -DnsLabel $dnsLabel -SourceCommit $sourceCommit -ExistingVaultName $existingVaultName -Location polandcentral -VMSize Standard_B2s -EnableOpenAI -Deploy
```

Die gewählte Größe steht im Plan und in der öffentlichen VM-Startkonfiguration.
Der tatsächliche SDK-Test deckt beide Größen einschließlich SSH-only-Profil,
JSON-Transport und unveränderter Standard-SSD ab. Der Quoten-Regressionstest
prüft Null, fehlende Angaben, bereits belegte vCPUs und die Wiederholung mit
einer vorhandenen VM ohne neuen Quotenbedarf. Kein automatischer Quotenantrag,
Wechsel auf Spot/ARM oder Löschen fehlgeschlagener Ressourcen.

### Falls der VM-Aufbau beim OS-Passwort abbricht

Die frühere Meldung `An OS password must not be serialized` konnte bereits vor
`New-AzVM` durch unseren lokalen Konfigurationsaufbau ausgelöst werden: Das
Zuweisen von `$null` an die typisierte SDK-Stringeigenschaft `AdminPassword`
ergibt in PowerShell eine leere Zeichenkette. Das bisherige untypisierte
Testdouble hat diesen Unterschied nicht abgebildet.

Der korrigierte Aufbau in `vm-config.ps1` lässt den optionalen
`-Credential`-Parameter von `Set-AzVMOperatingSystem` vollständig weg und setzt
nur den OS-Benutzernamen. `AdminPassword` bleibt unangetastet wirklich `null`.
Die strenge Prüfung bleibt erhalten: kein Passwortwert einschließlich leerer
Zeichenkette, Passwortanmeldung deaktiviert, genau der erzeugte öffentliche
SSH-Schlüssel. Port 22 bleibt gesperrt. Das Studio-Anmeldepasswort im Key Vault
ist davon getrennt und bleibt erforderlich.

Zur Wiederholung den vollständigen korrigierten Quellstand einschließlich
`vm-config.ps1` auschecken und denselben Bereitstellungsbefehl mit dessen
`-SourceCommit` und derselben Region ausführen. Vorhandene passende Netzwerk-
ressourcen und Secrets werden geprüft und weiterverwendet. Die VM wurde bei
diesem lokalen Abbruch noch nicht erstellt; eine bereits angelegte öffentliche
IP kann dennoch Kosten verursachen. Es gibt keine automatische Löschung.

Der tatsächliche lokale Aufbau und SDK-JSON-Transport wurden mit
**Az.Compute 11.10.0 / Az.Accounts 5.5.3** geprüft: `adminPassword` fehlt im
serialisierten OS-Profil, Passwortanmeldung ist deaktiviert und der öffentliche
Schlüssel stimmt überein. Derselbe Test reproduziert den früheren Fehler am
echten typisierten SDK-Modell. Er führt keine Azure-Anmeldung und keinen
Ressourcenaufruf aus:

```powershell
./tests/test_azure_vm_config.ps1
```

Die CI installiert diese Modulversionen ausdrücklich und führt den Test
zusätzlich zu den bisherigen Az-Testdoubles aus. Ein erfolgreicher lokaler oder
CI-SDK-Test belegt weiterhin keine erfolgreiche Azure-Bereitstellung.

### Falls vorhandene Ressourcen trotz passender Tags abgewiesen werden

Az.Network-Objekte für NSG, VNet, öffentliche IP und NIC stellen ihre
Kennzeichnungen in **`Tag`** bereit. VM- und generische Ressourcenobjekte nutzen
**`Tags`**. Der frühere ausschließlich plurale Zugriff konnte deshalb bereits
korrekt gekennzeichnete Netzwerkressourcen beim erneuten Start abweisen.

`resource-tags.ps1` liest beide Modellfelder, ohne Ressourcen oder Tags zu
verändern. Die Eigentumsbedingung bleibt `Application=AgenticAnalyticsStudio`;
fehlende oder fremde Kennzeichnungen an VM-/Netzwerkressourcen werden weiterhin
vor Änderungen abgewiesen. Widersprüchliche oder ungültige Metadaten werden
nicht geraten. Der ausdrücklich wiederverwendete ungetaggte Key Vault bleibt
die bestehende, auf seine genaue Ressourcen-ID begrenzte Ausnahme.

Die lokalen SDK-Tests mit **Az.Network 8.3.0** prüfen alle vier tatsächlichen
Netzwerkmodelltypen, das unveränderte Lesen, fehlende/fremde Marker und
widersprüchliche Metadaten. Der Compute-Test prüft zusätzlich dessen plurales
Modellfeld. Die CI pinnt auch Az.Network auf diese Version. Ein generischer
`Get-AzResource`-Metadatenabruf zeigt die Kennzeichnungen weiterhin als `Tags`:

```powershell
Get-AzResource -ResourceGroupName rg-agentic-studio |
    Select-Object Name, ResourceType, Location,
        @{Name='Application';Expression={$_.Tags['Application']}},
        @{Name='Deployment';Expression={$_.Tags['Deployment']}}
```

Sind diese Kennzeichnungen bereits korrekt, ist für diese Korrektur kein
Retagging und keine Löschung erforderlich; den aktualisierten Quellstand verwenden.

## 3. Genau hier liegt der Key in Azure

Das Skript nennt den **Key-Vault-Namen**. Im Azure-Portal:

1. **Ressourcengruppen → `rg-agentic-studio` → den ausgegebenen Key Vault**.
2. Im Vault links **Objekte / Objects → Geheimnisse / Secrets** öffnen.
3. **+ Generieren/Importieren / Generate/Import** wählen.
4. Bei Uploadoption **Manuell / Manual** auswählen.
5. **Name: `openai-api-key`**.
6. Unter **Geheimniswert / Secret value** den auf der OpenAI-Plattform
   erzeugten API-Schlüssel eintragen und **Erstellen / Create** wählen.

**Geheimnisse / Secrets** ist der richtige Bereich. **Schlüssel / Keys** ist
für kryptografische Schlüssel und hier nicht der richtige Menüpunkt.
Wenn das Skript den Key bereits gespeichert hat, das vorhandene Secret öffnen
und bei einem Austausch eine **neue Version** erstellen.

Bei einem RBAC-Fehler benötigt dein Portal-Benutzer die Rolle
**Geheimnisbeauftragter für Schlüsseltresore** (englisch: `Key Vault Secrets Officer`).
Sie wird am Vault unter **Zugriffssteuerung (IAM) → Hinzufügen → Rollenzuweisung
hinzufügen** vergeben. Anschließend kann die Übernahme einige Minuten dauern.
Das Erstellen eines Vaults oder eine Contributor-Rolle allein gewährt noch
keinen Zugriff auf seine Secret-Werte.

Es handelt sich um einen Schlüssel für die **OpenAI API**, nicht für Azure
OpenAI. Der vorhandene Client verwendet `api.openai.com`. ChatGPT-Abonnements
bezahlen diese API-Nutzung nicht. API-Abrechnung und Guthaben werden bei
[OpenAI](https://platform.openai.com/settings/organization/billing/overview)
verwaltet; die VM wird über Azure abgerechnet.

Nach dem Setzen oder Austauschen eines Secrets den Dienst neu starten:

```powershell
Invoke-AzVMRunCommand -ResourceGroupName rg-agentic-studio -VMName aas-studio -CommandId RunShellScript -ScriptString 'systemctl restart agentic-studio.service'
```

Beim Start werden die aktuellen Secret-Versionen geladen. Der OpenAI-Key landet
nicht im Browser, Docker-Image oder Git. Er wird dem App-Prozess zur Laufzeit
bereitgestellt; Azure-Administratoren und root auf der VM haben entsprechend
weitreichenden Zugriff. Das Projekt verspricht keine Geheimhaltung vor diesen
Administratoren.

## 4. Die erste tatsächliche Prüfung

1. Die vom Skript ausgegebene **`https://<dnsLabel>.<region>.cloudapp.azure.com`**-Adresse
   öffnen und mit `studio` und dem Studio-Passwort anmelden.
2. **Vorhandene Quellen prüfen & Modelle öffnen** wählen. Die sechs Original-
   Quelldateien müssen ihren vorhandenen SHA-256-Prüfsummen entsprechen.
   Die Seite zeigt reale Reihen, acht feste Modelle, verpflichtende Stationaritäts-
   diagnostik sowie ungeklärte Trainingsmonate. Keine synthetischen Ersatzwerte.
3. Modellvariante und gegebenenfalls Lag 2/3 auswählen; die fehlenden Dieselmonate,
   gepaarten Basisvergleiche und Diagnosewarnungen prüfen. Seite neu laden:
   Derselbe verifizierte Snapshot muss erhalten bleiben.
4. Falls OpenAI aktiviert ist: eine kurze Frage stellen, die Vorschau der
   **beobachteten privaten Ergebnisse** prüfen und ausdrücklich freigeben.
   Erst eine echte Antwort samt Nutzungsanzeige belegt den kostenpflichtigen
   Live-Aufruf. Die alte synthetische Archivfreigabe wird dafür nicht verwendet.
5. In einem privaten Browserfenster muss jede Studio-Seite einschließlich
   `/api/health` eine Anmeldung verlangen.

Die vorhandenen API-Budgetgrenzen und die Freigabe je Gesprächszug bleiben
bestehen. Das Studio garantiert damit keine Obergrenze der gesamten Azure-
oder OpenAI-Rechnung. Keine Zugangsdaten oder vertraulichen Daten Dritter in die Frage kopieren.

## Kosten und Betrieb

Tatsächlich abgerufene öffentliche PAYG-Listenpreise, West Europe, USD,
2026-10-27, ohne Reservierung/Spot:

| Posten | Preis | Beispiel bei 730 Stunden/Monat |
|---|---:|---:|
| Linux `Standard_B2als_v2` | 0,0432 USD/Stunde | 31,54 USD |
| Standard SSD E4 LRS, 32 GiB | 2,40 USD/Monat | 2,40 USD |
| Statische Standard-IPv4 | 0,005 USD/Stunde | 3,65 USD |
| Key-Vault-Standardoperationen | 0,03 USD/10.000 Operationen | nutzungsabhängig |

Grundbetrag in West Europe etwa **37,59 USD/Monat**. Diese Preisprüfung gilt nicht
automatisch für eine andere Region. Hinzu kommen unter anderem Steuern,
Währungsumrechnung, Netzwerkverkehr, Festplattenoperationen und OpenAI-Nutzung.
Das ist keine verbindliche Rechnung oder Budgetobergrenze. Ein größerer
Datenträger kostet entsprechend mehr. Die ältere B1/B2-v1-Familie wird wegen
angekündigter Einschränkungen und Ablösung nicht als Standard verwendet.

Zusätzlich am **2026-10-28** aus der offiziellen Retail Prices API abgefragt:
Linux `Standard_B2s`, Produkt `Virtual Machines BS Series`, Poland Central,
PAYG ohne Windows/Spot/Reservierung: **0,048 USD/Stunde**, also **35,04 USD für
730 VM-Stunden**. Der regionale B2als-v2-Vergleichspreis beträgt 0,0432 USD/Stunde;
die B2s-Alternative kostet damit rund 3,50 USD mehr je 730 Stunden. Diese Zahlen
betreffen nur die VM; Disk, öffentliche IP, Operationen, Traffic, Steuern und
OpenAI kommen hinzu. Keine Rechnungsgarantie oder bestätigte SKU-Verfügbarkeit.

Eine einzelne VM ist kein hochverfügbarer Dienst. Der Arbeitsstand liegt unter
`/srv/aas` auf der OS-Festplatte und überlebt Container- und VM-Neustarts. Das
Löschen der VM/Festplatte oder Ressourcengruppe kann ihn zerstören. Es wird kein
verwalteter Backupdienst eingerichtet. Vor solchen Löschungen einen separaten
Sicherungsauftrag durchführen. Das Skript löscht fehlgeschlagene oder vorhandene
Bereitstellungen nicht automatisch; nach einem Fehler können Kosten weiterlaufen.

Zum Unterbrechen der VM-Rechenkosten bewusst deallozieren:

```powershell
Stop-AzVM -ResourceGroupName rg-agentic-studio -Name aas-studio
```

Datenträger, IPv4 und andere verbleibende Ressourcen können weiterhin kosten.
`Start-AzVM -ResourceGroupName rg-agentic-studio -Name aas-studio` startet sie
wieder. Secrets werden bei jedem Dienststart frisch geladen. Die Verbindung von
Basic Auth, HTTPS, exaktem Origin und nicht veröffentlichtem App-Port ist Teil
der Bereitstellung; den App-Port nicht nachträglich öffentlich freigeben.

## Verifikation und Quellen

Tatsächlich lokal geprüft: vollständige Suite mit **389 Tests bestanden**
(91,799 Sekunden), einschließlich sieben Hosting- und sieben Secret-Tests,
sowie PowerShell- und Bash-Syntax. Der Container wurde gebaut und lief als UID 10001 mit
schreibgeschütztem Root-Dateisystem, ohne Netzwerk und ohne veröffentlichte
Ports. Ein echter synthetischer OLS/HAC-Lauf und das Wiederfinden desselben
Laufs nach Container-Neustart bestanden. Python im Container: 3.12.16.

Ein separater lokaler Caddy-2.11.7-Test mit verifizierter lokaler TLS-CA prüfte
Anmeldepflicht, falsches Passwort, das Entfernen von Authentifizierungsheadern
vor der Weiterleitung und die Origin-Prüfung der tatsächlichen Anwendung.
Er prüft keine öffentliche ACME-Zertifikatsausstellung.
Auch die tatsächliche Compose-Konfiguration wurde mit einem lokalen TLS-Issuer
geprüft: App-Healthcheck erfolgreich, Caddy als UID 10002, keine veröffentlichten
App-Ports, nicht angemeldete Anfrage 401 und angemeldete Anfrage 200.

Für Entwickler, mit installiertem `requirements-demo.lock` und vorhandener
Caddy-2.11.7-Binärdatei:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests -p test_hosting.py -v
python -m unittest discover -s tests -p test_azure_secrets.py -v
python scripts/azure_proxy_smoke.py --caddy /pfad/zu/caddy
bash -n deploy/azure/bootstrap.sh
docker build -t aas-studio:local .
```

Der lokale Build benötigte in dieser verwalteten Testumgebung Host-Networking,
Standard-Proxy-Buildargumente und einen nur beim Build eingehängten CA-Bundle
(`--secret id=build_ca,src=/etc/ssl/certs/ca-certificates.crt`). Diese Ausnahme
schaltet keine TLS-Prüfung ab und kopiert keine Proxy-CA ins Runtime-Image;
für eine VM mit direktem TLS-Zugang ist sie nicht erforderlich.

Die Secret-Unit-Tests verwenden ausdrücklich erfundene Zugangswerte und einen
Kryptografie-Testdouble; sie sind kein Beleg eines Key-Vault-Zugriffs.
Eine zusätzliche lokale PowerShell-Prüfung mit Az-Testdoubles bestand Anlage,
Wiederholung und negative Fälle für Quellstand, Fremdressourcen, Netzwerk-
abweichungen und temporäre OS-Festplatten; auch das ist keine Azure-Bereitstellung.
Der entsprechende Regressionstest ist jetzt mit
`pwsh -NoProfile -File tests/test_azure_deploy.ps1` reproduzierbar und Bestandteil
der CI. Er prüft auch die explizite Wiederverwendung eines ungetaggten Vaults,
ohne den vorhandenen API-Key oder die menschlichen Rollen zu verändern.
Die Regionskorrektur wurde am 2026-10-28 zusätzlich lokal mit PowerShell 7.6.9
und diesen Az-Testdoubles geprüft: Standardregion und explizite andere Region,
DNS-/Startkonfigurationsbindung, Wiederholung, Abbruch bei fremder Region sowie
weitergereichte Azure-403-Ablehnung ohne automatischen Ausweichversuch.
Alle 8 Secret-Tests und 7 HTTP-/Hosting-Tests bestanden ebenfalls. Diese Tests
verwendeten keine realen Azure-Zugangsdaten und bestätigen keine Kontokapazität.
CI-Nachweise gehören zum jeweiligen Commit im PR. Ein Syntaxcheck, lokaler
Container oder CI-Fake ist kein Nachweis einer erfolgreichen Azure-
Bereitstellung oder eines bezahlten Live-API-Aufrufs.

- [Azure Retail Prices API](https://prices.azure.com/api/retail/prices)
- [Basv2-VM-Größen](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/general-purpose/basv2-series)
- [VM-Ablösung und Kapazitätsbeschränkungen](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/lifecycle/retirements-and-capacity-restrictions)
- [Key-Vault-Secrets im Portal](https://learn.microsoft.com/en-us/azure/key-vault/secrets/quick-create-portal)
- [Key-Vault-RBAC](https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide)
- [Keine Secrets in VM-Custom-Data](https://learn.microsoft.com/en-us/azure/virtual-machines/custom-data)
- [SQLite und Netzwerkdateisysteme](https://sqlite.org/useovernet.html)
- [Bisherige Gesprächsgrenzen und API-Datenverarbeitung](EMPIRICAL_STUDIO.md)
