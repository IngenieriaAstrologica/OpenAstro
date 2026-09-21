# -*- coding: utf-8 -*-
"""self.X() calls that will raise AttributeError when the line runs.

Two failures, both invisible to py_compile, both of which have actually
happened in this script:

  1. self.X() where X lives on a *different* class. `mainWindow` called
     self.dec2deg(), which belongs to openAstroInstance; the right call is
     openAstro.dec2deg(). A user hit it in a real session.

  2. self.X() where X exists on *no* class at all -- a typo, or a rename
     that missed its call sites. This is the worse of the two and the
     original version of this check skipped it silently.

Case 2 needs care, because an inherited method legitimately appears
nowhere in the file. The rule used here needs no allowlist: a class
declared with no base (`class openAstroCfg:`) inherits nothing but object,
so every self.X() it makes must be defined in it. Only `drawSVG` has a
base -- Gtk.DrawingArea -- and it is exempt from case 2 alone.
"""
import os
import re
import sys

path = os.path.join(os.environ.get('OA_ROOT', '.'), 'openastro')
lines = open(path, encoding='utf-8').read().splitlines()

decl = re.compile(r'class (\w+)\s*(\(([^)]*)\))?\s*:')
classes = [(i, m.group(1), (m.group(3) or '').strip())
           for i, l in enumerate(lines) if (m := decl.match(l))]
classes.append((len(lines), '<eof>', ''))
ranges = [(classes[k][1], classes[k][0], classes[k + 1][0], classes[k][2])
          for k in range(len(classes) - 1)]

methods = {}
for name, a, b, base in ranges:
    methods[name] = {m.group(1) for l in lines[a:b]
                     if (m := re.match(r'    def (\w+)', l))}
everywhere = set().union(*methods.values()) if methods else set()

print('clases y numero de metodos:')
for name, a, b, base in ranges:
    print('   %-22s %3d metodos   lineas %d-%d%s' % (
        name, len(methods[name]), a + 1, b,
        '   hereda de %s' % base if base else ''))

elsewhere = []
nowhere = []
for name, a, b, base in ranges:
    own = methods[name]
    for i in range(a, b):
        if lines[i].lstrip().startswith('#'):
            continue
        for m in re.finditer(r'self\.(\w+)\(', lines[i]):
            fn = m.group(1)
            if fn in own:
                continue
            other = [c for c in methods if c != name and fn in methods[c]]
            if other:
                elsewhere.append((i + 1, name, fn, other))
            elif fn not in everywhere and not base:
                # no base class, so there is nowhere for this to come from
                nowhere.append((i + 1, name, fn))

print('\nllamadas self.X() a metodos de OTRA clase:')
for ln, name, fn, other in elsewhere:
    print('   linea %-5d en %-18s self.%s()  -> definido en %s' % (ln, name, fn, other))
print('   %d hallazgos' % len(elsewhere))

print('\nllamadas self.X() a metodos que no existen en NINGUNA clase')
print('(solo en clases sin clase base, donde no pueden venir heredados):')
for ln, name, fn in nowhere:
    print('   linea %-5d en %-18s self.%s()  -> no existe' % (ln, name, fn))
print('   %d hallazgos' % len(nowhere))

total = len(elsewhere) + len(nowhere)
print('\n%d hallazgos en total' % total)
sys.exit(1 if total else 0)
