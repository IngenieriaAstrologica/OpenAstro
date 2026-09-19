"""Atacir engine: rigid rotation of the whole chart at 360/N degrees a year.

An atacir (Demetrio Santos' term for what Morinus calls a profection) turns
the entire radix -- bodies and cusps alike -- by a constant rate, so every
position keeps its distance to every other. The cycle N names the technique:
C-12 completes a turn in 12 years and so advances 30 degrees a year, C-360
advances 1 degree a year.

This makes three techniques one engine:

    C-12    30 deg/year   annual profections
    C-72     5 deg/year   the "5-degree atacir"
    C-360    1 deg/year   symbolic directions

Reference: `Morinus SE/profections.py`, whose K = 12.17473968 is days per
degree for C-12. That is TROPICAL_YEAR / (360/12) exactly, which is the
identity this module generalises:

    arc = days * (360 / N) / TROPICAL_YEAR

Note that `days * N / TROPICAL_YEAR` -- the shorthand that first appeared in
the project roadmap -- is NOT equivalent and does not reproduce Morinus: for
N=12 it gives a quarter of the correct rotation.

Pure arithmetic: no ephemerides are consulted, so an atacir cannot drift
against the Swiss Ephemeris. Only the birth instant and the target instant
matter, both as Julian days.
"""

import math

#Mean tropical year in days, matching Morinus' constant.
TROPICAL_YEAR = 365.2421904

#Cycles offered in the UI. Any positive N works; these are the traditional
#ones. C-12 is the reference cycle and the default.
CYCLES = (12, 24, 36, 72, 360)
DEFAULT_CYCLE = 12

#Monthly subdivision of a C-12 year (Morinus profectionsmonthly.py): twelve
#steps of a mean month, or thirteen of a lunar month. Kept here because the
#monthly table belongs to this family; not used by the wheel itself.
MONTH_STEP_12 = 30.4368492
MONTH_STEP_13 = 28.0955531


def degrees_per_year(cycle=DEFAULT_CYCLE):
    """Rotation rate of cycle N, in degrees per tropical year."""
    cycle = float(cycle)
    if cycle <= 0:
        raise ValueError("atacir cycle must be positive, got %r" % (cycle,))
    return 360.0 / cycle


def days_per_degree(cycle=DEFAULT_CYCLE):
    """Inverse rate. For C-12 this is Morinus' K = 12.17473968."""
    return TROPICAL_YEAR / degrees_per_year(cycle)


def arc_for_days(days, cycle=DEFAULT_CYCLE):
    """Total rotation for an elapsed span, in degrees.

    Not normalised: the whole turns carry the information of how many
    cycles have closed, and the sign carries direction (negative before
    birth, which is how a converse atacir is expressed).
    """
    return float(days) * degrees_per_year(cycle) / TROPICAL_YEAR


def arc_for_jds(jd_birth, jd_target, cycle=DEFAULT_CYCLE):
    """Total rotation between two Julian days."""
    return arc_for_days(float(jd_target) - float(jd_birth), cycle)


def normalize(degrees):
    """Fold an angle into [0, 360)."""
    return float(degrees) % 360.0


def turns(degrees):
    """Whole cycles closed by a total arc (negative before birth)."""
    return int(math.floor(float(degrees) / 360.0))


def rotate(longitudes, arc):
    """Apply the arc to a list of ecliptic longitudes.

    The rotation is rigid, so aspects among the rotated bodies are exactly
    the natal ones; what changes is their relation to the natal frame.
    """
    return [normalize(float(v) + arc) for v in longitudes]


def years_for_arc(arc, cycle=DEFAULT_CYCLE):
    """Elapsed tropical years that a given total arc represents."""
    return float(arc) / degrees_per_year(cycle)
