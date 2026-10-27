#Requires -Version 7.2
[CmdletBinding()]
param(
    [Parameter(Mandatory)][guid]$SubscriptionId,
    [Parameter(Mandatory)][ValidatePattern('^[a-z][a-z0-9-]{1,61}[a-z0-9]$')][string]$DnsLabel,
    [guid]$AdminObjectId = [guid]::Empty,
    [ValidatePattern('^$|^[0-9a-f]{40}$')][string]$SourceCommit = '',
    [switch]$Deploy,
    [switch]$EnableOpenAI
)
$ErrorActionPreference = 'Stop'
$VerbosePreference = 'SilentlyContinue'
$DebugPreference = 'SilentlyContinue'
$ProgressPreference = 'SilentlyContinue'
$location = 'westeurope'
$group = 'rg-agentic-studio'
$vmName = 'aas-studio'
$tag = @{ Application = 'AgenticAnalyticsStudio'; Deployment = 'private-vm-v1' }
$seed = [Text.Encoding]::UTF8.GetBytes("$SubscriptionId/$DnsLabel")
$suffix = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($seed)).ToLower().Substring(0, 18)
$vaultName = "aas$suffix"
$hostname = "$DnsLabel.westeurope.cloudapp.azure.com"
$githubHeaders = @{ 'User-Agent' = 'AgenticAnalyticsStudio-Deployment'; Accept = 'application/vnd.github+json' }
$ref = if ($SourceCommit) { $SourceCommit } else { 'deploy/azure-private-studio' }
$resolved = Invoke-RestMethod -Uri "https://api.github.com/repos/sayac007/Agentic-Analytics-Studio/commits/$ref" -Headers $githubHeaders
if ($resolved.sha -notmatch '^[0-9a-f]{40}$' -or ($SourceCommit -and $resolved.sha -cne $SourceCommit)) {
    throw 'GitHub did not verify the requested source commit.'
}
$SourceCommit = $resolved.sha
$treeSha = $resolved.commit.tree.sha
if ($treeSha -notmatch '^[0-9a-f]{40}$') { throw 'GitHub did not return the commit tree identity.' }
$tree = Invoke-RestMethod -Uri "https://api.github.com/repos/sayac007/Agentic-Analytics-Studio/git/trees/${treeSha}?recursive=1" -Headers $githubHeaders
if ($tree.truncated -ne $false) { throw 'Source tree validation is incomplete; no Azure changes were made.' }
$requiredFiles = @('Dockerfile', '.dockerignore', 'demo/hosting.py', 'requirements.lock', 'requirements-demo.lock',
    'deploy/azure/Deploy-Studio.ps1', 'deploy/azure/bootstrap.sh', 'deploy/azure/refresh-secrets.py',
    'deploy/azure/compose.yaml', 'deploy/azure/Caddyfile', 'deploy/azure/agentic-studio.service')
foreach ($path in $requiredFiles) {
    if (-not @($tree.tree | Where-Object { $_.path -ceq $path -and $_.type -eq 'blob' -and $_.mode -in @('100644', '100755') }).Count) {
        throw "The pinned source lacks required regular file $path; no Azure changes were made."
    }
}
Write-Host "Subscription: $SubscriptionId | Resource group: $group | Location: $location"
Write-Host "VM: $vmName, Standard_B2als_v2, Ubuntu 24.04 x86, Standard SSD 32 GiB"
Write-Host "URL: https://$hostname | Key Vault: $vaultName | Source: $SourceCommit"
Write-Host "Optional OpenAI enabled: $($EnableOpenAI.IsPresent). BasicAuth user: studio."
Write-Host 'Indicative recurring infrastructure: approximately USD37.59/month; API, tax and variable operations extra.'
if (-not $Deploy) {
    Write-Host 'PLAN ONLY: no Azure resources, role assignments or secrets were changed. Add -Deploy to provision.'
    return
}
Get-Command Get-AzContext, New-AzVM, New-AzKeyVault -ErrorAction Stop | Out-Null
Set-AzContext -Subscription $SubscriptionId.ToString() | Out-Null
if ($AdminObjectId -eq [guid]::Empty) {
    $AdminObjectId = [guid](Get-AzADUser -SignedIn).Id
}
if ($AdminObjectId -eq [guid]::Empty) { throw 'Pass your human account object ID with -AdminObjectId.' }

function Assert-Owned($Resource) {
    if ($null -ne $Resource -and ($null -eq $Resource.Tags -or $Resource.Tags['Application'] -ne $tag.Application)) {
        throw 'An existing resource is not tagged for this deployment; refusing to modify it.'
    }
}
function Ensure-Role([string]$ObjectId, [string]$RoleId, [string]$Scope, [string]$ObjectType) {
    $existing = Get-AzRoleAssignment -ObjectId $ObjectId -RoleDefinitionId $RoleId -Scope $Scope
    if (-not $existing) {
        for ($attempt = 0; $attempt -lt 6; $attempt++) {
            try {
                New-AzRoleAssignment -ObjectId $ObjectId -RoleDefinitionId $RoleId -Scope $Scope -ObjectType $ObjectType | Out-Null
                break
            } catch {
                if ($attempt -eq 5) { throw 'Role assignment failed; check role-assignment rights and managed-identity propagation.' }
                Start-Sleep -Seconds 10
            }
        }
    }
}
function Ensure-Secret([string]$Name, [string[]]$ExistingNames) {
    if ($Name -in $ExistingNames) {
        Write-Host "Reusing existing Key Vault secret: $Name"
        return
    }
    $prompt = if ($Name -eq 'studio-login-password') {
        'Create studio login password (16-64 ASCII characters; input hidden)'
    } else { 'Paste OpenAI API key (input hidden; or create openai-api-key in the portal before rerunning)' }
    $value = Read-Host $prompt -AsSecureString
    $pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($value)
    try {
        # Validate only in memory; never interpolate this value into commands, logs or ARM.
        $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
        if (($Name -eq 'studio-login-password' -and $plain -cnotmatch '^[\x20-\x7e]{16,64}$') -or
            ($Name -eq 'openai-api-key' -and $plain -cnotmatch '^sk-[A-Za-z0-9_-]{16,512}$')) {
            throw 'Secret format is unsupported; no secret was written.'
        }
        try { Set-AzKeyVaultSecret -VaultName $vaultName -Name $Name -SecretValue $value | Out-Null }
        catch { throw "Key Vault secret write failed for $Name; check the account role and retry." }
    } finally {
        $plain = $null
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
        $value.Dispose()
    }
}

try {
    $rg = Get-AzResourceGroup -Name $group -ErrorAction SilentlyContinue
    Assert-Owned $rg
    if (-not $rg) { New-AzResourceGroup -Name $group -Location $location -Tag $tag | Out-Null }
    $vault = Get-AzKeyVault -VaultName $vaultName -ResourceGroupName $group -ErrorAction SilentlyContinue
    Assert-Owned $vault
    if (-not $vault) {
        $vault = New-AzKeyVault -VaultName $vaultName -ResourceGroupName $group -Location $location `
            -Sku Standard -DisableRbacAuthorization:$false -SoftDeleteRetentionInDays 7 -Tag $tag
    }
    if (-not $vault.EnableRbacAuthorization) { throw 'The existing vault must use Azure RBAC; no access policy was changed.' }
    Ensure-Role $AdminObjectId.ToString() 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7' $vault.ResourceId 'User'
    $secretNames = $null
    for ($attempt = 0; $attempt -lt 12; $attempt++) {
        try { $secretNames = @(Get-AzKeyVaultSecret -VaultName $vaultName | ForEach-Object Name); break }
        catch {
            if ($attempt -eq 11) { throw 'Key Vault RBAC is not ready. Retry deployment after role propagation.' }
            Start-Sleep -Seconds 10
        }
    }
    Ensure-Secret 'studio-login-password' $secretNames
    if ($EnableOpenAI) { Ensure-Secret 'openai-api-key' $secretNames }

    $nsg = Get-AzNetworkSecurityGroup -ResourceGroupName $group -Name 'aas-web' -ErrorAction SilentlyContinue
    Assert-Owned $nsg
    if (-not $nsg) {
        $rules = @(
            New-AzNetworkSecurityRuleConfig -Name 'HTTPS' -Protocol Tcp -Direction Inbound -Priority 100 `
                -SourceAddressPrefix Internet -SourcePortRange '*' -DestinationAddressPrefix '*' -DestinationPortRange 443 -Access Allow
            New-AzNetworkSecurityRuleConfig -Name 'ACME-HTTP' -Protocol Tcp -Direction Inbound -Priority 110 `
                -SourceAddressPrefix Internet -SourcePortRange '*' -DestinationAddressPrefix '*' -DestinationPortRange 80 -Access Allow
            New-AzNetworkSecurityRuleConfig -Name 'Deny-other-inbound' -Protocol '*' -Direction Inbound -Priority 4096 `
                -SourceAddressPrefix '*' -SourcePortRange '*' -DestinationAddressPrefix '*' -DestinationPortRange '*' -Access Deny
        )
        $nsg = New-AzNetworkSecurityGroup -ResourceGroupName $group -Location $location -Name 'aas-web' -SecurityRules $rules -Tag $tag
    }
    $allowed = @($nsg.SecurityRules | Where-Object { $_.Direction -eq 'Inbound' -and $_.Access -eq 'Allow' })
    $ports = @($allowed | ForEach-Object DestinationPortRange)
    if ($allowed.Count -ne 2 -or '80' -notin $ports -or '443' -notin $ports -or @($allowed | Where-Object {
        $_.Protocol -ne 'Tcp' -or $_.SourceAddressPrefix -ne 'Internet' -or $_.SourcePortRange -ne '*' -or
        $_.DestinationAddressPrefix -ne '*'
    }).Count) {
        throw 'Existing NSG does not have the expected 80/443-only policy; review it manually.'
    }
    $deny = @($nsg.SecurityRules | Where-Object {
        $_.Direction -eq 'Inbound' -and $_.Access -eq 'Deny' -and $_.Priority -eq 4096 -and
        $_.Protocol -eq '*' -and $_.SourceAddressPrefix -eq '*' -and $_.DestinationPortRange -eq '*' -and
        $_.SourcePortRange -eq '*' -and $_.DestinationAddressPrefix -eq '*'
    })
    if ($deny.Count -ne 1) { throw 'The explicit deny-other-inbound rule is required, including for VNet traffic.' }
    $vnet = Get-AzVirtualNetwork -ResourceGroupName $group -Name 'aas-network' -ErrorAction SilentlyContinue
    Assert-Owned $vnet
    if (-not $vnet) {
        $subnet = New-AzVirtualNetworkSubnetConfig -Name 'studio' -AddressPrefix '10.17.0.0/24'
        $vnet = New-AzVirtualNetwork -ResourceGroupName $group -Location $location -Name 'aas-network' `
            -AddressPrefix '10.17.0.0/24' -Subnet $subnet -Tag $tag
    }
    $ip = Get-AzPublicIpAddress -ResourceGroupName $group -Name 'aas-public-ip' -ErrorAction SilentlyContinue
    Assert-Owned $ip
    if (-not $ip) {
        $ip = New-AzPublicIpAddress -ResourceGroupName $group -Location $location -Name 'aas-public-ip' `
            -AllocationMethod Static -Sku Standard -DomainNameLabel $DnsLabel -Tag $tag
    }
    if ($ip.DnsSettings.Fqdn -cne $hostname) { throw 'The existing public IP has a different DNS name; refusing to repoint it.' }
    $nic = Get-AzNetworkInterface -ResourceGroupName $group -Name 'aas-nic' -ErrorAction SilentlyContinue
    Assert-Owned $nic
    if (-not $nic) {
        $nic = New-AzNetworkInterface -ResourceGroupName $group -Location $location -Name 'aas-nic' `
            -SubnetId $vnet.Subnets[0].Id -NetworkSecurityGroupId $nsg.Id -PublicIpAddressId $ip.Id -Tag $tag
    }
    if ($nic.IpConfigurations.Count -ne 1 -or $nic.NetworkSecurityGroup.Id -ne $nsg.Id -or
        $nic.IpConfigurations[0].PublicIpAddress.Id -ne $ip.Id -or $nic.IpConfigurations[0].Subnet.Id -ne $vnet.Subnets[0].Id) {
        throw 'The existing NIC is not bound to the reviewed NSG/public IP; refusing to deploy.'
    }
    $vm = Get-AzVM -ResourceGroupName $group -Name $vmName -ErrorAction SilentlyContinue
    Assert-Owned $vm
    if (-not $vm) {
        $sshFile = Join-Path ([IO.Path]::GetTempPath()) ('aas-ssh-' + [guid]::NewGuid().ToString('N'))
        try {
            & ssh-keygen -q -t ed25519 -N '' -f $sshFile
            if ($LASTEXITCODE -ne 0) { throw 'Temporary SSH public-key generation failed.' }
            $credential = [PSCredential]::new('aasadmin', [Security.SecureString]::new())
            $vm = New-AzVMConfig -VMName $vmName -VMSize Standard_B2als_v2 -IdentityType SystemAssigned -Tags $tag
            $vm = Set-AzVMOperatingSystem -VM $vm -Linux -ComputerName $vmName -Credential $credential -DisablePasswordAuthentication
            $vm.OSProfile.AdminPassword = $null
            $vm = Add-AzVMSshPublicKey -VM $vm -KeyData (Get-Content "$sshFile.pub" -Raw).Trim() -Path '/home/aasadmin/.ssh/authorized_keys'
            $vm = Set-AzVMSourceImage -VM $vm -PublisherName Canonical -Offer ubuntu-24_04-lts -Skus server -Version latest
            $vm = Set-AzVMOSDisk -VM $vm -CreateOption FromImage -StorageAccountType StandardSSD_LRS -DiskSizeInGB 32
            $vm = Add-AzVMNetworkInterface -VM $vm -Id $nic.Id
            if ($null -ne $vm.OSProfile.AdminPassword) { throw 'An OS password must not be serialized.' }
            New-AzVM -ResourceGroupName $group -Location $location -VM $vm -DisableBginfoExtension | Out-Null
        } finally {
            if ($sshFile) { Remove-Item -LiteralPath $sshFile, "$sshFile.pub" -ErrorAction SilentlyContinue }
        }
        $vm = Get-AzVM -ResourceGroupName $group -Name $vmName
    }
    if ($vm.Location -ne $location -or $vm.StorageProfile.OsDisk.DiffDiskSettings.Option -eq 'Local' -or
        $vm.HardwareProfile.VmSize -ne 'Standard_B2als_v2' -or $vm.NetworkProfile.NetworkInterfaces.Count -ne 1 -or
        $vm.NetworkProfile.NetworkInterfaces[0].Id -ne $nic.Id) { throw 'Existing VM size or network differs from this deployment.' }
    if (-not $vm.Identity.PrincipalId) { throw 'The VM needs its system-assigned managed identity.' }
    Ensure-Role $vm.Identity.PrincipalId '4633458b-17de-408a-b874-0445c86b69e6' $vault.ResourceId 'ServicePrincipal'
    $publicConfig = @{ source_commit = $SourceCommit; vault_name = $vaultName; hostname = $hostname;
                       enable_openai = $EnableOpenAI.IsPresent } | ConvertTo-Json -Compress
    # Run Command receives public configuration only. It retrieves no secret in this script.
    $command = @"
set -eu
umask 077
install -d -m 0700 /etc/aas
cat > /etc/aas/deploy.json <<'AAS_PUBLIC_CONFIGURATION'
$publicConfig
AAS_PUBLIC_CONFIGURATION
curl --fail --silent --show-error --proto '=https' --tlsv1.2 --retry 3 'https://raw.githubusercontent.com/sayac007/Agentic-Analytics-Studio/$SourceCommit/deploy/azure/bootstrap.sh' --output /tmp/aas-bootstrap.sh
bash /tmp/aas-bootstrap.sh
"@
    $result = Invoke-AzVMRunCommand -ResourceGroupName $group -VMName $vmName -CommandId RunShellScript -ScriptString $command
    if (-not @($result.Value | Where-Object { $_.Message -match "AAS_BOOTSTRAP_OK:$SourceCommit" }).Count) {
        throw 'VM bootstrap did not complete. Inspect Run Command status; no secrets should be included in its arguments.'
    }
    Write-Host "Deployment command completed. Open https://$hostname and sign in as studio."
    Write-Host 'The API key stays in Key Vault and private runtime memory/files. Adding a key alone does not enable OpenAI.'
} catch {
    Write-Warning 'Deployment stopped. Partially created resources can continue to incur cost; inspect the resource group. No automatic deletion was performed.'
    throw
}
