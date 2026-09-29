"""?Cae mi funcion de intensidad dentro del RNG=15 que declara _0MES.DHQ?"""
import sys, random, statistics
from openastromod import harmogram as H, swiss
import swisseph as swe

B = (swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS,
     swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO)

# valor esperado analitico para pares al azar
import math
k = -math.log(H.WEIGHT_AT_ORB)
frac = 2*H.ORB/360.0
# media de la gaussiana truncada sobre [0,orbe]
N = 200000
mean_w = sum(math.exp(-k*(i/N)**2) for i in range(N))/N
print('fraccion del circulo dentro del orbe : %.4f' % frac)
print('peso medio dentro del orbe           : %.4f' % mean_w)
print('esperanza por par                    : %.4f' % (frac*mean_w))
print('esperanza con 10x10 = 100 pares      : %.2f   (RNG/2 = 7.5)' % (100*frac*mean_w))
print()

# --- transitos armonicos reales: radix 1987 contra un ano de cielo ---
radix = swiss.longitudes_at(swe.julday(1987, 4, 9, 12.0), B)
jd0 = swe.julday(2026, 1, 1, 0.0)
vals = {n: [] for n in H.HARMONICS}
for step in range(0, 366*4):          # un ano, cada 6 horas
    jd = jd0 + step*0.25
    mov = swiss.longitudes_at(jd, B)
    for n in H.HARMONICS:
        vals[n].append(H.intensity(radix, mov, n))

allv = [v for n in vals for v in vals[n]]
print('TRANSITOS ARMONICOS, radix 1987 x 2026 (10x10, 1464 momentos x 12 armonicos)')
print('   minimo %.2f   media %.2f   p99 %.2f   maximo %.2f' % (
    min(allv), statistics.mean(allv), sorted(allv)[int(.99*len(allv))], max(allv)))
over = sum(1 for v in allv if v > 15.0)
print('   por encima de 15: %d de %d  (%.3f%%)' % (over, len(allv), 100.0*over/len(allv)))
print()
for n in H.HARMONICS:
    print('   H%-2d  min %5.2f  media %5.2f  max %5.2f' % (n, min(vals[n]), statistics.mean(vals[n]), max(vals[n])))

# --- armograma natal: 10 cuerpos contra si mismos = 45 pares ---
print('\nARMOGRAMA NATAL (mismo conjunto, 45 pares)')
nat = []
for step in range(0, 366*4):
    jd = jd0 + step*0.25
    mov = swiss.longitudes_at(jd, B)
    for n in H.HARMONICS:
        nat.append(H.intensity(mov, mov, n, same_set=True))
print('   minimo %.2f   media %.2f   p99 %.2f   maximo %.2f  (45*%.4f = %.2f esperado)' % (
    min(nat), statistics.mean(nat), sorted(nat)[int(.99*len(nat))], max(nat), frac*mean_w, 45*frac*mean_w))
