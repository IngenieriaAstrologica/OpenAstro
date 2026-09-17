# OpenAstro Changelog

Entries without a date come from the 2026-08-26 session.

Fork changes by jipejavier@gmail.com — notably the Lots of Fortune, Spirit and
Infortune (see the "Lot of Infortune" and "Lot of Fortune / Lot of Spirit"
sections below). The original software is by Pelle van der Scheer (GPL v3).

## Issue 1: Planets were not drawn on the chart

### Symptom
All planets appeared at the same position (18° Sagittarius) in the grid, and
only 4 minor points (south_node, Mc, night_pars, vesta) were drawn on the
chart wheel.

### Cause
Bug in `openastromod/swiss.py:95-102`. pyswisseph's `swe.calc_ut()` returns a
tuple: `((lon, lat, dist, speed_lon, speed_lat, speed_dist), flag)`.

The original code used `ret_flag[1]` (the integer flag, always 258) instead of
`ret_flag[0][0]` (the actual ecliptic longitude). Since 258 = 240 + 18, every
planet landed at 18° Sagittarius.

### Fix
```python
# BEFORE (bug):
if (ret_flag[1] >= deg_low):
    self.planets_degree[i] = ret_flag[1] - deg_low
    self.planets_degree_ut[i] = ret_flag[1]

# AFTER (fixed):
if (ret_flag[0][0] >= deg_low):
    self.planets_degree[i] = ret_flag[0][0] - deg_low
    self.planets_degree_ut[i] = ret_flag[0][0]
```

### Files changed
- `openastromod/swiss.py` (lines 94-102)

---

## Issue 2: Nodes and Lilith were not drawn

### Symptom
The symbols for mean_node, south_node, mean_apogee (Black Moon Lilith),
osc._apogee and other points with spaces in their names did not appear on the
chart.

### Cause
`svgSafeHref()` converts spaces to underscores:
`"mean node"` -> `"mean_node"`

But the `<symbol>` IDs in the SVG templates contained spaces:
`<symbol id="mean node">`

So `<use xlink:href="#mean_node">` could not find `<symbol id="mean node">`.
XML IDs cannot contain spaces, and references must match them exactly.

### Fix
Renamed every symbol ID containing spaces in both XML files:

| Original ID        | Fixed ID          |
|--------------------|-------------------|
| `mean node`        | `mean_node`       |
| `true node`        | `true_node`       |
| `mean apogee`      | `mean_apogee`     |
| `true lilith`      | `true_lilith`     |
| `osc. apogee`      | `osc._apogee`     |
| `south node`       | `south_node`      |
| `day pars`         | `day_pars`        |
| `night pars`       | `night_pars`      |
| `intp. apogee`     | `intp._apogee`    |
| `intp perigee`     | `intp_perigee`    |
| `marriage pars`    | `marriage_pars`   |
| `black sun`        | `black_sun`       |

### Files changed
- `openastro-svg.xml`
- `openastro-svg-table.xml`

---

## Issue 3: WSL did not show the GTK window

### Symptom
When OpenAstro was launched from PowerShell with `wsl -e bash -c "..."`, the
GTK window did not appear.

### Cause
`wsl -e bash -c "..."` runs a non-interactive shell that does NOT load
`~/.bashrc` or `~/.profile`, so the WSLg variables needed for the graphical
display were not set.

### Fix
A launch script, `launch.sh`, that sets the variables explicitly:

```bash
#!/bin/bash
export DISPLAY=:0                  # Local X11 display
export WAYLAND_DISPLAY=wayland-0   # Wayland display (WSLg)
export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir  # WSLg runtime directory (sockets)
cd "$(dirname "$(readlink -f "$0")")"   # the project folder
python3 openastro
```

### Usage
From the project folder, in PowerShell:
```powershell
wsl bash ./launch.sh
```

### File created
- `launch.sh` (repository root)

---

## Feature: Editable lat/lon in Edit Event

### Change
The "Edit Event" dialog showed lat/lon as a read-only `Gtk.Label`. They are
now editable `Gtk.Entry` fields where the user can type coordinates directly.

### Behavior
- Searching for a city (geonames or DB) fills in the fields automatically
- The user can overwrite the values by hand for coordinates that are not in
  the database
- A comma is accepted as the decimal separator (it is converted to a dot)
- The Location field is shown as a label below lat/lon

### Visual change
```
BEFORE:
  Latitude: 41.38879
  Longitude: 2.15899
  Location: Barcelona, Catalonia, Spain

AFTER:
  Latitude: [41.38879 ]  (editable)
  Longitude: [2.15899  ]  (editable)
  Location: Barcelona, Catalonia, Spain
```

### Files changed
- `openastro` (methods eventData, updateChartData, eventDataChangedCitybox)

---

## Feature: Node opposition removed

### Change
The mean_node <-> south_node opposition (always 180°) was removed from:
- `makeAspects()` — no aspect is generated
- `makeAspectGrid()` — no line is drawn
- `makePatterns()` — it is not included in patterns

### Rationale
The North and South Nodes are always in exact opposition. That is an
astronomical constant, not an aspect with interpretive value.

### Files changed
- `openastro` (lines ~2257, ~2401, ~2483)

---

## Feature: Lot of Infortune

### Change
New lot on the natal chart: the **Lot of Infortune**.

### Formula
```
Day chart:   Lot of Infortune = ASC + Mars - Saturn
Night chart: Lot of Infortune = ASC + Saturn - Mars
```
Until Issue 5 the day formula was applied to every chart.

### Symbol
**☩** Cross of Jerusalem (U+2629, a cross potent), taken from Wikimedia
Commons (public domain): an SVG glyph with the characteristic T-shaped ends.

### Database
```sql
-- settings_planet
id=35, name='lot_of_infortune', label='Lot of Infortune', short='LI'
visible=1, zodiac_relation=-1, color=#8B0000

-- color_codes
planet_35=#8B0000
```

### Files changed
- `openastromod/swiss.py` — ASC + Mars - Saturn calculation; normalization
  loop extended to `range(23,36)`
- `openastro-svg.xml` — `lot_of_infortune` symbol with the ☩ path
- `openastro-svg-table.xml` — `lot_of_infortune` symbol with the ☩ path
- `openastro` — `planet_35` color in `defaultColors`

---

## Feature: Lot of Fortune / Lot of Spirit — symbols fixed

### Change
The `day_pars` and `night_pars` symbols were swapped and the points renamed:

| ID | Previous name | New name | Symbol |
|----|---------------|----------|--------|
| 27 | Day Pars (DP) | Lot of Fortune (LF) | ⊗ (circle with a diagonal cross) |
| 28 | Night Pars (NP) | Lot of Spirit (LS) | ɸ (phi, U+0278) |

### Details
- **Lot of Fortune**: ASC + Moon - Sun (day) / ASC + Sun - Moon (night)
- **Lot of Spirit**: ASC + Sun - Moon (day) / ASC + Moon - Sun (night)
- The ɸ symbol was extracted from **Noto Sans Regular** with fonttools'
  SVGPathPen

### Database
The labels of points 27 and 28 were updated in `settings_planet`. They were
first stored in Spanish; the current English labels are listed under "Labels
and changelog in English" below.

### Files changed
- `openastro-svg.xml` — symbols day_pars (⊗) and night_pars (ɸ)
- `openastro-svg-table.xml` — symbols day_pars (⊗) and night_pars (ɸ)

---

## Issue 4: Invisible window under WSLg — `[WARN:COPY MODE]` (2026-09-11)

### Symptom
Running `python openastro` showed the icon in the Windows taskbar, but the
window was not visible. There were no errors in the console.

### Cause
A WSL/WSLg bug, not an OpenAstro one. When the distro restarts inside a WSL VM
that is already running, Weston (the WSLg compositor) fails to open the memory
it shares with Windows and falls back to "copy mode", in which windows stay
transparent. From `/mnt/wslg/weston.log`:

```
rdp_allocate_shared_memory: Failed to open "/mnt/shared_memory/{...}" with error: Input/output error
RDP backend: use_gfxredir = 0
```

On the Windows side the window existed (maximized, 1920x1032, not minimized),
but its title was `[WARN:COPY MODE] OpenAstro.org (Ubuntu)` and it was never
painted. On the Linux side everything was correct: GTK (Wayland backend)
created and painted the maximized window without problems.

- Versions: WSL 2.7.13.0, WSLg 1.0.73.2, kernel 6.18.33.2-2, Windows 10.0.26200.9445
- Issue: https://github.com/microsoft/wslg/issues/1456
- Root cause: https://github.com/microsoft/openvmm/issues/4274 — fixed in
  openvmm (PR #4311, 2026-08-31), but WSL 2.7.13 does not include the fix yet.
  Try `wsl --update` later.

### Diagnosis
```bash
grep use_gfxredir /mnt/wslg/weston.log | tail -1   # "= 0" -> broken, "= 1" -> OK
```

### Fix
Restart Weston inside the WSLg system distro. No sudo is needed: WSLGd
relaunches it automatically, and the second attempt does open the shared
memory.

```bash
wsl.exe --system -- sh -c 'kill $(pgrep -x weston)'
```

This closes any Linux GUI apps that are open. Alternative: `wsl --shutdown`
from PowerShell (it shuts down all of WSL). Repeat the fix whenever the
problem comes back, until the installed WSL version ships the fix.

### Note
An earlier fix attempt in `mainWindow.__init__` (`set_default_size` +
`maximize()`/`present()` after `show_all()`) was based on a wrong diagnosis
(GTK window size). It is not needed for this issue.

### Files changed
- None (WSL environment issue)

---

## Issue 5: Lots ignored the chart sect (night charts) — 2026-09-11

### Symptom
In a night chart, the Lot of Fortune and the Lot of Spirit were swapped and
the Lot of Infortune was wrong. In day charts (e.g., the natal chart used as a
reference) everything was correct.

### Cause
`openastromod/swiss.py` always applied the day formula of all three lots,
whether the chart was diurnal or nocturnal.

### Fix
The chart sect is now determined: the chart is diurnal if the Sun is above the
horizon (houses 7-12, i.e., between the Dsc and the Asc in zodiacal order). In
night charts the formulas are reversed:

| ID | Point | Day | Night |
|----|-------|-----|-------|
| 27 | Lot of Fortune | ASC + Moon - Sun | ASC + Sun - Moon |
| 28 | Lot of Spirit | ASC + Sun - Moon | ASC + Moon - Sun |
| 35 | Lot of Infortune | ASC + Mars - Saturn | ASC + Saturn - Mars |

### Verification
Compared with an independent calculation (Swiss Ephemeris called directly,
sect taken from the Sun's actual altitude):
- Night chart (2026-09-11 21:10 UT): Fortune 22°38' Tau,
  Spirit 11°19' Gem, Infortune 24°46' Aqu — correct.
- Natal chart (diurnal): unchanged — Fortune 9°44' Sag, Spirit 29°43' Pis,
  Infortune 16°11' Cap.
- 48-hour sweep in 7-minute steps (412 charts: 214 diurnal, 198 nocturnal):
  0 mismatches.

### Files changed
- `openastromod/swiss.py` — sect calculation and indices 27, 28 and 35

---

## Feature: Sign colors by element — 2026-09-11

### Change
Sign colors now follow their element: fire in reds, earth in greens, air in
yellows and water in blues. Within each element the shade depends on the
modality (cardinal medium, fixed deep, mutable light). Each glyph uses a
darker shade than its sector background so that it stays legible (the
background is drawn at 50% opacity).

| Sign (N) | Element | Background (`zodiac_bg_N`) | Glyph (`zodiac_icon_N`) |
|----------|---------|----------------------------|-------------------------|
| Aries (0) | Fire | #e53935 | #b71c1c |
| Leo (4) | Fire | #b71c1c | #7f0000 |
| Sagittarius (8) | Fire | #ef5350 | #c62828 |
| Capricorn (9) | Earth | #43a047 | #1b5e20 |
| Taurus (1) | Earth | #1b5e20 | #0e4a13 |
| Virgo (5) | Earth | #81c784 | #2e7d32 |
| Libra (6) | Air | #fdd835 | #9a7400 |
| Aquarius (10) | Air | #f0c000 | #8a6a00 |
| Gemini (2) | Air | #fff176 | #9c7c00 |
| Cancer (3) | Water | #1e88e5 | #0d47a1 |
| Scorpio (7) | Water | #0d47a1 | #002171 |
| Pisces (11) | Water | #64b5f6 | #1565c0 |

The element legend (Fire/Earth/Air/Water %) no longer uses hard-coded colors:
it takes the glyph color of the cardinal signs (Aries, Capricorn, Libra,
Cancer), so it follows whatever is set in Settings → Colors.

### Database
The 24 colors (`zodiac_bg_0..11`, `zodiac_icon_0..11`) were updated in the
`color_codes` table of `~/.openastro.org/astrodb.sql`. Backup taken before the
change: `~/.openastro.org/astrodb.sql.bak-2026-09-11-colors`.

### Files changed
- `openastro` — `defaultColors` (new databases) and `makeElements()` (legend)

---

## Repository: files missing from git — 2026-09-11

### Problem
A fresh clone of the repository did not start: only `openastro`,
`openastromod/swiss.py`, the SVG templates and little else were tracked. The
other `openastromod` modules, `openastro-ui.xml`, the translations (`locale/`)
and the icons (`icons/`, excluded by the `*.svg` rule in `.gitignore`) were
missing.

### Change
- Added the missing files: modules, UI definition, translations, icons,
  license, README and packaging.
- `.gitignore`: `*.svg` is kept with an exception for `icons/`; `geonames.sql`,
  `openastro.db` (31 MB each) and `old/` are now ignored.

### Note
`geonames.sql` (the offline city atlas) is not in git: in a new clone, copy it
by hand to the project root for the city search to work. `openastro.db` is an
identical copy that the app does not use.

### Verification
Fresh clone in a temporary folder, using the existing `~/.openastro.org`
database: the modules, translations, menus, window icon and aspect icons load,
and the chart is generated without errors.

---

## Labels and changelog in English — 2026-09-12

### Change
- This changelog was translated from Spanish into English and proofread. Two
  inaccuracies were corrected along the way: the files changed by the Lot of
  Infortune feature, and the location of `launch.sh`.
- The chart labels of points 27 and 28 were stored in Spanish in the local
  database. They are now `Lot of Fortune` (LF) and `Lot of Spirit` (LS); the
  short label of the Lot of Spirit changes from LE to LS.
- Point 35 follows the same "Lot of" convention: it is now the
  `Lot of Infortune` (LI), and its internal name and SVG symbol id are
  `lot_of_infortune`.
- Commit messages written in Spanish, or using names other than the "Lot of"
  ones, were reworded in the development history.
- Code comments corrected: `27=pars fortuna` → `27=lot of fortune`; the
  normalization loop covers indices 23 to 35 (not 32 to 35); the house degree
  normalization comment said "planet"; `decHourJoin()` takes no timezone; the
  window sizing comments no longer describe it as a WSLg fix.
- Spelling fixes found with codespell: "inconsistencies" and "subtract" in
  comments; "Customizable", "80,000" and the article in the `debian/control`
  description.

### Database
```sql
UPDATE settings_planet SET label='Lot of Fortune', label_short='LF' WHERE id=27;
UPDATE settings_planet SET label='Lot of Spirit', label_short='LS' WHERE id=28;
UPDATE settings_planet SET name='lot_of_infortune', label='Lot of Infortune', label_short='LI' WHERE id=35;
```
Backups taken before the changes: `~/.openastro.org/astrodb.sql.bak-2026-09-12-labels`
(points 27 and 28) and `~/.openastro.org/astrodb.sql.bak-2026-09-12-infortune`
(point 35).

### Files changed
- `CHANGELOG.md`
- `openastro` — comments only
- `openastromod/swiss.py` — comments only
- `openastro-svg.xml`, `openastro-svg-table.xml` — symbol id `lot_of_infortune`
- `debian/control` — package description wording

---

## Issue 6: New databases crashed at startup — 2026-09-12

### Symptom
With a new `~/.openastro.org` (first run on a machine, or after deleting the
folder), the app crashed while calculating the chart:
`IndexError: list assignment index out of range` in `openastromod/swiss.py`.

### Cause
Point 35 (Lot of Infortune) had only been added by hand to the local database.
The `settings_planet` defaults in `openastro` stopped at point 34, so a new
database had no row 35 and `swiss.py` had no slot for index 35.

### Fix
- Point 35 added to the `settings_planet` defaults: `lot_of_infortune`, label
  Lot of Infortune (LI), color #8B0000, visible, with aspect lines and aspect
  grid (the same values as the local database).
- The default labels of points 27 and 28 follow the "Lot of" convention: Lot
  of Fortune (LF) and Lot of Spirit (LS) instead of Day Pars (DP) and Night
  Pars (NP). These three labels have no translations yet, so other interface
  languages show them in English.

### Verification
Fresh `HOME` in a temporary folder: the database is created with 36 points and
the chart is generated without errors.

### Note
A fresh install also needs the Swiss Ephemeris files (e.g. `seas_18.se1`) in
`~/.openastro.org/swiss_ephemeris`; without them `swe.calc_ut()` fails. Like
`geonames.sql`, they are not in git: copy them from an existing installation.

### Files changed
- `openastro` — `settings_planet` defaults

---

## Typo in the duplicate-name warning — 2026-09-12

### Change
The warning "There is already an entry for this name, please choose another"
misspelled "already" in the code. The message is translatable, so the msgid
was also renamed inside the 20 compiled catalogs that translate it and in the
`.pot` template, keeping every translation. The catalogs are written like
CPython's `msgfmt.py` (entries sorted, no hash table), which Python's
`gettext` reads the same way.

### Verification
Each rebuilt catalog is identical to the previous one except for the renamed
msgid, and the message still appears translated (checked in Spanish, German,
French and Japanese).

### Files changed
- `openastro` — the message, in two dialogs
- `locale/*/LC_MESSAGES/openastro.mo` — 20 catalogs
- `locale/templates/openastro.pot`

---

## Feature: Windows launcher — 2026-09-12

### Change
`OpenAstro.bat` starts OpenAstro from Windows: it runs `launch.sh` from its own
folder in the Ubuntu WSL distro, and `launch.sh` sets the WSLg variables (see
Issue 3).
`OpenAstro.ico` is an icon for a Windows shortcut to it (16x16 to 256x256).

### Usage
Double-click `OpenAstro.bat`, or create a shortcut to it and set
`OpenAstro.ico` as the shortcut icon.

### Files created
- `OpenAstro.bat`
- `OpenAstro.ico`

---

## Public release preparation — 2026-09-12

### Change
- Personal data removed from this changelog (the birth data used as a
  reference and the home location in examples); the Edit Event example now
  uses Barcelona.
- `launch.sh` and `OpenAstro.bat` no longer contain the author's paths: they
  work from wherever the project folder is.
- `.gitignore` also excludes chart exports (`*.png`, `*.jpg`, `*.jpeg`, `*.pdf`,
  which contain birth data), databases (`*.sql`, `*.db`; `famous.sql` stays
  tracked), `desktop.ini` and Dropbox conflict copies.
- `README`: fork notes, current requirements, files not included in the
  repository, how to run the app, and credits for the lot symbols.
- The personal note marker in the `openastro` header was replaced.
- The public repository starts from a single commit with this state; the
  earlier development history is kept privately.

### Files changed
- `CHANGELOG.md`, `README`, `.gitignore`, `launch.sh`, `OpenAstro.bat`
- `openastro` — header comment only

---

## Python 3 modernization — 2026-09-16

### Change
- **Time zones migrated from `pytz` to the standard-library `zoneinfo`**
  (PEP 615, Python 3.9+); `pytz` is no longer recommended. The 10 call sites
  changed from `pytz.timezone(tz).localize(dt_input)` to
  `dt_input.replace(tzinfo=ZoneInfo(tz), fold=1)`; the naive-UTC conversion
  that follows is unchanged. `fold=1` reproduces pytz's old `is_dst=False`
  choice at the once-a-year ambiguous fall-back hour, so the result is
  identical to the previous `pytz` output in every case tested: 2400 normal
  times (10 zones × 5 years × 12 months × 4 times of day) plus the ambiguous
  DST hour in both hemispheres.
- **`setup.py` migrated from `distutils` to `setuptools`** — `distutils` was
  removed in Python 3.12, so the old file raised `ModuleNotFoundError` on
  modern Python.
- **`requirements.txt` rewritten** as a valid pip file (only `pyswisseph`;
  time zones now come from `zoneinfo`). The GTK 3 stack and ImageMagick are
  documented as system packages, not pip installs.
- `debian/control`: `X-Python-Version` raised to `>= 3.9` (required by
  `zoneinfo`).

### Files changed
- `openastro` — imports and the 10 time-zone conversions
- `setup.py`, `requirements.txt`, `debian/control`

---

## GTK 3 deprecation cleanup — 2026-09-16

Several deprecated GTK 3 / librsvg calls printed `DeprecationWarning`s on every
run (and would break under GTK 4). The isolated ones were fixed and verified
(the app runs and renders the chart correctly):

### Change
- **`Gdk.Screen.get_width()/get_height()`** → `Gdk.Display` + monitor geometry
  (`get_primary_monitor()` with a `get_monitor(0)` fallback, because Wayland/WSLg
  reports no "primary" monitor). Returns the same values. *(2 call sites)*
- **`Rsvg.set_default_dpi()`** (global, deprecated) → per-handle
  `Rsvg.Handle.set_dpi()` after the file is loaded. *(3 call sites)*
- **`Rsvg.Handle.render_cairo()`** (deprecated) → `render_document()` via a new
  `_rsvg_render()` helper that renders the SVG at its natural size. *(5 call sites)*
- **`Gtk.ScrolledWindow.add_with_viewport()`** → `.add()`, and an explicit
  `Gtk.Viewport` for the main chart area (the non-deprecated equivalent). *(8 sites)*

### Menu rewritten (removes the remaining ~12 warnings)
The whole menu was rewritten from the deprecated `Gtk.UIManager` /
`Gtk.ActionGroup` / `Gtk.Action` API to a hand-built **`Gtk.MenuBar`**:
- Static menus (Chart / Event / Settings / Chart Type / Tables / Zoom / Extra /
  About) as `Gtk.MenuItem` + submenus, reusing the existing callbacks. Each
  import/export item keeps its widget name via `set_name()` so `doImport` /
  `doExport` still detect the file format.
- The dynamic **History** and **Quick Open Database** submenus are rebuilt in
  `updateUI()` (now repopulating two `Gtk.Menu`s instead of UIManager merge-ids).
- **Zoom** is a `Gtk.RadioMenuItem` group.
- Keyboard accelerators (Ctrl+N / O / S / E / Q) via a `Gtk.AccelGroup`.
- `openastro-ui.xml` is no longer read (kept in the tree for reference).

### Dialog widget constructors modernized
Converted the deprecated positional-argument constructor calls across all
dialogs to keyword arguments (125 calls), silencing the "Using positional
arguments…" warnings without changing widget types or layout:
- `Gtk.Window(type=…)` (7), `Gtk.Label(label=…)` (97),
  `Gtk.HBox`/`Gtk.VBox(homogeneous=…, spacing=…)` (13), `Gtk.Table(n_rows=…, …)` (9),
  `Gtk.Button(label=…)` (20), `Gtk.TreeView(model=…)` (2).

### Edit Event / New Chart no longer require the atlas
`eventData`, `settingsLocation` and their apply handlers used the offline
geonames dropdowns when online geocoding is off, and crashed with "no such
table: continent" if `geonames.sql` was not installed. They now fall back to
the manual/online location entry (via the existing `geoname.search`, which
already fails gracefully offline) whenever the atlas is absent. Added
`db.hasGeonames()`.
- Removed 14 no-op `set_col_spacings(0)` / `set_row_spacings(0)` calls (0 is the
  default), clearing those warnings with no visual change.
- `Gtk.Table` and the boxes were kept (not migrated to `Gtk.Grid`/`Gtk.Box`):
  that would mean rewriting 127 `.attach()` calls to a different API, which
  can't be verified in this environment.

### Stock items removed
Replaced all deprecated `Gtk.STOCK_*` usage (61 occurrences): `Gtk.Button(stock=…)`
became `Gtk.Button.new_with_mnemonic(_("…"))`, and the stock IDs inside dialog
button tuples became plain translatable labels. Buttons now show a text label
instead of a stock icon (the modern GTK style).

### Still pending
- `Gtk.Widget.modify_base` (widget background colour) — the replacement needs a
  CSS provider; deferred.
- `Gtk.Table.set_row_spacing` / `set_*_spacings(15)` (8 calls in a few dialogs) —
  removing these needs `Gtk.Table` → `Gtk.Grid`, i.e. rewriting 127 `.attach()`
  calls to a different API; deferred as too risky to do without a GTK runtime.

### Not a code issue — window opened minimized under WSLg
While testing, the window came up minimized. This was traced to **WSLg, not the
code**: even a bare `show_all()` + `present()` with no `maximize()`, on both the
X11 and Wayland backends — and even `xclock` — failed to show a window. It was
fixed at the environment level with `wsl --shutdown` / `wsl --update`. No code
change was needed and the window-show logic was left unchanged.

### Files changed
- `openastro` — screen size, SVG DPI/rendering, and the main chart viewport

---

## Data files — 2026-09-17

- **`famous.sql`** — the ~364 KB famous-people SQLite atlas (~2000 public
  figures, from the GPL `openastro.org-data` package) is now bundled in the
  repo, so "Open Famous People Database" works out of the box.
- **`geonames.sql`** — the ~31 MB offline city atlas (~150k places) is also
  bundled in the repo, so the offline city search works out of the box.
- Missing-atlas paths degrade gracefully: `gnearest()` and `getDatabaseFamous()`
  return empty instead of crashing when their table is absent, and Edit Event /
  Set Home Location fall back to manual/online entry.

### Secondary Progressions fixed
`swiss.py:years_diff()` called `swe._years_diff()` and `swe._revjul()`, which do
not exist in pyswisseph, so "Chart Type → Secondary Progressions" crashed with
`AttributeError`. Replaced them with the standard day-for-a-year formula
(`jd1 + (jd2-jd1)/365.248193724`) and `swe.revjul()`.

### Synastry / Composite / Combine selection fixed
`openDatabaseSelectReturn()` used a `list` variable that was only assigned inside
the match loop, so it raised `UnboundLocalError` when no row was selected (or no
match was found). It now returns early on an empty/unmatched selection instead
of crashing.

---

## Bi-wheel view and Chart View selector — 2026-09-17

### Change
- **Solar Return** and **Secondary Progressions** are now drawn as a **bi-wheel**
  by default: the natal chart on the inside and the return / progressed chart on
  the outside (reusing the transit ring), instead of a single wheel.
- New **Chart Type → Chart View** radio submenu to switch the current bi-wheel
  between **Both**, **Inner only** and **Outer only**.
- The selector covers all four bi-wheel charts: **Solar Return**, **Secondary
  Progressions**, **Transit Chart** and **Synastry**. "Inner only" always shows
  the natal chart; "Outer only" shows the return, the progressed chart, the
  transit moment or the partner's chart respectively. (A fifth bi-wheel,
  **Dodecatemoria**, was added later — see below.)

### How it works
- Each bi-wheel chart copies its outer chart into the transit slots (`t_*`) and
  sets `type="Transit"`, then records two markers: `solar_active` (a bi-wheel is
  on screen, so Chart View applies) and `biwheel_single` (which single-wheel type
  "Outer only" must render — `Solar`, `SecondaryProgression` or `TransitOuter`).
  This is done by `localToSolar()`, `localToSecondaryProgression()`,
  `specialTransit()` and `openDatabaseSelectReturn()` (Synastry).
- `solarView()` applies the chosen mode by reusing the render paths: `Transit`
  (both), `Radix` (inner) and the recorded `biwheel_single` type (outer), then
  redraws. It does nothing unless a bi-wheel is on screen, and `specialRadix()`
  clears the markers when you go back to a plain natal chart.
- `TransitOuter` is a new render type: it draws the `t_*` chart on its own, with
  its own houses, like a radix of that moment — needed because transits and
  synastry had no existing single-wheel type for their outer chart.

### Files changed
- `openastro` — `localToSolar`, `localToSecondaryProgression`, `specialTransit`,
  `openDatabaseSelectReturn`, the `TransitOuter` branch in `makeSVG`, the
  `Chart View` submenu and the `solarView` handler

---

## Feature: Dodecatemoria chart — 2026-09-17

### Change
- New **Chart Type → Dodecatemoria Chart**: a **bi-wheel** with the radix on the
  inside and the **dodecatemorias** of every natal position on the outside
  (reusing the transit ring). The **Chart View** submenu applies as usual:
  **Both**, **Inner only** (radix) and **Outer only** (dodecatemorias alone on
  the natal house frame).
- Bonus: the Both view also draws the radix–dodecatemoria aspects.
- Formula ported from Morinus (`antiscia.calcDodecatemoria`):
  `dodec = 30*sign + 12*relative_longitude (mod 360)` — each 30° sign expands
  ×12 over the zodiac (2.5° slices). No extra ayanamsa step: OpenAstro
  longitudes already come in the configured zodiac (tropical/sidereal).

### How it works
- `openastromod/swiss.py` — new `calc_dodecatemoria()` plus per-body
  `planets_dodecatemoria_ut` / `houses_dodecatemoria_ut` (sign + in-sign degree)
  computed in `ephData`.
- `openastro.localToDodecatemoria()` derives the outer wheel from the radix
  into `t_*` and sets `type="Transit"`, `solar_active=True`,
  `biwheel_single="Dodecatemoria"` (no new date needed — unlike returns).
- `makeSVG()` re-derives `t_*` from the radix when
  `biwheel_single == "Dodecatemoria"`, because the `Transit` branch rewrites
  `t_*` from `t_year` (= natal) on every redraw. New `type == "Dodecatemoria"`
  branch renders the single-wheel "Outer only" view: dodecatemoria planets on
  natal houses.
- `specialDodecatemoria()` + Special-menu entry; `solarView()` needed no
  changes (it already dispatches through `biwheel_single`).

### Files changed
- `openastro` — `localToDodecatemoria`, `specialDodecatemoria`, the
  `Dodecatemoria` branch and outer-wheel override in `makeSVG`, the Special
  menu entry
- `openastromod/swiss.py` — `calc_dodecatemoria`, dodecatemoria attributes
- `openastro-ui.xml` — reference menu entry (file kept for reference only)

---

## Feature: Primary Directions chart — 2026-09-17

### Change
- New **Chart Type → Primary Directions**: a **bi-wheel** with the radix on
  the inside and the **topocentric primary-direction positions** (Polich-Page)
  for the requested date on the outside (reusing the transit ring). The
  **Chart View** submenu applies as usual: **Both**, **Inner only** (radix)
  and **Outer only** (directed chart alone, with directed houses).
- The dialog asks the target date, the **time key**: Naibod
  (0.9856473663°/year, default), Ptolemy (1°/year) or solar arc in RA — the
  **direction**: direct or converse (negated arc, towards the past) — and the
  **measure**, following the three chart kinds of
  carta-natal.es/direcciones-primarias.php: ecliptic directed / natal
  ecliptic, i.e. Marr-directed ecliptic longitudes with zodiacal aspects
  (the default); ascensional directed / natal ascensional, i.e. both wheels
  rendered in oblique-ascension space with an equal OA-frame and aspects on
  OA differences; or ascensional directed / natal ecliptic, i.e. the natal
  ecliptic wheel with the directed positions overlaid.
- Directed are the visible bodies and the cusps, each under its own
  topocentric pole; natal aspects/orbs config applies to the drawing as usual.
- The "Directed to Natal" list shows, per contact, the directed body, the
  aspect glyph, the natal body, and the ARC orb in DMS (exact perfection
  arc minus elapsed arc, both aspect rays tried) with applicative (green
  +/A) vs separative (red −/S) — rectificacion report style — sorted
  tightest-orb first.

### How it works
- `openastromod/primary.py` — port of the verified `primary_directions.py
  ` engine (15/16 Starkman directions within 2'): oblique ascension under the
  significator's topocentric pole, arc added on the equator, Marr's Ascendant
  formula back to the ecliptic. Only stdlib + swisseph.
- `openastromod/swiss.py` — `ephData` now also stores ecliptic latitudes,
  the RAMC (`ascmc[2]`, sidereal-time fallback) and the birth JD.
- `openastro.localToDirected()` derives the outer wheel from the radix into
  `t_*` and sets `type="Transit"`, `solar_active=True`,
  `biwheel_single="Directed"`. `makeSVG()` re-derives `t_*` from the stored
  arc on every redraw (the `Transit` branch rewrites `t_*` from `t_year`);
  new `type == "Directed"` branch renders the single-wheel "Outer only" view.
  In ascensional measure both wheels render in OA space (`oa_positions()`,
  equal OA-frame houses, aspects on OA differences); the ecliptic measures
  render Marr-directed ecliptic longitudes (`direct_frame()`).
- `specialDirected()` dialog (date, time key, direct/converse, measure;
  last used values remembered in `astrocfg`) + Special-menu entry;
  `solarView()` needed no changes (it already dispatches through
  `biwheel_single`).

### Files changed
- `openastro` — `localToDirected`, `specialDirected`/`specialDirectedSubmit`,
  the `Directed` branch and outer-wheel override in `makeSVG`, directed
  frame grab, Special menu entry
- `openastromod/primary.py` — new engine module
- `openastromod/swiss.py` — latitudes, RAMC, birth JD
- `openastro-ui.xml` — reference menu entry (file kept for reference only)
