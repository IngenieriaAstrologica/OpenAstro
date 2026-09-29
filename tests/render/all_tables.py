# -*- coding: utf-8 -*-
"""Render every SVG table for real and rasterise it.

This replaces the one-script-per-table harnesses that grew up during
development. They all did the same thing: pull a method's source out of the
`openastro` script with a regex, exec it against stubs, write the SVG.

That trick works because of a property these particular methods share -- they
build the whole page with string.Template and write it to disk *before* they
touch GTK -- so a catch-all mock absorbs the GTK half. It does not generalise
to dialogs, where the widget tree is the result. For those see tests/dialog/.

What this catches: template placeholders that no longer resolve, XML that
Rsvg refuses, geometry that throws, and any table whose method signature
drifts. What it cannot catch is whether the drawing looks right; that is what
the golden images in tests/render/golden are for, and even they only report
that something *changed*.
"""
import os
import sys
import math
import datetime
import importlib.util
import importlib.machinery
import tempfile
from string import Template

ROOT = os.environ.get("OA_ROOT") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.environ.get("OA_OUT") or tempfile.mkdtemp(prefix="oa-render-")

# openAstroCfg() writes ~/.openastro.org/; on a real HOME that is the user's
# live database. Redirect before importing anything from the script.
if not os.environ.get("HOME", "").startswith(tempfile.gettempdir()):
    os.environ["HOME"] = tempfile.mkdtemp(prefix="oa-render-home-")

os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.argv = ["openastro"]

import gi
gi.require_version("Rsvg", "2.0")
from gi.repository import Rsvg
import cairo
import swisseph as swe

spec = importlib.util.spec_from_loader(
    "oa", importlib.machinery.SourceFileLoader("oa", os.path.join(ROOT, "openastro")))
oa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oa)          # mainWindow() is behind the __main__ guard

oa.cfg = oa.openAstroCfg()
oa.db = oa.openAstroSqlite()
oa.openAstro = oa.openAstroInstance()
oa.cfg.tempfilenametable = os.path.join(OUT, "table.svg")
oa.cfg.tempfilenametableprint = os.path.join(OUT, "table-print.svg")

#a fixed chart, so a golden image means something
oa.openAstro.name = "Render Fixture"
oa.openAstro.year, oa.openAstro.month, oa.openAstro.day = 1987, 4, 9
oa.openAstro.hour = 12.0
oa.openAstro.geolat, oa.openAstro.geolon, oa.openAstro.altitude = 40.4165, -3.70256, 600
oa.openAstro.location = "Madrid, Spain"
oa.openAstro.timezone = 1.0
oa.openAstro.charttype = "Radix"
oa.openAstro.type = "Radix"
oa.openAstro.makeSVG()


class Window(object):
    """Stands in for mainWindow without building one.

    The table methods only reach back for `self.window` (a parent for
    dialogs), `self.tabletype`, and the print helper. Everything a real
    mainWindow does beyond that is menu and chart plumbing they never touch.
    """
    window = None
    tabletype = None

    def tableMonthlyTimelinePrint(self, **kw):
        pass


def rasterise(svg_path, png_path):
    handle = Rsvg.Handle.new_from_file(svg_path)
    w, h = float(handle.props.width), float(handle.props.height)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w), int(h))
    cr = cairo.Context(surface)
    cr.set_source_rgb(1, 1, 1)
    cr.paint()
    vp = Rsvg.Rectangle()
    vp.x, vp.y, vp.width, vp.height = 0.0, 0.0, w, h
    handle.render_document(cr, vp)
    surface.write_to_png(png_path)
    return w, h


#Tables that draw straight from the open chart, with no dialog to answer.
DIRECT = [
    ("cuspaspects", "tableCuspAspects"),
    ("fixedstars", "tableFixedStars"),
    ("firdaria", "tableFirdaria"),
    ("midpoints", "tableMidpoints"),
    ("arabicparts", "tableArabicParts"),
    ("profections", "tableProfections"),
    ("harmonicflower", "tableHarmonicFlower"),
]

#Tables whose dialog sets state first; the state is supplied here directly so
#the *drawing* half can be exercised without answering a dialog.
VIA_STATE = [
    ("cyclic", "tableCyclicIndexShow", "tCIentry",
     {"F": 1980, "T": 2030, "H": True}),
    ("harmogram-natal", "tableHarmogramShow", "tHGentry",
     {"C": datetime.datetime(2026, 9, 21, 12, 0), "days": 16, "ppd": 12,
      "mode": "natal"}),
    ("harmogram-transits", "tableHarmogramShow", "tHGentry",
     {"C": datetime.datetime(2026, 9, 21, 12, 0), "days": 16, "ppd": 12,
      "mode": "transits"}),
    ("mundane", "tableMundaneShow", "tMUentry",
     {"F": datetime.datetime(2026, 1, 1), "T": datetime.datetime(2027, 1, 1),
      "categories": ("ingress_sun", "lunation", "eclipse")}),
]

fails = []


def attempt(label, fn):
    svg = oa.cfg.tempfilenametable
    if os.path.exists(svg):
        os.unlink(svg)
    try:
        fn()
    except Exception as exc:
        fails.append("%s: %s: %s" % (label, type(exc).__name__, exc))
        print("  FAIL  %-22s %s: %s" % (label, type(exc).__name__, exc))
        return
    if not os.path.exists(svg):
        fails.append("%s: wrote no SVG" % (label,))
        print("  FAIL  %-22s wrote no SVG" % (label,))
        return
    png = os.path.join(OUT, "%s.png" % (label,))
    try:
        w, h = rasterise(svg, png)
    except Exception as exc:
        fails.append("%s: Rsvg refused the SVG: %s" % (label, exc))
        print("  FAIL  %-22s Rsvg refused it: %s" % (label, exc))
        return
    print("  ok    %-22s %5d x %-5d  %7d bytes" % (
        label, w, h, os.path.getsize(png)))


for label, method in DIRECT:
    w = Window()
    attempt(label, lambda w=w, m=method: getattr(w, m, None) or
            oa.mainWindow.__dict__[m](w, None))

for label, method, attr, state in VIA_STATE:
    w = Window()
    setattr(w, attr, state)
    attempt(label, lambda w=w, m=method: oa.mainWindow.__dict__[m](w, None))

print("\n%d rendered, %d failed" % (len(DIRECT) + len(VIA_STATE) - len(fails),
                                    len(fails)))
sys.exit(1 if fails else 0)
