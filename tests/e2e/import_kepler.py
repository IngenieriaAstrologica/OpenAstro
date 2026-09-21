# -*- coding: utf-8 -*-
"""End to end: run openAstroInstance.importKepler for real and read the
people database back, then recompute a chart from a stored row and check
the UT it implies."""
import os, sys, sqlite3, importlib.util, tempfile, shutil

WT = os.environ.get("OA_ROOT") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# openAstroCfg() creates and writes ~/.openastro.org/, which on a real HOME
# is the user's live chart database. Never let it see the real one.
HOME = tempfile.mkdtemp(prefix="oa-e2e-")
os.environ["HOME"] = HOME
os.chdir(WT)
sys.path.insert(0, WT)
sys.argv = ["openastro"]

spec = importlib.util.spec_from_loader(
    "oa", importlib.machinery.SourceFileLoader("oa", os.path.join(WT, "openastro")))
oa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oa)
print("module loaded, HOME =", HOME)

oa.cfg = oa.openAstroCfg()
oa.db = oa.openAstroSqlite()
oa.openAstro = oa.openAstroInstance()
print("instances built; peopledb =", oa.cfg.peopledb)

# a Kepler file of our own, same shape as the format, nobody real in it
BS = chr(92)
def rec(date, zone, lat, lon, acc, name, place, note):
    return (BS + "A>2002-11- 4 12:17 -1.00  38.35   -0.48"
            + BS + "S>%s %s %s %s %s" % (date, zone, lat, lon, acc)
            + BS + "N>" + name + BS + "L>" + place + BS + "D>" + note)

lines = [
    # Capricorn ingress of 2002, one moment written in four time zones.
    # All four must land on the same UTC row in the database.
    rec("2002-12-22  2:15", "-1.00", " 38.35", "  -0.48", "0.02", "Ingress CET",   "Alicante", ":E:ingress"),
    rec("2002-12-22  4:15", "-3.00", " 33.33", "  44.40", "0.02", "Ingress UTC+3", "Baghdad",  ":E:ingress"),
    rec("2002-12-21 20:15", " 5.00", " 40.67", " -73.97", "0.02", "Ingress UTC-5", "New York", ":E:ingress"),
    rec("2002-12-21 21:15", " 4.00", "-34.33", " -58.50", "0.02", "Ingress UTC-4", "Elsewhere",":E:ingress"),
    # a person, with accents and a sex code
    rec("1952-11-27 17:10", "-1.00", " 38.10", "  -0.95", "0.08", "Juana Mu\xf1oz P\xe9rez", "Alcal\xe1", ":P:H:a made up case"),
    # corrupt lines that must not reach the database
    rec("1952- 0-27 17:10", "-1.00", " 38.10", "  -0.95", "0.08", "Bad Month", "x", ":P:V:"),
    rec("1909- 2-29 12: 0", " 0.00", " 40.40", "  -3.70", "0.00", "Bad Day",   "x", ":P:V:"),
    rec("1952-11-27 17:80", "-1.00", " 38.10", "  -0.95", "0.08", "Bad Minute","x", ":P:V:"),
]
src = os.path.join(HOME, "SAMPLE.DAT")
open(src, "wb").write(("\r\n".join(lines) + "\r\n").encode("iso-8859-1"))

before = sqlite3.connect(oa.cfg.peopledb).execute("SELECT count(*) FROM event_natal").fetchone()[0]
oa.openAstro.importKepler(src)
con = sqlite3.connect(oa.cfg.peopledb)
con.row_factory = sqlite3.Row
rows = con.execute("SELECT name,year,month,day,hour,geolat,geolon,timezone,location,notes,timezonestr"
                   " FROM event_natal ORDER BY id").fetchall()
print("rows before=%d after=%d" % (before, len(rows)))
print()
print("%-22s %-18s %8s %8s %6s  %-16s %s" % ("name", "UTC stored", "lat", "lon", "tz", "location", "notes"))
for r in rows:
    print("%-22s %04d-%02d-%02d %05.2f %8.2f %8.2f %6.2f  %-16s %s" % (
        r['name'], int(r['year']), int(r['month']), int(r['day']), float(r['hour']),
        float(r['geolat']), float(r['geolon']), float(r['timezone']), r['location'], r['notes']))

utcs = set((int(r['year']), int(r['month']), int(r['day']), round(float(r['hour']), 4))
           for r in rows if r['name'].startswith("Ingress"))
print()
print("distinct UTC instants among the four ingress rows:", utcs)
assert len(utcs) == 1, "the four zones did not converge on one UTC instant"

names = [r['name'] for r in rows]
for bad in ("Bad Month", "Bad Day", "Bad Minute"):
    assert bad not in names, "%s reached the database" % bad
print("corrupt rows kept out of the database: yes")

# the stored UTC must actually be the ingress: Sun at 270 deg
import swisseph as swe
y, mo, d, h = utcs.pop()
jd = swe.julday(y, mo, d, h)
lon = swe.calc_ut(jd, swe.SUN)[0][0]
print("Sun longitude at the stored UTC: %.4f deg (270.0000 = exact Capricorn ingress)" % lon)
assert abs(lon - 270.0) < 0.01

# accents survived the whole chain
person = [r for r in rows if "oz" in r['name']][0]
print("person row name=%r location=%r notes=%r" % (person['name'], person['location'], person['notes']))
assert person['name'] == "Juana Mu\xf1oz P\xe9rez"
assert person['location'] == "Alcal\xe1"

# a non Kepler .dat must be a clean no-op
astro = os.path.join(HOME, "ASTROLOG.DAT")
open(astro, "w").write('@0102  ; Astrolog chart info.\n'
                       '/qb 6 23 1972  3:00:00 ST -1:00   5:24:00E 43:18:00N\n'
                       '/zi "A Name" "A Town"\n')
n0 = len(rows)
oa.openAstro.importKepler(astro)
n1 = sqlite3.connect(oa.cfg.peopledb).execute("SELECT count(*) FROM event_natal").fetchone()[0]
print("astrolog32 .dat through importKepler: rows %d -> %d (unchanged = rejected)" % (n0, n1))
assert n0 == n1

# empty, binary and missing files must not raise
for name, blob in (("EMPTY.DAT", b""), ("BINARY.DAT", bytes(range(256)) * 8)):
    p = os.path.join(HOME, name)
    open(p, "wb").write(blob)
    oa.openAstro.importKepler(p)
oa.openAstro.importKepler(os.path.join(HOME, "DOES-NOT-EXIST.DAT"))
oa.openAstro.importKepler(HOME)
n2 = sqlite3.connect(oa.cfg.peopledb).execute("SELECT count(*) FROM event_natal").fetchone()[0]
print("empty / binary / missing / directory: no raise, rows still %d" % n2)
assert n2 == n1

shutil.rmtree(HOME, ignore_errors=True)
print()
print("E2E_OK")
