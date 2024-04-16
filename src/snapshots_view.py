from gi.repository import Adw, Gtk, GLib, Gio

@Gtk.Template(resource_path='/org/gnome/Example/snapshots_view.ui')
class SnapshotsView(Adw.NavigationPage):
    __gtype_name__ = 'SnapshotsView'

    def __init__(self, main_window, **kwargs):
        super().__init__(**kwargs)

        self.main_window = main_window