"""Replica la busqueda de localToLunar y comprueba que da el retorno mas cercano."""
import sys, datetime, calendar
from openastromod import swiss
zod=['aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricorn','aquarius','pisces']
pl=[{'name':'p%d'%i,'visible':1} for i in range(36)]
CFG={'houses_system':'P','postype':'geo','siderealmode':'FAGAN_BRADLEY','zodiactype':'tropical'}
LON,LAT,ALT=2.0367,41.3436,12
def eph(dt): return swiss.ephData(dt.year,dt.month,dt.day,dt.hour+dt.minute/60.0+dt.second/3600.0,LON,LAT,ALT,pl,zod,CFG)
nat=eph(datetime.datetime(1987,4,9,12,0,30)); natmoon=nat.planets_degree_ut[1]
SECS=27.321661*86400.0
def find(year,month,day):
    day=max(1,min(int(day),calendar.monthrange(year,month)[1]))
    dt=datetime.datetime(year,month,day,12,0,30)
    md=(natmoon-eph(dt).planets_degree_ut[1]+180.0)%360.0-180.0
    dt=dt+datetime.timedelta(seconds=(md/360.0)*SECS)
    for _ in range(3):
        m1=eph(dt); dt2=dt+datetime.timedelta(hours=1); m2=eph(dt2)
        sp=((m2.planets_degree_ut[1]-m1.planets_degree_ut[1]+180.0)%360.0-180.0)/3600.0
        if abs(sp)<1e-9: break
        d=(natmoon-m1.planets_degree_ut[1]+180.0)%360.0-180.0
        dt=dt+datetime.timedelta(seconds=d/sp)
    return dt
fails=[]
def chk(l,c,e=''):
    if not c: fails.append(l)
    print('%-54s %s %s'%(l,'OK' if c else 'FALLA',e))

print('Luna natal %.6f\n'%natmoon)
print('dia pedido -> retorno encontrado (distancia en dias):')
res={}
for day in (1,5,10,15,20,25,28):
    r=find(2026,9,day); res[day]=r
    dist=abs((r-datetime.datetime(2026,9,day,12,0,30)).total_seconds())/86400.0
    resid=abs((eph(r).planets_degree_ut[1]-natmoon+180)%360-180)*3600
    print('   dia %2d -> %s   %5.2f d   residuo %.2f"'%(day,r.strftime('%Y-%m-%d %H:%M:%S'),dist,resid))
    chk('  dia %2d: la Luna vuelve a su grado natal'%day, resid<1.0, '%.2f arcsec'%resid)
    chk('  dia %2d: el retorno esta a menos de 14 dias'%day, dist<14.0, '%.2f d'%dist)

# dias distintos deben poder dar retornos distintos (no siempre el de mitad de mes)
chk('\ndias alejados dan retornos distintos', res[1]!=res[28],
    '%s vs %s'%(res[1].date(),res[28].date()))
# y dias contiguos el mismo
chk('dias contiguos convergen al mismo retorno', abs((res[10]-res[15]).total_seconds())<1.0)
# clamping
r=find(2026,2,31)
chk('dia 31 en febrero se acota sin reventar', r is not None, r.strftime('%Y-%m-%d'))
print('\n%d fallos'%len(fails)); sys.exit(1 if fails else 0)
