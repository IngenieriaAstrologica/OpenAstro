"""openastromod.mundane: ingresses, lunations, eclipses, checked two ways.

Each search gets one cross-check against a published value it could not have
been fitted to, and one structural invariant a broken search could not
accidentally satisfy (see tests/README.md and CLAUDE.md's "Verifying
astrology").
"""
import sys
import datetime

from openastromod import mundane as M

fails = []


def chk(label, ok, extra=''):
    if not ok:
        fails.append(label)
    print('%-64s %s %s' % (label, 'OK' if ok else 'FALLA', extra))


# ---- solar ingresses ------------------------------------------------------

# 2024 March equinox / June-Sept-Dec: NASA/USNO publish 2024 equinoxes and
# solstices; the commonly quoted UTC times are Mar 20 03:06, Jun 20 20:51,
# Sep 22 12:44, Dec 21 09:20. Cross-checked here against the March one,
# which is also the date this project's other verified figures use as a
# reference year.
ingresses_2024 = M.solar_ingresses(datetime.datetime(2024, 1, 1), datetime.datetime(2025, 1, 1))
by_sign = {e['sign']: e['date'] for e in ingresses_2024}
march_eq = by_sign[0]  # Aries
print('\n2024 Aries ingress (March equinox): %s UTC' % (march_eq,))
published = datetime.datetime(2024, 3, 20, 3, 6)
delta_s = abs((march_eq - published).total_seconds())
chk('2024 March equinox within 5 min of published 03:06 UTC', delta_s < 300, '%.1f s off' % delta_s)

# Structural: a 12-month window holds all twelve signs exactly once, in
# zodiac order, nothing skipped or doubled -- a search that missed a cusp or
# double-counted one could not pass this by accident.
signs_seen = [e['sign'] for e in ingresses_2024]
chk('2024: exactly 12 solar ingresses', len(ingresses_2024) == 12, str(len(ingresses_2024)))
chk('2024: the twelve signs, each once', sorted(signs_seen) == list(range(12)), str(sorted(signs_seen)))
chk('2024: in zodiac order (Aries..Pisces starting wherever Jan 1 sits)',
    signs_seen == sorted(signs_seen, key=lambda s: (s - signs_seen[0]) % 12), str(signs_seen))
gaps = [(ingresses_2024[i + 1]['date'] - ingresses_2024[i]['date']).total_seconds() / 86400.0
        for i in range(len(ingresses_2024) - 1)]
chk('2024: every ingress 27-32 days after the last (one sign a month)',
    all(27.0 < g < 32.0 for g in gaps), '%.2f..%.2f' % (min(gaps), max(gaps)))

# ---- lunations --------------------------------------------------------

# 2024-04-08's total solar eclipse happened at new moon; NASA's eclipse page
# gives the new moon (= greatest eclipse, essentially) at 2024-04-08 18:21
# UTC. Independent of the eclipse search below -- this comes from the
# syzygy root-finder, that one from swe_sol_eclipse_when_glob.
lu = M.lunations(datetime.datetime(2024, 4, 1), datetime.datetime(2024, 4, 15))
new_apr = next(e for e in lu if e['kind'] == 'new')
print('\n2024-04-08 new moon: %s UTC' % (new_apr['date'],))
published_nm = datetime.datetime(2024, 4, 8, 18, 21)
delta_s = abs((new_apr['date'] - published_nm).total_seconds())
chk('2024-04-08 new moon within 5 min of published 18:21 UTC', delta_s < 300, '%.1f s off' % delta_s)

# Structural: the true synodic month runs 29.27-29.83 days, never outside
# it -- consecutive new moons over several years must all fall in that
# window, or the root-finder is chasing the wrong crossing.
lu_5y = M.lunations(datetime.datetime(2022, 1, 1), datetime.datetime(2027, 1, 1))
news = [e['date'] for e in lu_5y if e['kind'] == 'new']
fulls = [e['date'] for e in lu_5y if e['kind'] == 'full']
new_gaps = [(news[i + 1] - news[i]).total_seconds() / 86400.0 for i in range(len(news) - 1)]
full_gaps = [(fulls[i + 1] - fulls[i]).total_seconds() / 86400.0 for i in range(len(fulls) - 1)]
print('2022-2027: %d new moons, %d full moons, synodic gap %.3f..%.3f days'
      % (len(news), len(fulls), min(new_gaps + full_gaps), max(new_gaps + full_gaps)))
chk('2022-2027: every new-to-new gap is 29.27-29.83 days',
    all(29.27 < g < 29.83 for g in new_gaps), '%.3f..%.3f' % (min(new_gaps), max(new_gaps)))
chk('2022-2027: every full-to-full gap is 29.27-29.83 days',
    all(29.27 < g < 29.83 for g in full_gaps), '%.3f..%.3f' % (min(full_gaps), max(full_gaps)))
chk('2022-2027: new and full alternate strictly',
    len(lu_5y) == len(news) + len(fulls) and
    all(lu_5y[i]['kind'] != lu_5y[i + 1]['kind'] for i in range(len(lu_5y) - 1)))
# Structural: at exact syzygy the Sun-Moon longitude difference is 0 or 180
# to within the Newton solver's own convergence, not just "close".
worst_new = 0.0
worst_full = 0.0
for e in lu_5y:
    swe_diff = None
    jd = M.to_jd(e['date'])
    diff, rate, _ = M._phase_and_rate(jd)
    err = diff if diff < 180.0 else 360.0 - diff
    if e['kind'] == 'new':
        worst_new = max(worst_new, min(diff, 360.0 - diff))
    else:
        worst_full = max(worst_full, abs(diff - 180.0))
print('worst Sun-Moon residual at "new": %.2e deg, at "full": %.2e deg' % (worst_new, worst_full))
chk('every "new" is Sun-Moon = 0 deg to 1e-5', worst_new < 1e-5, '%.2e' % worst_new)
chk('every "full" is Sun-Moon = 180 deg to 1e-5', worst_full < 1e-5, '%.2e' % worst_full)

# ---- eclipses -----------------------------------------------------------

# 2024-04-08: the "Great American Eclipse", a total solar eclipse. NASA's
# eclipse catalogue gives greatest eclipse at 18:17:21 UTC.
se = M.solar_eclipses(datetime.datetime(2024, 1, 1), datetime.datetime(2025, 1, 1))
total_apr = next(e for e in se if e['kind'] == 'total')
print('\n2024 total solar eclipse: %s UTC' % (total_apr['date'],))
published_ecl = datetime.datetime(2024, 4, 8, 18, 17, 21)
delta_s = abs((total_apr['date'] - published_ecl).total_seconds())
chk('2024 total solar eclipse within 2 min of NASA 18:17:21 UTC', delta_s < 120, '%.1f s off' % delta_s)

# 2025-09-07: a well-documented total lunar eclipse ("blood moon"),
# published greatest eclipse near 18:11 UTC.
le = M.lunar_eclipses(datetime.datetime(2025, 1, 1), datetime.datetime(2026, 1, 1))
total_sep = next(e for e in le if e['kind'] == 'total' and e['date'].month == 9)
print('2025 total lunar eclipse: %s UTC' % (total_sep['date'],))
published_lecl = datetime.datetime(2025, 9, 7, 18, 11)
delta_s = abs((total_sep['date'] - published_lecl).total_seconds())
chk('2025 total lunar eclipse within 5 min of published 18:11 UTC', delta_s < 300, '%.1f s off' % delta_s)

# Structural: solar eclipses only ever happen within a day or two of a new
# moon, lunar eclipses only within a day or two of a full moon -- true by
# the geometry of an eclipse, and a search that found the wrong event
# entirely (e.g. picked up noise, or confused solar/lunar) would violate it.
se_5y = M.solar_eclipses(datetime.datetime(2022, 1, 1), datetime.datetime(2027, 1, 1))
le_5y = M.lunar_eclipses(datetime.datetime(2022, 1, 1), datetime.datetime(2027, 1, 1))


def nearest_gap_days(dt, others):
    return min(abs((dt - o).total_seconds()) for o in others) / 86400.0


worst_se = max(nearest_gap_days(e['date'], news) for e in se_5y)
worst_le = max(nearest_gap_days(e['date'], fulls) for e in le_5y)
print('2022-2027: %d solar eclipses, worst distance from a new moon %.2f d' % (len(se_5y), worst_se))
print('2022-2027: %d lunar eclipses, worst distance from a full moon %.2f d' % (len(le_5y), worst_le))
chk('every solar eclipse is within 2 days of a new moon', worst_se < 2.0, '%.2f d' % worst_se)
chk('every lunar eclipse is within 2 days of a full moon', worst_le < 2.0, '%.2f d' % worst_le)
chk('solar eclipse kinds are all recognised', all(e['kind'] != 'unknown' for e in se_5y))
chk('lunar eclipse kinds are all recognised', all(e['kind'] != 'unknown' for e in le_5y))

# ---- combined search() ---------------------------------------------------

rows = M.search(datetime.datetime(2026, 1, 1), datetime.datetime(2027, 1, 1),
                 categories=('ingress_sun', 'lunation', 'eclipse'))
dates = [r['date'] for r in rows]
chk('search(): rows come back sorted by date', dates == sorted(dates), '')
chk('search(): every row is tagged with a category', all('category' in r for r in rows))
cats = set(r['category'] for r in rows)
chk('search(): all three requested categories present', cats == {'ingress_sun', 'lunation', 'eclipse'}, str(cats))

print('\n%d fallos' % len(fails))
sys.exit(1 if fails else 0)
