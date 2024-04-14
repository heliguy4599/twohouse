from gi.repository import Adw, Gtk, GLib, Gio, Pango
import subprocess

class shared:
    icon_theme = Gtk.IconTheme.new()
    icon_theme.add_search_path("/var/lib/flatpak/exports/share/icons/")
    icon_theme.add_search_path("/home/heliguy/.local/share/flatpak/exports/share/icons")
    direction = Gtk.Image().get_direction()

class Flatpak:

    def mask(self, *args):
        subprocess.run(f'flatpak-spawn --host flatpak mask {self.info["ref"]}', shell=True)

    def unmask(self, *args):
        subprocess.run(f'flatpak-spawn --host flatpak mask --remove {self.info["ref"]}', shell=True)

    def get_installation(self, *args):
        installation = self.info["installation"]
        
        match installation:
            case "user":
                return "--user"
            case "system":
                return "--installation=default"

        return f'--installation={installation}'

    def get_properties(self, *args):
        properties = subprocess.run(
            f"flatpak-spawn --host flatpak info {self.get_installation()} {self.info['ref']}",
            text=True, shell=True, capture_output=True
        ).stdout.strip().split("\n")
        for i, line in enumerate(properties):
            properties[i] = line.strip().split(": ", 1)
        return properties

    def get_icon_path(self, refresh=False, *args):
        if refresh or self.icon_path == 0:
            try:
                self.icon_path = (
                    shared.icon_theme.lookup_icon(
                        self.info["id"], None, 512, 1, shared.direction, 0
                    )
                    .get_file()
                    .get_path()
                )
            except GLib.GError:
                icon_path = None
        return self.icon_path


    def __init__(self, info_array):
        self.info = {
            "name":           info_array[0],
            "description":    info_array[1],
            "id":             info_array[2],
            "version":        info_array[3],
            "branch":         info_array[4],
            "arch":           info_array[5],
            "origin":         info_array[6],
            "ref":            info_array[8],
            "installed_size": info_array[11],
            "options":        info_array[12],
        }
        installation = info_array[7]
        if len(info_array[7].split(' ')) > 1:
            self.info["installation"] = installation.split(' ')[1].replace("(", "").replace(")", "")
        else:
            self.info["installation"] = installation

        self.icon_path = 0

        self.is_runtime = "runtime" in info_array[12]