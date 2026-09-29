"""Independent oracle for openastromod.munprofection.

Morinus' own `munprofections.py` / `planets.py` cannot be imported and run
here as a live oracle: `astrology.py` wraps a bespoke compiled extension
(`sweastrology`), not the pip `pyswisseph` this project uses, and that
extension is not installed in this environment. So this file is the by-hand
port the task asked for instead -- every formula in `mun_profections`,
`compute_placidian_speculum`, `iterate` and `calc_mundane_prof_pos` below is
retyped a second time, independently, straight from the Morinus source
(`Morinus SE/munprofections.py`, `Morinus SE/planets.py` lines ~95-252 and
~491-606), using only pyswisseph -- none of it calls into
`openastromod.munprofection`, which is only imported at the bottom to be
checked against this oracle.
"""
import math
import sys

import swisseph as swe

from openastromod import munprofection as M
from openastromod import swiss

swe.set_ephe_path(swiss.ephe_path)

ok = lambda c: 'OK' if c else 'FALLA'
fails = []
total = 0
def check(label, cond, extra=''):
	global total
	total += 1
	if not cond: fails.append(label)
	print('%-70s %s %s' % (label, ok(cond), extra))

TROPICAL_YEAR = 365.2421904


def norm(x):
	return x % 360.0


# --------------------------------------------------------------- the oracle
# Hand-ported a second time from Morinus, independently of
# openastromod.munprofection (which is only ever called below the line that
# says "production code starts here").

def mun_profections(natal_ramc, natal_asc_decl, place_lat, place_lon, jd_target, jd_birth):
	"""munprofections.MunProfections.__init__"""
	val = math.tan(math.radians(natal_asc_decl)) * math.tan(math.radians(place_lat))
	adlatAsc = 0.0
	if math.fabs(val) <= 1.0:
		adlatAsc = math.degrees(math.asin(val))
	dsalatAsc = 90.0 + adlatAsc
	nsalatAsc = 90.0 - adlatAsc
	dhlatAsc = dsalatAsc / 3.0
	nhlatAsc = nsalatAsc / 3.0

	lon360 = place_lon
	if place_lon < 0.0:
		lon360 = 360.0 + place_lon

	diffYear = (jd_target - jd_birth) / TROPICAL_YEAR
	cycInYears = diffYear - int(diffYear / 12.0) * 12.0
	DCycInYears = cycInYears
	if cycInYears > 6.0:
		DCycInYears = 6.0
	NCycInYears = 0.0
	if cycInYears > 6.0:
		NCycInYears = cycInYears - DCycInYears
	diffLon = DCycInYears * dhlatAsc + NCycInYears * nhlatAsc
	lon360Z = norm(lon360 + diffLon)
	lonZ = lon360Z
	east = True
	if lon360Z > 180.0:
		lonZ = 360.0 - lon360Z
		east = False
	return lonZ, east, diffLon, cycInYears


def compute_placidian_speculum(lon, lat, ra, decl, ramc, placelat):
	"""planets.Planet.computePlacidianSpeculum"""
	raic = ramc + 180.0
	if raic > 360.0:
		raic -= 360.0

	eastern = True
	if ramc > raic:
		if ra > raic and ra < ramc:
			eastern = False
	else:
		if (ra > raic and ra < 360.0) or (ra < ramc and ra > 0.0):
			eastern = False

	adlat = 0.0
	val = math.tan(math.radians(placelat)) * math.tan(math.radians(decl))
	if math.fabs(val) <= 1.0:
		adlat = math.degrees(math.asin(val))

	med = math.fabs(ramc - ra)
	if med > 180.0:
		med = 360.0 - med
	icd = math.fabs(raic - ra)
	if icd > 180.0:
		icd = 360.0 - icd

	md = med

	aoasc = ramc + 90.0
	if aoasc >= 360.0:
		aoasc -= 360.0
	dodesc = raic + 90.0
	if dodesc >= 360.0:
		dodesc -= 360.0

	aohd = ra - adlat
	hdasc = aohd - aoasc
	if hdasc < 0.0:
		hdasc *= -1
	if hdasc > 180.0:
		hdasc = 360.0 - hdasc

	dohd = ra + adlat
	hddesc = dohd - dodesc
	if hddesc < 0.0:
		hddesc *= -1
	if hddesc > 180.0:
		hddesc = 360.0 - hddesc

	hd = hdasc
	if hddesc < hdasc:
		hd = hddesc
		hd *= -1

	dsa = 90.0 + adlat
	nsa = 90.0 - adlat

	abovehorizon = True
	if med > dsa:
		abovehorizon = False

	sa = dsa
	if not abovehorizon:
		sa = -nsa
		md = icd
		md *= -1

	th = sa / 6.0

	hod = 0.0
	if th != 0.0:
		hod = md / math.fabs(th)

	pmp = 0.0
	tmd = md
	if tmd < 0.0:
		tmd *= -1
	pmpsa = sa
	if pmpsa < 0.0:
		pmpsa *= -1

	if not abovehorizon and eastern:
		pmp = 90.0 - 90.0 * (tmd / pmpsa)
	elif not abovehorizon and not eastern:
		pmp = 90.0 + 90.0 * (tmd / pmpsa)
	elif abovehorizon and not eastern:
		pmp = 270.0 - 90.0 * (tmd / pmpsa)
	elif abovehorizon and eastern:
		pmp = 270.0 + 90.0 * (tmd / pmpsa)

	tval = math.fabs(sa)
	adphi = 0.0
	if tval != 0.0:
		adphi = math.fabs(tmd) * adlat / tval

	tval2 = math.tan(math.radians(decl))
	phi = 0.0
	if tval2 != 0.0:
		phi = math.degrees(math.atan(math.sin(math.radians(adphi)) / tval2))

	if eastern:
		ao = ra - adphi
	else:
		ao = ra + adphi
		ao *= -1

	return {'long': lon, 'lat': lat, 'ra': ra, 'decl': decl, 'adlat': adlat,
		'sa': sa, 'md': md, 'hd': hd, 'th': th, 'hod': hod, 'pmp': pmp,
		'adph': adphi, 'poh': phi, 'aodo': ao}


def iterate(pmp, rao, rdo, robl, rpoh, lon):
	"""planets.Planet.iterate"""
	okGa = okGd = True
	if pmp < 90.0 or (pmp >= 270.0 and pmp < 360.0):
		Ga = math.degrees(math.cos(rao) * math.cos(robl) - math.sin(robl) * math.tan(rpoh))
		if Ga != 0.0:
			Fa = math.degrees(math.atan(math.sin(rao) / (math.cos(rao) * math.cos(robl) - math.sin(robl) * math.tan(rpoh))))
			if Fa >= 0.0 and Ga > 0.0:
				lon = Fa
			elif Fa < 0.0 and Ga > 0.0:
				lon = Fa + 360.0
			elif Ga < 0.0:
				lon = Fa + 180.0
		else:
			okGa = False
	else:
		Gd = math.degrees(math.cos(rdo) * math.cos(robl) + math.sin(robl) * math.tan(rpoh))
		if Gd != 0.0:
			Fd = math.degrees(math.atan(math.sin(rdo) / (math.cos(rdo) * math.cos(robl) + math.sin(robl) * math.tan(rpoh))))
			if Fd >= 0.0 and Gd > 0.0:
				lon = Fd
			elif Fd < 0.0 and Gd > 0.0:
				lon = Fd + 360.0
			elif Gd < 0.0:
				lon = Fd + 180.0
		else:
			okGd = False
	return okGa, okGd, lon


def calc_mundane_prof_pos(spec, ramc, placelat, obl):
	"""planets.Planet.calcMundaneProfPos"""
	raic = ramc + 180.0
	if raic > 360.0:
		raic -= 360.0

	md = spec['md']
	if md < 0.0:
		md *= -1
	ra = spec['ra']

	if spec['pmp'] < 90.0:
		ra = raic - md
	elif spec['pmp'] >= 90.0 and spec['pmp'] < 180.0:
		ra = raic + md
	elif spec['pmp'] >= 180.0 and spec['pmp'] < 270.0:
		ra = ramc - md
	elif spec['pmp'] >= 270.0 and spec['pmp'] < 360.0:
		ra = ramc + md
	ra = norm(ra)

	ao = do = 0.0
	adph = math.fabs(spec['adph'])
	if placelat == 0.0 or spec['decl'] == 0.0:
		ao = do = ra
	if (placelat > 0.0 and spec['decl'] > 0.0) or (placelat < 0.0 and spec['decl'] < 0.0):
		ao = ra - adph
		do = ra + adph
	if (placelat > 0.0 and spec['decl'] < 0.0) or (placelat < 0.0 and spec['decl'] > 0.0):
		ao = ra + adph
		do = ra - adph

	ao = norm(ao)
	do = norm(do)

	poh = spec['poh']
	rao = math.radians(ao)
	rdo = math.radians(do)
	robl = math.radians(obl)
	rpoh = math.radians(poh)
	lon = spec['long']

	okGa, okGd, lon = iterate(spec['pmp'], rao, rdo, robl, rpoh, lon)
	if not okGa:
		lon1 = iterate(spec['pmp'], rao + math.radians(0.5), rdo, robl, rpoh, lon)[2]
		lon2 = iterate(spec['pmp'], rao - math.radians(0.5), rdo, robl, rpoh, lon)[2]
		lon = norm((lon1 + lon2) / 2)
	elif not okGd:
		lon1 = iterate(spec['pmp'], rao, rdo + math.radians(0.5), robl, rpoh, lon)[2]
		lon2 = iterate(spec['pmp'], rao, rdo - math.radians(0.5), robl, rpoh, lon)[2]
		lon = norm((lon1 + lon2) / 2)

	return lon


def houses_p(jd_ut, geolat, geolon):
	"""houses.Houses(..., hsys='P'): cusps, RAMC and Asc declination."""
	cusps, ascmc = swe.houses(jd_ut, geolat, geolon, b'P')
	obl = swe.calc_ut(jd_ut, swe.ECL_NUT, 0)[0][0]
	ascra, ascdecl, _ = swe.cotrans((ascmc[0], 0.0, 1.0), -obl)
	mcra, mcdecl, _ = swe.cotrans((ascmc[1], 0.0, 1.0), -obl)
	return {'cusps': cusps, 'ascmc': ascmc, 'obl': obl, 'ramc': mcra % 360.0,
		'asc_decl': ascdecl}


def ecl_to_equ(lon, lat, obl):
	ra, decl, _ = swe.cotrans((lon, lat, 1.0), -obl)
	return ra % 360.0, decl


# ------------------------------------------------------- the natal chart
# Same chart already exercised by tests/engine/lunar.py, reused here to
# stay inside data this suite already trusts.
YEAR, MONTH, DAY, HOUR = 1987, 4, 9, 12.0 + 30.0 / 60.0
LON, LAT, ALT = 2.0367, 41.3436, 12

jd_birth = swe.julday(YEAR, MONTH, DAY, HOUR)
nat_houses = houses_p(jd_birth, LAT, LON)
natal_ramc = nat_houses['ramc']
natal_asc_decl = nat_houses['asc_decl']
obl_birth = nat_houses['obl']

print('natal RAMC=%.6f  Asc decl=%.6f  obl=%.6f\n' % (natal_ramc, natal_asc_decl, obl_birth))

BODIES = {'Sun': swe.SUN, 'Moon': swe.MOON, 'Saturn': swe.SATURN}
natal_body = {}
for name, pid in BODIES.items():
	xx, _ = swe.calc_ut(jd_birth, pid, swe.FLG_SWIEPH)
	lon, lat = xx[0], xx[1]
	ra, decl = ecl_to_equ(lon, lat, obl_birth)
	natal_body[name] = {'lon': lon, 'lat': lat, 'ra': ra, 'decl': decl}
	print('natal %-6s lon=%9.5f lat=%8.5f ra=%9.5f decl=%8.5f' % (name, lon, lat, ra, decl))

# ------------------------------------------------------ cnt=0 is the radix
check('\nat cnt=0 diffLon is exactly 0 (production)',
	M.relocated_longitude(natal_ramc, natal_asc_decl, LAT, LON, 0.0)[1] == 0.0)
lonZ0, east0, diffLon0, cyc0 = mun_profections(natal_ramc, natal_asc_decl, LAT, LON, jd_birth, jd_birth)
check('at cnt=0 diffLon is exactly 0 (oracle)', diffLon0 == 0.0)
lon0, _, _ = M.relocated_longitude(natal_ramc, natal_asc_decl, LAT, LON, 0.0)
check('at cnt=0 the fictitious longitude is the radix longitude',
	abs(lon0 - LON) < 1e-9, '%.9f vs %.9f' % (lon0, LON))

print()

# ------------------------------------------------ several offsets, cross-checked
# 8, 20 and 45 land past the 6-year mark within their 12-year cycle
# (cycInYears = 8, 8, 9 respectively); 13 wraps into a second cycle just
# past it. -5 exercises the (unfolded, see module docstring) converse case
# with the same formula, not a claim that it is astrologically meaningful.
for cnt in (0, 3, 6, 8, 13, 20, 45, -5):
	jd_target = jd_birth + cnt * TROPICAL_YEAR

	lonZ, east, diffLon_o, cyc_o = mun_profections(natal_ramc, natal_asc_decl, LAT, LON, jd_target, jd_birth)
	lon_oracle = lonZ if east else -lonZ

	lon_prod, diffLon_p, cyc_p = M.relocated_longitude(natal_ramc, natal_asc_decl, LAT, LON, float(cnt))

	check('cnt=%-3d cycInYears matches (%.6f)' % (cnt, cyc_o), abs(cyc_o - cyc_p) < 1e-9)
	check('cnt=%-3d diffLon matches (%.6f deg)' % (cnt, diffLon_o), abs(diffLon_o - diffLon_p) < 1e-9)
	check('cnt=%-3d fictitious longitude matches (%.6f deg E)' % (cnt, lon_oracle),
		abs(((lon_oracle - lon_prod + 180.0) % 360.0) - 180.0) < 1e-9,
		'oracle=%.9f prod=%.9f' % (lon_oracle, lon_prod))

	# relocated Placidus houses, same UT instant, fictitious longitude
	reloc = houses_p(jd_birth, LAT, lon_prod)
	new_ramc = reloc['ramc']

	for name, b in natal_body.items():
		spec_o = compute_placidian_speculum(b['lon'], b['lat'], b['ra'], b['decl'], natal_ramc, LAT)
		lon_body_oracle = calc_mundane_prof_pos(spec_o, new_ramc, LAT, obl_birth)

		spec_p = M.placidian_speculum(b['lon'], b['lat'], b['ra'], b['decl'], natal_ramc, LAT)
		# field-by-field speculum agreement, not just the final longitude
		fields = ('md', 'pmp', 'adph', 'poh', 'sa', 'adlat')
		idx = {'md': M.MD, 'pmp': M.PMP, 'adph': M.ADPH, 'poh': M.POH, 'sa': M.SA, 'adlat': M.ADLAT}
		mism = [f for f in fields if abs(spec_o[f] - spec_p[idx[f]]) > 1e-9]
		check('cnt=%-3d %-6s natal speculum matches field by field' % (cnt, name),
			not mism, mism)

		lon_body_prod = M.mundane_reposition(spec_p, new_ramc, LAT, obl_birth)
		check('cnt=%-3d %-6s repositioned longitude matches (oracle %.6f)' % (cnt, name, lon_body_oracle),
			abs(((lon_body_oracle - lon_body_prod + 180.0) % 360.0) - 180.0) < 1e-6,
			'oracle=%.9f prod=%.9f' % (lon_body_oracle, lon_body_prod))

		if cnt == 0:
			# NOT the radix longitude, and this is Morinus' own behaviour,
			# not a bug in this port: `calcMundaneProfPos` is a single trig
			# solve (Morinus calls it `iterate` but it never actually
			# iterates/converges), built on the proportional
			# ("regula trium") approximation of a body's pole height from
			# MD/SA. That approximation is not an exact inverse of
			# `computePlacidianSpeculum`, so even at diffLon=0 -- new RAMC
			# equal to the natal RAMC -- round-tripping a real body through
			# the speculum and back can drift by close to a degree (Saturn
			# here: 261.09 natal vs 261.98 round-tripped). Both independent
			# transcriptions (this oracle and openastromod.munprofection)
			# agree on that drifted value to 1e-6 deg, confirming it is a
			# property of Morinus' formula, not a transcription slip.
			#
			# This is exactly why Morinus' own stepper dialog
			# (`profectionstepperdlg.py`, method `show`) special-cases a
			# multiple of 12 elapsed years on the natal month/day and shows
			# the RADIX CHART UNCHANGED (`pchart = self.chart`), never
			# calling calcMundaneProfPos at all in that case. This project's
			# integration (`openastro.localToMunProfection`) reproduces that
			# same bypass -- keyed off `diffLon == 0` rather than Morinus'
			# coarser whole-year/month/day match, since the UI here takes an
			# arbitrary date/time -- which is what actually guarantees a
			# cnt=0 chart identical to the radix; see tests/dialog for that
			# integration-level check.
			drift = abs(((b['lon'] - lon_body_prod + 180.0) % 360.0) - 180.0)
			check('cnt=0 %-6s: known non-inverting drift stays under 2 deg (%.4f deg)' % (name, drift),
				drift < 2.0, 'natal=%.9f cnt0=%.9f' % (b['lon'], lon_body_prod))

print('\n%d comprobaciones, %d fallos' % (total, len(fails)))
if fails:
	print('FALLAN:', fails)
	sys.exit(1)
print('TODO CORRECTO')
