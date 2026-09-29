# tools

Unattended operation. Nothing here is needed to work on OpenAstro by hand.

## What resumes work, and when

Two different limits get confused, and they need different answers:

- **Context** fills up mid-session. Handled automatically by compaction;
  nothing here touches it.
- **Usage**, the hourly window. This is what needs a wake-up.

**The normal case** is an open session scheduling its own wake-up past the
reset. It costs nothing and keeps its context. It lives only in memory, so it
does not survive a closed terminal, a crash or a reboot.

**The fallback** is `resume.ps1`, run by Task Scheduler, which does survive
those. It is a fallback and not the main path: it starts a fresh session with
`--continue`, so it picks up the conversation but not the reasoning in flight.

## Setting it up

```powershell
.\tools\register-task.ps1 -DryRunTask    # rehearse: the task runs, starts nothing
.\tools\register-task.ps1                # for real, every 30 minutes
.\tools\register-task.ps1 -Show
.\tools\register-task.ps1 -Remove
```

Off without removing, and back on:

```powershell
Disable-ScheduledTask -TaskName OpenAstroResume
Enable-ScheduledTask  -TaskName OpenAstroResume
Get-Content $env:TEMP\openastro-autonomy.log -Tail 40
```

The interval is not how often an agent starts. It is how long after a reset
before work picks up; most wake-ups stand down immediately.

## The interlocks

`resume.ps1` refuses to start when it would collide. In order:

1. **Any `claude-code` process is running.** This catches an interactive
   session, which writes no lock of its own — without it the task would start
   a second agent on top of somebody working, both with `--continue` on the
   same conversation. It matches the command line, not the executable name:
   the Claude desktop app is also `claude.exe` and runs a dozen helpers, so
   matching by name would mean this never ran while the app was open.
2. **A lock file held by a live process, newer than `-StaleMinutes`** (90).
   Older than that, or naming a process that is gone, or unreadable: taken
   over.
3. **WSL must answer.** It runs the whole test suite, and with no user
   session it is not there — every check would fail for a reason that has
   nothing to do with the code.

All five lock states were tested: live process, dead PID, stale, corrupt,
absent. So was the whole chain, with a rehearsal task that Task Scheduler
fired for real.

## Two things worth knowing

`-Model` is passed explicitly because the global `settings.json` on this
machine sets `"model": "sonnet"`, which a headless run would inherit in
silence.

**It never pushes.** The credential helper here opens a GUI dialog, so an
unattended push does not fail — it hangs until something kills it. The
standing instruction also keeps it off `main`: work lands on `feat/*`
branches and merging stays a human decision.

## If it is not running

```powershell
.\tools\register-task.ps1 -Show                      # state, last result, next run
Get-Content $env:TEMP\openastro-autonomy.log -Tail 40
```

A last result of `267011` on a task that has never run is normal — it means
"not yet", not a failure. The log says why each wake-up stood down; an empty
log means the task never fired at all, which is a Task Scheduler question
rather than a script one.
