#Requires -Version 7.2
# Actual pinned SDK, local builders/serialization only; no Azure login or New-AzVM.
param([string]$ModuleDirectory = '')
$ErrorActionPreference = 'Stop'
foreach ($module in @(@{Name='Az.Accounts';Version='5.5.3'}, @{Name='Az.Compute';Version='11.10.0'}, @{Name='Az.Network';Version='8.3.0'})) {
    $name = if ($ModuleDirectory) { Join-Path $ModuleDirectory "$($module.Name)/$($module.Version)/$($module.Name).psd1" } else { $module.Name }
    Import-Module -FullyQualifiedName @{ModuleName=$name;RequiredVersion=$module.Version} -ErrorAction Stop
}
. (Join-Path $PSScriptRoot '../deploy/azure/vm-config.ps1')
. (Join-Path $PSScriptRoot '../deploy/azure/resource-tags.ps1')
function Assert-That([bool]$Condition, [string]$Message) { if (-not $Condition) { throw $Message } }
$owner = @{Application='AgenticAnalyticsStudio';Deployment='private-vm-v1'}
foreach ($type in @([Microsoft.Azure.Commands.Network.Models.PSNetworkSecurityGroup],
    [Microsoft.Azure.Commands.Network.Models.PSVirtualNetwork],
    [Microsoft.Azure.Commands.Network.Models.PSPublicIpAddress],
    [Microsoft.Azure.Commands.Network.Models.PSNetworkInterface])) {
    $resource = [Activator]::CreateInstance($type)
    $resource.Tag = $owner.Clone()
    Assert-That ($null -eq $resource.PSObject.Properties['Tags']) 'Network model unexpectedly exposes plural Tags'
    $read = Get-StudioResourceTags $resource
    Assert-That ($read.Application -ceq $owner.Application -and $read.Deployment -ceq $owner.Deployment) 'Actual network tag ownership was lost'
    $read.Application='MODIFIED_SOFTWARE_TEST_ONLY'
    Assert-That ($resource.Tag.Application -ceq $owner.Application) 'Tag reader mutated the resource'
    foreach ($bad in @(@{}, @{Application='UnrelatedApplication'})) {
        $resource.Tag=$bad
        Assert-That ((Get-StudioResourceTags $resource).Application -ne $owner.Application) 'Missing/foreign network ownership accepted'
    }
}
foreach ($bad in @([pscustomobject]@{Tags=@{Application='FOREIGN'};Tag=$owner},
    [pscustomobject]@{Tag='not a dictionary'}, [pscustomobject]@{Tag=@{Application=7}})) {
    $refused=$false
    try { $null=Get-StudioResourceTags $bad } catch { $refused=$true }
    Assert-That $refused 'Ambiguous or malformed tag metadata accepted'
}
Assert-That ((Get-StudioResourceTags ([pscustomobject]@{Tags=$owner;Tag=$owner})).Application -ceq $owner.Application) 'Equivalent aliases rejected'
Write-Host 'PASS: actual Az.Network 8.3.0 NSG/VNet/public-IP/NIC singular Tag models, missing/foreign markers, immutable reads and conflicting metadata refusal. Offline only.'
$keyFile = Join-Path ([IO.Path]::GetTempPath()) ('aas-sdk-test-' + [guid]::NewGuid().ToString('N'))
$client = $null
try {
    & ssh-keygen -q -t ed25519 -N '' -f $keyFile
    if ($LASTEXITCODE -ne 0) { throw 'Test public-key generation failed.' }
    $publicKey = (Get-Content "$keyFile.pub" -Raw).Trim()
    foreach ($size in @('Standard_B2als_v2', 'Standard_B2s')) {
    $vm = New-StudioVMConfig -Name 'aas-offline-test' -Tags @{Application='OFFLINE_SOFTWARE_TEST'} `
        -NetworkInterfaceId '/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/rg-offline-test/providers/Microsoft.Network/networkInterfaces/offline-nic' `
        -PublicKey $publicKey -VMSize $size
    Assert-That ($null -eq $vm.OSProfile.AdminPassword) 'Actual SDK password is not null'
    Assert-That ((Get-StudioResourceTags $vm).Application -eq 'OFFLINE_SOFTWARE_TEST') 'Actual Compute plural Tags were lost'
    Assert-That ($vm.OSProfile.AdminUsername -eq 'aasadmin') 'Wrong OS user'
    Assert-That ($vm.OSProfile.LinuxConfiguration.DisablePasswordAuthentication -eq $true) 'Password authentication enabled'
    # Constructing a client for its real serializer does not send any request.
    $client = [Microsoft.Azure.Management.Compute.ComputeManagementClient]::new(
        [Microsoft.Rest.TokenCredentials]::new('OFFLINE_SOFTWARE_TEST_NOT_A_TOKEN'),
        [System.Net.Http.DelegatingHandler[]]@())
    # New-AzVM copies the PowerShell wrapper into this SDK transport model.
    $parameters = [Microsoft.Azure.Management.Compute.Models.VirtualMachine]::new()
    $parameters.Location = 'polandcentral'
    $parameters.OsProfile = $vm.OSProfile
    $parameters.HardwareProfile = $vm.HardwareProfile
    $parameters.StorageProfile = $vm.StorageProfile
    $parameters.NetworkProfile = $vm.NetworkProfile
    $json = [Microsoft.Rest.Serialization.SafeJsonConvert]::SerializeObject($parameters, $client.SerializationSettings)
    $body = ConvertFrom-Json $json -AsHashtable
    $profile = $body.properties.osProfile
    Assert-That ($null -ne $profile -and -not $profile.ContainsKey('adminPassword')) 'SDK JSON lacks OS profile or contains adminPassword'
    Assert-That ($profile.linuxConfiguration.disablePasswordAuthentication -eq $true) 'Serialized password-auth flag changed'
    Assert-That ($profile.linuxConfiguration.ssh.publicKeys.Count -eq 1 -and
        $profile.linuxConfiguration.ssh.publicKeys[0].keyData -ceq $publicKey) 'Serialized public key changed'
    Assert-That ($body.properties.hardwareProfile.vmSize -eq $size) 'Explicit VM size changed'
    Assert-That ($body.properties.storageProfile.osDisk.managedDisk.storageAccountType -eq 'StandardSSD_LRS') 'Disk changed'
    # Reproduce the reported failure using the actual CLR-typed SDK property.
    $vm.OSProfile.AdminPassword = $null
    Assert-That ($null -ne $vm.OSProfile.AdminPassword -and $vm.OSProfile.AdminPassword.Length -eq 0) 'Typed-null regression not reproduced'
    $badBody = ConvertFrom-Json ([Microsoft.Rest.Serialization.SafeJsonConvert]::SerializeObject($parameters, $client.SerializationSettings)) -AsHashtable
    Assert-That ($badBody.properties.osProfile.ContainsKey('adminPassword')) 'Expected empty-password serialization not reproduced'
    Write-Host "PASS: actual Az.Compute 11.10.0 $size builders/serializer retain explicit size, disk and SSH-only config; typed-null bug reproduced. Offline only."
    $client.Dispose(); $client=$null
    }
} finally {
    if ($client) { $client.Dispose() }
    Remove-Item -LiteralPath $keyFile, "$keyFile.pub" -ErrorAction SilentlyContinue
}
