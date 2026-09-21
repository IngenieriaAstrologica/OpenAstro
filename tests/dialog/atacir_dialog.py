# -*- coding: utf-8 -*-
"""Drive the real specialAtacir()/specialAtacirSubmit() dialog headless.

This dialog has never been opened by anything. It has the most moving parts
of the technique dialogs -- a spin button for the cycle, two combo boxes, and
a label that recomputes as the spinner moves -- so it is the one most likely
to be hiding something.
"""
import datetime
import os
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _harness import grab, Store, Cfg, make_shim, find_button, Report

from openastromod import atacir as atacir_engine

R = Report('atacir dialog')
STORE = Store()
ERRORS = []
CALLS = []


class OpenAstro(object):
    year, month, day = 1987, 4, 9

    def localToAtacir(self, dt, cycle, converse, key):
        CALLS.append(('localToAtacir', dt, cycle, converse, key))

    def makeSVG(self):
        CALLS.append(('makeSVG',))


ns = {'datetime': datetime, 'Gtk': make_shim(ERRORS), 'db': STORE, 'cfg': Cfg(),
      'atacir_engine': atacir_engine, 'openAstro': OpenAstro(),
      '_': lambda s: s}
exec(grab('specialAtacir'), ns)
exec(grab('specialAtacirSubmit'), ns)


class Win(object):
    specialAtacir = ns['specialAtacir']
    specialAtacirSubmit = ns['specialAtacirSubmit']
    window = None
    _reset = 0

    def _resetChartViewBoth(self):
        Win._reset += 1

    def updateChart(self):
        CALLS.append(('updateChart',))


def open_dialog(w):
    """Open it and hand back the entry dict, without submitting."""
    captured = {}
    w.specialAtacirSubmit = lambda widget, entry: captured.setdefault('e', entry)
    w.specialAtacir(None)
    ok = find_button(w.win_SAT.vbox, 'Submit')
    assert ok is not None, 'no Submit button in the dialog'
    ok.emit('clicked')
    del w.specialAtacirSubmit
    return captured['e']


# ------------------------------------------------------ first open: defaults
w = Win()
entry = open_dialog(w)
now = datetime.datetime.now()
got = tuple(entry[k].get_text() for k in ('Y', 'M', 'D'))
R.note('defaults with an empty astrocfg: %s' % (got,))
R.check('opens on today', got == ('%d' % now.year, '%02d' % now.month, str(now.day)), got)
R.check('cycle defaults to C-%d' % (atacir_engine.DEFAULT_CYCLE,),
        entry['C'].get_value_as_int() == atacir_engine.DEFAULT_CYCLE,
        'C-%d' % entry['C'].get_value_as_int())
R.check('direction defaults to Direct', entry['R'].get_active() == 0)
R.check('rate defaults to the cycle', entry['K'].get_active() == 0)

# ------------------------------------------- the rate label tracks the spinner
# The label is the only feedback that says what a cycle means, and it is
# recomputed by a signal handler. If that handler is wrong the dialog still
# works and quietly lies about the rate.
entry['C'].set_value(360)
label_360 = None
for child in w.win_SAT.vbox.get_children():
    lab = find_button(child, 'per year')
    if lab is not None:
        label_360 = lab.get_label()
R.note('C-360 reads: %s' % (label_360,))
R.check('C-360 is described as one degree a year',
        label_360 is not None and "1°00'" in label_360, label_360)

entry['C'].set_value(12)
label_12 = None
for child in w.win_SAT.vbox.get_children():
    lab = find_button(child, 'per year')
    if lab is not None:
        label_12 = lab.get_label()
R.note('C-12  reads: %s' % (label_12,))
R.check('C-12 is described as thirty degrees a year',
        label_12 is not None and "30°00'" in label_12, label_12)
R.check('the label is plain text, not SVG entities',
        label_12 is not None and '&#' not in label_12, label_12)

# ----------------------------------------------------- what reaches the engine
del CALLS[:]
entry['Y'].set_text('2020')
entry['M'].set_text('12')
entry['D'].set_text('21')
entry['C'].set_value(24)
entry['R'].set_active(1)          # converse
entry['K'].set_active(1)          # solar arc
w.specialAtacirSubmit(None, entry)
R.note('localToAtacir called with: %s' % (CALLS[0] if CALLS else None,))
R.check('the request reaches the engine',
        CALLS and CALLS[0] == ('localToAtacir', datetime.datetime(2020, 12, 21),
                               24, True, 'solar_arc'), CALLS[:1])
R.check('the chart is redrawn as a bi-wheel',
        Win._reset == 1 and ('updateChart',) in CALLS)
R.note('stored in astrocfg: %s' % (dict(sorted(STORE.items())),))
R.check('cycle, direction and rate persist',
        STORE == {'atacir_cycle': '24', 'atacir_dir': '1',
                  'atacir_key': 'solar_arc'}, dict(STORE))

# ------------------------------------------------- reopening restores the rest
w2 = Win()
entry2 = open_dialog(w2)
got2 = tuple(entry2[k].get_text() for k in ('Y', 'M', 'D'))
R.note('reopened on %s with C-%d, dir %d, rate %d' % (
    got2, entry2['C'].get_value_as_int(), entry2['R'].get_active(),
    entry2['K'].get_active()))
R.check('reopens on today, not on the date last used',
        got2 == ('%d' % now.year, '%02d' % now.month, str(now.day)), got2)
R.check('the cycle comes back', entry2['C'].get_value_as_int() == 24)
R.check('the direction comes back', entry2['R'].get_active() == 1)
R.check('the rate comes back', entry2['K'].get_active() == 1)

# ------------------------------------------------------------ the cycle bounds
# valid_cycle() clamps, but the spinner should not let it get that far.
entry2['C'].set_value(0)
R.check('the spinner refuses a cycle below %d' % (atacir_engine.MIN_CYCLE,),
        entry2['C'].get_value_as_int() >= atacir_engine.MIN_CYCLE,
        'C-%d' % entry2['C'].get_value_as_int())
entry2['C'].set_value(9999)
R.check('the spinner refuses a cycle above %d' % (atacir_engine.MAX_CYCLE,),
        entry2['C'].get_value_as_int() <= atacir_engine.MAX_CYCLE,
        'C-%d' % entry2['C'].get_value_as_int())

# --------------------------------------------------------- a date it cannot use
# Every technique dialog builds a datetime from raw entry text. Without a
# guard that is an unhandled exception inside a signal handler: GTK prints a
# traceback to stderr the user never sees, and the OK button simply does
# nothing.
w3 = Win()
entry3 = open_dialog(w3)
del CALLS[:]
del ERRORS[:]
entry3['M'].set_text('13')
try:
    w3.specialAtacirSubmit(None, entry3)
    crashed = None
except Exception as exc:
    crashed = '%s: %s' % (type(exc).__name__, exc)
R.note('month 13 -> %s' % (crashed or (ERRORS[-1] if ERRORS else 'accepted'),))
R.check('month 13 is refused, not raised',
        crashed is None and not CALLS and ERRORS,
        crashed or (ERRORS[-1] if ERRORS else CALLS))

R.finish()
