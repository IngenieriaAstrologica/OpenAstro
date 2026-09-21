import sys
from openastromod import atacir as A
fails=[]
def chk(lbl,got,want):
    ok = got==want
    if not ok: fails.append(lbl)
    print('%-46s -> %-6s %s' % (lbl, got, 'OK' if ok else 'FALLA, esperaba %s'%want))

print('rango admitido: C-%d .. C-%d, por defecto C-%d\n' % (A.MIN_CYCLE,A.MAX_CYCLE,A.DEFAULT_CYCLE))
chk('valid_cycle(12)   normal',            A.valid_cycle(12), 12)
chk('valid_cycle(1)    limite inferior',   A.valid_cycle(1), 1)
chk('valid_cycle(360)  limite superior',   A.valid_cycle(360), 360)
chk('valid_cycle(0)    por debajo -> tope',A.valid_cycle(0), 1)
chk('valid_cycle(-5)   negativo -> tope',  A.valid_cycle(-5), 1)
chk('valid_cycle(1000) por encima -> tope',A.valid_cycle(1000), 360)
chk('valid_cycle("7")  texto numerico',    A.valid_cycle("7"), 7)
chk('valid_cycle("ab") basura -> defecto', A.valid_cycle("ab"), 12)
chk('valid_cycle(None) vacio -> defecto',  A.valid_cycle(None), 12)
chk('valid_cycle(7.9)  decimal se trunca', A.valid_cycle(7.9), 7)

print('\ntasas en todo el rango, ninguna debe fallar:')
bad=[n for n in range(A.MIN_CYCLE, A.MAX_CYCLE+1) if not (0 < A.degrees_per_year(n) <= 360.0)]
print('   %d ciclos probados, %d problematicos' % (A.MAX_CYCLE-A.MIN_CYCLE+1, len(bad)))
if bad: fails.append('rango')
for n in (1,5,12,36,90,360):
    print('   C-%-4d %8.4f deg/anio   vuelta en %3d anios' % (n, A.degrees_per_year(n), n))

# la vuelta completa debe cerrar para cualquier N del rango
import math
worst = max(abs(A.arc_for_days(A.TROPICAL_YEAR*n, n) - 360.0) for n in range(1,361))
print('\npeor desviacion de la vuelta completa en los 360 ciclos: %.3e grados' % worst)
if worst > 1e-9: fails.append('vuelta')
print('\n%d fallos' % len(fails))
sys.exit(1 if fails else 0)
