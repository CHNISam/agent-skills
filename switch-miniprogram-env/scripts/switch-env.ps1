param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$Target,

  [string]$ConfigPath,

  [string]$RepoRoot,

  [switch]$CheckOnly
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($RepoRoot) {
  $repoRootPath = (Resolve-Path $RepoRoot).Path
} else {
  $repoRootPath = (Resolve-Path (Join-Path $scriptDir '..')).Path
}
if (-not $ConfigPath) {
  $ConfigPath = Join-Path $scriptDir 'env-config.json'
}

function Read-TextFile {
  param([string]$Path)
  return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

function Write-TextFile {
  param(
    [string]$Path,
    [string]$Content
  )
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
}

function Test-HasUtf8Bom {
  param([string]$Path)
  if (-not (Test-Path $Path)) { return $false }
  $bytes = [System.IO.File]::ReadAllBytes($Path)
  return $bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF
}

function Resolve-RepoPath {
  param([string]$RelativePath)
  return Join-Path $repoRootPath $RelativePath
}

function Set-Or-CheckContent {
  param(
    [string]$Path,
    [string]$NewContent,
    [switch]$CheckOnly
  )

  $script:ProjectedContent[$Path] = $NewContent
  $oldContent = Read-TextFile $Path
  $hasBom = Test-HasUtf8Bom $Path
  if ($oldContent -eq $NewContent -and -not $hasBom) {
    return $false
  }

  if (-not $CheckOnly) {
    Write-TextFile $Path $NewContent
  }

  return $true
}

function Replace-JsStringProperty {
  param(
    [string]$Content,
    [string]$Property,
    [string]$Value
  )

  $escaped = [regex]::Escape($Property)
  $pattern = "($escaped\s*:\s*['""])[^'""]*(['""])"
  return [regex]::Replace($Content, $pattern, "`${1}$Value`${2}", 1)
}

function Replace-JsonStringProperty {
  param(
    [string]$Content,
    [string]$Property,
    [string]$Value
  )

  $escaped = [regex]::Escape($Property)
  $pattern = "(`"$escaped`"\s*:\s*`")[^`"]*(`")"
  return [regex]::Replace($Content, $pattern, "`${1}$Value`${2}", 1)
}

function Replace-KnownValues {
  param(
    [string]$Content,
    [string[]]$KnownValues,
    [string]$TargetValue
  )

  $newContent = $Content
  foreach ($value in $KnownValues) {
    if ($value -and $value -ne $TargetValue) {
      $newContent = $newContent.Replace($value, $TargetValue)
    }
  }
  return $newContent
}

function Get-CloudFunctionEnvFiles {
  param([string[]]$Roots)

  $files = @()
  foreach ($root in $Roots) {
    $fullRoot = Resolve-RepoPath $root
    if (Test-Path $fullRoot) {
      $files += Get-ChildItem -Path $fullRoot -Recurse -File | Where-Object {
        $_.Extension -in @('.js', '.json', '.env')
      }
    }
  }
  return $files
}

function Get-ScanFiles {
  param(
    [string[]]$ExcludeDirectories,
    [string[]]$ExcludeFiles
  )

  $rootPath = $repoRootPath
  return Get-ChildItem -Path $rootPath -Recurse -File | Where-Object {
    $relative = $_.FullName.Substring($rootPath.Length).TrimStart('\', '/').Replace('\', '/')
    foreach ($dir in $ExcludeDirectories) {
      $prefix = $dir.Trim('/').Replace('\', '/') + '/'
      if ($relative.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $false
      }
    }
    foreach ($file in $ExcludeFiles) {
      if ($relative -eq $file.Replace('\', '/')) {
        return $false
      }
    }
    return $true
  }
}

if (-not (Test-Path $ConfigPath)) {
  throw "Missing config file: $ConfigPath"
}

$config = Get-Content -Raw -Path $ConfigPath -Encoding UTF8 | ConvertFrom-Json
$envNames = @($config.environments.PSObject.Properties.Name)
if ($envNames -notcontains $Target) {
  throw "Unknown environment '$Target'. Available: $($envNames -join ', ')"
}

$targetEnv = $config.environments.$Target
$knownAppids = @($config.environments.PSObject.Properties | ForEach-Object { $_.Value.resourceAppid } | Where-Object { $_ })
$knownResourceEnvs = @($config.environments.PSObject.Properties | ForEach-Object { $_.Value.resourceEnv } | Where-Object { $_ })
$knownCloudDomins = @($config.environments.PSObject.Properties | ForEach-Object { $_.Value.cloudDomin } | Where-Object { $_ })
$knownValues = @($knownAppids + $knownResourceEnvs + $knownCloudDomins | Sort-Object -Unique)
$targetValues = @($targetEnv.resourceAppid, $targetEnv.resourceEnv, $targetEnv.cloudDomin) | Where-Object { $_ }
$nonTargetValues = @($knownValues | Where-Object { $targetValues -notcontains $_ })
$scanConfig = $config.scan
$excludeDirectories = @()
$excludeFiles = @()
$reportOnlyFiles = @()
if ($scanConfig) {
  $excludeDirectories = @($scanConfig.excludeDirectories | Where-Object { $_ })
  $excludeFiles = @($scanConfig.excludeFiles | Where-Object { $_ })
  $reportOnlyFiles = @($scanConfig.reportOnlyFiles | Where-Object { $_ } | ForEach-Object { $_.Replace('\', '/') })
}

$changed = New-Object System.Collections.Generic.List[string]
$script:ProjectedContent = New-Object 'System.Collections.Generic.Dictionary[string,string]'

if ($config.files.appConfig) {
  $appConfigPath = Resolve-RepoPath $config.files.appConfig
  $content = Read-TextFile $appConfigPath
  if ($targetEnv.resourceEnv) {
    $content = Replace-JsStringProperty $content 'resourceEnv' $targetEnv.resourceEnv
  }
  if ($targetEnv.cloudDomin) {
    $content = Replace-JsStringProperty $content 'cloudDomin' $targetEnv.cloudDomin
  }
  if (Set-Or-CheckContent $appConfigPath $content -CheckOnly:$CheckOnly) {
    $changed.Add($config.files.appConfig)
  }
}

if ($config.files.projectConfig) {
  $projectConfigPath = Resolve-RepoPath $config.files.projectConfig
  $content = Read-TextFile $projectConfigPath
  if ($targetEnv.resourceEnv) {
    $content = Replace-JsonStringProperty $content 'env' $targetEnv.resourceEnv
  }
  if ($targetEnv.resourceAppid) {
    $content = Replace-JsonStringProperty $content 'appid' $targetEnv.resourceAppid
  }
  if (Set-Or-CheckContent $projectConfigPath $content -CheckOnly:$CheckOnly) {
    $changed.Add($config.files.projectConfig)
  }
}

if ($config.files.cloudbaseConfig) {
  $cloudbaseConfigPath = Resolve-RepoPath $config.files.cloudbaseConfig
  $content = Read-TextFile $cloudbaseConfigPath
  if ($targetEnv.resourceEnv) {
    $content = Replace-JsonStringProperty $content 'envId' $targetEnv.resourceEnv
  }
  if (Set-Or-CheckContent $cloudbaseConfigPath $content -CheckOnly:$CheckOnly) {
    $changed.Add($config.files.cloudbaseConfig)
  }
}

$cloudFunctionFiles = Get-CloudFunctionEnvFiles @($config.files.cloudFunctionRoots)
foreach ($file in $cloudFunctionFiles) {
  $content = Read-TextFile $file.FullName
  if ($targetEnv.resourceEnv) {
    $content = Replace-KnownValues $content $knownResourceEnvs $targetEnv.resourceEnv
  }
  if ($targetEnv.resourceAppid) {
    $content = Replace-KnownValues $content $knownAppids $targetEnv.resourceAppid
  }
  if (Set-Or-CheckContent $file.FullName $content -CheckOnly:$CheckOnly) {
    $relative = $file.FullName.Substring($repoRootPath.Length).TrimStart('\', '/').Replace('\', '/')
    $changed.Add($relative)
  }
}

$residuals = New-Object System.Collections.Generic.List[string]
$reportOnlyResiduals = New-Object System.Collections.Generic.List[string]
$scanFiles = Get-ScanFiles $excludeDirectories $excludeFiles
foreach ($file in $scanFiles) {
  $relative = $file.FullName.Substring($repoRootPath.Length).TrimStart('\', '/').Replace('\', '/')
  if ($script:ProjectedContent.ContainsKey($file.FullName)) {
    $text = $script:ProjectedContent[$file.FullName]
  } else {
    try {
      $text = Read-TextFile $file.FullName
    } catch {
      continue
    }
  }

  foreach ($value in $nonTargetValues) {
    if ($text.Contains($value)) {
      $message = "$relative contains $value"
      if ($reportOnlyFiles -contains $relative) {
        $reportOnlyResiduals.Add($message)
      } else {
        $residuals.Add($message)
      }
    }
  }
}

if ($CheckOnly) {
  Write-Host "Check only: no files were written."
} else {
  Write-Host "Environment switched to '$Target'."
}

if ($changed.Count -eq 0) {
  Write-Host "Changed files: none"
} else {
  Write-Host "Changed files:"
  $changed | Sort-Object -Unique | ForEach-Object { Write-Host "  $_" }
}

if ($residuals.Count -gt 0) {
  Write-Host "Residual non-target values:"
  $residuals | Sort-Object -Unique | ForEach-Object { Write-Host "  $_" }
  exit 2
}

if ($reportOnlyResiduals.Count -gt 0) {
  Write-Host "Report-only non-target values:"
  $reportOnlyResiduals | Sort-Object -Unique | ForEach-Object { Write-Host "  $_" }
}

Write-Host "Validation passed for '$Target'."
