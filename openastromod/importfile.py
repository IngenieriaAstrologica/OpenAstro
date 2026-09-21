#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    This file is part of openastro.org.

    OpenAstro.org is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with OpenAstro.org.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import with_statement

import datetime
import re

from xml.dom.minidom import parseString

from codecs import EncodedFile

def _getText(nodelist):
	"""Internal function to return text from nodes
	"""
	rc = ""
	for node in nodelist:
		if node.nodeType == node.TEXT_NODE:
			rc = rc + node.data
	return rc

def getOAC(filename):
	f=open(filename)	
	dom = parseString(f.read())
	f.close()
	
	valid=['name','datetime','location','altitude','latitude','longitude','countrycode',
			'timezone','geonameid','extra']
	output=[]
	for a in dom.getElementsByTagName("openastrochart"):
		output.append({})
		for i in range(len(valid)):
			output[-1][valid[i]]=_getText(a.getElementsByTagName(valid[i])[0].childNodes)
			
	#close dom
	dom.unlink()
	#return results
	return output

def getOroboros(filename):
	f=open(filename)
	dom = parseString(f.read())
	f.close()
	output=[]
	for a in dom.getElementsByTagName("ASTROLOGY"):
		output.append({})
		output[-1]['name']=_getText(a.getElementsByTagName('NAME')[0].childNodes)
		output[-1]['datetime']=_getText(a.getElementsByTagName('DATETIME')[0].childNodes)
		output[-1]['location']=_getText(a.getElementsByTagName('LOCATION')[0].childNodes)
		output[-1]['altitude']=a.getElementsByTagName('LOCATION')[0].attributes['altitude'].value
		output[-1]['latitude']=a.getElementsByTagName('LOCATION')[0].attributes['latitude'].value
		output[-1]['longitude']=a.getElementsByTagName('LOCATION')[0].attributes['longitude'].value
		output[-1]['countryname']=_getText(a.getElementsByTagName('COUNTRY')[0].childNodes)
		output[-1]['zoneinfo']=a.getElementsByTagName('COUNTRY')[0].attributes['zoneinfo'].value
	dom.unlink()
	return output

def getSkylendar(filename):
	f=open(filename)
	dom = parseString(f.read())
	f.close()
	output=[]
	for a in dom.getElementsByTagName("DATASET"):
		output.append({})
		output[-1]['name']=_getText(a.getElementsByTagName('NAME')[0].childNodes)
		output[-1]['year']=a.getElementsByTagName('DATE')[0].attributes['Year'].value
		output[-1]['month']=a.getElementsByTagName('DATE')[0].attributes['Month'].value
		output[-1]['day']=a.getElementsByTagName('DATE')[0].attributes['Day'].value
		
		tz=a.getElementsByTagName('DATE')[0].attributes['Timezone'].value.split(':')
		if float(tz[0]) < 0:
			output[-1]['timezone']=float(tz[0])+(float(tz[1]/60.0)/-1)
		else:
			output[-1]['timezone']=float(tz[0])+float(tz[1]/60.0)

		output[-1]['daylight']=a.getElementsByTagName('DATE')[0].attributes['Daylight'].value
		hm=a.getElementsByTagName('DATE')[0].attributes['Hm'].value
		output[-1]['hour']=hm.split(':')[0]
		output[-1]['minute']=hm.split(':')[1]
		output[-1]['location']=_getText(a.getElementsByTagName('PLACE')[0].childNodes)
		
		lat=a.getElementsByTagName('PLACE')[0].attributes['Latitude'].value.split(':')
		if float(lat[0]) < 0:
			output[-1]['latitude'] = float(lat[0])+(float(lat[1]/60.0)/-1)
		else:
			output[-1]['latitude'] = float(lat[0])+float(lat[1]/60.0)
			
		lon=a.getElementsByTagName('PLACE')[0].attributes['Longitude'].value.split(':')
		if float(lon[0]) < 0:
			output[-1]['longitude'] = float(lon[0])+(float(lon[1]/60.0)/-1)
		else:
			output[-1]['longitude'] = float(lon[0])+float(lon[1]/60.0)
					
		output[-1]['zoneinfofile']=a.getElementsByTagName('COUNTRY')[0].attributes['ZoneInfoFile'].value
		output[-1]['countryname']=_getText(a.getElementsByTagName('COUNTRY')[0].childNodes)
		
		dom.unlink()
	return output
	
def getAstrolog32(filename):
	"""
	examples:
@0102  ; Astrolog chart info.
/qb 6 23 1972  3:00:00 ST -1:00   5:24:00E 43:18:00N
/zi "Zinedine Zidane" "Marseille"	
@0102  ; Astrolog32 chart info.

; Date is in American format: month day year.

/qb 10 27 1980 10:20:00 ST -1:00  14:39'00E 50:11'00N
/zi "Honzik" "Brandys nad Labem"	
	"""
	d={}
	h=open(filename)
	f=EncodedFile(h,"utf-8","latin-1")
	for line in f.readlines():
		if line[0:3] == "/qb":
			s0=line.strip().split(' ')
			s=[]
			for j in range(len(s0)):
				if s0[j]!='':
					s.append(s0[j])
			d['month']=s[1]
			d['day']=s[2]
			d['year']=s[3]
			d['hour'],d['minute'],d['second']=0,0,0
			for x in range(len(s[4].split(':'))):
				if x == 0:
					d['hour'] = s[4].split(':')[0]
				if x == 1:
					d['minute'] = s[4].split(':')[1]
				if x == 2:
					d['second'] = s[4].split(':')[2]

			#timezone
			tz=s[6].split(':')
			d['timezone']=float(tz[0])+float(tz[1])/60.0
			if float(tz[0]) < 0:
				d['timezone']=d['timezone']/-1.0
			#longitude
			lon=s[7].split(':')
			lon.append(lon[-1][-1])
			lon[-2]=lon[-2][0:2]
			d['longitude']=float(lon[0])+(float(lon[1])/60.0)
			if len(lon) > 3:
				d['longitude']+=float(lon[2])/3600.0
			if lon[-1] == 'W':
				d['longitude'] = d['longitude']/-1.0
			#latitude
			lon=s[8].split(':')
			lon.append(lon[-1][-1])
			lon[-2]=lon[-2][0:2]
			d['latitude']=float(lon[0])+(float(lon[1])/60.0)
			if len(lon) > 3:
				d['latitude']+=float(lon[2])/3600.0
			if lon[-1] == 'S':
				d['latitude'] = d['latitude']/-1.0			
			
		if line[0:3] == "/zi":
			s0=line.strip().split('"')
			s=[]
			for j in range(len(s0)):
				if s0[j] != '' and s0[j] != ' ':
					s.append(s0[j])
			d['name']=s[1]
			d['location']=s[2]
	f.close()
	return [d]


#Kepler/CPA record layout, one record per line, fields introduced by a
#backslash tag.  Only the tags below are used by this importer:
#
#  \A>  secondary chart (the moment the chart was drawn); ignored
#  \S>  the natal subject: date, clock time, zone, latitude, longitude, tolerance
#  \N>  name
#  \L>  place name
#  \D>  classification codes plus a free-text note
#
#The numeric block of \A> and \S> is fixed width and space padded, so
#"1988- 6-10 21:33" and " 325- 5-20 12: 0" are both single date/time fields
#and must not be split on whitespace.  \S> carries one float more than \A>:
#the birth time tolerance in decimal hours (12.00 = time unknown, chart cast
#for noon).
KEPLER_TAG = re.compile('\\\\([A-Za-z0-9])>')
#year-month-day hour:minute, every part space padded, the year possibly BC
KEPLER_DATETIME = re.compile('^\\s*(-?\\d{1,4})-\\s*(\\d{1,2})-\\s*(\\d{1,2})\\s+(\\d{1,2}):\\s*(\\d{1,2})\\s*(.*)$')
KEPLER_FLOAT = re.compile('-?\\d+\\.\\d+')
#leading classification codes of \D>: a kind (:P a person, :E an event) and
#for a person a sex (:V a man, :H a woman, :N an institution).  Anything
#after those is the note itself, so the sex letter only counts when it fills
#a whole colon separated field.
KEPLER_CODES = re.compile('^:([PE])(?::([VHN])(?=:|$))?:?')
#the corpus holds stray NUL and ESC bytes inside the text fields
KEPLER_CONTROL = re.compile('[\\x00-\\x1f\\x7f]')

def _keplerText(text):
	"""Internal function to clean one Kepler/CPA text field
	"""
	return KEPLER_CONTROL.sub('',text).strip()

def _keplerDecode(raw):
	"""Internal function to decode a Kepler/CPA file to text

	The format is single byte and never UTF-8, but it is not one codepage
	either.  Files written by the DOS programs are CP850, where the Spanish
	accents sit in 0x80-0xA8, while a few later ones are ISO-8859-1, where
	they sit in 0xC0-0xFF.  Reading CP850 as ISO-8859-1 turns every "n with
	a tilde" into a currency sign, so choose by the range the file actually
	uses.  ISO-8859-1 is the fallback because it decodes any byte at all,
	which is what keeps a binary file from raising.
	"""
	try:
		return raw.decode("utf-8")
	except UnicodeDecodeError:
		pass
	dos=0
	latin=0
	for byte in bytearray(raw):
		if 0x80 <= byte <= 0xA8:
			dos += 1
		elif 0xC0 <= byte <= 0xFF:
			latin += 1
	if dos > latin:
		try:
			return raw.decode("cp850")
		except (UnicodeDecodeError, LookupError):
			pass
	return raw.decode("iso-8859-1")

def _keplerSegments(line):
	"""Internal function to split one Kepler/CPA line into its backslash tags

	Returns a dict tag -> text.  A tag repeated on the same line keeps its
	first occurrence, which is how the Kepler programs read them back.
	"""
	segments={}
	marks=[(m.group(1),m.start(),m.end()) for m in KEPLER_TAG.finditer(line)]
	for i in range(len(marks)):
		tag,start,end = marks[i]
		stop = marks[i+1][1] if i+1 < len(marks) else len(line)
		if tag not in segments:
			segments[tag]=line[end:stop]
	return segments

def _keplerRecord(line):
	"""Internal function to turn one Kepler/CPA line into a chart dict

	Returns None when the line carries no usable natal segment, so that a
	corrupt line never aborts the whole file.
	"""
	segments=_keplerSegments(line)
	if 'S' not in segments:
		return None
	m=KEPLER_DATETIME.match(segments['S'])
	if not m:
		return None
	year,month,day,hour,minute,tail = m.groups()
	numbers=KEPLER_FLOAT.findall(tail)
	if len(numbers) < 3:
		return None

	d={}
	d['year']=int(year)
	d['month']=int(month)
	d['day']=int(day)
	d['hour']=int(hour)
	d['minute']=int(minute)
	#Reject the typing damage the corpus carries - month 0, day 82, 7:80,
	#82:00 - and BC years, which no chart in openastro can hold.  datetime
	#also settles 1909-02-29 and the like, which a range check would pass.
	if d['year'] < 1 or not 0 <= d['hour'] <= 23 or not 0 <= d['minute'] <= 59:
		return None
	try:
		datetime.date(d['year'],d['month'],d['day'])
	except ValueError:
		return None

	#The zone field is the correction to ADD to the clock time to obtain UT,
	#i.e. the negated UTC offset: Spain on CET is stored as -1.00.  Hand it
	#on as a plain UTC offset so that it reads like every other importer.
	#Written as a subtraction to keep a zone of 0.00 from becoming -0.0.
	d['timezone']=0.0-float(numbers[0])
	d['latitude']=float(numbers[1])
	d['longitude']=float(numbers[2])
	if abs(d['latitude']) > 90 or abs(d['longitude']) > 180:
		return None
	#birth time tolerance in decimal hours; absent on a few old records
	d['accuracy']=float(numbers[3]) if len(numbers) > 3 else None

	d['name']=_keplerText(segments.get('N',''))
	d['location']=_keplerText(segments.get('L',''))

	notes=_keplerText(segments.get('D',''))
	codes=KEPLER_CODES.match(notes)
	d['sex']=''
	if codes:
		if codes.group(1) == 'P' and codes.group(2) in ('V','H'):
			d['sex']='M' if codes.group(2) == 'V' else 'F'
		notes=notes[codes.end():].strip()
	d['notes']=notes
	return d

def getKepler(filename):
	"""Read a Kepler/CPA chart database and return every record it holds

	example (fields are the fixed width ones described above):
\\A>1988- 6-10 21:33 -1.00  40.25   -3.70\\S>1952-11-27 17:10 -1.00  38.10   -0.95  0.08\\N>A Name\\L>A Town\\D>:P:V:a note

	Kepler/CPA shares the *.dat extension with Astrolog32, so the format is
	recognised by content: an Astrolog32 file has no backslash tagged natal
	segment and yields an empty list here, exactly as a file of any other
	kind would.  Decoding never fails, so a binary file also comes back
	empty rather than raising.
	"""
	h=open(filename,"rb")
	raw=h.read()
	h.close()
	text=_keplerDecode(raw)
	output=[]
	for line in text.replace("\r\n","\n").replace("\r","\n").split("\n"):
		if not line.strip():
			continue
		try:
			record=_keplerRecord(line)
		except (ValueError, IndexError):
			record=None
		if record is not None:
			output.append(record)
	return output
