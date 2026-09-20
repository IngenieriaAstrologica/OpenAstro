"""Midpoints, and the 90-degree dial that reads them.

The midpoint of two bodies is the degree halfway between them. Every pair
has two such degrees, 180 apart; the one taken here is the near midpoint,
the one inside the shorter arc, which is the convention Morinus follows in
`midpoints.py`.

A midpoint matters when a third body sits on it, and the tradition counts
not only a conjunction but also a square or an opposition, since all three
put the body on the same axis. Reducing every longitude modulo 90 collapses
those three angles onto one point, so in the **90-degree dial** a single
proximity test finds all of them at once. That is what the dial is for, and
why the table is built on it.

Pure geometry: no ephemerides here, only longitudes handed in by the caller.

Not implemented: Morinus also offers the midpoint *with latitude*, after
Ruediger Plantiko -- the true midpoint of the great circle joining the two
bodies rather than of their projections on the ecliptic. It is a different
quantity, not a refinement of this one, and nothing else in OpenAstro works
in that space.
"""

DIAL = 90.0

#Contact orb in the dial, in degrees. Ebertin works tight; a degree and a
#half keeps the table readable without dropping real contacts.
DEFAULT_ORB = 1.5


def normalize(deg):
    """Fold an angle into [0, 360)."""
    return float(deg) % 360.0


def midpoint(lon_a, lon_b):
    """Near midpoint of two ecliptic longitudes, in [0, 360).

    Mirrors Morinus: the midpoint falls inside the shorter of the two arcs
    joining the bodies, so it is never the opposite degree.
    """
    a = normalize(lon_a)
    b = normalize(lon_b)
    d = abs(a - b)
    if d <= 180.0:
        return normalize(min(a, b) + d / 2.0)
    return normalize(max(a, b) + (360.0 - d) / 2.0)


def dial(lon, harmonic=DIAL):
    """Position on the N-degree dial."""
    return normalize(lon) % float(harmonic)


def dial_separation(lon_a, lon_b, harmonic=DIAL):
    """Shortest distance between two positions on the dial.

    The dial wraps at `harmonic`, so a body at 89 and one at 1 are two
    degrees apart, not eighty-eight.
    """
    h = float(harmonic)
    d = abs(dial(lon_a, h) - dial(lon_b, h)) % h
    return min(d, h - d)


def contacts(mid_lon, bodies, orb=DEFAULT_ORB, harmonic=DIAL):
    """Bodies sitting on a midpoint, read in the dial.

    `bodies` is a sequence of (key, longitude). Returns
    [(key, separation)] within `orb`, closest first. Because the test runs
    in the dial, a hit means conjunction, square or opposition in the
    360-degree chart -- all three place the body on the midpoint's axis.
    """
    out = []
    for key, lon in bodies:
        sep = dial_separation(mid_lon, lon, harmonic)
        if sep <= orb:
            out.append((key, sep))
    out.sort(key=lambda kv: kv[1])
    return out


def pairs(bodies):
    """All unordered pairs of the bodies, in the order given."""
    keys = list(bodies)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            yield keys[i], keys[j]


def tree(bodies, orb=DEFAULT_ORB, harmonic=DIAL, activated_only=False):
    """Midpoint tree: every pair, its midpoint and what activates it.

    `bodies` is a sequence of (key, longitude). Each entry of the result is
    a dict:

        a, b        the pair's keys
        lon         midpoint longitude in [0, 360)
        dial        its position on the dial
        contacts    [(key, separation)], the pair's own members excluded
                    because a body is trivially on its own midpoint's axis

    With `activated_only`, pairs nobody contacts are left out, which is
    what makes the table worth reading on a real chart.
    """
    items = list(bodies)
    out = []
    for (key_a, lon_a), (key_b, lon_b) in pairs(items):
        mid = midpoint(lon_a, lon_b)
        hits = [(k, s) for (k, s) in contacts(mid, items, orb, harmonic)
                if k != key_a and k != key_b]
        if activated_only and not hits:
            continue
        out.append({'a': key_a, 'b': key_b, 'lon': mid,
                    'dial': dial(mid, harmonic), 'contacts': hits})
    return out
