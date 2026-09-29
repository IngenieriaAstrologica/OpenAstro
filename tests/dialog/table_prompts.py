# -*- coding: utf-8 -*-
"""Drive the table dialogs that ask a question before drawing.

Three of the Tables entries prompt first: Cyclic Index wants a span of
years, Harmogram wants a centre date and a window. They use the synchronous
Gtk.Dialog ACCEPT/REJECT form -- `dialog.run()` -- which nothing had
exercised, and they are the only dialogs carrying numeric guards of their
own. A guard that never runs is a guard nobody has checked.
"""
import datetime
import os
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _harness import grab, Store, Cfg, make_shim, Report

R = Report('table prompts')


class Chart(object):
    """Just enough of the open chart for a dialog to pick its defaults."""
    name = 'Prompt Fixture'
    year, month, day = 1987, 4, 9


def build(names, extra_ns, responses, on_run=None):
    """Bind the named methods against a fresh stub window."""
    errors = []
    store = Store()
    ns = {'datetime': datetime, 'Gtk': make_shim(errors, responses, on_run),
          'db': store, 'cfg': Cfg(), 'openAstro': Chart(), '_': lambda s: s}
    ns.update(extra_ns)
    for n in names:
        exec(grab(n), ns)
    return ns, store, errors


# =============================================================== Cyclic Index
from openastromod import cyclic as cyclic_engine

SHOWN = []


def cyclic_win(responses, fill=None):
    box = {}

    def on_run(dialog):
        if fill and 'w' in box:
            wid = getattr(box['w'], 'tCIwidget', None)
            if wid:
                for k, v in fill.items():
                    wid[k].set_text(v)

    ns, store, errors = build(['tableCyclicIndex'], {'cyclic_engine': cyclic_engine},
                              responses, on_run)

    class Win(object):
        tableCyclicIndex = ns['tableCyclicIndex']
        window = None
        tabletype = None

        def tableCyclicIndexShow(self):
            SHOWN.append(dict(self.tCIentry))

    box['w'] = Win()
    return box['w'], store, errors


# accepted: the defaults should be a sane span, and they should draw
del SHOWN[:]
w, store, errors = cyclic_win([Gtk.ResponseType.ACCEPT])
w.tableCyclicIndex(None)
R.note('accepted with the defaults -> %s' % (SHOWN[0] if SHOWN else None,))
R.check('the default span is drawn', len(SHOWN) == 1, SHOWN)
if SHOWN:
    span = SHOWN[0]
    R.check('the default span runs forward',
            span['F'] < span['T'], '%s..%s' % (span['F'], span['T']))
    R.check('the default span is within the 400-year limit',
            span['T'] - span['F'] <= 400, span['T'] - span['F'])
    R.check('heliocentric is the default', span['H'] is True)

# cancelled: nothing should be drawn
del SHOWN[:]
w, store, errors = cyclic_win([Gtk.ResponseType.REJECT])
w.tableCyclicIndex(None)
R.check('cancelling draws nothing', not SHOWN, SHOWN)

# the guards: backwards, too wide, out of range, not a number
for label, F, T, ok_expected in (
        ('a span running backwards', '2000', '1900', False),
        ('a span wider than 400 years', '1000', '2900', False),
        ('a year before 1000', '0999', '1100', False),
        ('a year after 2900', '2800', '2950', False),
        ('letters instead of a year', 'abcd', '2000', False),
        ('a legitimate span', '1900', '2000', True)):
    del SHOWN[:]
    w, store, errors = cyclic_win([Gtk.ResponseType.ACCEPT], {'F': F, 'T': T})
    w.tableCyclicIndex(None)
    drew = bool(SHOWN)
    R.check('%s is %s' % (label, 'accepted' if ok_expected else 'refused'),
            drew == ok_expected,
            '%s (%s)' % ('drew' if drew else 'refused',
                         errors[-1] if errors and not drew else ''))


# =================================================================== Harmogram
from openastromod import harmogram as harmogram_engine

HG = []


def harmo_win(days, ppd, mode_index):
    errors = []
    store = Store()
    box = {}

    def on_run(dialog):
        wid = getattr(box.get('w'), 'tHGwidget', None)
        if wid:
            wid['days'].set_value(days)
            wid['ppd'].set_value(ppd)
            wid['mode'].set_active(mode_index)

    ns = {'datetime': datetime, 'Gtk': make_shim(errors, None, on_run),
          'db': store, 'cfg': Cfg(), 'harmogram_engine': harmogram_engine,
          'openAstro': Chart(), '_': lambda s: s}
    exec(grab('tableHarmogram'), ns)

    class Win(object):
        tableHarmogram = ns['tableHarmogram']
        window = None
        tabletype = None

        def tableHarmogramShow(self):
            HG.append(dict(self.tHGentry))

    box['w'] = Win()
    box['w'].tableHarmogram(None)
    return store, errors


del HG[:]
store, errors = harmo_win(16, 36, 0)
R.note('16 days x 36/day, natal -> %s' % (HG[0] if HG else None,))
R.check('a normal window is drawn', len(HG) == 1, HG)
if HG:
    R.check('the centre defaults to now',
            HG[0]['C'].date() == datetime.date.today(), HG[0]['C'])
    R.check('natal is the default reading', HG[0]['mode'] == 'natal', HG[0]['mode'])
R.check('the choices persist',
        store.get('harmogram_days') == '16' and store.get('harmogram_ppd') == '36',
        dict(store))

# the cost guard: days x samples must not exceed 3000
del HG[:]
store, errors = harmo_win(200, 36, 0)
R.note('200 days x 36/day = 7200 samples -> %s' % (errors[-1] if errors else 'no error'))
R.check('an unaffordable window is refused', not HG and errors, HG)

del HG[:]
store, errors = harmo_win(80, 36, 1)
R.check('2880 samples is allowed', len(HG) == 1, HG)
if HG:
    R.check('the transits reading is passed through',
            HG[0]['mode'] == 'transits', HG[0]['mode'])

R.finish()
