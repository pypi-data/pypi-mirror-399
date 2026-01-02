#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib
from Xlib import display, X

class MouseInfoGTK(Gtk.Window):
    def __init__(self):
        super().__init__(title="MouseInfo GTK")
        self.set_default_size(600, 450)
        
        self.x_disp = display.Display()
        self.x_root = self.x_disp.screen().root
        self.gdk_disp = Gdk.Display.get_default()

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_vbox.set_border_width(10)
        self.add(main_vbox)

        # Toolbar de Controle
        hbox_tools = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        main_vbox.pack_start(hbox_tools, False, False, 0)

        self.btn_toggle_color = Gtk.ToggleButton(label="Ocultar Cores")
        self.btn_toggle_color.connect("toggled", self.on_toggle_color_visibility)
        
        btn_clear = Gtk.Button(label="Limpar Logs")
        btn_clear.connect("clicked", self.on_clear_logs)

        hbox_tools.pack_start(self.btn_toggle_color, False, False, 0)
        hbox_tools.pack_start(btn_clear, False, False, 0)

        # Labels de tempo real
        grid = Gtk.Grid(column_spacing=15, row_spacing=10)
        main_vbox.pack_start(grid, False, False, 0)

        self.xy_val = Gtk.Label(label="0, 0", xalign=0)
        self.rgb_label_title = Gtk.Label(label="<b>RGB:</b>", use_markup=True, xalign=0)
        self.rgb_val = Gtk.Label(label="0, 0, 0", xalign=0)
        self.hex_label_title = Gtk.Label(label="<b>HEX:</b>", use_markup=True, xalign=0)
        self.hex_val = Gtk.Label(label="#000000", xalign=0)

        grid.attach(Gtk.Label(label="<b>Posição XY:</b>", use_markup=True, xalign=0), 0, 0, 1, 1)
        grid.attach(self.xy_val, 1, 0, 1, 1)
        grid.attach(self.rgb_label_title, 0, 1, 1, 1)
        grid.attach(self.rgb_val, 1, 1, 1, 1)
        grid.attach(self.hex_label_title, 0, 2, 1, 1)
        grid.attach(self.hex_val, 1, 2, 1, 1)

        # Área de Logs com Paned
        self.paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.paned.set_wide_handle(True)
        main_vbox.pack_start(self.paned, True, True, 0)

        # Log XY
        self.buffer_xy = Gtk.TextBuffer()
        view_xy = Gtk.TextView(buffer=self.buffer_xy, editable=False)
        self.box_xy = self.create_scrolled_window(view_xy, "Log Coordenadas (F6)")
        self.paned.pack1(self.box_xy, True, False)

        # Log Cores
        self.buffer_color = Gtk.TextBuffer()
        view_color = Gtk.TextView(buffer=self.buffer_color, editable=False)
        self.box_color = self.create_scrolled_window(view_color, "Log Cores (F6)")
        self.paned.pack2(self.box_color, True, False)

        self.connect("key-press-event", self.on_key_press)
        GLib.timeout_add(40, self.update_info)

    def create_scrolled_window(self, child, title):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        box.pack_start(Gtk.Label(label=title, xalign=0), False, False, 0)
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        sw.add(child)
        box.pack_start(sw, True, True, 0)
        return box

    def on_toggle_color_visibility(self, button):
        visible = not button.get_active()
        # Oculta labels
        self.rgb_label_title.set_visible(visible)
        self.rgb_val.set_visible(visible)
        self.hex_label_title.set_visible(visible)
        self.hex_val.set_visible(visible)
        # Oculta painel de log de cores
        self.box_color.set_visible(visible)
        button.set_label("Mostrar Cores" if not visible else "Ocultar Cores")

    def on_clear_logs(self, button):
        self.buffer_xy.set_text("")
        self.buffer_color.set_text("")

    def update_info(self):
        _, x, y = self.gdk_disp.get_default_seat().get_pointer().get_position()
        self.xy_val.set_text(f"{x}, {y}")

        if self.rgb_val.get_visible():
            try:
                img = self.x_root.get_image(x, y, 1, 1, X.ZPixmap, 0xffffffff)
                px = img.data
                r, g, b = px[2], px[1], px[0]
                self.rgb_val.set_text(f"{r}, {g}, {b}")
                self.hex_val.set_text(f"#{r:02X}{g:02X}{b:02X}")
            except:
                pass
        return True

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_F6:
            self.buffer_xy.insert(self.buffer_xy.get_end_iter(), f"{self.xy_val.get_text()}\n")
            if self.box_color.get_visible():
                color_str = f"{self.rgb_val.get_text()} | {self.hex_val.get_text()}\n"
                self.buffer_color.insert(self.buffer_color.get_end_iter(), color_str)
            return True
        return False

def run():
    win = MouseInfoGTK()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    
if __name__ == "__main__":
    run()
