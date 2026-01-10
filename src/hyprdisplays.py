#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gdk
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime
import hashlib

class ConfigurationManager:
    """Manages saved monitor configurations based on connected monitors"""
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "hypr"
        self.profiles_path = self.config_dir / "hyprdisplays_profiles.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.profiles = self.load_profiles()
    
    def load_profiles(self):
        """Load saved monitor profiles"""
        if self.profiles_path.exists():
            try:
                with open(self.profiles_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading profiles: {e}")
                return {"profiles": {}, "history": []}
        return {"profiles": {}, "history": []}
    
    def save_profiles(self):
        """Save monitor profiles to disk"""
        try:
            with open(self.profiles_path, 'w') as f:
                json.dump(self.profiles, f, indent=2)
        except Exception as e:
            print(f"Error saving profiles: {e}")
    
    def get_monitor_fingerprint(self, monitors_info):
        """Create a unique fingerprint for a set of monitors
        
        Args:
            monitors_info: List of dicts with keys: name, make, model, serial
        
        Returns:
            String fingerprint that uniquely identifies this monitor setup
        """
        # Create detailed identifier for each monitor
        monitor_ids = []
        for monitor in monitors_info:
            # Use make, model, serial to uniquely identify the physical monitor
            # Fall back to name if details not available
            make = monitor.get('make', '').strip()
            model = monitor.get('model', '').strip()
            serial = monitor.get('serial', '').strip()
            name = monitor.get('name', 'unknown')
            
            # Create identifier: name|make|model|serial
            # This allows differentiating between same connector but different physical monitors
            if make or model or serial:
                # Use detailed info if available
                monitor_id = f"{name}|{make}|{model}|{serial}"
            else:
                # Fall back to just name (for monitors without detailed info)
                monitor_id = name
            
            monitor_ids.append(monitor_id)
        
        # Sort to ensure consistency regardless of detection order
        sorted_ids = sorted(monitor_ids)
        fingerprint = ";;".join(sorted_ids)
        return fingerprint
    
    def save_configuration(self, monitors_info, monitor_configs):
        """Save current configuration for this monitor setup
        
        Args:
            monitors_info: List of dicts with monitor details (name, make, model, serial)
            monitor_configs: Dict mapping monitor names to their configurations
        """
        fingerprint = self.get_monitor_fingerprint(monitors_info)
        
        # Prepare config data
        config_data = {
            "monitors": monitor_configs,
            "saved_at": datetime.now().isoformat(),
            "monitors_info": monitors_info  # Save the full monitor details
        }
        
        # Save to profiles
        self.profiles["profiles"][fingerprint] = config_data
        
        # Add to history
        history_entry = {
            "fingerprint": fingerprint,
            "monitors_info": monitors_info,
            "saved_at": config_data["saved_at"]
        }
        
        if "history" not in self.profiles:
            self.profiles["history"] = []
        
        # Keep only last 50 history entries
        self.profiles["history"].insert(0, history_entry)
        self.profiles["history"] = self.profiles["history"][:50]
        
        self.save_profiles()
        print(f"Saved configuration for fingerprint: {fingerprint}")
        print(f"  Monitors: {[m.get('name') for m in monitors_info]}")
        return fingerprint
    
    def load_configuration(self, monitors_info):
        """Load saved configuration for this monitor setup
        
        Args:
            monitors_info: List of dicts with monitor details (name, make, model, serial)
        
        Returns:
            Dict of monitor configurations if found, None otherwise
        """
        fingerprint = self.get_monitor_fingerprint(monitors_info)
        
        if fingerprint in self.profiles.get("profiles", {}):
            config = self.profiles["profiles"][fingerprint]
            print(f"Found saved configuration for fingerprint: {fingerprint}")
            print(f"  Saved at: {config.get('saved_at', 'unknown')}")
            return config.get("monitors", {})
        
        print(f"No saved configuration found for fingerprint: {fingerprint}")
        return None
    
    def get_history(self, limit=10):
        """Get configuration history"""
        return self.profiles.get("history", [])[:limit]

class DisplayConfig:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.description = data.get('description', '')
        self.disabled = data.get('disabled', False)
        self.available_modes = data.get('availableModes', [])
        self.focused = data.get('focused', False)  # Primary/focused monitor

        # Handle dimensions (might be 0/missing if disabled)
        self.width = data.get('width', 0)
        self.height = data.get('height', 0)
        self.refresh_rate = data.get('refreshRate', 60.0)
        
        # Heuristics for disabled monitors: use largest available mode or default
        if (self.disabled or self.width == 0 or self.height == 0) and self.available_modes:
            try:
                # Find best mode (usually first or one with highest resolution)
                # Parse first mode as default
                best_mode = self.available_modes[0]
                # Try to find the 'preferred' mode if possible? 
                # Hyprland usually returns preferred as first or implicit.
                
                parts = best_mode.replace('Hz', '').split('@')
                res_parts = parts[0].split('x')
                self.width = int(res_parts[0])
                self.height = int(res_parts[1])
                if len(parts) > 1:
                    self.refresh_rate = float(parts[1])
            except:
                self.width = 1920
                self.height = 1080
        elif self.disabled and self.width == 0:
             # Fallback if no modes available (unlikely for connected display)
             self.width = 1920
             self.height = 1080
             
        self.x = data.get('x', 0)
        self.y = data.get('y', 0)
        self.scale = data.get('scale', 1.0)
        self.transform = data.get('transform', 0)
        
        # Capability flags (best effort detection)
        self.is_10bit = data.get('10bit', False)
        self.vrr_enabled = data.get('vrr', False)

class MonitorRow(Gtk.Box):
    def __init__(self, display, all_monitors_list, on_change, on_primary_change):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.display = display
        self.all_monitors_list = all_monitors_list 
        self.on_change = on_change
        self.on_primary_change = on_primary_change
        self.on_monitor_size_changed = None  # Will be set by window class
        
        # Store previous size to detect changes
        self.prev_width = display.width / display.scale
        self.prev_height = display.height / display.scale
        if display.transform in [1, 3]:
            self.prev_width, self.prev_height = self.prev_height, self.prev_width
        
        # Container for content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)
        self.append(content)
        
        # Header with monitor name and primary button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        title_label = Gtk.Label(label=display.name)
        title_label.add_css_class("title-2")
        title_label.set_xalign(0)
        title_box.append(title_label)
        
        desc_label = Gtk.Label(label=display.description)
        desc_label.add_css_class("caption")
        desc_label.set_xalign(0)
        desc_label.set_wrap(True)
        title_box.append(desc_label)
        
        title_box.set_hexpand(True)
        header_box.append(title_box)
        
        # Enable toggle at the top (better UX)
        self.enabled_check = Gtk.Switch()
        self.enabled_check.set_active(not display.disabled)
        self.enabled_check.connect('notify::active', self.on_enabled_toggled)
        self.enabled_check.set_valign(Gtk.Align.CENTER)
        
        header_box.append(self.enabled_check)
        
        content.append(header_box)
        content.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        
        # --- Main Settings ---
        self.settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.append(self.settings_box)
        
        # Parse available modes
        self.modes_map = {}
        for mode in display.available_modes:
            if '@' in mode and 'x' in mode:
                try:
                    parts = mode.replace('Hz', '').split('@')
                    res = parts[0]
                    refresh = float(parts[1])
                    if res not in self.modes_map:
                        self.modes_map[res] = []
                    if refresh not in self.modes_map[res]:
                        self.modes_map[res].append(refresh)
                except:
                    pass
        
        # Sort resolutions
        def sort_res(res_str):
            try:
                w, h = map(int, res_str.split('x'))
                return w * h
            except:
                return 0
        self.sorted_resolutions = sorted(self.modes_map.keys(), key=sort_res, reverse=True)
        
        # Mirroring Option
        self.settings_box.append(self.create_label("Display Mode"))
        self.mirror_combo = Gtk.ComboBoxText()
        self.mirror_combo.append("extend", "Extend Display")
        
        # Add mirroring options
        if self.all_monitors_list:
            for m in self.all_monitors_list:
                if m['name'] != self.display.name:
                    self.mirror_combo.append(m['name'], f"Mirror of {m['name']}")
                    
        self.mirror_combo.set_active_id("extend") # Default
        self.mirror_combo.connect('changed', self.on_mirror_changed)
        self.settings_box.append(self.mirror_combo)
        
        # Resolution
        self.res_label = self.create_label("Resolution")
        self.settings_box.append(self.res_label)
        self.res_combo = Gtk.ComboBoxText()
        for res in self.sorted_resolutions:
            self.res_combo.append_text(res)
            
        current_res = f"{display.width}x{display.height}"
        if current_res in self.modes_map:
            self.res_combo.set_active_id(current_res)
            for i, res in enumerate(self.sorted_resolutions):
                if res == current_res:
                    self.res_combo.set_active(i)
                    break
        elif len(self.sorted_resolutions) > 0:
            self.res_combo.set_active(0)
            
        self.res_combo.connect('changed', self.on_res_changed)
        self.settings_box.append(self.res_combo)

        # Scale
        self.scale_label = self.create_label("Scale")
        self.settings_box.append(self.scale_label)
        
        self.scale_input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        # Presets
        for val in [1.0, 1.25, 1.5, 2.0]:
            btn = Gtk.Button(label=f"{int(val*100)}%")
            btn.connect('clicked', lambda b, v=val: self.scale_spin.set_value(v))
            self.scale_input_box.append(btn)
            
        # Custom input
        self.scale_spin = Gtk.SpinButton()
        self.scale_spin.set_adjustment(Gtk.Adjustment(value=display.scale, lower=0.5, upper=3.0, step_increment=0.1))
        self.scale_spin.set_digits(2)
        self.scale_spin.set_hexpand(True)
        self.scale_spin.connect('value-changed', self.on_setting_changed)
        self.scale_input_box.append(self.scale_spin)
        
        self.settings_box.append(self.scale_input_box)
        
        # Primary monitor row (Prettier)
        primary_frame = Gtk.Frame()
        primary_frame.add_css_class("card")
        
        primary_row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        primary_row_box.set_margin_top(12)
        primary_row_box.set_margin_bottom(12)
        primary_row_box.set_margin_start(12)
        primary_row_box.set_margin_end(12)
        
        primary_info = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        primary_heading = Gtk.Label(label="Primary Display")
        primary_heading.set_xalign(0)
        primary_heading.add_css_class("heading")
        primary_info.append(primary_heading)
        
        primary_desc = Gtk.Label(label="Use this display for top bar and system tray")
        primary_desc.set_xalign(0)
        primary_desc.add_css_class("caption")
        primary_desc.set_wrap(True)
        primary_info.append(primary_desc)
        
        primary_row_box.append(primary_info)
        primary_info.set_hexpand(True)
        
        self.primary_check = Gtk.Switch()
        self.primary_check.set_valign(Gtk.Align.CENTER)
        if display.focused:
            self.primary_check.set_active(True)
        self.primary_check.connect('state-set', self.on_primary_toggled)
        primary_row_box.append(self.primary_check)
        
        primary_frame.set_child(primary_row_box)
        self.settings_box.append(primary_frame)
        
        # --- Advanced Section ---
        
        content.append(Gtk.Box(height_request=10)) # Spacer
        
        self.advanced_revealer = Gtk.Revealer()
        self.advanced_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        
        advanced_toggle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.advanced_toggle = Gtk.CheckButton(label="Show Advanced Settings")
        self.advanced_toggle.connect('toggled', lambda b: self.advanced_revealer.set_reveal_child(b.get_active()))
        advanced_toggle_box.append(self.advanced_toggle)
        content.append(advanced_toggle_box)
        
        advanced_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        advanced_content.set_margin_top(12)
        self.advanced_revealer.set_child(advanced_content)
        content.append(self.advanced_revealer)
        
        # Refresh Rate
        advanced_content.append(self.create_label("Refresh Rate"))
        self.rate_combo = Gtk.ComboBoxText()
        self.update_rates_for_current_res()
        self.rate_combo.connect('changed', self.on_rate_changed)
        advanced_content.append(self.rate_combo)
        
        # Transform
        advanced_content.append(self.create_label("Rotation"))
        self.transform_combo = Gtk.ComboBoxText()
        transforms = ["0° (Normal)", "90°", "180°", "270°"]
        for t in transforms:
            self.transform_combo.append_text(t)
        self.transform_combo.set_active(display.transform if display.transform < 4 else 0)
        self.transform_combo.connect('changed', self.on_setting_changed)
        advanced_content.append(self.transform_combo)
        
        # Position (Internal but exposed in advanced)
        advanced_content.append(self.create_label("Position (X, Y)"))
        pos_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        self.x_spin = Gtk.SpinButton()
        self.x_spin.set_adjustment(Gtk.Adjustment(value=display.x, lower=-10000, upper=10000, step_increment=10))
        self.x_spin.set_digits(0)
        self.x_spin.set_hexpand(True)
        
        self.y_spin = Gtk.SpinButton()
        self.y_spin.set_adjustment(Gtk.Adjustment(value=display.y, lower=-10000, upper=10000, step_increment=10))
        self.y_spin.set_digits(0)
        self.y_spin.set_hexpand(True)
        
        pos_box.append(self.x_spin)
        pos_box.append(self.y_spin)
        advanced_content.append(pos_box)
        
        # Features
        advanced_content.append(self.create_label("Features"))
        
        # HDR
        self.hdr_check = Gtk.CheckButton(label="HDR (10-bit color)")
        if display.is_10bit:
            self.hdr_check.set_active(True)
        self.hdr_check.connect('toggled', self.on_setting_changed)
        advanced_content.append(self.hdr_check)
        
        # VRR
        self.vrr_check = Gtk.CheckButton(label="VRR (Adaptive Sync)")
        if display.vrr_enabled:
            self.vrr_check.set_active(True)
        self.vrr_check.connect('toggled', self.on_setting_changed)
        advanced_content.append(self.vrr_check)

        # Enabled toggle
        self.enabled_check = Gtk.CheckButton(label="Enable This Monitor")
        self.enabled_check.set_active(not display.disabled)
        self.enabled_check.connect('toggled', self.on_setting_changed)
        advanced_content.append(self.enabled_check)
        
    def create_label(self, text):
        l = Gtk.Label(label=text)
        l.set_xalign(0)
        l.add_css_class("heading")
        return l
    
    def on_enabled_toggled(self, switch, pspec):
        self.update_ui_state()
        self.on_setting_changed(switch)
        
    def on_mirror_changed(self, combo):
        self.update_ui_state()
        self.on_setting_changed(combo)
        
    def update_ui_state(self):
        """Enable/Disable controls based on state"""
        is_enabled = self.enabled_check.get_active()
        is_mirror = self.mirror_combo.get_active_id() != "extend"
        
        self.settings_box.set_sensitive(is_enabled)
        
        if is_enabled:
            # If mirroring, disable resolution/scale as they depend on source
            self.res_combo.set_sensitive(not is_mirror)
            self.scale_input_box.set_sensitive(not is_mirror)
            self.transform_combo.set_sensitive(not is_mirror)
    
    def on_primary_toggled(self, switch, state):
        """Handle primary monitor toggle"""
        if state:
            self.on_primary_change(self)
        else:
             # Prevent disabling if it's already active (enforcing radio behavior visually)
             # But since we have other monitors, we rely on them being enabled.
             # If user tries to untoggle, we just revert visual state unless another one is picked?
             # Actually, best UX is: if you click it off, it stays on. 
             # You must click another monitor to be primary.
             switch.set_active(True)
             return True
        self.on_change()
        return False
    
    def set_primary(self, is_primary):
        """Set this monitor as primary or not"""
        self.display.focused = is_primary
        # Block signal to prevent loop
        self.primary_check.handler_block_by_func(self.on_primary_toggled)
        self.primary_check.set_active(is_primary)
        self.primary_check.handler_unblock_by_func(self.on_primary_toggled)
    
    def update_rates_for_current_res(self):
        self.rate_combo.remove_all()
        current_res = self.res_combo.get_active_text()
        if not current_res or current_res not in self.modes_map:
            # Fallback
            self.rate_combo.append_text(f"{self.display.refresh_rate}Hz")
            self.rate_combo.set_active(0)
            return
            
        rates = sorted(self.modes_map[current_res], reverse=True)
        for rate in rates:
            self.rate_combo.append_text(f"{rate}Hz")
            
        # Try to select current refresh rate
        current_rate_str = f"{self.display.refresh_rate}Hz"
        selected = False
        
        # Check if we should select based on current display state
        if f"{self.display.width}x{self.display.height}" == current_res:
            best_rate = None
            min_diff = 1000
            for i, rate in enumerate(rates):
                diff = abs(rate - self.display.refresh_rate)
                if diff < min_diff:
                    min_diff = diff
                    best_rate = i
            if best_rate is not None and min_diff < 1.0:
                 self.rate_combo.set_active(best_rate)
                 selected = True
        
        if not selected and len(rates) > 0:
            self.rate_combo.set_active(0)

    def on_res_changed(self, combo):
        self.update_rates_for_current_res()
        self.on_change()

    def on_rate_changed(self, combo):
        self.on_change()
    
    def on_setting_changed(self, widget):
        """Called when scale, rotation, or enabled state changes"""
        # When any monitor size changes (due to rotation/scale), adjust connected monitors
        if hasattr(self, 'on_monitor_size_changed') and self.on_monitor_size_changed:
            self.on_monitor_size_changed(self)
        self.on_change()
    
    def get_config_line(self):
        """Generate Hyprland config line for this monitor"""
        if not self.enabled_check.get_active():
            return f"monitor={self.display.name},disabled"
            
        # Check mirroring
        mirror_source = self.mirror_combo.get_active_id()
        if mirror_source and mirror_source != "extend":
            return f"monitor={self.display.name},preferred,auto,1,mirror,{mirror_source}"
            
        resolution = self.res_combo.get_active_text()
        rate_text = self.rate_combo.get_active_text()
        
        if not resolution:
             resolution = f"{self.display.width}x{self.display.height}"
        
        if not rate_text:
             refresh = f"{self.display.refresh_rate:.2f}"
        else:
             refresh = rate_text.replace("Hz", "")
        
        x = int(self.x_spin.get_value())
        y = int(self.y_spin.get_value())
        scale = self.scale_spin.get_value()
        transform = self.transform_combo.get_active()
        
        # Debug output
        print(f"get_config_line for {self.display.name}: position={x}x{y}, scale={scale}, enabled={True}")
        
        config_line = f"monitor={self.display.name},{resolution}@{refresh},{x}x{y},{scale},transform,{transform}"
        
        # Add bitdepth if HDR is enabled
        if self.hdr_check.get_active():
             config_line += ",bitdepth,10"
             
        # Add vrr if enabled
        if self.vrr_check.get_active():
             config_line += ",vrr,1"
             
        return config_line

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
        
        # Internal drag state for smooth rendering (raw monitor coordinates)
        self.cur_drag_x = 0
        self.cur_drag_y = 0
    
    def get_monitor_data(self):
        """Get current monitor positions and sizes from widgets"""
        monitors = self.get_monitors()
        if not monitors:
            return []
        
        monitor_data = []
        for row in monitors:
            # Use current drag position for the monitor being dragged just for drawing/logic
            if row == self.dragging_monitor:
                 current_x = self.cur_drag_x
                 current_y = self.cur_drag_y
            else:
                 current_x = int(row.x_spin.get_value())
                 current_y = int(row.y_spin.get_value())
                 
            current_scale = row.scale_spin.get_value()
            current_transform = row.transform_combo.get_active()
            
            # Calculate logical size based on scale
            logical_width = row.display.width / current_scale
            logical_height = row.display.height / current_scale
            
            # Swap width/height for 90° and 270° rotations
            if current_transform in [1, 3]:  # 90° or 270°
                logical_width, logical_height = logical_height, logical_width
            
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
            is_enabled = m['enabled']
            
            # Draw shadow if enabled
            if is_enabled and (is_dragging or is_hovered):
                cr.set_source_rgba(0, 0, 0, 0.4)
                cr.rectangle(x + 4, y + 4, w, h)
                cr.fill()
            
            # Draw monitor background
            is_primary = m.get('primary', False)
            
            if not is_enabled:
                 cr.set_source_rgb(0.3, 0.3, 0.3) # Dark gray for disabled
            elif is_dragging:
                cr.set_source_rgb(0.4, 0.65, 0.95)
            elif is_hovered:
                cr.set_source_rgb(0.35, 0.55, 0.85)
            elif is_primary:
                cr.set_source_rgb(0.35, 0.55, 0.35)  # Green tint for primary
            else:
                cr.set_source_rgb(0.25, 0.45, 0.75)
            
            cr.rectangle(x, y, w, h)
            cr.fill()
            
            # Draw border
            if not is_enabled:
                cr.set_source_rgb(0.5, 0.5, 0.5)
                cr.set_line_width(1)
                cr.set_dash([4.0, 4.0])
            elif is_dragging:
                cr.set_source_rgb(0.6, 0.85, 1.0)
                cr.set_line_width(3)
                cr.set_dash([])
            elif is_hovered:
                cr.set_source_rgb(0.5, 0.75, 0.95)
                cr.set_line_width(2)
                cr.set_dash([])
            elif is_primary:
                cr.set_source_rgb(0.2, 0.4, 0.2)  # Darker border for primary
                cr.set_line_width(3)
                cr.set_dash([])
            else:
                cr.set_source_rgb(0.1, 0.1, 0.1)
                cr.set_line_width(2)
                cr.set_dash([])
            
            cr.rectangle(x, y, w, h)
            cr.stroke()
            cr.set_dash([]) # Reset dash
            
            # Draw display number badge
            if is_enabled:
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
                name_text += " ★"
            if not is_enabled:
                name_text += " (Disabled)"
            cr.show_text(name_text)
            
            # Draw rotation indicator if rotated
            transform = m['row'].transform_combo.get_active()
            if transform > 0 and is_enabled:
                rotation_labels = ["", "90°", "180°", "270°"]
                cr.set_font_size(10)
                cr.set_source_rgba(1, 1, 0.2, 0.9)  # Yellow for rotation indicator
                rotation_text = f"⟲ {rotation_labels[transform]}"
                cr.move_to(x + 8, y + 35)
                cr.show_text(rotation_text)
            
            # Draw resolution and scale at bottom
            cr.set_source_rgb(1, 1, 1)
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
        
        # Sort by z-order (enabled on top)
        monitor_data.sort(key=lambda m: 1 if m['enabled'] else 0, reverse=True)
        
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
            # Trigger selection callback
            if hasattr(self, 'on_monitor_selected_callback') and self.on_monitor_selected_callback:
                self.on_monitor_selected_callback(monitor)

            # Check if this is the primary monitor
            if monitor.display.focused:
                # Don't allow dragging the primary monitor
                return
            
            self.dragging_monitor = monitor
            self.drag_start_monitor_x = int(monitor.x_spin.get_value())
            self.drag_start_monitor_y = int(monitor.y_spin.get_value())
            
            # Initialize drag coordinates (used for visual rendering)
            self.cur_drag_x = self.drag_start_monitor_x
            self.cur_drag_y = self.drag_start_monitor_y
            
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
        """Handle drag update - move monitor with visual magnetic snapping"""
        if not self.dragging_monitor:
            return
        
        # Calculate delta in canvas pixels
        delta_canvas_x = offset_x
        delta_canvas_y = offset_y
        
        # Convert delta to monitor coordinates (raw movement)
        delta_monitor_x = delta_canvas_x / self.scale_factor
        delta_monitor_y = delta_canvas_y / self.scale_factor
        
        # Raw new position
        raw_x = self.drag_start_monitor_x + delta_monitor_x
        raw_y = self.drag_start_monitor_y + delta_monitor_y
        
        # Get monitor dimensions from data
        monitor_data = self.get_monitor_data()
        dragged_data = None
        for m in monitor_data:
            if m['row'] == self.dragging_monitor:
                dragged_data = m
                break
        
        if dragged_data:
            # Check for magnetic snap opportunities (loose snapping)
            snap_x, snap_y = self.find_magnetic_snap(
                self.dragging_monitor,
                raw_x, raw_y,
                dragged_data['width'], dragged_data['height'],
                monitor_data
            )
            
            # If a snap was found (not None), use it. Otherwise use raw.
            self.cur_drag_x = snap_x if snap_x is not None else raw_x
            self.cur_drag_y = snap_y if snap_y is not None else raw_y
            
        self.queue_draw()

    def find_magnetic_snap(self, monitor, x, y, width, height, all_monitors):
        """Find a magnetic snap position if close to an edge, otherwise return None"""
        # Range in monitor coordinates to snap
        snap_threshold = 40 / self.scale_factor # 40 visual pixels range
        snap_threshold = min(100, max(20, snap_threshold)) # Clamp to reasoanble monitor pixel range
        
        best_x, best_y = None, None
        min_distance = float('inf')

        for other in all_monitors:
            if other['row'] == monitor or not other['enabled']:
                continue
            
            snap_configs = [
                # Edge snaps
                {'x': other['x'] + other['width'], 'y': y,     'type': 'x'},
                {'x': other['x'] - width,          'y': y,     'type': 'x'},
                {'x': x, 'y': other['y'] + other['height'],    'type': 'y'},
                {'x': x, 'y': other['y'] - height,             'type': 'y'},
            ]
            
            for snap in snap_configs:
                # Calculate alignment for the other axis
                prop_x, prop_y = snap['x'], snap['y']
                
                # Check distance to this snap edge
                dist_x = abs(prop_x - x)
                dist_y = abs(prop_y - y)
                
                # If snapping X edge (vertical edges touching)
                if snap['type'] == 'x' and dist_x < snap_threshold:
                    # Check for Y alignments (top-top, bottom-bottom, center)
                    alignments = [
                         other['y'], 
                         other['y'] + other['height'] - height,
                         other['y'] + other['height']/2 - height/2
                    ]
                    
                    # Find closest Y alignment
                    best_align_y = y
                    closest_align_dist = snap_threshold
                    for ay in alignments:
                        if abs(ay - y) < closest_align_dist:
                            best_align_y = ay
                            closest_align_dist = abs(ay - y)

                    # Only valid if we don't overlap others (excluding the one we snapped to is complicated,
                    # just check general overlap at this new position)
                    if not self.check_overlap(prop_x, best_align_y, width, height, monitor, all_monitors):
                        total_dist = dist_x + closest_align_dist
                        if total_dist < min_distance:
                            min_distance = total_dist
                            best_x, best_y = prop_x, best_align_y
                            
                # If snapping Y edge (horizontal edges touching)
                elif snap['type'] == 'y' and dist_y < snap_threshold:
                    # Check for X alignments
                    alignments = [
                        other['x'],
                        other['x'] + other['width'] - width,
                        other['x'] + other['width']/2 - width/2
                    ]
                    
                    best_align_x = x
                    closest_align_dist = snap_threshold
                    for ax in alignments:
                        if abs(ax - x) < closest_align_dist:
                            best_align_x = ax
                            closest_align_dist = abs(ax - x)

                    if not self.check_overlap(best_align_x, prop_y, width, height, monitor, all_monitors):
                        total_dist = dist_y + closest_align_dist
                        if total_dist < min_distance:
                            min_distance = total_dist
                            best_x, best_y = best_align_x, prop_y

        return best_x, best_y
    
    def on_drag_end(self, gesture, offset_x, offset_y):
        """Handle drag end - finalize position and enforce connecting"""
        if not self.dragging_monitor:
            return
            
        monitor = self.dragging_monitor
        
        # Get final visual position
        final_x = self.cur_drag_x
        final_y = self.cur_drag_y
        
        monitor_data = self.get_monitor_data()
        dragged_data = None
        for m in monitor_data:
            if m['row'] == monitor:
                dragged_data = m
                break
                
        if dragged_data:
            w = dragged_data['width']
            h = dragged_data['height']
            
            # 1. Enforce lack of overlap (critical)
            # If overlapping, we must move it out. The find_snap_position handles this by finding valid spots.
            
            # 2. Enforce touching (critical)
            # Use strict snap finding to get the closest VALID (touching, non-overlapping) position
            valid_x, valid_y = self.find_snap_position(
                monitor, final_x, final_y, w, h, monitor_data
            )
            
            # Update the actual widgets, which will trigger the layout update
            monitor.x_spin.set_value(int(round(valid_x)))
            monitor.y_spin.set_value(int(round(valid_y)))
            
        self.dragging_monitor = None
        self.queue_draw()
        
        # Reset visual drag coordinates
        self.cur_drag_x = 0
        self.cur_drag_y = 0
        
        # Notify change
        self.on_position_changed()

class HyprDisplaysWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Hyprland Display Manager")
        self.set_default_size(1100, 750)
        
        # Initialize configuration manager
        self.config_manager = ConfigurationManager()
        
        # Track last monitor setup for auto-detection
        self.last_monitor_fingerprint = None
        
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
        self.canvas.on_monitor_selected_callback = self.on_monitor_selected
        canvas_box.append(self.canvas)
        paned.set_start_child(canvas_box)
        
        # Right side: Scrolled settings
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(False)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        paned.set_end_child(scrolled)
        
        # Initial position (approx 70% canvas, 30% sidebar)
        paned.set_position(800)
        
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
        
        # Start monitoring for display changes (every 1 second)
        GLib.timeout_add_seconds(1, self.check_monitor_changes)
    
    def check_monitor_changes(self):
        """Check if monitors have been connected/disconnected"""
        try:
            # Use 'all' to see disabled monitors too, so hiding a monitor doesn't trigger a setup change event
            result = subprocess.run(['hyprctl', 'monitors', 'all', '-j'], 
                                    capture_output=True, text=True, check=True)
            displays_data = json.loads(result.stdout)
            
            # Extract monitor info with details for fingerprinting
            monitors_info = []
            for d in displays_data:
                monitors_info.append({
                    'name': d.get('name'),
                    'make': d.get('make', ''),
                    'model': d.get('model', ''),
                    'serial': d.get('serial', '')
                })
            
            # Get current fingerprint
            current_fingerprint = self.config_manager.get_monitor_fingerprint(monitors_info)
            
            # Check if setup has changed
            if current_fingerprint != self.last_monitor_fingerprint:
                print(f"Monitor setup changed: {self.last_monitor_fingerprint} -> {current_fingerprint}")
                self.last_monitor_fingerprint = current_fingerprint
                
                # Try to load saved configuration for this setup
                saved_config = self.config_manager.load_configuration(monitors_info)
                if saved_config:
                    print("Applying saved configuration for this monitor setup...")
                    self.apply_saved_configuration(saved_config, displays_data)
                    self.status_label.set_text(f"Auto-applied saved config for {len(monitors_info)} monitor(s)")
                else:
                    print("No saved configuration found, keeping current")
                    self.load_displays()
        except Exception as e:
            print(f"Error checking monitor changes: {e}")
        
        return True  # Continue checking
    
    def apply_saved_configuration(self, saved_config, displays_data):
        """Apply a saved configuration to the displays"""
        try:
            # Apply via hyprctl first
            for monitor_name, config in saved_config.items():
                # Build monitor config line
                if config.get('disabled'):
                    cmd = f"{monitor_name},disabled"
                else:
                    resolution = config.get('resolution', f"{config.get('width')}x{config.get('height')}")
                    refresh = config.get('refresh_rate', 60)
                    x = config.get('x', 0)
                    y = config.get('y', 0)
                    scale = config.get('scale', 1.0)
                    transform = config.get('transform', 0)
                    
                    cmd = f"{monitor_name},{resolution}@{refresh},{x}x{y},{scale},transform,{transform}"
                    
                    if config.get('hdr') or config.get('bitdepth') == 10:
                        cmd += ",bitdepth,10"
                        
                    if config.get('vrr') == 1:
                        cmd += ",vrr,1"
                
                print(f"Applying saved config: monitor={cmd}")
                subprocess.run(['hyprctl', 'keyword', 'monitor', cmd], 
                             capture_output=True, text=True, check=False)
            
            # Reload display to update UI
            GLib.timeout_add(500, lambda: self.load_displays())
            
        except Exception as e:
            print(f"Error applying saved configuration: {e}")
            self.status_label.set_text(f"Error applying saved config: {e}")
    
    def load_displays(self):
        """Load current display configuration from Hyprland"""
        try:
            # Use 'all' to include disabled monitors
            result = subprocess.run(['hyprctl', 'monitors', 'all', '-j'], 
                                    capture_output=True, text=True, check=True)
            displays_data = json.loads(result.stdout)
            
            # Extract monitor info with details for fingerprinting
            monitors_info = []
            for d in displays_data:
                monitors_info.append({
                    'name': d.get('name'),
                    'make': d.get('make', ''),
                    'model': d.get('model', ''),
                    'serial': d.get('serial', '')
                })
            
            # Update fingerprint
            self.last_monitor_fingerprint = self.config_manager.get_monitor_fingerprint(monitors_info)
            
            # Clear existing
            while self.content_box.get_first_child():
                self.content_box.remove(self.content_box.get_first_child())
            self.monitor_rows.clear()
            
            # Check if any monitor is marked as focused/primary
            has_primary = any(d.get('focused', False) for d in displays_data)
            
            # Add monitor rows
            active_row_set = False
            for i, display_data in enumerate(displays_data):
                # If no primary is set, make the first one primary
                if not has_primary and i == 0:
                    display_data['focused'] = True
                
                display = DisplayConfig(display_data)
                row = MonitorRow(display, monitors_info, self.on_canvas_update, self.on_primary_changed)
                row.on_monitor_size_changed = self.on_monitor_size_changed  # Set callback
                self.monitor_rows.append(row)
                self.content_box.append(row)
                
                # Only show the sidebar for the focused monitor initially
                if display.focused and not active_row_set:
                    row.set_visible(True)
                    active_row_set = True
                else:
                    row.set_visible(False)
            
            # Fallback if somehow none visible
            if not active_row_set and self.monitor_rows:
                 self.monitor_rows[0].set_visible(True)
            
            self.canvas.queue_draw()
            
            # Check if we have a saved config for this setup
            saved_config = self.config_manager.load_configuration(monitors_info)
            if saved_config:
                status_msg = f"Loaded {len(displays_data)} display(s) - Saved config available"
                
                # Apply saved settings to UI (specifically HDR and VRR which aren't in hyprctl monitors)
                for row in self.monitor_rows:
                    if row.display.name in saved_config:
                        sc = saved_config[row.display.name]
                        if 'hdr' in sc:
                            row.hdr_check.set_active(sc['hdr'])
                        elif 'bitdepth' in sc:
                             row.hdr_check.set_active(sc['bitdepth'] == 10)
                             
                        if 'vrr' in sc:
                            row.vrr_check.set_active(sc['vrr'] == 1)
            else:
                status_msg = f"Loaded {len(displays_data)} display(s)"
            self.status_label.set_text(status_msg)
        except Exception as e:
            self.status_label.set_text(f"Error loading displays: {e}")

    def on_monitor_selected(self, monitor_row):
        """Handle monitor selection from canvas - show only the selected monitor settings"""
        for row in self.monitor_rows:
            row.set_visible(row == monitor_row)
    
    def on_monitor_size_changed(self, changed_row):
        """Called when any monitor size/rotation/enabled changes - adjust connected monitors"""
        print(f"=== MONITOR SIZE CHANGED: {changed_row.display.name} ===")
        
        # Get the OLD size from the stored previous values
        old_width = changed_row.prev_width
        old_height = changed_row.prev_height
        
        # Calculate NEW size
        scale = changed_row.scale_spin.get_value()
        transform = changed_row.transform_combo.get_active()
        
        new_width = changed_row.display.width / scale
        new_height = changed_row.display.height / scale
        
        if transform in [1, 3]:
            new_width, new_height = new_height, new_width
        
        # Update stored size
        changed_row.prev_width = new_width
        changed_row.prev_height = new_height
        
        changed_x = int(changed_row.x_spin.get_value())
        changed_y = int(changed_row.y_spin.get_value())
        
        print(f"  Old size: {old_width}x{old_height}")
        print(f"  New size: {new_width}x{new_height}")
        print(f"  Position: {changed_x}x{changed_y}")
        
        # Calculate the change in size
        width_delta = new_width - old_width
        height_delta = new_height - old_height
        
        if abs(width_delta) < 1 and abs(height_delta) < 1:
            print("  No significant size change, skipping adjustment")
            return
        
        # Adjust all monitors that are positioned relative to the changed monitor
        for row in self.monitor_rows:
            if row == changed_row or not row.enabled_check.get_active():
                continue
            
            # Don't move the primary monitor (it stays at 0x0)
            if row.display.focused:
                continue
            
            current_x = int(row.x_spin.get_value())
            current_y = int(row.y_spin.get_value())
            
            # Check if this monitor was adjacent to the changed one
            # Right edge: monitor's X equals changed monitor's old right edge
            old_right_edge = changed_x + old_width
            was_at_right = abs(current_x - old_right_edge) < 5  # Allow small tolerance
            
            # Bottom edge: monitor's Y equals changed monitor's old bottom edge
            old_bottom_edge = changed_y + old_height
            was_at_bottom = abs(current_y - old_bottom_edge) < 5
            
            new_x = current_x
            new_y = current_y
            
            if was_at_right and abs(width_delta) > 1:
                # Monitor was to the right, adjust X position
                new_x = int(changed_x + new_width)
                print(f"  Adjusting {row.display.name} X: {current_x} -> {new_x} (maintaining right edge connection)")
            
            if was_at_bottom and abs(height_delta) > 1:
                # Monitor was below, adjust Y position
                new_y = int(changed_y + new_height)
                print(f"  Adjusting {row.display.name} Y: {current_y} -> {new_y} (maintaining bottom edge connection)")
            
            if new_x != current_x or new_y != current_y:
                row.x_spin.set_value(new_x)
                row.y_spin.set_value(new_y)
        
        # Update canvas
        self.canvas.queue_draw()
    
    def on_primary_size_changed(self):
        """Called when primary monitor size/rotation/enabled changes - reposition other monitors"""
        print("=== PRIMARY MONITOR SIZE CHANGED ===")
        
        # Find the primary monitor
        primary_row = None
        for row in self.monitor_rows:
            if row.display.focused:
                primary_row = row
                break
        
        if not primary_row:
            return
        
        # Calculate primary monitor's current size
        primary_scale = primary_row.scale_spin.get_value()
        primary_transform = primary_row.transform_combo.get_active()
        primary_enabled = primary_row.enabled_check.get_active()
        
        primary_width = primary_row.display.width / primary_scale
        primary_height = primary_row.display.height / primary_scale
        
        # Swap dimensions for 90/270 rotation
        if primary_transform in [1, 3]:
            primary_width, primary_height = primary_height, primary_width
        
        # If primary is disabled, treat it as having no size
        if not primary_enabled:
            primary_width = 0
            primary_height = 0
        
        print(f"Primary monitor: {primary_row.display.name}, size: {primary_width}x{primary_height}, enabled: {primary_enabled}")
        
        # Primary is always at 0x0, so reposition other monitors relative to it
        for row in self.monitor_rows:
            if row == primary_row:
                # Primary always stays at 0x0
                row.x_spin.set_value(0)
                row.y_spin.set_value(0)
                continue
            
            # Get current position
            current_x = int(row.x_spin.get_value())
            current_y = int(row.y_spin.get_value())
            
            # Calculate this monitor's size
            scale = row.scale_spin.get_value()
            transform = row.transform_combo.get_active()
            width = row.display.width / scale
            height = row.display.height / scale
            
            if transform in [1, 3]:
                width, height = height, width
            
            print(f"Monitor {row.display.name}: current pos {current_x}x{current_y}, size {width}x{height}")
            
            # Check if this monitor overlaps with primary
            # Primary is at 0,0 with size primary_width x primary_height
            overlaps = not (current_x + width <= 0 or 
                          current_x >= primary_width or
                          current_y + height <= 0 or
                          current_y >= primary_height)
            
            if overlaps or primary_width == 0:
                # Need to reposition - place it to the right of primary
                new_x = int(primary_width)
                new_y = 0
                
                print(f"  Repositioning to {new_x}x{new_y} (was overlapping or primary disabled)")
                
                row.x_spin.set_value(new_x)
                row.y_spin.set_value(new_y)
        
        # Update canvas
        self.canvas.queue_draw()
    
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
        """Save configuration to Hyprland config file and profile"""
        hypr_dir = Path.home() / ".config" / "hypr"
        config_path = hypr_dir / "hyprland.conf"
        monitors_conf_path = hypr_dir / "monitors.conf"
        
        try:
            # Get current monitor details from Hyprland (including disabled)
            result = subprocess.run(['hyprctl', 'monitors', 'all', '-j'], 
                                  capture_output=True, text=True, check=True)
            displays_data = json.loads(result.stdout)
            
            # Extract monitor info with details for fingerprinting
            monitors_info = []
            for d in displays_data:
                monitors_info.append({
                    'name': d.get('name'),
                    'make': d.get('make', ''),
                    'model': d.get('model', ''),
                    'serial': d.get('serial', '')
                })
            
            # Generate monitor lines and configuration data
            monitor_lines = []
            monitor_configs = {}
            
            for row in self.monitor_rows:
                config_line = row.get_config_line()
                monitor_lines.append(config_line + '\n')
                
                # Store configuration data for profile
                resolution = row.res_combo.get_active_text()
                rate_text = row.rate_combo.get_active_text()
                
                if not resolution:
                    resolution = f"{row.display.width}x{row.display.height}"
                    
                if rate_text:
                    refresh = float(rate_text.replace("Hz", ""))
                else:
                    refresh = row.display.refresh_rate
                
                monitor_configs[row.display.name] = {
                    'resolution': resolution,
                    'refresh_rate': refresh,
                    'x': int(row.x_spin.get_value()),
                    'y': int(row.y_spin.get_value()),
                    'scale': row.scale_spin.get_value(),
                    'transform': row.transform_combo.get_active(),
                    'disabled': not row.enabled_check.get_active(),
                    'focused': row.display.focused,
                    'width': row.display.width,
                    'height': row.display.height,
                    'hdr': row.hdr_check.get_active(),
                    'vrr': row.vrr_check.get_active()
                }
                
                # Debug: print what we're saving
                print(f"Saving: {config_line}")
            
            # Save to profile system with monitor details
            fingerprint = self.config_manager.save_configuration(monitors_info, monitor_configs)
            
            # Strategy: Save to monitors.conf which is typically sourced last
            # This ensures our settings override any earlier monitor configs
            # Also add header to indicate this file is managed by HyprDisplays
            monitors_content = [
                "# Monitor configuration - Generated by HyprDisplays\n",
                "# This file is automatically managed by HyprDisplays.\n",
                "# Manual changes may be overwritten.\n",
                f"# Profile: {fingerprint[:60]}...\n",  # Truncate long fingerprints
                f"# Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
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
            
            # Reload Hyprland to ensure variables are reset and disabled monitors are handled
            # This is more robust than applying keywords individually, especially for disabling monitors
            print("Reloading Hyprland configuration...")
            result = subprocess.run(['hyprctl', 'reload'], capture_output=True, text=True, check=False)
            if result.returncode != 0:
                print(f"Warning: Failed to reload hyprland: {result.stderr}")
            
            self.status_label.set_text(f"Config saved for {len(monitors_info)} monitor(s) - Will auto-load on reconnect!")
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
