import sys, datetime
from openastromod import profections as PR, atacir as A, arabicparts as AP, swiss
zod=['aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricorn','aquarius','pisces']
SIGNS='Ari Tau Gem Cnc Leo Vir Lib Sco Sgr Cap Aqr Psc'.split()
PL='Sol Luna Mer Ven Mar Jup Sat'.split()
planets=[{'name':'p%d'%i,'visible':1} for i in range(36)]
nat=swiss.ephData(1987,4,9,12.0+0.5/3600,2.0367,41.3436,12,planets,zod,
    {'houses_system':'P','postype':'geo','siderealmode':'FAGAN_BRADLEY','zodiactype':'tropical'})
asc=nat.houses_degree_ut[0]; jd=nat.jd_ut
fails=[]
def chk(l,c,e=''):
    if not c: fails.append(l)
    print('%-56s %s %s'%(l,'OK' if c else 'FALLA',e))

print('Asc natal %.4f = %s %.2f\n'%(asc,SIGNS[PR.sign_of(asc)],asc%30))
t=PR.table(datetime.datetime(1987,4,9), asc, upto=90)

# 1. CONCORDANCIA con el atacir C-12: el signo profectado debe ser el del
#    Ascendente girado por el arco del atacir a esa edad
bad=0
for e in t[:40]:
    arc=A.arc_for_days(A.TROPICAL_YEAR*e['age'],12)
    rotated=(asc+arc)%360.0
    if PR.sign_of(rotated)!=e['sign']: bad+=1
chk('el signo profectado = signo del Asc girado por el atacir C-12', bad==0, '%d discrepancias en 40 anios'%bad)

# 2. avanza exactamente un signo por anio
chk('avanza un signo por anio', all((t[i+1]['sign']-t[i]['sign'])%12==1 for i in range(len(t)-1)))
# 3. ciclo de 12
chk('vuelve al signo natal a los 12 anios', t[12]['sign']==t[0]['sign'] and t[0]['sign']==PR.sign_of(asc))
chk('y a los 84 tambien (7 vueltas)', t[84]['sign']==t[0]['sign'])
# 4. casas
chk('edad 0 -> casa 1, edad 11 -> casa 12, edad 12 -> casa 1',
    t[0]['house']==1 and t[11]['house']==12 and t[12]['house']==1)
# 5. regente coherente con la tabla de domicilios compartida
chk('el regente sale de la tabla compartida con los lotes',
    all(e['lord']==AP.DOMICILE[e['sign']] for e in t))
# 6. fechas: cada anio empieza en el cumpleanos
chk('cada anio empieza en el cumpleanos', all(e['start'].month==4 and e['start'].day==9 for e in t))
chk('y encadena sin huecos', all(t[i]['end']==t[i+1]['start'] for i in range(len(t)-1)))
# 7. 29 de febrero
q=PR.table(datetime.datetime(2000,2,29), asc, upto=4)
chk('nacimiento 29-feb no revienta', q[1]['start'].day in (28,29), str(q[1]['start'].date()))
# 8. current_age
chk('current_age antes del nacimiento devuelve None', PR.current_age(datetime.datetime(1987,4,9),datetime.datetime(1980,1,1)) is None)
chk('current_age el dia antes del cumple resta un anio',
    PR.current_age(datetime.datetime(1987,4,9),datetime.datetime(2020,4,8))==32 and
    PR.current_age(datetime.datetime(1987,4,9),datetime.datetime(2020,4,9))==33)

print('\nprimeros anios:')
for e in t[:6]:
    print('   %2d  %s  %s  casa %2d  regente %s'%(e['age'],e['start'].date(),SIGNS[e['sign']],e['house'],PL[e['lord']]))
print('\n%d fallos'%len(fails)); sys.exit(1 if fails else 0)
