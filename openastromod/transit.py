#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    This file is part of openastro.org.

    OpenAstro.org is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenAstro.org is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with OpenAstro.org.  If not, see <http://www.gnu.org/licenses/>.
"""
"""Which instant of sky a transit wheel draws.

The transit chart itself needs no engine: the outer wheel is a plain
ephemeris reading, so the only question is *when*. This module answers it,
and answers it for the converse direction too.

    DIRECT     the sky of the requested moment.
    CONVERSE   the sky of the moment mirrored about the birth instant.

Why mirroring is the converse of a transit
------------------------------------------
Primary directions and atacires both run on an arc that is a linear
function of the time elapsed since birth (Naibod: 0.9856 deg per year;
atacir C-N: 360/N deg per year). "Converse" there means negating that arc,
which -- because the arc is linear in elapsed time -- is exactly the same
statement as negating the elapsed time itself.

A transit has no arc to negate: the outer positions are whatever the
ephemeris says, a nonlinear function of the instant. What survives the
generalisation is the parameter, not the formula: the signed displacement
from birth. So a converse transit is the sky at

    t_sky = t_birth - (t_requested - t_birth)

i.e. the heavens run backwards from the nativity at the same rate real time
runs forwards, which is the classical definition of converse motion. The
birth instant is the fixed point (at zero displacement both directions give
the natal sky), and t_birth is the exact midpoint of the direct and
converse moments -- the symmetry this module is tested on.

Note that only the instant is mirrored, never the place: the converse sky
is still read from where the chart is cast.

Stdlib only (datetime + zoneinfo); no ephemerides are consulted here, so
this arithmetic cannot drift against the Swiss Ephemeris.
"""

import datetime
from zoneinfo import ZoneInfo

#Direction of the transit: forwards from birth, or mirrored about it.
DIRECTION_KEYS = ("direct", "converse")

DIRECTION_TAGS = {"direct": "", "converse": ", converse"}


def valid_direction(direction, default="direct"):
    """Coerce user input into a usable direction key."""
    if direction in DIRECTION_KEYS:
        return direction
    return default


def local_to_utc(local_dt, tz_name):
    """Naive wall-clock time in a zone -> (naive UTC datetime, offset hours).

    fold=1 resolves the ambiguous hour of a DST fall-back to its second
    occurrence, matching what the chart dialogs did before this module.
    """
    aware = local_dt.replace(tzinfo=ZoneInfo(tz_name), fold=1)
    offset = aware.utcoffset()
    return aware.replace(tzinfo=None) - offset, offset.total_seconds() / 3600.0


def utc_to_local(utc_dt, tz_name):
    """Naive UTC datetime -> (naive local datetime, offset hours).

    The offset is the one in force at *that* instant, so a converse moment
    landing in another DST season -- or before the zone had DST at all --
    reports its own offset instead of the requested date's.
    """
    aware = utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(ZoneInfo(tz_name))
    return aware.replace(tzinfo=None), aware.utcoffset().total_seconds() / 3600.0


def converse_utc(birth_utc, target_utc):
    """Mirror a moment about the birth instant (both naive UTC).

    The elapsed time is negated, which leaves birth_utc as the midpoint of
    target_utc and the value returned.
    """
    return birth_utc - (target_utc - birth_utc)


def round_to_second(dt):
    """Nearest whole second.

    The chart keeps its hour as decimal hours built from h/m/s, so a mirrored
    instant carrying microseconds (the birth hour is a decimal) would lose
    almost a second to truncation. Rounding here keeps the worst case at half
    a second, which is below the resolution the wheels are drawn at.
    """
    if dt.microsecond >= 500000:
        dt = dt + datetime.timedelta(seconds=1)
    return dt.replace(microsecond=0)


def moment(local_dt, tz_name, birth_utc, converse=False):
    """Resolve a transit request into the instant to draw.

    local_dt   wall-clock time asked for in the dialog, in tz_name
    tz_name    IANA zone of the place the transit is read from
    birth_utc  birth instant as a naive UTC datetime (the mirror's pivot)
    converse   True mirrors the elapsed time about birth_utc

    Returns (sky_utc, sky_local, tz_offset_hours): the instant to feed the
    ephemeris, the same instant as local wall-clock time for labels, and
    that instant's UTC offset in hours.
    """
    target_utc, _offset = local_to_utc(local_dt, tz_name)
    sky_utc = round_to_second(converse_utc(birth_utc, target_utc)) if converse else target_utc
    sky_local, tz_offset = utc_to_local(sky_utc, tz_name)
    return sky_utc, sky_local, tz_offset
