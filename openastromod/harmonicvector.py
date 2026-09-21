"""Harmonic Vector, and the Harmonic Flower drawn from it.

Miguel García's construction, in his own words: put a Dirac delta at each
planet's longitude and take the Fourier spectrum of the sum. Each harmonic
h then has an amplitude and a phase,

    C(h) = SUM over planets of exp(i * h * lambda)
    A(h) = |C(h)|        how concentrated the chart is in harmonic h
    W(h) = arg(C(h)) / h  where that concentration points

which he calls the h-th coordinate of the harmonic vector. Boudineau's
Resultante Planetaria is the same thing at h=1.

The reading is direct. In the h-th harmonic chart every longitude is
multiplied by h, so `C(h)` is the vector sum of unit arrows at those
multiplied positions. All the planets in one place gives an amplitude of
n, the number of planets; planets spread evenly around the circle gives
zero, the arrows cancelling. Normalised by n it becomes an index between
0 and 1, and plotting that index for the first twelve harmonics as petals
around a centre is the **Harmonic Flower**.

The flower and a harmogram answer different questions, which is why the
dominant harmonic often differs between them:

    flower      how concentrated the chart is in each harmonic
    harmogram   how many conjunctions each harmonic chart holds,
                weighted by an intensity function

This module is the first. `openastromod.harmogram` is the second.

No ephemerides here: longitudes come from the caller.
"""

import cmath
import math

HARMONICS = tuple(range(1, 13))


def coefficient(longitudes, h):
    """The h-th Fourier coefficient, as a complex number.

    Unit arrows at each planet's position in the h-th harmonic chart,
    added tip to tail.
    """
    return sum(cmath.exp(1j * h * math.radians(float(lon))) for lon in longitudes)


def amplitude(longitudes, h):
    """|C(h)|: how tightly the chart gathers in harmonic h, 0..n."""
    return abs(coefficient(longitudes, h))


def phase(longitudes, h):
    """Where that gathering points, as a longitude in [0, 360).

    The argument of C(h) is an angle in the harmonic circle; dividing by h
    brings it back to the zodiac. Only one of the h possible preimages is
    returned -- the others sit 360/h apart.
    """
    if not longitudes:
        return 0.0
    ang = math.degrees(cmath.phase(coefficient(longitudes, h)))
    return (ang / float(h)) % 360.0


def concentration(longitudes, h):
    """Amplitude normalised to 0..1: the flower's petal length.

    1 when every planet shares one point of the harmonic circle, 0 when
    they are spread so evenly that the arrows cancel.
    """
    n = len(longitudes)
    if n == 0:
        return 0.0
    return amplitude(longitudes, h) / float(n)


def flower(longitudes, harmonics=HARMONICS):
    """The Harmonic Flower: one petal per harmonic.

    Each entry is a dict with the harmonic, its concentration index
    (0..1), the raw amplitude and the phase. Sorted by harmonic, not by
    strength, so the shape can be drawn directly.
    """
    return [{'harmonic': h,
             'concentration': concentration(longitudes, h),
             'amplitude': amplitude(longitudes, h),
             'phase': phase(longitudes, h)}
            for h in harmonics]


def dominant(longitudes, harmonics=HARMONICS):
    """The harmonic the chart gathers in most tightly."""
    petals = flower(longitudes, harmonics)
    return max(petals, key=lambda p: p['concentration'])['harmonic']
