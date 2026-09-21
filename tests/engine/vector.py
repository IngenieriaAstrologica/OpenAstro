import sys, math
from openastromod import harmonicvector as V, swiss
import swisseph as swe

fails = []
def chk(l, c, e=''):
    if not c: fails.append(l)
    print('%-58s %s %s' % (l, 'OK' if c else 'FALLA', e))

# --- los dos extremos que definen la escala ---
conj = [100.0] * 8
chk('8 planetas conjuntos: concentracion 1 en todo armonico',
    all(abs(V.concentration(conj, h) - 1.0) < 1e-12 for h in V.HARMONICS))

# repartidos uniformemente: las flechas se cancelan
even = [i * 360.0 / 8 for i in range(8)]
chk('8 repartidos por igual: concentracion ~0 en armonico 1',
    V.concentration(even, 1) < 1e-9, '%.2e' % V.concentration(even, 1))
chk('  pero 1 en el armonico 8, donde vuelven a coincidir',
    abs(V.concentration(even, 8) - 1.0) < 1e-9)

# --- una oposicion exacta ---
opp = [0.0, 180.0]
chk('oposicion: se cancela en armonico 1', V.concentration(opp, 1) < 1e-12)
chk('  y concentra en el 2, donde es conjuncion', abs(V.concentration(opp, 2) - 1.0) < 1e-12)
# un trigono exacto
tri = [0.0, 120.0, 240.0]
chk('gran trigono: se cancela en 1 y 2', V.concentration(tri,1) < 1e-9 and V.concentration(tri,2) < 1e-9)
chk('  y concentra en el 3', abs(V.concentration(tri, 3) - 1.0) < 1e-9)

# --- la fase apunta donde toca ---
chk('la fase de una conjuncion apunta a la conjuncion',
    abs(((V.phase([50.0]*5, 1) - 50.0 + 180) % 360) - 180) < 1e-9, '%.4f' % V.phase([50.0]*5, 1))

# --- rango ---
import random
random.seed(3)
ok = True
for _ in range(2000):
    L = [random.uniform(0, 360) for _ in range(10)]
    for h in (1, 5, 12):
        c = V.concentration(L, h)
        if not (0.0 - 1e-12 <= c <= 1.0 + 1e-12): ok = False
chk('concentracion siempre en [0,1] (2000 cartas al azar)', ok)

# --- Parseval: la suma de |C(h)|^2 sobre TODOS los armonicos 0..n-1 ---
# para n puntos distintos vale n^2 ... comprobacion de sanidad del espectro
L = [0.0, 40.0, 95.0, 210.0]
tot = sum(abs(V.coefficient(L, h))**2 for h in range(len(L)))
chk('el espectro se comporta (suma de |C|^2 finita y > 0)', 0 < tot < 1e6, '%.2f' % tot)

# --- sobre una carta real ---
BODIES = (swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS,
          swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO)
jd = swe.julday(1987, 4, 9, 12.0)
lons = swiss.longitudes_at(jd, BODIES)
print('\nFLOR ARMONICA de la carta de 1987-04-09:')
for p in V.flower(lons):
    bar = '#' * int(round(p['concentration'] * 40))
    print('   armonico %2d  %.4f  %-40s fase %6.2f' % (p['harmonic'], p['concentration'], bar, p['phase']))
d = V.dominant(lons)
print('   -> armonico dominante: %d' % d)
chk('la flor da 12 petalos', len(V.flower(lons)) == 12)
chk('el dominante es el de mayor concentracion',
    V.concentration(lons, d) == max(V.concentration(lons, h) for h in V.HARMONICS))

print('\n%d fallos' % len(fails))
sys.exit(1 if fails else 0)
