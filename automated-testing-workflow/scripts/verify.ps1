<#
verify.ps1 — deterministic canonical-verification gate for a repository (Windows / pwsh).

Runs format -> lint -> typecheck -> test in order, fail-fast, streaming output, then
prints an exact "what ran / what passed / what did not run" summary.

The `automated-testing-workflow` skill owns the JUDGMENT (scope by risk, failure
diagnosis, modification authority). This script only EXECUTES the gate.

Provenance: the sequential fail-fast gate pattern is adapted from the OpenAI Agents SDK
skill `code-change-verification` (github.com/openai/openai-agents-python, .agents/skills,
MIT). No upstream code was copied.

Configuration (first match wins):
  1. A repo-local `verify.config` file (KEY=command per line; keys: format, lint,
     typecheck, test, setup; '#' comments; empty value = skip). Path via -Config or
     $env:VERIFY_CONFIG, else <repo-root>\verify.config.
  2. Auto-detection for npm/pnpm/yarn, python, cargo, go.

Usage:
  verify.ps1 [-Stage format,lint,typecheck,test] [-List] [-Config path]
#>
[CmdletBinding()]
param(
  [string[]]$Stage,
  [string]$Config,
  [switch]$List
)

$ErrorActionPreference = 'Stop'
$root = (& git rev-parse --show-toplevel 2>$null)
if (-not $root) { $root = (Get-Location).Path }
$root = $root -replace '/', '\'

$allStages = @('format', 'lint', 'typecheck', 'test')
$cmd = [ordered]@{}
if (-not $Config) { $Config = if ($env:VERIFY_CONFIG) { $env:VERIFY_CONFIG } else { Join-Path $root 'verify.config' } }

if (Test-Path $Config) {
  $src = "verify.config ($Config)"
  foreach ($line in Get-Content $Config) {
    if ($line -match '^\s*#' -or $line -match '^\s*$') { continue }
    $k, $v = $line -split '=', 2
    $cmd[$k.Trim()] = $v
  }
} else {
  $src = 'auto-detection'
  if (Test-Path (Join-Path $root 'package.json')) {
    $pm = 'npm'
    if (Test-Path (Join-Path $root 'pnpm-lock.yaml')) { $pm = 'pnpm' }
    elseif (Test-Path (Join-Path $root 'yarn.lock')) { $pm = 'yarn' }
    $pkg = Get-Content (Join-Path $root 'package.json') -Raw
    $run = if ($pm -eq 'npm') { 'npm run' } else { "$pm run" }
    if ($pkg -match '"format"')    { $cmd['format'] = "$run format" }
    if ($pkg -match '"lint"')      { $cmd['lint'] = "$run lint" }
    if ($pkg -match '"typecheck"') { $cmd['typecheck'] = "$run typecheck" }
    elseif ($pkg -match '"build"') { $cmd['typecheck'] = "$run build" }
    if ($pkg -match '"test"')      { $cmd['test'] = "$run test" }
  } elseif ((Test-Path (Join-Path $root 'pyproject.toml')) -or (Test-Path (Join-Path $root 'requirements.txt'))) {
    if (Get-Command ruff -ErrorAction SilentlyContinue)    { $cmd['format'] = 'ruff format --check .'; $cmd['lint'] = 'ruff check .' }
    if (Get-Command pyright -ErrorAction SilentlyContinue) { $cmd['typecheck'] = 'pyright' }
    elseif (Get-Command mypy -ErrorAction SilentlyContinue) { $cmd['typecheck'] = 'mypy .' }
    if (Get-Command pytest -ErrorAction SilentlyContinue)  { $cmd['test'] = 'pytest -q' }
  } elseif (Test-Path (Join-Path $root 'Cargo.toml')) {
    $cmd['format'] = 'cargo fmt --check'; $cmd['lint'] = 'cargo clippy -- -D warnings'
    $cmd['typecheck'] = 'cargo check'; $cmd['test'] = 'cargo test'
  } elseif (Test-Path (Join-Path $root 'go.mod')) {
    $cmd['format'] = 'gofmt -l .'; $cmd['lint'] = 'go vet ./...'; $cmd['test'] = 'go test ./...'
  }
}

if ($List) {
  Write-Host "root:   $root"
  Write-Host "source: $src"
  foreach ($s in $allStages) { '{0,-10} {1}' -f $s, ($(if ($cmd[$s]) { $cmd[$s] } else { '<none>' })) }
  return
}

$stages = if ($Stage) { $Stage } else { $allStages }
Write-Host "verify.ps1 | root=$root | commands from $src"
Write-Host ("stages: " + ($stages -join ' '))
Write-Host ''

$result = [ordered]@{}
$failed = $null
foreach ($s in $stages) {
  $c = $cmd[$s]
  if (-not $c) { $result[$s] = 'skip (no command)'; Write-Host "== ${s}: SKIP (no command configured)`n"; continue }
  Write-Host "== ${s}: $c"
  Push-Location $root
  try {
    & $env:ComSpec /c $c
    $rc = $LASTEXITCODE
  } finally { Pop-Location }
  if ($rc -eq 0) { $result[$s] = 'pass'; Write-Host "== ${s}: PASS`n" }
  else { $result[$s] = "FAIL (exit $rc)"; $failed = $s; Write-Host "== ${s}: FAIL (exit $rc)`n"; break }
}

Write-Host '---------------- verify.ps1 summary ----------------'
foreach ($s in $stages) { '{0,-10} {1}' -f $s, ($(if ($result[$s]) { $result[$s] } else { 'not run' })) }
if ($failed) {
  $idx = $stages.IndexOf($failed)
  if ($idx -ge 0 -and ($idx + 1) -lt $stages.Count) {
    $notRun = @($stages[($idx + 1)..($stages.Count - 1)]) | Where-Object { $_ }
    if ($notRun) { Write-Host ("  did not run: " + ($notRun -join ' ') + " (stopped at first failure)") }
  }
  Write-Host "RESULT: FAIL at '$failed'"
  exit 1
}
Write-Host 'RESULT: PASS'
