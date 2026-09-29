# The `.DHQ` file format (ARMON.EXE)

ARMON.EXE is a 1996 DOS/Windows 3.1x program by Miguel García (Alicante)
that draws harmonic transit charts, natal harmograms and the "Harmonic
Flower" vector diagrams later reimplemented from first principles in
`openastromod/harmogram.py` and `openastromod/harmonicvector.py`. Its
plotting configuration — which curves to draw, in what color, over what
date range, weighted by which wave function — is stored in `.DHQ` files.

This document reverse-engineers that format from two sources:

- **The corpus**: 129 `.DHQ` files shipped with ARMON, at
  `SOFTWARE ASTROLOGIA\KeplerCPA_y_Armon\*.DHQ` in the project's backup
  tree. All 129 were parsed programmatically; the grammar and value ranges
  below are measured across the whole set, not guessed from one example.
- **The manual**: `ARMON.TXT` (a short README) and `ARMON1.DOC` (an old
  Word 6 binary `.doc`, read via `strings` since no `.doc` converter was
  available in this environment — recovers body text but loses accents and
  paragraph structure). Both are by the same author and independently
  corroborate several field meanings below.

Two other files mentioned as possible sources were checked and turned out
not to be useful:

- **`AYUDAS.HLP`** is genuine ISO-8859 text, but it is a 1 KB file
  containing exactly one help topic (`evaluar_archivos`, about a CPA/Kepler
  file-filtering screen unrelated to `.DHQ` plotting). It is not ARMON's
  help file and has nothing to do with this format.
- **`ARMOCUAN.DOC`** (and the much larger `ARMOCU2.DOC`, not in the task's
  original list but present alongside it) is not a technical manual either
  — `strings` recovers a first-person allegorical essay ("La Torre de los
  Armónicos", a tower-of-harmonics narrative) about the *meaning* of each
  harmonic number. It has no field-level detail and isn't cited further
  here.

**`ARMONIC.MOD`**, by contrast, turned out to be directly useful: it is a
separate, simpler config file (not itself in `.DHQ` grammar) holding the
program's default per-harmonic color and line-style table. Its values
cross-validate the `LES`/`LCL` grammar recovered from the corpus (see
§4.5).

No personal/birth data was found in any `.DHQ` file inspected — these are
purely plotting parameters (colors, orbs, harmonics, wave shapes, date
expressions). A couple of files carry an author's private phone number in
free-text comments outside the `.DHQ` corpus (`ARMON.TXT`); that is not
reproduced here beyond what's already in this document's citation of it.

---

## 1. File-level structure

### 1.1 Encoding and line endings

`.DHQ` files are single-byte-per-character text, ISO-8859-1 in practice
(observed accented bytes are Latin-1: `\xf3`=ó, `\xe1`=á, `\xed`=í, etc.),
terminated `CRLF`. One file (`_0WAVEF.DHQ`) contains a single stray
non-Latin1-alphabetic byte (`0xEE`) inside an otherwise normal record —
see §4.9.

### 1.2 The record grammar

Every non-empty line is a fixed-width header followed by a value that
fills out the rest of the line:

```
SSSIIILLL<value>
```

- `SSS` — 3-char, right-justified, signed decimal **section number**.
- `III` — 3-char, right-justified decimal **field index** (0-based,
  meaning depends on the section — see below).
- `LLL` — 3-char, right-justified decimal **value length**, in bytes.
- `<value>` — exactly `LLL` bytes, running to the end of the line (never
  padded, never truncated — verified across all 129 files, 0 mismatches).

There is no delimiter between the three integer fields or between the
length and the value; the grammar is purely positional. Confirmed with a
byte-exact slice test (`line[0:3]`, `line[3:6]`, `line[6:9]`, `line[9:9+L]`)
against every line of every file in the corpus — zero parse errors, zero
length mismatches.

A file ends with a trailing `CRLF` (so splitting on `\r\n` yields one
trailing empty string to discard) and nothing else — no final sentinel
byte, no checksum.

### 1.3 Sections

| Section | Role | Present in corpus |
|---|---|---|
| `-1` | **Title.** One record, `idx=0`, free-text description of the whole file (what appears as the entry's name in ARMON's "Diseño de Página" picker). | 129/129 files, always exactly one record |
| `0` | **Field-code table.** Declares which field codes this file uses and at what index. One record per code, `idx` = the field index used everywhere else in the file, value = the 3-letter code (`FCH`, `NDY`, ...). | 129/129 files — and **every file declares the identical 16 codes, in the identical order** (see §2). No file was found that adds, drops, or reorders a code. |
| `1` | **Field labels.** Human-readable Spanish label for each code from section 0, at the same `idx`. Purely descriptive — the parser doesn't need it, but it self-documents the format and is why the codes could be cross-checked (§2 pairs every code with its section-1 label; all 129 files agree on every pairing). | 129/129 |
| `2, 3, 4, …` | **Bands.** Each section number ≥ 2 is one plotted curve/band. `idx` inside a band section is the field index from section 0 (so `idx=4` is always `RTL`, the band's label, etc.) — **not** a running record counter. | 129/129, `2..N` with N observed from 3 (2 bands) to 14 (13 bands) |

So the "section 0 lists field codes, section 1 gives labels, sections ≥2
are bands" description from the initial read holds exactly, with one
addition: there is always a section `-1` title record ahead of section 0,
which the initial read didn't mention.

### 1.4 Sparse bands: field inheritance

Only the first band (section 2) of a file reliably carries every field.
Later bands typically specify only `QBN, RTL, LCL, LES, AOH` (indices
3–7) — the per-band essentials (marker/order, label, color, line style,
harmonic:orb) — and omit `PRE, PEM, ZDT, MDY, WAV, RES, FES, RNG` (indices
8–15), which are file-wide settings established once in band 1. `FCH, NDY,
NDP` (indices 0–2, the date/sampling window) are logically file-scoped
too: they appear in band 1 of every file, and only exceptionally — 2 of
129 files (`0INTMERC.DHQ` bands 1–2, `_JUPSAT.DHQ` bands 1–2) — are
redundantly restated in a second band, always with the *same* value, never
a genuine override.

The corpus never contradicts "an omitted field carries the value last set
for that field index, walking sections in order" — but because in every
observed file all the overrides that do happen for fields 8–15 happen in
band 1 and are never revisited, the corpus **cannot distinguish** "inherit
from band 1" from "inherit from nearest preceding band" — they're
equivalent for every file that exists. A parser should implement the more
general "carry forward the last explicit value per field index" rule,
which satisfies both readings. See §5.1.

---

## 2. Field-code table

All 16 codes below appear, in this exact order, in section 0 of all 129
files, and section 1 pairs each with exactly the Spanish label shown — no
file was found with a different label for a given code (i.e. the
self-description is fully consistent corpus-wide).

| Idx | Code | Label (§1, Spanish) | Meaning | Value grammar | Observed range |
|---|---|---|---|---|---|
| 0 | `FCH` | Fecha | Start date of the plotted window | `d/m/yyyy` literal date **or** a relative keyword, optionally with a signed integer offset, **or** a `$`-prefixed program variable — see §4.1 | 57 distinct values across 131 occurrences |
| 1 | `NDY` | Número de Días | Length of the window, in days (or years, if `FCH` selects a progression technique) | integer | 1 to 36525 (an entire century, in `CRR_F10.DHQ`/`CRR_F12.DHQ`); also `-1` seen once (`7HOLO.DHQ`, alongside `RNG=-1` — likely a sentinel, see §4.4) |
| 2 | `NDP` | Nº de partes/día | Sampling resolution: parts (samples) per day. Per `ARMON1.DOC`, must be raised whenever the Moon is a receiver/emitter, since it's by far the fastest body | integer or decimal | `0.01` to `288`; most common are `36` and `1` |
| 3 | `QBN` | Banda | Per-band integer, semantics genuinely unclear — see §4.2 | integer | almost always `1`; observed ascending/descending runs up to 12 in files using non-default `WAV` values |
| 4 | `RTL` | Rótulo | Band label / legend text | free text | 167 distinct values: mostly short (`x11`, `H3`, `2`), sometimes a full aspect name (`Trigono`, `Conj`) or a planet/body name (`Saturno`, `La Tierra`) |
| 5 | `LCL` | Color | Band's line color | one of a fixed Spanish color-name vocabulary | see §4.5 — 11 distinct names observed |
| 6 | `LES` | Estilo:Grosor | Line dash-style : stroke weight | `[\|/]?(token)+:N` — see §4.6 | 87 distinct values, weight `N` observed 1–16 |
| 7 | `AOH` | Armónico:Orbe | Which harmonic(s)/aspect(s) this band plots, and their orb | see §4.7 — by far the richest field | 81 distinct value shapes |
| 8 | `PRE` | Receptores | The bodies that **receive** the aspect (per `ARMON1.DOC`, "Receptores"/"Emisores" is nominal — `R:`/`T:` prefixes inside the value are what actually distinguish Radix from Transiting points) | `(prefix:letters)(,prefix:letters)*` — see §4.8 | 81 distinct values |
| 9 | `PEM` | Emisores | The bodies that **emit** the aspect | same grammar as `PRE` | 64 distinct values |
| 10 | `ZDT` | Zodiaco | Zodiac used | free text, effectively an enum | `trópico` (128×) / `tropico` (2×, unaccented variant — same value) |
| 11 | `MDY` | Forma | Curve "shape" | free text, effectively an enum | `picos` (peaks) in all 130 occurrences — **no other value was found in the corpus**, so this field's alternatives (there presumably are some, since it has its own label) are undocumented — see §5.2 |
| 12 | `WAV` | Onda | Wave/weighting function used to turn aspect-orb-closeness into plotted amplitude | free text, effectively an enum | 16 distinct values — see §4.10 |
| 13 | `RES` | Resonancia | Physical "resonance" model layered on top of the wave function | free text, effectively an enum | `No` (120×) / `marea` (tide, 14×) / `inercia` (inertia, 2×) |
| 14 | `FES` | Factor de escala | Vertical scale factor applied to the band | decimal (occasionally integer-looking, e.g. `1`, `5`) | `0.04` to `1000.0`; default is `1.0` (115/148 occurrences). One outlier, `c:27.69231` in `RIEMANN.DHQ`, reuses the `AOH`-style `letter:number` shape — almost certainly an experimental scratch file, not a second grammar for this field (see §4.7 note) |
| 15 | `RNG` | Rango | Plot range (vertical axis half-range, in the band's native units) | integer (occasionally decimal, e.g. `1.5`, `3.25`) | `1` to `15`; `-1` observed twice (`7HOLO.DHQ`, `7HOLOGRM.DHQ`), likely an "autoscale" sentinel — see §4.4 |

This is a complete accounting of every field code found in all 129
sample files. No code outside this set of 16 was observed anywhere in the
corpus.

---

## 3. Worked example: `CLRDINXX.DHQ`

`ARMON.TXT` names this file explicitly as the program's primary example:
*"El que más utilizamos en este momento (27-11-96) es el CLRDINXX.DHQ.
Corresponde al trazado del Harmograma natal de los once primeros
armónicos"* — the natal Harmogram of the first eleven harmonics. Full file,
annotated:

```
 -1  0 62Harmograma natal. Centrado en la fecha. Sólo aspectos propios.
```
Section `-1`, idx `0`, length `62`: the file's title, shown in ARMON's
design picker. "Natal harmogram. Centered on the date. Own aspects only."
("Own aspects" = the `xN` notation in `AOH`, §4.7 — aspects proper to
harmonic N, not reducible to a lower harmonic's aspects.)

```
  0  0  3FCH
  0  1  3NDY
   ... (all 16 codes, idx 0..15, see §2 table for the full list)
  0 15  3RNG
```
Section `0`: declares the 16 field codes at their indices — identical in
every file in the corpus.

```
  1  0  5Fecha
  1  1 14Número de Días
   ... (all 16 labels)
  1 15  5Rango
```
Section `1`: the Spanish labels, paired 1:1 with section 0 by `idx`.

```
  2  0  8centrada
  2  1  13
  2  2  248
  2  3  11
  2  4  3x11
  2  5  7Magenta
  2  6  9\AaAaDa:3
  2  7 12x11:27.69231
  2  8 12T:lhvemjsunp
  2  9 12T:lhvemjsunp
  2 10  7trópico
  2 11  5picos
  2 12  5suave
  2 13  2No
  2 14  31.0
  2 15  210
```
Section `2` — band 1, harmonic 11:
- `FCH="centrada"` — window centered on the reference date (see §4.1).
- `NDY="3"`, `NDP="48"` — 3 days, 48 samples/day.
- `QBN="1"` (this file never uses a non-default `QBN`).
- `RTL="x11"` — legend label: harmonic 11's *own* (proper) aspects.
- `LCL="Magenta"`.
- `LES="\AaAaDa:3"` — dash pattern `\AaAaDa`, weight 3.
- `AOH="x11:27.69231"` — harmonic 11's own aspects, orb 27.69231° (in the
  harmonic circle — see §4.7 for why this specific constant recurs
  across the whole corpus).
- `PRE=PEM="T:lhvemjsunp"` — all ten core bodies (Moon, Mercury, Venus,
  Sun, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto — §4.8), transiting
  ("T:") — since `PRE` and `PEM` are identical, this is a natal harmogram
  measuring the chart against itself, not a two-party transit.
- `ZDT="trópico"`, `MDY="picos"`, `WAV="suave"` (smooth/Gaussian-like
  weighting), `RES="No"` (no resonance model), `FES="1.0"`, `RNG="10"`.

```
  3  3  11
  3  4  3x10
  3  5  4Cian
  3  6  8AaAaDa:2
  3  7  3x10
```
Section `3` — band 2, harmonic 10: only the per-band essentials
(`QBN,RTL,LCL,LES,AOH`) are given; `PRE,PEM,ZDT,MDY,WAV,RES,FES,RNG`
inherit band 1's values (§1.4). Note `AOH="x10"` has **no orb suffix** —
the orb is presumably a program-side default when omitted (unconfirmed,
§5.3).

Sections `4` through `12` repeat the same shape for harmonics 9 down to 1
(`x9,x8,x7,x6,x5,x4,x3,x2` then, notably, section `12`'s `RTL="H1"` —
switching notation from `xN` to `HN` for the harmonic-1 band, with an
*empty* `AOH` value, `length=0`). This is the file's title's promise made
concrete: eleven bands, harmonics 11 down to 1, "own aspects" only.

---

## 4. Field grammars in detail

### 4.1 `FCH` — Fecha (date)

Two shapes, both confirmed against `ARMON1.DOC`'s own description:

1. **Absolute date**: `d/m/yyyy` (e.g. `20/1/1996`) or `d-m-yyyy`
   (2 files use hyphens instead of slashes: `2YJUPIT.DHQ`, `LALI01.DHQ`).
   The manual is explicit that the year must be written in full.
2. **Relative keyword**, optionally `+`/`-` an integer offset:
   `centrada`/`centrado` (window centered on the reference date — used
   for natal harmograms), `mes` (first day of the current month; `mes-1`,
   `mes+1` seen), `hoy` (today; `hoy-20` seen), `natal` (the chart's own
   birth date), `sec`/`secundaria` (secondary-progression technique,
   starting at the given age — `sec+40`, `secundaria-5` etc. — per
   `ARMON1.DOC`: *"si, en vez de una fecha se escribe sec+aa el programa
   calculará progresiones armónicas empezando en la edad aa"*).

A third, rarer shape uses a `$`-prefixed single-letter **program
variable** instead of a literal value: `$f` (8 occurrences, presumably
"fecha" — a live-bound date, e.g. "today" resolved at calculation time)
and `sec+$e` (5 occurrences, "edad" — age bound to a UI field rather than
hardcoded). The exact binding mechanism is not documented anywhere in the
corpus or manual — flagged as open in §5.4.

### 4.2 `QBN` — Banda

Labelled "Banda" (band), but its actual semantics are not what that name
suggests: it is **not** a running band index (bands are already numbered
by their section number) and it is **not** consistently a boolean flag
either. In most files it's a constant `1` for every band (949/1152
occurrences). But in files whose band 1 uses a non-default `WAV`
(`holo/*`, `vector`, `energia`), `QBN` instead runs as an ascending or
descending integer sequence across the bands (e.g. `7HOLO.DHQ`: `11, 10,
9, …, 1`, exactly tracking each band's harmonic number, descending;
`_0EM_VEC.DHQ`: `2, 3, 4, …, 12`, ascending). The working hypothesis —
supported but not proven — is that it's a per-band *order/weight index*
consumed specifically by the `holo/*` (Fourier-style) and `vector` wave
functions to know each band's position in a synthesis sequence, and
otherwise left at its default of `1`. Not confirmed against source code
(there is none available) or the manual (which doesn't mention it) —
open question, §5.5.

### 4.3 `RTL` — Rótulo (band label)

Free text. Most bands use a short mnemonic tied to `AOH` (`x11`, `H3`),
but it's genuinely freeform — full aspect names (`Conj`, `Opos`,
`Trigono`, `Cuad`, `Sext`), planet names (`Saturno`, `Júpiter`), or
arbitrary experiment labels (`Suma`, `CARGAS`, `EXCESO`, `STRESS`) all
appear. No grammar to document beyond "string".

### 4.4 `RNG` and `NDY` sentinel `-1`

`7HOLO.DHQ` and `7HOLOGRM.DHQ` (both titled "Hologram" designs using
`WAV=holo/l` / `holo/a`) set `RNG="-1"` on band 1. Every other file uses a
small positive number (1–15). The natural reading is "autoscale — don't
clamp to a fixed range", but this is inferred from context (both files
are `holo/*` Fourier-synthesis designs where a fixed range would make
little sense), not confirmed by the manual. `7HOLO.DHQ` also sets
`NDY="-1"` on the same band 1 record, alongside `FCH="centrada"` — this
second `-1` is unexplained; it does not fit "autoscale" the way `RNG=-1`
plausibly does. Left as open, §5.6.

### 4.5 `LCL` — Color

A closed Spanish color-name vocabulary — all 1175 occurrences across the
corpus use one of exactly 11 names: `Verde, Rojo, Cian, Azul, Naranja,
Negro, Magenta, Amarillo, Marron, Siena, Gris` (green, red, cyan, blue,
orange, black, magenta, yellow, brown, sienna, grey). No RGB or hex
values ever appear in `.DHQ` files — those live in `ARMONIC.MOD` instead
(see below), a separate default-style table, *not* itself `.DHQ` grammar:
one line per harmonic, `<number> <color-spec> <style>`, e.g.

```
1 (160,160,160) AA:3
8 <350,1.0,0.8> Aa:2
9 <236,0.9,1.0> \Cc:3
```

Harmonic 1 uses a plain `(R,G,B)` triple (gray); every other harmonic uses
a `<hue,saturation,value>`-shaped triple instead (hue in degrees,
saturation/value 0–1) — a mixed grammar within the same file that isn't
explained anywhere, though the numbers are consistent with HSV. This
file's per-harmonic `LES` styles were checked directly against
`CLRDINXX.DHQ`'s: harmonics 1, 8, 9 and 10 match `ARMONIC.MOD` **exactly**
(`AA:3`, `Aa:2`, `\Cc:3`, `AaAaDa:2`); harmonic 7 is close but not
identical (`ARMONIC.MOD` has `/Ac:7`, `CLRDINXX.DHQ` has `/AA:10`). This
is strong (not conclusive) evidence that `ARMONIC.MOD` is the on-disk
default per-harmonic style table ARMON draws from when auto-populating a
new harmogram design, which the user can then hand-edit per band (as
apparently happened for harmonic 7 in `CLRDINXX.DHQ`).

### 4.6 `LES` — Estilo:Grosor (style : weight)

Grammar, confirmed structurally across all 87 distinct values in the
corpus:

```
["\" | "/"]? (token)+ ":" weight
```

- Optional single leading `\` or `/` (no other prefix character observed).
- One or more two-character **tokens**, almost always an uppercase letter
  `A`–`G` followed by a lowercase letter `a`–`f` (`Aa`, `Bc`, `Ea`, …);
  the doubled-uppercase form `AA` is also common and behaves as its own
  token (189/1175 occurrences — the single most common `LES` value is
  `AA:3`). One single lowercase anomaly, `aa:1`, appears once
  (`_0COSMOS.DHQ`) and is presumably a typo for `AA:1`.
- Tokens concatenate directly with no separator: `AaAaDa:2` is the
  3-token sequence `Aa`, `Aa`, `Da`.
- `weight` is a small positive integer (1–16 observed), the line's stroke
  thickness per the section-1 label "Estilo:Grosor" ("style:weight").

**What the tokens themselves encode is not confirmed.** The
letter-pair-repeated shape strongly resembles a dash/gap pattern (e.g. an
old Borland BGI-style custom line pattern, plausible given ARMON's DOS
graphics heritage — see `ARMON.TXT`'s TrueType/BGI-era framing), with the
leading `\`/`/` perhaps selecting a diagonal hatch or double-line variant,
but nothing in the manual or corpus pins down letter-to-dash-length
semantics. Flagged open, §5.7.

### 4.7 `AOH` — Armónico:Orbe (harmonic : orb) — the richest field

`ARMON1.DOC` describes this field's grammar directly (§ "Aspectos y
Diseño de la Rueda") and the corpus corroborates every shape it
describes, plus a few more:

1. **Bare harmonic number**: `"7"` — all aspects derivable from dividing
   the circle into 7 (i.e. the full aspect set `0/7, 1/7, …, 6/7`).
2. **"Own" aspects of a harmonic**, `xN`: aspects of harmonic N that don't
   reduce to a lower harmonic's aspects. Manual's own example: `x8`
   excludes the conjunction (`0/8`, harmonic 1's aspect), the two squares
   (`2/8`, `6/8` — harmonic 4's aspects) and the opposition (`4/8`,
   harmonic 2's), leaving only `1/8, 3/8, 5/8, 7/8` (semi/sesquiquadrate).
3. **Explicit fraction(s)**: `p/q` (e.g. `1/3`, `1/8`), comma-separated
   for multiple (`1/8:27.69231,7/8`).
4. **`:orb` suffix** on any of the above, in **harmonic-circle degrees**,
   not natural-zodiac degrees — the manual is emphatic about this
   distinction: *"1/8:24 quiere decir que se utilizará un orbe de 24° [...]
   en el círculo armónico. Por lo tanto, en grados del Zodiaco natural
   será un orbe de 24/8, es decir, de 3°"* (an orb of 24° in the harmonic
   circle of an octave is 3° of natural zodiac). This resolves why the
   corpus's overwhelmingly dominant orb constant is `27.69231`: it is
   `27.69231 = 360/13`, i.e. an orb chosen so that, however it's further
   divided by the harmonic number, it always lands on a clean natural-orb
   fraction across the harmonic series 1–13 García uses for his default
   "first N harmonics" designs.
5. **Comma-separated harmonic list**: `1,x2,x3,x4,x6` (`2YJUPIT.DHQ`,
   band "Suma" — a composite band summing several harmonics; the file's
   later bands then break the same list out into individual per-aspect
   bands labelled `Conj, Opos, Trigono, Cuad, Sext`, confirming the
   harmonic-number ↔ aspect-name correspondence: 1=conjunction,
   2=opposition, 3=trine, 4=square, 6=sextile).
6. **Weighted-list form**, `(w)n,(w)n`: `(1)3,(-1)4` (`_0LEANDE.DHQ`,
   band 4) and `(0)1` (band 5) — parenthesized signed coefficients ahead
   of a harmonic number. Not explained anywhere; presumably a weighted
   composite for some index/total calculation analogous to the
   coefficient columns `ARMON.TXT`'s "evaluar_archivos" screen describes
   for a *different* CPA/Kepler feature — plausible reuse of the idea,
   not confirmed. Open, §5.8.
7. **Empty value** (`length=0`): the harmonic-1 band convention seen in
   `CLRDINXX.DHQ` and elsewhere — no orb given, presumably a program-side
   default.

The one apparent counter-example, `FES="c:27.69231"` in `RIEMANN.DHQ`
(§2, field 14), reuses shape 4 above (`letter:number`) in a field that
elsewhere is always a plain decimal. Given the file's title ("Orbes de
RIEMANN") is itself an orb-constant experiment, this reads as the author
typing an `AOH`-shaped value into the wrong field by habit rather than a
second grammar for `FES` — but it is worth knowing a parser may encounter
it if it validates `FES` strictly.

### 4.8 `PRE` / `PEM` — Receptores / Emisores (bodies)

Grammar: one or more groups, comma-separated, each of the shape

```
prefix ":" letters
```

**Prefix** — which "moment" the following bodies are taken from. Per
`ARMON1.DOC`: *"las especificaciones R:lhve.. y T:lhve.. [...] hacen
referencia a los planetas Radicales y a los planetos Transitantes"*
(Radical/natal vs. Transiting). The corpus shows a third value, `S:`, and
files that combine several in one prefix cluster:

| Prefix | Meaning |
|---|---|
| `R` | Radix / natal |
| `T` | Transiting |
| `S` | inferred: Secondary-progressed (never independently defined in the manual, but appears alongside R/T exactly where a third "moment" is needed, e.g. `RST:lhvemjsunp` in `_9SUPER.DHQ` = "Super transitos", and `RS:lhvemjsunp,T:hvemjsunp` in `_9SUPER3.DHQ`) |
| a bare digit, e.g. `1` | seen once, `_0PRIMAR.DHQ` ("Harmograma en Primarias") uses `PEM="1:lhvemjsunp"` where every other file uses a letter prefix — likely a technique-specific numeric code for Primary Directions rather than a typo, since it's the file's *only* deviation and the file is specifically about that technique. Not confirmed. |
| lowercase `t` | seen once (`_0SYMBOL.DHQ`, `t:lhvemjsunp`) — likely meant as `T:` (case probably insignificant for this prefix) but not confirmed |

**Letters** — which bodies. The core 10-letter string `lhvemjsunp`
appears in 47+17+… occurrences and was fully decoded by cross-referencing
files whose title names the specific body/pair a band is about:

| Letter | Body | Evidence |
|---|---|---|
| `l` | Moon (Luna) | `ARMON1.DOC` itself, verbatim: *"hay que cambiar T:lhvemjsunp por T:hvemjsunp"* to remove the Moon |
| `h` | Mercury | `0INTMERC.DHQ` ("Interacciones de **Mercurio**") pairs every band's *other* letter (`p,u,s,j,m,t,v`) against a constant `h` |
| `v` | Venus | Spanish initial; consistent everywhere |
| `e` | Sun (Sol) | `_0EM_VEC.DHQ` ("Transitos Ondulatorios para **Sol/Marte**") uses `PEM="T:em"` — directly confirms both `e`=Sun and `m`=Mars together |
| `m` | Mars (Marte) | as above, and Spanish initial |
| `j` | Jupiter (Júpiter) | Spanish initial, consistent everywhere incl. `0INTMERC.DHQ` |
| `s` | Saturn (Saturno) | `0INTMERC.DHQ` band "Saturno" ↔ `T:sh` |
| `u` | Uranus (Urano) | `0INTMERC.DHQ` band "Urano" ↔ `T:uh` |
| `n` | Neptune (Neptuno) | `SUN5080.DHQ` ("Energía vectorial SUN") band 1 `T:sun` decomposes into sub-bands `su, sn, nu` — i.e. the pairwise breakdown of {Saturn, Uranus, Neptune}; note the file's title "SUN" is a coincidental mnemonic (**S**aturn-**U**ranus-**N**eptune), *not* the solar body — a real trap for a naive reader |
| `p` | Pluto (Plutón) | `0INTMERC.DHQ` band "Pluton" ↔ `T:ph` |

Letters `l,h,v,e,m,j,s,u,n,p` are, in that order, exactly the Chaldean
planetary sequence (Moon, Mercury, Venus, Sun, Mars, Jupiter, Saturn) with
the three modern outer planets appended — which is also the fixed order
section-0-style declarations always list them in.

Beyond the core 10, two more lowercase letters and several uppercase
single letters were found, all outside the `lhvemjsunp` string and always
prepended or used standalone:

| Letter | Body/point | Evidence |
|---|---|---|
| `t` (lowercase) | Earth (Tierra) | `0INTMERC.DHQ` band "La Tierra" ↔ `T:th` |
| `a` (lowercase) | Ascendant (inferred) | `_0NODOS.DHQ`, `PRE="R:alhvemjsunp"` — prepended to the standard 10; no direct confirmation of "Ascendente" beyond the letter and position, but no better candidate fits |
| `C` (uppercase) | Ceres | `_CERES.DHQ`/`_CERES1.DHQ`/`_CERES3.DHQ`, bands like `T:CPV`, `T:Cm`, `T:Cj` in a file about Ceres |
| `P` (uppercase) | Pallas | `_PALLAS.DHQ`/`_PALLAS1.DHQ`, bands `T:PV`, `T:Pm`, `T:CP` in a file about Pallas |
| `V` (uppercase) | Vesta | same Ceres/Pallas files, `T:CPV`, `T:PV`, `T:CV` |
| `N` (uppercase) | North Node | `_0NODOS.DHQ`, bands `1-Norte`/`3-Norte` ↔ `T:N` |
| `S` (uppercase) | South Node | `_0NODOS.DHQ`, bands `1-Sur`/`3-Sur` ↔ `T:S` — note this collides in spelling (not in case) with the `S:` *prefix* letter for secondary progressions; the two are disambiguated only by position (before vs. after the `:`) |
| `G` (uppercase) | **unconfirmed** | `_PALLAS1.DHQ`, band "Pallas" ↔ `T:GP` — `P`=Pallas is confirmed elsewhere but `G`'s referent is not; no title or context pins it down. Open, §5.9. |

### 4.9 The stray byte in `_0WAVEF.DHQ`

Band 1 of `_0WAVEF.DHQ` ("Forma de Onda por tránsitos") sets
`PEM="T:\xee"` — a single byte, `0xEE`, that is not an ASCII letter at
all (Latin-1 `î`; CP850 gives a different glyph again). Every other
`PRE`/`PEM` value in the corpus uses only ASCII letters. This is plausibly
a point selected through a symbol picker bound to ARMON's custom `ASTRO`
TrueType font (mentioned in `ARMON.TXT` as required for correct on-screen
rendering) rather than typed — i.e. some extra point (an asteroid, the
Black Moon/Lilith, or similar) whose single-character code is a font
glyph slot rather than a mnemonic letter. Unconfirmed; flagged open,
§5.10. A parser should at minimum not assume `PRE`/`PEM` letters are
always printable ASCII.

### 4.10 `WAV` — Onda (wave/weighting function)

Free-text enum, 16 distinct values observed: `suave` (smooth, the
default — 65 occurrences), `vector` (59), `holo/t`, `holo/a`, `holo/l`,
`holo/E`, `barbault` (the Gouchon/Barbault synastry-strength formula,
confirmed by `RTL="Gouchon/Barbault"` labelling a `WAV="barbault"` band in
`CRR_F10.DHQ`), `energia`, `triangular`/`triangulo` (two spellings),
`miguel` (presumably the author's own custom formula), `gauss`,
`logistica`, `concentracion`, `h/t`, `cuadrada`. No enum is declared
anywhere (section 0/1 only name the field, not its legal values), so this
list should be read as "observed", not "complete" — see §5.2, same caveat
as `MDY`.

---

## 5. Open questions / ambiguities

These are the points this document could not pin down confidently from
the corpus and manual alone. Listed here explicitly rather than resolved
by guessing:

1. **`FCH`'s `$`-variables** (§4.1): `$f` and `$e` are clearly live
   program bindings (date-today, age), but the exact resolution mechanism
   (dialog field reference? macro?) isn't documented anywhere available.
2. **`QBN`'s full semantics** (§4.2): default-1-but-sometimes-a-sequence
   pattern is described, plausible tie to `holo`/`vector` wave functions
   is noted, but not confirmed against source or documentation.
3. **`AOH`'s empty-value default** (§3, §4.7 point 7): when `AOH` is
   omitted or empty, what orb (if any) ARMON assumes is not stated
   anywhere in the corpus or manual.
4. **`RNG`/`NDY` sentinel `-1`** (§4.4): plausible "autoscale" reading for
   `RNG=-1`, but `NDY=-1` in the same record (`7HOLO.DHQ`) has no
   equally plausible explanation.
5. **Full `LES` token semantics** (§4.6): the two-character-token,
   optional-`\`/`/`-prefix *shape* is solid; what the individual letters
   encode (dash length? gap length? line cap?) is not.
6. **`AOH`'s weighted-coefficient form**, `(w)n` (§4.7 point 6): seen
   twice in one file (`_0LEANDE.DHQ`), never explained.
7. **The `G` letter** in `PRE`/`PEM` (§4.8): one occurrence, no
   corroborating title or context.
8. **The `0xEE` byte** in `_0WAVEF.DHQ`'s `PEM` (§4.9): almost certainly a
   font-glyph-coded extra point, not identified further.
9. **`MDY` and `WAV`'s full enumerations** (§4.10 and §2 idx 11): the
   corpus shows only one `MDY` value (`picos`) ever, across all 130
   occurrences, despite the field having its own label ("Forma") implying
   alternatives exist. `WAV` shows 16 values but nothing declares the set
   closed. A parser should treat both as open string fields, not validate
   against an enum.
10. **Numeric vs. string typing generally**: nothing in the format
    declares a field's type; every value is a length-prefixed string, and
    fields that are "usually numeric" (`NDY`, `NDP`, `FES`, `RNG`) each
    have at least one outlier that isn't a clean number (§4.4, §4.7's
    `RIEMANN.DHQ` `FES` note). A permissive parser should keep every
    value as a string and let the caller coerce per-field as needed,
    rather than assuming strict numeric types.

---

## 6. Verification

The grammar in §1.2 was checked byte-for-byte against all 129 corpus
files with a throwaway script (not committed — see the task notes) that
sliced every line by fixed column and confirmed `len(value) ==
declared_length` with zero exceptions, zero decode errors, and the
section/field-index structure described in §1.3 holding for every file.
The field-code table in §2 (section 0 declares the same 16 codes, same
order, same section-1 labels, in all 129 files) was likewise checked
programmatically, not sampled. Three files not used in the worked example
above — `01SEC.DHQ`, `_CERES.DHQ`, `_PALLAS1.DHQ` — were read in full by
hand during this investigation (they appear as evidence throughout §4)
and parse without contradicting anything stated here.

This is a documentation deliverable, not a parser or a numerically
verified engine change: `openastromod/harmogram.py` and
`openastromod/harmonicvector.py` are untouched by this work.
