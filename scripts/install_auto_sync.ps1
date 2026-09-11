param(
    [ValidatePattern('^(?:[01]\d|2[0-3]):[0-5]\d$')]
    [string]$DailyAt = "12:00",
    [switch]$Remove
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$TaskName = "Agent Skills Auto Sync"
$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$SyncScript = Join-Path $PSScriptRoot "sync_skills.ps1"

if ($Remove) {
    $existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($null -ne $existing) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Removed scheduled task: $TaskName"
    }
    else {
        Write-Host "Scheduled task not present: $TaskName"
    }
    exit 0
}

if (-not (Test-Path -LiteralPath $SyncScript -PathType Leaf)) {
    throw "Missing sync runner: $SyncScript"
}

$PowerShellPath = (Get-Command powershell.exe -ErrorAction Stop).Source
$PythonPath = (Get-Command python -ErrorAction Stop).Source
$GitPath = (Get-Command git -ErrorAction Stop).Source

$time = [TimeSpan]::ParseExact($DailyAt, "hh\:mm", [Globalization.CultureInfo]::InvariantCulture)
$runAt = [DateTime]::Today.Add($time)

$arguments = @(
    "-NoProfile"
    "-ExecutionPolicy Bypass"
    "-File `"$SyncScript`""
    "-PythonPath `"$PythonPath`""
    "-GitPath `"$GitPath`""
) -join " "

$action = New-ScheduledTaskAction -Execute $PowerShellPath -Argument $arguments -WorkingDirectory $RepoRoot
$trigger = New-ScheduledTaskTrigger -Daily -At $runAt
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Safely fast-forward CHNISam/agent-skills and refresh managed core Agent Skills once per day." `
    -Force | Out-Null

Write-Host "Installed scheduled task: $TaskName"
Write-Host "Schedule: daily at $DailyAt (local time; StartWhenAvailable enabled)"
Write-Host "Repository: $RepoRoot"
Write-Host "Log: $env:LOCALAPPDATA\agent-skills\auto-sync.log"
Write-Host "The sync skips automatically if the repo is dirty, not on master, ahead, or diverged."
