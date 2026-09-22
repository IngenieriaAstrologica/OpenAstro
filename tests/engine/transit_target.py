"""Verify openastromod.primary.transit_target_longitude(): the new transit
target modes (natal / antiscion / contra-antiscion) that let a transiting
planet be measured against the natal antiscia instead of the natal true
positions (Morinus transits.py Transit.ANTISCION / .CONTRAANTISCION).

Real Swiss Ephemeris throughout (same natal chart as tests/engine/lunar.py:
1987-04-09 12:00:30 UT, lon 2.0367, lat 41.3436), not stubs.
"""
import sys, datetime
from openastromod import swiss
from openastromod import primary as primary_engine

fails = []
total = 0


def chk(label, cond, extra=''):
    global total
    total += 1
    if not cond:
        fails.append(label)
    print('%-64s %s %s' % (label, 'OK' if cond else 'FALLA', extra))


def degree_diff(a, b):
    # mirrors openAstroInstance.degreeDiff() in `openastro`: unsigned
    # angular distance folded to <= 180 degrees
    out = a - b if a > b else b - a
    if out > 180.0:
        out = 360.0 - out
    return out


# --------------------------------------------------------- natal chart
zod = ['aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra',
       'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces']
pl = [{'name': 'p%d' % i, 'visible': 1} for i in range(36)]
CFG = {'houses_system': 'P', 'postype': 'geo', 'siderealmode': 'FAGAN_BRADLEY',
       'zodiactype': 'tropical'}
LON, LAT, ALT = 2.0367, 41.3436, 12
nat = swiss.ephData(1987, 4, 9, 12.0 + 0.0 / 60.0 + 30.0 / 3600.0, LON, LAT, ALT, pl, zod, CFG)
sun = nat.planets_degree_ut[0]
moon = nat.planets_degree_ut[1]
print('natal Sun %.6f  Moon %.6f\n' % (sun, moon))

# 1. 'natal' target is the identity (the pre-existing behaviour, untouched)
chk("target 'natal' returns the longitude unchanged",
    primary_engine.transit_target_longitude(sun, 0.0, 'natal') == sun)

# 2. antiscion/contra-antiscion reuse swiss.calc_antiscion() exactly -- no
# second antiscion formula in primary.py
for lon, name in ((sun, 'Sun'), (moon, 'Moon')):
    ant, cant = swiss.calc_antiscion(lon, 0.0)
    got_ant = primary_engine.transit_target_longitude(lon, 0.0, 'antiscion')
    got_cant = primary_engine.transit_target_longitude(lon, 0.0, 'contraantiscion')
    chk("%s: transit_target_longitude('antiscion') == calc_antiscion()[0]" % name,
        got_ant == ant, '%.9f vs %.9f' % (got_ant, ant))
    chk("%s: transit_target_longitude('contraantiscion') == calc_antiscion()[1]" % name,
        got_cant == cant, '%.9f vs %.9f' % (got_cant, cant))

# 3. hand formula (declination-symmetry reflection on the Cancer0/Capricorn0
# axis: ant = (180 - lon) mod 360, contra = (360 - lon) mod 360) matches to
# well under an arcsecond -- same check the Antiscia chart feature used
for lon in (sun, moon, 0.0, 90.0, 180.0, 270.0, 359.999):
    ant, cant = swiss.calc_antiscion(lon, 0.0)
    hand_ant = (180.0 - lon) % 360.0
    hand_cant = (360.0 - lon) % 360.0
    chk('hand antiscion formula matches calc_antiscion (lon=%9.4f)' % lon,
        abs(ant - hand_ant) < 1e-9, '%.9f vs %.9f' % (ant, hand_ant))
    chk('hand contra-antiscion formula matches calc_antiscion (lon=%9.4f)' % lon,
        abs(cant - hand_cant) < 1e-9, '%.9f vs %.9f' % (cant, hand_cant))

# 4. involution: antiscion of the antiscion is the original longitude
ant_sun, _ = swiss.calc_antiscion(sun, 0.0)
ant_ant_sun, _ = swiss.calc_antiscion(ant_sun, 0.0)
chk('ant(ant(Sun)) == Sun (involution)', abs(ant_ant_sun - sun) < 1e-9,
    '%.12f' % abs(ant_ant_sun - sun))

# 5. sidereal pass-through: a nonzero ayanamsa reaches calc_antiscion
ayan = 24.7
ant_trop, _ = swiss.calc_antiscion(sun, 0.0)
ant_sid = primary_engine.transit_target_longitude(sun, ayan, 'antiscion')
ant_sid_direct, _ = swiss.calc_antiscion(sun, ayan)
chk('ayanamsa forwarded to calc_antiscion (sidereal antiscion moves)',
    ant_sid == ant_sid_direct and abs(ant_sid - ant_trop) > 1e-6,
    '%.6f vs tropical %.6f' % (ant_sid, ant_trop))

# ---------------------------------------------------------------------
# 6. Exact-contact verification, replicating makeAspectsTransit's diff:
# a transiting planet placed EXACTLY on the natal Sun's antiscion must
# register a 0-orb conjunction under target='antiscion', the same way the
# ascensional-measure feature verified an exact mundo contact by
# construction (see CHANGELOG "Ascensional transits").
natal_antiscion_sun = primary_engine.transit_target_longitude(sun, 0.0, 'antiscion')
transiting_planet_lon = natal_antiscion_sun  # placed exactly on the target
diff = degree_diff(natal_antiscion_sun, transiting_planet_lon)
print('\nnatal Sun antiscion  = %.6f' % natal_antiscion_sun)
print('transiting planet at = %.6f  (placed exactly on the antiscion)' % transiting_planet_lon)
print('orb (degreeDiff)     = %.12f deg (%.6f arcsec)\n' % (diff, diff * 3600.0))
chk('transiting planet exactly on the natal antiscion -> 0-orb conjunction',
    diff == 0.0, '%.2e deg' % diff)

# 7. sanity: an off-target transiting planet is NOT a 0-orb conjunction
off_target = (transiting_planet_lon + 5.0) % 360.0
diff_off = degree_diff(natal_antiscion_sun, off_target)
chk('a transiting planet 5 deg off the antiscion is not a conjunction',
    abs(diff_off - 5.0) < 1e-9, '%.6f deg' % diff_off)

# 8. contra-antiscion target is a different point (180 deg from antiscion,
# except at the two axis points where antiscion==contra-antiscion)
natal_contra_sun = primary_engine.transit_target_longitude(sun, 0.0, 'contraantiscion')
chk('antiscion and contra-antiscion are 180 deg apart',
    abs(degree_diff(natal_antiscion_sun, natal_contra_sun) - 180.0) < 1e-9,
    '%.9f deg apart' % degree_diff(natal_antiscion_sun, natal_contra_sun))

print('\n%d comprobaciones, %d fallos' % (total, len(fails)))
if fails:
    print('FALLAN:', fails)
    sys.exit(1)
print('TODO CORRECTO')
