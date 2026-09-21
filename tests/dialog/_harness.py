# -*- coding: utf-8 -*-
"""Shared scaffolding for driving the program's real dialogs headless.

The method bodies are lifted out of the `openastro` script and bound to a
stub window, so the widgets, the astrocfg round-trip and the validation
path exercised here are the shipped ones. Only what would block is
replaced.

Leading underscore, so tests/run.sh does not try to run this file.

What has to be faked, and why only this:

  MessageDialog.run()   a modal loop, and nobody will click Close. There
                        are 9 of them, and any one reached by a validation
                        path hangs the run forever.
  Dialog.run()          same, for the 21 dialogs that use the synchronous
                        ACCEPT/REJECT form.

Everything else is the real Gtk. That is the point: a stubbed widget tree
proves nothing about a dialog, because there the widget tree IS the result.
"""
import io
import os
import re
import textwrap

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

ROOT = os.environ.get('OA_ROOT', '.')
SRC = io.open(os.path.join(ROOT, 'openastro'), encoding='utf-8').read().split('\n')


def grab(name):
    """The source of one method of `openastro`, dedented ready to exec."""
    start, out = None, []
    for i, line in enumerate(SRC):
        if re.match(r'    def %s\(' % (name,), line):
            start = i
            out.append(line)
            continue
        if start is not None:
            if line.strip() and not line.startswith('        ') and not line.startswith('    #'):
                break
            out.append(line)
    assert out, 'no method named %s' % (name,)
    return textwrap.dedent('\n'.join(out))


class Store(dict):
    """Stands in for the astrocfg table."""

    def getAstrocfg(self, key):
        return self.get(key)

    def setAstrocfg(self, key, value):
        self[key] = value


class Cfg(object):
    iconWindow = os.path.join(ROOT, 'icons', 'openastro.svg')
    tempfilenametable = os.path.join(os.environ.get('OA_OUT', '/tmp'), 'table.svg')
    tempfilenametableprint = os.path.join(os.environ.get('OA_OUT', '/tmp'), 'table-print.svg')
    xml_svg_table = os.path.join(ROOT, 'openastro-svg-table.xml')


def make_shim(errors, responses=None, on_run=None):
    """A Gtk stand-in that answers the modal loops instead of hanging.

    `errors` collects every message a MessageDialog was given, so a test can
    assert that bad input was refused *and* read back what the user would
    have been told. `responses` is a list of Gtk.ResponseType values handed
    to successive Dialog.run() calls, defaulting to ACCEPT -- pass REJECT to
    exercise the cancel path.

    `on_run(dialog)` runs just before each answer. That callback is the only
    moment a test can fill the widgets: the dialog is built, and the method
    has not yet read the values back. Monkeypatching Gtk.Dialog.run from
    outside does not work -- the dialog in play is the subclass below, which
    has its own run() and wins.
    """
    queue = list(responses or [])

    class FakeMessageDialog(object):
        def __init__(self, *a, **kw):
            errors.append(a[-1] if a else kw.get('message_format'))

        def run(self):
            return Gtk.ResponseType.CLOSE

        def destroy(self):
            pass

    class FakeDialog(Gtk.Dialog):
        def run(self):
            if on_run is not None:
                on_run(self)
            return queue.pop(0) if queue else Gtk.ResponseType.ACCEPT

    class Shim(object):
        MessageDialog = FakeMessageDialog
        Dialog = FakeDialog

        def __getattr__(self, key):
            return getattr(Gtk, key)

    return Shim()


def find_button(container, label_fragment):
    """Depth-first search of a widget tree for a button by its label."""
    found = []

    def walk(widget):
        try:
            label = widget.get_label()
        except Exception:
            label = None
        if label and label_fragment in label:
            found.append(widget)
        try:
            children = widget.get_children()
        except Exception:
            children = []
        for child in children:
            walk(child)

    walk(container)
    return found[0] if found else None


class Report(object):
    """Check counter, so the summary cannot drift from what ran.

    A hardcoded total went stale once already when the thing it counted
    disappeared.
    """

    def __init__(self, title):
        self.title = title
        self.total = 0
        self.fails = []

    def check(self, label, condition, extra=''):
        self.total += 1
        if not condition:
            self.fails.append(label)
        print('  %-54s %s %s' % (label, 'ok' if condition else 'FAILS', extra))

    def note(self, text):
        print('  %s' % (text,))

    def finish(self):
        print('\n%s: %d checks, %d failed' % (self.title, self.total, len(self.fails)))
        if self.fails:
            for f in self.fails:
                print('  FAILED: %s' % (f,))
            raise SystemExit(1)
        raise SystemExit(0)
