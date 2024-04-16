from gi.repository import Adw, Gtk, GLib, Gio, Pango
from .properties_pane import PropertiesPane
from .flatpak import Flatpak
from .common_resources import CommonResources

import subprocess

class AppRow(Adw.ActionRow):
    def __init__(self, pak_arr, **kwargs):
        super().__init__(**kwargs)

        self.set_activatable(True)

        self.package = Flatpak(pak_arr)
        self.image = Gtk.Image()
        self.add_prefix(self.image)
        self.set_title(self.package.info["name"])
        self.set_subtitle(self.package.info["id"])
        self.select_button = Gtk.CheckButton(visible=False)
        self.select_button.add_css_class("selection-mode")
        self.add_suffix(self.select_button)

        def done(*args):
            if self.package.get_icon_path():
                self.image.set_from_file(self.package.get_icon_path())
                self.image.set_icon_size(Gtk.IconSize.LARGE)
                self.image.add_css_class("icon-dropshadow")
            else:
                self.image.set_from_icon_name("application-x-executable-symbolic")
                self.image.set_icon_size(Gtk.IconSize.LARGE)

        Gio.Task.new(None, None, done).run_in_thread(self.package.get_icon_path)
        
        
        


@Gtk.Template(resource_path='/org/gnome/Example/packages_view.ui')
class PackagesView(Adw.BreakpointBin):
    __gtype_name__ = 'PackagesView'

    packages_split = Gtk.Template.Child()
    packages_list = Gtk.Template.Child()
    packages_bpt = Gtk.Template.Child()
    search_bar = Gtk.Template.Child()
    search_entry = Gtk.Template.Child()
    packages_scroll = Gtk.Template.Child()
    packages_tbv = Gtk.Template.Child()

    more_menu = Gtk.Template.Child()
    more_list = Gtk.Template.Child()
    refresh = Gtk.Template.Child()

    properties_pane = Gtk.Template.Child()

    sidebar_button = Gtk.Template.Child()

    select_button = Gtk.Template.Child()

    def filter_func(self, row):
        if self.search_entry.get_text().lower() in row.get_title().lower():
            return True

    def on_invalidate(self, row):
        self.packages_list.invalidate_filter()

    def show_info(self, list_box, row):
        self.properties_pane.generate_list(row.package)
        if self.packages_split.get_collapsed():
            self.packages_split.set_show_content(True)

    def generate_list(self, *args):
        self.packages_tbv.set_content(Adw.StatusPage(
            title="Loading",
            child=Gtk.Spinner(opacity=0.5, spinning=True)
        ))
        self.packages_list.remove_all()
        def thread(*args):
            arr = subprocess.run("flatpak-spawn --host flatpak list --columns=all", text=True, capture_output=True, shell=True).stdout.strip().split("\n")
            def thing(line):
                row = AppRow(line.split("\t"))
                self.packages_list.append(row)
                
            for i, line in enumerate(arr):
                GLib.idle_add(thing, line)

        def done(*args):
            self.packages_list.set_filter_func(self.filter_func)
            self.search_entry.connect("search-changed", self.on_invalidate)
            self.search_bar.connect_entry(self.search_entry)
            self.packages_tbv.set_content(self.packages_scroll)
            if not self.packages_split.get_collapsed():
                first = self.packages_list.get_row_at_index(0)
                self.packages_list.select_row(first)
                self.show_info(self.packages_list, first)

        task = Gio.Task.new(None, None, lambda *_: GLib.idle_add(done))
        task.run_in_thread(thread)

    def breakpoint_handler(self, *args):
        if self.properties_pane.package == None:
            # If the user widens the window to show the properties pane, but no row has been selected, select the first row
            first = self.packages_list.get_row_at_index(0)
            self.packages_list.select_row(first)
            self.show_info(self.packages_list, first)
        self.packages_split.set_show_content(False)
        self.properties_pane.properties_navpage.set_can_pop(False)

    def overflow_handler(self, list_box, row, *args):
        self.more_menu.popdown()
        match row:
            case self.refresh:
                self.generate_list()

    def sidebar_handler(self, sidebar, *args):
        self.sidebar_button.set_visible(sidebar.get_collapsed() or not sidebar.get_show_sidebar())

    def select_mode_handler(self, button):
        row = self.packages_list.get_row_at_index(0)
        i = 0
        while row != None:
            row.select_button.set_visible(button.get_active())
            i += 1
            row = self.packages_list.get_row_at_index(i)

    def __init__(self, main_window, **kwargs):
        super().__init__(**kwargs)

        self.main_window = main_window

        self.packages_list.connect("row-activated", self.show_info)

        self.packages_bpt.connect("apply", lambda *_: self.properties_pane.properties_navpage.set_can_pop(True))
        self.packages_bpt.connect("unapply", self.breakpoint_handler)

        self.more_list.connect("row-activated", self.overflow_handler)

        self.generate_list()

        # self.sidebar_button.connect("clicked", self.sidebar_handler)

        main_window.outer_split.connect("notify::show-sidebar", self.sidebar_handler)
        main_window.outer_split.connect("notify::collapsed", self.sidebar_handler)
        
        self.sidebar_button.connect("clicked", lambda *_: main_window.outer_split.set_show_sidebar(True))

        self.select_button.connect("clicked", self.select_mode_handler)