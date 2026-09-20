"""Arabic parts (lots): a point measured off the Ascendant.

Every lot has the same shape. Two significators are taken, the arc from one
to the other is measured, and that arc is laid off from the Ascendant:

    lot = A + B - C

Most lots reverse B and C for a nocturnal nativity, which is what keeps the
Lot of Fortune on the Moon's side of the luminaries by day and the Sun's by
night. A handful never reverse; those carry `reverse=False`.

Terms are written as pairs so a formula can name any of four things:

    ('cusp', n)     the n-th house cusp, 1..12 -- ('cusp', 1) is the Asc
    ('planet', i)   a body, by its index in OpenAstro's planet list
    ('lot', name)   a lot computed earlier, so lots can build on lots
    ('lord', n)     the domicile ruler of the sign on the n-th cusp

The domicile table matches Morinus' `doms` in `arabicparts.py`, and its
implied planet order (Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn) is
exactly OpenAstro's indices 0-6, so no translation is needed.

Only lots whose formula is attested in the tradition without variants are
listed here. Several house lots circulate in more than one form depending
on the source; including them would mean picking a side silently, so they
are left out rather than guessed.
"""

#OpenAstro planet indices used by the formulas
SUN, MOON, MERCURY, VENUS, MARS, JUPITER, SATURN = range(7)

#Domicile ruler of each sign, Aries first, as a planet index. Same table
#Morinus uses.
DOMICILE = (MARS, VENUS, MERCURY, MOON, SUN, MERCURY,
            VENUS, MARS, JUPITER, SATURN, SATURN, JUPITER)


def normalize(deg):
    """Fold an angle into [0, 360)."""
    return float(deg) % 360.0


#(key, label, A, B, C, reverse at night)
#
#The Hermetic lots first, then the lots of the persons. Fortune and Spirit
#head the list because later lots are measured from them.
CATALOGUE = (
    ('fortune',   'Fortune',
     ('cusp', 1), ('planet', MOON), ('planet', SUN), True),
    ('spirit',    'Spirit',
     ('cusp', 1), ('planet', SUN), ('planet', MOON), True),
    ('eros',      'Eros',
     ('cusp', 1), ('planet', VENUS), ('lot', 'spirit'), True),
    ('necessity', 'Necessity',
     ('cusp', 1), ('planet', MERCURY), ('lot', 'fortune'), True),
    ('courage',   'Courage',
     ('cusp', 1), ('lot', 'fortune'), ('planet', MARS), True),
    ('victory',   'Victory',
     ('cusp', 1), ('planet', JUPITER), ('lot', 'spirit'), True),
    ('nemesis',   'Nemesis',
     ('cusp', 1), ('lot', 'fortune'), ('planet', SATURN), True),

    ('father',    'Father',
     ('cusp', 1), ('planet', SUN), ('planet', SATURN), True),
    ('mother',    'Mother',
     ('cusp', 1), ('planet', VENUS), ('planet', MOON), True),
    ('brothers',  'Brothers',
     ('cusp', 1), ('planet', JUPITER), ('planet', SATURN), True),
    ('children',  'Children',
     ('cusp', 1), ('planet', SATURN), ('planet', JUPITER), True),

    #These two are a pair: the same arc read from either luminary,
    #which is why each sex takes its own.
    ('marriage_m', 'Marriage (men)',
     ('cusp', 1), ('planet', VENUS), ('planet', SATURN), True),
    ('marriage_w', 'Marriage (women)',
     ('cusp', 1), ('planet', SATURN), ('planet', VENUS), True),

    ('illness',   'Illness',
     ('cusp', 1), ('planet', MARS), ('planet', SATURN), True),
    #Measured to the cusp of the eighth, not to a planet.
    ('death',     'Death',
     ('cusp', 8), ('planet', SATURN), ('planet', MOON), True),
    #The only one here built on a house ruler.
    ('travel',    'Travel',
     ('cusp', 1), ('cusp', 9), ('lord', 9), True),
)


def _term(term, cusps, planets, lots):
    """Longitude a formula term stands for, or None if unavailable."""
    kind, value = term
    try:
        if kind == 'cusp':
            return float(cusps[value - 1])
        if kind == 'planet':
            return float(planets[value])
        if kind == 'lot':
            got = lots.get(value)
            return None if got is None else float(got)
        if kind == 'lord':
            sign = int(normalize(cusps[value - 1]) // 30.0) % 12
            return float(planets[DOMICILE[sign]])
    except (IndexError, KeyError, TypeError, ValueError):
        return None
    return None


def compute(cusps, planets, day_chart, catalogue=CATALOGUE):
    """All lots of the catalogue for one chart.

    `cusps` is the twelve house cusps in order, `planets` the body
    longitudes indexed as OpenAstro indexes them. Returns a list of dicts
    with key, label, lon and the formula as resolved, in catalogue order so
    that lots built on Fortune and Spirit find them already computed.

    A lot whose formula cannot be resolved -- a missing body, say -- is
    skipped rather than silently placed at zero degrees.
    """
    lots = {}
    out = []
    for key, label, a, b, c, reverse in catalogue:
        #at night the two significators trade places
        first, second = (b, c) if (day_chart or not reverse) else (c, b)
        va = _term(a, cusps, planets, lots)
        vb = _term(first, cusps, planets, lots)
        vc = _term(second, cusps, planets, lots)
        if va is None or vb is None or vc is None:
            continue
        lon = normalize(va + vb - vc)
        lots[key] = lon
        out.append({'key': key, 'label': label, 'lon': lon,
                    'terms': (a, first, second), 'reversed': not day_chart and reverse})
    return out
