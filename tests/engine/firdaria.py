"""Compara mi motor con el algoritmo de Morinus, reimplementado literalmente."""
import sys
from datetime import datetime, timedelta
from openastromod import firdaria as F

# --- transcripcion literal de Morinus SE/firdaria.py ---
class Morinus:
    def __init__(self, by,bm,bd, isdaily, isbonatti):
        self.startdate=datetime(by,bm,bd); self.isdaily=isdaily; self.bon=isbonatti
        self.d=[(3,10),(4,8),(5,13),(6,9),(0,11),(1,12),(2,7),(7,3),(8,2)]
        self.a=[(6,9),(0,11),(1,12),(2,7),(3,10),(4,8),(5,13),(7,3),(8,2)]
        self.b=[(6,9),(0,11),(1,12),(2,7),(7,3),(8,2),(3,10),(4,8),(5,13)]
    def isNode(self,i):
        if self.isdaily: return i==7 or i==8
        return (i==4 or i==5) if self.bon else (i==7 or i==8)
    def nextIndex(self,i):
        i=i+1
        if self.isdaily:
            if self.isNode(i) or i>8: return 0
        else:
            if self.bon:
                if self.isNode(i): return 6
                elif i>8: return 0
            else:
                if self.isNode(i) or i>8: return 0
        return i
    def run(self):
        py = self.d if self.isdaily else (self.b if self.bon else self.a)
        rows=[]; starting=self.startdate
        for index in range(len(py)+3):
            ai=index%len(py); planet,years=py[ai]
            ending=datetime(starting.year+years, starting.month, starting.day)
            subs=[]
            if not self.isNode(ai):
                ss=starting; secs=(ending-starting).total_seconds(); i=ai
                for _ in range(7):
                    se=ss+timedelta(seconds=secs/7)
                    subs.append((py[i][0], ss, se)); ss=se; i=self.nextIndex(i)
            rows.append((planet,years,starting,ending,subs)); starting=ending
        return rows

fails=[]
CASES=[(1987,4,9),(1970,1,1),(2000,12,31),(1955,6,15)]
MODES=[(True,False,'diurna'),(False,False,'nocturna Al-Biruni'),(False,True,'nocturna Bonatti')]
for (y,m,d) in CASES:
    for daily,bon,name in MODES:
        mine = F.periods(datetime(y,m,d), daily, bon)
        theirs = Morinus(y,m,d,daily,bon).run()
        if len(mine)!=len(theirs): fails.append('len %s %s'%(name,(y,m,d))); continue
        for a,b in zip(mine,theirs):
            if (a['ruler'],a['years'],a['start'],a['end']) != (b[0],b[1],b[2],b[3]):
                fails.append('periodo %s %s'%(name,(y,m,d))); break
            if [(r,s,e) for r,s,e in a['sub']] != b[4]:
                fails.append('subperiodos %s %s'%(name,(y,m,d))); break
print('%d fechas x %d ordenes comparadas periodo a periodo y subperiodo a subperiodo' % (len(CASES),len(MODES)))
print('discrepancias con Morinus: %d %s' % (len(fails), fails[:4]))

# totales
for daily,bon,name in MODES:
    seq=F.sequence(daily,bon); tot=sum(y for _,y in seq)
    print('   %-20s suma %d anios, %d periodos, nodos en %s' % (name, tot, len(seq), sorted(F.node_slots(seq))))
    if tot!=75: fails.append('total '+name)

# los nodos no reciben subperiodos
p=F.periods(datetime(1987,4,9), True)
bad=[x['ruler'] for x in p if x['is_node'] and x['sub']]
print('   nodos con subperiodos indebidos: %d' % len(bad))
if bad: fails.append('nodos')

# 29 de febrero
try:
    q=F.periods(datetime(2000,2,29), True)
    print('   nacimiento 29-feb: primer corte %s  OK' % q[0]['end'].date())
except Exception as e:
    fails.append('29feb'); print('   29-feb FALLA: %s' % e)

print('\n%d fallos' % len(fails))
sys.exit(1 if fails else 0)
