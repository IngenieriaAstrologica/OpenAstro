# OpenAstro Changelog

Entries without a date come from the 2026-08-26 session.

## Change: the harmogram's twelve curves, made legible — 2026-09-21

### Change
One line weight for all twelve harmonics, and a palette picked for
perceptual distance rather than for even hue steps.

### Why the first palette failed
It spaced twelve hues 30° apart. That divides the *hue circle* evenly,
which is not the same as dividing *perception* evenly: the eye separates
greens from each other far worse than it separates red from blue, and
CIELAB hue angle is at its least uniform in exactly the green-to-blue
band. Four of the twelve landed in green/teal/cyan and read as one
colour.

Measuring it turned up a second cause that had nothing to do with
spacing: **six of the twelve were below WCAG contrast 3.0 on white**, the
palest at 1.73. Half the palette was washing out against the paper.

### How they are chosen now
Glasbey's method — walk the sRGB grid and repeatedly take the colour
whose CIEDE2000 distance to every colour already taken is largest,
seeding the set with the white paper and the black ink so no curve can be
confused with the background or the text — followed by a local-search
pass that optimises the minimum pairwise distance directly instead of
approximating it one greedy step at a time.

Three constraints, each earning its place:

| constraint | what it buys |
|---|---|
| `C* >= 55` | vivid. Muted fills are exactly what a pure distance objective reaches for. |
| `L* <= 61` | visible on white — this is WCAG contrast 3.0 to the point. |
| `hue >= 18°` | walks the whole circle. |

The hue floor is the least obvious and the most necessary. Maximising
distance alone piles colours into the magenta and purple region, where
chroma is largest and so distances are too: the unconstrained run scored
well and looked repetitive, four purples with no cyan and no yellow
anywhere.

| | before | after |
|---|---|---|
| minimum CIEDE2000, any two curves | 17.6 | 18.3 |
| between consecutive harmonics | — | 47.2 |
| minimum hue separation | 5° | 19° |
| chroma, mean | 58 | 66 |
| WCAG contrast on white, minimum | 1.73 | 3.09 |
| curves below contrast 3.0 | 6 of 12 | 0 of 12 |

### The line weights are gone
They came from ARMON's `LES` field and were drawn at one third scale,
putting the curves between 0.67 and 3.33px. The range hurt more than it
helped: the thin harmonics could not be followed at all and the thick
ones buried whatever they crossed. All twelve now draw at 1.5px and the
work of telling them apart goes to colour and dash.

### What this costs
Stated plainly, because it is a real loss: the dichromatic floor the
intermediate palette carried is gone, deuteranopia 8.1 → 3.6. Vivid,
white-legible and hue-spread cannot all hold together with it — the
search runs out of candidates at the tenth colour, which is a fact about
the sRGB gamut and not a tuning failure. The dash patterns are what
carries that case now.

An earlier attempt to make dichromacy the *objective* rather than a floor
was worse than useless: it dropped the normal-vision minimum to 12.3,
below the palette being replaced, so it would have made the reported
problem worse while appearing to address a different one.

### A bug in the generator, worth recording
When the constraints were mutually infeasible the script quietly relaxed
them and returned a palette that violated what had been asked for *while
looking like it complied*. It fed one wrong measurement before being
caught. It now aborts and names the step at which it ran out of
candidates. Any search under constraints wants this: silent fallback is
worse than failure, because the caller cannot tell the difference.

## Feature: the harmogram and the Harmonic Flower, drawn — 2026-09-21

### Change
Two new Tables entries. `Tables -> Harmogram` asks a centre date, a window
in days and which of the two readings to take; `Tables -> Harmonic Flower`
asks nothing, since the flower is a property of the open chart.

### The layout is García's, not invented
ARMON's plot templates — the `.DHQ` files — turned out to describe their
own drawings, and two fields settled decisions that were about to be
guesswork:

- **`QBN` is 1 in all twelve bands of `_0MES.DHQ`.** García overlays the
  twelve curves in a single box and tells them apart by colour, dash and
  weight; he does not stack them. The overlay is reproduced, and its line
  weights are read straight off the `LES` field. Overlaid curves answer
  "which harmonic is loudest here" and are hopeless for following one, so
  the same curves are repeated below as twelve lanes over their own ranges.
- **`RNG` is 15.** The vertical scale is fixed, not fitted to the data —
  two harmograms are only comparable if the axis does not move under them.

`_0MES.DHQ` also reads `PRE = R:lhvemjsunp` against `PEM = T:lhvemjsunp`,
i.e. ten radix receivers against ten transiting emitters: that template is
harmonic transits, and the ten letters are Luna, Helios, Venus, Mercurio,
Marte, Júpiter, Saturno, Urano, Neptuno, Plutón in speed order.

### The scale figure checks out independently
`RNG = 15` is only sensible if the intensity function produces numbers of
that size, so this is a test of the engine written earlier. The Gaussian
weighting has an expected value of 0.0776 per random pair, which for the
template's 100 pairs predicts a mean of 7.76. Measured across a year of
real transits, sampled every six hours: **7.97**, with 99.74% of samples
below 15. García's plot range and this engine's magnitudes agree to a few
percent, which neither was fitted to do.

The natal reading needed its own figure. Its 45 pairs are the same ten
bodies read against themselves, which includes the slow pairs that stay
locked together for years, so the distribution is far more skewed: over
the same year the mean is 3.70 but the 99th percentile is 9.85. Scaling
the transit ratio down by pair count would put the ceiling at 6.75 and
widen on most dates, so that one is set from the measurement. A plot
widens past its standard rather than clip a peak, and says so when it does.

### The flower needed a reference circle
The concentration index runs to 1, but ten bodies dropped at random
already average 0.28, and one chart in twenty reaches 0.55 by chance
alone. Without marks at those radii half the dial is permanently empty and
every petal looks small. Both figures come out of the same Rayleigh
distribution the coefficient obeys — the modulus of a walk of n unit steps
in uniformly random directions — and they live in the engine as
`chance_level()` and `significance_level()` rather than in the drawing.

Checked against 200,000 random charts:

| bodies | predicted | measured |
|--------|-----------|----------|
| 6      | 0.3618    | 0.3661   |
| 10     | 0.2802    | 0.2818   |
| 14     | 0.2368    | 0.2385   |

### Verification
Both drawings were rasterised from the real SVG before being committed,
not reasoned about: the harmogram for the natal and transit readings and
for 2-, 16- and 60-day windows, the flower for two charts. Four things the
first render caught — a title duplicated from the template, axis dates
printed over the legend heading, a hardwired grid step that labelled only
0 and 5 on a scale of 8, and lanes flattened into straight lines by
sharing the overlay's scale.

The flower has a sanity check that does not depend on my own arithmetic:
**2020-12-21**, the day of the Jupiter–Saturn great conjunction, comes out
with harmonic 1 dominant at 0.679 and past the one-in-twenty level.

### Still open
Astrodines remain the intensity function itself rather than a third
drawing, as the previous entry records. García reports testing "a
thousand" variants of it; this one is the canonical Gaussian, parametrised
by `WEIGHT_AT_ORB` so that changing one number moves the whole weighting.

## Feature: Harmonic Vector and Harmonic Flower engine — 2026-09-21

### Change
`openastromod/harmonicvector.py`. With the harmogram engine added earlier
this completes the calculation side of Miguel García's harmonic suite;
the drawings come next.

### Read from the primary source
The three techniques are defined in García's own *Suite Armónica* (1997),
and the definitions settle what had been guesswork:

- **Harmonic Vector** — "the Fourier spectrum of the sum of a Dirac delta
  per planet". Each harmonic gets an amplitude and a phase:
  `C(h) = Σ exp(i·h·λ)`. Boudineau's *Resultante Planetaria* is the same
  thing at h=1.
- **Harmonic Flower** — the concentration index per harmonic, `|C(h)|/n`,
  drawn as petals. It answers a different question from a harmogram,
  which is why the dominant harmonic often differs between the two: the
  flower measures how tightly a chart gathers, the harmogram counts
  conjunctions.
- **Astrodines** — *not a third drawing*. García: "a function that
  assigns a force value, some astrodines, to each point of the circle
  representing the angular separation between two planets". They are the
  aspect intensity function itself — the weighting the harmogram engine
  already carries as a parameter. He reports testing "a thousand"
  variants of it over several years.

One more thing falls out: García notes that "Gouchon and Barbault's
**cyclic index** is an example of using the harmogram of harmonic one
[inverted] from Jupiter to Pluto". The curve added two entries ago is a
special case of this machinery.

### Verification
The mathematics is checked at the points where the answer is forced.
Eight conjunct planets give a concentration of exactly 1 in every
harmonic; eight spread evenly give 0 in harmonic 1 and 1 in harmonic 8,
where they meet again. An exact opposition cancels in harmonic 1 and
concentrates in 2; a grand trine cancels in 1 and 2 and concentrates in 3.
A conjunction's phase points at the conjunction. Across 2,000 random
charts the index never left [0, 1].

### Files changed
- `openastromod/harmonicvector.py` — new engine module

## Feature: harmogram engine — 2026-09-21

### Change
`openastromod/harmogram.py`, the calculation behind the harmograms of Mike
O'Neill and Miguel García Ferrández: the strength of each of the first
twelve harmonics, traced as a curve over time. The engine only; the plot
comes next.

### The technique, and where it was read from
A harmonic chart of order N multiplies every longitude by N, which turns
that harmonic's aspect family into conjunctions. "How strong is harmonic N"
therefore becomes "how many conjunctions does the Nth harmonic chart hold",
and that is a number one can plot.

Two readings, and the `.DHQ` templates that ship with ARMON name both:

- **Harmonic transits** — the moving sky against a fixed radix. The
  templates mark it `R:` (receivers, natal) against `T:` (emitters,
  transiting).
- **Natal harmogram** — the sky against itself, both sets `T:`. García
  introduced it because harmonic transits misbehave near the birth moment:
  every planet is then conjunct its own radical place in *all* the low
  harmonics, and the curves spike.

**The orb is 360/13 = 27.69231°**, the literal constant in the templates.
García's own reasoning, per the source: it is the widest orb a conjunction
can take before reaching into the semisextile's territory at 360/12. Not
empirical — a mathematical argument.

Conjunctions are counted "weighted by a Gaussian orb". The sources say that
and no more, giving no constant, so the weighting is parametrised rather
than guessed: `WEIGHT_AT_ORB` states what a conjunction exactly on the
boundary is worth and the Gaussian width follows from it.

### Verification
The source gives numbers, and they are reproduced. With O'Neill's 12° orb
the article states the transiting Sun stays conjunct its radical place
"about twelve days in harmonic 1, six in harmonic 2, four in harmonic 3":

| Harmonic | Published | Computed |
|----------|-----------|----------|
| 1 | ~12 days | **12.3** |
| 2 | ~6 days | **6.1** |
| 3 | ~4 days | **4.1** |

With García's orb the same scaling holds exactly — 28.5, 14.2, 9.4 days,
which is 1, 1/2 and 1/3 of the first.

The engine also reproduces the artefact that motivated the natal variant:
at the birth moment harmonic transits reach 17.55 where the natal
harmogram reads 3.78, the spike being precisely what reading the sky
against itself removes.

Plus the mechanics: an opposition is a conjunction in harmonic 2, a square
in harmonic 4, a trine in harmonic 3 and not in 4; the weight is 1 when
exact, `WEIGHT_AT_ORB` at the boundary, 0 beyond, and monotonic between; a
16-day window at 36 parts a day gives 577 samples centred on the date.

### Files changed
- `openastromod/harmogram.py` — new engine module
- `openastromod/swiss.py` — `longitudes_at()`, a thin call for dense sampling

## Fix: GTK 2 constants, and dialogs now open on today — 2026-09-21

### Error dialogs raised instead of showing
`Gtk.MESSAGE_ERROR`, `Gtk.BUTTONS_CLOSE` and a mistyped `Gtk.ButtonS_CLOSE`
survived the GTK 3 port. **None of the three exists in GTK 3**, checked
against the live library, so each would raise `AttributeError` at the
moment it was asked to report a problem — the Monthly Timeline's two
validation messages and the print-failure dialog. They are now
`Gtk.MessageType.ERROR` and `Gtk.ButtonsType.CLOSE`. Five uses across
three call sites; none remain.

### Dialogs open on the current date and time
Transits, Lunar Return, Primary Directions and Atacir reopened on
whatever date was last used, which is rarely the one wanted — the common
case is *now*. All six date-taking dialogs now open on the current moment.
Solar Return and Secondary Progressions already did.

The distinction that matters: **dates reset, technique settings do not.**
Cycle, time key, measure and direct/converse are still remembered, because
those express how someone works rather than what they are looking at
today. The date fields no longer write to `astrocfg` either, since nothing
reads them back, and one `last()` helper left with no callers went with
them.

### Verification
Every one of the six dialogs checked programmatically: none reads a date
from `astrocfg`, all six seed from the current moment, and no date field
is written back. The nine technique settings that should persist still do.

### Files changed
- `openastro` — the three message dialogs, date seeding in `specialTransit`,
  `specialLunar`, `specialDirected` and `specialAtacir`

## Feature: import Kepler/CPA natal files — 2026-09-21

### Change
Charts can be imported from Kepler/CPA `.DAT` files, joining the skylendar,
oroboros, astrolog32 and Zet8 importers. Astrolog32 already claims the
`.dat` extension, so the two are told apart **by content**, not by name.

### How it works
The format is plain ISO-8859 text, one record per line, fields marked by a
backslash tag: `\S>` the natal moment, `\A>` a second chart, `\N>` the
name, `\L>` the place, `\D>` notes. Coordinates are decimal degrees.

**The zone field is the correction to add to clock time to reach UT — the
negated UTC offset.** Spain on CET is stored as `-1.00`. It is negated on
import so the value reads like every other importer's.

That sign was the one real unknown in the format, and it is settled by
evidence rather than assumption: across the whole corpus the derived
offsets track longitude, which they could only do with the sign this way
round.

| Derived offset | Records | Mean longitude | Expected |
|----------------|---------|----------------|----------|
| −5 | 195 | −76.9 | −75 (US Eastern) |
| −6 | 129 | −88.1 | −90 (US Central) |
| −8 | 55 | −119.3 | −120 (US Pacific) |

**8 of 8** of the commonest offsets agree with their longitude; with the
sign inverted only 3 of 8 would.

### Verification
Run over a corpus of 40 files: **40 read without an exception, 8,196
records parsed**, every derived offset inside the valid −12..+14 range,
none out of bounds. Malformed lines, missing fields and empty files are
skipped rather than propagated.

### Fix carried along
`importZet8()` declared **17 columns and supplied 16 values** — `null`
plus fifteen placeholders against a sixteen-value tuple, with
`countrycode` missing. Any Zet8 import raised `OperationalError` and had
done since the importer was written. Found because the Kepler importer
walks the same path; fixed there.

### Files changed
- `openastromod/importfile.py` — `getKepler()` and its helpers
- `openastro` — import menu entry, `importZet8()` column fix
## Feature: Cyclic Index — 2026-09-21

### Change
New **Tables → Cyclic Index**: the Gouchon/Barbault curve, mundane
astrology's single number for a date. For every sampled date the ten
angular separations among Jupiter, Saturn, Uranus, Neptune and Pluto are
summed; low values mean the slow planets are gathered, high values that
they are spread. Drawn as a plotted curve over a century, split into
25-year panels, with a table of turning points naming the closest and
widest pair at each.

### How it works
`openastromod/cyclic.py` for the geometry, plus a deliberately thin
`swiss.cyclic_longitudes()` that fetches only the five longitudes — the
curve samples hundreds of dates, and `ephData` would build a whole chart
for each.

**Heliocentric by default, and that is a choice.** Seen from the Sun the
curve moves only as the planets actually move; seen from the Earth every
outer planet retrogrades once a year and the sum picks up an annual ripple
that is an artefact of where the observer stands. The geocentric variant
remains available.

### Verification
Three claims were checked independently of the implementation.

**The ceiling is 1080, not 1800.** Ten pairs at 180° would give 1800, but
five points on a circle cannot all be in opposition at once. A hill-climb
from 4,000 random starts never exceeded **1080.0000**, and the mean over a
uniform spread came to 901 against the predicted 900.

**That ceiling is a plateau, not a peak** — a finding that changes how the
curve is read. Perturbing any planet in the January 2003 configuration by
one or five degrees left the sum at exactly 1080 in **18 of 20** cases. So
a reading of "100% of maximum" is saturation, the tops of the curve are
genuinely flat, and it is the *minima* that carry the information.

**The curve lands where the tradition says it should.** Computed from
scratch with a separate script: 1983-06 gives 306.4 (28% of maximum, the
minimum Barbault built his reputation on), 1943-08 gives 562.3, 2022-06
gives 500.7, and 2003-01 sits on the plateau at 1080.0.

### Files changed
- `openastromod/cyclic.py` — new engine module
- `openastromod/swiss.py` — `cyclic_longitudes()`, a thin ephemeris call
- `openastro` — `tableCyclicIndex`, Tables menu entry, print dispatch
## Feature: transit date and converse transits — 2026-09-20

### Change
The transit dialog now asks **when**. It used to ask only for the measure and
always draw the present moment; it takes year, month, day, hour and minute
— with a **Now** button that puts the current moment back in one click, so
the old behaviour is still a click away — and a **Direction** selector:

- **Direct**: the sky of the requested moment, as before.
- **Converse**: that moment mirrored about the birth instant, i.e. the
  heavens running backwards from the nativity.

Every field is remembered in `astrocfg` (`transit_Y/M/D/h/m`, `transit_dir`,
alongside the `transit_measure` already stored), so reopening the dialog
returns the last request. Bad input is refused with a message and the dialog
stays open with the values still in it.

This closes the roadmap's §7 and §8, which are one dialog and were done as one
change.

### How it works
`openastromod/transit.py` — new, stdlib only (`datetime` + `zoneinfo`), no
ephemerides, so it cannot drift against the Swiss Ephemeris. It answers the
only question a transit poses, which is *which instant*: the outer wheel
itself is a plain ephemeris reading. `moment()` turns the dialog's wall-clock
time into the UT instant to draw, plus that instant's own UTC offset (so a
converse moment landing in another DST season — or before the zone had DST at
all — reports its own offset, not the requested date's).

**Why converse is a mirror of the instant.** Primary directions and atacires
both run on an arc that is *linear* in the time elapsed since birth (Naibod
0.9856°/year, atacir C-N 360/N °/year), and there "converse" means negating
the arc — which, because the arc is linear in elapsed time, is the very same
statement as negating the elapsed time. A transit has no arc to negate: its
positions are whatever the ephemeris says, a nonlinear function of the
instant. What generalises is the parameter, not the formula — the signed
displacement from birth:

    t_sky = t_birth - (t_requested - t_birth)

So the birth instant is the fixed point (at zero displacement both directions
give the natal sky), and it is the exact midpoint of the direct and converse
moments. Only the instant is mirrored, never the place: the converse sky is
still read from where the chart is cast. The mirrored instant is rounded to
the whole second, because the chart stores its hour as decimal hours built
from h/m/s and the birth hour is a decimal that would otherwise lose most of
a second to truncation.

In `openastro`, the new `openAstroInstance.localToTransit()` replaces the
date arithmetic that was inlined in the dialog's submit handler, following
`localToDirected()` / `localToAtacir()`: the radix stays in `self.*` and the
transit moment goes into `self.t_*` as the outer wheel. Called with no
argument it still draws right now, so nothing else in the program had to
change. Both existing measures (ecliptic and ascensional mundo contacts) work
in either direction.

### Verification
Example chart 1987-04-09 12:00:30 UT, lon 2.0367, lat 41.3436 (natal Sun
19°Ari06'34", Moon 24°Leo07'13"). Everything below ran under WSL with real
Swiss Ephemeris; the two UI checks exec the **method bodies lifted from the
`openastro` script itself**, so what was tested is the shipped code, not a
copy of it.

The requested date really is the date drawn: local 2026-09-20 12:00 at the
chart place resolves to 10:00 UT (offset +2, CEST) and the wheel gets Sun
27°Vir28'16", Moon 14°Cap23'31", Saturn 12°Ari23'27" — the Sun advances
0.9772° over the following day, and the same clock time a year earlier is
0.2°+ away, so the positions belong to that date and no other. A winter
request (2026-01-15 09:30 local) resolves at offset +1, CET.

The converse is symmetric about birth, and to the tenth of a millisecond:
the requested moment sits +14408.916319 days from the nativity and the
converse moment −14408.916319, landing on 1947-10-27 14:01 UT, where the
wheel gets Sun 3°Sco18'21", Moon 5°Ari37'58", Saturn 21°Leo22'36". All ten
bodies match an independently mirrored instant to 1e-9°. At zero displacement
both directions return the natal sky; mirroring twice returns the original
moment; and a birth hour carrying a fractional second still yields
whole-second moments with a symmetry error of 0.

The dialog, driven headless under Xvfb: first use offers today with
Direct/Ecliptic; **Now** refills the fields; a request of 1999-12-31 23:45
converse ascensional reaches `localToTransit()` with exactly those arguments
and is stored in `astrocfg`; reopening returns all seven remembered values.
Refused without reaching the engine — month 13, day 32, hour 25, minute 99,
an empty year, letters, year 999, and 1999-02-29 — while 2000-02-29 is
accepted, as a leap year should be.

Also checked: `primary.transit_oa_pair()` still gets what it needs from the
new moment (ascensional measure untouched), the direct chart's title string
is byte-identical to the old one, and no dialog method calls an
`openAstroInstance` method through `self` (the cross-class trap).

### Files changed
- `openastromod/transit.py` — new: the transit instant, direct and converse
- `openastro` — `localToTransit()`, date/time and direction fields plus
  validation in `specialTransit` / `specialTransitSubmit`

## Feature: pick the day for a Lunar Return — 2026-09-20

### Change
The Lunar Return dialog takes a **day** as well as a year and month, and
returns the lunar return **nearest that date**. It used to ask only for
the month and always seed the search at the 15th, which gave the return
nearest mid-month whether or not that was the one wanted.

### How it works
Barely a change, because the search was already right: the correction it
applies is normalised to (-180, 180], so it always takes the shorter way
round and lands on the return nearest its seed. Only the seed moved, from
the 15th to the day asked for. `day` defaults to `None`, which keeps the
old mid-month behaviour for any caller that does not pass one.

A day the month does not have is clamped rather than raising, and the
dialog now rejects bad input instead of letting the exception surface
behind the window.

### Verification
Seeded at seven days across September 2026 against a real chart. The Moon
comes back to its natal degree within **0.5 arcseconds** every time, and
the nearest-return behaviour holds where it matters — the boundary:

| Day asked | Return found | Distance |
|-----------|--------------|----------|
| 20 | 2026-09-09 | 11.10 d |
| 25 | 2026-10-06 | 11.19 d |

Those two returns are 27.3 days apart, so day 20 is nearer the September
one (11.1 vs 16.2) and day 25 nearer the October one. The search switches
where it should. No seed landed further than 11.19 days from its return,
inside the half-month maximum.

### Files changed
- `openastro` — `localToLunar` seed day, day field and validation in
  `specialLunar`/`specialLunarSubmit`

## Feature: Profections table — 2026-09-20

### Change
New **Tables → Profections**: ninety-one years, each with the sign the
Ascendant has profected to, the house it puts first, the lord of that sign
and where that lord stands natally. The year being lived now is shaded, so
the table answers "who rules this year" at a glance. It paginates.

### How it works
`openastromod/profections.py` computes nothing astronomical. Profecting
*is* the atacir of cycle 12 seen another way: that atacir turns the chart
30° a year, which is exactly one sign, so at each birthday the Ascendant
has stepped on and the first house with it. The module only names what the
rotation lands on — which is the payoff of having built the generic engine
first, since profections cost a lookup table rather than a second
implementation.

The domicile table is imported from `arabicparts` rather than copied, so
the lots and the time lords can never disagree about who rules a sign.

### Verification
The load-bearing check: for each of the first forty years, the sign this
module reports is compared against the Ascendant **actually rotated by the
atacir C-12 arc** for that age — **zero discrepancies**. The two are the
same technique, and now demonstrably so.

Also: the sign advances exactly one per year and returns to the natal sign
at 12 and at 84; ages 0, 11 and 12 give houses 1, 12 and 1; every lord
matches the shared domicile table; the years chain with no gaps, each
opening on the birthday; a 29 February birth does not raise; and
`current_age` handles the day before a birthday and dates before birth.

Rendered outside GTK before committing: 91 rows over 2 pages, headers
repeated, page break clean.

### Files changed
- `openastromod/profections.py` — new engine module
- `openastro` — `tableProfections`, Tables menu entry, print dispatch

## Feature: solar-arc directions — 2026-09-20

### Change
The Atacir dialog gains a **Rate** selector: the constant 360/N of a cycle,
or the **solar arc** taken from the progressed Sun. Both turn the chart
rigidly; only the source of the arc differs, so this is one more reading of
the engine already there rather than a second chart type. The cycle field
greys out when the Sun supplies the arc, because it then means nothing.

With this, the roadmap's §2 is covered: the 1°-a-year symbolic directions
*are* the atacir C-360, already available, and the solar arc is what was
missing.

### How it works
`primary.solar_arc_lon()`, alongside the existing `solar_arc_ra()`. One
ephemeris day per year of life, and the arc is the progressed Sun's travel
in **ecliptic longitude** — where the older function measures the same
travel in right ascension for the primary directions. Signed, so a
converse chart just passes a negative age.

### Verification
Measured on a real chart: 0° at birth, 0.9819°/year at one year, 0.9745 at
thirty, 0.9698 at fifty — the slow drift of the real Sun, bracketing
Naibod's constant 0.98565 within 0.011. Monotonic to a hundred years,
negative for converse.

The two arcs it must not be confused with, both checked to differ: the
right-ascension arc gives 28.2486° where longitude gives 29.2336° at the
same age, and the C-360 cycle gives exactly 30.0000° because it is a
constant, not an ephemeris.

### Files changed
- `openastromod/primary.py` — `solar_arc_lon()`
- `openastro` — `localToAtacir` key, Rate selector in `specialAtacir`

## Feature: Arabic Parts table — 2026-09-20

### Change
New **Tables → Arabic Parts**: sixteen lots with their position, the house
they fall in, and the formula as resolved for the chart's sect. Lots that
reverse at night are marked, so the table shows what was actually computed
rather than a textbook formula that may not apply.

This extends what the chart already had — Fortune, Spirit, marriage and
Infortune as fixed entries in `swiss.py` — into a catalogue.

### How it works
`openastromod/arabicparts.py`. Every lot has the same shape, `A + B - C`,
with B and C trading places for a nocturnal nativity. Terms name one of
four things, so a formula can reach anything in the chart:

    ('cusp', n)     the n-th house cusp
    ('planet', i)   a body, by OpenAstro's index
    ('lot', name)   a lot computed earlier, so lots build on lots
    ('lord', n)     the domicile ruler of the sign on the n-th cusp

The domicile table is Morinus' `doms`, and its implied planet order — Sun,
Moon, Mercury, Venus, Mars, Jupiter, Saturn — turns out to be exactly
OpenAstro's indices 0-6, verified sign by sign, so no translation layer is
needed. The catalogue is ordered so Fortune and Spirit are resolved before
the lots measured from them, and a formula that cannot be resolved is
skipped rather than silently placed at 0°.

### Verification
Fortune and Spirit match the values `swiss.py` already computes at indices
27 and 28 **to the last digit, in both a diurnal and a nocturnal chart** —
the new engine agrees with the code in production. Also checked: the two
are mirror images about the Ascendant, the night reversal swaps them
exactly, `lord(n)` resolves through the domicile table, and an unresolvable
formula drops out instead of defaulting.

Rendered outside GTK against the real template before committing: 16 rows,
514px, everything inside its box.

### Not included
Lots whose formula circulates in more than one version depending on the
source. Including them would mean picking a side silently; the catalogue
holds only what is attested without variants.

### Files changed
- `openastromod/arabicparts.py` — new engine module
- `openastro` — `tableArabicParts`, Tables menu entry, print dispatch

## Feature: Midpoints table — 2026-09-20

### Change
New **Tables → Midpoints**: every pair of visible bodies, its midpoint,
and the bodies sitting on it. Pairs nobody occupies are left out — a
midpoint with nothing on it says nothing — and the rest are sorted by
tightest contact. Orb defaults to 1.5° and can be set through
`midpoints_orb` in `astrocfg`.

### How it works
`openastromod/midpoints.py`, pure geometry. The midpoint is the near one,
inside the shorter of the two arcs joining the bodies, as Morinus computes
it.

Contacts are tested in the **90-degree dial**: reducing every longitude
modulo 90 collapses conjunction, square and opposition onto one point, so a
single proximity test finds all three — which is the whole reason the dial
exists, since those three angles all put a body on the midpoint's axis. The
dial wraps, so 89° and 1° are two degrees apart, not eighty-eight.

A pair's own members are excluded from its contacts: a body is trivially on
the axis of any midpoint it helps define.

### Verification
The midpoint matches a literal transcription of Morinus' `countMidPoints`
over a 14,400-point grid plus 3,000 random pairs — **worst difference
0.0**. Geometric properties checked independently on 5,000 random pairs:
the midpoint is equidistant from both bodies and lies in the shorter arc.
The dial registers 0°, 90°, 180° and 270° as contacts and rejects a trine.

Simulated on a real chart (13 bodies, 78 pairs): 22 activated pairs at the
default orb, 554px of table, and 43 even at orb 3° — all within the page.

### Not included
Morinus' second method, the midpoint **with latitude** after Ruediger
Plantiko — the true midpoint of the great circle joining the bodies rather
than of their ecliptic projections. It is a different quantity rather than
a refinement, and nothing else in OpenAstro works in that space.

### Files changed
- `openastromod/midpoints.py` — new engine module
- `openastro` — `tableMidpoints`, Tables menu entry, print dispatch

## Fix: Monthly Timeline gains Save as CSV — 2026-09-19

The Timeline window had Print and Save as PDF only. A **Save as CSV**
button now exports the same table: `Transit, Aspect, Natal` plus one
column per day (`01`…), cells holding the orb to two decimals with an `R`
suffix when the transiting planet is retrograde that day. Rows keep the
Chaldean display order; the default filename is
`timeline-YYYY-MM-<name>.csv`.

Transit/Natal use UTF-8 glyphs (☉ ☽ ☿ ♀ ♂ ♃ ♄ ♅ ♆ ♇ ☊ ☋ ⚸ ⊕ ⚷ ⚳ ⚴ ⚵
⚶), angles/lots/minor points their short label; aspects use ☌ ⚺ ∠ ⚹ Q □
△ ⚼ bQ ⚻ ☍. The file is written with BOM (`utf-8-sig`) so Excel detects
the encoding directly.

**Node glyphs are real node symbols.** The first build mapped `mean node`
/ `true node` to U+264A and `south node` to U+264B, which are the zodiac
signs Gemini and Cancer (♊ ♋), so those rows showed the wrong symbol.
They now use ☊ (U+260A) and ☋ (U+260B) like the rest of the column.

### Files changed
- `openastro` — `tableMonthlyTimelineCSV`, stored table in `tableMonthlyTimelineShow`

## Fix: quincunx yellow unreadable, Asc/Mc not black — 2026-09-19

**Quincunx (150°) is no longer yellow.** `#fff600` on white measures
1.14:1 contrast, so its line, glyph and Timeline cells were invisible. It
is now a dark teal `#00796b` (5.32:1, WCAG AA), distinct from quintile
blue, trine green and the browns. **Asc and Mc draw in black**: Asc was
orange (`orange` / `#ff7e00`, 2.55:1) and Mc red (`#FF0000`).

Changed in the three places that carry these inks — `color_codes`
defaults (what drawing and Settings → Colors use), `settings_aspect` /
`settings_planet` defaults — plus a conditional migration at startup that
updates only rows still holding the old defaults, so user customizations
survive. Dsc stays blue, Ic was already black.

### Files changed
- `openastro` — `defaultColors`, `value_settings_planet`, `settings_aspect` defaults, startup migration

## Fix: Monthly Timeline ignored Settings -> Aspects — 2026-09-19

**Monthly Timeline only showed major aspects with a fixed ±4° orb.**
`tableMonthlyTimelineShow` filtered on `is_major == 1` (conjunction,
sextile, square, trine, opposition) and hardcoded `orb_before = orb_after
= 4`, so anything ticked in Settings -> Aspects outside those five —
quintile, biquintile, quincunx, etc. — never appeared, and the per-aspect
orb column was ignored. The opacity shading also divided by the same
hardcoded 4.

Now the loop skips an aspect only when both `visible` (in Circle) and
`visible_grid` are 0, and the detection window plus the shading use
`float(aspects[z]['orb'])` with a 4° fallback and a guard for orb <= 0.
Deselected aspects stay hidden; selected minors appear with their
configured orb (e.g. trine at 126.5° now shows with orb 8, quincunx at
153.5° stays hidden with orb 3).

**Rows are now sorted in Chaldean order, slowest first.** The old key
sorted by natal index, so the Moon opened the table. The sort key is now
`(rank(transit), rank(natal), aspect)`, with Pluto, Neptune, Uranus,
Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon first and any remaining
points (nodes, asteroids, angles, lots) keeping their relative order
afterwards.

**The month came out short with western timezones.** The day count was
`(enddate - startdate).days` computed from datetimes already shifted to
UTC, so the truncation dropped a day (September showed 29, February 27,
December 30) and past +12 the start fell in the previous month and the
table broke entirely. The title even used the shifted date and could name
the wrong month. Days now come from `calendar.monthrange(y, m)`, each
column samples its own day at local noon, and the title uses the plain
`datetime(y, m, 1)`.

**Invalid month/year in the dialog now show an error instead of crashing.**
The entry fields are validated on OK: month must be 1–12, year 1000–9999;
otherwise a message dialog appears and the table is not generated.

**Removed the PyGTK `buttons=` deprecation warning.** All seven
`Gtk.FileChooserDialog` calls (PDF/SQL export, DB import, XML import,
chart export/import, PDF print, Timeline PDF and CSV) passed their buttons
as the deprecated `buttons=` constructor argument. They now use
`add_buttons()`.

### Files changed
- `openastro` — `tableMonthlyTimelineShow`, aspect filter + orb + shading + Chaldean sort

## Feature: Firdaria table — 2026-09-19

### Change
New **Tables → Firdaria**: the 75-year Persian chain of time lords, one row
per period with its ruler, span, length and its seven sub-periods. The sect
picks the order without asking — diurnal charts open with the Sun,
nocturnal ones with the Moon — using the same test `swiss.py` already
applies to the lots (`(sun - asc) % 360 >= 180`). The table prints and
saves to PDF like the other tables.

All three traditional orders are implemented. Nocturnal charts follow
Al-Biruni by default; `firdaria_bonatti` in `astrocfg` switches to
Bonatti's, which moves the nodes mid-chain, before the Sun, instead of
closing it.

### How it works
`openastromod/firdaria.py`, pure calendar arithmetic with no ephemerides,
so nothing here can drift. Each non-node period divides into seven equal
sub-periods whose rulers walk the same chain from the period's own lord,
skipping the nodes — and Bonatti's order resumes at the Sun rather than
wrapping to the start, which is why the node positions are read from the
chain itself instead of being hardcoded.

### Verification
Morinus' algorithm was transcribed literally and run alongside this one
over four birth dates × the three orders, compared period by period *and*
sub-period by sub-period: **zero discrepancies**. All three chains sum to
75 years, the nodes never receive sub-periods, and the ruler-to-planet
mapping was checked against the real name list for all nine rulers.

One deliberate departure: a **29 February** birth. Morinus computes each
boundary as `datetime(year + years, month, day)`, which raises for a leap
day whenever the target year is common. Boundaries are kept at the 28th
rather than spilling into March.

### Files changed
- `openastromod/firdaria.py` — new engine module
- `openastro` — `tableFirdaria`, Tables menu entry, print dispatch

## Feature: Atacir chart — 2026-09-19

### Change
New **Chart Type → Atacir Chart**: a bi-wheel with the radix inside and the
whole chart rotated at **360/N degrees a year** outside, cusps included.
The dialog asks the target date, the cycle and the direction (direct or
converse); the last values are remembered in `astrocfg`. Chart View
Both/Inner/Outer applies, with its own `Atacir` single-wheel type.

The cycle is entered as a free integer in [1, 360] rather than picked from
a list, because it is a continuous parameter: C-1 turns the chart once a
year, C-360 advances a single degree a year. The dialog shows the resulting
rate as you change it. The cycle names the technique, so one engine covers:

| Cycle | Rate | Known as |
|-------|------|----------|
| C-12 | 30°/year | annual profections |
| C-72 | 5°/year | the "5-degree atacir" |
| C-360 | 1°/year | symbolic directions |

### How it works
`openastromod/atacir.py`, ~40 lines of pure arithmetic — no ephemerides in
the loop, so an atacir cannot drift against the Swiss Ephemeris. The
rotation is rigid: bodies and cusps take the same arc, so the aspects among
rotated positions stay exactly the natal ones and what the chart shows is
their new relation to the natal frame.

    arc = days * (360 / N) / 365.2421904

**The roadmap had this formula wrong.** It recorded
`days * N / 365.2421904`, which for C-12 yields a quarter of the correct
rotation. The reference is Morinus' `profections.py`, whose
`K = 12.17473968` is days per degree for C-12; that is exactly
`365.2421904 / (360/12)`, which is the identity the module generalises. The
TODO entry has been corrected.

`localToAtacir()` derives the outer wheel into `t_*` and sets
`type="Transit"`, `solar_active=True`, `biwheel_single="Atacir"`. As with
primary directions, `makeSVG()` re-derives `t_*` from the stored arc on
every redraw, because the `Transit` branch rewrites `t_*` from `t_year`.

### Verification
Engine, 24 checks: `days_per_degree(12)` reproduces Morinus' K to the last
digit; C-12 matches `days / K` across four spans; the cycles advance
30/15/10/5/1° a year; a rotation preserves every internal distance; an
invalid cycle raises.

Cycle input, 10 checks: the bounds hold, out-of-range values clamp instead
of escaping, and unparseable input falls back to C-12 rather than reaching
the drawing code as a division by zero. All 360 cycles were then swept:
every rate is sane, and the worst deviation from closing an exact turn at
N years is 5.7e-14 degrees.

Against a real chart (1987-04-09, Sant Boi), the two criteria the roadmap
asked for and the doctrine behind them:

- at the birth instant the arc is 0 and nothing moves;
- at exactly 12 tropical years the arc is 360.000000° and the chart returns
  to itself;
- **at 1 year the Ascendant advances exactly one sign**, at 5 years five,
  at 30 years six (30 mod 12) — the classic annual profection falls out of
  the general engine rather than being special-cased;
- C-360 advances 25° in 25 years; converse three years back gives -90°.

### Not included
The **placidian** annual profection (Morinus'
`PlacidianAnnualProfection`). It advances the Ascendant from cusp to cusp
in discrete jumps rather than rotating continuously, so it is a different
mapping and does not fall out of this engine. The zodiacal variant — the
one that unifies symbolic directions and profections — is what ships here.

### Files changed
- `openastromod/atacir.py` — new engine module
- `openastro` — `localToAtacir`, `specialAtacir`/`specialAtacirSubmit`, the
  `Atacir` branches in `makeSVG`, Special menu entry

## Fix: three drawing bugs found while restyling — 2026-09-19

**Bodies whose name has a space were missing from the aspect lists.** The
first glyph of each row was `<use xlink:href="#name">` with the raw name,
while the second went through `svgSafeHref()`. Symbol ids use underscores,
so `#day pars` matched nothing and the Lot of Fortune simply did not draw —
visible as a row starting with its aspect. It affects 12 of the 36 bodies
(both nodes, both Liliths, the interpolated apogees, the lots with a space,
black sun). The Lot of Infortune escaped only because its name is already
`lot_of_infortune`. Fixed at all three unsanitised call sites: the directed
list, the transit list and the monthly Timeline table. An audit of all 14
`<use>` references to a planet name now reports zero unsanitised.

**Oppositions showed a nonsense arc orb in primary directions.** The ray
selection read `rays = (0.0,) if alpha in (0.0, 180.0) else (alpha, -alpha)`.
Collapsing conjunction and opposition to a single ray is right — the other
aspects have a dexter and a sinister one — but the ray *is* the aspect
angle, and passing 0 for an opposition aims `arc_of_direction()` at the
promisor's body instead of the point opposite it. With a promisor in exact
opposition and a directed arc of 39.50°, the orb came out 140°22'19"
instead of 39°30'00", off by the opposition's own 180°. Because the list
sorts by tightest orb, exact oppositions were being pushed to the bottom.
Checked across all eleven aspects: only the 180° row changes.

**Planet ink came from a stale table.** Two tables carry a planet colour:
`color_codes`, which feeds the glyph through the template and is what
Settings → Colors edits, and `settings_planet.color`, a legacy column that
nothing updates. They disagree for 13 of the 36 bodies, so a retrograde
Mercury drew its glyph in `#289900` and its R in `#520800`. All drawing now
goes through a new `planet_color()` reading `color_codes`. This also
retires two values SVG cannot parse that were sitting in the old column:
`orange` and `#33182`.

### Files changed
- `openastro` — `makeAspectTransitGrid`, Timeline table, `makeAspectsTransit`,
  new `planet_color()` and its eight call sites

---

## Chart style: retrograde glyph, wheel offset, glyph weight — 2026-09-19

**The ℞ glyph is back**, in the planet's own colour, replacing the letter R
on both wheels and in the planet grid. The S of a stationary planet stays a
letter — the symbol can only say "retrograde". The `#retrograde` symbol had
`fill:$paper_color_0` baked into its path, which overrides anything a caller
sets, so the fill was removed and each `<use>` now supplies the colour. That
also repairs the Timeline's retrograde marker, which had been passing a
colour that was silently ignored.

**Degrees of Asc and Mc read in the cusp colour** (`RADIX_CUSP_COLOR` on the
radix wheel, `houses_transit_line` on the outer one). Their glyph is an
arrowhead on the cusp, so the figure belongs to the cusp rather than to a
body. The literal black of the radix cusps became that constant, shared by
the cusp lines, their arrowheads and these readings.

**The outer wheel prints degree and minute next to each planet** instead of
a rotated degrees-only label out on the rim at r+3. The anti-collision
`group_offset` still applies, so a tight conjunction keeps its two readings
apart even when the glyphs overlap.

**The wheel sits 16px right** of the left-hand text, and the fixed-star ring
was pulled in from 10/22/34 to 8/18/26 to pay for it: the ring reaches
further out than the wheel, and at the old radius the rightmost star label
would have hit the planet column. `$makeFixedStars` also moved inside the
template's `$circleX` group — it draws in wheel coordinates, so it would
otherwise have detached from the wheel.

**The transit/directed list is right-aligned** on a 20px margin instead of a
fixed x. Its width depends on whether a second column appears past 12 rows,
so a single-column list can start 107px further right without the two-column
case overflowing the viewBox.

**Glyphs carry more weight.** Signs, nodes and lots are filled shapes and
take a `stroke` of their own colour; planets are stroked outlines, so their
`stroke-width` was raised instead — adding a second stroke would blur them.
Planet glyphs then went to `PLANET_GLYPH_SCALE = 0.7`, with the widths
raised by the inverse factor so the on-screen weight stays at 1.664px:
`stroke-width` lives inside the symbol and scales with it, so changing the
scale alone silently thins the outline. The four text symbols (As, Mc, Ds,
Ic) are left alone; stroking letters deforms them.

Fonts were evaluated as a source of glyphs and rejected: the twelve zodiac
codepoints fall back to emoji on every font installed here, and Leo has no
glyph at all.

### Files changed
- `openastro` — `motion_markup()`, `arrowhead()` callers, `zodiacSlice`,
  `makeHouses`, `makePlanets`, `makeAspectTransitGrid`, the drawing constants
- `openastro-svg.xml`, `openastro-svg-table.xml` — `#retrograde` fill,
  `$makeFixedStars` placement, symbol stroke weights

## Fix: New Chart / Edit Event took seconds to open — 2026-09-19

The dialog did two full scans of the 149,848-row `geonames` table before it
could appear, ~5.6 s of work on the atlas:

- `db.gnearest()`, which preselects the nearest city, filtered by a
  latitude/longitude box with no index on those columns: **2.750 s** to
  find the 244 rows inside the box.
- `eventDataChangedProvbox()`, filling the city combo with
  `WHERE country=? AND admin1=?`, also unindexed: **2.878 s**.

Three indexes added to the bundled `geonames.sql`:

| Index | Query | Before | After |
|-------|-------|--------|-------|
| `idx_geonames_lat_lon` | nearest-city box | 2.750 s | 0.029 s |
| `idx_geonames_country_admin1` | cities of a province | 2.878 s | 0.046 s |
| `idx_admin1codes_country` | provinces of a country | 0.010 s | 0.001 s |

Total data work on opening the dialog: **5.6 s → 0.097 s**. The lat/lon one
becomes a covering index — the query reads only `id`, `latitude` and
`longitude`, so it never touches the table.

The file grows 31.31 MB → 37.41 MB (+6.10). Indexing the shipped asset
rather than creating the indexes at runtime is deliberate: in a system
install the atlas sits read-only under `/usr/share/openastro.org`, where
`CREATE INDEX` would fail. `PRAGMA integrity_check` passes.

Measured and ruled out along the way: the internet check (returns
immediately, `use_geonames.org` is 0 here), and GTK widget construction —
building the `ListStore`, filling 662 rows and attaching the combo is
0.034 s, and even the atlas's worst province (England, 3,360 cities)
takes 0.106 s.

Adding `name` to the city index would drop the temporary sort, but costs
1.66 MB more to save 0.4 ms on 662 rows. Not taken.

### Files changed
- `geonames.sql` — three indexes

## Fix: South Node never showed its R — 2026-09-18

The South Node is derived as `planets_degree_ut[10] - 180`, the North
Node's opposite point, so it moves exactly as the North Node does and is
retrograde whenever the node is — which, for the mean node, is always
(~-0.0529°/day).

It never carried the mark. The normalisation loop that closes the derived
bodies (`for i in range(23,36)`) sets `retrograde=False`, `speed=0.0` and
`stationary=False` for everything in that range, which is right for the
lots and the hypothetical points but wrong for the South Node: it has real
motion, it is just expressed relative to another body. Its motion is now
restored from index 10 after that loop.

This reaches the outer wheel too — the transit ring reads
`t_module_data.planets_retrograde` from the same class.

Verified against real ephemeris on 2026-09-18, 2026-01-05, 2025-06-22 and
1990-03-11: separation from the North Node exactly 180.000° in each,
speed inherited to the last digit (-0.052939, -0.052933, -0.052924,
-0.052995 °/day), and `motion_mark` returning `R` for index 29 while the
lots and the Sun still return nothing.

### Files changed
- `openastromod/swiss.py` — South Node motion after the derived-body loop

---

## Chart style: outer wheel cusps thin, dashed and single-coloured — 2026-09-18

The outer wheel now matches the radix treatment introduced in "thin black
cusps with ASC/MC arrows", instead of keeping the old heavy solid look:

- **Thin dashed cusps.** `stroke-width: 2px` solid at 30% opacity becomes
  **1px dashed** (`stroke-dasharray:3,2`) at 40%, the same values the radix
  wheel uses.
- **One colour for every cusp.** The Ascendant, MC, Descendant and IC used
  to take their own colour from `planets[23..26]` while the other eight
  cusps used `houses_transit_line`; all twelve now use
  `houses_transit_line` (blue by default, still editable in
  Settings → Colors).
- **As/Mc glyphs replaced by arrowheads.** The outer wheel drew the `As`
  and `Mc` text glyphs; they are skipped now (as the radix wheel already
  skipped them) and an arrowhead marks the outer end of those two cusps.
  It is drawn in the cusp colour and slightly smaller than the radix one
  (L=8, W=6 against 10 and 8) to stay in proportion with the thinner line.

The arrowhead trigonometry moved out of `makeHouses` into an `arrowhead()`
method now that both wheels need it, and the per-angle `linecolor` block
was removed: after this change nothing read it — the radix wheel draws
every cusp black and the outer wheel uses the single colour.

Ds and Ic keep their glyphs on both wheels, as before; only the two angles
that get an arrow lose theirs.

### Files changed
- `openastro` — new `arrowhead()`, `makeHouses`, `makePlanets` (transit branch)

---

## Chart style: right-hand columns packed to the margin — 2026-09-18

Removing the row labels left each column spending its old name width on
nothing, so the three column blocks are repositioned as named constants
(`GRID_LOTS_X`, `GRID_PLANETS_X`, `GRID_HOUSES_X`) instead of the literals
that were buried in `makePlanetGrid` and `makeHousesGrid`.

Everything on the page sits inside the template's `translate(50,50)`, so
absolute x is 50 plus these. Measured extents:

| Column | Was | Now | Gutter |
|--------|-----|-----|--------|
| Lots | 445-519 | 490-559 | 29 |
| Planets | 565-639 | 588-657 | 29 |
| Houses | 686-751 | unchanged | 21 (right margin) |

The houses column is the widest and was already flush against the right
margin, so it anchors the block and the other two pack up to it on an even
gutter. The 21px right margin matches the header's 20px on the left.

This also closes a latent overlap. The lots column runs down the top-right
while the wheel bulges out to meet it; nine lot rows are possible
(`swiss.py` indices 27-35), and at the ninth the wheel reaches x=470.7.
The old x=445 would have put rows 8 and 9 inside the wheel — only the
default set of four lots kept it from showing. At 490 the worst row clears
by 19px.

The transit/directed list stays at its own x: in Directed mode its second
column carries the arc-orb text out to x=744, and moving it with the
others would push it past the 772.2 viewBox.

### Files changed
- `openastro` — grid x constants, `makePlanetGrid`, `makeHousesGrid`

---

## Chart style: planet names and "Cusp" dropped from the grids — 2026-09-18

The planet grid no longer prints the body's name ("Sun", "Lot of
Fortune", ...) — the glyph already identifies it — and the houses grid
prints `1:` instead of `Cusp  1:`. Rows keep their existing column
positions: the name was end-anchored at `x=0` and so extended left of the
block, and dropping it frees that margin instead of leaving a hole.

The `&#160;&#160;` padding on cusps 1-9 went with it. It existed to line
up `Cusp  1:` under `Cusp 10:`, but the text is end-anchored at `x=40`,
which right-aligns the numbers on its own.

`label['cusp']` is still used by the monthly Timeline table, so the
translation stays.

### Files changed
- `openastro` — `makePlanetGrid`, `makeHousesGrid`

---

## Chart style: LCh sign palette, smaller glyphs, layer alpha — 2026-09-18

### Sign glyphs
Wheel sign glyphs are drawn at **0.8** of their previous size
(`ZODIAC_GLYPH_SCALE`). They were `<use>`d at natural size inside a
`translate(-16,-16)`; they now scale about that same centre, so the
recentring scales with the glyph and the symbol stays in its sector.

### Palette rebuilt in CIELAB LCh
The old palette mixed Material shades of very different perceptual weight
— `#fdd835` (Libra) and `#0d47a1` (Scorpio) are nominally peers but one
glows and the other is nearly black, so sectors competed for attention.

The twelve sign colours are now generated from LCh, where **element sets
the hue** and **modality the lightness tier**:

| | hue (h°) | | cardinal | fixed | mutable |
|---|---|---|---|---|---|
| fire | 32 | **sector L\*** | 78 | 71 | 86 |
| air | 88 | **glyph L\*** | 42 | 35 | 45 |
| earth | 148 | **sector C\*** | 34 | 40 | 26 |
| water | 258 | | | | |

Two deliberate departures from a naive equal-L\* scheme, both from how the
hues actually behave:

- **Chroma is fitted to the sRGB gamut** by bisection per (L\*, h), so no
  channel is silently clipped. A requested C\* of 40 survives at blue but
  is cut to 18.7 at light water and 20.4 at light fire — clipping those
  would have quietly destroyed the uniformity the scheme is for.
- **Yellow carries a +7 L\* offset.** The yellow hue family only reads as
  yellow when light; at the blue tier's lightness it turns olive, and air
  would have stopped looking like air.

Worst glyph-on-sector contrast is **3.85:1** against the composited tint
(WCAG AA for large text is 3.0), down from cases where a deep glyph sat on
an equally deep sector.

### Alpha
The hardcoded `fill-opacity: 0.5` on sectors is now `ZODIAC_BG_ALPHA`
(0.45) next to the scale constant, and sign glyphs are drawn at
`ZODIAC_GLYPH_ALPHA` (0.92) so cusp lines and aspect rays read through
them. The contrast figure above is measured at these values — changing
them changes it.

Colours stay plain hex in the database so Settings → Colors keeps working;
the alpha is applied at draw time per layer rather than baked into the
stored value.

### Database
`defaultColors` covers new databases only (`INSERT OR IGNORE`), so the 24
rows were updated in `color_codes` of `~/.openastro.org/astrodb.sql` and
verified read-back. Backup: `astrodb.sql.bak-2026-09-18-lch-colors`.

### Files changed
- `openastro` — `ZODIAC_GLYPH_SCALE`/`ZODIAC_BG_ALPHA`/`ZODIAC_GLYPH_ALPHA`,
  `zodiacSlice`, `makeZodiac`, `defaultColors`

---

## Chart style: smaller header, grid and label text — 2026-09-18

Second pass over the canvas text, from screenshots of a rendered chart.
The wheel was not the only place things collided:

- **Planet grid.** The degree column starts at `x=19` and prints 9
  characters of DMS (`25&deg;49'02"`), which at 10px monospace is 54px
  wide and ran to `x=73` — straight through the zodiac glyph at `x=60`
  and into the R/S mark at `x=74`. The sign glyph was drawn on top of the
  seconds. Degrees are now 7px (ending at ~57, clear of the glyph),
  labels 8px, R/S mark 8px.
- **Houses grid.** Same column layout, same treatment: cusp label 8px,
  degrees 7px.
- **Header block.** Title 24px &rarr; 17px, chart name 12px &rarr; 10px and
  the location/date/lat/lon/position lines 10px &rarr; 8px. The date line
  is 28 characters and reached `x=188`, overlapping the wheel; it now ends
  at ~154. Bottom-left lines 10px &rarr; 9px.
- **Element percentages** 10px &rarr; 8px — "Earth (element) 15%" was
  running into the wheel.
- **Fixed-star labels** 7px &rarr; 6px (crowded stars were overprinting
  each other), **transit/directed list** title 12px &rarr; 10px, rows
  10px &rarr; 8px, directed orb column 9px &rarr; 7px.

Column clearances were computed from the monospace advance (0.6em), not
eyeballed, and noted in a comment where the planet-grid degrees are drawn.

### Files changed
- `openastro` — `makePlanetGrid`, `makeHousesGrid`, `makeElements`,
  `makeFixedStars`, `makeAspectTransitGrid`
- `openastro-svg.xml` — header and bottom-left text sizes

---

## Chart style: smaller canvas text, aspect grid moved right — 2026-09-18

The per-planet texts were colliding with their neighbours. Planets grouped
closer than `planet_drange` (3.4°) sit at a wheel radius of 146-166px, so
their arc separation is only ~9px, while `12°34'` at 7px in a monospace
face is ~25px wide — three neighbours' worth.

Sizes reduced on the wheel: planet degree+minute 7px → **5px** (halo
stroke 2px → 1.5px, which at 5px would otherwise swallow the glyphs),
R/S marks 10px → **7px** natal and **6px** on the outer wheel (whose
glyph is only 12px across), outer-wheel degrees 8px → **6px**, house
numbers 11px → **9px**.

Positions: the R/S mark moved up from the glyph's bottom-right corner to
its right flank (`y+12` → `y+4` natal, `y+10` → `y+2` outer), and the
degree+minute moved closer under the glyph (`+7,+23` → `+3,+17`).

The natal aspect grid starts 50px further right (`xindent` 380 → 430).
It grows right and up by 14px per visible planet, so with all 20 shown it
spans 280px and 430 keeps it inside the 772.2px viewBox.

Note: smaller type reduces the collisions but cannot remove them for tight
conjunctions — at ~9px of arc even 5px text overlaps. Widening
`planet_drange` or dropping the wheel to degrees-only (`type="1"`) would
be the next lever.

### Files changed
- `openastro` — `makeHouses`, `makePlanets` (natal and transit branches),
  `makeAspectGrid`

---

## Fix: house numbers crashed the wheel drawing — 2026-09-18

"Smaller house numbers in cusp sign color" (67d8d11) built the `<text>`
element by concatenation but left the colour as a `%s` with the `%`
operator at the very end of the expression. Python binds `%` to the last
operand only, so the format was applied to the trailing
`'</tspan></text>\n'` — a string with no placeholders — and every house
number raised `TypeError: not all arguments converted during string
formatting` instead of being drawn.

The colour is now concatenated like the rest of the element. Both call
sites were affected (transit ring and natal ring, `openastro:2479` and
`:2493`).

### Files changed
- `openastro` — `makeSVG`, transit and natal house-number `<text>`

---

## Docs: roadmap synced with the code — 2026-09-18

`TODO.md` had gone stale: it still listed the whole of wave 1 as pending
(fixed stars, antiscia, lunar return, ascensional transits — all four
branches merged into `main`, 0 commits ahead) and claimed the heliocentric
chart still needed a UI, when `helio` has long been one of the position-type
options in preferences. All of that moved to the "already in" block.

`README.md` gained the wave-1 features it never listed: lunar return, fixed
stars (222-star catalog), antiscia/contraantiscia charts, ascensional
transits and the R/S motion marks.

`AGENTS.md` marks wave 1 complete and defines wave 2 with its merge order.

Also recorded in `TODO.md`: **atacires** as the next feature, with the
finding that drives its design — in Morinus, *atacir* is the Spanish name
for *profection* (`Morinus SE/mtexts.py:37,50` → "Atacires del C-12";
`:253-254` → placidian vs zodiacal annual variants). So the atacir engine,
the profections engine and the 1°/year symbolic directions are one and the
same rigid `360/N` degrees-per-year rotation (`Morinus SE/profections.py`,
`K = 12.17473968` days/degree = 365.2421904/30). Wave 2 therefore builds one
generic engine with a configurable cycle and derives C-12 (profections) and
C-360 (symbolic) as presets, instead of three separate implementations.

### Files changed
- `TODO.md`, `AGENTS.md` (untracked working docs), `README.md`

---

## Chart style: thin black cusps with ASC/MC arrows — 2026-09-18

House cusp lines are thin black (1px); the As/Mc wheel glyphs are replaced
by arrowheads at the outer end of the Ascendant and MC cusp lines.

## Feature: R/S motion marks — 2026-09-18

Planets show **R** when retrograde and **S** when stationary, on the
wheel (natal and outer) and in the planet grid (replacing the ℞ glyph).
Stationary = |daily motion| under 3% of the planet's mean motion
(`MEAN_MOTION`/`STATION_FRACTION` in `openastromod/swiss.py`, Sun..Pluto
only — Sun, Moon and nodes can never trigger it); S wins over R at the
station itself. Verified with real ephemeris: Mercury R Aug 8-9, S Aug
10-11 (direct station), direct from Aug 12; Sun/Moon never flagged in 12
monthly samples.

## Fix: frozen new-chart dialog on slow networks — 2026-09-18

`eventData()` called `checkInternetConnection()` on the GTK thread before
showing the dialog, and that check did a blocking `connect()` with no
timeout: on networks that drop packets the whole UI froze for minutes.
The check is now bounded with a 3 s socket timeout (always restored),
covering all three call sites at once.

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

---

## Feature: Lunar Return chart — 2026-09-18

### Change
- New **Chart Type → Lunar Return**: bi-wheel with the radix inside and the
  lunar return outside, cloned from the solar-return flow. The dialog asks
  year and month (last used remembered in `astrocfg`); the return found is
  the one nearest mid-month. Chart View Both/Inner/Outer applies, with its
  own `Lunar` single-wheel type.
- Geocentric Moon always (lunar parallax reaches almost a degree and would
  eat any tight orb — measured doctrine).

### How it works
- `openastro.localToLunar()`: coarse step proportional to the tropical
  month (27.321661 d), then 3 refinement passes with measured two-point
  lunar speed (seconds precision). Return houses at the natal place.
- Verified against an independent minute-scan crossing search: agreement
  0.7 s on a 2026-09 test chart; return residue under 1″.

### Files changed
- `openastro` — `localToLunar`, `specialLunar`/`specialLunarSubmit`,
  `Lunar` branch in `makeSVG`, Special menu entry
- `openastro-ui.xml` — reference menu entry (file kept for reference only)

---

## Feature: Antiscia chart — 2026-09-18

### Change
- New **Chart Type → Antiscia Chart**: a **bi-wheel** with the radix on the
  inside and the antiscion positions outside (reuses the transit ring).
  Chart View Both/Inner/Outer applies, with its own `Antiscia` single-wheel
  type (antiscia on the natal house frame). A dialog selects **Antiscia**
  or **Contraantiscia** (= antiscion + 180°) for the outer wheel, remembered
  in `astrocfg`; opposition lines to an antiscion outer wheel also mark
  contraantiscion directions.
- Antiscion = reflection on the Cancer 0° / Capricorn 0° axis (declination
  symmetry), following Morinus (`antiscia.calc`). Antiscia are tropical by
  definition: with a sidereal zodiac the input converts to tropical and
  back via the current ayanamsa.

### How it works
- `openastromod/swiss.py` — `calc_antiscion(lon, ayan)`, `ayanamsa`
  attribute in `ephData` (from `swe.get_ayanamsa_ut` when sidereal),
  per-body and per-cusp antiscion/contraantiscion lists.
- `openastro.localToAntiscia()` derives the outer wheel from the radix into
  `t_*` and sets `type="Transit"`, `solar_active=True`,
  `biwheel_single="Antiscia"`; `makeSVG()` re-derives `t_*` from the stored
  lists on every redraw, and the `Antiscia` branch renders "Outer only".
  `specialAntiscia()` dialog (antiscia/contraantiscia, remembered).
- Verified 16/16 against replicated Morinus branch logic, tropical and
  sidereal (symmetry ant(ant(lon)) == lon holds to 5.7e-14).

### Files changed
- `openastro` — `localToAntiscia`, `specialAntiscia`, the `Antiscia` branch
  and outer-wheel override in `makeSVG`, Special menu entry
- `openastromod/swiss.py` — `calc_antiscion`, ayanamsa, antiscia lists
- `openastro-ui.xml` — reference menu entry (file kept for reference only)

---

## Feature: Fixed Stars — 2026-09-18

### Change
- New **Tables → Fixed Stars**: only stars in conjunction with a visible
  planet or a cusp are listed (star | longitude | latitude | conjunction),
  and only those are drawn as markers with short labels OUTSIDE the
  circle, staggered over three outer rings so close markers never overlap.
  Per-star orb by brightness: 2° under magnitude 1, 1° otherwise.
- Catalog of 222 major stars (see `FIXED_STARS` in `openastromod/swiss.py`;
  `Han`/`Marfik` excluded as mislabeled catalog lines, `Coxa` as a `Chertan`
  duplicate, `Dschubba` included as `Isidis (Dschubba)`), computed with
  `swe_fixstar_ut` like Morinus (`fixstars.py`).
- Colors by nature: black for the very malefic (Vertex, Algol, Alcyone,
  Prisipe, Algorab, Aculeus, Acumen, Spiculum, Facies, Scheat), blue for
  the very benefic (Regulus, Zaniah, Spica, Arcturus, Atria, Polis,
  Ascella, Dheneb, Sadalsuud, El Nath), default ink for the rest.
  Needs the star catalog (`sefstars.txt`) in the ephemeris path;
  missing stars are skipped silently, so older catalogs simply show
  fewer stars (this swe build also falls back to `fixstars.cat`,
  and Spica is built in).
- The catalog ships with the repo as `sefstars.txt` (Morinus data) and
  auto-installs into `~/.openastro.org/swiss_ephemeris` on first run if
  missing, so all 222 resolve out of the box.

### How it works
- `openastromod/swiss.py` — `FIXED_STARS` catalog, per-star
  `swe_fixstar_ut` with 3-/4-tuple tolerant unpacking (pyswisseph
  versions differ), `fixed_*` attributes in `ephData`.
- `openastro.makeFixedStars()` draws markers; `tableFixedStars()`
  renders the SVG table with print/PDF.
- Verified with real ephemeris: the catalog resolves fully with the
  bundled file (with older catalogs Facies/Acumen/Kaus Media are skipped)
  and positions match references to 0.005°; empty catalog degrades to an
  empty list without errors.

### Files changed
- `openastro` — `makeFixedStars`, `tableFixedStars`, Tables menu entry
- `openastromod/swiss.py` — `FIXED_STARS`, fixed-star computation
- `openastro-svg.xml` — `$makeFixedStars` placeholder
- `openastro-ui.xml` — reference menu entry (file kept for reference only)

---

## Feature: Ascensional transits (mundo contacts) — 2026-09-18

### Change
- New **Measure** selector in the **Transit Chart** dialog: **Ecliptic**
  (default, the current behaviour) or **Ascensional (mundo)**.
- In ascensional mode the contacts are measured by equality of oblique
  ascension under the transiting planet's own topocentric pole — the
  transit analogue of the ascensional measure of primary directions
  (carta-natal.es/transitos.php context). Both bodies keep their true
  ecliptic latitude; only visible planets are considered.
- The wheels stay ecliptic: each contact uses its own transit pole, so no
  single OA wheel exists (unlike directions, there is no OA rendering).
- The last used measure is remembered in `astrocfg` (`transit_measure`),
  like the directions dialog does. Synastry (which reuses the transit
  bi-wheel) follows the saved measure.

### How it works
- `openastromod/primary.py` — new `TRANSIT_MEASURE_KEYS`/`TAGS` plus a
  minimal `transit_oa_pair()` helper built only on the existing
  primitives (`ecliptic_to_equatorial`, `topocentric_pole`,
  `oblique_ascension`): transit RA/Dec give the pole, then OA of both
  bodies under that pole. Natal frame uses the birth JD, transit frame
  the transit JD, pole and OAs the transit RAMC at the natal latitude.
- `openastro` — `specialTransit()` is now a measure dialog and
  `specialTransitSubmit()` draws the now-moment bi-wheel with the chosen
  measure (chart title gains ", ascensional"); `makeSVG()` also grabs
  the transit latitudes, RAMC and JD; `makeAspectsTransit()` compares OA
  differences with the usual orbs when the measure is ascensional on a
  `TransitOuter` bi-wheel, and the ecliptic longitudes otherwise.

### Verification
- Hand calculation with the engine primitives (pyswisseph 2.10.03 via wsl
  python3): natal MC 58.394075 deg (Barcelona 41.38879N 2.15899E,
  2000-06-15 10:00 UT, JD 2451710.916667) vs transit Moon 62.295142 deg,
  lat 5.197333 deg (2026-03-23 12:07:20 UT, JD 2461123.005093,
  RAMC 4.990014): Moon RA 59.077297 / Dec 25.710511, MC RA 56.150883 /
  Dec 19.801192, pole 22.494157, OA transit 47.576382 vs OA natal
  47.576528 — mundo orb 0.000146 deg (~0.5") while the ecliptic distance
  is 3.901067 deg, so the contact exists only in mundo. The helper
  matches the manual primitives to 1e-9; obliquities 23.437937/23.438356.
- `py_compile` passes on both touched Python files.

### Files changed
- `openastro` — `specialTransit`/`specialTransitSubmit`, `transit_measure`
  default, transit frame grab in `makeSVG`, OA branch in
  `makeAspectsTransit`, saved measure applied to Synastry
- `openastromod/primary.py` — `TRANSIT_MEASURE_KEYS`/`TAGS`,
  `transit_oa_pair()`
