"""Annual profections: the year's ruler, read off the atacir C-12.

Profecting is the atacir of cycle 12 seen a different way. That atacir turns
the chart 30 degrees a year, which is one whole sign, so at each birthday
the Ascendant has stepped into the next sign and the first house has moved
on to the next. The lord of that sign rules the year.

Nothing here recomputes the rotation: `openastromod.atacir` already does it,
and this module only names what the rotation lands on. Which is the point of
having built the generic engine first -- profections cost a lookup table,
not a second implementation.

    age 0   Ascendant's own sign     1st house    lord = ruler of that sign
    age 1   the next sign            2nd house
    ...
    age 12  back to the start        1st house

Because the step is exactly one sign, the year's lord depends only on the
natal Ascendant and the age: no ephemeris is consulted.
"""

from datetime import datetime

#Domicile rulership, shared with the lots rather than copied: one table for
#the whole program, so the two can never disagree.
from .arabicparts import DOMICILE

SIGNS_PER_CYCLE = 12


def sign_of(longitude):
    """Zodiac sign index of a longitude, Aries = 0."""
    return int(float(longitude) % 360.0 // 30.0) % 12


def profected_sign(natal_asc, age):
    """Sign the Ascendant has profected to at a given age."""
    return (sign_of(natal_asc) + int(age)) % SIGNS_PER_CYCLE


def profected_house(age):
    """House the year falls on, 1..12. Age 0 is the first house."""
    return (int(age) % SIGNS_PER_CYCLE) + 1


def lord_of(natal_asc, age):
    """Planet ruling the year, as an OpenAstro planet index."""
    return DOMICILE[profected_sign(natal_asc, age)]


def _anniversary(birth, age):
    """The birthday `age` years on.

    A 29 February birth has no anniversary in a common year; it is kept at
    the 28th rather than spilling into March.
    """
    try:
        return birth.replace(year=birth.year + int(age))
    except ValueError:
        return birth.replace(year=birth.year + int(age), day=28)


def table(birth, natal_asc, upto=90):
    """The profection years from birth to `upto`.

    `birth` is a date or datetime, `natal_asc` the natal Ascendant in
    degrees. Each entry is a dict:

        age     completed years at the start of the year
        start   the birthday that opens it
        end     the birthday that closes it, exclusive
        sign    profected sign index, Aries = 0
        house   profected house, 1..12
        lord    planet index ruling the year
    """
    if isinstance(birth, datetime):
        start = birth.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start = datetime(birth.year, birth.month, birth.day)

    out = []
    for age in range(int(upto) + 1):
        out.append({
            'age': age,
            'start': _anniversary(start, age),
            'end': _anniversary(start, age + 1),
            'sign': profected_sign(natal_asc, age),
            'house': profected_house(age),
            'lord': lord_of(natal_asc, age),
        })
    return out


def current_age(birth, when):
    """Completed years between two dates, by birthday, or None if before."""
    if isinstance(birth, datetime):
        b = birth
    else:
        b = datetime(birth.year, birth.month, birth.day)
    if when < b:
        return None
    age = when.year - b.year
    if (when.month, when.day) < (b.month, b.day):
        age -= 1
    return age
