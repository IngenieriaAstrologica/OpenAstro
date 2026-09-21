"""Harmonic chart engine: the radix with every longitude multiplied by N.

A harmonic chart of order N takes every longitude in the radix and
multiplies it by N, folding the result back into the circle (mod 360). It
is the cheapest derived chart there is -- no new ephemeris lookup, just a
linear map over positions already computed -- and it is the shared
geometric floor under everything harmonic already in this project:
`harmogram.py` traces how loud each harmonic chart's conjunctions are over
time, and `harmonicvector.py` reads the same transform as a Fourier
spectrum (the Harmonic Flower, and Boudineau's Resultante Planetaria at
h=1). Neither of those needed a chart-level transform of its own, only the
single-longitude map -- see "Reuse, not duplication" below.

N=1 is the identity: `harmonic(lon, 1) == lon`, the radix itself. Every
other N folds the circle N times, so bodies N-th-harmonic-related in the
radix land on top of each other; that collapsing-and-folding is the whole
content of Addey's harmonic astrology, and this module has no more
machinery than the fold itself.

Reuse, not duplication
-----------------------
`harmogram.harmonic(lon, n)` already is exactly this engine's primitive:
`normalize(lon * n)`. Rewriting it here would be a second copy of a
one-line formula the harmogram tests already exercise (harmonic 1 is the
identity, a trigon closes in the 3rd, and so on) -- so this module
imports it rather than duplicating it. `harmogram.py` keeps its own
reason to exist, the Gaussian-orb intensity trace over time, and is not
touched: moving `harmonic()` out of it and into here would ripple into
`harmonicvector.py`'s cross-reference and the harmogram test for no
benefit, so it stays where it is. What this module adds on top of that
primitive -- a range check on N, a whole-chart transform, and the
composition identity below -- did not exist anywhere in the project
before this file.

Houses: kept radical, not multiplied
-------------------------------------
Morinus (`Morinus SE/`) has no harmonic-chart module to check against --
the technique is Addey's, not part of the Placidus/Regiomontanus
tradition Morinus otherwise covers -- so there is no reference
implementation in this codebase's usual second source for this one
choice. It is argued from the arithmetic instead.

Multiplying the *bodies*' longitudes by N is exactly the point of the
technique: aspects among the harmonized bodies become the Nth-harmonic
aspects. House cusps are a different kind of object -- twelve boundaries
that must stay in ascending ecliptic order all the way round the circle
-- and multiplication by N does not respect that order. Concrete
counterexample: radix cusps 10, 100, 190, 280 (ascending) map under
`harmonic(., 3)` to 30, 300, 210, 120 -- descending, i.e. no longer a
valid house division at all. A map that can silently reorder or invert
the houses cannot stand in for a house system, and building a real
"harmonic house system" (re-deriving Placidus, or whatever system, from a
synthetic harmonic MC/Ascendant) needs geometry and geography -- latitude,
obliquity, the MC/ARMC relation -- that a pure longitude engine
deliberately has none of.

So `chart()` below is meant to be called on the bodies the caller wants
harmonized -- planets and points, not cusps -- and the harmonic chart, as
this project implements it, is read against the RADICAL houses: the
technique asks which bodies fall together in the Nth harmonic circle, not
for a redrawn house division. A caller that wants a "harmonic Ascendant"
as an informational point (not a cusp with ordering obligations) can pass
it through `harmonic()` like any other single longitude -- but that is a
choice for the dialog/drawing layer, not something this engine does on
its own.
"""

from . import harmogram as _harmogram

#Practical range for a UI spinner, not a mathematical limit. Unlike the
#atacir cycle, N here has no natural periodicity that would make 360 a
#structural boundary: lon*N mod 360 is not periodic in N once lon is a
#non-integer degree, so there is no N beyond which "it repeats". 360 is
#kept only because it is the same generous, round ceiling atacir already
#settled on, and it comfortably holds every harmonic named in the
#literature (4, 5, 7, 9, 16, and the low hundreds some authors use).
MIN_HARMONIC = 1
MAX_HARMONIC = 360
DEFAULT_HARMONIC = 1


def valid_harmonic(n, default=DEFAULT_HARMONIC):
    """Coerce user input into a usable harmonic order.

    Mirrors `atacir.valid_cycle`: unparseable input falls back to the
    default, and out-of-range values are clamped, so a stray dialog entry
    can never reach the transform as a zero or negative multiplier.
    """
    try:
        n = int(n)
    except (TypeError, ValueError):
        return default
    return max(MIN_HARMONIC, min(MAX_HARMONIC, n))


def normalize(degrees):
    """Fold an angle into [0, 360)."""
    return _harmogram.normalize(degrees)


def harmonic(lon, n):
    """Position of a single longitude in the Nth harmonic chart.

    Delegates to `harmogram.harmonic` -- see "Reuse, not duplication"
    above for why this is a re-export and not a second copy.
    """
    return _harmogram.harmonic(lon, n)


def chart(longitudes, n):
    """The Nth harmonic chart: every longitude multiplied by N, mod 360.

    `longitudes` is whatever the caller wants harmonized -- typically
    `ephData.planets_degree_ut`, or a subset of it. House cusps are
    deliberately not this function's business; see "Houses" above.
    """
    return [harmonic(v, n) for v in longitudes]


def compose(n, m):
    """The harmonic order equivalent to an Nth chart of an Mth chart.

    `harmonic(harmonic(lon, m), n) == harmonic(lon, n * m)` for every lon
    (up to ordinary floating-point rounding): folding mod 360 and then
    scaling by n is the same map as scaling by n*m and folding once. This
    lets a caller reach a nested reading directly -- the 4th harmonic of a
    5th harmonic chart is just harmonic order 20 -- instead of composing
    two transforms by hand.
    """
    return int(n) * int(m)
