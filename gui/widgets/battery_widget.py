import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango
import cairo
import math

class BatteryWidget(Gtk.DrawingArea):
    def __init__(self):
        super().__init__()
        self.percentage = 0
        self.status = "Unknown" # Charging, Discharging, Full
        self.set_size_request(200, 200)
        self.connect('draw', self.on_draw)

    def set_data(self, percentage, status):
        self.percentage = max(0, min(100, percentage))
        self.status = status
        self.queue_draw()

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        center_x = width / 2
        center_y = height / 2
        radius = min(center_x, center_y) * 0.8
        
        # Draw background circle
        cr.set_line_width(radius * 0.1)
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
        cr.stroke()
        
        # Draw value arc
        start_angle = -0.5 * math.pi # Top
        end_angle = start_angle + (2 * math.pi * (self.percentage / 100.0))
        
        if self.percentage <= 20:
            cr.set_source_rgb(0.9, 0.3, 0.3) # Red
        elif self.status == "Charging":
            cr.set_source_rgb(0.3, 0.9, 0.3) # Green
        else:
            cr.set_source_rgb(0.2, 0.6, 1.0) # Blue
            
        cr.arc(center_x, center_y, radius, start_angle, end_angle)
        cr.stroke()
        
        # Draw text
        layout = widget.create_pango_layout(f"{int(self.percentage)}%")
        desc = Pango.FontDescription("Sans Bold 32")
        layout.set_font_description(desc)
        ink_rect, logical_rect = layout.get_extents()
        cr.move_to(center_x - logical_rect.width / 2048, center_y - logical_rect.height / 2048)
        cr.set_source_rgb(1, 1, 1)
        Pango.cairo_show_layout(cr, layout)
        
        # Draw status
        layout_status = widget.create_pango_layout(self.status)
        desc_status = Pango.FontDescription("Sans 12")
        layout_status.set_font_description(desc_status)
        ink_rect, logical_rect = layout_status.get_extents()
        cr.move_to(center_x - logical_rect.width / 2048, center_y + radius * 0.4)
        cr.set_source_rgb(0.8, 0.8, 0.8)
        Pango.cairo_show_layout(cr, layout_status)
        
        # Lightning bolt if charging
        if self.status == "Charging":
            cr.save()
            cr.translate(center_x, center_y - radius * 0.5)
            cr.scale(0.5, 0.5)
            # Simple bolt shape
            cr.move_to(0, -10)
            cr.line_to(5, 0)
            cr.line_to(2, 0)
            cr.line_to(4, 10)
            cr.line_to(-5, 0)
            cr.line_to(-2, 0)
            cr.close_path()
            cr.set_source_rgb(1, 1, 0)
            cr.fill()
            cr.restore()
            
        return False
