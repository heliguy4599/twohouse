from gi.repository import Adw, Gtk, GLib, Gio, Pango
from .flatpak import Flatpak

import os, pathlib

class app_box(Adw.ActionRow):
    def __init__(self, folder, **kwargs):
        super().__init__(**kwargs)

        # self.add_css_class("card")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        title_box = Gtk.Box(halign=Gtk.Align.FILL, spacing=6, margin_end=18)

        image = Gtk.Image(margin_start=12, margin_end=12, margin_top=12, margin_bottom=12)
        image.set_from_icon_name("application-x-executable-symbolic")
        image.set_icon_size(Gtk.IconSize.LARGE)
        title_box.append(image)

        self.label = Gtk.Label(ellipsize=Pango.EllipsizeMode.MIDDLE, hexpand=True, halign=Gtk.Align.START, label=folder.split(".")[-1])
        self.label.add_css_class("title-4")
        title_box.append(self.label)

        
        lower_box = Gtk.Box(halign=Gtk.Align.FILL, spacing=6, margin_start=12, margin_end=6, margin_bottom=6)
        
        size = Gtk.Label(label="26 MB", hexpand=True, halign=Gtk.Align.START)
        lower_box.append(size)

        self.open_folder = Gtk.Button(icon_name="folder-open-symbolic")
        self.open_folder.add_css_class("flat")
        self.open_folder.add_css_class("circular")
        lower_box.append(self.open_folder)

        self.trash = Gtk.Button(icon_name="user-trash-symbolic")
        self.trash.add_css_class("flat")
        self.trash.add_css_class("circular")
        lower_box.append(self.trash)

        self.select = Gtk.CheckButton(visible=False, can_focus=False)
        self.select.add_css_class("selection-mode")
        lower_box.append(self.select)

        confirm_box = Gtk.Box(halign=Gtk.Align.FILL, spacing=6, margin_start=6, margin_end=6, margin_bottom=6)

        ye = Gtk.Button(label="Trash", hexpand=True)
        ye.add_css_class("destructive-action")
        confirm_box.append(ye)

        no = Gtk.Button(label="Cancel", hexpand=True)
        confirm_box.append(no)

        stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.CROSSFADE)
        stack.add_child(lower_box)
        stack.add_child(confirm_box)

        box.append(title_box)
        box.append(stack)
        self.set_child(box)
        self.set_activatable_widget(self.select)
        self.set_activatable(False)

        def on_trash(button, toggle, *args):
            stack.set_visible_child(confirm_box if toggle else lower_box)

        self.trash.connect("clicked", on_trash, True)
        no.connect("clicked", on_trash, False)

@Gtk.Template(resource_path='/org/gnome/Example/user_data_view.ui')
class UserDataView(Adw.NavigationPage):
    __gtype_name__ = 'UserDataView'

    select_button = Gtk.Template.Child()
    flow_box = Gtk.Template.Child()
    search_bar = Gtk.Template.Child()
    search_entry = Gtk.Template.Child()

    def generate_list(self, *args):
        for i, folder in enumerate(os.listdir(str(pathlib.Path.home()) + "/.var/app/")):
            box = app_box(folder)
            self.data_boxes.append(box)

            dumb = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
            dumb.append(box)
            dumb.add_css_class("boxed-list")

            self.flow_box.append(dumb)

            self.flow_box.get_child_at_index(i).set_focusable(False)

    def select_mode_handler(self, button):
        for box in self.data_boxes:
            box.set_activatable(button.get_active())
            box.select.set_visible(button.get_active())
            box.open_folder.set_visible(not button.get_active())
            box.trash.set_visible(not button.get_active())

    def on_search(self, entry):
        text = entry.get_text()
        for i, box in enumerate(self.data_boxes):
            visible = text.lower() in box.label.get_text().lower() or text == ""
            # box.set_visible(visible)
            self.flow_box.get_child_at_index(i).set_visible(visible)

    def __init__(self, main_window, **kwargs):
        super().__init__(**kwargs)

        self.data_boxes = []

        self.main_window = main_window

        self.generate_list()

        self.select_button.connect("toggled", self.select_mode_handler)

        self.search_bar.connect_entry(self.search_entry)

        self.search_entry.connect("search-changed", self.on_search)

