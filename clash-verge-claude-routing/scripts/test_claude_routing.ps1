$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$source = Join-Path $PSScriptRoot 'configure_clash_verge_claude.ps1'
$tokens = $null; $parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($source, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw ($parseErrors | Out-String) }
# Load helper definitions only: never execute the live script entrypoint.
$managedMarker = 'clash-verge-claude-routing managed block'
foreach ($definition in $ast.FindAll({ param($a) $a -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $false)) {
    . ([scriptblock]::Create($definition.Extent.Text))
}
function Assert-True($Condition, $Message) { if (-not $Condition) { throw $Message } }
function Assert-Rejected([scriptblock]$Action, [string]$Message) {
    $rejected = $false
    try { & $Action | Out-Null } catch { $rejected = $true }
    Assert-True $rejected $Message
}
function Invoke-CoreGet {
    param($Connection, [string]$Path)
    return [pscustomobject]@{ proxies = [pscustomobject]@{
        GLOBAL = [pscustomobject]@{ now = 'US one'; all = @('US one','Other country') }
        'US one' = [pscustomobject]@{ type = 'Shadowsocks' }
        'US two' = [pscustomobject]@{ type = 'Shadowsocks' }
        DIRECT = [pscustomobject]@{ type = 'Direct' }
        REJECT = [pscustomobject]@{ type = 'Reject' }
        Broken = [pscustomobject]@{ all = @('US one') }
        Loop = [pscustomobject]@{ now = 'Loop2'; all = @('Loop2') }
        Loop2 = [pscustomobject]@{ now = 'Loop'; all = @('Loop') }
    } }
}
$fixture = Join-Path ([System.IO.Path]::GetTempPath()) ('claude-routing-test-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $fixture | Out-Null
try {
    $nodes = @(Resolve-ClaudeCandidates $null '' @('US one','US two','US one'))
    Assert-True ($nodes.Count -eq 2 -and $nodes[0] -eq 'US one' -and $nodes[1] -eq 'US two') 'Candidate identity/order/deduplication failed'
    Assert-True ((Resolve-ClaudeCandidates $null '' @()) -eq 'US one') 'Default GLOBAL leaf resolution failed'
    foreach ($bad in @('GLOBAL','DIRECT','REJECT','Broken','missing','Loop','')) {
        Assert-Rejected { Resolve-ClaudeCandidates $null '' @($bad) } "Accepted unsafe candidate: $bad"
    }
    Assert-Rejected { Resolve-ClaudeCandidates $null 'US one' @('US two') } 'Conflicting parameters accepted'
    Assert-Rejected { Resolve-LeafProxy $null 'Broken' } 'Unresolved group accepted'
    Assert-Rejected { Resolve-LeafProxy $null 'Loop' } 'Selector cycle accepted'

    Write-Utf8Atomic (Join-Path $fixture 'profiles.yaml') "current: replacement`nitems:`n- uid: replacement`n  option:`n    merge: m`n    rules: r`n    groups: g`n"
    Assert-Rejected { & $source -ConfigRoot $fixture -ExpectedProfileUid 'intended-profile' -WhatIf } 'Changed subscription was not rejected before controller access'
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $fixture 'backups'))) 'Profile guard wrote backups'

    $groups = Join-Path $fixture 'groups.yaml'; $rules = Join-Path $fixture 'rules.yaml'
    Write-Utf8Atomic $groups "prepend: []`nappend:`n- name: unrelated`n  type: select`n  proxies: [DIRECT]`ndelete: []`n"
    Write-Utf8Atomic $rules "prepend: []`nappend:`n- DOMAIN,example.org,DIRECT`ndelete: []`n"
    Set-GroupEnhancement $groups 'Claude' $nodes
    Set-RuleEnhancement $rules 'Claude'
    $firstGroups = [IO.File]::ReadAllText($groups); $firstRules = [IO.File]::ReadAllText($rules)
    Set-GroupEnhancement $groups 'Claude' $nodes
    Set-RuleEnhancement $rules 'Claude'
    Assert-True ($firstGroups -eq [IO.File]::ReadAllText($groups)) 'Groups are not idempotent'
    Assert-True ($firstRules -eq [IO.File]::ReadAllText($rules)) 'Rules are not idempotent'
    Assert-True ($firstGroups.Contains('name: unrelated') -and $firstRules.Contains('DOMAIN,example.org,DIRECT')) 'Unrelated enhancement lost'
    foreach ($node in $nodes) { Assert-True ($firstGroups.Contains("  - '$node'")) 'Candidate omitted' }
    foreach ($domain in @('anthropic.com','claude.ai','claude.com','claude.app','claudeusercontent.com','claudemcpcontent.com')) {
        Assert-True ($firstRules.Contains("DOMAIN-SUFFIX,$domain,Claude")) "Missing suffix: $domain"
    }
    foreach ($required in @('IP-CIDR,160.79.104.0/23,Claude,no-resolve','IP-CIDR6,2607:6bc0::/48,Claude,no-resolve','DOMAIN,http-intake.logs.us5.datadoghq.com,Claude','DOMAIN,browser-intake-us5-datadoghq.com,Claude','PROCESS-NAME,claude.exe,Claude','PROCESS-NAME,Claude.exe,Claude')) {
        Assert-True ($firstRules.Contains($required)) "Missing rule: $required"
    }
    Assert-True ($firstRules.IndexOf('IP-CIDR,127.0.0.0/8,DIRECT') -lt $firstRules.IndexOf('PROCESS-NAME,claude.exe')) 'Local MCP exclusion comes too late'
    Assert-True (-not $firstRules.Contains('DOMAIN-SUFFIX,datadoghq.com')) 'Shared telemetry provider routed broadly'
    Set-GroupEnhancement $groups 'Claude' @("US O'Brien")
    Assert-True ([IO.File]::ReadAllText($groups).Contains("'US O''Brien'")) 'YAML quote escaping failed'
    $backup = New-Backup $fixture @($groups,$rules) 'fixture-profile'
    Write-Utf8Atomic $rules 'damaged'
    Restore-BackupFiles $backup
    Assert-True ([IO.File]::ReadAllText($rules) -eq $firstRules) 'Backup restore failed'
    Write-Output 'PASS: parsing, approved leaf selection, unsafe rejection, endpoint coverage, preservation, idempotence, escaping and rollback'
} finally {
    # Verify the absolute cleanup target remains inside this uniquely created fixture.
    $resolvedFixture = [IO.Path]::GetFullPath($fixture)
    $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\') + '\'
    if (-not $resolvedFixture.StartsWith($tempRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe test cleanup path' }
    Remove-Item -LiteralPath $resolvedFixture -Recurse -Force
}
