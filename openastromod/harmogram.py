"""Harmograms: the strength of each harmonic, traced over time.

A harmonic chart of order N is the radix with every longitude multiplied by
N and folded back into the circle. Aspects of the Nth harmonic family
become conjunctions there, so the whole question "how strong is harmonic N
right now" reduces to "how many conjunctions does the Nth harmonic chart
contain" -- which is a number, and a number can be plotted against time.
Doing that for the first twelve harmonics gives twelve curves: a harmogram.

Mike O'Neill arrived at the technique, and Miguel García Ferrández reached
it independently; ARMON is his program, and the `.DHQ` files that ship with
it are its plot templates. Two of those templates name the two readings
this module implements:

* **Harmonic transits.** The moving sky measured against a fixed radix:
  receivers are the natal degrees, emitters the transiting planets. The
  `.DHQ` templates mark this as `R:` against `T:`.
* **Natal harmogram.** The moving sky measured against itself, with no
  reference to the radix, both sets `T:`. García introduced it because
  harmonic transits misbehave near the birth moment: every planet is then
  conjunct its own radical place in *all* the low harmonics at once, and
  the curves spike absurdly. Reading the sky against itself removes the
  artefact.

The orb
-------
`ORB = 360/13 = 27.6923...` degrees, and that exact figure is García's.
It is not empirical: it is the widest orb a conjunction can be given
before it reaches into the semisextile's territory, 360/12 away. The
`.DHQ` templates carry it as the literal `27.69231`.

The weighting
-------------
Conjunctions are counted "weighted by a Gaussian orb". The sources
describing the technique say that much and no more -- they give no
constant -- so the shape here is the canonical Gaussian, parametrised
rather than hidden: `WEIGHT_AT_ORB` fixes what a conjunction exactly at
the orb boundary is worth, and the curve follows from it. Change that one
number and the whole weighting moves with it.
"""

import math

#García's conjunction orb: 360/(12+1).
ORB = 360.0 / 13.0

#Harmonics a harmogram traces, as in ARMON's own templates.
HARMONICS = tuple(range(1, 13))

#The ten bodies ARMON's templates carry, as Swiss Ephemeris numbers, and
#the same ten as OpenAstro indexes them. Sun through Pluto: the `.DHQ`
#body lists hold exactly ten characters.
DEFAULT_BODIES = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
RADIX_INDICES = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)

#What a conjunction sitting exactly on the orb boundary counts for. The
#Gaussian is cut off there, so this also sets how abruptly it ends: at 5%
#the discontinuity is too small to show in a plotted curve.
WEIGHT_AT_ORB = 0.05


def normalize(deg):
    """Fold an angle into [0, 360)."""
    return float(deg) % 360.0


def harmonic(lon, n):
    """Position of a longitude in the Nth harmonic chart."""
    return normalize(float(lon) * int(n))


def separation(a, b):
    """Shorter arc between two longitudes, 0..180."""
    d = abs(float(a) - float(b)) % 360.0
    return min(d, 360.0 - d)


def weight(sep, orb=ORB, at_orb=WEIGHT_AT_ORB):
    """Gaussian weight of a conjunction `sep` degrees wide.

    1 when exact, `at_orb` at the orb boundary, 0 beyond it. Writing the
    exponent as -ln(at_orb) is what ties the two ends together: the caller
    states what the boundary is worth and the width follows, instead of a
    bare sigma nobody can interpret.
    """
    sep = abs(float(sep))
    if sep >= orb:
        return 0.0
    k = -math.log(float(at_orb))
    return math.exp(-k * (sep / float(orb)) ** 2)


def intensity(receivers, emitters, n, orb=ORB, same_set=False, at_orb=WEIGHT_AT_ORB):
    """Strength of harmonic `n` between two sets of longitudes.

    Every emitter is tested against every receiver in the Nth harmonic
    chart and the weights are summed.

    `same_set` is for the natal harmogram, where the two sets are one and
    the same: each pair is then counted once and no body is matched with
    itself, since a body is always exactly conjunct its own place and
    would just add a constant to every harmonic.
    """
    r = [harmonic(v, n) for v in receivers]
    e = [harmonic(v, n) for v in emitters]
    total = 0.0
    for i, ev in enumerate(e):
        for j, rv in enumerate(r):
            if same_set and j <= i:
                continue
            total += weight(separation(ev, rv), orb, at_orb)
    return total


def sample_times(jd_centre, days, parts_per_day):
    """Julian days across a window centred on `jd_centre`.

    `days` and `parts_per_day` are the `.DHQ` fields NDY and NDP; the
    window is centred because ARMON draws the moment of interest as a
    vertical line down the middle of the plot.
    """
    days = float(days)
    steps = max(1, int(round(days * float(parts_per_day))))
    start = jd_centre - days / 2.0
    step = days / float(steps)
    return [start + i * step for i in range(steps + 1)]


def curves(longitudes_at_jd, jd_centre, days, parts_per_day,
           radix=None, harmonics=HARMONICS, orb=ORB, at_orb=WEIGHT_AT_ORB):
    """Trace every harmonic across the window.

    `longitudes_at_jd` is a callable taking a Julian day and returning the
    emitter longitudes -- injected rather than imported so the engine can
    be exercised without an ephemeris.

    Pass `radix` for harmonic transits, where receivers are fixed natal
    degrees; leave it out for a natal harmogram, where the sky is read
    against itself.

    Returns (jds, {harmonic: [intensity per sample]}).
    """
    jds = sample_times(jd_centre, days, parts_per_day)
    out = {n: [] for n in harmonics}
    for jd in jds:
        moving = longitudes_at_jd(jd)
        for n in harmonics:
            if radix is None:
                out[n].append(intensity(moving, moving, n, orb, True, at_orb))
            else:
                out[n].append(intensity(radix, moving, n, orb, False, at_orb))
    return jds, out


def max_intensity(n_receivers, n_emitters, same_set=False):
    """Ceiling a curve could reach: every pair exactly conjunct.

    Only useful for scaling an axis; real charts come nowhere near it.
    """
    if same_set:
        return n_emitters * (n_emitters - 1) / 2.0
    return float(n_receivers) * float(n_emitters)
