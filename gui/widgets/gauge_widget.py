import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango
import cairo
import math

class GaugeWidget(Gtk.DrawingArea):
    def __init__(self, title="", unit="", min_val=0, max_val=100, critical_val=80):
        super().__init__()
        self.title = title
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
        self.critical_val = critical_val
        self.value = 0
        self.set_size_request(150, 150)
        self.connect('draw', self.on_draw)

    def set_value(self, value):
        self.value = max(self.min_val, min(self.max_val, value))
        self.queue_draw()

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        center_x = width / 2
        center_y = height / 2
        radius = min(center_x, center_y) * 0.8
        
        # Draw background arc
        start_angle = 0.75 * math.pi
        end_angle = 2.25 * math.pi
        
        cr.set_line_width(radius * 0.15)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_source_rgb(0.2, 0.2, 0.2)
        cr.arc(center_x, center_y, radius, start_angle, end_angle)
        cr.stroke()
        
        # Draw value arc
        percentage = (self.value - self.min_val) / (self.max_val - self.min_val)
        current_angle = start_angle + (end_angle - start_angle) * percentage
        
        # Color based on value
        if self.value >= self.critical_val:
            cr.set_source_rgb(0.9, 0.3, 0.3) # Red for critical
        else:
            cr.set_source_rgb(0.2, 0.6, 1.0) # Blue for normal
            
        cr.arc(center_x, center_y, radius, start_angle, current_angle)
        cr.stroke()
        
        # Draw text
        layout = widget.create_pango_layout(f"{int(self.value)}{self.unit}")
        desc = Pango.FontDescription("Sans Bold 20")
        layout.set_font_description(desc)
        ink_rect, logical_rect = layout.get_extents()
        cr.move_to(center_x - logical_rect.width / 2048, center_y - logical_rect.height / 2048)
        cr.set_source_rgb(1, 1, 1)
        Pango.cairo_show_layout(cr, layout)
        
        # Draw title
        layout_title = widget.create_pango_layout(self.title)
        desc_title = Pango.FontDescription("Sans 10")
        layout_title.set_font_description(desc_title)
        ink_rect, logical_rect = layout_title.get_extents()
        cr.move_to(center_x - logical_rect.width / 2048, center_y + radius * 0.5)
        cr.set_source_rgb(0.7, 0.7, 0.7)
        Pango.cairo_show_layout(cr, layout_title)
        
        return False
