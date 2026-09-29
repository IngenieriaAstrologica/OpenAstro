<#
.SYNOPSIS
    Register, inspect or remove the Task Scheduler entry that runs resume.ps1.

.DESCRIPTION
    Creates a task that wakes every -EveryMinutes and asks resume.ps1 whether
    there is work to pick up. resume.ps1 stands down on its own if a
    claude-code session is already running or a fresh lock is held, so the
    interval only decides how quickly work resumes after a limit resets, not
    how often an agent actually starts.

    The task runs only while the user is logged on, deliberately: WSL has no
    user session otherwise, and every check in tests/run.sh would fail for a
    reason unrelated to the code.

.EXAMPLE
    .\tools\register-task.ps1 -DryRunTask      # register, but only rehearse
    .\tools\register-task.ps1                  # register for real
    .\tools\register-task.ps1 -Show
    .\tools\register-task.ps1 -Remove

.NOTES
    Turning it off without removing it:
        Disable-ScheduledTask -TaskName OpenAstroResume
    And back on:
        Enable-ScheduledTask  -TaskName OpenAstroResume
    What it has been doing:
        Get-Content $env:TEMP\openastro-autonomy.log -Tail 40
#>
[CmdletBinding()]
param(
    [string]$TaskName = 'OpenAstroResume',
    [int]$EveryMinutes = 30,
    [switch]$DryRunTask,
    [switch]$Show,
    [switch]$Remove
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$Repo = Split-Path -Parent $PSScriptRoot
$Script = Join-Path $PSScriptRoot 'resume.ps1'

if ($Show) {
    $t = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if (-not $t) { Write-Host "no task named $TaskName"; exit 0 }
    Write-Host ("task      {0}" -f $t.TaskName)
    Write-Host ("state     {0}" -f $t.State)
    foreach ($a in $t.Actions) {
        Write-Host ("runs      {0} {1}" -f $a.Execute, $a.Arguments)
    }
    $i = Get-ScheduledTaskInfo -TaskName $TaskName
    Write-Host ("last run  {0}  (result {1})" -f $i.LastRunTime, $i.LastTaskResult)
    Write-Host ("next run  {0}" -f $i.NextRunTime)
    exit 0
}

if ($Remove) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "removed $TaskName"
    exit 0
}

$scriptArgs = '-ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File "{0}"' -f $Script
if ($DryRunTask) { $scriptArgs += ' -DryRun' }

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument $scriptArgs -WorkingDirectory $Repo

# Repeat forever from a fixed start, so it survives a reboot without needing
# an AtStartup trigger (which would fire before the user session exists).
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) `
    -RepetitionInterval (New-TimeSpan -Minutes $EveryMinutes)

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Settings $settings -Force | Out-Null

Write-Host ("registered {0}, every {1} min{2}" -f $TaskName, $EveryMinutes,
    $(if ($DryRunTask) { ', DRY RUN only' } else { '' }))
Write-Host ("  runs    powershell {0}" -f $scriptArgs)
Write-Host ("  log     {0}\openastro-autonomy.log" -f $env:TEMP)
Write-Host "  off     Disable-ScheduledTask -TaskName $TaskName"
