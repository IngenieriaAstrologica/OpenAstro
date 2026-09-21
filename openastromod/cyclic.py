"""The cyclic index of Henri Gouchon and Andre Barbault.

Mundane astrology's one number for a date: how tightly the slow planets are
packed. Gouchon proposed it in 1946 and Barbault made it his working tool,
so the curve is usually named after both. For every date you take the five
slow planets -- Jupiter, Saturn, Uranus, Neptune, Pluto -- measure the
angular distance of each of the **ten pairs** they form, and add the ten
distances up. Plotted against time the sum becomes a slow wave:

    low index    the planets are gathered in one part of the zodiac,
                 conjunctions pile up, the tradition reads crisis
    high index   they are spread around it, tension released

Each distance is the shorter arc, so it runs 0 to 180 degrees. That gives a
nominal ceiling of 1800, but **the index can never reach it**: ten pairs
cannot all be in opposition at once. Five points on a circle maximise the
sum of their pairwise arcs when they split into two antipodal groups of two
and three, which puts 2*3 = 6 pairs at 180 degrees and the remaining four at
0, so the real maximum is 1080. The floor is 0, all five conjunct, and the
average over a uniform random spread is 10 * 90 = 900. `MAX_INDEX` and
`MEAN_INDEX` below record those three landmarks; they are what the vertical
axis of any honest plot should be scaled to.

Frame of reference: **heliocentric, and that is a choice**
------------------------------------------------------------------
Two conventions circulate and they give visibly different curves.

* *Heliocentric* (what this module defaults to). The planets are seen from
  the Sun, so nothing in the curve comes from the Earth's own motion. The
  index then moves only as fast as Jupiter and the rest actually move, and
  the wave is smooth over decades -- which is how Barbault's published
  curves look, and what makes a minimum datable to a year rather than to a
  month of retrograde wobble.
* *Geocentric*. Every outer planet retrogrades once a year as seen from the
  Earth, so the sum picks up an annual ripple of a few tens of degrees on
  top of the real signal. Readable, but the ripple is an artefact of where
  the observer stands, not of the planets' configuration.

The deciding evidence for the default is the only primary material this
project has on the technique: the plot templates of Miguel Garcia's ARMON
(1996-2006), which name the curve outright. `CRR_F10.DHQ` labels its band
"Gouchon/Barbault" and `_MALAGA2.DHQ` and `MUNCYCL.DHQ` label theirs
"Indice Ciclico"; all three declare the same band -- wave type `barbault`,
harmonic 1, orb 180, bodies `T:jsunp` (transiting Jupiter, Saturn, Uranus,
Neptune, Pluto) -- which is exactly the definition above, and the scripts
that draw the first two (`ARTICLES.SCR` lines 1698 and 2543) set
`helio=si`. A third figure, `_S99_II3.DHQ`, has the same `helio=si` line
commented out, so the geocentric reading was a deliberate variant of the
same author's, not an oversight. Hence: heliocentric by default,
geocentric available by passing the longitudes of the geocentric planets
instead. This module never decides the frame itself -- it only adds up
whatever longitudes it is handed.

No ephemerides here. `openastromod.swiss.cyclic_longitudes()` fetches the
five longitudes for a date; everything in this file is arithmetic on
numbers the caller supplies, which is also what makes it testable without
Swiss Ephemeris installed.

Not implemented, and deliberately so:

* The *planetary resultant* / *index of concentration* (ARMON's
  `concentracion` wave, Barbault's "resultante planetaire"): the vector sum
  of the planets' unit vectors rather than the sum of their separations. A
  different quantity with a different meaning, not a refinement of this
  one.
* The *harmonic* cyclic index (ARMON's `_S99_II4`), which measures the
  pairs modulo a harmonic instead of on the whole circle.
* Barbault's practice of reading the curve together with the individual
  planetary-pair cycles. That is interpretation, not computation.
"""

#The five slow planets, as OpenAstro planet indices. These coincide with the
#Swiss Ephemeris body numbers, so the same tuple serves both.
SLOW_PLANETS = (5, 6, 7, 8, 9)

#Ten pairs out of five bodies.
PAIR_COUNT = 10

#Attainable maximum: two antipodal groups of two and three bodies, so six
#pairs at 180 degrees and four at 0. Not 1800 -- see the module docstring.
#The maximum is a PLATEAU, not a peak, and that changes how the curve is
#read. 1080 is not reached at one special arrangement but across a wide
#region: perturbing any of the five planets by a degree or five usually
#leaves the sum at exactly 1080 (18 of 20 such perturbations, measured on
#the January 2003 configuration, which itself sits at 1080.0000). So a
#reading of "100% of maximum" is saturation rather than a sharp high, and
#the tops of the curve are genuinely flat. Minima, by contrast, are sharp
#and are where the technique carries its information.
MAX_INDEX = 1080.0

#Expected value for longitudes spread uniformly at random: ten pairs at a
#mean separation of 90 degrees.
MEAN_INDEX = 900.0


def separation(lon_a, lon_b):
    """Angular distance of two longitudes, the shorter arc, in [0, 180]."""
    d = abs(float(lon_a) - float(lon_b)) % 360.0
    if d > 180.0:
        d = 360.0 - d
    return d


def pairs(items):
    """All unordered pairs of a sequence, in the order given."""
    seq = list(items)
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            yield seq[i], seq[j]


def index(longitudes):
    """The cyclic index of one moment: sum of the pairwise separations.

    `longitudes` is a sequence of ecliptic longitudes in degrees -- five of
    them for the classical index, but any number works and the result is
    then the sum over that many bodies' pairs. Returns a float in
    [0, 1080] for five bodies.
    """
    return sum(separation(a, b) for a, b in pairs(longitudes))


def separations(longitudes, keys=SLOW_PLANETS):
    """The individual pair separations, for showing the index's makeup.

    Returns [(key_a, key_b, separation)] in the pair order of `pairs()`.
    `keys` names the bodies; it is only used for labelling and must be as
    long as `longitudes`.
    """
    lons = list(longitudes)
    names = list(keys)
    out = []
    for i, j in pairs(range(len(lons))):
        out.append((names[i], names[j], separation(lons[i], lons[j])))
    return out


def series(samples):
    """The index over time.

    `samples` is an iterable of `(date, longitudes)`: whatever date object
    the caller wants to label the point with, and the sequence of
    longitudes for that date. Each entry of the result is a dict:

        date    the label handed in, untouched
        index   the cyclic index there

    Kept this dumb on purpose: the ephemeris loop belongs to the caller, so
    the same function serves a real curve and a test with made-up numbers.
    """
    return [{'date': when, 'index': index(lons)} for when, lons in samples]


def extrema(rows, half_window=24):
    """Turning points of the curve: the minima and maxima worth naming.

    A sample is a minimum when no sample within `half_window` positions on
    either side is lower, and a maximum when none is higher; ties inside the
    window keep the first occurrence, so a flat bottom is reported once.
    The window is in samples, not years -- with monthly sampling the default
    of 24 asks for the lowest point in a four-year neighbourhood, which is
    the scale Barbault's minima live on.

    Returns [{'date', 'index', 'kind'}] in date order, `kind` being 'min' or
    'max'. The ends of the series are skipped: half a window is not enough
    evidence to call a turning point.
    """
    data = list(rows)
    n = len(data)
    w = int(half_window)
    out = []
    for i in range(w, n - w):
        here = data[i]['index']
        window = data[i - w:i + w + 1]
        lows = [r['index'] for r in window]
        if here == min(lows) and all(r['index'] > here for r in window[:w]):
            out.append({'date': data[i]['date'], 'index': here, 'kind': 'min'})
        elif here == max(lows) and all(r['index'] < here for r in window[:w]):
            out.append({'date': data[i]['date'], 'index': here, 'kind': 'max'})
    return out
