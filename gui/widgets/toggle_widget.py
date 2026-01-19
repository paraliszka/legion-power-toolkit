#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, Pango
import cairo
import math

class ToggleWidget(Gtk.DrawingArea):
    """Custom animated toggle switch widget"""
    
    __gsignals__ = {
        'toggled': (GObject.SignalFlags.RUN_FIRST, None, (bool,))
    }
    
    def __init__(self):
        super().__init__()
        
        # State
        self._active = False
        self._animation_progress = 0.0
        self._animation_target = 0.0
        self._animation_timer = None
        
        # Dimensions
        self.width = 60
        self.height = 30
        
        # Set minimum size
        self.set_size_request(self.width, self.height)
        
        # Enable events
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | 
                       Gdk.EventMask.BUTTON_RELEASE_MASK)
        
        # Connect signals
        self.connect('draw', self.on_draw)
        self.connect('button-press-event', self.on_button_press)
        
    def set_active(self, active):
        """Set toggle state"""
        if self._active != active:
            self._active = active
            self._animation_target = 1.0 if active else 0.0
            self._start_animation()
            
    def get_active(self):
        """Get toggle state"""
        return self._active
    
    def _start_animation(self):
        """Start animation"""
        if self._animation_timer is None:
            self._animation_timer = GObject.timeout_add(16, self._animate)
    
    def _animate(self):
        """Animation step"""
        step = 0.1
        
        if abs(self._animation_progress - self._animation_target) < 0.01:
            self._animation_progress = self._animation_target
            self._animation_timer = None
            self.queue_draw()
            return False
        
        if self._animation_progress < self._animation_target:
            self._animation_progress = min(1.0, self._animation_progress + step)
        else:
            self._animation_progress = max(0.0, self._animation_progress - step)
        
        self.queue_draw()
        return True
    
    def on_draw(self, widget, cr):
        """Draw the toggle switch"""
        # Get dimensions
        width = self.get_allocated_width()
        height = self.get_allocated_height()
        
        # Calculate positions
        track_height = height * 0.6
        track_y = (height - track_height) / 2
        knob_size = track_height * 1.2
        knob_y = (height - knob_size) / 2
        
        # Calculate knob position based on animation
        knob_travel = width - knob_size - 4
        knob_x = 2 + (knob_travel * self._animation_progress)
        
        # Colors
        if self._active:
            track_color = (0.3, 0.6, 1.0)  # Blue when active
        else:
            track_color = (0.5, 0.5, 0.5)  # Gray when inactive
        
        # Draw track
        cr.set_source_rgb(*track_color)
        cr.arc(track_height/2, height/2, track_height/2, math.pi/2, 3*math.pi/2)
        cr.arc(width - track_height/2, height/2, track_height/2, -math.pi/2, math.pi/2)
        cr.fill()
        
        # Draw knob
        cr.set_source_rgb(1.0, 1.0, 1.0)  # White knob
        cr.arc(knob_x + knob_size/2, knob_y + knob_size/2, knob_size/2, 0, 2*math.pi)
        cr.fill()
        
        # Draw knob shadow
        cr.set_source_rgba(0, 0, 0, 0.2)
        cr.arc(knob_x + knob_size/2 + 1, knob_y + knob_size/2 + 1, knob_size/2, 0, 2*math.pi)
        cr.fill()
        
        return False
    
    def on_button_press(self, widget, event):
        """Handle button press"""
        self._active = not self._active
        self._animation_target = 1.0 if self._active else 0.0
        self._start_animation()
        self.emit('toggled', self._active)
        return True

# Test if run directly
if __name__ == '__main__':
    win = Gtk.Window(title="Toggle Test")
    win.connect("destroy", Gtk.main_quit)
    
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    box.set_margin_top(20)
    box.set_margin_bottom(20)
    box.set_margin_start(20)
    box.set_margin_end(20)
    
    toggle = ToggleWidget()
    
    def on_toggled(widget, active):
        print(f"Toggle: {active}")
    
    toggle.connect('toggled', on_toggled)
    
    label = Gtk.Label(label="Toggle Switch:")
    box.pack_start(label, False, False, 0)
    box.pack_start(toggle, False, False, 0)
    
    win.add(box)
    win.show_all()
    Gtk.main()
