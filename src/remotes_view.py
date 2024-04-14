from gi.repository import Adw
from gi.repository import Gtk

@Gtk.Template(resource_path='/org/gnome/Example/remotes_view.ui')
class RemotesView(Adw.BreakpointBin):
    __gtype_name__ = 'RemotesView'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)