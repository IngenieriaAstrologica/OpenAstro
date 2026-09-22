# Drive the REAL specialTransit()/specialTransitSubmit() dialog headless.
# Both method bodies are lifted from the `openastro` script and bound to a
# stub window, so the widgets, the astrocfg round-trip and the validation
# path that run here are the shipped ones.
import datetime, io, os, re, textwrap
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from openastromod import primary as primary_engine

src = io.open('openastro', encoding='utf-8').read().split('\n')


def grab(name):
    start, out = None, []
    for i, line in enumerate(src):
        if re.match(r'    def %s\(' % name, line):
            start = i
            out.append(line)
            continue
        if start is not None:
            if line.strip() and not line.startswith('        ') and not line.startswith('    #'):
                break
            out.append(line)
    assert out, name
    return textwrap.dedent('\n'.join(out))


STORE = {}


class DB(object):
    def getAstrocfg(self, k):
        return STORE.get(k)

    def setAstrocfg(self, k, v):
        STORE[k] = v


class CFG(object):
    iconWindow = os.path.join('icons', 'openastro.svg')


ERRORS = []


class FakeMessageDialog(object):
    # the real one would block in run() with nobody to click Close
    def __init__(self, *a, **kw):
        ERRORS.append(a[-1] if a else kw.get('message_format'))

    def run(self):
        return Gtk.ResponseType.CLOSE

    def destroy(self):
        pass


class GtkShim(object):
    MessageDialog = FakeMessageDialog

    def __getattr__(self, k):
        return getattr(Gtk, k)


CALLS = []


class OpenAstro(object):
    def localToTransit(self, dt_local=None, converse=False, measure="ecliptic", target="natal"):
        CALLS.append((dt_local, converse, measure, target))

    def makeSVG(self):
        CALLS.append(('makeSVG',))


class Draw(object):
    def queue_draw(self):
        pass

    def setSVG(self, name):
        pass


ns = {'datetime': datetime, 'Gtk': GtkShim(), 'db': DB(), 'cfg': CFG(),
      'primary_engine': primary_engine, 'openAstro': OpenAstro(),
      '_': lambda s: s}
exec(grab('specialTransit'), ns)
exec(grab('specialTransitSubmit'), ns)


class Win(object):
    specialTransit = ns['specialTransit']
    specialTransitSubmit = ns['specialTransitSubmit']
    window = None
    draw = Draw()
    tempfilename = 'x.svg'
    _reset = 0

    def _resetChartViewBoth(self):
        Win._reset += 1


def open_dialog(w):
    captured = {}
    w.specialTransitSubmit = lambda widget, entry: captured.setdefault('e', entry)
    w.specialTransit(None)
    ok = None
    for child in w.win_ST.get_action_area().get_children():
        if 'OK' in (child.get_label() or ''):
            ok = child
    assert ok is not None, "no OK button"
    ok.emit("clicked")
    del w.specialTransitSubmit
    return captured['e'], ok


# ---------------------------------------------------------- first use: defaults
w = Win()
entry, ok = open_dialog(w)
now = datetime.datetime.now()
got = tuple(entry[k].get_text() for k in ('Y', 'M', 'D', 'h', 'm'))
print("defaults with an empty astrocfg:", got)
assert got[:3] == ('%d' % now.year, '%02d' % now.month, '%02d' % now.day), got
assert entry['R'].get_active() == 0 and entry['S'].get_active() == 0
assert entry['T'].get_active() == 0
print("[ok] first use offers today and Direct/Ecliptic/Natal positions")

# the Now button refills the fields
entry['Y'].set_text('1500')
for child in w.win_ST.get_children()[0].get_children():
    pass
found_now = []


def walk(widget):
    if isinstance(widget, Gtk.Button) and (widget.get_label() or '') == 'Now':
        found_now.append(widget)
    if hasattr(widget, 'get_children'):
        for c in widget.get_children():
            walk(c)


walk(w.win_ST)
assert found_now, "no Now button"
found_now[0].emit("clicked")
assert entry['Y'].get_text() == '%d' % datetime.datetime.now().year
print("[ok] the Now button puts the current moment back")

# ------------------------------------------------------ a full, valid request
for k, v in (('Y', '1999'), ('M', '12'), ('D', '31'), ('h', '23'), ('m', '45')):
    entry[k].set_text(v)
entry['R'].set_active(1)
entry['S'].set_active(1)
entry['T'].set_active(1)
w.specialTransitSubmit(ok, entry)
print("localToTransit called with:", CALLS[0])
assert CALLS[0] == (datetime.datetime(1999, 12, 31, 23, 45), True, 'ascensional', 'antiscion'), CALLS
assert ('makeSVG',) in CALLS and Win._reset == 1
print("stored in astrocfg:", {k: v for k, v in sorted(STORE.items())})
# The date is deliberately NOT remembered. Every technique dialog was
# changed to open on the current moment, and restoring the last date used
# would defeat that -- the point of a transit dialog is usually "now".
# Direction, measure and target are preferences and do persist.
assert STORE == {'transit_dir': '1', 'transit_measure': 'ascensional', 'transit_target': 'antiscion'}, STORE
print("[ok] the request reaches the engine; direction, measure and target")
print("     persist, and the date deliberately does not")

# --------------------------------------------- the dialog reopens where it was
w2 = Win()
entry2, ok2 = open_dialog(w2)
got2 = tuple(entry2[k].get_text() for k in ('Y', 'M', 'D', 'h', 'm'))
print("reopened with:", got2, "dir", entry2['R'].get_active(), "measure", entry2['S'].get_active(),
      "target", entry2['T'].get_active())
now2 = datetime.datetime.now()
assert got2[:3] == (str(now2.year), '%02d' % now2.month, '%02d' % now2.day), got2
assert entry2['R'].get_active() == 1 and entry2['S'].get_active() == 1
assert entry2['T'].get_active() == 1
print("[ok] it reopens on today, with the last direction, measure and target kept")

# ----------------------------------------------------------------- validation
del CALLS[:]
for bad, why in ((('13', 'M'), 'month 13'), (('32', 'D'), 'day 32'),
                 (('25', 'h'), 'hour 25'), (('99', 'm'), 'minute 99'),
                 (('', 'Y'), 'empty year'), (('abc', 'Y'), 'letters')):
    val, key = bad
    entry2[key].set_max_length(0)
    saved = entry2[key].get_text()
    entry2[key].set_text(val)
    w2.specialTransitSubmit(ok2, entry2)
    assert not CALLS, "%s reached the engine" % why
    assert ERRORS, "%s raised no error dialog" % why
    print("[ok] refused: %-12s -> %s" % (why, ERRORS[-1]))
    del ERRORS[:]
    entry2[key].set_text(saved)

entry2['Y'].set_text('999')
w2.specialTransitSubmit(ok2, entry2)
assert not CALLS and ERRORS
print("[ok] refused: year 999   -> %s" % ERRORS[-1])
del ERRORS[:]
entry2['Y'].set_text('1999')
# February 29 of a non leap year must be refused too, and of a leap year taken
entry2['M'].set_text('02'); entry2['D'].set_text('29')
w2.specialTransitSubmit(ok2, entry2)
assert not CALLS and ERRORS
print("[ok] refused: 1999-02-29 -> %s" % ERRORS[-1])
del ERRORS[:]
entry2['Y'].set_text('2000')
w2.specialTransitSubmit(ok2, entry2)
# only the date is under test here; the hour and minute are whatever the
# dialog reopened with, which is now the current time by design
assert CALLS and CALLS[0][0].date() == datetime.date(2000, 2, 29), CALLS
assert not ERRORS
print("[ok] accepted: 2000-02-29 ->", CALLS[0])

print()
print("DIALOG CHECKS PASSED")
