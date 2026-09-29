import sys
from openastromod import primary as pe
import swisseph as swe

# carta de la captura: Sant Boi, 1987-04-09 14:00:30 +02:00 -> 12:00:30 UT
jd = swe.julday(1987,4,9,12.0+0.5/60)
geolat, geolon = 41.3436, 2.0367
ramc = swe.houses(jd, geolat, geolon, b'P')[1][2]

def dms(x):
    s = '-' if x < 0 else '+'
    x = abs(x); d = int(x); m = int((x-d)*60); sec = round(((x-d)*60-m)*60)
    return '%s%02d°%02d\'%02d"' % (s,d,m,sec)

# un par en oposicion: significador y promisor separados ~180
sig_lon, sig_lat = 20.0, 0.0
pro_lon = 200.3          # oposicion casi exacta
arc_now = 39.5           # arco dirigido de ejemplo

print('significador %.1f  promisor %.1f  (separacion %.1f = oposicion)' % (sig_lon, pro_lon, (pro_lon-sig_lon)%360))
print('arco dirigido actual: %.2f\n' % arc_now)

for label, ray in [('ray=0.0   (lo que hace el codigo)', 0.0),
                   ('ray=180.0 (lo correcto)', 180.0)]:
    exact = pe.arc_of_direction(sig_lon, sig_lat, pro_lon, 0.0, ray, geolat, ramc, jd)
    delta = (exact - arc_now + 180.0) % 360.0 - 180.0
    print('%-34s arco exacto %8.3f  ->  orbe mostrado %s' % (label, exact, dms(abs(delta))))

print('\ndiferencia entre ambos: %s' % dms(abs(
    pe.arc_of_direction(sig_lon,sig_lat,pro_lon,0.0,180.0,geolat,ramc,jd) -
    pe.arc_of_direction(sig_lon,sig_lat,pro_lon,0.0,0.0,geolat,ramc,jd))))
print('\n(conjuncion, para comprobar que ray=0 SI es correcto ahi:)')
e0 = pe.arc_of_direction(sig_lon, sig_lat, 22.0, 0.0, 0.0, geolat, ramc, jd)
print('   promisor 22.0, ray=0 -> arco %.3f  orbe %s' % (e0, dms(abs((e0-arc_now+180)%360-180))))
