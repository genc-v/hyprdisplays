#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gdk
import json
import subprocess
import os
from pathlib import Path

class DisplayConfig:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.description = data.get('description', '')
        self.width = data.get('width')
        self.height = data.get('height')
        self.refresh_rate = data.get('refreshRate')
        self.x = data.get('x')
        self.y = data.get('y')
        self.scale = data.get('scale')
        self.transform = data.get('transform')
        self.disabled = data.get('disabled', False)
        self.available_modes = data.get('availableModes', [])
        self.focused = data.get('focused', False)  # Primary/focused monitor

class MonitorRow(Gtk.Box):
    def __init__(self, display, on_change, on_primary_change):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)
        
        self.display = display
        self.on_change = on_change
        self.on_primary_change = on_primary_change
        
        # Header with monitor name
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header = Gtk.Label()
        header.set_markup(f"<b>{display.name}</b> - {display.description}")
        header.set_xalign(0)
        header.set_hexpand(True)
        header_box.append(header)
        
        # Primary monitor toggle button
        self.primary_button = Gtk.ToggleButton(label="Primary")
        self.primary_button.set_active(display.focused)
        self.primary_button.connect('toggled', self.on_primary_toggled)
        header_box.append(self.primary_button)
        
        self.append(header_box)
        
        # Resolution and refresh rate
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        mode_box.append(Gtk.Label(label="Mode:"))
        
        self.mode_combo = Gtk.ComboBoxText()
        
        # Find and select the current mode
        current_index = -1
        for i, mode in enumerate(display.available_modes):
            self.mode_combo.append_text(mode)
            if '@' in mode and 'x' in mode:
                try:
                    parts = mode.replace('Hz', '').split('@')
                    res = parts[0]
                    refresh = float(parts[1])
                    expected_res = f"{display.width}x{display.height}"
                    # Match if resolution is same and refresh rate is very close (within 0.5Hz)
                    if res == expected_res and abs(refresh - display.refresh_rate) < 0.5:
                        current_index = i
                except:
                    pass
        
        # Set the active mode
        if current_index >= 0:
            self.mode_combo.set_active(current_index)
        elif len(display.available_modes) > 0:
            self.mode_combo.set_active(0)
        
        self.mode_combo.connect('changed', self.on_mode_changed)
        mode_box.append(self.mode_combo)
        self.append(mode_box)
        
        # Store position internally (not editable by user directly)
        self.x_spin = Gtk.SpinButton()
        self.x_spin.set_adjustment(Gtk.Adjustment(value=display.x, lower=-10000, upper=10000, step_increment=10))
        self.x_spin.set_digits(0)
        
        self.y_spin = Gtk.SpinButton()
        self.y_spin.set_adjustment(Gtk.Adjustment(value=display.y, lower=-10000, upper=10000, step_increment=10))
        self.y_spin.set_digits(0)
        
        # Scale control (visible to user)
        scale_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        scale_box.append(Gtk.Label(label="Scale:"))
        self.scale_spin = Gtk.SpinButton()
        self.scale_spin.set_adjustment(Gtk.Adjustment(value=display.scale, lower=0.5, upper=3.0, step_increment=0.1))
        self.scale_spin.set_digits(2)
        self.scale_spin.connect('value-changed', lambda _: self.on_change())
        scale_box.append(self.scale_spin)
        
        self.append(scale_box)
        
        # Transform
        transform_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        transform_box.append(Gtk.Label(label="Rotation:"))
        self.transform_combo = Gtk.ComboBoxText()
        transforms = ["0° (Normal)", "90°", "180°", "270°"]
        for t in transforms:
            self.transform_combo.append_text(t)
        self.transform_combo.set_active(display.transform if display.transform < 4 else 0)
        self.transform_combo.connect('changed', lambda _: self.on_change())
        transform_box.append(self.transform_combo)
        
        # Disabled toggle
        self.enabled_check = Gtk.CheckButton(label="Enabled")
        self.enabled_check.set_active(not display.disabled)
        self.enabled_check.connect('toggled', lambda _: self.on_change())
        transform_box.append(self.enabled_check)
        
        self.append(transform_box)
        
        # Separator
        self.append(Gtk.Separator())
    
    def on_primary_toggled(self, button):
        """Handle primary monitor toggle"""
        if button.get_active():
            self.on_primary_change(self)
        self.on_change()
    
    def set_primary(self, is_primary):
        """Set this monitor as primary or not"""
        self.display.focused = is_primary
        self.primary_button.set_active(is_primary)
    
    def on_mode_changed(self, combo):
        self.on_change()
    
    def get_config_line(self):
        """Generate Hyprland config line for this monitor"""
        mode_text = self.mode_combo.get_active_text()
        if not mode_text:
            mode_text = f"{self.display.width}x{self.display.height}@{self.display.refresh_rate:.2f}"
        
        # Parse mode
        parts = mode_text.replace("Hz", "").split("@")
        resolution = parts[0]
        refresh = parts[1] if len(parts) > 1 else str(self.display.refresh_rate)
        
        x = int(self.x_spin.get_value())
        y = int(self.y_spin.get_value())
        scale = self.scale_spin.get_value()
        transform = self.transform_combo.get_active()
        
        # Debug output
        print(f"get_config_line for {self.display.name}: position={x}x{y}, scale={scale}, enabled={self.enabled_check.get_active()}")
        
        if not self.enabled_check.get_active():
            return f"monitor={self.display.name},disabled"
        
        return f"monitor={self.display.name},{resolution}@{refresh},{x}x{y},{scale},transform,{transform}"

class DisplayCanvas(Gtk.DrawingArea):
    def __init__(self, get_monitors_func, on_position_changed):
        super().__init__()
        self.get_monitors = get_monitors_func
        self.on_position_changed = on_position_changed
        self.set_size_request(700, 500)
        self.set_vexpand(True)
        self.set_hexpand(True)
        self.set_draw_func(self.draw_monitors)
        
        # Mouse interaction - drag for moving monitors
        self.drag_controller = Gtk.GestureDrag()
        self.drag_controller.connect('drag-begin', self.on_drag_begin)
        self.drag_controller.connect('drag-update', self.on_drag_update)
        self.drag_controller.connect('drag-end', self.on_drag_end)
        self.add_controller(self.drag_controller)
        
        # Motion controller for hover effects
        self.motion_controller = Gtk.EventControllerMotion()
        self.motion_controller.connect('motion', self.on_motion)
        self.add_controller(self.motion_controller)
        
        # Scroll controller for zoom
        self.scroll_controller = Gtk.EventControllerScroll()
        self.scroll_controller.set_flags(Gtk.EventControllerScrollFlags.VERTICAL)
        self.scroll_controller.connect('scroll', self.on_scroll)
        self.add_controller(self.scroll_controller)
        
        # Zoom gesture for pinch-to-zoom on trackpad
        self.zoom_gesture = Gtk.GestureZoom()
        self.zoom_gesture.connect('scale-changed', self.on_pinch_zoom)
        self.add_controller(self.zoom_gesture)
        
        self.dragging_monitor = None
        self.hovered_monitor = None
        self.drag_start_monitor_x = 0
        self.drag_start_monitor_y = 0
        self.base_scale_factor = 0.15
        self.scale_factor = 0.15
        self.zoom_level = 1.0
        self.min_zoom = 0.3
        self.max_zoom = 3.0
        self.snap_distance = 20  # Pixels in real monitor coordinates
    
    def get_monitor_data(self):
        """Get current monitor positions and sizes from widgets"""
        monitors = self.get_monitors()
        if not monitors:
            return []
        
        monitor_data = []
        for row in monitors:
            current_x = int(row.x_spin.get_value())
            current_y = int(row.y_spin.get_value())
            current_scale = row.scale_spin.get_value()
            logical_width = row.display.width / current_scale
            logical_height = row.display.height / current_scale
            monitor_data.append({
                'row': row,
                'x': current_x,
                'y': current_y,
                'width': logical_width,
                'height': logical_height,
                'enabled': row.enabled_check.get_active(),
                'primary': row.display.focused  # Track primary monitor
            })
        return monitor_data
    
    def canvas_to_monitor_coords(self, canvas_x, canvas_y):
        """Convert canvas coordinates to monitor coordinates"""
        min_x = getattr(self, 'layout_min_x', 0)
        min_y = getattr(self, 'layout_min_y', 0)
        offset_x = getattr(self, 'layout_offset_x', 0)
        offset_y = getattr(self, 'layout_offset_y', 0)
        
        monitor_x = (canvas_x - offset_x) / self.scale_factor + min_x
        monitor_y = (canvas_y - offset_y) / self.scale_factor + min_y
        return monitor_x, monitor_y
    
    def monitor_to_canvas_coords(self, monitor_x, monitor_y):
        """Convert monitor coordinates to canvas coordinates"""
        min_x = getattr(self, 'layout_min_x', 0)
        min_y = getattr(self, 'layout_min_y', 0)
        offset_x = getattr(self, 'layout_offset_x', 0)
        offset_y = getattr(self, 'layout_offset_y', 0)
        
        canvas_x = (monitor_x - min_x) * self.scale_factor + offset_x
        canvas_y = (monitor_y - min_y) * self.scale_factor + offset_y
        return canvas_x, canvas_y
    
    def reset_view(self):
        """Reset zoom to default"""
        self.zoom_level = 1.0
        self.scale_factor = self.base_scale_factor * self.zoom_level
        self.queue_draw()
    
    def on_scroll(self, controller, dx, dy):
        """Handle scroll for zoom"""
        # Zoom in/out based on scroll direction
        zoom_step = 0.1
        if dy < 0:  # Scroll up - zoom in
            self.zoom_level = min(self.max_zoom, self.zoom_level + zoom_step)
        else:  # Scroll down - zoom out
            self.zoom_level = max(self.min_zoom, self.zoom_level - zoom_step)
        
        self.scale_factor = self.base_scale_factor * self.zoom_level
        self.queue_draw()
        return True
    
    def on_pinch_zoom(self, gesture, scale):
        """Handle pinch-to-zoom gesture on trackpad"""
        # Scale is relative to initial pinch, adjust zoom level accordingly
        new_zoom = self.zoom_level * scale
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))
        
        if abs(new_zoom - self.zoom_level) > 0.01:  # Threshold to avoid tiny changes
            self.zoom_level = new_zoom
            self.scale_factor = self.base_scale_factor * self.zoom_level
            self.queue_draw()
        
        return True
    
    def draw_monitors(self, area, cr, width, height):
        """Draw monitor layout on canvas"""
        monitor_data = self.get_monitor_data()
        if not monitor_data:
            return
        
        # Apply zoom to scale factor
        self.scale_factor = self.base_scale_factor * self.zoom_level
        
        # Find primary monitor to center on
        primary_monitor = None
        for m in monitor_data:
            if m.get('primary', False):
                primary_monitor = m
                break
        
        # If no primary, use first monitor
        if not primary_monitor and monitor_data:
            primary_monitor = monitor_data[0]
        
        # Center canvas on the primary monitor's center point
        if primary_monitor:
            primary_center_x = primary_monitor['x'] + primary_monitor['width'] / 2
            primary_center_y = primary_monitor['y'] + primary_monitor['height'] / 2
            self.layout_min_x = primary_center_x
            self.layout_min_y = primary_center_y
        else:
            self.layout_min_x = 0
            self.layout_min_y = 0
        
        self.layout_offset_x = width / 2
        self.layout_offset_y = height / 2
        
        # Draw background
        cr.set_source_rgb(0.12, 0.12, 0.12)
        cr.paint()
        
        # Draw grid lines
        cr.set_source_rgba(0.3, 0.3, 0.3, 0.3)
        cr.set_line_width(1)
        grid_spacing = 100 * self.scale_factor
        if grid_spacing > 20:
            # Vertical lines
            x_pos = self.layout_offset_x
            step = 0
            while x_pos < width:
                cr.move_to(x_pos, 0)
                cr.line_to(x_pos, height)
                cr.stroke()
                step += 1
                x_pos = self.layout_offset_x + step * grid_spacing
            
            step = 1
            x_pos = self.layout_offset_x - grid_spacing
            while x_pos > 0:
                cr.move_to(x_pos, 0)
                cr.line_to(x_pos, height)
                cr.stroke()
                step += 1
                x_pos = self.layout_offset_x - step * grid_spacing
            
            # Horizontal lines
            y_pos = self.layout_offset_y
            step = 0
            while y_pos < height:
                cr.move_to(0, y_pos)
                cr.line_to(width, y_pos)
                cr.stroke()
                step += 1
                y_pos = self.layout_offset_y + step * grid_spacing
            
            step = 1
            y_pos = self.layout_offset_y - grid_spacing
            while y_pos > 0:
                cr.move_to(0, y_pos)
                cr.line_to(width, y_pos)
                cr.stroke()
                step += 1
                y_pos = self.layout_offset_y - step * grid_spacing
        
        # Draw origin crosshair
        cr.set_source_rgba(0.5, 0.5, 0.5, 0.8)
        cr.set_line_width(2)
        # Vertical line at x=0
        cr.move_to(self.layout_offset_x, 0)
        cr.line_to(self.layout_offset_x, height)
        cr.stroke()
        # Horizontal line at y=0
        cr.move_to(0, self.layout_offset_y)
        cr.line_to(width, self.layout_offset_y)
        cr.stroke()
        
        # Draw origin label
        cr.set_source_rgb(0.7, 0.7, 0.7)
        cr.set_font_size(12)
        cr.move_to(self.layout_offset_x + 5, self.layout_offset_y - 5)
        cr.show_text("0x0")
        
        # Draw each monitor
        for i, m in enumerate(monitor_data, 1):
            x, y = self.monitor_to_canvas_coords(m['x'], m['y'])
            w = m['width'] * self.scale_factor
            h = m['height'] * self.scale_factor
            
            is_hovered = self.hovered_monitor == m['row']
            is_dragging = self.dragging_monitor == m['row']
            
            # Draw shadow
            if is_dragging or is_hovered:
                cr.set_source_rgba(0, 0, 0, 0.4)
                cr.rectangle(x + 4, y + 4, w, h)
                cr.fill()
            
            # Draw monitor background
            is_primary = m.get('primary', False)
            
            if is_dragging:
                cr.set_source_rgb(0.4, 0.65, 0.95)
            elif is_hovered:
                cr.set_source_rgb(0.35, 0.55, 0.85)
            elif is_primary:
                cr.set_source_rgb(0.35, 0.55, 0.35)  # Green tint for primary
            elif m['enabled']:
                cr.set_source_rgb(0.25, 0.45, 0.75)
            else:
                cr.set_source_rgb(0.4, 0.4, 0.4)
            
            cr.rectangle(x, y, w, h)
            cr.fill()
            
            # Draw border
            if is_dragging:
                cr.set_source_rgb(0.6, 0.85, 1.0)
                cr.set_line_width(3)
            elif is_hovered:
                cr.set_source_rgb(0.5, 0.75, 0.95)
                cr.set_line_width(2)
            elif is_primary:
                cr.set_source_rgb(0.2, 0.4, 0.2)  # Darker border for primary (non-draggable)
                cr.set_line_width(3)
            else:
                cr.set_source_rgb(0.1, 0.1, 0.1)
                cr.set_line_width(2)
            
            cr.rectangle(x, y, w, h)
            cr.stroke()
            
            # Draw display number badge
            badge_size = min(w, h) * 0.3
            badge_size = max(30, min(badge_size, 60))
            badge_x = x + w / 2
            badge_y = y + h / 2
            
            cr.set_source_rgba(0, 0, 0, 0.6)
            cr.arc(badge_x, badge_y, badge_size / 2, 0, 2 * 3.14159)
            cr.fill()
            
            cr.set_source_rgb(1, 1, 1)
            cr.select_font_face("Sans", 0, 1)
            cr.set_font_size(badge_size * 0.6)
            text = str(i)
            extents = cr.text_extents(text)
            cr.move_to(badge_x - extents.width / 2, badge_y + extents.height / 2)
            cr.show_text(text)
            
            # Draw monitor info at top
            cr.set_source_rgb(1, 1, 1)
            cr.set_font_size(12)
            cr.move_to(x + 8, y + 18)
            name_text = m['row'].display.name
            if m.get('primary', False):
                name_text += " ★"  # Star for primary monitor
            cr.show_text(name_text)
            
            # Draw resolution and scale at bottom
            cr.set_font_size(10)
            scale_val = m['row'].scale_spin.get_value()
            info_text = f"{int(m['width'])}x{int(m['height'])} @{scale_val:.1f}x"
            extents = cr.text_extents(info_text)
            cr.move_to(x + w - extents.width - 8, y + h - 8)
            cr.show_text(info_text)
            
            # Draw position at top right
            cr.set_font_size(9)
            pos_text = f"{m['x']}x{m['y']}"
            extents = cr.text_extents(pos_text)
            cr.move_to(x + w - extents.width - 8, y + 18)
            cr.show_text(pos_text)
    
    def get_monitor_at_position(self, canvas_x, canvas_y):
        """Find which monitor is at the given canvas position"""
        monitor_data = self.get_monitor_data()
        if not monitor_data:
            return None
        
        for m in monitor_data:
            mx, my = self.monitor_to_canvas_coords(m['x'], m['y'])
            mw = m['width'] * self.scale_factor
            mh = m['height'] * self.scale_factor
            
            if mx <= canvas_x <= mx + mw and my <= canvas_y <= my + mh:
                return m['row']
        return None
    
    def on_motion(self, controller, x, y):
        """Handle mouse motion for hover effects"""
        new_hovered = self.get_monitor_at_position(x, y)
        
        # Don't show hover effect on primary monitor (can't drag it)
        if new_hovered and new_hovered.display.focused:
            new_hovered = None
        
        if new_hovered != self.hovered_monitor:
            self.hovered_monitor = new_hovered
            self.queue_draw()
    
    def on_drag_begin(self, gesture, start_x, start_y):
        """Handle drag begin - grab the monitor"""
        monitor = self.get_monitor_at_position(start_x, start_y)
        if monitor:
            # Check if this is the primary monitor
            if monitor.display.focused:
                # Don't allow dragging the primary monitor
                return
            
            self.dragging_monitor = monitor
            self.drag_start_monitor_x = int(monitor.x_spin.get_value())
            self.drag_start_monitor_y = int(monitor.y_spin.get_value())
            self.queue_draw()
    
    def check_overlap(self, x, y, width, height, monitor, all_monitors):
        """Check if monitor at given position overlaps with any other monitor"""
        for other in all_monitors:
            if other['row'] == monitor:
                continue
            
            # Check for overlap
            if not (x + width <= other['x'] or 
                   x >= other['x'] + other['width'] or
                   y + height <= other['y'] or
                   y >= other['y'] + other['height']):
                return True
        return False
    
    def is_touching_any_monitor(self, x, y, width, height, monitor, all_monitors):
        """Check if monitor at given position is touching at least one other enabled monitor"""
        for other in all_monitors:
            if other['row'] == monitor or not other['enabled']:
                continue
            
            # Check if edges are touching (sharing an edge)
            # Horizontal touch (left/right edges)
            if (abs(x + width - other['x']) < 1 or abs(x - (other['x'] + other['width'])) < 1):
                # Check if there's vertical overlap for the edge to actually touch
                if not (y + height <= other['y'] or y >= other['y'] + other['height']):
                    return True
            
            # Vertical touch (top/bottom edges)
            if (abs(y + height - other['y']) < 1 or abs(y - (other['y'] + other['height'])) < 1):
                # Check if there's horizontal overlap for the edge to actually touch
                if not (x + width <= other['x'] or x >= other['x'] + other['width']):
                    return True
        
        return False
    
    def find_snap_position(self, monitor, x, y, width, height, all_monitors):
        """Find snap position for monitor - must be touching another monitor, no gaps allowed"""
        best_x, best_y = None, None
        min_distance = float('inf')
        alignment_threshold = 30  # Pixels to auto-align edges
        
        # Count enabled monitors (excluding the one being dragged)
        enabled_others = [m for m in all_monitors if m['row'] != monitor and m['enabled']]
        
        # If there are no other enabled monitors, snap to origin (0, 0)
        if len(enabled_others) == 0:
            return 0, 0
        
        for other in all_monitors:
            if other['row'] == monitor or not other['enabled']:
                continue
            
            # Calculate all edge snap positions (touching edges only)
            snap_configs = [
                # Right edge of other monitor (this monitor's left edge touches)
                {'x': other['x'] + other['width'], 'y': y, 'align_y': True},
                # Left edge of other monitor (this monitor's right edge touches)
                {'x': other['x'] - width, 'y': y, 'align_y': True},
                # Bottom edge of other monitor (this monitor's top edge touches)
                {'x': x, 'y': other['y'] + other['height'], 'align_x': True},
                # Top edge of other monitor (this monitor's bottom edge touches)
                {'x': x, 'y': other['y'] - height, 'align_x': True},
                # Corner snaps (diagonal corners touching)
                {'x': other['x'] + other['width'], 'y': other['y']},
                {'x': other['x'] - width, 'y': other['y']},
                {'x': other['x'] + other['width'], 'y': other['y'] + other['height'] - height},
                {'x': other['x'] - width, 'y': other['y'] + other['height'] - height},
                # Top right / bottom left corners
                {'x': other['x'], 'y': other['y'] + other['height']},
                {'x': other['x'], 'y': other['y'] - height},
                {'x': other['x'] + other['width'] - width, 'y': other['y'] + other['height']},
                {'x': other['x'] + other['width'] - width, 'y': other['y'] - height},
            ]
            
            for snap in snap_configs:
                snap_x, snap_y = snap['x'], snap['y']
                
                # Auto-align edges when stacking horizontally or vertically
                if snap.get('align_y'):
                    # Horizontal placement - align Y edges if close
                    if abs(y - other['y']) < alignment_threshold:
                        snap_y = other['y']  # Align top edges
                    elif abs(y + height - other['y'] - other['height']) < alignment_threshold:
                        snap_y = other['y'] + other['height'] - height  # Align bottom edges
                    elif abs(y + height/2 - other['y'] - other['height']/2) < alignment_threshold:
                        snap_y = other['y'] + other['height']/2 - height/2  # Center align
                
                if snap.get('align_x'):
                    # Vertical placement - align X edges if close
                    if abs(x - other['x']) < alignment_threshold:
                        snap_x = other['x']  # Align left edges
                    elif abs(x + width - other['x'] - other['width']) < alignment_threshold:
                        snap_x = other['x'] + other['width'] - width  # Align right edges
                    elif abs(x + width/2 - other['x'] - other['width']/2) < alignment_threshold:
                        snap_x = other['x'] + other['width']/2 - width/2  # Center align
                
                # Check if this position is valid (no overlap and touching at least one monitor)
                if not self.check_overlap(snap_x, snap_y, width, height, monitor, all_monitors):
                    if self.is_touching_any_monitor(snap_x, snap_y, width, height, monitor, all_monitors):
                        distance = ((x - snap_x) ** 2 + (y - snap_y) ** 2) ** 0.5
                        if distance < min_distance:
                            min_distance = distance
                            best_x, best_y = snap_x, snap_y
        
        # If no valid position found (shouldn't happen if monitors are already connected), 
        # return current position to prevent monitor from moving
        if best_x is None:
            return int(monitor.x_spin.get_value()), int(monitor.y_spin.get_value())
        
        return best_x, best_y
    
    def on_drag_update(self, gesture, offset_x, offset_y):
        """Handle drag update - move monitor with automatic snapping"""
        if not self.dragging_monitor:
            return
        
        # Calculate delta in canvas pixels
        delta_canvas_x = offset_x
        delta_canvas_y = offset_y
        
        # Convert delta to monitor coordinates
        delta_monitor_x = delta_canvas_x / self.scale_factor
        delta_monitor_y = delta_canvas_y / self.scale_factor
        
        # Apply delta to starting position
        new_x = self.drag_start_monitor_x + delta_monitor_x
        new_y = self.drag_start_monitor_y + delta_monitor_y
        
        # Get monitor data
        monitor_data = self.get_monitor_data()
        dragged_data = None
        for m in monitor_data:
            if m['row'] == self.dragging_monitor:
                dragged_data = m
                break
        
        if dragged_data:
            # Snap during drag to prevent gaps
            snapped_x, snapped_y = self.find_snap_position(
                self.dragging_monitor,
                new_x, new_y,
                dragged_data['width'], dragged_data['height'],
                monitor_data
            )
            
            # Update position with snapping
            self.dragging_monitor.x_spin.set_value(int(round(snapped_x)))
            self.dragging_monitor.y_spin.set_value(int(round(snapped_y)))
        
        self.queue_draw()
    
    def on_drag_end(self, gesture, offset_x, offset_y):
        """Handle drag end - finalize position"""
        if not self.dragging_monitor:
            return
        
        # Position is already snapped during drag, just finalize
        self.on_position_changed()
        self.dragging_monitor = None
        self.queue_draw()

class HyprDisplaysWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Hyprland Display Manager")
        self.set_default_size(900, 700)
        
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        
        # Header bar
        header = Adw.HeaderBar()
        main_box.append(header)
        
        # Refresh button
        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.connect('clicked', lambda _: self.load_displays())
        header.pack_start(refresh_btn)
        
        # Identify displays button
        identify_btn = Gtk.Button(label="Identify Displays")
        identify_btn.connect('clicked', lambda _: self.show_display_identifiers())
        header.pack_start(identify_btn)
        
        # Apply and Save button (combined)
        apply_btn = Gtk.Button(label="Apply & Save")
        apply_btn.add_css_class("suggested-action")
        apply_btn.connect('clicked', lambda _: self.save_to_config())
        header.pack_end(apply_btn)
        
        # Create paned view: canvas on left, settings on right
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_vexpand(True)
        paned.set_shrink_start_child(False)
        paned.set_shrink_end_child(False)
        paned.set_resize_start_child(True)
        paned.set_resize_end_child(False)
        main_box.append(paned)
        
        # Left side: Visual canvas
        canvas_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Canvas toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_margin_top(6)
        toolbar.set_margin_bottom(6)
        toolbar.set_margin_start(6)
        toolbar.set_margin_end(6)
        
        toolbar_label = Gtk.Label(label="Drag displays to reposition • Scroll to zoom")
        toolbar_label.set_hexpand(True)
        toolbar_label.set_xalign(0)
        toolbar.append(toolbar_label)
        
        # Zoom level label
        self.zoom_label = Gtk.Label(label="100%")
        toolbar.append(self.zoom_label)
        
        # Reset view button
        reset_btn = Gtk.Button(label="Reset View")
        reset_btn.connect('clicked', lambda _: self.reset_canvas_view())
        toolbar.append(reset_btn)
        
        canvas_box.append(toolbar)
        
        self.canvas = DisplayCanvas(
            lambda: self.monitor_rows,
            self.on_config_changed
        )
        canvas_box.append(self.canvas)
        paned.set_start_child(canvas_box)
        
        # Right side: Scrolled settings
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(False)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        paned.set_end_child(scrolled)
        
        # Content box for monitors
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        scrolled.set_child(self.content_box)
        
        # Status bar
        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_margin_top(6)
        self.status_label.set_margin_bottom(6)
        main_box.append(self.status_label)
        
        self.monitor_rows = []
        self.load_displays()
    
    def load_displays(self):
        """Load current display configuration from Hyprland"""
        try:
            result = subprocess.run(['hyprctl', 'monitors', '-j'], 
                                    capture_output=True, text=True, check=True)
            displays_data = json.loads(result.stdout)
            
            # Clear existing
            while self.content_box.get_first_child():
                self.content_box.remove(self.content_box.get_first_child())
            self.monitor_rows.clear()
            
            # Check if any monitor is marked as focused/primary
            has_primary = any(d.get('focused', False) for d in displays_data)
            
            # Add monitor rows
            for i, display_data in enumerate(displays_data):
                # If no primary is set, make the first one primary
                if not has_primary and i == 0:
                    display_data['focused'] = True
                
                display = DisplayConfig(display_data)
                row = MonitorRow(display, self.on_canvas_update, self.on_primary_changed)
                self.monitor_rows.append(row)
                self.content_box.append(row)
            
            self.canvas.queue_draw()
            self.status_label.set_text(f"Loaded {len(displays_data)} display(s)")
        except Exception as e:
            self.status_label.set_text(f"Error loading displays: {e}")
    
    def on_primary_changed(self, new_primary_row):
        """Handle when user selects a different primary monitor"""
        for row in self.monitor_rows:
            if row != new_primary_row:
                row.set_primary(False)
        new_primary_row.set_primary(True)
        self.canvas.queue_draw()
    
    def reset_canvas_view(self):
        """Reset canvas zoom and view"""
        self.canvas.reset_view()
        self.zoom_label.set_text("100%")
    
    def on_canvas_update(self):
        self.canvas.queue_draw()
        # Update zoom label
        zoom_percent = int(self.canvas.zoom_level * 100)
        self.zoom_label.set_text(f"{zoom_percent}%")
        self.on_config_changed()
    
    def on_config_changed(self):
        self.status_label.set_text("Configuration changed (not applied)")
    
    def apply_config(self):
        """Apply configuration immediately via hyprctl"""
        try:
            for row in self.monitor_rows:
                config_line = row.get_config_line()
                # Extract the monitor config part
                cmd = config_line.replace("monitor=", "")
                subprocess.run(['hyprctl', 'keyword', 'monitor', cmd], check=True)
            
            self.status_label.set_text("Configuration applied successfully!")
            GLib.timeout_add_seconds(2, lambda: self.load_displays())
        except Exception as e:
            self.status_label.set_text(f"Error applying config: {e}")
    
    def show_revert_dialog(self, countdown=15):
        """Show a dialog asking if the user wants to keep the changes"""
        dialog = Adw.MessageDialog.new(self)
        dialog.set_heading("Keep display configuration?")
        dialog.set_body(f"Reverting in {countdown} seconds...")
        dialog.add_response("revert", "Revert")
        dialog.add_response("keep", "Keep Changes")
        dialog.set_response_appearance("keep", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("keep")
        dialog.set_close_response("revert")
        
        # Store the countdown state
        dialog.countdown = countdown
        dialog.reverted = False
        
        def update_countdown():
            if dialog.countdown > 0 and not dialog.reverted:
                dialog.countdown -= 1
                dialog.set_body(f"Reverting in {dialog.countdown} seconds...")
                return True  # Continue timeout
            elif dialog.countdown <= 0 and not dialog.reverted:
                # Time's up, revert
                dialog.reverted = True
                dialog.close()
                self.revert_config()
                return False
            return False
        
        def on_response(dialog, response):
            print(f"Dialog response: {response}")
            dialog.reverted = True  # Stop countdown
            if response == "revert":
                print("User chose to revert")
                self.revert_config()
            else:
                print("User chose to keep changes")
                self.save_config_permanently()
        
        dialog.connect("response", on_response)
        GLib.timeout_add_seconds(1, update_countdown)
        dialog.present()
    
    def save_config_permanently(self):
        """Save configuration to Hyprland config file"""
        hypr_dir = Path.home() / ".config" / "hypr"
        config_path = hypr_dir / "hyprland.conf"
        monitors_conf_path = hypr_dir / "monitors.conf"
        
        try:
            # Generate monitor lines first
            monitor_lines = []
            for row in self.monitor_rows:
                config_line = row.get_config_line()
                monitor_lines.append(config_line + '\n')
                # Debug: print what we're saving
                print(f"Saving: {config_line}")
            
            # Strategy: Save to monitors.conf which is typically sourced last
            # This ensures our settings override any earlier monitor configs
            # Also add header to indicate this file is managed by HyprDisplays
            monitors_content = [
                "# Monitor configuration - Generated by HyprDisplays\n",
                "# This file is automatically managed by HyprDisplays.\n",
                "# Manual changes may be overwritten.\n",
                "\n"
            ] + monitor_lines
            
            # Write to monitors.conf
            with open(monitors_conf_path, 'w') as f:
                f.writelines(monitors_content)
            
            print(f"Config saved to {monitors_conf_path}")
            
            # Also clean up monitor lines from main config and sourced files
            # to avoid conflicts
            files_to_clean = [
                config_path,
                hypr_dir / "hyprland" / "general.conf",
                hypr_dir / "custom" / "general.conf"
            ]
            
            for file_path in files_to_clean:
                if not file_path.exists():
                    continue
                
                try:
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                    
                    # Remove monitor lines and HyprDisplays headers, but keep commented lines
                    # Also keep the "source=monitors.conf" line if present
                    new_lines = []
                    for line in lines:
                        stripped = line.strip()
                        # Keep the line if:
                        # - It's not a monitor= line (or is commented)
                        # - It's not an old HyprDisplays header
                        # - It's a source=monitors.conf line (we need this!)
                        if (not stripped.startswith('monitor=') or stripped.startswith('#')) and \
                           '# Monitor configuration - Generated by HyprDisplays' not in line and \
                           'This file is automatically managed by HyprDisplays' not in line:
                            new_lines.append(line)
                        elif 'source=monitors.conf' in line or 'source = monitors.conf' in line:
                            # Keep the source line
                            new_lines.append(line)
                    
                    # Write back
                    with open(file_path, 'w') as f:
                        f.writelines(new_lines)
                    
                    print(f"Cleaned monitor lines from {file_path}")
                except Exception as e:
                    print(f"Warning: Could not clean {file_path}: {e}")
            
            # Ensure main config sources monitors.conf
            # Check if it already has the source line
            if config_path.exists():
                with open(config_path, 'r') as f:
                    content = f.read()
                
                if 'source=monitors.conf' not in content and 'source = monitors.conf' not in content:
                    # Add source line
                    with open(config_path, 'a') as f:
                        f.write('\n# Monitor configuration\nsource=monitors.conf\n')
                    print("Added source=monitors.conf to hyprland.conf")
            
            # Re-apply the configuration to ensure it takes effect
            # This ensures the saved config matches what's currently displayed
            for row in self.monitor_rows:
                config_line = row.get_config_line()
                cmd = config_line.replace("monitor=", "")
                result = subprocess.run(['hyprctl', 'keyword', 'monitor', cmd], 
                                      capture_output=True, text=True, check=False)
                if result.returncode != 0:
                    print(f"Warning: Failed to apply monitor config: {result.stderr}")
            
            self.status_label.set_text(f"Configuration saved to monitors.conf and applied!")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_label.set_text(f"Error saving config: {e}")
    
    def revert_config(self):
        """Revert to previous configuration"""
        print("=== REVERTING CONFIGURATION ===")
        try:
            for row in self.monitor_rows:
                if not hasattr(row.display, 'old_config_line'):
                    print(f"ERROR: No old_config_line for {row.display.name}")
                    self.status_label.set_text("Error: Cannot revert - no saved configuration")
                    return
                
                config_line = row.display.old_config_line
                cmd = config_line.replace("monitor=", "")
                print(f"Reverting {row.display.name}: {cmd}")
                result = subprocess.run(['hyprctl', 'keyword', 'monitor', cmd], 
                                      capture_output=True, text=True, check=False)
                if result.returncode != 0:
                    print(f"ERROR reverting {row.display.name}: {result.stderr}")
                else:
                    print(f"✓ Reverted {row.display.name}")
            
            self.status_label.set_text("Configuration reverted")
            print("Reloading displays...")
            GLib.timeout_add_seconds(1, lambda: self.load_displays())
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_label.set_text(f"Error reverting config: {e}")
    
    def save_to_config(self):
        """Apply configuration and ask user to confirm or revert"""
        try:
            # Save current config for potential revert
            print("=== SAVING OLD CONFIG FOR REVERT ===")
            for row in self.monitor_rows:
                old_line = f"monitor={row.display.name},{row.display.width}x{row.display.height}@{row.display.refresh_rate:.2f},{row.display.x}x{row.display.y},{row.display.scale},transform,{row.display.transform}"
                row.display.old_config_line = old_line
                print(f"Old config for {row.display.name}: {old_line}")
            
            # Apply new config
            print("=== APPLYING NEW CONFIG ===")
            for row in self.monitor_rows:
                config_line = row.get_config_line()
                cmd = config_line.replace("monitor=", "")
                print(f"Applying: {cmd}")
                result = subprocess.run(['hyprctl', 'keyword', 'monitor', cmd], 
                                      capture_output=True, text=True, check=False)
                if result.returncode != 0:
                    print(f"ERROR: {result.stderr}")
                    raise Exception(f"Failed to apply config: {result.stderr}")
            
            self.status_label.set_text("Configuration applied - Confirm to keep changes")
            
            # Show revert dialog
            self.show_revert_dialog()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status_label.set_text(f"Error applying config: {e}")
    
    def show_display_identifiers(self):
        """Show overlay on each display with its name/number"""
        try:
            # Set up window rules for overlay windows to be floating
            # Use a unique title pattern for identification
            subprocess.run([
                'hyprctl', 'keyword', 'windowrulev2',
                'float,title:^(Display [0-9]+ - ).*'
            ], capture_output=True, check=False)
            
            for i, row in enumerate(self.monitor_rows, 1):
                monitor_name = row.display.name
                description = row.display.description.replace('"', '\\"')
                
                # Try to show overlay on specific monitor using Hyprland's monitor assignment
                # Use a simple Python GTK overlay window positioned on each monitor
                self.create_overlay_window(i, monitor_name, description, row.display)
            
            self.status_label.set_text("Display identifiers shown on all screens")
        except Exception as e:
            self.status_label.set_text(f"Error showing identifiers: {e}")
    
    def create_overlay_window(self, display_num, monitor_name, description, display):
        """Create a GTK overlay window on a specific monitor"""
        # Create overlay window
        overlay = Gtk.Window()
        overlay.set_title(f"Display {display_num} - {monitor_name}")  # Unique title for window rules
        overlay.set_decorated(False)
        overlay.set_default_size(400, 200)
        overlay.set_modal(False)
        
        # Create content
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)
        
        # Add semi-transparent background
        overlay.add_css_class('overlay-identifier')
        
        # Display number (large)
        number_label = Gtk.Label()
        number_label.set_markup(f"<span size='xx-large' weight='bold'>Display {display_num}</span>")
        box.append(number_label)
        
        # Monitor name
        name_label = Gtk.Label()
        name_label.set_markup(f"<b>{monitor_name}</b>")
        box.append(name_label)
        
        # Description
        desc_label = Gtk.Label(label=description)
        desc_label.set_wrap(True)
        desc_label.set_max_width_chars(40)
        box.append(desc_label)
        
        overlay.set_child(box)
        
        # Add CSS for styling
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        .overlay-identifier {
            background-color: rgba(0, 0, 0, 0.85);
            color: white;
            border-radius: 12px;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        """)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        overlay.present()
        
        # Position after window is realized
        def position_overlay():
            try:
                # Give the window a moment to appear
                import time
                time.sleep(0.05)
                
                # Get the actual window size (might differ from default)
                width = overlay.get_width()
                height = overlay.get_height()
                if width == 0:
                    width = 400
                if height == 0:
                    height = 200
                
                # Calculate center position ensuring it's within monitor bounds
                scale = display.scale if hasattr(display, 'scale') else 1.0
                monitor_width = display.width / scale
                monitor_height = display.height / scale
                
                # Center with some padding from edges
                x = display.x + max(10, (monitor_width - width) // 2)
                y = display.y + max(10, (monitor_height - height) // 2)
                
                # Ensure window stays within monitor bounds
                x = max(display.x, min(x, display.x + monitor_width - width - 10))
                y = max(display.y, min(y, display.y + monitor_height - height - 10))
                
                # Use hyprctl to position the window
                result = subprocess.run(['hyprctl', 'clients', '-j'], 
                                      capture_output=True, text=True, check=True)
                clients = json.loads(result.stdout)
                
                # Find our overlay window by title pattern
                for client in reversed(clients):
                    title = client.get('title', '')
                    if f'Display {display_num} - ' in title:
                        window_address = client.get('address', '')
                        if window_address and window_address.startswith('0x'):
                            # Position it (should already be floating due to window rule)
                            subprocess.run(['hyprctl', 'dispatch', 'movewindowpixel', 
                                          f'exact {int(x)} {int(y)},address:{window_address}'], 
                                         capture_output=True, check=False)
                            break
            except Exception as e:
                print(f"Error positioning overlay: {e}")
            return False
        
        # Position after a short delay
        GLib.timeout_add(150, position_overlay)
        
        # Auto-close after 3 seconds
        GLib.timeout_add_seconds(3, lambda: overlay.close())

class HyprDisplaysApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.github.hyprdisplays')
        
    def do_activate(self):
        win = HyprDisplaysWindow(self)
        win.present()

if __name__ == '__main__':
    app = HyprDisplaysApp()
    app.run(None)
