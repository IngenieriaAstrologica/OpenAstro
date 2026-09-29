import sys, random
from openastromod import harmonics as HN, swiss
import swisseph as swe

fails = []
def chk(l, c, e=''):
    if not c: fails.append(l)
    print('%-58s %s %s' % (l, 'OK' if c else 'FALLA', e))

# --- datos reales, no stubs: una carta real via Swiss Ephemeris ---
BODIES = (swe.SUN, swe.MOON, swe.MERCURY, swe.VENUS, swe.MARS,
          swe.JUPITER, swe.SATURN, swe.URANUS, swe.NEPTUNE, swe.PLUTO)
jd_birth = swe.julday(1987, 4, 9, 12.0)
radix = swiss.longitudes_at(jd_birth, BODIES)
chk('la carta real trae 10 cuerpos', len(radix) == 10, '%d' % len(radix))

# =====================================================================
# 1. N=1 es la identidad
# =====================================================================
h1 = HN.chart(radix, 1)
chk('armonico 1 es la identidad, cuerpo a cuerpo',
    all(abs(a - b) < 1e-9 for a, b in zip(h1, radix)),
    '%r vs %r' % (h1[:2], radix[:2]))
chk('  tambien para harmonic() suelto', abs(HN.harmonic(radix[0], 1) - radix[0]) < 1e-9)

# =====================================================================
# 2. dos planetas en conjuncion exacta siguen conjuntos en todo armonico
# =====================================================================
conj_a, conj_b = radix[0], radix[0]  # misma longitud exacta: conjuncion perfecta
ok = True
for n in range(1, 21):
    da, db = HN.harmonic(conj_a, n), HN.harmonic(conj_b, n)
    if abs(da - db) > 1e-9:
        ok = False
chk('conjuncion exacta: sigue conjunta en los armonicos 1..20', ok)

# =====================================================================
# 3. una oposicion exacta (180 grados) se vuelve conjuncion en N=2
# =====================================================================
opp_a, opp_b = radix[3], (radix[3] + 180.0) % 360.0
sep180 = min(abs(opp_a - opp_b) % 360.0, 360.0 - abs(opp_a - opp_b) % 360.0)
chk('control: la pareja construida es opuesta de verdad', abs(sep180 - 180.0) < 1e-9)

def separation(a, b):
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)

chk('oposicion exacta: NO conjuncion en el armonico 1',
    separation(HN.harmonic(opp_a, 1), HN.harmonic(opp_b, 1)) > 100.0)
chk('oposicion exacta: conjuncion en el armonico 2',
    separation(HN.harmonic(opp_a, 2), HN.harmonic(opp_b, 2)) < 1e-9,
    '%.10f' % separation(HN.harmonic(opp_a, 2), HN.harmonic(opp_b, 2)))

# =====================================================================
# 4. un trigono exacto (120 grados) se vuelve conjuncion en N=3
# =====================================================================
tri_a, tri_b = radix[6], (radix[6] + 120.0) % 360.0
chk('trigono exacto: NO conjuncion en el armonico 1',
    separation(HN.harmonic(tri_a, 1), HN.harmonic(tri_b, 1)) > 50.0)
chk('trigono exacto: NO conjuncion en el armonico 2 tampoco',
    separation(HN.harmonic(tri_a, 2), HN.harmonic(tri_b, 2)) > 50.0)
chk('trigono exacto: conjuncion en el armonico 3',
    separation(HN.harmonic(tri_a, 3), HN.harmonic(tri_b, 3)) < 1e-9,
    '%.10f' % separation(HN.harmonic(tri_a, 3), HN.harmonic(tri_b, 3)))

# =====================================================================
# 5. el armonico N de un armonico M equivale al armonico N*M
# =====================================================================
random.seed(7)
sample = list(radix) + [random.uniform(0, 360) for _ in range(50)]
ok = True
worst = 0.0
for lon in sample:
    for n in (1, 2, 3, 4, 5, 7, 9, 12, 30):
        for m in (1, 2, 3, 5, 6, 11):
            nested = HN.harmonic(HN.harmonic(lon, m), n)
            direct = HN.harmonic(lon, HN.compose(n, m))
            d = separation(nested, direct)
            worst = max(worst, d)
            if d > 1e-7:
                ok = False
chk('armonico N de un armonico M == armonico N*M (fold-and-scale)', ok, 'peor caso %.2e' % worst)
chk('compose() hace la multiplicacion literal', HN.compose(4, 5) == 20 and HN.compose(7, 1) == 7)

# también con la carta real completa, N y M típicos de uso
h5 = HN.chart(radix, 5)
h5_then_4 = HN.chart(h5, 4)
h20 = HN.chart(radix, HN.compose(4, 5))
chk('el 4o armonico del 5o armonico (carta completa) es el armonico 20',
    all(separation(a, b) < 1e-7 for a, b in zip(h5_then_4, h20)))

# =====================================================================
# 6. todo resultado cae en [0, 360)
# =====================================================================
random.seed(11)
ok = True
for _ in range(5000):
    lon = random.uniform(-10000.0, 10000.0)
    n = random.randint(HN.MIN_HARMONIC, HN.MAX_HARMONIC)
    v = HN.harmonic(lon, n)
    if not (0.0 <= v < 360.0):
        ok = False
chk('5000 pares (lon, N) al azar: siempre cae en [0, 360)', ok)
# también sobre la carta real, todos los armonicos 1..12 (como harmogram.HARMONICS)
ok = True
for n in range(1, 13):
    for v in HN.chart(radix, n):
        if not (0.0 <= v < 360.0):
            ok = False
chk('la carta real, armonicos 1..12: siempre en [0, 360)', ok)

# =====================================================================
# extra: valid_harmonic() como atacir.valid_cycle()
# =====================================================================
chk('valid_harmonic descarta basura -> default', HN.valid_harmonic('nada') == HN.DEFAULT_HARMONIC)
chk('valid_harmonic recorta por debajo', HN.valid_harmonic(0) == HN.MIN_HARMONIC)
chk('valid_harmonic recorta por encima', HN.valid_harmonic(99999) == HN.MAX_HARMONIC)
chk('valid_harmonic deja pasar un valor bueno', HN.valid_harmonic(7) == 7)

# extra: chart() no toca la longitud de la lista ni reordena
chk('chart() conserva el numero de cuerpos', len(HN.chart(radix, 5)) == len(radix))

print('\n%d fallos' % len(fails))
if fails:
    print('FALLAN:', fails)
sys.exit(1 if fails else 0)
