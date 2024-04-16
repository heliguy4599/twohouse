from gi.repository import Adw, Gtk, GLib, Gio, Pango

class shared:
    icon_theme = Gtk.IconTheme.new()
    icon_theme.add_search_path("/var/lib/flatpak/exports/share/icons/")
    icon_theme.add_search_path("/home/heliguy/.local/share/flatpak/exports/share/icons")

@Gtk.Template(resource_path='/org/gnome/Example/properties_pane.ui')
class PropertiesPane(Adw.NavigationPage):
    __gtype_name__ = 'PropertiesPane'

    properties_navpage = Gtk.Template.Child()
    properties_header = Gtk.Template.Child()
    properties_scroll = Gtk.Template.Child()
    app_icon = Gtk.Template.Child()
    name = Gtk.Template.Child()
    description = Gtk.Template.Child()
    open_app_button = Gtk.Template.Child()
    uninstall_button = Gtk.Template.Child()
    more_menu = Gtk.Template.Child()

    # Grab the rows from the blp
    actions = Gtk.Template.Child()
    pin_row = Gtk.Template.Child()
    data_row = Gtk.Template.Child()
    version_row = Gtk.Template.Child()
    mask_row = Gtk.Template.Child()
    downgrade_row = Gtk.Template.Child()
    installed_size_row = Gtk.Template.Child()

    package_info = Gtk.Template.Child()
    id_row = Gtk.Template.Child()
    ref_row = Gtk.Template.Child()
    arch_row = Gtk.Template.Child()
    branch_row = Gtk.Template.Child()
    license_row = Gtk.Template.Child()

    remote_info = Gtk.Template.Child()
    runtime_row = Gtk.Template.Child()
    sdk_row = Gtk.Template.Child()
    origin_row = Gtk.Template.Child()
    collection_row = Gtk.Template.Child()
    installation_row = Gtk.Template.Child()

    commit_info = Gtk.Template.Child()
    commit_row = Gtk.Template.Child()
    parent_row = Gtk.Template.Child()
    subject_row = Gtk.Template.Child()
    date_row = Gtk.Template.Child()

    package = None

    def generate_list(self, in_package, *args):
        if self.package == in_package:
            # do not regenerate the list if the package to show info is the same package as last list generation
            return

        self.package = in_package
        # self.properties_navpage.set_title(in_package.info["name"] + " Properties")
        self.name.set_label(in_package.info["name"])
        desc = in_package.info["description"]
        self.description.set_label(desc)
        self.description.set_visible(len(desc) > 0)
        # self.properties_list.remove_all()
        
        def thread(*args):
            info = in_package.get_properties()
            info_dict = {}
            for line in info:
                if len(line) < 2:
                    continue
                info_dict[line[0].lower()] = line[1]

            def set_icon(*args):
                if self.package.get_icon_path():
                    self.app_icon.set_from_file(self.package.get_icon_path())
                    self.app_icon.set_icon_size(Gtk.IconSize.LARGE)
                    self.app_icon.add_css_class("icon-dropshadow")
                else:
                    self.app_icon.set_from_icon_name("application-x-executable-symbolic")
                    self.app_icon.set_icon_size(Gtk.IconSize.LARGE)
            GLib.idle_add(set_icon)

            def set_row(key, row):
                visible = key in info_dict
                if key == "version" and (not visible):
                    row.set_subtitle("No version information available")
                    return

                row.set_visible(visible)

                if visible:

                    row.set_subtitle(info_dict[key])

            for key, row in self.info_rows.items():
                GLib.idle_add(set_row, key, row)

        Gio.Task().run_in_thread(thread)
        self.data_row.set_visible(not self.package.is_runtime)
        self.pin_row.set_visible(self.package.is_runtime)
        self.open_app_button.set_visible(not self.package.is_runtime)
        self.uninstall_button.get_child().set_label("Uninstall" if self.package.is_runtime else "")

    def title_visible(self, a):
        self.properties_header.set_show_title(not a.get_value() == 0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.properties_scroll.get_vadjustment().connect("value-changed", self.title_visible)

        self.info_rows = {
            "version": self.version_row,
            "installed": self.installed_size_row,

            "id": self.id_row,
            "ref": self.ref_row,
            "arch": self.arch_row,
            "branch": self.branch_row,
            "license": self.license_row,

            "runtime": self.runtime_row,
            "sdk": self.sdk_row,
            "origin": self.origin_row,
            "collection": self.collection_row,
            "installation": self.installation_row,

            "commit": self.commit_row,
            "parent": self.parent_row,
            "subject": self.subject_row,
            "date": self.date_row,
        }