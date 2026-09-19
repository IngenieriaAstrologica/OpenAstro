"""Firdaria: the Persian chain of time lords, 75 years of planetary periods.

Each period hands rulership to a planet for a fixed number of years, and the
order depends on the sect of the chart. A diurnal nativity opens with the
Sun, a nocturnal one with the Moon. Every period except the nodes' divides
again into seven sub-periods of equal length, whose rulers follow the same
chain from the period's own lord.

Three orders are in use, all of them here:

    diurnal              Sun Venus Mercury Moon Saturn Jupiter Mars, then nodes
    nocturnal Al-Biruni  Moon Saturn Jupiter Mars Sun Venus Mercury, then nodes
    nocturnal Bonatti    as Al-Biruni but the nodes fall mid-chain, before
                         the Sun, instead of closing it

Reference: `Morinus SE/firdaria.py`. Pure calendar arithmetic -- no
ephemerides are consulted, so nothing here can drift; only the birth date
and the sect matter.
"""

from datetime import datetime, timedelta

#Rulers, in the order Morinus indexes them.
SATURN, JUPITER, MARS, SUN, VENUS, MERCURY, MOON, NORTH_NODE, SOUTH_NODE = range(9)

NODES = (NORTH_NODE, SOUTH_NODE)

#(ruler, years) in chain order. The years are the traditional ones and sum
#to 75 in all three orders.
DIURNAL = ((SUN, 10), (VENUS, 8), (MERCURY, 13), (MOON, 9), (SATURN, 11),
           (JUPITER, 12), (MARS, 7), (NORTH_NODE, 3), (SOUTH_NODE, 2))

NOCTURNAL_ALBIRUNI = ((MOON, 9), (SATURN, 11), (JUPITER, 12), (MARS, 7),
                      (SUN, 10), (VENUS, 8), (MERCURY, 13),
                      (NORTH_NODE, 3), (SOUTH_NODE, 2))

NOCTURNAL_BONATTI = ((MOON, 9), (SATURN, 11), (JUPITER, 12), (MARS, 7),
                     (NORTH_NODE, 3), (SOUTH_NODE, 2),
                     (SUN, 10), (VENUS, 8), (MERCURY, 13))

TOTAL_YEARS = 75
SUBPERIODS = 7

#How far past the 75-year chain to carry the table. Morinus shows three
#more periods, which reaches into the second turn of the chain.
EXTRA_PERIODS = 3


def sequence(day_chart, bonatti=False):
    """The chain for this sect. `bonatti` only affects nocturnal charts."""
    if day_chart:
        return DIURNAL
    return NOCTURNAL_BONATTI if bonatti else NOCTURNAL_ALBIRUNI


def node_slots(seq):
    """Positions in the chain held by a node.

    Taken from the chain itself rather than hardcoded: Bonatti puts the
    nodes at positions 4 and 5, the other two orders at 7 and 8.
    """
    return frozenset(i for i, (ruler, _years) in enumerate(seq) if ruler in NODES)


def next_slot(seq, slot, bonatti=False):
    """Chain position following `slot`, skipping the nodes.

    Sub-period rulers walk the chain but never land on a node. Bonatti's
    order resumes at the Sun after the nodes; the others wrap to the start.
    """
    nodes = node_slots(seq)
    slot += 1
    if slot > len(seq) - 1:
        return 0
    if slot in nodes:
        return 6 if bonatti else 0
    return slot


def _add_years(when, years):
    """Anniversary `years` after `when`.

    Firdaria periods run in calendar years, so the boundary falls on the
    birthday. A 29 February birth has no anniversary in a common year; it
    is kept at the 28th rather than spilling into March.
    """
    year = when.year + years
    try:
        return when.replace(year=year)
    except ValueError:
        return when.replace(year=year, day=28)


def periods(birth, day_chart, bonatti=False, extra=EXTRA_PERIODS):
    """The chain of firdaria for a birth date.

    `birth` is a date or datetime. Returns a list of dicts:

        ruler       planet id of the period lord
        years       length in calendar years
        start, end  datetimes, end exclusive
        is_node     nodes take no sub-periods
        sub         list of (ruler, start, end), empty for the nodes

    The list runs the full 75-year chain plus `extra` periods, so a long
    life stays covered.
    """
    if isinstance(birth, datetime):
        start = birth.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start = datetime(birth.year, birth.month, birth.day)

    seq = sequence(day_chart, bonatti)
    out = []
    for step in range(len(seq) + extra):
        slot = step % len(seq)
        ruler, years = seq[slot]
        end = _add_years(start, years)
        is_node = ruler in NODES

        sub = []
        if not is_node:
            span = (end - start).total_seconds() / float(SUBPERIODS)
            sub_slot = slot
            sub_start = start
            for _ in range(SUBPERIODS):
                sub_end = sub_start + timedelta(seconds=span)
                sub.append((seq[sub_slot][0], sub_start, sub_end))
                sub_start = sub_end
                sub_slot = next_slot(seq, sub_slot, bonatti)

        out.append({'ruler': ruler, 'years': years, 'start': start,
                    'end': end, 'is_node': is_node, 'sub': sub})
        start = end
    return out
