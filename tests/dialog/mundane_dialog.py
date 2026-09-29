# -*- coding: utf-8 -*-
"""Drive the Ingresses/Lunations/Eclipses dialog headless.

Same trick as table_prompts.py: the method body is lifted straight out of
`openastro` and bound to a stub window, so the widget tree, the astrocfg
round-trip and the validation guards are the shipped ones.
"""
import datetime
import os
import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _harness import grab, Store, Cfg, make_shim, Report

R = Report('mundane dialog')


class Chart(object):
    name = 'Prompt Fixture'
    year, month, day = 1987, 4, 9


SHOWN = []


def mundane_win(responses, fill=None):
    """fill: dict of widget key -> value. 'FY'/'FM'/'FD'/'TY'/'TM'/'TD' set
    Entry text; the four category keys ('ingress_sun' etc.) set a
    CheckButton's active state.
    """
    box = {}

    def on_run(dialog):
        wid = getattr(box.get('w'), 'tMUwidget', None)
        if not wid or not fill:
            return
        for k, v in fill.items():
            if isinstance(v, bool):
                wid[k].set_active(v)
            else:
                wid[k].set_text(v)

    errors = []
    store = Store()
    ns = {'datetime': datetime, 'Gtk': make_shim(errors, responses, on_run),
          'db': store, 'cfg': Cfg(), 'openAstro': Chart(), '_': lambda s: s,
          'mundane_engine': None}
    exec(grab('tableMundane'), ns)

    class Win(object):
        tableMundane = ns['tableMundane']
        window = None
        tabletype = None

        def tableMundaneShow(self):
            SHOWN.append(dict(self.tMUentry))

    box['w'] = Win()
    box['w'].tableMundane(None)
    return store, errors


# accepted: the defaults should be a sane span (the current calendar year)
# with Sun ingresses, lunations and eclipses on and Moon ingresses off
del SHOWN[:]
store, errors = mundane_win([Gtk.ResponseType.ACCEPT])
R.note('accepted with the defaults -> %s' % (SHOWN[0] if SHOWN else None,))
R.check('the default span is drawn', len(SHOWN) == 1, SHOWN)
if SHOWN:
    span = SHOWN[0]
    R.check('From is this year, January 1st',
            span['F'] == datetime.datetime(datetime.date.today().year, 1, 1), span['F'])
    R.check('To is one year later',
            span['T'] == datetime.datetime(datetime.date.today().year + 1, 1, 1), span['T'])
    R.check('categories default to sun ingress + lunation + eclipse (moon ingress off)',
            set(span['categories']) == {'ingress_sun', 'lunation', 'eclipse'}, span['categories'])
R.check('nothing persisted dates (only categories go to astrocfg)',
        'mundane_from' not in store and 'mundane_ingress_sun' in store, dict(store))

# cancelled: nothing should be drawn, nothing persisted
del SHOWN[:]
store, errors = mundane_win([Gtk.ResponseType.REJECT])
R.check('cancelling draws nothing', not SHOWN, SHOWN)
R.check('cancelling persists nothing', not store, dict(store))

# the guards
for label, fill, ok_expected in (
        ('To before From', {'FY': '2026', 'TY': '2020'}, False),
        ('To equal to From', {'TY': '2026', 'TM': '1', 'TD': '1', 'FY': '2026', 'FM': '1', 'FD': '1'}, False),
        ('a span wider than 40 years', {'FY': '1900', 'TY': '2000'}, False),
        ('an invalid calendar date', {'FM': '2', 'FD': '30'}, False),
        ('letters instead of a year', {'FY': 'abcd'}, False),
        ('a legitimate span', {'FY': '2020', 'FM': '1', 'FD': '1', 'TY': '2021', 'TM': '1', 'TD': '1'}, True)):
    del SHOWN[:]
    store, errors = mundane_win([Gtk.ResponseType.ACCEPT], fill)
    drew = bool(SHOWN)
    R.check('%s is %s' % (label, 'accepted' if ok_expected else 'refused'),
            drew == ok_expected,
            '%s (%s)' % ('drew' if drew else 'refused',
                         errors[-1] if errors and not drew else ''))

# no category selected at all
del SHOWN[:]
store, errors = mundane_win([Gtk.ResponseType.ACCEPT],
    {'ingress_sun': False, 'ingress_moon': False, 'lunation': False, 'eclipse': False})
R.check('no category selected is refused', not SHOWN and errors, errors)

# a non-default category selection round-trips and persists
del SHOWN[:]
store, errors = mundane_win([Gtk.ResponseType.ACCEPT],
    {'ingress_sun': False, 'ingress_moon': True, 'lunation': False, 'eclipse': True})
R.check('a custom selection is passed through',
        SHOWN and set(SHOWN[0]['categories']) == {'ingress_moon', 'eclipse'},
        SHOWN[0]['categories'] if SHOWN else None)
R.check('the custom selection persists to astrocfg',
        store.get('mundane_ingress_sun') == '0' and store.get('mundane_ingress_moon') == '1'
        and store.get('mundane_lunation') == '0' and store.get('mundane_eclipse') == '1',
        dict(store))

# and the persisted selection becomes the next dialog's default
store2, errors2 = mundane_win([Gtk.ResponseType.REJECT])
# re-run accepted immediately after, sharing nothing -- persistence lives in
# the Store passed in, so drive a second dialog against the SAME store to
# prove it sticks
del SHOWN[:]
box = {}


def on_run2(dialog):
    pass


ns = {'datetime': datetime, 'Gtk': make_shim([], [Gtk.ResponseType.ACCEPT], on_run2),
      'db': store, 'cfg': Cfg(), 'openAstro': Chart(), '_': lambda s: s}
exec(grab('tableMundane'), ns)


class Win2(object):
    tableMundane = ns['tableMundane']
    window = None
    tabletype = None

    def tableMundaneShow(self):
        SHOWN.append(dict(self.tMUentry))


w2 = Win2()
w2.tableMundane(None)
R.check('a later dialog opens with the persisted categories as default',
        SHOWN and set(SHOWN[0]['categories']) == {'ingress_moon', 'eclipse'},
        SHOWN[0]['categories'] if SHOWN else None)

R.finish()
