# OpenAstro — working notes

A fork of OpenAstro 1.1.57, a GTK 3 / PyGObject astrology program. The whole
UI is one script, `openastro` (~9900 lines, five classes); the calculation
lives in `openastromod/`.

## Before anything else

**The Windows Python cannot run this.** `pyswisseph` is installed only in
WSL. Every script, test and check goes through `wsl python3`. A traceback
saying `No module named 'swisseph'` almost always means the wrong
interpreter, not a missing package.

**Verify before committing:**

```sh
bash tests/run.sh
```

19 checks, ~60 seconds, exit 0 only if all pass. See `tests/README.md`.
`py_compile` alone is not enough and never was: Python resolves attributes
at call time, so a renamed method compiles cleanly and crashes later — for a
GTK menu item, possibly months later. Both lint checks in `tests/lint/` exist
because exactly that reached a user.

## The shape of the code

Five classes in `openastro`, three of which are instantiated once into
module globals that the rest of the script reaches by name:

| global | class | what it is |
|---|---|---|
| `cfg` | `openAstroCfg` | paths, `~/.openastro.org/` |
| `db` | `openAstroSqlite` | the chart database and `astrocfg` settings |
| `openAstro` | `openAstroInstance` | the open chart, and all the drawing |

`mainWindow` is the menus and dialogs; `drawSVG` is the canvas widget. A
method on `openAstroInstance` is called from `mainWindow` as
`openAstro.method()`, never `self.method()` — that mistake is what
`tests/lint/` was written to catch.

Charts are SVG built from `string.Template`. There are **two independent
copies of the symbol set**: `openastro-svg.xml` (the wheel) and
`openastro-svg-table.xml` (the tables). A glyph added to one is not in the
other.

Derived charts (transits, progressions, directions, atacir) are bi-wheels:
`type="Transit"` plus the `t_*` arrays plus `biwheel_single`. `makeSVG()`
re-derives the `t_*` values on every redraw.

## Conventions

- **Commit messages in English**, small commits, one idea each. Say what
  changed and why; if something was verified, say how, with the numbers.
- **Never `git push` without being asked.** The credential helper here opens
  a GUI dialog, so an unattended push hangs rather than fails.
- Work on `feat/*` branches. `main` is merged by hand.
- Dialog parameters persist in `astrocfg` — except dates, deliberately:
  every technique dialog opens on the current moment.
- Keep personal data out of the repository. `TODO.md` and `AGENTS.md` are
  gitignored because they quote local paths and reverse-engineering sources.
  `*.db`, `*.sql` (bar the two shipped atlases), chart exports and PDFs are
  ignored too, since they carry birth data.

## Verifying astrology

Against published values or against Morinus, with real ephemeris — not
stubs. Precedents worth matching: primary directions agreed to the arcsecond
against carta-natal.es, the lunar return to 0.7 s, the atacir constant
reproduced Morinus' `K = 12.17473968` exactly.

When a number can be checked two ways, check it two ways. The harmogram's
Gaussian weighting predicts a mean of 7.76 for 100 pairs; measured over a
year of real transits it came out 7.97, which is what makes García's
`RNG = 15` plot range credible. Neither figure was fitted to the other.

## What the tests cannot tell you

Whether a drawing looks right. A reference image reports that something
changed, never that it is good. Anything about glyph weight, colour
separation or crowding needs a person to look at it — see the review block
at the top of `TODO.md`.
