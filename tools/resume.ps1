<#
.SYNOPSIS
    Resume unattended work on OpenAstro after the session died or the usage
    limit reset. Meant to be run by Task Scheduler.

.DESCRIPTION
    This is the fallback. The normal case is an open session rescheduling
    itself, which costs nothing and keeps its context; that lives only in
    memory, so it does not survive a closed terminal or a reboot. This does.

    It refuses to run when a live session is already working, so the two
    mechanisms cannot both act at once. The lock is a file holding a PID and
    a timestamp; a lock whose process is gone, or older than -StaleMinutes,
    is treated as abandoned and taken over.

.PARAMETER Prompt
    What to work on. Defaults to the standing instruction below.

.PARAMETER DryRun
    Print what would be run and exit. Use this first.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File tools\resume.ps1 -DryRun

.NOTES
    Register it to run only while the user is logged on. WSL needs a user
    session, and without one every `wsl python3` in the suite fails -- which
    would look like a broken test suite rather than a scheduling problem.

    -Model is passed explicitly on purpose: the global settings.json here
    sets "model": "sonnet", and a headless run would inherit it silently.
#>
[CmdletBinding()]
param(
    [string]$Prompt = @'
Continue the autonomous work on OpenAstro, following CLAUDE.md.

Pick the next item from the "Cola ejecutable" section of TODO.md. Do not
touch the "PENDIENTE DE REVISAR EN LA APLICACION" block -- those need a
person at a screen.

Work on a feat/* branch. Run `bash tests/run.sh` and do not commit unless it
exits 0. Never merge to main. Never push.

If the queue is empty, say so and stop rather than inventing work.
'@,
    [string]$Model = 'claude-opus-5',
    [int]$StaleMinutes = 90,
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Repo = Split-Path -Parent $PSScriptRoot
$LockFile = Join-Path $env:TEMP 'openastro-autonomy.lock'
$LogFile = Join-Path $env:TEMP 'openastro-autonomy.log'

function Write-Log([string]$Message) {
    # Write-Host, not Write-Output. Write-Output puts the line on the success
    # stream, which inside a function becomes part of its return value: a
    # logging Test-LockHeld returned @('...the log line...', $false), an
    # array of two, which is truthy. The fallback would then have stood down
    # every single time, including when the lock was dead -- and said nothing
    # about it, because the log line was swallowed as the return value.
    $line = '{0}  {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message
    Write-Host $line
    Add-Content -Path $LogFile -Value $line -Encoding utf8
}

function Test-LockHeld {
    if (-not (Test-Path $LockFile)) { return $false }
    try {
        $lock = Get-Content $LockFile -Raw | ConvertFrom-Json
    } catch {
        Write-Log 'lock file unreadable; treating as abandoned'
        return $false
    }
    $age = (Get-Date) - [datetime]$lock.started
    if ($age.TotalMinutes -gt $StaleMinutes) {
        Write-Log ('lock is {0:N0} min old (stale past {1}); taking over' -f $age.TotalMinutes, $StaleMinutes)
        return $false
    }
    $proc = Get-Process -Id $lock.pid -ErrorAction SilentlyContinue
    if (-not $proc) {
        Write-Log ('lock names PID {0}, which is gone; taking over' -f $lock.pid)
        return $false
    }
    Write-Log ('PID {0} is still working ({1:N0} min); standing down' -f $lock.pid, $age.TotalMinutes)
    return $true
}

function Get-LiveCliSessions {
    # The lock only knows about runs this script started. An interactive
    # session writes nothing, so without this check the scheduled task would
    # happily start a second agent on top of somebody working -- both of them
    # with --continue, on the same conversation.
    #
    # Match the CLI specifically. The Claude desktop app is also claude.exe
    # and runs a dozen helper processes; matching on the name alone would
    # mean this never runs while the app is open, which is most of the time.
    $me = $PID
    @(Get-CimInstance Win32_Process -Filter "Name='claude.exe'" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.CommandLine -and
            $_.CommandLine -match 'claude-code' -and
            $_.ProcessId -ne $me
        })
}

$live = Get-LiveCliSessions
if ($live.Count -gt 0) {
    Write-Log ('{0} claude-code session(s) already running (PID {1}); standing down' -f
        $live.Count, ($live.ProcessId -join ', '))
    exit 0
}

if (Test-LockHeld) { exit 0 }

# WSL is what runs the test suite; without a user session it is not there,
# and every check would fail for a reason that has nothing to do with the code.
& wsl.exe -e true 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Log 'WSL is not available (no user session?); not starting'
    exit 1
}

$claude = (Get-Command claude -ErrorAction SilentlyContinue)
if (-not $claude) {
    Write-Log 'claude is not on PATH; not starting'
    exit 1
}

$argv = @(
    '-p', $Prompt,
    '--continue',
    '--model', $Model,
    '--dangerously-skip-permissions'
)

if ($DryRun) {
    Write-Log 'DRY RUN, nothing started'
    Write-Log ('  repo   {0}' -f $Repo)
    Write-Log ('  lock   {0}' -f $LockFile)
    Write-Log ('  log    {0}' -f $LogFile)
    Write-Log ('  run    {0} -p <prompt> --continue --model {1} --dangerously-skip-permissions' -f $claude.Source, $Model)
    exit 0
}

@{ pid = $PID; started = (Get-Date).ToString('o'); repo = $Repo } |
    ConvertTo-Json | Set-Content -Path $LockFile -Encoding utf8
Write-Log ('starting, PID {0}, repo {1}' -f $PID, $Repo)

try {
    Push-Location $Repo
    & $claude.Source @argv 2>&1 | ForEach-Object { Write-Log "  $_" }
    Write-Log ('finished, exit {0}' -f $LASTEXITCODE)
} finally {
    Pop-Location
    Remove-Item $LockFile -ErrorAction SilentlyContinue
}
