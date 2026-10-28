#Requires -Version 7.2
# Local Az test doubles only: no Azure authentication, network or real credentials.
$ErrorActionPreference = 'Stop'
$DeployScript = Join-Path $PSScriptRoot '../deploy/azure/Deploy-Studio.ps1'
$ExpectedCommit = 'a' * 40
$DummyPassword = 'PrivateMockPassword-01'
$DummyApiKey = 'sk-test-mock-never-a-real-key-123456789'
$MockState = @{ Changes = 0; Roles = @(); Secrets = @{}; PasswordPrompts = 0; Commands = @();
    Group = $null; Vault = $null; Nsg = $null; Vnet = $null; Ip = $null; Nic = $null; Vm = $null;
    Marker = $true; VmProfiles = @(); SourceMode='valid'; AzureContextCalls=0; GraphCalls=0; GraphForbidden=$false; NewVaults=0; SecretWrites=@(); ExpectedVaultName=$null; SourceRefs=@() }
function Assert-That([bool]$Condition, [string]$Message) { if (-not $Condition) { throw $Message } }
function Invoke-RestMethod { param($Uri, $Headers)
    if ($Uri -like 'https://api.github.com/repos/sayac007/Agentic-Analytics-Studio/commits/*') { $MockState.SourceRefs+=$Uri; return @{sha=$ExpectedCommit;commit=@{tree=@{sha=('b'*40)}}} }
    Assert-That ($Uri -eq ('https://api.github.com/repos/sayac007/Agentic-Analytics-Studio/git/trees/'+('b'*40)+'?recursive=1')) 'Unexpected network URI'
    $paths=@('Dockerfile','.dockerignore','demo/hosting.py','requirements.lock','requirements-demo.lock',
        'deploy/azure/Deploy-Studio.ps1','deploy/azure/bootstrap.sh','deploy/azure/refresh-secrets.py',
        'deploy/azure/compose.yaml','deploy/azure/Caddyfile','deploy/azure/agentic-studio.service',
        'requirements-empirical.lock','empirical/data.py','empirical/model.py','empirical/features.py',
        'empirical/diagnostics.py','empirical/service.py','empirical/restore.py','demo/static/empirical.html',
        'demo/static/empirical.js','demo/empirical_chat.py','data/verified_sources/manifest.json','workorders/03c-empirical-live.md')
    $tree=@($paths|ForEach-Object { if (-not($MockState.SourceMode -eq 'missing' -and $_ -eq 'Dockerfile')) {
        @{path=$_;type='blob';mode=if ($MockState.SourceMode -eq 'symlink' -and $_ -eq 'Dockerfile') {'120000'} else {'100644'}}
    }})
    return @{truncated=($MockState.SourceMode -eq 'truncated');tree=$tree}
}
function Get-AzContext { return @{Subscription=@{Id='11111111-1111-1111-1111-111111111111'}} }
function Set-AzContext { param($Subscription) $MockState.AzureContextCalls++ }
function Get-AzADUser { param([switch]$SignedIn) $MockState.GraphCalls++; if ($MockState.GraphForbidden) { throw 'Graph unavailable to Cloud Shell mock identity' }; return @{Id='22222222-2222-2222-2222-222222222222'} }
function Read-Host { param($Prompt, [switch]$AsSecureString)
    Assert-That $AsSecureString.IsPresent 'Secret prompt was not hidden'
    $MockState.PasswordPrompts++
    $v = if ($Prompt -match 'OpenAI') { $DummyApiKey } else { $DummyPassword }
    return ConvertTo-SecureString $v -AsPlainText -Force
}
function Start-Sleep { param($Seconds) }
function Get-AzResourceGroup { param($Name,$ErrorAction) return $MockState.Group }
function New-AzResourceGroup { param($Name,$Location,$Tag) $MockState.Changes++; $MockState.Group=@{Name=$Name;Location=$Location;Tags=$Tag}; return $MockState.Group }
function Get-AzKeyVault { param($VaultName,$ResourceGroupName,$ErrorAction) return $MockState.Vault }
function New-AzKeyVault { param($VaultName,$ResourceGroupName,$Location,$Sku,[bool]$DisableRbacAuthorization,$SoftDeleteRetentionInDays,$Tag)
    Assert-That (-not $DisableRbacAuthorization) 'RBAC disabled'; $MockState.Changes++; $MockState.NewVaults++
    $MockState.Vault=@{Tags=$Tag; EnableRbacAuthorization=$true; ResourceId='/mock/vault'; VaultName=$VaultName}; return $MockState.Vault
}
function Get-AzRoleAssignment { param($ObjectId,$RoleDefinitionId,$Scope) return @($MockState.Roles|Where-Object {$_.ObjectId -eq $ObjectId -and $_.RoleDefinitionId -eq $RoleDefinitionId -and $_.Scope -eq $Scope}) }
function New-AzRoleAssignment { param($ObjectId,$RoleDefinitionId,$Scope,$ObjectType)
    Assert-That ($ObjectType -in @('User','ServicePrincipal')) 'Role target ObjectType missing'
    $MockState.Changes++; $value=@{ObjectId=$ObjectId;RoleDefinitionId=$RoleDefinitionId;Scope=$Scope;ObjectType=$ObjectType}; $MockState.Roles += $value; return $value
}
function Get-AzKeyVaultSecret { param($VaultName) Assert-That ($args.Count -eq 0) 'Secret contents requested instead of listing metadata'; if ($MockState.ExpectedVaultName) { Assert-That ($VaultName -eq $MockState.ExpectedVaultName) 'Listed secrets from wrong vault' }; return @($MockState.Secrets.Keys|ForEach-Object {[pscustomobject]@{Name=$_}}) }
function Set-AzKeyVaultSecret { param($VaultName,$Name,[securestring]$SecretValue)
    if ($MockState.ExpectedVaultName) { Assert-That ($VaultName -eq $MockState.ExpectedVaultName) 'Wrote secret to wrong vault' }; $MockState.Changes++; $MockState.Secrets[$Name]=$true; $MockState.SecretWrites += $Name
    Assert-That ($SecretValue.Length -ge 16) 'Secret too short'; return @{Name=$Name}
}
function Get-AzNetworkSecurityGroup { param($ResourceGroupName,$Name,$ErrorAction) return $MockState.Nsg }
function New-AzNetworkSecurityRuleConfig { param($Name,$Protocol,$Direction,$Priority,$SourceAddressPrefix,$SourcePortRange,$DestinationAddressPrefix,$DestinationPortRange,$Access)
    return [pscustomobject]@{Name=$Name;Protocol=$Protocol;Direction=$Direction;Priority=$Priority;SourceAddressPrefix=$SourceAddressPrefix;SourcePortRange=$SourcePortRange;DestinationAddressPrefix=$DestinationAddressPrefix;DestinationPortRange=$DestinationPortRange;Access=$Access}
}
function New-AzNetworkSecurityGroup { param($ResourceGroupName,$Location,$Name,$SecurityRules,$Tag)
    if ($MockState.BlockedLocation -eq $Location) { throw '403 RequestDisallowedByAzure: locationineligible' }
    $MockState.Changes++; $MockState.Nsg=@{Id='/mock/nsg';Location=$Location;SecurityRules=$SecurityRules;Tags=$Tag}; return $MockState.Nsg
}
function Get-AzVirtualNetwork { param($ResourceGroupName,$Name,$ErrorAction) return $MockState.Vnet }
function New-AzVirtualNetworkSubnetConfig { param($Name,$AddressPrefix) return @{Id='/mock/subnet';Name=$Name;AddressPrefix=$AddressPrefix} }
function New-AzVirtualNetwork { param($ResourceGroupName,$Location,$Name,$AddressPrefix,$Subnet,$Tag) $MockState.Changes++; $MockState.Vnet=@{Location=$Location;Tags=$Tag;Subnets=@($Subnet)}; return $MockState.Vnet }
function Get-AzPublicIpAddress { param($ResourceGroupName,$Name,$ErrorAction) return $MockState.Ip }
function New-AzPublicIpAddress { param($ResourceGroupName,$Location,$Name,$AllocationMethod,$Sku,$DomainNameLabel,$Tag)
    $MockState.Changes++; $MockState.Ip=@{Id='/mock/ip';Location=$Location;Tags=$Tag;DnsSettings=@{Fqdn="$DomainNameLabel.$Location.cloudapp.azure.com"}}; return $MockState.Ip
}
function Get-AzNetworkInterface { param($ResourceGroupName,$Name,$ErrorAction) return $MockState.Nic }
function New-AzNetworkInterface { param($ResourceGroupName,$Location,$Name,$SubnetId,$NetworkSecurityGroupId,$PublicIpAddressId,$Tag)
    $MockState.Changes++; $MockState.Nic=@{Id='/mock/nic';Location=$Location;Tags=$Tag;NetworkSecurityGroup=@{Id=$NetworkSecurityGroupId};IpConfigurations=@(@{PublicIpAddress=@{Id=$PublicIpAddressId};Subnet=@{Id=$SubnetId}})}; return $MockState.Nic
}
function Get-AzVM { param($ResourceGroupName,$Name,$ErrorAction) return $MockState.Vm }
function New-AzVMConfig { param($VMName,$VMSize,$IdentityType,$Tags)
    Assert-That ($IdentityType -eq 'SystemAssigned') 'No system MI'
    return [pscustomobject]@{Tags=$Tags;Location=$null;StorageProfile=@{OsDisk=@{DiffDiskSettings=@{Option=$null}}};OSProfile=[pscustomobject]@{AdminPassword='INITIAL_ONLY';AdminUsername=$null;LinuxConfiguration=$null};HardwareProfile=@{VmSize=$VMSize};NetworkProfile=@{NetworkInterfaces=@()};Identity=@{PrincipalId='33333333-3333-3333-3333-333333333333'}}
}
function Set-AzVMOperatingSystem { param($VM,[switch]$Linux,$ComputerName,[pscredential]$Credential,[switch]$DisablePasswordAuthentication)
    Assert-That ($Linux -and $DisablePasswordAuthentication) 'Linux password authentication not disabled'
    Assert-That ($Credential.Password.Length -eq 0) 'VM credential password not empty'
    $VM.OSProfile.AdminUsername=$Credential.UserName; $VM.OSProfile.LinuxConfiguration=@{DisablePasswordAuthentication=$true}; return $VM
}
function Add-AzVMSshPublicKey { param($VM,$KeyData,$Path) Assert-That ($KeyData -like 'ssh-ed25519 *') 'Not actual SSH public-key material'; return $VM }
function Set-AzVMSourceImage { param($VM,$PublisherName,$Offer,$Skus,$Version) Assert-That ($PublisherName -eq 'Canonical') 'Wrong image publisher'; return $VM }
function Set-AzVMOSDisk { param($VM,$CreateOption,$StorageAccountType,$DiskSizeInGB) Assert-That ($StorageAccountType -eq 'StandardSSD_LRS') 'Wrong disk'; return $VM }
function Add-AzVMNetworkInterface { param($VM,$Id) $VM.NetworkProfile.NetworkInterfaces=@(@{Id=$Id}); return $VM }
function New-AzVM { param($ResourceGroupName,$Location,$VM,[switch]$DisableBginfoExtension)
    Assert-That ($null -eq $VM.OSProfile.AdminPassword) 'AdminPassword would serialize'
    Assert-That ($VM.OSProfile.AdminUsername -eq 'aasadmin') 'Wrong OS user'
    $VM.Location=$Location; $MockState.VmProfiles+=($VM|ConvertTo-Json -Depth 15); $MockState.Vm=$VM; $MockState.Changes++
}
function Invoke-AzVMRunCommand { param($ResourceGroupName,$VMName,$CommandId,$ScriptString)
    Assert-That ($ScriptString.Contains($ExpectedCommit)) 'Source commit not pinned'
    Assert-That (-not $ScriptString.Contains($DummyPassword) -and -not $ScriptString.Contains($DummyApiKey)) 'Secret in ARM Run Command'
    Assert-That ($ScriptString -notmatch '(?i)(Authorization|Bearer|adminpassword|sk-test)') 'Credential-like parameter in Run Command'
    Assert-That ($ScriptString.Contains('"enable_openai":true')) 'EnableOpenAI config not passed'
    if ($MockState.ExpectedVaultName) { Assert-That ($ScriptString.Contains('"vault_name":"' + $MockState.ExpectedVaultName + '"')) 'Wrong vault passed to VM startup' }; $MockState.Commands += $ScriptString
    $marker=if ($MockState.Marker) { "AAS_BOOTSTRAP_OK:$ExpectedCommit" } else {'AAS_BOOTSTRAP_OK:wrong_commit'}
    return @{Value=@(@{Message=$marker})}
}
$arguments=@{SubscriptionId=[guid]'11111111-1111-1111-1111-111111111111';DnsLabel='aas-mock-check';SourceCommit=$ExpectedCommit;Deploy=$true;EnableOpenAI=$true}
$planArguments=$arguments.Clone()
$planArguments.Remove('SourceCommit')
$planArguments.Deploy=$false
& $DeployScript @planArguments
Assert-That ($MockState.Changes -eq 0 -and $MockState.AzureContextCalls -eq 0 -and $MockState.GraphCalls -eq 0) 'Plan reached Azure'
Assert-That ($MockState.SourceRefs[-1].EndsWith('/commits/main')) 'Default source still depends on a merged/deleted branch'
& $DeployScript @arguments
Assert-That ($MockState.VmProfiles.Count -eq 1) 'VM was not provisioned once'
Assert-That ($MockState.PasswordPrompts -eq 2) 'Expected two hidden dummy secret prompts'
Assert-That ($MockState.Commands.Count -eq 1) 'Expected one bootstrap invocation'
Assert-That ($MockState.Roles.Count -eq 2) 'Expected narrowly scoped human and VM roles'
Assert-That (@($MockState.Roles|Where-Object {$_.Scope -ne '/mock/vault'}).Count -eq 0) 'Role broader than vault'
$before=$MockState.Changes
& $DeployScript @arguments
Assert-That ($MockState.Changes -eq $before) 'Owned rerun unexpectedly rewrote Azure resource/secret'
Assert-That ($MockState.PasswordPrompts -eq 2) 'Owned rerun reprompted secrets'
Assert-That ($MockState.Commands.Count -eq 2) 'Owned rerun did not re-run pinned bootstrap'
$MockState.Group.Tags=@{Application='UnrelatedApplication'}
$before=$MockState.Changes
$refused=$false
try { & $DeployScript @arguments } catch { $refused=$_.Exception.Message -match 'not tagged' }
Assert-That $refused 'Unowned group not rejected'
Assert-That ($MockState.Changes -eq $before) 'Unowned group was mutated'
Assert-That ($MockState.Commands.Count -eq 2) 'Unowned group reached bootstrap'
$MockState.Group.Tags=@{Application='AgenticAnalyticsStudio';Deployment='private-vm-v1'}
$MockState.Marker=$false
$refused=$false
try { & $DeployScript @arguments } catch { $refused=$_.Exception.Message -match 'did not complete' }
Assert-That $refused 'Wrong bootstrap marker was accepted'
$MockState.Marker=$true
$originalRules=@($MockState.Nsg.SecurityRules)
$MockState.Nsg.SecurityRules+=New-AzNetworkSecurityRuleConfig -Name 'BAD-SSH' -Protocol Tcp -Direction Inbound -Priority 120 -SourceAddressPrefix Internet -SourcePortRange '*' -DestinationAddressPrefix '*' -DestinationPortRange 22 -Access Allow
$refused=$false
try { & $DeployScript @arguments } catch {$refused=$_.Exception.Message -match 'NSG'}
Assert-That $refused 'NSG drift allowingSSH not rejected'
$MockState.Nsg.SecurityRules=$originalRules
$MockState.Nic.IpConfigurations[0].Subnet.Id='/mock/other-subnet'
$refused=$false
try { & $DeployScript @arguments } catch {$refused=$_.Exception.Message -match 'NIC'}
Assert-That $refused 'NIC subnet drift not rejected'
$MockState.Nic.IpConfigurations[0].Subnet.Id='/mock/subnet'
$MockState.Vm.StorageProfile.OsDisk.DiffDiskSettings.Option='Local'
$refused=$false
try { & $DeployScript @arguments } catch {$refused=$_.Exception.Message -match 'Existing VM'}
Assert-That $refused 'Ephemeral OS disk not rejected'
$MockState.Vm.StorageProfile.OsDisk.DiffDiskSettings.Option=$null
foreach ($mode in @('missing','truncated','symlink')) {
    $MockState.SourceMode=$mode
    $azbefore=$MockState.AzureContextCalls; $before=$MockState.Changes
    $refused=$false
    try { & $DeployScript @arguments } catch {$refused=$_.Exception.Message -match 'source|tree'}
    Assert-That $refused "Invalid source mode $mode was accepted"
    Assert-That ($MockState.AzureContextCalls -eq $azbefore -and $MockState.Changes -eq $before) 'Invalid source reached Azure operations'
}

# Explicit reuse works with an untagged group and vault, even without Graph access.
$MockState.SourceMode='valid'
$MockState.Group.Tags=@{}
$MockState.Group.Location='polandcentral'
$MockState.Vault.Tags=@{}
$MockState.Vault.VaultName='existing-test-vault'
$vaultId='/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/rg-agentic-studio/providers/Microsoft.KeyVault/vaults/existing-test-vault'
$MockState.Vault.ResourceId=$vaultId
$MockState.Secrets=@{'openai-api-key'=$true}
$MockState.SecretWrites=@()
$MockState.Roles=@()
$MockState.GraphForbidden=$true
$MockState.ExpectedVaultName='existing-test-vault'
$reuseArguments=$arguments.Clone()
$reuseArguments.ExistingVaultName='existing-test-vault'
$graphBefore=$MockState.GraphCalls; $vaultsBefore=$MockState.NewVaults; $promptsBefore=$MockState.PasswordPrompts
& $DeployScript @reuseArguments
Assert-That ($MockState.GraphCalls -eq $graphBefore) 'Reuse unexpectedly queried Graph'
Assert-That ($MockState.NewVaults -eq $vaultsBefore) 'Reuse created another vault'
Assert-That ($MockState.PasswordPrompts -eq $promptsBefore + 1) 'Reuse must only prompt for the missing login password'
Assert-That ($MockState.SecretWrites.Count -eq 1 -and $MockState.SecretWrites[0] -eq 'studio-login-password') 'Existing API key was rewritten'
Assert-That ($MockState.Group.Tags.Count -eq 0 -and $MockState.Vault.Tags.Count -eq 0) 'Existing containers were retagged'
Assert-That ($MockState.Group.Location -eq 'polandcentral') 'Resource group moved'
Assert-That ($MockState.Roles.Count -eq 1 -and $MockState.Roles[0].ObjectType -eq 'ServicePrincipal' -and
    $MockState.Roles[0].Scope -eq $vaultId -and
    $MockState.Roles[0].RoleDefinitionId -eq '4633458b-17de-408a-b874-0445c86b69e6') 'Reuse changed human roles or granted broad VM permissions'
$before=$MockState.Changes; $promptsBefore=$MockState.PasswordPrompts
& $DeployScript @reuseArguments
Assert-That ($MockState.Changes -eq $before -and $MockState.PasswordPrompts -eq $promptsBefore) 'Reuse rerun rewrote secrets, roles or resources'

function Assert-ReuseRefused([string]$Pattern) {
    $before=$MockState.Changes; $promptsBefore=$MockState.PasswordPrompts; $commandsBefore=$MockState.Commands.Count
    $refused=$false
    try { & $DeployScript @reuseArguments } catch { $refused=$_.Exception.Message -match $Pattern }
    Assert-That $refused "Invalid existing vault was not rejected: $Pattern"
    Assert-That ($MockState.Changes -eq $before -and $MockState.Commands.Count -eq $commandsBefore -and
        $MockState.PasswordPrompts -eq $promptsBefore) 'Invalid reuse mutated state, prompted for keys or reached bootstrap'
}
$vaultBefore=$MockState.Vault
$MockState.Vault=$null
Assert-ReuseRefused 'requires'
$MockState.Vault=$vaultBefore
$groupBefore=$MockState.Group
$MockState.Group=$null
Assert-ReuseRefused 'requires'
$MockState.Group=$groupBefore
$MockState.Vault.ResourceId='/subscriptions/other/resourceGroups/other/providers/Microsoft.KeyVault/vaults/other'
Assert-ReuseRefused 'does not match'
$MockState.Vault.ResourceId=$vaultId
$MockState.Vault.EnableRbacAuthorization=$false
Assert-ReuseRefused 'RBAC'
$MockState.Vault.EnableRbacAuthorization=$true
$MockState.Vault.Tags=@{Application='UnrelatedApplication'}
Assert-ReuseRefused 'another application'
$MockState.Vault.Tags=@{}
$MockState.Group.Tags=@{Application='UnrelatedApplication'}
Assert-ReuseRefused 'another application'
$MockState.Group.Tags=@{}
$MockState.Secrets=@{}
Assert-ReuseRefused 'must already contain'
$MockState.Secrets=@{'openai-api-key'=$true;'studio-login-password'=$true}
$MockState.Vm.Tags=@{Application='UnrelatedApplication'}
Assert-ReuseRefused 'not tagged'
$MockState.Vm.Tags=@{Application='AgenticAnalyticsStudio';Deployment='private-vm-v1'}

# Reject cross-region partial resources before any secret/role/network writes.
foreach ($component in @('Nsg','Vnet','Ip','Nic','Vm')) {
    $MockState[$component].Location='polandcentral'
    Assert-ReuseRefused 'outside selected location'
    $MockState[$component].Location='westeurope'
}
$reuseArguments.Location='polandcentral'
Assert-ReuseRefused 'outside selected location'
foreach ($component in @('Nsg','Vnet','Ip','Nic','Vm')) { $MockState[$component]=$null }

# Azure rejection must not switch regions or allocate a VM/IP automatically.
$MockState.BlockedLocation='polandcentral'
$before=$MockState.Changes; $commandsBefore=$MockState.Commands.Count
$refused=$false
try { & $DeployScript @reuseArguments } catch { $refused=$_.Exception.Message -match 'locationineligible' }
Assert-That $refused 'Azure region rejection was swallowed'
Assert-That ($MockState.Changes -eq $before -and $MockState.Commands.Count -eq $commandsBefore -and
    $null -eq $MockState.Ip -and $null -eq $MockState.Vm) 'Rejected region caused writes or automatic fallback'
$MockState.BlockedLocation=$null

# A deliberately selected region propagates to every component and public config.
& $DeployScript @reuseArguments
foreach ($component in @('Nsg','Vnet','Ip','Nic','Vm')) {
    Assert-That ($MockState[$component].Location -eq 'polandcentral') "$component ignored chosen region"
}
Assert-That ($MockState.Ip.DnsSettings.Fqdn -eq 'aas-mock-check.polandcentral.cloudapp.azure.com') 'DNS region mismatch'
Assert-That ($MockState.Commands[-1].Contains('"location":"polandcentral"') -and
    $MockState.Commands[-1].Contains('"hostname":"aas-mock-check.polandcentral.cloudapp.azure.com"')) 'Runtime region config mismatch'
Assert-That ($MockState.Vault.ResourceId -eq $vaultId -and $MockState.Group.Location -eq 'polandcentral') 'Existing vault/group changed'
$before=$MockState.Changes; $promptsBefore=$MockState.PasswordPrompts
& $DeployScript @reuseArguments
Assert-That ($MockState.Changes -eq $before -and $MockState.PasswordPrompts -eq $promptsBefore) 'Regional rerun rewrote state'

foreach ($bad in @('polandcentral.evil','PolandCentral','https://polandcentral',"polandcentral`n")) {
    $badArguments=$reuseArguments.Clone();$badArguments.Location=$bad
    $before=$MockState.Changes;$azbefore=$MockState.AzureContextCalls
    $refused=$false
    try { & $DeployScript @badArguments } catch { $refused=$_.Exception.Message -match 'validat' }
    Assert-That $refused 'Invalid region identifier accepted'
    Assert-That ($MockState.Changes -eq $before -and $MockState.AzureContextCalls -eq $azbefore) 'Invalid region reached Azure'
}
Write-Host 'PASS: selectable region, bound DNS/runtime config, cross-region and Azure-rejection gates; existing secret/role/tag/network/source/RBAC checks. Local mocks only; no Azure deployment.'
