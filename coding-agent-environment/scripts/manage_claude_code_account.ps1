[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param(
    [ValidateSet('Discover', 'Apply', 'Verify', 'Rollback')]
    [string]$Action = 'Discover',

    [ValidatePattern('^[A-Za-z][A-Za-z0-9_-]*$')]
    [string]$Name = 'claude2',

    [string]$ConfigDirectory,
    [string]$LauncherDirectory,
    [string]$ClaudeCommand
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$managedMarker = ':: agent-skills: managed Claude Code account launcher'
$authenticationOverrideVariables = @(
    # Anthropic's documented process-level credential selectors. Each can
    # outrank credentials saved in CLAUDE_CONFIG_DIR, so Verify must not call
    # a directory mapping independent while one is present.
    'CLAUDE_CODE_USE_BEDROCK',
    'CLAUDE_CODE_USE_VERTEX',
    'CLAUDE_CODE_USE_FOUNDRY',
    'ANTHROPIC_API_KEY',
    'ANTHROPIC_AUTH_TOKEN',
    'CLAUDE_CODE_OAUTH_TOKEN',
    'ANTHROPIC_PROFILE',
    'ANTHROPIC_FEDERATION_RULE_ID',
    'ANTHROPIC_ORGANIZATION_ID'
)
# Keep launchers byte-for-byte stable across Windows PowerShell (legacy ANSI
# default) and PowerShell 7 (UTF-8 default). Path literals are made ASCII below,
# while the real Windows path is expanded by cmd.exe from its environment.
$batchFileEncoding = [System.Text.UTF8Encoding]::new($false, $true)
$cmdPathEnvironmentVariables = @(
    'APPDATA',
    'LOCALAPPDATA',
    'USERPROFILE',
    'ProgramFiles',
    'ProgramFiles(x86)',
    'ProgramData',
    'TEMP',
    'TMP'
)

function Resolve-AccountPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $expanded = [Environment]::ExpandEnvironmentVariables($Path)
    if ($expanded -eq '~') {
        $expanded = $HOME
    } elseif ($expanded.StartsWith('~\\')) {
        $expanded = Join-Path $HOME $expanded.Substring(2)
    }
    return [System.IO.Path]::GetFullPath($expanded)
}

function Test-SamePath {
    param([Parameter(Mandatory = $true)][string]$Left, [Parameter(Mandatory = $true)][string]$Right)

    $normalLeft = (Resolve-AccountPath $Left).TrimEnd([char[]]@('\', '/'))
    $normalRight = (Resolve-AccountPath $Right).TrimEnd([char[]]@('\', '/'))
    return [string]::Equals($normalLeft, $normalRight, [System.StringComparison]::OrdinalIgnoreCase)
}

function Resolve-PrimaryCommand {
    param([string]$RequestedCommand)

    if ($RequestedCommand) {
        $path = Resolve-AccountPath $RequestedCommand
    } else {
        # On Windows the supported npm installation exposes claude.cmd. Resolving that
        # exact file prevents a same-named PowerShell function from changing the launcher.
        $command = Get-Command -Name 'claude.cmd' -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $command) {
            throw 'Could not resolve claude.cmd on PATH. Install Claude Code first or pass -ClaudeCommand with its .cmd path.'
        }
        $path = if ($command.Path) { $command.Path } elseif ($command.Source) { $command.Source } else { $command.Definition }
        $path = Resolve-AccountPath $path
    }

    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Claude command does not exist: $path"
    }
    if ([System.IO.Path]::GetExtension($path).ToLowerInvariant() -notin @('.cmd', '.bat')) {
        throw "Claude command must be a Windows .cmd or .bat launcher: $path"
    }
    return $path
}

function Test-DirectoryOnPath {
    param([Parameter(Mandatory = $true)][string]$Directory)

    $normalDirectory = (Resolve-AccountPath $Directory).TrimEnd([char[]]@('\', '/'))
    foreach ($entry in ($env:Path -split [regex]::Escape([string][System.IO.Path]::PathSeparator))) {
        if (-not $entry) { continue }
        if (Test-SamePath $entry $normalDirectory) { return $true }
    }
    return $false
}

function Get-AuthenticationOverrideNames {
    $present = @()
    foreach ($variable in $authenticationOverrideVariables) {
        if (-not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($variable))) {
            $present += $variable
        }
    }
    return $present
}

function Assert-LauncherDirectoryIsReachable {
    param([Parameter(Mandatory = $true)][string]$Directory)

    if (-not (Test-Path -LiteralPath $Directory -PathType Container)) {
        throw "Launcher directory does not exist: $Directory"
    }
    if (-not (Test-DirectoryOnPath $Directory)) {
        throw "Launcher directory is not on PATH, so the daily account entry would not be stable: $Directory"
    }
}

function Get-LauncherContent {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    # Read with the exact explicit encoding used to write ASCII-only .cmd files.
    # This stays stable between Windows PowerShell and PowerShell 7.
    return [System.IO.File]::ReadAllText($Path, $batchFileEncoding)
}

function Get-LauncherState {
    param([Parameter(Mandatory = $true)][string]$Path)

    $content = Get-LauncherContent $Path
    if ($null -eq $content) { return 'Absent' }
    if ($content.Contains($managedMarker)) { return 'Managed' }
    return 'Unmanaged'
}

function ConvertTo-CmdLiteral {
    param([Parameter(Mandatory = $true)][string]$Value)

    if ($Value -match '[\r\n"]') { throw 'Launcher paths cannot contain quotes or line breaks.' }
    if ($Value -match '[^\x00-\x7F]') {
        throw 'The launcher would need non-ASCII literal path text. Use a path under USERPROFILE, APPDATA, or another supported Windows environment directory.'
    }
    # A percent sign is expanded by cmd.exe even inside a quoted SET assignment.
    return $Value.Replace('%', '%%')
}

function ConvertTo-CmdPathLiteral {
    param([Parameter(Mandatory = $true)][string]$Value)

    $resolvedValue = Resolve-AccountPath $Value
    foreach ($variable in $cmdPathEnvironmentVariables) {
        $root = [Environment]::GetEnvironmentVariable($variable)
        if ([string]::IsNullOrWhiteSpace($root)) { continue }
        $resolvedRoot = Resolve-AccountPath $root
        $trimmedRoot = $resolvedRoot.TrimEnd([char[]]@('\', '/'))
        if (Test-SamePath $resolvedValue $trimmedRoot) {
            return ('%' + $variable + '%')
        }
        $prefix = $trimmedRoot + [System.IO.Path]::DirectorySeparatorChar
        if ($resolvedValue.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            $relative = $resolvedValue.Substring($trimmedRoot.Length)
            return ('%' + $variable + '%' + (ConvertTo-CmdLiteral $relative))
        }
    }
    return ConvertTo-CmdLiteral $resolvedValue
}

function New-LauncherContent {
    param(
        [Parameter(Mandatory = $true)][string]$PrimaryCommand,
        [Parameter(Mandatory = $true)][string]$IsolatedConfigDirectory
    )

    $safeCommand = ConvertTo-CmdPathLiteral $PrimaryCommand
    $safeConfig = ConvertTo-CmdPathLiteral $IsolatedConfigDirectory
    $lines = @(
        '@echo off',
        $managedMarker,
        'setlocal DisableDelayedExpansion',
        ('set "CLAUDE_CONFIG_DIR=' + $safeConfig + '"'),
        ('call "' + $safeCommand + '" %*'),
        'set "CLAUDE_ACCOUNT_EXIT=%ERRORLEVEL%"',
        'endlocal & exit /b %CLAUDE_ACCOUNT_EXIT%'
    )
    return ($lines -join "`r`n") + "`r`n"
}

function Write-BatchAtomic {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Content)

    $directory = Split-Path -Parent $Path
    $temporary = Join-Path $directory ('.' + [System.IO.Path]::GetFileName($Path) + '.tmp-' + [guid]::NewGuid().ToString('N'))
    try {
        [System.IO.File]::WriteAllText($temporary, $Content, $batchFileEncoding)
        [System.IO.File]::Move($temporary, $Path)
    } finally {
        if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary -Force }
    }
}

function Assert-AuthenticationStatusUsesConfigDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$ExpectedConfigDirectory,
        [Parameter(Mandatory = $true)][object[]]$StatusOutput
    )

    try {
        $status = (($statusOutput -join "`n") | ConvertFrom-Json -ErrorAction Stop)
    } catch {
        throw "$Label did not return JSON authentication status."
    }

    $loggedIn = $status.PSObject.Properties['loggedIn']
    if ($null -eq $loggedIn -or -not [bool]$loggedIn.Value) {
        throw "$Label is not logged in. Start the entry and use the official /login flow before verification."
    }
    $reportedDirectory = $status.PSObject.Properties['configDirectory']
    if ($null -eq $reportedDirectory -or [string]::IsNullOrWhiteSpace([string]$reportedDirectory.Value)) {
        throw "$Label did not report its effective configuration directory."
    }
    if (-not (Test-SamePath ([string]$reportedDirectory.Value) $ExpectedConfigDirectory)) {
        throw "$Label is using a different configuration directory than the requested isolated account."
    }
}

function Assert-AuthenticatedEntryUsesConfigDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$ExpectedConfigDirectory
    )

    # The CLI owns authentication storage. Keep its JSON in memory only: account
    # identity, organisation, and subscription details must never reach logs.
    $statusOutput = @(& $Command 'auth' 'status' '--json' 2>$null)
    if ($LASTEXITCODE -ne 0) {
        throw "$Label could not obtain Claude Code authentication status."
    }
    Assert-AuthenticationStatusUsesConfigDirectory $Label $ExpectedConfigDirectory $statusOutput
}

function Assert-CmdEntryUsesConfigDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$EntryName,
        [Parameter(Mandatory = $true)][string]$ExpectedConfigDirectory
    )

    $statusOutput = @(& $env:ComSpec '/d' '/c' ("{0} auth status --json" -f $EntryName) 2>$null)
    if ($LASTEXITCODE -ne 0) {
        throw "cmd.exe could not obtain authentication status through $EntryName."
    }
    Assert-AuthenticationStatusUsesConfigDirectory 'cmd.exe entry' $ExpectedConfigDirectory $statusOutput
}

function New-Result {
    param(
        [bool]$Changed = $false,
        [bool]$VersionCheckSucceeded = $false,
        [Nullable[bool]]$LoggedIn = $null,
        [bool]$AuthStatusCommandSucceeded = $false
    )

    [pscustomobject]@{
        Action = $Action
        Name = $Name
        PrimaryCommand = $primaryCommand
        DefaultPrimaryConfigDirectory = $defaultPrimaryConfigDirectory
        PrimaryConfigDirectory = $primaryConfigDirectory
        ConfigDirectory = $configDirectory
        ConfigDirectoryExists = (Test-Path -LiteralPath $configDirectory -PathType Container)
        IsolatedFromPrimary = (-not (Test-SamePath $primaryConfigDirectory $configDirectory))
        LauncherPath = $launcherPath
        LauncherState = (Get-LauncherState $launcherPath)
        LauncherDirectoryOnPath = (Test-DirectoryOnPath $launcherDirectory)
        Changed = $Changed
        VersionCheckSucceeded = $VersionCheckSucceeded
        AuthStatusCommandSucceeded = $AuthStatusCommandSucceeded
        LoggedIn = $LoggedIn
        CallerConfigDirectory = $env:CLAUDE_CONFIG_DIR
        AuthenticationOverrideVariables = @(Get-AuthenticationOverrideNames)
    }
}

if ([string]::Equals($Name, 'claude', [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'Refusing to replace the primary claude command. Choose a distinct account entry such as claude2.'
}

$defaultPrimaryConfigDirectory = Resolve-AccountPath (Join-Path $HOME '.claude')
$primaryConfigDirectory = if ($env:CLAUDE_CONFIG_DIR) {
    Resolve-AccountPath $env:CLAUDE_CONFIG_DIR
} else {
    $defaultPrimaryConfigDirectory
}
$configDirectory = if ($ConfigDirectory) {
    Resolve-AccountPath $ConfigDirectory
} else {
    Resolve-AccountPath (Join-Path (Join-Path $HOME '.claude-profiles') $Name)
}
if (Test-SamePath $primaryConfigDirectory $configDirectory) {
    throw 'The isolated configuration directory must differ from the effective primary configuration directory.'
}

$primaryCommand = Resolve-PrimaryCommand $ClaudeCommand
$launcherDirectory = if ($LauncherDirectory) {
    Resolve-AccountPath $LauncherDirectory
} else {
    Resolve-AccountPath (Split-Path -Parent $primaryCommand)
}
$launcherPath = Join-Path $launcherDirectory ($Name + '.cmd')
$expectedLauncher = New-LauncherContent $primaryCommand $configDirectory

switch ($Action) {
    'Discover' {
        Write-Output (New-Result)
        return
    }

    'Apply' {
        Assert-LauncherDirectoryIsReachable $launcherDirectory
        $state = Get-LauncherState $launcherPath
        if ($state -eq 'Unmanaged') {
            throw "Refusing to replace an unmanaged launcher: $launcherPath"
        }
        if ($state -eq 'Managed') {
            if ((Get-LauncherContent $launcherPath) -ne $expectedLauncher) {
                throw "Managed launcher differs from the requested account mapping. Roll it back before applying a new mapping: $launcherPath"
            }
            Write-Output (New-Result)
            return
        }

        if ($PSCmdlet.ShouldProcess($configDirectory, 'Create an empty isolated Claude Code configuration directory')) {
            New-Item -ItemType Directory -Path $configDirectory -Force | Out-Null
        }
        if ($PSCmdlet.ShouldProcess($launcherPath, "Create $Name launcher for an isolated Claude Code account")) {
            Write-BatchAtomic $launcherPath $expectedLauncher
            Write-Output (New-Result -Changed $true)
        }
        return
    }

    'Verify' {
        Assert-LauncherDirectoryIsReachable $launcherDirectory
        if ((Get-LauncherState $launcherPath) -ne 'Managed') {
            throw "Managed launcher is missing or altered: $launcherPath"
        }
        if ((Get-LauncherContent $launcherPath) -ne $expectedLauncher) {
            throw "Managed launcher does not match the requested account mapping: $launcherPath"
        }
        if (-not (Test-Path -LiteralPath $configDirectory -PathType Container)) {
            throw "Isolated configuration directory is missing: $configDirectory"
        }
        $overrides = @(Get-AuthenticationOverrideNames)
        if ($overrides.Count -gt 0) {
            throw ('Cannot verify independent account selection while process authentication override variables are set: ' + ($overrides -join ', '))
        }

        $callerConfigDirectory = $env:CLAUDE_CONFIG_DIR
        $null = @(& $primaryCommand '--version' 2>&1)
        if ($LASTEXITCODE -ne 0) {
            throw "The original claude command could not start: $primaryCommand"
        }
        Assert-AuthenticatedEntryUsesConfigDirectory $primaryCommand 'Original claude entry' $primaryConfigDirectory
        $null = @(& $launcherPath '--version' 2>&1)
        $versionSucceeded = ($LASTEXITCODE -eq 0)
        if (-not $versionSucceeded) {
            throw "Launcher could not start Claude Code: $launcherPath"
        }
        $null = @(& $env:ComSpec '/d' '/c' ("{0} --version" -f $Name) 2>&1)
        if ($LASTEXITCODE -ne 0) {
            throw "cmd.exe could not start the daily $Name entry."
        }
        Assert-CmdEntryUsesConfigDirectory $Name $configDirectory
        $null = Get-Command -Name $Name -ErrorAction Stop | Select-Object -First 1
        $null = @(& $Name '--version' 2>&1)
        if ($LASTEXITCODE -ne 0) {
            throw "The current PowerShell entry for $Name could not start Claude Code."
        }
        Assert-AuthenticatedEntryUsesConfigDirectory $launcherPath 'Managed launcher' $configDirectory
        Assert-AuthenticatedEntryUsesConfigDirectory $Name 'Current PowerShell entry' $configDirectory
        if ($env:CLAUDE_CONFIG_DIR -ne $callerConfigDirectory) {
            throw 'The launcher changed the caller CLAUDE_CONFIG_DIR instead of only its child process.'
        }
        Write-Output (New-Result -VersionCheckSucceeded $versionSucceeded -AuthStatusCommandSucceeded $true -LoggedIn $true)
        return
    }

    'Rollback' {
        $state = Get-LauncherState $launcherPath
        if ($state -eq 'Unmanaged') {
            throw "Refusing to remove an unmanaged launcher: $launcherPath"
        }
        if ($state -eq 'Absent') {
            Write-Output (New-Result)
            return
        }
        $existingLauncher = Get-LauncherContent $launcherPath
        if ($existingLauncher -ne $expectedLauncher) {
            throw "Refusing to remove a managed marker with a different account mapping: $launcherPath"
        }
        if ($PSCmdlet.ShouldProcess($launcherPath, "Remove managed $Name launcher without deleting its configuration directory")) {
            Remove-Item -LiteralPath $launcherPath -Force
            Write-Output (New-Result -Changed $true)
        }
        return
    }
}
