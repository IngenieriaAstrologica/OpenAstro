# -*- coding: utf-8 -*-
"""Drive the remaining derived-chart dialogs headless.

Solar Return, Lunar Return, Secondary Progressions, Antiscia and Primary
Directions. None of them had been opened by anything either; between this
file and its two siblings, every technique dialog in the Special menu is now
exercised.

What is checked for each is the same short list, because it is the list that
catches real faults: it opens without raising, its fields default to
something sensible, what the user typed is what reaches the engine, the
preferences that should persist do, and the date does not -- these dialogs
were all changed to open on the current moment.
"""
import datetime
import os
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _harness import grab, Store, Cfg, make_shim, find_button, Report

from openastromod import primary as primary_engine

R = Report('special charts')
NOW = datetime.datetime.now()


class Chart(object):
    """Records every request the dialogs make of the engine."""

    def __init__(self, calls):
        self.calls = calls
        self.year, self.month, self.day = 1987, 4, 9

    def __getattr__(self, name):
        if name.startswith('localTo') or name == 'makeSVG':
            def record(*a, **kw):
                self.calls.append((name,) + a)
            return record
        raise AttributeError(name)


def bind(methods, extra=None):
    """Bind method bodies to a stub window, with fresh recorders."""
    calls, errors = [], []
    store = Store()
    ns = {'datetime': datetime, 'Gtk': make_shim(errors), 'db': store,
          'cfg': Cfg(), 'primary_engine': primary_engine,
          'openAstro': Chart(calls), '_': lambda s: s}
    ns.update(extra or {})
    for m in methods:
        exec(grab(m), ns)

    class Win(object):
        window = None
        _reset = 0

        def _resetChartViewBoth(self):
            Win._reset += 1

        def updateChart(self):
            calls.append(('updateChart',))

    for m in methods:
        setattr(Win, m, ns[m])
    return Win(), store, errors, calls


def fresh(methods, opener, submitter, win_attr, extra=None):
    """A brand-new dialog, open and ready.

    One per case, deliberately. A successful submit calls destroy() on its
    window, and reusing the entries afterwards reads widgets that are on
    their way out -- which produced three convincing failures against
    dialogs that were behaving correctly.
    """
    w, store, errors, calls = bind(methods, extra)
    entry, win = open_and_capture(w, opener, submitter, win_attr)
    return w, entry, store, errors, calls


def open_and_capture(w, opener, submitter, win_attr, button='OK'):
    """Open the dialog and hand back its entry dict without submitting.

    These five put their OK in the action area; the atacir dialog puts a
    Submit inside the table. Search both rather than assume either.
    """
    captured = {}
    setattr(w, submitter, lambda widget, entry: captured.setdefault('e', entry))
    getattr(w, opener)(None)
    win = getattr(w, win_attr)
    ok = None
    for where in (win.action_area, win.vbox):
        ok = find_button(where, button)
        if ok is not None:
            break
    assert ok is not None, 'no %s button in %s' % (button, opener)
    ok.emit('clicked')
    delattr(w, submitter)
    return captured['e'], win


# ===================================================== Solar Return (year only)
# Solar Return and Antiscia hand their submit a single widget, not the dict
# of widgets the other dialogs use.
w, store, errors, calls = bind(['specialSolar', 'specialSolarSubmit'])
entry, win = open_and_capture(w, 'specialSolar', 'specialSolarSubmit', 'win_SS')
R.note('solar return offers year %s' % (entry.get_text(),))
R.check('solar return opens on this year',
        entry.get_text() == str(NOW.year), entry.get_text())
entry.set_text('2020')
w.specialSolarSubmit(None, entry)
R.check('the year reaches the engine',
        ('localToSolar', 2020) in calls, calls)

w, entry, store, errors, calls = fresh(
    ['specialSolar', 'specialSolarSubmit'], 'specialSolar',
    'specialSolarSubmit', 'win_SS')
entry.set_text('not a year')
try:
    w.specialSolarSubmit(None, entry)
    crashed = None
except Exception as exc:
    crashed = '%s: %s' % (type(exc).__name__, exc)
R.note('a non-numeric year -> %s' % (crashed or (errors[-1] if errors else 'accepted'),))
R.check('a year that is not a number is refused, not raised',
        crashed is None and not calls and errors,
        crashed or (errors[-1] if errors else calls))

# ============================================== Lunar Return (year, month, day)
w, store, errors, calls = bind(['specialLunar', 'specialLunarSubmit'])
entry, win = open_and_capture(w, 'specialLunar', 'specialLunarSubmit', 'win_SL')
got = tuple(entry[k].get_text() for k in ('Y', 'M', 'D'))
R.note('lunar return offers %s' % (got,))
R.check('lunar return opens on today',
        got == (str(NOW.year), '%02d' % NOW.month, str(NOW.day)), got)
R.check('it asks for a day, not just a month', 'D' in entry)
entry['Y'].set_text('2020'); entry['M'].set_text('12'); entry['D'].set_text('21')
w.specialLunarSubmit(None, entry)
R.check('the whole date reaches the engine',
        ('localToLunar', 2020, 12, 21) in calls, calls)

w, entry, store, errors, calls = fresh(
    ['specialLunar', 'specialLunarSubmit'], 'specialLunar',
    'specialLunarSubmit', 'win_SL')
entry['M'].set_text('13')
try:
    w.specialLunarSubmit(None, entry)
    crashed = None
except Exception as exc:
    crashed = '%s: %s' % (type(exc).__name__, exc)
R.note('month 13 -> %s' % (crashed or (errors[-1] if errors else 'accepted'),))
R.check('month 13 is refused, not raised',
        crashed is None and not calls and errors,
        crashed or (errors[-1] if errors else calls))

# ======================================================= Secondary Progressions
w, store, errors, calls = bind(['specialSecondaryProgression',
                                'specialSecondaryProgressionSubmit'])
entry, win = open_and_capture(w, 'specialSecondaryProgression',
                              'specialSecondaryProgressionSubmit', 'win_SSP')
got = tuple(entry[k].get_text() for k in ('Y', 'M', 'D'))
R.note('progressions offer %s' % (got,))
R.check('progressions open on today',
        got == (str(NOW.year), '%02d' % NOW.month, str(NOW.day)), got)
entry['Y'].set_text('2020'); entry['M'].set_text('12'); entry['D'].set_text('21')
entry['h'].set_text('23'); entry['m'].set_text('45')
w.specialSecondaryProgressionSubmit(None, entry)
R.check('the moment reaches the engine',
        ('localToSecondaryProgression', datetime.datetime(2020, 12, 21, 23, 45)) in calls,
        calls)

w, entry, store, errors, calls = fresh(
    ['specialSecondaryProgression', 'specialSecondaryProgressionSubmit'],
    'specialSecondaryProgression', 'specialSecondaryProgressionSubmit', 'win_SSP')
entry['h'].set_text('25')
try:
    w.specialSecondaryProgressionSubmit(None, entry)
    crashed = None
except Exception as exc:
    crashed = '%s: %s' % (type(exc).__name__, exc)
R.note('hour 25 -> %s' % (crashed or (errors[-1] if errors else 'accepted'),))
R.check('hour 25 is refused, not raised',
        crashed is None and not calls and errors,
        crashed or (errors[-1] if errors else calls))

# ==================================================================== Antiscia
w, store, errors, calls = bind(['specialAntiscia', 'specialAntisciaSubmit'])
entry, win = open_and_capture(w, 'specialAntiscia', 'specialAntisciaSubmit', 'win_SA')
R.check('antiscia defaults to antiscia, not contra', entry.get_active() == 0)
entry.set_active(1)
w.specialAntisciaSubmit(None, entry)
R.check('contra-antiscia reaches the engine',
        ('localToAntiscia', True) in calls, calls)
R.check('the choice persists', store.get('antiscia_contra') == '1', dict(store))

w2, store2, _e, _c = bind(['specialAntiscia', 'specialAntisciaSubmit'])
w2_entry, _w = open_and_capture(w2, 'specialAntiscia', 'specialAntisciaSubmit', 'win_SA')
R.check('a fresh dialog starts from its own empty store',
        w2_entry.get_active() == 0)

# =========================================================== Primary Directions
w, store, errors, calls = bind(['specialDirected', 'specialDirectedSubmit'])
entry, win = open_and_capture(w, 'specialDirected', 'specialDirectedSubmit', 'win_SPD')
got = tuple(entry[k].get_text() for k in ('Y', 'M', 'D'))
R.note('directions offer %s, key %d, dir %d, measure %d' % (
    got, entry['K'].get_active(), entry['R'].get_active(), entry['S'].get_active()))
R.check('directions open on today',
        got == (str(NOW.year), '%02d' % NOW.month, str(NOW.day)), got)
R.check('the key defaults to the first offered', entry['K'].get_active() == 0)
R.check('direction defaults to Direct', entry['R'].get_active() == 0)

entry['Y'].set_text('2020'); entry['M'].set_text('12'); entry['D'].set_text('21')
entry['h'].set_text('12'); entry['m'].set_text('00')
entry['R'].set_active(1)
w.specialDirectedSubmit(None, entry)
R.note('stored: %s' % (dict(sorted(store.items())),))
R.check('the direction persists', store.get('directed_dir') == '1', dict(store))
R.check('the date is not stored',
        not any(k.startswith('directed_Y') for k in store), dict(store))

w, entry, store, errors, calls = fresh(
    ['specialDirected', 'specialDirectedSubmit'], 'specialDirected',
    'specialDirectedSubmit', 'win_SPD')
entry['D'].set_text('32')
try:
    w.specialDirectedSubmit(None, entry)
    crashed = None
except Exception as exc:
    crashed = '%s: %s' % (type(exc).__name__, exc)
R.note('day 32 -> %s' % (crashed or (errors[-1] if errors else 'accepted'),))
R.check('day 32 is refused, not raised',
        crashed is None and not calls and errors,
        crashed or (errors[-1] if errors else calls))

R.finish()
