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
"""
    Mundane astrology's calendar: ingresses, lunations, eclipses.

    A search over a date range that returns a table of dated events, not a
    chart -- the three techniques carta-natal.es separates into
    /estaciones.php (ingresses), /lunaciones.php (lunations) and
    /eclipses.php (eclipses). All three answer the same question -- "what
    happens, and exactly when" -- so they share one search module and one
    table in the UI.

    Every date this module returns comes from a Swiss Ephemeris solver built
    for the purpose, not from a day-by-day scan:

    * **Ingresses** -- `swe.solcross_ut()` / `swe.mooncross_ut()` give the
      exact instant a body crosses a *chosen* ecliptic longitude. Walking
      the twelve 30-degree cusps forward from the start of the range turns
      that into "every sign ingress in [start, end]" with one exact solver
      call per event -- no scanning, no missed cusp.
    * **Lunations** -- new and full moon are the instants the Sun-Moon
      angular separation is 0 or 180 degrees. pyswisseph has no `syzygy_ut`
      of its own (checked the installed build: the `cross` family only
      covers one body against a *fixed* target, and the Sun-Moon target
      moves), so this is the one place the module root-finds by hand -- but
      it is still a solver, not a scan: the relative motion of Moon minus
      Sun is always positive (the Moon's slowest apparent speed, ~11.8
      deg/day, is always faster than the Sun's fastest, ~1.02 deg/day), so
      the phase angle is monotonic and Newton's method on it converges in a
      handful of iterations to sub-second precision. Morinus' own
      `syzygy.py` solves the same problem by repeated hour/minute/second
      bisection (`getDateHour` / `getDateMinute` / `getDateSecond`); Newton
      on the actual angular rate reaches the same answer in far fewer
      steps because it uses the speed Swiss Ephemeris already hands back
      with `FLG_SPEED`, instead of halving a fixed step.
    * **Eclipses** -- `swe.sol_eclipse_when_glob()` and
      `swe.lun_eclipse_when()` are Swiss Ephemeris' own forward search,
      global (not tied to an observer), returning the exact time of
      greatest eclipse and its type in one call.

    Scope, deliberately:

    * Ingresses default to the **Sun** (the "estaciones"/equinox-and-
      solstice sense carta-natal.es and most mundane calendars mean by the
      word) with the **Moon** offered as an opt-in -- pyswisseph's `cross`
      family only reaches Sun and Moon directly (no generic planet-crossing
      solver in the installed build), and a year of Moon ingresses alone is
      already ~150 rows, so it is opt-in rather than default.
    * Eclipses are the **global** existence and type of the event
      (`_glob`/plain `lun_eclipse_when`), not whether it is visible from any
      particular place -- `sol_eclipse_when_loc` exists for that and is a
      different, location-bound question this table does not ask.
"""
import datetime

import swisseph as swe

from openastromod.swiss import ephe_path

# Same body numbers in Swiss Ephemeris and in OpenAstro's planet list.
SUN = 0
MOON = 1

ZODIAC = ('aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra',
    'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces')

IFLAG = swe.FLG_SWIEPH + swe.FLG_SPEED

# Solar eclipse type, most specific first -- ECL_ANNULAR_TOTAL (hybrid) has
# both the ECL_ANNULAR and ECL_TOTAL bits set in some pyswisseph builds, so
# it must be tested before either.
_SOL_ECLIPSE_TYPES = (
    (swe.ECL_ANNULAR_TOTAL, 'hybrid'),
    (swe.ECL_TOTAL, 'total'),
    (swe.ECL_ANNULAR, 'annular'),
    (swe.ECL_PARTIAL, 'partial'),
)

_LUN_ECLIPSE_TYPES = (
    (swe.ECL_TOTAL, 'total'),
    (swe.ECL_PARTIAL, 'partial'),
    (swe.ECL_PENUMBRAL, 'penumbral'),
)

# Safety caps on the event loops below: a date range fat-fingered by three
# orders of magnitude should raise, not hang the dialog. 6000 covers ~35
# years of Moon ingresses (the densest of the four searches, ~1 every 2.3
# days) with headroom; the UI dialog keeps well under that (see openastro).
_MAX_EVENTS = 6000


def _ephe():
    """Point the shared swisseph module at this project's ephemeris files.

    Mirrors `openastromod.swiss.cyclic_longitudes`: called at the top of
    every public function here, so this module never depends on some other
    call having run first.
    """
    swe.set_ephe_path(ephe_path)


def to_jd(dt):
    """A naive UTC `datetime.datetime` to a Julian day number (UT)."""
    hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0 + dt.microsecond / 3.6e9
    return swe.julday(dt.year, dt.month, dt.day, hour)


def to_datetime(jd_ut):
    """A Julian day number (UT) back to a naive UTC `datetime.datetime`.

    Same idiom as `openastromod.swiss.years_diff`: `revjul` gives a
    fractional hour, and `timedelta` absorbs the carry into day/month/year
    correctly instead of hand-rolling it.
    """
    y, m, d, hourf = swe.revjul(float(jd_ut), swe.GREG_CAL)
    return datetime.datetime(int(y), int(m), int(d)) + datetime.timedelta(hours=hourf)


def sign_of(lon):
    """Ecliptic longitude (degrees) to zodiac sign index, 0=Aries..11=Pisces."""
    return int(float(lon) % 360.0 // 30.0) % 12


# ---------------------------------------------------------------- ingresses

def _ingresses(cross_fn, body, jd_start, jd_end):
    events = []
    lon0 = swe.calc_ut(jd_start, body, IFLAG)[0][0] % 360.0
    target = (int(lon0 // 30.0) + 1) * 30.0 % 360.0
    jd = jd_start
    for _ in range(_MAX_EVENTS):
        jd = cross_fn(target, jd, IFLAG)
        if jd > jd_end:
            break
        events.append({'date': to_datetime(jd), 'planet': body,
            'sign': int(round(target / 30.0)) % 12})
        target = (target + 30.0) % 360.0
    else:
        raise ValueError('too many ingresses in range (capped at %d)' % (_MAX_EVENTS,))
    return events


def solar_ingresses(dt_start, dt_end):
    """The Sun's twelve sign ingresses in [dt_start, dt_end].

    Each entry: {'date': datetime (UTC), 'planet': 0, 'sign': 0..11}. Exact
    to the precision `swe.solcross_ut` supports -- see the module docstring.
    """
    _ephe()
    return _ingresses(swe.solcross_ut, SUN, to_jd(dt_start), to_jd(dt_end))


def lunar_ingresses(dt_start, dt_end):
    """The Moon's sign ingresses in [dt_start, dt_end] -- opt-in, see module docstring.

    Same shape as `solar_ingresses`, 'planet': 1. About one every 2.3 days,
    so a year is roughly 150 rows.
    """
    _ephe()
    return _ingresses(swe.mooncross_ut, MOON, to_jd(dt_start), to_jd(dt_end))


# ---------------------------------------------------------------- lunations

def _phase_and_rate(jd):
    sun = swe.calc_ut(jd, SUN, IFLAG)[0]
    moon = swe.calc_ut(jd, MOON, IFLAG)[0]
    diff = (moon[0] - sun[0]) % 360.0
    rate = moon[3] - sun[3]  # deg/day; always positive, see module docstring
    return diff, rate, moon[0]


def _next_syzygy(jd_from, target):
    """The next instant at or after `jd_from` where Sun-Moon longitude
    difference equals `target` (0 = new moon, 180 = full moon).

    Newton's method on the phase angle: the relative speed Swiss Ephemeris
    already returns (`FLG_SPEED`) makes each step close almost all of the
    remaining error, so a handful of iterations reaches sub-second
    precision. See the module docstring for why the phase is monotonic and
    a solver applies here at all.
    """
    diff, rate, _ = _phase_and_rate(jd_from)
    delta = (target - diff) % 360.0
    if delta < 1e-9:
        delta = 360.0
    jd = jd_from + delta / rate
    for _ in range(20):
        diff, rate, moon_lon = _phase_and_rate(jd)
        err = ((diff - target + 180.0) % 360.0) - 180.0
        step = err / rate
        jd -= step
        if abs(step) < 1e-8:  # ~1 ms
            break
    _, _, moon_lon = _phase_and_rate(jd)
    return jd, moon_lon


def lunations(dt_start, dt_end):
    """New and full moons in [dt_start, dt_end].

    Each entry: {'date': datetime (UTC), 'kind': 'new'/'full',
    'longitude': Moon's ecliptic longitude at exact syzygy, 'sign': 0..11}.
    """
    _ephe()
    jd_start, jd_end = to_jd(dt_start), to_jd(dt_end)
    events = []
    jd = jd_start
    for _ in range(_MAX_EVENTS):
        jd_new, lon_new = _next_syzygy(jd, 0.0)
        jd_full, lon_full = _next_syzygy(jd, 180.0)
        if jd_new <= jd_full:
            nxt, kind, lon = jd_new, 'new', lon_new
        else:
            nxt, kind, lon = jd_full, 'full', lon_full
        if nxt > jd_end:
            break
        events.append({'date': to_datetime(nxt), 'kind': kind,
            'longitude': lon % 360.0, 'sign': sign_of(lon)})
        # a real synodic half-month is never under ~14.6 days; stepping
        # forward by a third of a day cannot skip the next one nor
        # re-find the one just recorded
        jd = nxt + 0.3
    else:
        raise ValueError('too many lunations in range (capped at %d)' % (_MAX_EVENTS,))
    return events


# ----------------------------------------------------------------- eclipses

def solar_eclipses(dt_start, dt_end):
    """Global solar eclipses in [dt_start, dt_end].

    Each entry: {'date': datetime (UTC) of greatest eclipse, 'body': 'sun',
    'kind': 'total'/'annular'/'hybrid'/'partial'}.
    """
    _ephe()
    jd_end = to_jd(dt_end)
    jd = to_jd(dt_start)
    events = []
    for _ in range(_MAX_EVENTS):
        retflag, tret = swe.sol_eclipse_when_glob(jd, IFLAG, 0, False)
        tmax = tret[0]
        if tmax > jd_end:
            break
        kind = next((name for bit, name in _SOL_ECLIPSE_TYPES if retflag & bit), 'unknown')
        events.append({'date': to_datetime(tmax), 'body': 'sun', 'kind': kind})
        jd = tmax + 1.0  # solar eclipses are never under ~29 days apart
    else:
        raise ValueError('too many solar eclipses in range (capped at %d)' % (_MAX_EVENTS,))
    return events


def lunar_eclipses(dt_start, dt_end):
    """Global lunar eclipses in [dt_start, dt_end].

    Each entry: {'date': datetime (UTC) of greatest eclipse, 'body': 'moon',
    'kind': 'total'/'partial'/'penumbral'}.
    """
    _ephe()
    jd_end = to_jd(dt_end)
    jd = to_jd(dt_start)
    events = []
    for _ in range(_MAX_EVENTS):
        retflag, tret = swe.lun_eclipse_when(jd, IFLAG, 0, False)
        tmax = tret[0]
        if tmax > jd_end:
            break
        kind = next((name for bit, name in _LUN_ECLIPSE_TYPES if retflag & bit), 'unknown')
        events.append({'date': to_datetime(tmax), 'body': 'moon', 'kind': kind})
        jd = tmax + 1.0  # lunar eclipses are never under ~29 days apart
    else:
        raise ValueError('too many lunar eclipses in range (capped at %d)' % (_MAX_EVENTS,))
    return events


def search(dt_start, dt_end, categories=('ingress_sun', 'lunation', 'eclipse')):
    """Everything asked for in `categories`, as one list sorted by date.

    `categories` is any subset of 'ingress_sun', 'ingress_moon', 'lunation',
    'eclipse'. Every returned row carries 'date' and 'category' plus the
    fields native to its kind (see the individual functions above), so a
    caller can format them uniformly without knowing which search produced
    which row.
    """
    rows = []
    if 'ingress_sun' in categories:
        for e in solar_ingresses(dt_start, dt_end):
            e['category'] = 'ingress_sun'
            rows.append(e)
    if 'ingress_moon' in categories:
        for e in lunar_ingresses(dt_start, dt_end):
            e['category'] = 'ingress_moon'
            rows.append(e)
    if 'lunation' in categories:
        for e in lunations(dt_start, dt_end):
            e['category'] = 'lunation'
            rows.append(e)
    if 'eclipse' in categories:
        for e in solar_eclipses(dt_start, dt_end):
            e['category'] = 'eclipse'
            rows.append(e)
        for e in lunar_eclipses(dt_start, dt_end):
            e['category'] = 'eclipse'
            rows.append(e)
    rows.sort(key=lambda r: r['date'])
    return rows
