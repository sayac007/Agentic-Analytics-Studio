# Studio im eigenen Azure-Abonnement

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

Standard: West Europe, Ubuntu, `Standard_B2als_v2` (2 vCPU, 4 GiB), Standard SSD,
statische öffentliche IPv4, Key Vault. Die konkrete VM-Verfügbarkeit und das
Kontingent hängen vom Abonnement ab; es wird nicht automatisch auf eine teurere
VM ausgewichen.

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
West Europe enthalten; ein vorhandener Vault wird nicht verschoben.

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

1. Die vom Skript ausgegebene **`https://…westeurope.cloudapp.azure.com`**-Adresse
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

Grundbetrag etwa **37,59 USD/Monat**. Hinzu kommen unter anderem Steuern,
Währungsumrechnung, Netzwerkverkehr, Festplattenoperationen und OpenAI-Nutzung.
Das ist keine verbindliche Rechnung oder Budgetobergrenze. Ein größerer
Datenträger kostet entsprechend mehr. Die ältere B1/B2-v1-Familie wird wegen
angekündigter Einschränkungen und Ablösung nicht als Standard verwendet.

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
- [Bisherige Gesprächsgrenzen und API-Datenverarbeitung](CONVERSATIONAL_AGENT.md)
