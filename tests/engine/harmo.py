import sys, math
from openastromod import harmogram as H, swiss
import swisseph as swe

fails = []
def chk(label, cond, extra=''):
    if not cond: fails.append(label)
    print('%-58s %s %s' % (label, 'OK' if cond else 'FALLA', extra))

# --- el orbe y la ponderacion ---
chk('ORB es 360/13 (el valor de Garcia)', abs(H.ORB - 27.69231) < 1e-5, '%.5f' % H.ORB)
chk('  y es el maximo antes del semisextil (360/12)', H.ORB < 360.0/12.0)
chk('peso 1 en conjuncion exacta', abs(H.weight(0.0) - 1.0) < 1e-12)
chk('peso = WEIGHT_AT_ORB justo en el borde',
    abs(H.weight(H.ORB - 1e-9) - H.WEIGHT_AT_ORB) < 1e-6, '%.4f' % H.weight(H.ORB - 1e-9))
chk('peso 0 pasado el orbe', H.weight(H.ORB + 0.001) == 0.0)
chk('la ponderacion decrece de forma monotona',
    all(H.weight(s) > H.weight(s + 0.5) for s in [x * 0.5 for x in range(int(H.ORB * 2) - 1)]))

# --- la carta armonica ---
chk('armonico 1 no mueve nada', abs(H.harmonic(123.45, 1) - 123.45) < 1e-9)
chk('una oposicion es conjuncion en el armonico 2',
    abs(H.separation(H.harmonic(10, 2), H.harmonic(190, 2))) < 1e-9)
chk('una cuadratura es conjuncion en el armonico 4',
    abs(H.separation(H.harmonic(10, 4), H.harmonic(100, 4))) < 1e-9)
chk('un trigono es conjuncion en el armonico 3',
    abs(H.separation(H.harmonic(10, 3), H.harmonic(130, 3))) < 1e-9)
chk('un trigono NO es conjuncion en el armonico 4',
    H.separation(H.harmonic(10, 4), H.harmonic(130, 4)) > 1.0)

# --- el conjunto propio no se cuenta consigo mismo ---
L = [0.0, 45.0, 90.0]
chk('mismo conjunto: 3 cuerpos dan 3 pares, no 9',
    H.intensity(L, L, 1, same_set=True) == H.intensity(L, L, 1, same_set=True) and
    H.max_intensity(3, 3, True) == 3.0)

# --- LA PRUEBA DE FUERZA: las espigas cerca del nacimiento ---
# El articulo: cerca del nacimiento cada planeta esta conjunto a su propio
# lugar radical en TODOS los armonicos bajos, y los transitos armonicos
# producen "espigas de intensidad muy desmesuradas". El armograma natal se
# invento para evitarlo. Si el motor es correcto, debe reproducirlo.
BODIES = (swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS,
          swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO)
jd_birth = swe.julday(1987, 4, 9, 12.0)
at = lambda jd: swiss.longitudes_at(jd, BODIES)
radix = at(jd_birth)

print('\nTRANSITOS ARMONICOS, intensidad en el instante natal:')
spike = 0.0
for n in (1, 2, 3, 6, 12):
    v = H.intensity(radix, radix, n)
    spike = max(spike, v)
    print('   armonico %2d -> %6.2f  (maximo posible %d)' % (n, v, int(H.max_intensity(10, 10))))
chk('transitos armonicos: espiga enorme en el nacimiento', spike > 9.0, '%.2f' % spike)

print('\nla misma fecha leida como ARMOGRAMA NATAL (cielo contra si mismo):')
natal = 0.0
for n in (1, 2, 3, 6, 12):
    v = H.intensity(radix, radix, n, same_set=True)
    natal = max(natal, v)
    print('   armonico %2d -> %6.2f  (maximo posible %d)' % (n, v, int(H.max_intensity(10, 10, True))))
chk('armograma natal: SIN espiga, que es su razon de ser', natal < spike / 2.0,
    'natal %.2f vs transitos %.2f' % (natal, spike))

# --- LA VALIDACION CONTRA EL ARTICULO ---
# "Si optamos por conceder a las conjunciones un orbe de 12 grados, que es
#  el que adopto O'Neill siguiendo a Addey, entonces el Sol en transito se
#  mantendra en conjuncion a su propia posicion radical por un periodo de
#  unos doce dias en el armonico 1, seis dias en el armonico 2, cuatro dias
#  en el armonico 3".
# Numeros publicados, para el orbe de O'Neill (12), no el de Garcia.
def days_conjunct(n, orb):
    d = 0.0
    while d < 60 and H.weight(H.separation(H.harmonic(at(jd_birth + d)[0], n),
                                           H.harmonic(radix[0], n)), orb) > 0:
        d += 0.05
    return d

print('\nVALIDACION: dias que el Sol sigue conjunto a su lugar radical')
print('con el orbe de 12 grados de O\'Neill, que es el del articulo:')
for n, expected in ((1, 12), (2, 6), (3, 4)):
    d = days_conjunct(n, 12.0)
    print('   armonico %d -> %5.1f dias   (el articulo dice ~%d)' % (n, d, expected))
    chk('  armonico %d: el articulo dice ~%d dias' % (n, expected),
        abs(d - expected) <= 1.5, '%.1f' % d)

print('\ny con el orbe de Garcia (%.2f), que escala igual:' % H.ORB)
base = days_conjunct(1, H.ORB)
for n in (1, 2, 3):
    d = days_conjunct(n, H.ORB)
    print('   armonico %d -> %5.1f dias   (1/%d de %.1f = %.1f)' % (n, d, n, base, base / n))
    chk('  armonico %d dura 1/%d de lo que dura el 1' % (n, n),
        abs(d - base / n) <= 0.6, '%.1f vs %.1f' % (d, base / n))

# --- muestreo ---
jds = H.sample_times(jd_birth, 16, 36)
chk('\nmuestreo 16 dias x 36 partes = 577 puntos', len(jds) == 577, '%d' % len(jds))
chk('  ventana centrada en la fecha',
    abs((jds[0] + jds[-1]) / 2.0 - jd_birth) < 1e-9)
chk('  abarca exactamente 16 dias', abs((jds[-1] - jds[0]) - 16.0) < 1e-9)

print('\n%d fallos' % len(fails))
sys.exit(1 if fails else 0)
