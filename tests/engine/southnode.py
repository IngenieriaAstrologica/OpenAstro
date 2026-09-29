"""Verify the South Node (index 29) reports the North Node's retrogradation."""
import sys
from openastromod import swiss

zodiac = ['aries','taurus','gemini','cancer','leo','virgo','libra',
          'scorpio','sagittarius','capricorn','aquarius','pisces']
planets = [{'name': 'p%d' % i, 'visible': 1} for i in range(36)]
cfg = {'houses_system': 'P', 'postype': 'geo',
       'siderealmode': 'FAGAN_BRADLEY', 'zodiactype': 'tropical'}

# Barcelona, a few dates spread across the year
for (y, m, d) in [(2026,9,18), (2026,1,5), (2025,6,22), (1990,3,11)]:
    e = swiss.ephData(y, m, d, 12.0, 2.1589, 41.3888, 12, planets, zodiac, cfg)
    n_lon, s_lon = e.planets_degree_ut[10], e.planets_degree_ut[29]
    sep = (s_lon - n_lon) % 360.0
    print('%04d-%02d-%02d  node %8.4f  south %8.4f  sep %7.3f' % (y, m, d, n_lon, s_lon, sep))
    print('              north: speed %+.6f retro=%s stat=%s' % (
        e.planets_speed[10], e.planets_retrograde[10], e.planets_stationary[10]))
    print('              south: speed %+.6f retro=%s stat=%s' % (
        e.planets_speed[29], e.planets_retrograde[29], e.planets_stationary[29]))
    assert abs(sep - 180.0) < 1e-6, 'south node is not opposite the north node'
    assert e.planets_retrograde[29] == e.planets_retrograde[10], 'motion not inherited'
    assert e.planets_speed[29] == e.planets_speed[10], 'speed not inherited'
    assert e.planets_retrograde[29] is True, 'mean node should be retrograde'

# the mark the wheel and grid actually print
def motion_mark(i, retro, stat):
    if i < len(stat) and stat[i]: return 'S'
    if i < len(retro) and retro[i]: return 'R'
    return ''

e = swiss.ephData(2026, 9, 18, 12.0, 2.1589, 41.3888, 12, planets, zodiac, cfg)
for i, label in ((10, 'North Node'), (29, 'South Node'), (0, 'Sun'), (1, 'Moon'),
                 (27, 'Lot of Fortune'), (35, 'Lot of Infortune')):
    print('mark for %-16s -> %r' % (label, motion_mark(i, e.planets_retrograde, e.planets_stationary)))
assert motion_mark(29, e.planets_retrograde, e.planets_stationary) == 'R'
assert motion_mark(27, e.planets_retrograde, e.planets_stationary) == ''
assert motion_mark(0, e.planets_retrograde, e.planets_stationary) == ''
print('\nALL OK')
