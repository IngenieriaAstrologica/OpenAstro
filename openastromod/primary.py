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
    Topocentric primary directions (Polich-Page system).

    Ported from a rectificacion-project engine module, verified
    against the directions Isaac Starkman publishes (15 of 16 within 2' of
    arc). Only stdlib + swisseph.

    A primary direction is measured ON THE EQUATOR, not on the ecliptic:
    the body is taken to its oblique ascension under its own topocentric
    pole, the arc is added there, and only then converted back to the
    ecliptic. Adding the arc straight to the ecliptic longitude introduces
    a mean error of ~3 degrees against an allowed orb of 0.183 degrees.

    Doctrine ported along with the formulas: GEOCENTRIC planets,
    TOPOCENTRIC cusps (the topocentric part enters through the houses,
    i.e. through the significator's pole — never through parallactic
    planet positions).
"""

import math

import swisseph as swe

# Naibod arc: mean motion of the Sun, degrees per year of life
NAIBOD_DEGREE_PER_YEAR = 0.9856473663
# Mean tropical year in days (for age = (target_jd - birth_jd) / year)
TROPICAL_YEAR = 365.2421896698

# Time keys: how many arc degrees one year of life is worth
TIME_KEYS = ("naibod", "ptolomeo", "arco_solar_ar")

# Measure modes, following the three chart kinds of
# https://carta-natal.es/direcciones-primarias.php :
#   ecl_ecl: ecliptic chart — natal ecliptic longitudes vs Marr-directed
#            ecliptic longitudes (OA + arc under each own topocentric pole,
#            back to the ecliptic), with zodiacal aspects.
#   asc_asc: ascensional chart — natal OA vs directed OA (= OA + arc),
#            both rendered in OA space with an equal 30-degree OA-frame
#            from OA(ASC) as houses, and aspects measured on OA differences.
#   asc_ecl: mixed overlay — natal ecliptic wheel with the Marr-directed
#            positions on top (same positions as ecl_ecl in a bi-wheel).
MEASURE_KEYS = ("ecl_ecl", "asc_asc", "asc_ecl")

MEASURE_TAGS = {"ecl_ecl": ", ecliptic", "asc_asc": ", ascensional", "asc_ecl": ", mixed"}


def norm360(x):
	"""Any angle to 0..360 degrees."""
	return x % 360.0


def julday(year, month, day, hour):
	"""Julian day (UT) from date parts; hour in decimal hours."""
	return swe.julday(year, month, day, hour)


def get_obliquity(jd_ut):
	"""True obliquity of the ecliptic for a JD, in degrees."""
	result = swe.calc_ut(jd_ut, swe.ECL_NUT, swe.FLG_SWIEPH)
	return result[0][0]


def ecliptic_to_equatorial(ecl_lon, ecl_lat, jd_ut):
	"""Ecliptic (lon, lat) to equatorial (right ascension, declination)."""
	eps = get_obliquity(jd_ut)

	lon_rad = math.radians(ecl_lon)
	lat_rad = math.radians(ecl_lat)
	eps_rad = math.radians(eps)

	cos_lat = math.cos(lat_rad)
	sin_lat = math.sin(lat_rad)
	sin_lon = math.sin(lon_rad)
	cos_lon = math.cos(lon_rad)
	sin_eps = math.sin(eps_rad)
	cos_eps = math.cos(eps_rad)

	ra_rad = math.atan2(
		sin_lon * cos_eps - math.tan(lat_rad) * sin_eps,
		cos_lon
	)
	dec_rad = math.asin(
		sin_lat * cos_eps + cos_lat * sin_eps * sin_lon
	)

	ra = math.degrees(ra_rad)
	if ra < 0:
		ra += 360.0
	dec = math.degrees(dec_rad)

	return ra, dec


def topocentric_pole(ra, dec, lat, ramc):
	"""Topocentric pole of a body: tan(P) = tan(lat) * DM/SA.

	Positive when the body is in the western semicircle, negative in the
	eastern one. 0 at the MC (DM=0) and +-lat at the horizon (DM=SA),
	the two known limit cases.
	"""
	# Diurnal semi-arc: cos(SA) = -tan(lat)*tan(dec)
	cos_sa = -math.tan(math.radians(lat)) * math.tan(math.radians(dec))
	sa_diurnal = math.degrees(math.acos(max(-1.0, min(1.0, cos_sa))))

	# Distance to the nearest meridian and matching semi-arc
	dm_from_mc = (ra - ramc + 180.0) % 360.0 - 180.0
	above_horizon = abs(dm_from_mc) < sa_diurnal
	if above_horizon:
		semiarc = sa_diurnal
		dm = abs(dm_from_mc)
	else:
		semiarc = 180.0 - sa_diurnal	# nocturnal semi-arc
		dm = 180.0 - abs(dm_from_mc)	# distance to the IC

	if semiarc == 0:
		return 0.0

	pole = math.degrees(math.atan(math.tan(math.radians(lat)) * dm / semiarc))

	# Sign by semicircle: western (+) or eastern (-)
	is_western = 0.0 < (ra - ramc) % 360.0 < 180.0
	return pole if is_western else -pole


def ascensional_difference(pole, dec):
	"""Ascensional difference under a given pole: AD = asin(tan(P)*tan(dec))."""
	v = math.tan(math.radians(pole)) * math.tan(math.radians(dec))
	return math.degrees(math.asin(max(-1.0, min(1.0, v))))


def oblique_ascension(ra, dec, pole):
	"""Oblique ascension: OA = RA - AD."""
	return norm360(ra - ascensional_difference(pole, dec))


def oblique_ascension_to_ecliptic(oa, pole, eps):
	"""Oblique ascension to ecliptic longitude (Marr's Ascendant formula
	under the given pole). Assumes ecliptic latitude 0, which is correct
	here because the OA was already computed from the body's true RA and
	declination."""
	oa = norm360(oa)
	sin_oa = math.sin(math.radians(oa))
	if abs(sin_oa) < 1e-12:
		# OA at 0 or 180: the point is on the equinox, no real indeterminacy
		return 0.0 if oa < 90.0 or oa > 270.0 else 180.0

	e = math.radians(eps)
	numerator = math.sin(e) * math.tan(math.radians(pole)) - math.cos(e) * math.cos(math.radians(oa))
	longitude = math.degrees(math.atan(numerator / sin_oa))
	longitude += 90.0 if oa < 180.0 else 270.0
	return norm360(longitude)


def direct_position(natal_ecl_lon, natal_ecl_lat, arc_degrees, lat, ramc, jd_ut):
	"""Ecliptic longitude of a body after a primary-direction arc.

	Applied to the SIGNIFICATOR — the body the primary motion carries —
	this is the directed position to display. It uses exactly the same
	pole as the arc measurement, so at orb 0 it falls on the ray's degree
	to the last decimal.
	"""
	eps = get_obliquity(jd_ut)
	ra, dec = ecliptic_to_equatorial(natal_ecl_lon, natal_ecl_lat, jd_ut)
	pole = topocentric_pole(ra, dec, lat, ramc)
	oa_directed = norm360(oblique_ascension(ra, dec, pole) + arc_degrees)
	return oblique_ascension_to_ecliptic(oa_directed, pole, eps)


def arc_of_direction(significator_lon, significator_lat, promisor_lon,
			promisor_lat, aspect_angle, geo_lat, ramc, jd_ut):
	"""Arc carrying the significator to the promisor's ray.

	The SIGNIFICATOR is dragged by the diurnal rotation: it is the subject
	of the direction and provides the pole. The PROMISOR stays at its natal
	place and offers the body or aspect ray the significator reaches. This
	is the Polich-Page, Marr and Starkman convention (reversing the roles
	takes the mean error from 0.8' to 3636').

	`aspect_angle` is SIGNED: every aspect but conjunction and opposition
	has two rays, dexter and sinister, and they are different directions —
	the caller must try +angle and -angle. Returns arc in (-180, 180].
	"""
	# The pole belongs to the moving body, the significator, derived from
	# its true position: it keeps its ecliptic latitude.
	ra_p, dec_p = ecliptic_to_equatorial(significator_lon, significator_lat, jd_ut)
	pole = topocentric_pole(ra_p, dec_p, geo_lat, ramc)

	# Zodiacal aspects here: the promisor's ray is an ecliptic degree, with
	# no latitude — conjunction included.
	ray_lon = norm360(promisor_lon + aspect_angle)
	ra_r, dec_r = ecliptic_to_equatorial(ray_lon, 0.0, jd_ut)

	oa_ray          = oblique_ascension(ra_r, dec_r, pole)
	oa_significator = oblique_ascension(ra_p, dec_p, pole)

	return (oa_ray - oa_significator + 180.0) % 360.0 - 180.0


def solar_arc_ra(birth_jd_ut, prog_jd_ut):
	"""Arc the Sun travels in right ascension between two dates, signed."""
	lon_natal = swe.calc_ut(birth_jd_ut, swe.SUN, swe.FLG_SWIEPH)[0][0]
	lon_prog = swe.calc_ut(prog_jd_ut, swe.SUN, swe.FLG_SWIEPH)[0][0]
	ra_natal, _ = ecliptic_to_equatorial(lon_natal, 0.0, birth_jd_ut)
	ra_prog, _ = ecliptic_to_equatorial(lon_prog, 0.0, prog_jd_ut)
	return (ra_prog - ra_natal + 180.0) % 360.0 - 180.0


def calculate_direction_arc(age_years, birth_jd_ut, key="naibod"):
	"""Direction arc for an age, by time key. Negative ages give converse arcs."""
	if key == "naibod":
		return age_years * NAIBOD_DEGREE_PER_YEAR
	if key == "ptolomeo":
		return age_years * 1.0
	if key == "arco_solar_ar":
		# One ephemeris day per year of life; the arc is what the Sun
		# travels in RA between birth and that date. Unlike the other two,
		# it depends on the date and not only the age.
		return solar_arc_ra(birth_jd_ut, birth_jd_ut + age_years)
	raise ValueError("Unknown time key: %s" % (key,))


def arc_for_dates(birth_jd_ut, target_jd_ut, key="naibod"):
	"""Direction arc between the birth moment and a target date."""
	age_years = (target_jd_ut - birth_jd_ut) / TROPICAL_YEAR
	return calculate_direction_arc(age_years, birth_jd_ut, key)


def direct_frame(planets_ut, planets_lat, houses_ut, arc_degrees, geo_lat, ramc, jd_ut):
	"""Direct a whole chart by an arc: returns (planets_ut, houses_ut).

	OA + arc under each own topocentric pole, back to the ecliptic with
	Marr's Ascendant formula (carta-natal.es ecliptic directed positions).
	`planets_lat` may be shorter than `planets_ut` (extra points have no
	latitude); missing latitudes default to 0. Cusps are ecliptic points,
	so they are always directed with latitude 0.
	"""
	directed_planets = []
	for i, lon in enumerate(planets_ut):
		lat = planets_lat[i] if i < len(planets_lat) else 0.0
		directed_planets.append(direct_position(lon, lat, arc_degrees, geo_lat, ramc, jd_ut))
	directed_houses = [direct_position(lon, 0.0, arc_degrees, geo_lat, ramc, jd_ut) for lon in houses_ut]
	return directed_planets, directed_houses


def oa_positions(planets_ut, planets_lat, asc_lon, arc_degrees, geo_lat, ramc, jd_ut):
	"""OA-space rendering (carta-natal.es ascensional chart): returns
	(oa_nat, oa_dir, frame_nat, frame_dir).

	oa_nat[i] = natal oblique ascension under its own topocentric pole
	(true ecliptic latitude); oa_dir = oa_nat + arc; frame_nat/dir are the
	equal 30-degree OA-frames from OA(ASC) — the ascensional houses.
	All values are plain 0..360 degree scales, rendered by the caller on
	the zodiac wheel exactly as the reference page does.
	"""
	oa_nat = []
	for i, lon in enumerate(planets_ut):
		lat = planets_lat[i] if i < len(planets_lat) else 0.0
		ra, dec = ecliptic_to_equatorial(lon, lat, jd_ut)
		pole = topocentric_pole(ra, dec, geo_lat, ramc)
		oa_nat.append(oblique_ascension(ra, dec, pole))
	ra_a, dec_a = ecliptic_to_equatorial(asc_lon, 0.0, jd_ut)
	pole_a = topocentric_pole(ra_a, dec_a, geo_lat, ramc)
	oa_asc = oblique_ascension(ra_a, dec_a, pole_a)
	oa_dir = [norm360(o + arc_degrees) for o in oa_nat]
	frame_nat = [norm360(oa_asc + 30.0 * k) for k in range(12)]
	frame_dir = [norm360(oa_asc + arc_degrees + 30.0 * k) for k in range(12)]
	return oa_nat, oa_dir, frame_nat, frame_dir
