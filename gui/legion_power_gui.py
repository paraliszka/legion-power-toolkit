#!/usr/bin/env python3
import sys
import os
import signal
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Gio, GObject

# Add current directory to path so we can import widgets
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from widgets.battery_widget import BatteryWidget
from widgets.gauge_widget import GaugeWidget
from widgets.toggle_widget import ToggleWidget

APP_ID = "com.legion.power.gui"
VERSION = "1.0.0"

class LegionPowerGUI(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Legion Power Manager")
        self.set_default_size(800, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # Set icon if available
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.svg")
        if os.path.exists(icon_path):
            self.set_icon_from_file(icon_path)

        # DBus Proxies
        self.legion_proxy = None
        self.upower_proxy = None
        
        self.setup_dbus()
        self.setup_ui()
        
        # Start polling
        self.poll_timer = GLib.timeout_add_seconds(2, self.update_data)
        self.update_data() # Initial update

    def setup_dbus(self):
        try:
            self.bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
            
            # Legion Power Service
            self.legion_proxy = Gio.DBusProxy.new_sync(
                self.bus,
                Gio.DBusProxyFlags.NONE,
                None,
                "com.legion.Power.Manager",
                "/com/legion/Power/Manager",
                "com.legion.Power.Manager",
                None
            )
            
            # UPower for Battery
            self.upower_proxy = Gio.DBusProxy.new_sync(
                self.bus,
                Gio.DBusProxyFlags.NONE,
                None,
                "org.freedesktop.UPower",
                "/org/freedesktop/UPower/devices/battery_BAT0",
                "org.freedesktop.UPower.Device",
                None
            )
            
        except Exception as e:
            print(f"Error connecting to DBus: {e}")
            # Show error dialog
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="DBus Connection Error"
            )
            dialog.format_secondary_text(f"Could not connect to services: {e}")
            dialog.run()
            dialog.destroy()

    def setup_ui(self):
        # Header Bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("Legion Power Manager")
        self.set_titlebar(header)
        
        # Refresh Button
        refresh_btn = Gtk.Button.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        refresh_btn.connect("clicked", lambda x: self.update_data())
        header.pack_start(refresh_btn)

        # Main Layout
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)
        
        self.setup_battery_tab()
        self.setup_performance_tab()
        self.setup_settings_tab()
        self.setup_about_tab()

    def setup_battery_tab(self):
        grid = Gtk.Grid()
        grid.set_column_spacing(20)
        grid.set_row_spacing(20)
        grid.set_margin_top(20)
        grid.set_margin_bottom(20)
        grid.set_margin_start(20)
        grid.set_margin_end(20)
        
        # Left side: Battery Info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        self.battery_widget = BatteryWidget()
        info_box.pack_start(self.battery_widget, False, False, 0)
        
        # Info labels
        self.lbl_percentage = Gtk.Label(label="Unknown %")
        self.lbl_state = Gtk.Label(label="State: Unknown")
        self.lbl_health = Gtk.Label(label="Health: Unknown")
        self.lbl_time = Gtk.Label(label="Time Remaining: Unknown")
        
        for lbl in [self.lbl_percentage, self.lbl_state, self.lbl_health, self.lbl_time]:
            lbl.set_halign(Gtk.Align.START)
            info_box.pack_start(lbl, False, False, 0)
            
        grid.attach(info_box, 0, 0, 1, 2)
        
        # Right side: Controls
        ctrl_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        
        # Conservation Mode
        cons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        cons_label = Gtk.Label(label="Conservation Mode (60% Limit)")
        cons_label.set_hexpand(True)
        cons_label.set_halign(Gtk.Align.START)
        
        self.cons_toggle = ToggleWidget()
        self.cons_toggle.connect("toggled", self.on_conservation_toggled)
        
        cons_box.pack_start(cons_label, True, True, 0)
        cons_box.pack_start(self.cons_toggle, False, False, 0)
        ctrl_box.pack_start(cons_box, False, False, 0)
        
        # Rapid Charge
        rapid_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        rapid_label = Gtk.Label(label="Rapid Charge")
        rapid_label.set_hexpand(True)
        rapid_label.set_halign(Gtk.Align.START)
        
        self.rapid_toggle = ToggleWidget()
        self.rapid_toggle.connect("toggled", self.on_rapid_toggled)
        
        rapid_box.pack_start(rapid_label, True, True, 0)
        rapid_box.pack_start(self.rapid_toggle, False, False, 0)
        ctrl_box.pack_start(rapid_box, False, False, 0)

        # Placeholder for Chart
        chart_frame = Gtk.Frame(label="Battery History (24h)")
        chart_area = Gtk.DrawingArea()
        chart_area.set_size_request(400, 200)
        chart_area.connect("draw", self.draw_mock_chart)
        chart_frame.add(chart_area)
        
        ctrl_box.pack_start(chart_frame, True, True, 0)
        
        grid.attach(ctrl_box, 1, 0, 1, 2)
        
        self.notebook.append_page(grid, Gtk.Label(label="Battery"))

    def setup_performance_tab(self):
        grid = Gtk.Grid()
        grid.set_column_spacing(20)
        grid.set_row_spacing(20)
        grid.set_margin_top(20)
        grid.set_margin_bottom(20)
        grid.set_margin_start(20)
        grid.set_margin_end(20)
        
        # Gauges
        gauge_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        
        self.cpu_gauge = GaugeWidget(title="CPU Temp", unit="°C", max_val=100, critical_val=90)
        self.gpu_gauge = GaugeWidget(title="GPU Temp", unit="°C", max_val=100, critical_val=85)
        self.fan_gauge = GaugeWidget(title="Fan Speed", unit=" RPM", max_val=5000, critical_val=4500)
        
        gauge_box.pack_start(self.cpu_gauge, True, True, 0)
        gauge_box.pack_start(self.gpu_gauge, True, True, 0)
        gauge_box.pack_start(self.fan_gauge, True, True, 0)
        
        grid.attach(gauge_box, 0, 0, 2, 1)
        
        # Power Profile
        profile_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        profile_label = Gtk.Label(label="Power Profile")
        profile_label.set_halign(Gtk.Align.START)
        
        self.profile_combo = Gtk.ComboBoxText()
        self.profile_combo.append("quiet", "Quiet (Blue)")
        self.profile_combo.append("balanced", "Balanced (White)")
        self.profile_combo.append("performance", "Performance (Red)")
        self.profile_combo.set_active(1)
        self.profile_combo.connect("changed", self.on_profile_changed)
        
        profile_box.pack_start(profile_label, False, False, 0)
        profile_box.pack_start(self.profile_combo, False, False, 0)
        
        grid.attach(profile_box, 0, 1, 1, 1)
        
        # Fan Mode
        fan_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        fan_label = Gtk.Label(label="Fan Mode")
        fan_label.set_halign(Gtk.Align.START)
        
        self.fan_mode_combo = Gtk.ComboBoxText()
        self.fan_mode_combo.append("auto", "Auto")
        self.fan_mode_combo.append("max", "Max Speed")
        self.fan_mode_combo.set_active(0)
        # self.fan_mode_combo.connect("changed", self.on_fan_mode_changed) # Not implemented in mock
        
        fan_box.pack_start(fan_label, False, False, 0)
        fan_box.pack_start(self.fan_mode_combo, False, False, 0)
        
        grid.attach(fan_box, 1, 1, 1, 1)
        
        self.notebook.append_page(grid, Gtk.Label(label="Performance"))

    def setup_settings_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        # Auto-switching
        auto_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        auto_label = Gtk.Label(label="Auto-switch power profile on AC/Battery")
        auto_label.set_hexpand(True)
        auto_label.set_halign(Gtk.Align.START)
        
        self.auto_toggle = Gtk.Switch()
        self.auto_toggle.set_active(True)
        
        auto_box.pack_start(auto_label, True, True, 0)
        auto_box.pack_start(self.auto_toggle, False, False, 0)
        box.pack_start(auto_box, False, False, 0)
        
        # Notifications
        notif_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        notif_label = Gtk.Label(label="Show desktop notifications")
        notif_label.set_hexpand(True)
        notif_label.set_halign(Gtk.Align.START)
        
        self.notif_toggle = Gtk.Switch()
        self.notif_toggle.set_active(True)
        
        notif_box.pack_start(notif_label, True, True, 0)
        notif_box.pack_start(self.notif_toggle, False, False, 0)
        box.pack_start(notif_box, False, False, 0)
        
        # Buttons
        btn_box = Gtk.ButtonBox(orientation=Gtk.Orientation.HORIZONTAL)
        btn_box.set_layout(Gtk.ButtonBoxStyle.END)
        btn_box.set_spacing(10)
        
        restore_btn = Gtk.Button(label="Restore Defaults")
        save_btn = Gtk.Button(label="Save Settings")
        save_btn.get_style_context().add_class("suggested-action")
        
        btn_box.pack_start(restore_btn, False, False, 0)
        btn_box.pack_start(save_btn, False, False, 0)
        
        box.pack_end(btn_box, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label(label="Settings"))

    def setup_about_tab(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_valign(Gtk.Align.CENTER)
        
        # Icon
        icon = Gtk.Image.new_from_icon_name("battery", Gtk.IconSize.DIALOG)
        # Try to load our logo
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.svg")
        if os.path.exists(logo_path):
            pixbuf = Gdk.Pixbuf.new_from_file_at_scale(logo_path, 128, 128, True)
            icon = Gtk.Image.new_from_pixbuf(pixbuf)
            
        box.pack_start(icon, False, False, 0)
        
        # Title
        title_label = Gtk.Label()
        title_label.set_markup(f"<span size='xx-large' weight='bold'>Legion Power Manager</span>")
        box.pack_start(title_label, False, False, 0)
        
        # Version
        ver_label = Gtk.Label(label=f"Version {VERSION}")
        box.pack_start(ver_label, False, False, 0)
        
        # Desc
        desc_label = Gtk.Label(label="A power management tool for Lenovo Legion laptops on Linux.\nControl conservation mode, power profiles, and more.")
        desc_label.set_justify(Gtk.Justification.CENTER)
        box.pack_start(desc_label, False, False, 0)
        
        # Copyright
        copy_label = Gtk.Label(label="© 2025 Open Source Community")
        box.pack_start(copy_label, False, False, 0)
        
        self.notebook.append_page(box, Gtk.Label(label="About"))

    def draw_mock_chart(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        
        # Background
        cr.set_source_rgb(0.95, 0.95, 0.95)
        cr.rectangle(0, 0, width, height)
        cr.fill()
        
        # Grid lines
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.set_line_width(1)
        for i in range(5):
            y = height * (i / 4.0)
            cr.move_to(0, y)
            cr.line_to(width, y)
        cr.stroke()
        
        # Mock data line
        cr.set_source_rgb(0.2, 0.6, 1.0)
        cr.set_line_width(3)
        cr.move_to(0, height * 0.5)
        
        import random
        random.seed(42) # Static mock
        
        points = []
        for i in range(21):
            x = width * (i / 20.0)
            y = height * (0.3 + random.random() * 0.4)
            points.append((x, y))
            cr.line_to(x, y)
            
        cr.stroke()
        
        # Fill under
        cr.move_to(0, height)
        cr.line_to(0, height * 0.5)
        for x, y in points:
            cr.line_to(x, y)
        cr.line_to(width, height)
        cr.close_path()
        cr.set_source_rgba(0.2, 0.6, 1.0, 0.2)
        cr.fill()

    def update_data(self):
        # Update Battery Info from UPower
        if self.upower_proxy:
            try:
                percentage = self.upower_proxy.get_cached_property("Percentage").get_double()
                state = self.upower_proxy.get_cached_property("State").get_uint32()
                # State: 1=Charging, 2=Discharging, 4=Fully Charged
                
                status_str = "Unknown"
                if state == 1: status_str = "Charging"
                elif state == 2: status_str = "Discharging"
                elif state == 4: status_str = "Full"
                
                self.battery_widget.set_data(percentage, status_str)
                self.lbl_percentage.set_text(f"{int(percentage)}%")
                self.lbl_state.set_text(f"State: {status_str}")
                
            except Exception as e:
                # print(f"UPower Error: {e}")
                pass

        # Update Legion Features
        if self.legion_proxy:
            try:
                # Need to check available properties on the interface
                # This assumes the properties exist
                pass
                # Example:
                # mode = self.legion_proxy.get_cached_property("ConservationMode").get_boolean()
                # self.cons_toggle.set_active(mode)
            except:
                pass

        # Mock Data for gauges (since we don't have real hardware sensors connected yet)
        import random
        self.cpu_gauge.set_value(45 + random.randint(-2, 5))
        self.gpu_gauge.set_value(40 + random.randint(-1, 3))
        self.fan_gauge.set_value(2200 + random.randint(-100, 100))
        
        return True # Keep polling

    def on_conservation_toggled(self, widget, active):
        if self.legion_proxy:
            print(f"Set Conservation Mode: {active}")
            # self.legion_proxy.SetConservationMode('(b)', active)
            # Use DBus call

    def on_rapid_toggled(self, widget, active):
        if self.legion_proxy:
            print(f"Set Rapid Charge: {active}")

    def on_profile_changed(self, combo):
        if self.legion_proxy:
            active_id = combo.get_active_id()
            print(f"Set Power Profile: {active_id}")

class Application(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)
        
    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = LegionPowerGUI(self)
        win.present()

if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)
