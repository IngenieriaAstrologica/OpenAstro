# -*- coding: utf-8 -*-
"""Calls on the three module-level singletons that name no existing method.

`openastro` keeps one instance of each of its first three classes in a module
global -- `cfg`, `db`, `openAstro` -- and the rest of the script reaches them
by those names. A typo or a rename in one of those classes therefore produces
an AttributeError that nothing catches until the code path runs, which for a
GTK menu item can be never.

This is not hypothetical. `mainWindow` once called `self.dec2deg(...)` for a
method that lives on `openAstroInstance`; the fix was `openAstro.dec2deg(...)`
and it took a user hitting it in a real session to find. Its sibling check,
cross_class_calls.py, covers the `self.X()` direction. This one covers the
other: `openAstro.X()` where `openAstroInstance` has no `X`.

Attributes are not checked, only calls -- a call is unambiguous in the source
and an attribute may be assigned anywhere.
"""
import os
import re
import sys

SINGLETONS = {
    'cfg': 'openAstroCfg',
    'db': 'openAstroSqlite',
    'openAstro': 'openAstroInstance',
}

path = os.path.join(os.environ.get('OA_ROOT', '.'), 'openastro')
lines = open(path, encoding='utf-8').read().splitlines()

# class ranges
bounds = [(i, m.group(1)) for i, l in enumerate(lines)
          if (m := re.match(r'class (\w+)', l))]
bounds.append((len(lines), '<eof>'))

methods = {}
for (start, name), (end, _) in zip(bounds, bounds[1:]):
    methods[name] = {m.group(1) for l in lines[start:end]
                     if (m := re.match(r'    def (\w+)', l))}

print('metodos por clase:')
for name in SINGLETONS.values():
    print('   %-20s %3d' % (name, len(methods.get(name, ()))))

pattern = re.compile(r'\b(%s)\.(\w+)\s*\(' % ('|'.join(SINGLETONS),))
findings = []
for i, line in enumerate(lines):
    stripped = line.lstrip()
    if stripped.startswith('#'):
        continue
    for var, attr in pattern.findall(line):
        cls = SINGLETONS[var]
        if attr in methods.get(cls, ()):
            continue
        # a data attribute that happens to be called, or a builtin on a value
        findings.append((i + 1, var, attr, cls))

print('\nllamadas a metodos que la clase no define:')
if not findings:
    print('   0 hallazgos')
else:
    for ln, var, attr, cls in findings:
        print('   linea %-5d  %s.%s()  -> %s no lo define' % (ln, var, attr, cls))

sys.exit(1 if findings else 0)
