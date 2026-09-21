# tests

```sh
bash tests/run.sh            # everything; exits 0 only if all of it passes
bash tests/run.sh lint       # one stage: lint | engine | render | dialog | e2e
```

Needs WSL, or any Linux with GTK 3, `pyswisseph`, `python3-gi`, `xvfb-run`
and the Swiss Ephemeris `.se1` files. The Windows Python cannot run these —
it has no `swisseph`.

## The stages

| stage    | what it proves | seconds |
|----------|----------------|---------|
| `lint`   | no `self.X()` or `openAstro.X()` that will raise AttributeError; no GTK 2 constants | ~1 |
| `engine` | the astrology is right: each module against published values or Morinus | ~20 |
| `render` | every SVG table builds and Rsvg accepts it | ~30 |
| `dialog` | real GTK dialogs, driven headless: defaults, validation, what reaches the engine | ~5 |
| `e2e`    | the script loaded as a module, importing a file into real SQLite and reading it back | ~5 |

`lint` catches what `py_compile` cannot. Python resolves attributes at call
time, so a renamed method is a clean compile and a crash later — for a GTK
menu item, possibly months later. Both lint failures in this directory are
ones that actually reached a user.

## Two things that will waste an hour if you don't know them

**`HOME` is redirected to a throwaway directory, and must stay that way.**
`openAstroCfg()` creates and writes `~/.openastro.org/`, where `astrodb.sql`
holds the user's saved charts and settings. A harness that builds it against
the real `HOME` edits live user data; the `.bak-*` files next to that
database suggest this has already gone wrong once. Any new test that touches
`openAstroCfg`, `openAstroSqlite` or `openAstroInstance` must inherit the
sandbox from `run.sh` or make its own.

Two consequences follow from moving `HOME`, and both look like missing
dependencies when they bite:

- `pyswisseph` is installed per-user, under the real `$HOME`, and Python
  derives that path from `HOME` at startup. `run.sh` resolves the user
  site-packages *before* the redirect and puts it on `PYTHONPATH`.
- The `.se1` ephemeris files are not in this repository and
  `/usr/share/swisseph` is empty. They live in the real
  `~/.openastro.org/swiss_ephemeris/`. The sandbox gets a symlink to them:
  reads go to the real files, writes stay inside. Override with `OA_EPHE`.

**GTK needs `WAYLAND_DISPLAY` unset, not just `DISPLAY`.** Under WSLg, GDK
prefers Wayland and quietly ignores the `DISPLAY` that `xvfb-run` sets, so
the window opens on the real desktop instead of the virtual one. The
incantation that works:

```sh
env -u WAYLAND_DISPLAY -u DISPLAY GDK_BACKEND=x11 xvfb-run -a python3 ...
```

## Adding a test

Drop a `.py` file in the right stage directory. `run.sh` picks up everything
except files starting with `_`. Exit non-zero to fail — and check that it
*can* fail: break the thing on purpose and confirm the suite goes red. A
test that cannot fail is worse than no test, because everything downstream
believes it.

Which pattern to copy depends on what you are testing:

- **An engine module** — import it and assert. See `engine/harmo.py`.
- **A table that draws SVG** — the 11 table methods build the whole page
  with `string.Template` and write it *before* they touch GTK, so a stub
  window is enough. See `render/all_tables.py`.
- **A dialog** — that trick does not work, because there the widget tree
  *is* the result. Use real GTK and shim only what blocks: `Dialog.run()`
  and `MessageDialog.run()` are modal loops that hang forever with nobody
  to click them. See `dialog/transit_dialog.py`, which builds the real
  dialog, walks the widget tree, emits the click and reads the entries
  back.

What none of this can do is tell you whether a drawing looks *right*. A
reference image reports that something changed, never that it is good.
