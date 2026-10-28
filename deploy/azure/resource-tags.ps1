# Read-only normalization of Azure's provider-specific Tag/Tags model properties.
function Get-StudioResourceTags {
    param([AllowNull()][object]$Resource)
    $result = @{}
    if ($null -eq $Resource) { return $result }
    foreach ($field in @('Tags', 'Tag')) {
        $value = if ($Resource -is [System.Collections.IDictionary]) { $Resource[$field] }
            else { $property = $Resource.PSObject.Properties[$field]; if ($null -ne $property) { $property.Value } }
        if ($null -eq $value) { continue }
        if ($value -isnot [System.Collections.IDictionary]) { throw 'Invalid Azure resource tag metadata; refusing to guess ownership.' }
        foreach ($entry in $value.GetEnumerator()) {
            if ($entry.Key -isnot [string] -or $entry.Value -isnot [string]) { throw 'Invalid Azure resource tag entry.' }
            if ($result.ContainsKey($entry.Key) -and $result[$entry.Key] -cne $entry.Value) {
                throw 'Conflicting Tag/Tags metadata; refusing to guess ownership.'
            }
            $result[$entry.Key] = $entry.Value
        }
    }
    return $result
}
