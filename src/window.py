# window.py
#
# Copyright 2024 Heliguy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk, GLib

from .packages_view import PackagesView
from .remotes_view import RemotesView
from .test import Test

@Gtk.Template(resource_path='/org/gnome/Example/window.ui')
class TwohouseWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'TwohouseWindow'

    packages = Gtk.Template.Child()
    remotes = Gtk.Template.Child()
    outer_sidebar_listbox = Gtk.Template.Child()
    outer_split = Gtk.Template.Child()
    outer_bpt = Gtk.Template.Child()
    ggg = Gtk.Template.Child()

    packages_view = Gtk.Template.Child()
    remotes_view = Gtk.Template.Child()
    content_stack = Gtk.Template.Child()

    views = {}

    def outer_navigation_handler(self, listbox, row):
        to_set = self.views[row.get_child()]
        if self.outer_split.get_content() != to_set:
            self.content_stack.set_visible_child(to_set)
        if self.outer_split.get_collapsed():
            self.outer_split.set_show_content(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)



        self.outer_sidebar_listbox.connect("row-activated", self.outer_navigation_handler)

        

        self.views = {
            self.packages: self.packages_view,
            self.remotes: self.remotes_view,
        }

        self.ggg.connect("apply", lambda *_: self.outer_split.set_show_content(True))

