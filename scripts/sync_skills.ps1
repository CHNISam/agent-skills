param(
    [string]$PythonPath = "",
    [string]$GitPath = "",
    [string]$Branch = "master",
    [string]$Remote = "origin"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$StateRoot = Join-Path $env:LOCALAPPDATA "agent-skills"
$LogPath = Join-Path $StateRoot "auto-sync.log"
New-Item -ItemType Directory -Force -Path $StateRoot | Out-Null

function Write-SyncLog {
    param([string]$Message)
    $line = "{0} {1}" -f (Get-Date -Format "yyyy-MM-ddTHH:mm:ssK"), $Message
    Add-Content -Path $LogPath -Value $line -Encoding UTF8
    Write-Host $line
}

if ([string]::IsNullOrWhiteSpace($GitPath)) {
    $GitPath = (Get-Command git -ErrorAction Stop).Source
}
if ([string]::IsNullOrWhiteSpace($PythonPath)) {
    $PythonPath = (Get-Command python -ErrorAction Stop).Source
}

function Invoke-Git {
    param([string[]]$Arguments)

    $output = & $GitPath -C $RepoRoot @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $text = ($output | Out-String).TrimEnd()
    if ($exitCode -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit code $exitCode`: $text"
    }
    return $text
}

try {
    $currentBranch = (Invoke-Git @("branch", "--show-current")).Trim()
    if ($currentBranch -ne $Branch) {
        Write-SyncLog "SKIP branch=$currentBranch expected=$Branch"
        exit 0
    }

    $status = Invoke-Git @("status", "--porcelain")
    if (-not [string]::IsNullOrWhiteSpace($status)) {
        Write-SyncLog "SKIP dirty worktree"
        exit 0
    }

    Invoke-Git @("fetch", "--quiet", $Remote, $Branch) | Out-Null

    $head = (Invoke-Git @("rev-parse", "HEAD")).Trim()
    $remoteRef = "$Remote/$Branch"
    $remoteHead = (Invoke-Git @("rev-parse", $remoteRef)).Trim()
    $mergeBase = (Invoke-Git @("merge-base", "HEAD", $remoteRef)).Trim()

    if ($head -eq $remoteHead) {
        Write-SyncLog "REMOTE_OK head=$head"
    }
    elseif ($head -eq $mergeBase) {
        Invoke-Git @("merge", "--ff-only", "--quiet", $remoteRef) | Out-Null
        $head = (Invoke-Git @("rev-parse", "HEAD")).Trim()
        Write-SyncLog "FAST_FORWARD_OK head=$head"
    }
    else {
        Write-SyncLog "SKIP local $Branch is ahead of or diverged from $remoteRef"
        exit 0
    }

    $distributor = Join-Path $RepoRoot "scripts\distribute_skills.py"
    & $PythonPath $distributor --profile core --apply --prune
    if ($LASTEXITCODE -ne 0) {
        throw "distribute_skills.py failed with exit code $LASTEXITCODE"
    }

    $finalHead = (Invoke-Git @("rev-parse", "HEAD")).Trim()
    Write-SyncLog "SYNC_OK head=$finalHead"
    exit 0
}
catch {
    Write-SyncLog "SYNC_ERROR $($_.Exception.Message)"
    exit 1
}
