import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
print('constantes usadas en el codigo actual:')
for n in ('MESSAGE_ERROR','BUTTONS_CLOSE','ButtonS_CLOSE'):
    print('   Gtk.%-14s existe? %s' % (n, hasattr(Gtk,n)))
print('\nlas correctas en GTK3:')
print('   Gtk.MessageType.ERROR   ->', Gtk.MessageType.ERROR)
print('   Gtk.ButtonsType.CLOSE   ->', Gtk.ButtonsType.CLOSE)
print('\nconclusion: las tres actuales lanzarian AttributeError al ejecutarse')
