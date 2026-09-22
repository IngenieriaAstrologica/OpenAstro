"""Munprofection engine: Morinus' mundane ("Placidian") annual profection.

The Atacir dialog offers two mappings for the same "one technique a year"
idea. Zodiacal (`openastromod.atacir`) turns the whole chart rigidly by
360/N degrees a year -- pure arithmetic, no ephemeris, aspects among the
rotated bodies unchanged. Placidian is a different technique entirely, ported
from Morinus' `munprofections.MunProfections` and
`planets.Planet.calcMundaneProfPos` (module `Morinus SE/munprofections.py`
and `Morinus SE/planets.py` lines ~95-252 and ~491-606):

1. The natal Ascendant's diurnal and nocturnal semi-arcs (divided by 3, the
   Placidus "hour") give two rates, one for the first 6 years of a 12-year
   cycle and one for the last 6. Elapsed years, split across that 6-year
   boundary, buy a longitude offset -- the chart is relocated to a
   fictitious geographical longitude, never a real place.
2. Placidus house cusps are recast at that fictitious longitude for the
   SAME UT instant as the radix (only the longitude moves), giving a fresh
   RAMC and a fresh set of cusps.
3. Each body is repositioned individually: its own natal Placidus speculum
   (meridian distance, Placidus mundane position, ascensional difference
   under the pole) is held fixed, and solved against the NEW RAMC for the
   ecliptic longitude that reproduces the same mundane position. This is
   the "mundane" or mundo-based sense in which the profection is Placidian
   -- a body keeps its relationship to the local horizon/meridian system,
   not its ecliptic distance to the natal Ascendant.

Bit-for-bit fidelity to Morinus' arithmetic is the point of this module (see
`tests/engine/munprofection.py`, which ports the same formulas a second,
independent time as a test oracle and cross-checks several year offsets,
including one that crosses the 6-year split). Two harmless simplifications
against the Morinus source are noted inline where they occur; neither
changes a single output value.

Two Morinus quirks are kept exactly rather than "fixed", because the task is
fidelity, not improvement:

- `cycInYears = diffYear - int(diffYear/12.0)*12.0` uses Python's
  truncating `int()`, not `floor()`. For years elapsed *before* birth
  (a converse profection) this does not fold cleanly into [0, 12) the way
  it does for positive years -- e.g. -5 years stays -5, not +7. Morinus'
  own stepper dialog never runs a mundane profection before birth (the
  zodiacal-profection branch is used instead in that case), so this is
  unexercised territory in the original program too. It is reproduced here
  unchanged rather than silently reinterpreted.
- Circumpolar/high-latitude degeneracies (a body or the Ascendant whose
  |tan(lat)*tan(decl)| > 1, i.e. it never rises or sets at that latitude)
  are handled by Morinus with a silent `adlat = 0.0` fallback rather than
  an error. Reproduced identically below at every site that computes an
  ascensional difference.
"""

import math

from . import atacir
from . import primary

#Mean tropical year, Morinus' constant -- see openastromod.atacir for the
#derivation and the K=12.17473968 cross-check against Morinus' own stepper.
TROPICAL_YEAR = atacir.TROPICAL_YEAR

#Field indices into a "placidian speculum" tuple, mirroring Morinus'
#planets.Planet speculum-field constants (LONG/LAT/RA/DECL common to every
#speculum kind, then the Placidus-specific fields in Morinus' own order).
LONG, LAT, RA, DECL, ADLAT, SA, MD, HD, TH, HOD, PMP, ADPH, POH, AODO = range(14)


def normalize(x):
	"""Fold an angle into [0, 360), matching Morinus' util.normalize."""
	return float(x) % 360.0


def relocated_longitude(natal_ramc, natal_asc_decl, place_lat, place_lon, diff_years):
	"""The fictitious geographical longitude for a mundane profection.

	Port of `munprofections.MunProfections.__init__`. `natal_ramc` and
	`natal_asc_decl` are the radix's RAMC and Ascendant declination
	(`radix.houses.ascmc2[MC][RA]` / `[ASC][DECL]` in Morinus);
	`place_lat`/`place_lon` are the radix's geographical coordinates, signed
	with East positive (OpenAstro's convention, same as pyswisseph's);
	`diff_years` is the elapsed time in tropical years since birth (Morinus
	computes the equivalent quantity via a `y,m,d,t,cnt` julian-day
	roundtrip that this module replaces with a single elapsed-years figure
	-- see the module docstring in `openastromod.atacir` for the analogous
	simplification already made for the Zodiacal mapping).

	Returns `(lon_signed, diff_lon, cyc_in_years)`: the fictitious longitude
	ready to feed to an ephemeris call (signed degrees, East positive), the
	raw longitude delta before wrapping, and the position within the
	12-year cycle (kept for the boundary-crossing test).
	"""
	val = math.tan(math.radians(natal_asc_decl)) * math.tan(math.radians(place_lat))
	adlat_asc = 0.0
	if math.fabs(val) <= 1.0:
		adlat_asc = math.degrees(math.asin(val))

	dsalat_asc = 90.0 + adlat_asc
	nsalat_asc = 90.0 - adlat_asc

	#diurnal/nocturnal "house": a Placidus semi-arc divided in three
	dhlat_asc = dsalat_asc / 3.0
	nhlat_asc = nsalat_asc / 3.0

	#Morinus: lon360 = placelon; if placelon<0: lon360 = 360+placelon.
	#Equivalent to a plain modulo for a signed, East-positive longitude.
	lon360 = normalize(place_lon)

	#Profection cycle position (Python int() truncates toward zero, not
	#floor -- see the module docstring)
	cyc_in_years = diff_years - int(diff_years / 12.0) * 12.0

	d_cyc = cyc_in_years
	if cyc_in_years > 6.0:
		d_cyc = 6.0

	n_cyc = 0.0
	if cyc_in_years > 6.0:
		n_cyc = cyc_in_years - d_cyc

	diff_lon = d_cyc * dhlat_asc + n_cyc * nhlat_asc

	lon360_z = normalize(lon360 + diff_lon)

	#Morinus keeps (magnitude, east/west) separately; collapsed here into a
	#single signed longitude, East positive -- what an ephemeris call wants.
	lon_signed = lon360_z - 360.0 if lon360_z > 180.0 else lon360_z

	return lon_signed, diff_lon, cyc_in_years


def placidian_speculum(lon, lat, ra, decl, ramc, place_lat):
	"""A body's natal Placidus speculum.

	Port of `planets.Planet.computePlacidianSpeculum`. `ra`/`decl` are the
	body's own equatorial coordinates (from its true ecliptic `lon`/`lat`
	via `openastromod.primary.ecliptic_to_equatorial`); `ramc` is the
	radix's RAMC; `place_lat` the radix's geographical latitude.

	Returns a 14-field tuple indexed by this module's LONG..AODO constants
	-- the same shape Morinus keeps in `Planet.speculums[0]`, since
	`mundane_reposition` below needs exactly MD, PMP, ADPH and DECL back
	out of it, and keeping the rest makes cross-checking against Morinus'
	own intermediate values (adlat, sa, hd, ...) possible field by field.
	"""
	raic = ramc + 180.0
	if raic > 360.0:
		raic -= 360.0

	eastern = True
	if ramc > raic:
		if raic < ra < ramc:
			eastern = False
	else:
		if (raic < ra < 360.0) or (0.0 < ra < ramc):
			eastern = False

	#ascensional difference under the place's own pole (not a body-specific
	#pole -- this is the natal Placidus speculum, computed once per body
	#against the fixed radix latitude)
	adlat = 0.0
	val = math.tan(math.radians(place_lat)) * math.tan(math.radians(decl))
	if math.fabs(val) <= 1.0:
		adlat = math.degrees(math.asin(val))

	med = math.fabs(ramc - ra)
	if med > 180.0:
		med = 360.0 - med
	icd = math.fabs(raic - ra)
	if icd > 180.0:
		icd = 360.0 - icd

	md = med

	#hd (horizon distance) -- independent of the day/night split below
	aoasc = ramc + 90.0
	if aoasc >= 360.0:
		aoasc -= 360.0
	dodesc = raic + 90.0
	if dodesc >= 360.0:
		dodesc -= 360.0

	aohd = ra - adlat
	hdasc = aohd - aoasc
	if hdasc < 0.0:
		hdasc = -hdasc
	if hdasc > 180.0:
		hdasc = 360.0 - hdasc

	dohd = ra + adlat
	hddesc = dohd - dodesc
	if hddesc < 0.0:
		hddesc = -hddesc
	if hddesc > 180.0:
		hddesc = 360.0 - hddesc

	hd = hdasc
	if hddesc < hdasc:
		hd = -hddesc

	#sa (semi-arc): diurnal if the body is above the horizon, else nocturnal
	#(negative, by Morinus' own convention) -- and md is retaken from the
	#IC distance in that case, also negated
	dsa = 90.0 + adlat
	nsa = 90.0 - adlat

	abovehorizon = not (med > dsa)

	sa = dsa
	if not abovehorizon:
		sa = -nsa
		md = -icd

	th = sa / 6.0

	hod = 0.0
	if th != 0.0:
		hod = md / math.fabs(th)

	tmd = math.fabs(md)
	pmpsa = math.fabs(sa)

	#pmp (Placidus Mundane Position): which of the four mundane quadrants,
	#and how far across it, by day/night and east/west
	pmp = 0.0
	if not abovehorizon and eastern:
		pmp = 90.0 - 90.0 * (tmd / pmpsa)
	elif not abovehorizon and not eastern:
		pmp = 90.0 + 90.0 * (tmd / pmpsa)
	elif abovehorizon and not eastern:
		pmp = 270.0 - 90.0 * (tmd / pmpsa)
	elif abovehorizon and eastern:
		pmp = 270.0 + 90.0 * (tmd / pmpsa)

	#adph (ascensional difference "at" this body's mundane position) and
	#poh (pole height reproducing it) -- the two quantities that pin the
	#body's mundane place down independently of any particular RAMC
	tval = math.fabs(sa)
	adphi = 0.0
	if tval != 0.0:
		adphi = math.fabs(tmd) * adlat / tval

	tval2 = math.tan(math.radians(decl))
	poh = 0.0
	if tval2 != 0.0:
		poh = math.degrees(math.atan(math.sin(math.radians(adphi)) / tval2))

	if eastern:
		aodo = ra - adphi
	else:
		aodo = -(ra + adphi)

	return (lon, lat, ra, decl, adlat, sa, md, hd, th, hod, pmp, adphi, poh, aodo)


def _solve_longitude(pmp, rao, rdo, robl, rpoh, lon):
	"""Port of `planets.Planet.iterate`.

	Not actually iterative in Morinus (the name is inherited from the
	fallback below, which straddles a singularity with a +/-0.5 degree
	average): a direct trig solve for the ecliptic longitude whose oblique
	ascension (under the sought pole `rpoh`) equals the AO or DO carried
	over from the natal speculum, in radians throughout.

	Returns `(ok_ga, ok_gd, lon)`; `ok_ga`/`ok_gd` are False only when the
	solve's denominator is exactly zero (a genuine singularity of this
	closed-form formula, not merely a large value) -- the caller straddles
	that case exactly as Morinus does. Morinus wraps the denominator in
	`math.degrees()` before testing its sign; that call is a positive linear
	rescaling and changes no comparison in `>0`/`<0`/`!=0`, so it is omitted
	here as dead arithmetic, not as a behavioural change.
	"""
	ok_ga = ok_gd = True
	if pmp < 90.0 or (270.0 <= pmp < 360.0):
		denom = math.cos(rao) * math.cos(robl) - math.sin(robl) * math.tan(rpoh)
		if denom != 0.0:
			f = math.degrees(math.atan(math.sin(rao) / denom))
			if f >= 0.0 and denom > 0.0:
				lon = f
			elif f < 0.0 and denom > 0.0:
				lon = f + 360.0
			elif denom < 0.0:
				lon = f + 180.0
		else:
			ok_ga = False
	else:
		denom = math.cos(rdo) * math.cos(robl) + math.sin(robl) * math.tan(rpoh)
		if denom != 0.0:
			f = math.degrees(math.atan(math.sin(rdo) / denom))
			if f >= 0.0 and denom > 0.0:
				lon = f
			elif f < 0.0 and denom > 0.0:
				lon = f + 360.0
			elif denom < 0.0:
				lon = f + 180.0
		else:
			ok_gd = False
	return ok_ga, ok_gd, lon


def mundane_reposition(speculum, new_ramc, place_lat, obl):
	"""A body's ecliptic longitude after relocation to a new RAMC.

	Port of `planets.Planet.calcMundaneProfPos`. `speculum` is this body's
	NATAL placidian speculum (from `placidian_speculum` above, evaluated
	against the natal RAMC); `new_ramc` is the RAMC of the relocated chart
	(same UT instant, fictitious longitude); `place_lat` is unchanged (the
	relocation only ever moves longitude); `obl` is the true obliquity at
	the birth instant (identical whether taken from the natal or the
	relocated frame, since both share the same UT moment).

	The body's declination is held fixed (Morinus keeps the planet's
	`dataEqu[DECLEQU]` from construction, never touching it in this
	method); only right ascension and ecliptic longitude are solved for.
	"""
	raic = new_ramc + 180.0
	if raic > 360.0:
		raic -= 360.0

	md = speculum[MD]
	if md < 0.0:
		md = -md

	pmp = speculum[PMP]
	if pmp < 90.0:
		ra = raic - md
	elif pmp < 180.0:
		ra = raic + md
	elif pmp < 270.0:
		ra = new_ramc - md
	else:
		ra = new_ramc + md
	ra = normalize(ra)

	adph = math.fabs(speculum[ADPH])
	decl = speculum[DECL]

	#See the module docstring: place_lat==0 or decl==0 is the degenerate
	#case (ao=do=ra); the two sign-combination branches below are mutually
	#exclusive so Morinus' three independent `if`s collapse to `elif`
	#without changing behaviour.
	if place_lat == 0.0 or decl == 0.0:
		ao = do = ra
	elif (place_lat > 0.0 and decl > 0.0) or (place_lat < 0.0 and decl < 0.0):
		ao = ra - adph
		do = ra + adph
	else:
		ao = ra + adph
		do = ra - adph

	ao = normalize(ao)
	do = normalize(do)

	poh = speculum[POH]

	rao = math.radians(ao)
	rdo = math.radians(do)
	robl = math.radians(obl)
	rpoh = math.radians(poh)
	lon = speculum[LONG]

	ok_ga, ok_gd, lon = _solve_longitude(pmp, rao, rdo, robl, rpoh, lon)
	if not ok_ga:
		#singularity in the AO solve: straddle it with rays +/-0.5 degree
		#either side and average, exactly as Morinus does
		lon1 = _solve_longitude(pmp, rao + math.radians(0.5), rdo, robl, rpoh, lon)[2]
		lon2 = _solve_longitude(pmp, rao - math.radians(0.5), rdo, robl, rpoh, lon)[2]
		lon = normalize((lon1 + lon2) / 2.0)
	elif not ok_gd:
		lon1 = _solve_longitude(pmp, rao, rdo + math.radians(0.5), robl, rpoh, lon)[2]
		lon2 = _solve_longitude(pmp, rao, rdo - math.radians(0.5), robl, rpoh, lon)[2]
		lon = normalize((lon1 + lon2) / 2.0)

	return lon


def reposition_frame(planets_ut, planets_lat, natal_ramc, new_ramc, place_lat, jd_ut):
	"""Reposition a whole list of bodies to a relocated RAMC.

	Port of the loop in `planets.Planets.calcMundaneProfPos` (which calls
	`Planet.calcMundaneProfPos` once per body). `planets_lat` may be shorter
	than `planets_ut`; entries with no latitude of their own (angles, lots,
	nodes-as-points) default to 0, same convention as
	`openastromod.primary.direct_frame`.

	Callers that also need the relocated angles (Ascendant, MC, ...) should
	take those directly from a fresh Placidus house computation at the
	relocated longitude, same UT instant -- not from this function, since a
	body's own mundane position is undefined exactly at the horizon/meridian
	it defines. `openastro.localToMunProfection` does this by overwriting
	the angle indices after calling this function, the same way Morinus'
	dialog casts a whole fresh `chart.Chart` at the fictitious longitude for
	its cusps rather than running the Ascendant through
	`calcMundaneProfPos`.
	"""
	obl = primary.get_obliquity(jd_ut)
	out = []
	for i, lon in enumerate(planets_ut):
		lat = planets_lat[i] if i < len(planets_lat) else 0.0
		ra, decl = primary.ecliptic_to_equatorial(lon, lat, jd_ut)
		spec = placidian_speculum(lon, lat, ra, decl, natal_ramc, place_lat)
		out.append(mundane_reposition(spec, new_ramc, place_lat, obl))
	return out
