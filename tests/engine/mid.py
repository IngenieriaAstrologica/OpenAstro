import sys, math, random
from openastromod import midpoints as M

# --- transcripcion literal de Morinus countMidPoints ---
def morinus(p1, p2):
    d = math.fabs(p1-p2); m = 0.0
    if d <= 180.0:
        m = p1+d/2.0 if p1 < p2 else p2+d/2.0
    else:
        d = 360.0-d
        m = p2+d/2.0 if p1 < p2 else p1+d/2.0
        if m >= 360.0: m -= 360.0
    return m % 360.0

fails=[]
def chk(lbl, cond, extra=''):
    if not cond: fails.append(lbl)
    print('%-52s %s %s' % (lbl, 'OK' if cond else 'FALLA', extra))

# 1. identico a Morinus en malla exhaustiva
random.seed(7)
worst=0.0
for a in range(0,360,3):
    for b in range(0,360,3):
        d=abs(M.midpoint(a,b)-morinus(float(a),float(b)))
        d=min(d,360-d); worst=max(worst,d)
for _ in range(3000):
    a=random.uniform(0,360); b=random.uniform(0,360)
    d=abs(M.midpoint(a,b)-morinus(a,b)); d=min(d,360-d); worst=max(worst,d)
chk('identico a Morinus (14400 malla + 3000 aleatorios)', worst<1e-9, 'peor %.2e' % worst)

# 2. el punto medio esta en el arco MENOR
bad=0
for _ in range(5000):
    a=random.uniform(0,360); b=random.uniform(0,360)
    m=M.midpoint(a,b)
    da=min(abs(m-a),360-abs(m-a)); db=min(abs(m-b),360-abs(m-b))
    sep=min(abs(a-b),360-abs(a-b))
    if abs(da-db)>1e-9 or abs(da-sep/2)>1e-9: bad+=1
chk('equidista de ambos y cae en el arco menor', bad==0, '%d fallos' % bad)

# 3. simetrico
chk('midpoint(a,b) == midpoint(b,a)',
    all(abs(M.midpoint(a,b)-M.midpoint(b,a))<1e-9 for a,b in [(10,350),(0,180),(359.9,0.1),(45,200)]))

# 4. casos limite a mano
for a,b,want in [(10,20,15),(350,10,0),(0,180,90),(180,0,90),(90,270,180),(359,1,0)]:
    got=M.midpoint(a,b)
    chk('  midpoint(%g,%g) = %g' % (a,b,want), abs(((got-want+180)%360)-180)<1e-9, 'da %.4f'%got)

# 5. el dial colapsa conjuncion, cuadratura y oposicion
mid=100.0
for off,name in [(0,'conjuncion'),(90,'cuadratura'),(180,'oposicion'),(270,'cuadratura 2')]:
    chk('  el dial ve %-12s como contacto' % name, M.dial_separation(mid, mid+off)<1e-9)
chk('  el dial NO ve un trigono (120)', M.dial_separation(mid, mid+120)>1.0)

# 6. el dial envuelve correctamente
chk('dial: 89 y 1 distan 2, no 88', abs(M.dial_separation(89,1)-2.0)<1e-9)

# 7. el arbol excluye a los miembros del propio par
bodies=[('A',10.0),('B',20.0),('C',15.0)]
t=M.tree(bodies, orb=2.0)
ab=[x for x in t if {x['a'],x['b']}=={'A','B'}][0]
chk('el par no se activa a si mismo', all(k=='C' for k,_ in ab['contacts']), str(ab['contacts']))
chk('  y C si activa a A/B (esta en su punto medio)', any(k=='C' for k,_ in ab['contacts']))

# 8. numero de pares
n=8; chk('pares de %d cuerpos = %d' % (n, n*(n-1)//2),
         len(list(M.pairs([(str(i),0.0) for i in range(n)])))==n*(n-1)//2)

print('\n%d fallos' % len(fails))
sys.exit(1 if fails else 0)
