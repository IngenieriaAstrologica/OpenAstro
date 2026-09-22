"""Verify the draconic chart: the whole chart re-referenced to the Mean Node.

A draconic chart is the radix rotated rigidly so the Mean (North) Lunar
Node sits at 0deg -- draconic_lon = normalize(true_lon - mean_node_lon) --
applied to every body, angle and house cusp. This checks that transform
directly against a plain tropical chart for the same birth data, computed
by openastromod.swiss.ephData with astrocfg['zodiactype'] set to
'tropical' vs 'draconic'.
"""
import sys
from openastromod import swiss

zodiac = ['aries','taurus','gemini','cancer','leo','virgo','libra',
          'scorpio','sagittarius','capricorn','aquarius','pisces']
planets = [{'name': 'p%d' % i, 'visible': 1} for i in range(36)]

def cfg(zodiactype):
    return {'houses_system': 'P', 'postype': 'geo',
            'siderealmode': 'FAGAN_BRADLEY', 'zodiactype': zodiactype}

def normalize(lon):
    return lon % 360.0

# An invented birth: Barcelona, 1990-03-11 14:30 local (treated as UT here,
# same convention southnode.py already uses for engine-level checks).
YEAR, MONTH, DAY, HOUR = 1990, 3, 11, 14.5
GEOLON, GEOLAT, ALT = 2.1589, 41.3888, 12

trop = swiss.ephData(YEAR, MONTH, DAY, HOUR, GEOLON, GEOLAT, ALT, planets, zodiac, cfg('tropical'))
drac = swiss.ephData(YEAR, MONTH, DAY, HOUR, GEOLON, GEOLAT, ALT, planets, zodiac, cfg('draconic'))

mean_node = trop.planets_degree_ut[10]
print('tropical Mean Node longitude: %.6f' % mean_node)
print('draconic  Mean Node longitude: %.6f' % drac.planets_degree_ut[10])

# (1) the Mean Node itself lands at exactly 0d00' draconic, by construction
assert abs(drac.planets_degree_ut[10]) < 1e-9 or abs(drac.planets_degree_ut[10] - 360.0) < 1e-9, \
    'Mean Node did not land on 0 degrees in its own draconic chart'
assert drac.mean_node_longitude == mean_node, 'stored reference longitude does not match the tropical Mean Node'
assert drac.draconic_mode is True
assert trop.draconic_mode is False

# (2) every other body's draconic longitude equals
#     normalize(true_ecliptic_lon - mean_node_lon), to within numeric noise
labels = ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus',
          'Neptune','Pluto','Mean_Node','Mean_Apogee/Lilith','n12','Chiron',
          'n14','n15','n16','n17','n18','n19','n20','n21','n22']
maxerr = 0.0
for i in range(23):
    expected = normalize(trop.planets_degree_ut[i] - mean_node)
    got = drac.planets_degree_ut[i]
    diff = min(abs(got - expected), 360.0 - abs(got - expected))
    maxerr = max(maxerr, diff)
    label = labels[i] if i < len(labels) else 'body%d' % i
    print('%-20s trop=%9.5f  draconic=%9.5f  expected=%9.5f  diff=%.2e' % (label, trop.planets_degree_ut[i], got, expected, diff))
    assert diff < 1e-6, '%s draconic longitude does not match the rotation formula' % label

# angles and lots (indices 23..35: Asc, MC, Dsc, IC, fortune, spirit,
# south node, marriage pars, black sun, vulcanus, persephone, true lilith,
# lot of infortune) are covered by the same rotation
for i in range(23, 36):
    expected = normalize(trop.planets_degree_ut[i] - mean_node)
    got = drac.planets_degree_ut[i]
    diff = min(abs(got - expected), 360.0 - abs(got - expected))
    maxerr = max(maxerr, diff)
    assert diff < 1e-6, 'index %d (angle/lot) draconic longitude does not match the rotation formula' % i

# house cusps rotate the same way
for i in range(12):
    expected = normalize(trop.houses_degree_ut[i] - mean_node)
    got = drac.houses_degree_ut[i]
    diff = min(abs(got - expected), 360.0 - abs(got - expected))
    maxerr = max(maxerr, diff)
    assert diff < 1e-6, 'house cusp %d does not match the rotation formula' % i

print('max deviation from the rotation formula across bodies/angles/houses: %.3e degrees' % maxerr)

# sign/degree-in-sign must agree with the rotated longitude, not the stale
# tropical one
for i in range(36):
    lon = drac.planets_degree_ut[i]
    s = int(lon // 30.0) % 12
    assert drac.planets_sign[i] == s, 'planet %d sign not re-derived after rotation' % i
    assert abs(drac.planets_degree[i] - (lon - s * 30.0)) < 1e-9, 'planet %d degree-in-sign not re-derived' % i
for i in range(12):
    lon = drac.houses_degree_ut[i]
    s = int(lon // 30.0) % 12
    assert drac.houses_sign[i] == s, 'house %d sign not re-derived after rotation' % i

# aspects are frame-invariant: the angular separation between any two
# bodies must be unchanged by a rigid rotation
import itertools
for i, j in itertools.islice(itertools.combinations(range(23), 2), 0, 40):
    d_trop = (trop.planets_degree_ut[i] - trop.planets_degree_ut[j]) % 360.0
    d_drac = (drac.planets_degree_ut[i] - drac.planets_degree_ut[j]) % 360.0
    diff = min(abs(d_trop - d_drac), 360.0 - abs(d_trop - d_drac))
    assert diff < 1e-6, 'separation between bodies %d and %d changed under rotation (not rigid)' % (i, j)

# a second, independent birth (a documented date, different hemisphere)
# to make sure this is not a coincidence of one instant
for (y, m, d, h, lon, lat) in [(2000, 1, 1, 0.0, -0.1276, 51.5074),
                                (1969, 7, 20, 20.17, -95.0, 29.5)]:
    t2 = swiss.ephData(y, m, d, h, lon, lat, 0, planets, zodiac, cfg('tropical'))
    d2 = swiss.ephData(y, m, d, h, lon, lat, 0, planets, zodiac, cfg('draconic'))
    mn2 = t2.planets_degree_ut[10]
    assert abs(d2.planets_degree_ut[10]) < 1e-9 or abs(d2.planets_degree_ut[10] - 360.0) < 1e-9
    for i in range(36):
        expected = normalize(t2.planets_degree_ut[i] - mn2)
        got = d2.planets_degree_ut[i]
        diff = min(abs(got - expected), 360.0 - abs(got - expected))
        assert diff < 1e-6, '%04d-%02d-%02d body %d fails the rotation formula' % (y, m, d, i)
    for i in range(12):
        expected = normalize(t2.houses_degree_ut[i] - mn2)
        got = d2.houses_degree_ut[i]
        diff = min(abs(got - expected), 360.0 - abs(got - expected))
        assert diff < 1e-6, '%04d-%02d-%02d house %d fails the rotation formula' % (y, m, d, i)
    print('%04d-%02d-%02d ok, Mean Node was %.5f' % (y, m, d, mn2))

print('\nALL OK')
