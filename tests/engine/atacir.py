import sys
from openastromod import atacir as A

ok = lambda c: 'OK' if c else 'FALLA'
fails = []
total = 0
def check(label, cond, extra=''):
    global total
    total += 1
    if not cond: fails.append(label)
    print('%-58s %s %s' % (label, ok(cond), extra))

# 1. identidad con la constante de Morinus
K = 12.17473968
check('days_per_degree(12) == K de Morinus', abs(A.days_per_degree(12)-K) < 1e-8,
      '%.8f' % A.days_per_degree(12))

# 2. Morinus: rotdeg = dias / K
for days in (0.0, 1000.0, 4383.0, 12345.6):
    mine = A.arc_for_days(days, 12)
    mor  = days / K
    check('C-12 coincide con Morinus para %9.1f dias' % days, abs(mine-mor) < 1e-9)

# 3. tasas por ciclo
for N, dpy in ((12,30.0),(24,15.0),(36,10.0),(72,5.0),(360,1.0)):
    check('C-%-3d avanza %g deg/anio' % (N,dpy), abs(A.degrees_per_year(N)-dpy) < 1e-12)

# 4. criterio de verificacion del TODO: 0 anios -> 0 grados
check('a los 0 anios el desplazamiento es 0', A.arc_for_days(0,12) == 0.0)

# 5. a los N anios exactos -> 360 (una vuelta, normaliza a 0)
# El modulo tenia una tupla CYCLES con los ciclos preestablecidos; al pasar
# el ciclo a entero libre (MIN_CYCLE..MAX_CYCLE) desaparecio, asi que aqui
# se toma una muestra que cubre los casos con nombre propio: C-12 el de
# referencia, C-360 el grado por anio, y C-1 el extremo de una vuelta anual.
for N in (1, 12, 24, 36, 72, 360):
    total = A.arc_for_days(A.TROPICAL_YEAR*N, N)
    check('C-%-3d a los %3d anios da vuelta exacta' % (N,N),
          abs(total-360.0) < 1e-9 and abs(A.normalize(total)) < 1e-9, '%.6f' % total)

# 6. rigidez: los aspectos internos no cambian
lons = [10.0, 95.5, 200.25, 359.9]
rot = A.rotate(lons, 137.77)
d0 = [(b-a) % 360.0 for a,b in zip(lons, lons[1:])]
d1 = [(b-a) % 360.0 for a,b in zip(rot, rot[1:])]
check('la rotacion es rigida (distancias intactas)',
      all(abs(x-y) < 1e-9 for x,y in zip(d0,d1)))

# 7. vueltas y anios
check('turns() cuenta vueltas cerradas', A.turns(725.0) == 2 and A.turns(-1.0) == -1)
check('years_for_arc invierte arc_for_days',
      abs(A.years_for_arc(A.arc_for_days(A.TROPICAL_YEAR*7, 12), 12) - 7.0) < 1e-9)

# 8. arco negativo antes del nacimiento (converso)
check('arco negativo antes del nacimiento', A.arc_for_days(-A.TROPICAL_YEAR, 12) < 0)

# 9. ciclo invalido
try:
    A.degrees_per_year(0); check('ciclo 0 lanza ValueError', False)
except ValueError:
    check('ciclo 0 lanza ValueError', True)

print('\n%d comprobaciones, %d fallos' % (total, len(fails)))
if fails: print('FALLAN:', fails); sys.exit(1)
print('TODO CORRECTO')
