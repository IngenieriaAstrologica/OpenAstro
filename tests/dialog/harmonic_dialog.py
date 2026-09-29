# -*- coding: utf-8 -*-
"""Drive the real specialHarmonic()/specialHarmonicSubmit() dialog headless.

The harmonic chart is the simplest technique dialog in the Special menu: one
spin button for the harmonic order N, no date, no bi-wheel view to reset.
Nothing had opened it yet, so the checks that matter are the same short list
used for its siblings: it opens without raising, N defaults to something
sensible, what the user set is what reaches the engine, and it persists in
astrocfg like the atacir cycle does.
"""
import datetime
import os
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _harness import grab, Store, Cfg, make_shim, find_button, Report

from openastromod import harmonics as harmonics_engine

R = Report('harmonic dialog')
STORE = Store()
ERRORS = []
CALLS = []


class OpenAstro(object):
    name = 'Dialog Fixture'
    year, month, day = 1987, 4, 9

    def localToHarmonic(self, n):
        CALLS.append(('localToHarmonic', n))

    def makeSVG(self):
        CALLS.append(('makeSVG',))


ns = {'datetime': datetime, 'Gtk': make_shim(ERRORS), 'db': STORE, 'cfg': Cfg(),
      'harmonics_engine': harmonics_engine, 'openAstro': OpenAstro(),
      '_': lambda s: s}
exec(grab('specialHarmonic'), ns)
exec(grab('specialHarmonicSubmit'), ns)


class Win(object):
    specialHarmonic = ns['specialHarmonic']
    specialHarmonicSubmit = ns['specialHarmonicSubmit']
    window = None

    def updateChart(self):
        CALLS.append(('updateChart',))


def open_dialog(w):
    """Open it and hand back the spin button, without submitting."""
    captured = {}
    w.specialHarmonicSubmit = lambda widget, entry: captured.setdefault('e', entry)
    w.specialHarmonic(None)
    ok = None
    for where in (w.win_SH.action_area, w.win_SH.vbox):
        ok = find_button(where, 'OK')
        if ok is not None:
            break
    assert ok is not None, 'no OK button in the dialog'
    ok.emit('clicked')
    del w.specialHarmonicSubmit
    return captured['e']


# ------------------------------------------------------ first open: defaults
w = Win()
entry = open_dialog(w)
R.note('harmonic defaults with an empty astrocfg: %d' % (entry.get_value_as_int(),))
R.check('N defaults to the identity (%d)' % (harmonics_engine.DEFAULT_HARMONIC,),
        entry.get_value_as_int() == harmonics_engine.DEFAULT_HARMONIC,
        entry.get_value_as_int())

# ----------------------------------------------------- what reaches the engine
del CALLS[:]
entry.set_value(5)
w.specialHarmonicSubmit(None, entry)
R.note('localToHarmonic called with: %s' % (CALLS[0] if CALLS else None,))
R.check('the request reaches the engine',
        CALLS and CALLS[0] == ('localToHarmonic', 5), CALLS[:1])
R.check('the chart is redrawn', ('updateChart',) in CALLS)
R.note('stored in astrocfg: %s' % (dict(sorted(STORE.items())),))
R.check('the harmonic order persists', STORE == {'harmonic_n': '5'}, dict(STORE))

# ------------------------------------------------- reopening restores the value
w2 = Win()
entry2 = open_dialog(w2)
R.check('the harmonic order comes back',
        entry2.get_value_as_int() == 5, entry2.get_value_as_int())

# ------------------------------------------------------------ the range bounds
# valid_harmonic() clamps, but the spinner should not let it get that far.
entry2.set_value(0)
R.check('the spinner refuses a harmonic below %d' % (harmonics_engine.MIN_HARMONIC,),
        entry2.get_value_as_int() >= harmonics_engine.MIN_HARMONIC,
        entry2.get_value_as_int())
entry2.set_value(9999)
R.check('the spinner refuses a harmonic above %d' % (harmonics_engine.MAX_HARMONIC,),
        entry2.get_value_as_int() <= harmonics_engine.MAX_HARMONIC,
        entry2.get_value_as_int())

R.finish()
