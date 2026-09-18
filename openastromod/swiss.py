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
import os.path, sys, datetime, math
#swiss ephemeris files directory
swissDir = os.path.join(sys.prefix,'share','swisseph')
#local swiss ephemeris files directory
home=os.path.expanduser("~")
oa=os.path.join(home, '.openastro.org')
swissLocalDir=os.path.join(oa, 'swiss_ephemeris')

#swiss ephemeris path
ephe_path=swissDir+':'+swissLocalDir

import swisseph as swe

# Fixed-star catalog (display name, swe_fixstar_ut name, short label).
# Every entry resolves in sefstars.txt (verified Sep-2026).
# Excluded: Dschubba is only reachable as 'Isidis (Dschubba)' (included
# under that swe name); 'Marfik' and 'Han' are mislabeled/ambiguous catalog
# lines (Marsik and Hanal cover the real stars); 'Coxa' duplicates Chertan.
# Stars brighter than magnitude 1.0 get a 2-degree orb, the rest 1 degree.
ORB_2_DEG = {'Sirius', 'Canopus', 'Arcturus', 'Toliman', 'Vega', 'Capella',
	'Rigel', 'Procyon', 'Achernar', 'Betelgeuse', 'Hadar', 'Altair',
	'Acrux', 'Aldebaran', 'Antares', 'Spica'}
FIXED_STARS = [
	('Aldebaran', 'Aldebaran', 'Ald'),
	('Algol', 'Algol', 'Alg'),
	('Antares', 'Antares', 'Ant'),
	('Regulus', 'Regulus', 'Reg'),
	('Spica', 'Spica', 'Spi'),
	('Fomalhaut', 'Fomalhaut', 'Fom'),
	('Altair', 'Altair', 'Alt'),
	('Vega', 'Vega', 'Veg'),
	('Deneb', 'Deneb', 'Den'),
	('Betelgeuse', 'Betelgeuse', 'Bet'),
	('Rigel', 'Rigel', 'Rig'),
	('Pollux', 'Pollux', 'Pol'),
	('Arcturus', 'Arcturus', 'Arc'),
	('Sirius', 'Sirius', 'Sir'),
	('Alnilam', 'Alnilam', 'Alm'),
	('Alnitak', 'Alnitak', 'Alk'),
	('Mintaka', 'Mintaka', 'Min'),
	('Capella', 'Capella', 'Cap'),
	('Castor', 'Castor', 'Cas'),
	('Procyon', 'Procyon', 'Pro'),
	('Alphard', 'Alphard', 'Alp'),
	('Denebola', 'Denebola', 'Deo'),
	('Alphecca', 'Alphecca', 'Aph'),
	('Bellatrix', 'Bellatrix', 'Bel'),
	('Rasalhague', 'Rasalhague', 'Ras'),
	('Sabik', 'Sabik', 'Sab'),
	('Alcyone', 'Alcyone', 'Alc'),
	('Caph', 'Caph', 'Cph'),
	('Schedar', 'Schedar', 'Sch'),
	('Hamal', 'Hamal', 'Ham'),
	('Menkar', 'Menkar', 'Men'),
	('Diphda', 'Diphda', 'Dip'),
	('Enif', 'Enif', 'Eni'),
	('Alderamin', 'Alderamin', 'Ade'),
	('Acrab', 'Acrab', 'Acr'),
	('Gacrux', 'Gacrux', 'Gac'),
	('Alnair', 'Alnair', 'Aln'),
	('Dubhe', 'Dubhe', 'Dub'),
	('Kochab', 'Kochab', 'Koc'),
	('Thuban', 'Thuban', 'Thu'),
	('Alcor', 'Alcor', 'Alo'),
	('Canopus', 'Canopus', 'Can'),
	('Achernar', 'Achernar', 'Ach'),
	('Mizar', 'Mizar', 'Miz'),
	('Alioth', 'Alioth', 'Ali'),
	('Facies', 'Facies', 'Fac'),
	('Acumen', 'Acumen', 'Acu'),
	('Lesath', 'Lesath', 'Les'),
	('Sargas', 'Sargas', 'Sar'),
	('Nunki', 'Nunki', 'Nun'),
	('Ascella', 'Ascella', 'Asc'),
	('Rukbat', 'Rukbat', 'Ruk'),
	('Arkab', 'Arkab', 'Ark'),
	('Alnasl', 'Alnasl', 'Asn'),
	('Tarazed', 'Tarazed', 'Tar'),
	('Alshain', 'Alshain', 'Ash'),
	('Sadalsuud', 'Sadalsuud', 'Ssd'),
	('Sadalmelik', 'Sadalmelik', 'Sml'),
	('Skat', 'Skat', 'Ska'),
	('Aladfar', 'Aladfar', 'Alf'),
	('Ruchbah', 'Ruchbah', 'Rub'),
	('Segin', 'Segin', 'Seg'),
	('Phecda', 'Phecda', 'Phe'),
	('Megrez', 'Megrez', 'Meg'),
	('Pherkad', 'Pherkad', 'Phk'),
	('Eltanin', 'Eltanin', 'Elt'),
	('Rastaban', 'Rastaban', 'Rst'),
	('Kuma', 'Kuma', 'Kum'),
	('Mirach', 'Mirach', 'Mir'),
	('Mirfak', 'Mirfak', 'Mrf'),
	('Markab', 'Markab', 'Mrk'),
	('Scheat', 'Scheat', 'Sht'),
	('Alpheratz', 'Alpheratz', 'Apz'),
	('Algenib', 'Algenib', 'Agn'),
	('Matar', 'Matar', 'Mat'),
	('Baten Kaitos', 'Baten Kaitos', 'Bka'),
	('Foramen', 'Foramen', 'For'),
	('Hadar', 'Hadar', 'Had'),
	('Shaula', 'Shaula', 'Sha'),
	('Mimosa', 'Mimosa', 'Mim'),
	('Acrux', 'Acrux', 'Acx'),
	('Aludra', 'Aludra', 'Alu'),
	('Wezen', 'Wezen', 'Wez'),
	('Adhara', 'Adhara', 'Adh'),
	('Naos', 'Naos', 'Nao'),
	('Aspidiske', 'Aspidiske', 'Asp'),
	('Miaplacidus', 'Miaplacidus', 'Mia'),
	('Avior', 'Avior', 'Avi'),
	('Alkaid', 'Alkaid', 'Akd'),
	('Merak', 'Merak', 'Mek'),
	('Suhail al Muhlif', 'Suhail al Muhlif', 'Sam'),
	('Kaus Media', 'Kaus Meridionalis', 'Kau'),
	('Mesarthim', 'Mesarthim', 'Mes'),
	('Botein', 'Botein', 'Bot'),
	('Ain', 'Ain', 'Ain'),
	('Prima Hyadum', 'Prima Hyadum', 'PHy'),
	('Secunda Hyadum', 'Secunda Hyadum', 'SHy'),
	('Maia', 'Maia', 'Mai'),
	('Merope', 'Merope', 'Mer'),
	('Electra', 'Electra', 'Ele'),
	('Taygeta', 'Taygeta', 'Tyg'),
	('Atlas', 'Atlas', 'Atl'),
	('Pleione', 'Pleione', 'Pln'),
	('Alhena', 'Alhena', 'Alh'),
	('Wasat', 'Wasat', 'Wst'),
	('Mebsuta', 'Mebsuta', 'Meb'),
	('Tejat', 'Tejat', 'Tej'),
	('Mekbuda', 'Mekbuda', 'Mkd'),
	('Propus', 'Propus etaGem', 'Prp'),
	('Acubens', 'Acubens', 'Acb'),
	('Al Tarf', 'Al Tarf', 'Ata'),
	('Asellus Australis', 'Asellus Australis', 'AsA'),
	('Asellus Borealis', 'Asellus Borealis', 'AsB'),
	('Tegmine', 'Tegmine', 'Teg'),
	('Algieba', 'Algieba', 'Agb'),
	('Zosma', 'Zosma', 'Zos'),
	('Ras Elased Australis', 'Ras Elased Australis', 'REA'),
	('Ras Elased Borealis', 'Ras Elased Borealis', 'REB'),
	('Alterf', 'Alterf', 'Atr'),
	('Subra', 'Subra', 'Sub'),
	('Chertan', 'Chertan', 'Cht'),
	('Adhafera', 'Adhafera', 'Adf'),
	('Porrima', 'Porrima', 'Por'),
	('Auva', 'Auva', 'Auv'),
	('Heze', 'Heze', 'Hez'),
	('Syrma', 'Syrma', 'Syr'),
	('Khambalia', 'Khambalia', 'Kha'),
	('Vindemiatrix', 'Vindemiatrix', 'Vin'),
	('Zaniah', 'Zaniah', 'Zan'),
	('Zuben Elgenubi', 'Zuben Elgenubi', 'ZEl'),
	('Zuben Eshamali', 'Zuben Eshamali', 'ZEs'),
	('Zuben Elakrab', 'Zuben Elakrab', 'ZEA'),
	('Zuben Hakrabi', 'Zuben Hakrabi', 'ZHk'),
	('Brachium', 'Brachium', 'Bra'),
	('Jabbah', 'Jabbah', 'Jab'),
	('Dschubba', 'Isidis (Dschubba)', 'Dsc'),
	('Marsik', 'Marsik', 'Msk'),
	('Yed Prior', 'Yed Prior', 'YPr'),
	('Yed Posterior', 'Yed Posterior', 'YPo'),
	('Unukalhai', 'Unukalhai', 'Unu'),
	('Alya', 'Alya', 'Aly'),
	('Rasalgethi', 'Rasalgethi', 'Rsg'),
	('Kornephoros', 'Kornephoros', 'Kor'),
	('Maasym', 'Maasym', 'Maa'),
	('Sarin', 'Sarin', 'Srn'),
	('Sheliak', 'Sheliak', 'Shl'),
	('Sulafat', 'Sulafat', 'Sul'),
	('Albireo', 'Albireo', 'Alb'),
	('Sadr', 'Sadr', 'Sdr'),
	('Gienah Cygni', 'Gienah Cygni', 'GCy'),
	('Azelfafage', 'Azelfafage', 'Aze'),
	('Anser', 'Anser', 'Ans'),
	('Sham', 'Sham', 'Shm'),
	('Sualocin', 'Sualocin', 'Sua'),
	('Rotanev', 'Rotanev', 'Rot'),
	('Kitalpha', 'Kitalpha', 'Kit'),
	('Atik', 'Atik', 'Atk'),
	('Menkib', 'Menkib', 'Mnk'),
	('Menkalinan', 'Menkalinan', 'Mkn'),
	('Almach', 'Almach', 'Amc'),
	('Homam', 'Homam', 'Hom'),
	('Baham', 'Baham', 'Bah'),
	('Sadalbari', 'Sadalbari', 'Sbr'),
	('Deneb Algedi', 'Deneb Algedi', 'DAl'),
	('Dabih', 'Dabih', 'Dab'),
	('Algedi', 'Algedi', 'Agi'),
	('Nashira', 'Nashira', 'Nas'),
	('Situla', 'Situla', 'Sit'),
	('Albali', 'Albali', 'Aba'),
	('Ancha', 'Ancha', 'Anc'),
	('Alrescha', 'Al Rescha', 'Are'),
	('Fum Alsamakah', 'Fum Alsamakah', 'Fum'),
	('Alpherg', 'Al Pherg', 'Apg'),
	('Revati', 'Revati', 'Rev'),
	('Acamar', 'Acamar', 'Aca'),
	('Zaurak', 'Zaurak', 'Zau'),
	('Rana', 'Rana', 'Ran'),
	('Cursa', 'Cursa', 'Cur'),
	('Arneb', 'Arneb', 'Arn'),
	('Nihal', 'Nihal', 'Nih'),
	('Phact', 'Phact', 'Pha'),
	('Wazn', 'Wazn', 'Waz'),
	('Gomeisa', 'Gomeisa', 'Gom'),
	('Labrum', 'Labrum', 'Lab'),
	('Gienah Corvi', 'Gienah Corvi', 'GCo'),
	('Algorab', 'Algorab', 'Ago'),
	('Kraz', 'Kraz', 'Kra'),
	('Minkar', 'Minkar', 'Mkr'),
	('Diadem', 'Diadem', 'Dia'),
	('Cor Caroli', 'Cor Caroli', 'CCr'),
	('Muscida', 'Muscida', 'Mus'),
	('Talitha Australis', 'Talitha Australis', 'TAA'),
	('Talitha Borealis', 'Talitha Borealis', 'TAB'),
	('Alula Australis', 'Alula Australis', 'AlA'),
	('Alula Borealis', 'Alula Borealis', 'AlB'),
	('Tania Australis', 'Tania Australis', 'TNA'),
	('Tania Borealis', 'Tania Borealis', 'TNB'),
	('Altais', 'Altais', 'Ats'),
	('Grumium', 'Grumium', 'Gru'),
	('Alfirk', 'Alfirk', 'Afi'),
	('Errai', 'Errai', 'Err'),
	('Kurhah', 'Kurhah', 'Kur'),
	('Achird', 'Achird', 'Acd'),
	('Marfak', 'Marfak', 'Mfa'),
	('Cih', 'Cih', 'Cih'),
	('Metallah', 'Metallah', 'Met'),
	('Markeb', 'Markeb', 'Mke'),
	('Toliman', 'Toliman', 'Tol'),
	('Menkent', 'Menkent', 'Mkt'),
	('Suhail Hadar', 'Suhail Hadar', 'SHa'),
	('Azmidiske', 'Azmidiske', 'Azm'),
	('Mirzam', 'Mirzam', 'Mrz'),
	('Sharatan', 'Sharatan', 'Shr'),
	('Celeano', 'Celeano', 'Cel'),
]

def normalize_dodec(lon):
	"""Normaliza longitud a 0..360 (igual que util.normalize de Morinus)."""
	lon = float(lon) % 360.0
	if lon < 0:
		lon += 360.0
	return lon

def calc_dodecatemoria(lon):
	"""Dodecatemoria segun Morinus (antiscia.calcDodecatemoria).

	30*signo + 12*longitud_relativa, normalizado a 0..360.
	Cada signo de 30 grados se expande x12 sobre el zodiaco
	(segmentos de 2.5 grados). La longitud de entrada ya viene
	en el zodiaco configurado (tropical/sideral), por eso no se
	resta ayanamsa aqui (Morinus lo hace porque parte de tropical).
	"""
	lon = normalize_dodec(lon)
	sign = int(lon // 30.0)
	rel = lon - sign * 30.0
	# KeepBetweenLimit(rel,30) ya garantizado; KeepInZodiac al final
	return normalize_dodec(30.0 * sign + 12.0 * rel)

#Eje de antiscios (Morinus antiscia.Antiscia): Cancer 0 / Capricornio 0.
CANCER0 = 90.0
CAPRICORN0 = 270.0

def calc_antiscion(lon, ayan=0.0):
	"""Antiscion y contraantiscion segun Morinus (antiscia.calc).

	Reflejo sobre el eje Cancer 0 / Capricornio 0 (simetria de
	declinacion): la misma rama if/elif que Morinus, que equivale
	a ant_trop = (180 - lon_trop) mod 360; contra = (ant + 180) mod 360.

	ayan es el ayanamsa vigente cuando el zodiaco es sideral (0.0 en
	tropical). Como los antiscios son tropicales por definicion, se
	convierte la entrada a tropical (lon + ayan), se refleja, y se
	devuelve al zodiaco configurado (ant_trop - ayan). Morinus hace
	lo mismo partiendo de longitudes tropicales (resta ayan al final);
	aqui la entrada ya viene en el zodiaco configurado, por eso se
	suma ayan primero. En tropical (ayan=0) es identidad: f(lon).
	"""
	ayan = float(ayan)
	if ayan:
		lon_trop = normalize_dodec(float(lon) + ayan)
	else:
		lon_trop = normalize_dodec(lon)

	if lon_trop == CANCER0 or lon_trop == CAPRICORN0:
		ant_trop = lon_trop
	elif lon_trop > CANCER0 and lon_trop < CAPRICORN0:
		ant_trop = normalize_dodec(CAPRICORN0 + (CAPRICORN0 - lon_trop))
	elif lon_trop < CANCER0:
		ant_trop = normalize_dodec(CANCER0 + (CANCER0 - lon_trop))
	else: # lon_trop > CAPRICORN0
		ant_trop = normalize_dodec(CAPRICORN0 - (lon_trop - CAPRICORN0))

	if ayan:
		ant = normalize_dodec(ant_trop - ayan)
	else:
		ant = normalize_dodec(ant_trop)
	cant = normalize_dodec(ant + 180.0)
	return ant, cant

class ephData:
	def __init__(self,year,month,day,hour,geolon,geolat,altitude,planets,zodiac,openastrocfg,houses_override=None):
		#ephemeris path (default "/usr/share/swisseph:/usr/local/share/swisseph")
		swe.set_ephe_path(ephe_path)
		
		#basic location		
		self.jul_day_UT=swe.julday(year,month,day,hour)
		self.geo_loc = swe.set_topo(geolon,geolat,altitude)

		#output variables
		self.planets_sign = list(range(len(planets)))
		self.planets_degree = list(range(len(planets)))
		self.planets_degree_ut = list(range(len(planets)))
		self.planets_latitude = [0.0] * len(planets)
		self.planets_info_string = list(range(len(planets)))
		self.planets_retrograde = list(range(len(planets)))
		#birth moment JD (before any houses_override rewrite below) and RAMC,
		#needed for topocentric primary directions (openastromod.primary)
		self.jd_ut = self.jul_day_UT
		self.ramc = 0.0
		
		#iflag
		"""
		#define SEFLG_JPLEPH         1L     // use JPL ephemeris
		#define SEFLG_SWIEPH         2L     // use SWISSEPH ephemeris, default
		#define SEFLG_MOSEPH         4L     // use Moshier ephemeris
		#define SEFLG_HELCTR         8L     // return heliocentric position
		#define SEFLG_TRUEPOS        16L     // return true positions, not apparent
		#define SEFLG_J2000          32L     // no precession, i.e. give J2000 equinox
		#define SEFLG_NONUT          64L     // no nutation, i.e. mean equinox of date
		#define SEFLG_SPEED3         128L     // speed from 3 positions (do not use it, SEFLG_SPEED is // faster and preciser.)
		#define SEFLG_SPEED          256L     // high precision speed (analyt. comp.)
		#define SEFLG_NOGDEFL        512L     // turn off gravitational deflection
		#define SEFLG_NOABERR        1024L     // turn off 'annual' aberration of light
		#define SEFLG_EQUATORIAL     2048L     // equatorial positions are wanted
		#define SEFLG_XYZ            4096L     // cartesian, not polar, coordinates
		#define SEFLG_RADIANS        8192L     // coordinates in radians, not degrees
		#define SEFLG_BARYCTR        16384L     // barycentric positions
		#define SEFLG_TOPOCTR      (32*1024L)     // topocentric positions
		#define SEFLG_SIDEREAL     (64*1024L)     // sidereal positions 		
		"""
		#check for apparent geocentric (default), true geocentric, topocentric or heliocentric
		iflag=swe.FLG_SWIEPH+swe.FLG_SPEED
		if(openastrocfg['postype']=="truegeo"):
			iflag += swe.FLG_TRUEPOS
		elif(openastrocfg['postype']=="topo"):
			iflag += swe.FLG_TOPOCTR
		elif(openastrocfg['postype']=="helio"):
			iflag += swe.FLG_HELCTR

		#sidereal
		if(openastrocfg['zodiactype']=="sidereal"):
			iflag += swe.FLG_SIDEREAL
			mode="SIDM_"+openastrocfg['siderealmode']
			swe.set_sid_mode(getattr(swe,mode))

		#ayanamsa vigente (0.0 en tropical): los antiscios son tropicales
		#por definicion, asi que calc_antiscion() lo necesita para volver
		#al zodiaco configurado (igual que Morinus antiscia.calc).
		self.ayanamsa = 0.0
		if(openastrocfg['zodiactype']=="sidereal"):
			try:
				self.ayanamsa = float(swe.get_ayanamsa_ut(self.jul_day_UT))
			except Exception:
				self.ayanamsa = 0.0

		#compute a planet (longitude,latitude,distance,long.speed,lat.speed,speed)
		for i in range(23):
			ret_flag = swe.calc_ut(self.jul_day_UT,i,iflag)
			for x in range(len(zodiac)):
				deg_low=float(x*30)
				deg_high=float((x+1)*30)
				if (ret_flag[0][0] >= deg_low):
					if ret_flag[0][0] <= deg_high:
						self.planets_sign[i]=x
						self.planets_degree[i] = ret_flag[0][0] - deg_low
						self.planets_degree_ut[i] = ret_flag[0][0]
						self.planets_latitude[i] = ret_flag[0][1]
						#if latitude speed is negative, there is retrograde
						#if ret_flag[3] < 0:						
						if ret_flag[0][3] < 0:						
							self.planets_retrograde[i] = True
						else:
							self.planets_retrograde[i] = False

		#fixed stars (Morinus fixstars.py): apparent positions via
		#swe_fixstar_ut, same flags as the planets (tropical/sidereal
		#follows the configuration). Needs sefstars.txt in the ephemeris
		#path; missing stars are skipped silently.
		self.fixed_names = []
		self.fixed_short = []
		self.fixed_degree_ut = []
		self.fixed_latitude = []
		self.fixed_sign = []
		self.fixed_degree = []
		self.fixed_orb = []
		for disp, swename, short in FIXED_STARS:
			try:
				res = swe.fixstar_ut(swename, self.jul_day_UT, iflag)
				if len(res) == 4:
					ret, nm, dat, serr = res
				else:
					dat, nm, ret = res
				lon = float(dat[0]) % 360.0
				lat = float(dat[1])
			except Exception:
				continue
			s = int(lon // 30.0) % 12
			self.fixed_names.append(disp)
			self.fixed_short.append(short)
			self.fixed_degree_ut.append(lon)
			self.fixed_latitude.append(lat)
			self.fixed_sign.append(s)
			self.fixed_degree.append(lon - int(lon // 30.0) * 30.0)
			self.fixed_orb.append(2.0 if disp in ORB_2_DEG else 1.0)

							
		#available house systems:
		"""
		hsys= 	‘P’     Placidus
				‘K’     Koch
				‘O’     Porphyrius
				‘R’     Regiomontanus
				‘C’     Campanus
				‘A’ or ‘E’     Equal (cusp 1 is Ascendant)
				‘V’     Vehlow equal (Asc. in middle of house 1)
				‘X’     axial rotation system
				‘H’     azimuthal or horizontal system
				‘T’     Polich/Page (“topocentric” system)
				‘B’     Alcabitus
				‘G’     Gauquelin sectors
				‘M’     Morinus
		"""
		#houses calculation (hsys=P for Placidus)
		#check for polar circle latitude < -66 > 66
		if houses_override:
			self.jul_day_UT = swe.julday(houses_override[0],houses_override[1],houses_override[2],houses_override[3])
			
		if geolat > 66.0:
			geolat = 66.0
			print("polar circle override for houses, using 66 degrees")
		elif geolat < -66.0:
			geolat = -66.0
			print("polar circle override for houses, using -66 degrees")

		#sidereal houses
		if(openastrocfg['zodiactype']=="sidereal"):
			sh = swe.houses_ex(self.jul_day_UT,geolat,geolon,openastrocfg['houses_system'].encode("ascii"),swe.FLG_SIDEREAL)
		else:
			sh = swe.houses(self.jul_day_UT,geolat,geolon,openastrocfg['houses_system'].encode("ascii"))

		self.houses_degree_ut = list(sh[0])

		#RAMC (right ascension of the MC, ascmc[2]) for primary directions.
		#Falls back to sidereal time + east longitude if the houses tuple
		#has an unexpected shape in some pyswisseph versions.
		try:
			self.ramc = float(sh[1][2]) % 360.0
		except Exception:
			try:
				self.ramc = (swe.sidtime(self.jul_day_UT) * 15.0 + geolon) % 360.0
			except Exception:
				self.ramc = 0.0

		#arabic parts
		sun,moon,asc = self.planets_degree_ut[0],self.planets_degree_ut[1],self.houses_degree_ut[0]
		dsc,venus = self.houses_degree_ut[6],self.planets_degree_ut[3]	

		#offset
		offset = moon - sun
		
		#if a house degree is greater than 360 subtract 360; if below 0, add 360
		for i in range(len(self.houses_degree_ut)):
			#add offset
			#self.houses_degree_ut[i] += offset
			
			if self.houses_degree_ut[i] > 360.0:
				self.houses_degree_ut[i] = self.houses_degree_ut[i] - 360.0
			elif self.houses_degree_ut[i] < 0.0:
				self.houses_degree_ut[i] = self.houses_degree_ut[i] + 360.0		
		

		self.houses_degree = list(range(len(self.houses_degree_ut)))
		self.houses_sign = list(range(len(self.houses_degree_ut)))
		for i in range(12):
			for x in range(len(zodiac)):
				deg_low=float(x*30)
				deg_high=float((x+1)*30)
				if self.houses_degree_ut[i] >= deg_low:
					if self.houses_degree_ut[i] <= deg_high:
						self.houses_sign[i]=x
						self.houses_degree[i] = self.houses_degree_ut[i] - deg_low
						
		
		#mean apogee
		bm=self.planets_degree_ut[12]
		#mean north node
		mn=self.planets_degree_ut[10]
		#perigee lunaire moyen
		pl=self.planets_degree_ut[22]
		#perigee solaire moyen
		#define SE_NODBIT_MEAN          1
		#define SE_NODBIT_OSCU          2
		#define SE_NODBIT_OSCU_BAR     4
		#define SE_NODBIT_FOPOINT     256
		#Return: 4 tuples of 6 float (asc, des, per, aph)
		ps=swe.nod_aps_ut(self.jul_day_UT,0,swe.NODBIT_MEAN,iflag)
		pl=swe.nod_aps_ut(self.jul_day_UT,1,swe.NODBIT_MEAN,iflag)
		ps=ps[2][0]
		pl=pl[2][0]
		#print mn
		#print sun
		#print ps
		#print moon
		#print pl
		
		c= 1.517 * math.sin(2*math.radians(sun-mn))
		c+= -0.163 * math.sin(math.radians(sun-ps))
		c+= -0.128 * math.sin(2*math.radians(moon-sun))
		c+= 0.120 * math.sin(2*math.radians(moon-mn))
		c+= 0.107 * math.sin(2*math.radians(pl-mn))
		c+= 0.063 * math.sin(math.radians(3*sun-ps-2*mn))
		c+= 0.040 * math.sin(math.radians(moon+pl-2*sun))
		c+= -0.040 * math.sin(math.radians(moon+pl-2*mn))
		c+= 0.027 * math.sin(math.radians(moon-pl))
		c+= -0.027 * math.sin(math.radians(sun+ps-2*mn))
		c+= 0.015 * math.sin(2*math.radians(sun-pl))
		c+= -0.013 * math.sin(math.radians(moon+2*mn-pl-2*sun))
		c+= -0.013 * math.sin(math.radians(moon-2*mn-pl+2*sun))
		c+= -0.007 * math.sin(math.radians(2*moon+pl-3*sun))
		c+= 0.005 * math.sin(math.radians(3*moon-pl-2*mn))
		c+= -0.005 * math.sin(math.radians(3*moon-pl-2*sun))
		#print c
		
		sbm=sun-bm
		if sbm < 0: sbm += 360
		if sbm > 180.0: sbm -= 180
		print("sun %s black moon %s sun-bm %s=%s" % (sun,bm,sun-bm,sbm))

		q=12.333
		if sbm < 60.0:
			print('sbm<60')
			c= q * math.sin(1.5*math.radians(sbm))
		elif sbm > 120.0:
			print('sbm>120')
			c= q * math.cos(1.5*math.radians(sbm))
		else:
			print('sbm 60-120')
			c= -q * math.cos(3.0*math.radians(sbm))

		true_lilith=c

		def true_lilith_calc(sun,lilith):
			deg=sun-lilith
			q=12.333
			if deg < 0.0: deg+=360.0
			if deg > 180.0: deg -= 180.0

			if deg < 60.0: return q * math.sin(1.5*math.radians(deg)) - 1.892 * math.sin(3*math.radians(deg))
			elif deg > 120.0: return q * math.cos(1.5*math.radians(deg)) + 1.892 * math.sin(3*math.radians(deg))
			elif deg < 100.0: return -q * math.cos(3.0*math.radians(deg)) + 0.821 * math.cos(4.5*math.radians(deg))
			else: return -q * math.cos(3.0*math.radians(deg))

		def true_lilith_calc2(sun,lilith):
			deg=sun-lilith
			q=12.333
			if deg < 0.0: deg += 360.0
			if deg > 180.0: deg -= 180.0

			if deg < 60.0: return q * math.sin(1.5*math.radians(deg))
			elif deg > 120.0: return q * math.cos(1.5*math.radians(deg))
			else: return -q * math.cos(3.0*math.radians(deg))

		true_lilith=true_lilith_calc2(sun,bm)
		#print c
		"""
		if sbm < 60.0:
			print 'sbm 0-60'
			c=  q * math.sin(1.5*math.radians(sbm)) - 0.0917
		elif sbm >= 60.0 and sbm < 120.0:
			print 'sbm 60-120'
			c= -q * math.cos(3*math.radians(sbm)) - 0.0917
		elif sbm >= 120.0 and sbm < 240.0:
			print 'sbm 120-240'
			c= q * math.cos(1.5*math.radians(sbm)) - 0.0917
		elif sbm >= 240.0 and sbm < 300.0:
			print 'sbm 240-300'
			c= q * math.cos(3*math.radians(sbm)) - 0.0917
		else:
			print 'sbm 300-360'
			c= -q * math.sin(1.5*math.radians(sbm)) - 0.0917
		"""
		c+= - 0.117 * math.sin(math.radians(sun-ps))
		#print c
		
		#c+= x * -0.163 * math.sin(math.radians(sun-ps))
		#c+= x * -0.128 * math.sin(2*math.radians(moon-sun))
		#c+= x * 0.120 * math.sin(2*math.radians(moon-bm))
		#c+= x * 0.107 * math.sin(2*math.radians(pl-bm))
		#c+= x * 0.063 * math.sin(math.radians(3*sun-ps-2*bm))
		#c+= x * 0.040 * math.sin(math.radians(moon+pl-2*sun))
		#c+= x * -0.040 * math.sin(math.radians(moon+pl-2*bm))
		#c+= x * 0.027 * math.sin(math.radians(moon-pl))
		#c+= x * -0.027 * math.sin(math.radians(sun+ps-2*bm))
		#c+= x * 0.015 * math.sin(2*math.radians(sun-pl))
		#c+= x * -0.013 * math.sin(math.radians(moon+2*bm-pl-2*sun))
		#c+= x * -0.013 * math.sin(math.radians(moon-2*bm-pl+2*sun))
		#c+= x * -0.007 * math.sin(math.radians(2*moon+pl-3*sun))
		#c+= x * 0.005 * math.sin(math.radians(3*moon-pl-2*bm))
		#c+= x * -0.005 * math.sin(math.radians(3*moon-pl-2*sun))
		

		#compute additional points and angles
		#list index 23 is asc, 24 is Mc, 25 is Dsc, 26 is Ic
		self.planets_degree_ut[23] = self.houses_degree_ut[0]
		self.planets_degree_ut[24] = self.houses_degree_ut[9]
		self.planets_degree_ut[25] = self.houses_degree_ut[6]
		self.planets_degree_ut[26] = self.houses_degree_ut[3]
		
		#sect: diurnal chart if the Sun is above the horizon (houses 7-12),
		#that is, between Dsc and Asc in zodiacal order
		day_chart = (sun - asc) % 360.0 >= 180.0

		#list index 27 is lot of fortune: ASC + Moon - Sun (day), ASC + Sun - Moon (night)
		#list index 28 is lot of spirit: ASC + Sun - Moon (day), ASC + Moon - Sun (night)
		if day_chart:
			self.planets_degree_ut[27] = asc + (moon - sun)
			self.planets_degree_ut[28] = asc + (sun - moon)
		else:
			self.planets_degree_ut[27] = asc + (sun - moon)
			self.planets_degree_ut[28] = asc + (moon - sun)
		#list index 29 is South Node
		self.planets_degree_ut[29] = self.planets_degree_ut[10] - 180.0
		#list index 30 is marriage pars
		self.planets_degree_ut[30] = (asc+dsc)-venus
		#list index 31 is black sun
		self.planets_degree_ut[31] = swe.nod_aps_ut(self.jul_day_UT,0,swe.NODBIT_MEAN,swe.FLG_SWIEPH)[3][0]
		#list index 32 is vulcanus
		self.planets_degree_ut[32] = 31.1 + (self.jul_day_UT-2425246.5) * 0.00150579
		#list index 33 is persephone
		self.planets_degree_ut[33] = 240.0 + (self.jul_day_UT-2425246.5) * 0.002737829
		#list index 34 is true lilith (own calculation)
		self.planets_degree_ut[34] = self.planets_degree_ut[12] + true_lilith
		#swiss ephemeris version of true lilith
		#self.planets_degree_ut[34] = swe.nod_aps_ut(self.jul_day_UT,1,swe.NODBIT_OSCU,swe.FLG_SWIEPH)[3][0]
		#list index 35 is lot of infortune: ASC + Mars - Saturn (day), ASC + Saturn - Mars (night)
		mars = self.planets_degree_ut[4]
		saturn = self.planets_degree_ut[6]
		if day_chart:
			self.planets_degree_ut[35] = asc + mars - saturn
		else:
			self.planets_degree_ut[35] = asc + saturn - mars

		#normalize list index 23 to 35
		for i in range(23,36):
			while ( self.planets_degree_ut[i] < 0 ): self.planets_degree_ut[i]+=360.0
			while ( self.planets_degree_ut[i] > 360.0): self.planets_degree_ut[i]-=360.0
	
			#get zodiac sign
			for x in range(12):
				deg_low=float(x*30.0)
				deg_high=float((x+1.0)*30.0)
				if self.planets_degree_ut[i] >= deg_low:
					if self.planets_degree_ut[i] <= deg_high:
						self.planets_sign[i]=x
						self.planets_degree[i] = self.planets_degree_ut[i] - deg_low
						self.planets_retrograde[i] = False

		#lunar phase, anti-clockwise degrees between sun and moon
		# --- Dodecatemorias (Morinus antiscia.calcDodecatemoria) ---
		# Longitud dodecatemoria para cada cuerpo y cada cuspide.
		# Se calculan sobre planets_degree_ut / houses_degree_ut ya
		# normalizados (tropical o sideral segun configuracion).
		self.planets_dodecatemoria_ut = [calc_dodecatemoria(v) for v in self.planets_degree_ut]
		self.planets_dodecatemoria_sign = []
		self.planets_dodecatemoria = []
		for v in self.planets_dodecatemoria_ut:
			s = int(v // 30.0) % 12
			self.planets_dodecatemoria_sign.append(s)
			self.planets_dodecatemoria.append(v - s * 30.0)
		self.houses_dodecatemoria_ut = [calc_dodecatemoria(v) for v in self.houses_degree_ut]
		self.houses_dodecatemoria_sign = []
		self.houses_dodecatemoria = []
		for v in self.houses_dodecatemoria_ut:
			s = int(v // 30.0) % 12
			self.houses_dodecatemoria_sign.append(s)
			self.houses_dodecatemoria.append(v - s * 30.0)

		# --- Antiscia y contraantiscia (Morinus antiscia.calc) ---
		# Reflejo sobre el eje Cancer 0 / Capricornio 0 (simetria de
		# declinacion). Son tropicales por definicion: calc_antiscion()
		# usa self.ayanamsa para volver al zodiaco configurado.
		self.planets_antiscia_ut = []
		self.planets_contra_ut = []
		for v in self.planets_degree_ut:
			a, c = calc_antiscion(v, self.ayanamsa)
			self.planets_antiscia_ut.append(a)
			self.planets_contra_ut.append(c)
		self.houses_antiscia_ut = []
		self.houses_contra_ut = []
		for v in self.houses_degree_ut:
			a, c = calc_antiscion(v, self.ayanamsa)
			self.houses_antiscia_ut.append(a)
			self.houses_contra_ut.append(c)

		ddeg=moon-sun
		if ddeg<0: ddeg+=360.0
		step=360.0 / 28.0
		print(moon,sun,ddeg)
		for x in range(28):
			low=x*step
			high=(x+1)*step
			if ddeg >= low and ddeg < high: mphase=x+1
		sunstep=[0,30,40,50,60,70,80,90,120,130,140,150,160,170,180,210,220,230,240,250,260,270,300,310,320,330,340,350]
		for x in range(len(sunstep)):
			low=sunstep[x]
			#if x is 27: high=360
			if (x == 27): high=360
			else: high=sunstep[x+1]
			if ddeg >= low and ddeg < high: sphase=x+1
		self.lunar_phase={
					"degrees":ddeg,
					"moon_phase":mphase,
					"sun_phase":sphase
		}
		
		#close swiss ephemeris
		swe.close()

def years_diff(y1, m1, d1, h1 , y2, m2, d2, h2):
		swe.set_ephe_path(ephe_path)
		jd1 = swe.julday(y1,m1,d1,h1)
		jd2 = swe.julday(y2,m2,d2,h2)
		jd = jd1 + ( (jd2-jd1) / 365.248193724 )
		#jd = jd1 + ( (jd2-jd1) / 365.248193724 )
		y, mth, d, hourf = swe.revjul(jd, swe.GREG_CAL)
		return datetime.datetime(y,mth,d) + datetime.timedelta(hours=hourf)
