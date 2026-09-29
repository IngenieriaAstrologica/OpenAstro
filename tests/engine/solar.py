import sys
from openastromod import primary as P, atacir as A
import swisseph as swe
jd = swe.julday(1987,4,9,12.0+0.5/3600)
fails=[]
def chk(l,c,e=''):
    if not c: fails.append(l)
    print('%-56s %s %s'%(l,'OK' if c else 'FALLA',e))

print('arco solar en longitud, por edad:')
for age in (0,1,10,30,50):
    a=P.solar_arc_lon(jd, age)
    print('   %2d anios -> %8.4f deg   (%.4f deg/anio)' % (age,a,a/age if age else 0))

# 1. a los 0 anios no hay arco
chk('a los 0 anios el arco es 0', abs(P.solar_arc_lon(jd,0))<1e-9)
# 2. ritmo cercano a Naibod (0.9856) y a 1 grado/anio
r30=P.solar_arc_lon(jd,30)/30.0
chk('ritmo medio a 30 anios entre 0.95 y 1.02 deg/anio', 0.95<r30<1.02, '%.5f'%r30)
chk('  y cerca de la clave de Naibod (%.5f)'%P.NAIBOD_DEGREE_PER_YEAR,
    abs(r30-P.NAIBOD_DEGREE_PER_YEAR)<0.03, 'dif %.5f'%abs(r30-P.NAIBOD_DEGREE_PER_YEAR))
# 3. converso = simetrico
chk('converso: arco(-10) es negativo', P.solar_arc_lon(jd,-10)<0, '%.4f'%P.solar_arc_lon(jd,-10))
chk('  y de magnitud parecida al directo', abs(abs(P.solar_arc_lon(jd,-10))-abs(P.solar_arc_lon(jd,10)))<1.0)
# 4. monotono en el rango util
vals=[P.solar_arc_lon(jd,a) for a in range(0,101)]
chk('crece de forma monotona hasta los 100 anios', all(b>a for a,b in zip(vals,vals[1:])))
# 5. NO es el mismo que el de ascension recta
ra=P.solar_arc_ra(jd, jd+30)
chk('difiere del arco en AR (son medidas distintas)', abs(ra-P.solar_arc_lon(jd,30))>0.05,
    'AR %.4f vs lon %.4f'%(ra,P.solar_arc_lon(jd,30)))
# 6. comparado con el atacir C-360 (1 grado/anio exacto)
c360=A.arc_for_days(A.TROPICAL_YEAR*30,360)
chk('el C-360 da exactamente 30 y el solar no', abs(c360-30.0)<1e-9 and abs(P.solar_arc_lon(jd,30)-30.0)>0.1,
    'C-360 %.4f vs solar %.4f'%(c360,P.solar_arc_lon(jd,30)))
print('\n%d fallos'%len(fails)); sys.exit(1 if fails else 0)
