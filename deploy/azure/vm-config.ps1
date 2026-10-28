# Pure local Az.Compute builders only: no authentication, requests or resources.
function New-StudioVMConfig {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$NetworkInterfaceId,
        [Parameter(Mandatory)][string]$PublicKey,
        [Parameter(Mandatory)][hashtable]$Tags
    )
    $vm = New-AzVMConfig -VMName $Name -VMSize Standard_B2als_v2 -IdentityType SystemAssigned -Tags $Tags
    # Credential is optional. Omit it so the SDK leaves AdminPassword truly null.
    # Assigning $null to that typed string property in PowerShell produces ''.
    $vm = Set-AzVMOperatingSystem -VM $vm -Linux -ComputerName $Name -DisablePasswordAuthentication
    $vm.OSProfile.AdminUsername = 'aasadmin'
    $vm = Add-AzVMSshPublicKey -VM $vm -KeyData $PublicKey -Path '/home/aasadmin/.ssh/authorized_keys'
    $vm = Set-AzVMSourceImage -VM $vm -PublisherName Canonical -Offer ubuntu-24_04-lts -Skus server -Version latest
    $vm = Set-AzVMOSDisk -VM $vm -CreateOption FromImage -StorageAccountType StandardSSD_LRS -DiskSizeInGB 32
    $vm = Add-AzVMNetworkInterface -VM $vm -Id $NetworkInterfaceId
    $linux = $vm.OSProfile.LinuxConfiguration
    if ($null -ne $vm.OSProfile.AdminPassword -or $linux.DisablePasswordAuthentication -ne $true -or
        $null -ne $vm.OSProfile.WindowsConfiguration -or $linux.Ssh.PublicKeys.Count -ne 1 -or
        $linux.Ssh.PublicKeys[0].Path -cne '/home/aasadmin/.ssh/authorized_keys' -or
        $linux.Ssh.PublicKeys[0].KeyData -cne $PublicKey) {
        throw 'VM configuration must omit the OS password and retain SSH-only authentication.'
    }
    return $vm
}
