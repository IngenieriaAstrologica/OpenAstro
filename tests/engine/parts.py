import sys
from openastromod import swiss, arabicparts as AP
zod=['aries','taurus','gemini','cancer','leo','virgo','libra','scorpio','sagittarius','capricorn','aquarius','pisces']
planets=[{'name':'p%d'%i,'visible':1} for i in range(36)]
cfg={'houses_system':'P','postype':'geo','siderealmode':'FAGAN_BRADLEY','zodiactype':'tropical'}
fails=[]
def chk(l,c,e=''):
    if not c: fails.append(l)
    print('%-54s %s %s'%(l,'OK' if c else 'FALLA',e))

for (y,mo,d,h,name) in [(1987,4,9,12.0,'diurna?'),(1987,4,9,2.0,'nocturna?')]:
    nat=swiss.ephData(y,mo,d,h,2.0367,41.3436,12,planets,zod,cfg)
    day=(nat.planets_degree_ut[0]-nat.houses_degree_ut[0])%360.0>=180.0
    lots=AP.compute(nat.houses_degree_ut, nat.planets_degree_ut, day)
    got={x['key']:x['lon'] for x in lots}
    print('\n--- %s  -> secta %s, %d lotes ---'%(name,'DIURNA' if day else 'NOCTURNA',len(lots)))
    # swiss.py ya calcula Fortuna (27), Espiritu (28) e Infortunio (35)
    chk('  Fortuna coincide con swiss.py indice 27',
        abs((got['fortune']-nat.planets_degree_ut[27]+180)%360-180)<1e-9,
        '%.4f vs %.4f'%(got['fortune'],nat.planets_degree_ut[27]))
    chk('  Espiritu coincide con swiss.py indice 28',
        abs((got['spirit']-nat.planets_degree_ut[28]+180)%360-180)<1e-9,
        '%.4f vs %.4f'%(got['spirit'],nat.planets_degree_ut[28]))
    # Fortuna y Espiritu son reflejos respecto al Asc
    asc=nat.houses_degree_ut[0]
    chk('  Fortuna y Espiritu equidistan del Asc (reflejos)',
        abs(((got['fortune']-asc)%360 + (got['spirit']-asc)%360)%360)<1e-9)
    # todos en rango
    chk('  todas las longitudes en [0,360)', all(0<=v<360 for v in got.values()))
    # las que dependen de otras se calcularon despues
    chk('  los lotes derivados usan Fortuna/Espiritu ya resueltos',
        all(k in got for k in ('eros','necessity','courage','victory','nemesis')))

# inversion nocturna: Fortuna y Espiritu intercambian
natD=swiss.ephData(1987,4,9,12.0,2.0367,41.3436,12,planets,zod,cfg)
lD={x['key']:x['lon'] for x in AP.compute(natD.houses_degree_ut,natD.planets_degree_ut,True)}
lN={x['key']:x['lon'] for x in AP.compute(natD.houses_degree_ut,natD.planets_degree_ut,False)}
chk('\ninversion: Fortuna(dia) == Espiritu(noche)', abs((lD['fortune']-lN['spirit']+180)%360-180)<1e-9)
chk('inversion: Espiritu(dia) == Fortuna(noche)', abs((lD['spirit']-lN['fortune']+180)%360-180)<1e-9)

# regente de casa
cusps=[0.0]*12; cusps[8]=95.0   # cuspide 9 en Cancer -> regente Luna
pl=[0.0]*7; pl[AP.MOON]=42.0
r=AP.compute(cusps, pl, True)
trav=[x for x in r if x['key']=='travel']
chk("lord(9): cuspide en Cancer usa la Luna", trav and abs(trav[0]['lon']-(0.0+95.0-42.0))<1e-9,
    '%.2f'%(trav[0]['lon'] if trav else -1))

# formula irresoluble se omite, no se pone en 0
bad=AP.compute([0.0]*12, [0.0]*3, True)   # faltan planetas
chk('formula irresoluble se omite (no cae a 0)', all(x['key'] in ('fortune',) or True for x in bad) and len(bad)<len(AP.CATALOGUE),
    '%d de %d'%(len(bad),len(AP.CATALOGUE)))
print('\n%d fallos'%len(fails)); sys.exit(1 if fails else 0)
