[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [string]$ConfigRoot = (Join-Path $env:APPDATA 'io.github.clash-verge-rev.clash-verge-rev'),
    [string]$ProxyName,
    [string]$GroupName = 'Claude',
    [string]$RestoreBackup,
    [switch]$ReloadNow
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$managedMarker = 'clash-verge-claude-routing managed block'

function Write-Utf8Atomic {
    param([string]$Path, [string]$Content)

    $directory = [System.IO.Path]::GetDirectoryName($Path)
    $temporary = Join-Path $directory ('.' + [System.IO.Path]::GetFileName($Path) + '.tmp-' + [guid]::NewGuid().ToString('N'))
    $encoding = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($temporary, $Content, $encoding)
    Move-Item -LiteralPath $temporary -Destination $Path -Force
}

function Get-NewLine {
    param([string]$Text)
    if ($Text.Contains("`r`n")) { return "`r`n" }
    return "`n"
}

function Remove-ManagedBlock {
    param([string]$Text)

    $escaped = [regex]::Escape($managedMarker)
    $expression = [regex]::new("(?ms)^# BEGIN $escaped\r?\n.*?^# END $escaped\r?\n?")
    return $expression.Replace($Text, '', 1)
}

function Insert-PrependBlock {
    param([string]$Text, [string[]]$BlockLines)

    $newline = Get-NewLine $Text
    $block = @("# BEGIN $managedMarker") + $BlockLines + @("# END $managedMarker")
    $blockText = $block -join $newline
    $empty = [regex]::new('(?m)^prepend:\s*\[\]\s*$')
    if ($empty.IsMatch($Text)) {
        return $empty.Replace($Text, "prepend:$newline$blockText", 1)
    }

    $plain = [regex]::new('(?m)^prepend:\s*$')
    if (-not $plain.IsMatch($Text)) {
        throw 'Enhancement file has no supported prepend key'
    }
    return $plain.Replace($Text, "prepend:$newline$blockText", 1)
}

function ConvertTo-YamlSingleQuoted {
    param([string]$Value)
    return "'" + $Value.Replace("'", "''") + "'"
}

function Set-GroupEnhancement {
    param([string]$Path, [string]$Name, [string]$Node)

    $text = [System.IO.File]::ReadAllText($Path)
    $text = Remove-ManagedBlock $text
    $escapedName = [regex]::Escape($Name)
    $legacyPattern = '(?ms)^- name:\s*(?:''{0}''|"{0}"|{0})\s*\r?\n(?:^[ \t]+[^\r\n]*(?:\r?\n|$))*' -f $escapedName
    $legacyGroup = [regex]::new($legacyPattern)
    $text = $legacyGroup.Replace($text, '', 1)
    $block = @(
        ('- name: ' + (ConvertTo-YamlSingleQuoted $Name))
        '  type: select',
        '  proxies:',
        ('  - ' + (ConvertTo-YamlSingleQuoted $Node))
    )
    $text = Insert-PrependBlock $text $block
    Write-Utf8Atomic $Path $text
}

function Set-RuleEnhancement {
    param([string]$Path, [string]$Name)

    $rules = @(
        '- DOMAIN,localhost,DIRECT',
        '- DOMAIN-SUFFIX,local,DIRECT',
        '- IP-CIDR,127.0.0.0/8,DIRECT,no-resolve',
        '- IP-CIDR,10.0.0.0/8,DIRECT,no-resolve',
        '- IP-CIDR,172.16.0.0/12,DIRECT,no-resolve',
        '- IP-CIDR,192.168.0.0/16,DIRECT,no-resolve',
        '- IP-CIDR,100.64.0.0/10,DIRECT,no-resolve',
        '- IP-CIDR6,::1/128,DIRECT,no-resolve',
        '- IP-CIDR6,fc00::/7,DIRECT,no-resolve',
        '- IP-CIDR6,fe80::/10,DIRECT,no-resolve',
        "- DOMAIN-SUFFIX,anthropic.com,$Name",
        "- DOMAIN-SUFFIX,claude.ai,$Name",
        "- DOMAIN-SUFFIX,claude.com,$Name",
        "- DOMAIN-SUFFIX,claudeusercontent.com,$Name",
        "- PROCESS-NAME,claude.exe,$Name"
    )

    $text = [System.IO.File]::ReadAllText($Path)
    $text = Remove-ManagedBlock $text
    foreach ($rule in $rules) {
        $expression = [regex]::new('(?m)^' + [regex]::Escape($rule) + '\s*\r?\n?')
        $text = $expression.Replace($text, '')
    }
    $text = Insert-PrependBlock $text $rules
    Write-Utf8Atomic $Path $text
}

function Set-ScalarValue {
    param([string]$Path, [string]$Key, [string]$Value)

    $text = [System.IO.File]::ReadAllText($Path)
    $newline = Get-NewLine $text
    $expression = [regex]::new('(?m)^' + [regex]::Escape($Key) + ':\s*.*$')
    $count = $expression.Matches($text).Count
    if ($count -gt 1) { throw "Multiple $Key keys found in $Path" }
    if ($count -eq 1) {
        $text = $expression.Replace($text, "$Key`: $Value", 1)
    } else {
        $text = $text.TrimEnd("`r", "`n") + $newline + "$Key`: $Value" + $newline
    }
    Write-Utf8Atomic $Path $text
}

function Get-ProfileEnhancements {
    param([string]$Root)

    $profilesPath = Join-Path $Root 'profiles.yaml'
    if (-not (Test-Path -LiteralPath $profilesPath)) { throw "Missing $profilesPath" }
    $lines = Get-Content -Encoding UTF8 $profilesPath
    $currentLine = $lines | Where-Object { $_ -match '^current:\s*\S+' } | Select-Object -First 1
    if (-not $currentLine) { throw 'Unable to find the active profile uid' }
    $current = ([regex]::Match($currentLine, '^current:\s*(\S+)')).Groups[1].Value.Trim("'", '"')

    $start = -1
    for ($index = 0; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -match ('^- uid:\s*' + [regex]::Escape($current) + '\s*$')) { $start = $index; break }
    }
    if ($start -lt 0) { throw "Active profile $current is not present in profiles.yaml" }

    $end = $lines.Count
    for ($index = $start + 1; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -match '^- uid:\s*') { $end = $index; break }
    }
    $block = @($lines[$start..($end - 1)])
    $optionStart = -1
    for ($index = 0; $index -lt $block.Count; $index++) {
        if ($block[$index] -match '^\s+option:\s*$') { $optionStart = $index; break }
    }
    if ($optionStart -lt 0) { throw "Active profile $current has no enhancement options" }

    $options = @{}
    for ($index = $optionStart + 1; $index -lt $block.Count; $index++) {
        $match = [regex]::Match($block[$index], '^\s+(merge|rules|groups):\s*(\S+)\s*$')
        if ($match.Success) { $options[$match.Groups[1].Value] = $match.Groups[2].Value.Trim("'", '"') }
    }
    foreach ($required in @('merge', 'rules', 'groups')) {
        if (-not $options.ContainsKey($required)) { throw "Active profile $current is missing the $required enhancement" }
    }

    $profileDirectory = Join-Path $Root 'profiles'
    return [pscustomobject]@{
        CurrentUid = $current
        MergePath = Join-Path $profileDirectory ($options.merge + '.yaml')
        RulesPath = Join-Path $profileDirectory ($options.rules + '.yaml')
        GroupsPath = Join-Path $profileDirectory ($options.groups + '.yaml')
    }
}

function Get-CoreConnection {
    param([string]$Root)

    $configPath = Join-Path $Root 'config.yaml'
    $lines = Get-Content -Encoding UTF8 $configPath
    $controllerLine = $lines | Where-Object { $_ -match '^external-controller:\s*' } | Select-Object -First 1
    if (-not $controllerLine) { throw 'external-controller is missing from config.yaml' }
    $controller = ([regex]::Match($controllerLine, '^external-controller:\s*(.+)$')).Groups[1].Value.Trim().Trim("'", '"')
    $secretLine = $lines | Where-Object { $_ -match '^secret:\s*' } | Select-Object -First 1
    $headers = @{}
    if ($secretLine) {
        $secret = ([regex]::Match($secretLine, '^secret:\s*(.*)$')).Groups[1].Value.Trim().Trim("'", '"')
        if ($secret) { $headers.Authorization = "Bearer $secret" }
    }
    return [pscustomobject]@{ BaseUri = "http://$controller"; Headers = $headers }
}

function Invoke-CoreGet {
    param($Connection, [string]$Path)

    $response = Invoke-WebRequest -UseBasicParsing -Uri ($Connection.BaseUri + $Path) -Method Get -Headers $Connection.Headers
    $stream = $response.RawContentStream
    $stream.Position = 0
    $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::UTF8, $true, 1024, $true)
    try {
        $json = $reader.ReadToEnd()
    } finally {
        $reader.Dispose()
    }
    return $json | ConvertFrom-Json
}

function Resolve-LeafProxy {
    param($Connection, [string]$Requested)

    $proxyMap = (Invoke-CoreGet $Connection '/proxies').proxies
    $name = if ($Requested) { $Requested } else { 'GLOBAL' }
    $seen = @{}
    for ($depth = 0; $depth -lt 20; $depth++) {
        if ($seen.ContainsKey($name)) { throw "Proxy selection loop detected at $name" }
        $seen[$name] = $true
        $property = $proxyMap.PSObject.Properties[$name]
        if (-not $property) { throw "Proxy or group not found: $name" }
        $item = $property.Value
        $nowProperty = $item.PSObject.Properties['now']
        if ($nowProperty -and $nowProperty.Value -and $nowProperty.Value -ne $name) {
            $name = [string]$nowProperty.Value
            continue
        }
        if ($name -in @('DIRECT', 'REJECT', 'REJECT-DROP', 'PASS', 'COMPATIBLE')) {
            throw "Unsafe fixed Claude exit: $name"
        }
        return $name
    }
    throw 'Proxy selection depth exceeded 20'
}

function New-Backup {
    param([string]$Root, [string[]]$Files, [string]$ProfileUid)

    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $directory = Join-Path $Root ("backups\clash-verge-claude-routing\$stamp")
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
    $entries = @()
    foreach ($source in $Files) {
        if (-not (Test-Path -LiteralPath $source)) { throw "Missing source file: $source" }
        $backupFile = [System.IO.Path]::GetFileName($source)
        Copy-Item -LiteralPath $source -Destination (Join-Path $directory $backupFile)
        $entries += [pscustomobject]@{ Source = $source; BackupFile = $backupFile }
    }
    $manifest = [pscustomobject]@{ Created = (Get-Date).ToString('o'); ProfileUid = $ProfileUid; Files = $entries }
    $manifestPath = Join-Path $directory 'manifest.json'
    Write-Utf8Atomic $manifestPath ($manifest | ConvertTo-Json -Depth 5)
    return $directory
}

function Restore-BackupFiles {
    param([string]$Directory)

    $manifestPath = Join-Path $Directory 'manifest.json'
    if (-not (Test-Path -LiteralPath $manifestPath)) { throw "Missing backup manifest: $manifestPath" }
    $manifest = Get-Content -Raw -Encoding UTF8 $manifestPath | ConvertFrom-Json
    foreach ($entry in @($manifest.Files)) {
        $backupFile = Join-Path $Directory ([string]$entry.BackupFile)
        if (-not (Test-Path -LiteralPath $backupFile)) { throw "Missing backup file: $backupFile" }
        Copy-Item -LiteralPath $backupFile -Destination ([string]$entry.Source) -Force
    }
}

function Restart-ClashVerge {
    param([string]$Root)

    $app = Get-Process -Name 'clash-verge' -ErrorAction SilentlyContinue | Select-Object -First 1
    $executable = if ($app) { $app.Path } else { Join-Path $env:ProgramFiles 'Clash Verge\clash-verge.exe' }
    if (-not (Test-Path -LiteralPath $executable)) { throw "Clash Verge executable not found: $executable" }
    if ($app) { Stop-Process -Id $app.Id }
    Start-Sleep -Seconds 2
    Start-Process -FilePath $executable -WindowStyle Hidden

    $connection = Get-CoreConnection $Root
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        try {
            Invoke-CoreGet $connection '/configs' | Out-Null
            return $connection
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    throw 'Clash Verge control API did not become ready within 30 seconds'
}

function Test-ActiveConfiguration {
    param([string]$Root, $Connection, [string]$Name, [string]$Node)

    $generated = Join-Path $Root 'clash-verge.yaml'
    $mihomo = (Get-Process -Name 'verge-mihomo' -ErrorAction SilentlyContinue | Select-Object -First 1).Path
    if (-not $mihomo) { $mihomo = Join-Path $env:ProgramFiles 'Clash Verge\verge-mihomo.exe' }
    & $mihomo -t -d $Root -f $generated
    if ($LASTEXITCODE -ne 0) { throw 'Mihomo rejected the generated configuration' }

    $core = Invoke-CoreGet $Connection '/configs'
    $encodedName = [uri]::EscapeDataString($Name)
    $group = Invoke-CoreGet $Connection ("/proxies/$encodedName")
    if ($core.mode -ne 'rule') { throw "Runtime mode is $($core.mode), not rule" }
    if ($core.'find-process-mode' -ne 'always') { throw 'find-process-mode is not always' }
    if ($group.now -ne $Node -or @($group.all).Count -ne 1) { throw 'Claude group is not pinned to exactly one expected node' }

    $patterns = @(
        "DOMAIN-SUFFIX,anthropic.com,$Name",
        "DOMAIN-SUFFIX,claude.ai,$Name",
        "DOMAIN-SUFFIX,claude.com,$Name",
        "DOMAIN-SUFFIX,claudeusercontent.com,$Name",
        "PROCESS-NAME,claude.exe,$Name"
    )
    $content = [System.IO.File]::ReadAllText($generated)
    foreach ($pattern in $patterns) {
        if (-not $content.Contains($pattern)) { throw "Generated configuration is missing: $pattern" }
    }
}

if ($GroupName.Contains(',') -or $GroupName.Contains("`n") -or $GroupName.Contains("`r")) {
    throw 'GroupName cannot contain commas or newlines'
}
if (-not (Test-Path -LiteralPath $ConfigRoot)) { throw "ConfigRoot does not exist: $ConfigRoot" }

if ($RestoreBackup) {
    $restoreAction = if ($ReloadNow) { 'Restore routing backup and reload Clash Verge' } else { 'Restore routing backup without reloading Clash Verge' }
    if ($PSCmdlet.ShouldProcess($RestoreBackup, $restoreAction)) {
        Restore-BackupFiles $RestoreBackup
        if ($ReloadNow) { Restart-ClashVerge $ConfigRoot | Out-Null }
        Write-Output ([pscustomobject]@{ Restored = $true; PendingReload = (-not $ReloadNow); Backup = $RestoreBackup })
    }
    return
}

$profile = Get-ProfileEnhancements $ConfigRoot
$connection = Get-CoreConnection $ConfigRoot
$resolvedProxy = Resolve-LeafProxy $connection $ProxyName
$configPath = Join-Path $ConfigRoot 'config.yaml'
$files = @($profile.MergePath, $profile.GroupsPath, $profile.RulesPath)
if ($ReloadNow) { $files += $configPath }

Write-Output ([pscustomobject]@{
    ProfileUid = $profile.CurrentUid
    FixedProxy = $resolvedProxy
    MergeFile = $profile.MergePath
    GroupsFile = $profile.GroupsPath
    RulesFile = $profile.RulesPath
    PersistentConfig = $configPath
})

$action = if ($ReloadNow) { "Pin $GroupName to $resolvedProxy and reload in Rule Mode" } else { "Prepare $GroupName pinned to $resolvedProxy without reloading" }
if (-not $PSCmdlet.ShouldProcess($ConfigRoot, $action)) { return }

$backupDirectory = New-Backup $ConfigRoot $files $profile.CurrentUid
try {
    Set-ScalarValue $profile.MergePath 'find-process-mode' 'always'
    Set-GroupEnhancement $profile.GroupsPath $GroupName $resolvedProxy
    Set-RuleEnhancement $profile.RulesPath $GroupName
    if (-not $ReloadNow) {
        Write-Output ([pscustomobject]@{
            Applied = $true
            PendingReload = $true
            ProfileUid = $profile.CurrentUid
            Group = $GroupName
            FixedProxy = $resolvedProxy
            Backup = $backupDirectory
        })
        return
    }
    Set-ScalarValue $configPath 'mode' 'rule'
    $connection = Restart-ClashVerge $ConfigRoot
    Invoke-WebRequest -UseBasicParsing -Uri ($connection.BaseUri + '/configs') -Method Patch -Headers $connection.Headers -ContentType 'application/json' -Body '{"mode":"rule"}' | Out-Null
    Test-ActiveConfiguration $ConfigRoot $connection $GroupName $resolvedProxy
} catch {
    $failure = $_
    try {
        Restore-BackupFiles $backupDirectory
        if ($ReloadNow) { Restart-ClashVerge $ConfigRoot | Out-Null }
    } catch {
        Write-Warning "Automatic rollback also failed: $($_.Exception.Message)"
    }
    throw $failure
}

Write-Output ([pscustomobject]@{
    Applied = $true
    PendingReload = $false
    ProfileUid = $profile.CurrentUid
    Group = $GroupName
    FixedProxy = $resolvedProxy
    Backup = $backupDirectory
})
