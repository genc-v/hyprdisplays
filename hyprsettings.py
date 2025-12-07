#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio, Gdk
import subprocess
import json
import os
from pathlib import Path
import re

class HyprlandConfig:
    """Interface to Hyprland configuration via hyprctl"""
    
    @staticmethod
    def get_option(option_name):
        """Get current value of a Hyprland option"""
        try:
            result = subprocess.run(
                ['hyprctl', 'getoption', '-j', option_name],
                capture_output=True, text=True, check=False
            )
            if result.returncode != 0 or not result.stdout.strip():
                return None
            data = json.loads(result.stdout)
            return data
        except (json.JSONDecodeError, Exception):
            return None
    
    @staticmethod
    def set_option(option_name, value):
        """Set a Hyprland option via hyprctl keyword"""
        try:
            # Format value properly
            if isinstance(value, bool):
                value = "true" if value else "false"
            elif isinstance(value, (int, float)):
                value = str(value)
            
            result = subprocess.run(
                ['hyprctl', 'keyword', option_name, value],
                capture_output=True, text=True, check=True
            )
            return True
        except Exception as e:
            print(f"Error setting {option_name} = {value}: {e}")
            return False
    
    @staticmethod
    def reload():
        """Reload Hyprland configuration"""
        try:
            subprocess.run(['hyprctl', 'reload'], check=True)
            return True
        except:
            return False


class SettingsPage(Gtk.Box):
    """Base class for settings pages"""
    
    def __init__(self, title, icon_name):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.title = title
        self.icon_name = icon_name
        # Add padding to prevent scrollbar overlap
        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        
    def create_group(self, title, description=None):
        """Create a preference group"""
        group = Adw.PreferencesGroup()
        group.set_title(title)
        if description:
            group.set_description(description)
        self.append(group)
        return group
    
    def create_switch_row(self, title, subtitle, option_name):
        """Create a switch row for boolean settings"""
        row = Adw.SwitchRow()
        row.set_title(title)
        if subtitle:
            row.set_subtitle(subtitle)
        
        # Load current value
        opt = HyprlandConfig.get_option(option_name)
        if opt:
            # Check if it's a boolean or int
            if 'int' in opt:
                row.set_active(opt['int'] == 1)
            elif 'str' in opt:
                row.set_active(opt['str'].lower() in ['true', 'yes', '1', 'on'])
        
        def on_toggled(switch, _):
            value = 1 if switch.get_active() else 0
            HyprlandConfig.set_option(option_name, value)
        
        row.connect('notify::active', on_toggled)
        return row
    
    def create_spin_row(self, title, subtitle, option_name, min_val, max_val, step=1, digits=0):
        """Create a spin button row for numeric settings"""
        row = Adw.ActionRow()
        row.set_title(title)
        if subtitle:
            row.set_subtitle(subtitle)
        
        # Load current value
        opt = HyprlandConfig.get_option(option_name)
        current_val = min_val
        if opt:
            if 'int' in opt:
                current_val = opt['int']
            elif 'float' in opt:
                current_val = opt['float']
        
        spin = Gtk.SpinButton()
        spin.set_adjustment(Gtk.Adjustment(
            value=current_val, 
            lower=min_val, 
            upper=max_val, 
            step_increment=step
        ))
        spin.set_digits(digits)
        spin.set_valign(Gtk.Align.CENTER)
        
        def on_changed(button):
            value = button.get_value()
            if digits == 0:
                value = int(value)
            HyprlandConfig.set_option(option_name, value)
        
        spin.connect('value-changed', on_changed)
        row.add_suffix(spin)
        row.set_activatable_widget(spin)
        return row
    
    def create_combo_row(self, title, subtitle, option_name, choices):
        """Create a combo box row for enum settings"""
        row = Adw.ComboRow()
        row.set_title(title)
        if subtitle:
            row.set_subtitle(subtitle)
        
        # Create string list model
        string_list = Gtk.StringList()
        for choice in choices:
            string_list.append(choice)
        row.set_model(string_list)
        
        # Load current value
        opt = HyprlandConfig.get_option(option_name)
        if opt:
            if 'int' in opt:
                row.set_selected(min(opt['int'], len(choices) - 1))
            elif 'str' in opt:
                try:
                    idx = choices.index(opt['str'])
                    row.set_selected(idx)
                except ValueError:
                    pass
        
        def on_changed(combo, _):
            selected = combo.get_selected()
            if selected < len(choices):
                HyprlandConfig.set_option(option_name, choices[selected])
        
        row.connect('notify::selected', on_changed)
        return row
    
    def create_color_row(self, title, subtitle, option_name):
        """Create a color picker row"""
        row = Adw.ActionRow()
        row.set_title(title)
        if subtitle:
            row.set_subtitle(subtitle)
        
        color_button = Gtk.ColorButton()
        color_button.set_valign(Gtk.Align.CENTER)
        
        # Load current color
        opt = HyprlandConfig.get_option(option_name)
        if opt and 'color' in opt:
            # Parse color (format: 0xRRGGBBAA)
            color_val = opt['color']
            if isinstance(color_val, int):
                r = ((color_val >> 24) & 0xFF) / 255.0
                g = ((color_val >> 16) & 0xFF) / 255.0
                b = ((color_val >> 8) & 0xFF) / 255.0
                a = (color_val & 0xFF) / 255.0
                rgba = Gdk.RGBA()
                rgba.red = r
                rgba.green = g
                rgba.blue = b
                rgba.alpha = a
                color_button.set_rgba(rgba)
        
        def on_color_set(button):
            rgba = button.get_rgba()
            # Convert to Hyprland format: 0xRRGGBBAA
            r = int(rgba.red * 255)
            g = int(rgba.green * 255)
            b = int(rgba.blue * 255)
            a = int(rgba.alpha * 255)
            color_hex = f"0x{r:02X}{g:02X}{b:02X}{a:02X}"
            HyprlandConfig.set_option(option_name, color_hex)
        
        color_button.connect('color-set', on_color_set)
        row.add_suffix(color_button)
        row.set_activatable_widget(color_button)
        return row


class GeneralPage(SettingsPage):
    """General settings page"""
    
    def __init__(self):
        super().__init__("General", "preferences-system-symbolic")
        
        # Border settings
        borders = self.create_group("Borders", "Window border configuration")
        borders.add(self.create_spin_row(
            "Border Size",
            "Width of window borders in pixels",
            "general:border_size", 0, 20, 1, 0
        ))
        borders.add(self.create_color_row(
            "Active Border Color",
            "Color of the active window border",
            "general:col.active_border"
        ))
        borders.add(self.create_color_row(
            "Inactive Border Color",
            "Color of inactive window borders",
            "general:col.inactive_border"
        ))
        
        # Gaps settings
        gaps = self.create_group("Gaps", "Space between windows and edges")
        gaps.add(self.create_spin_row(
            "Inner Gaps",
            "Gap size between windows",
            "general:gaps_in", 0, 50, 1, 0
        ))
        gaps.add(self.create_spin_row(
            "Outer Gaps",
            "Gap size from screen edges",
            "general:gaps_out", 0, 100, 1, 0
        ))
        gaps.add(self.create_spin_row(
            "Workspace Gaps",
            "Additional gap for fullscreen workspaces",
            "general:gaps_workspaces", 0, 100, 1, 0
        ))
        
        # Layout settings
        layout = self.create_group("Layout", "Window layout and behavior")
        layout.add(self.create_combo_row(
            "Layout",
            "Default tiling layout",
            "general:layout",
            ["dwindle", "master"]
        ))
        layout.add(self.create_switch_row(
            "Resize on Border",
            "Allow resizing windows by dragging borders",
            "general:resize_on_border"
        ))
        layout.add(self.create_switch_row(
            "Extend Border Grab Area",
            "Extend the area where borders can be grabbed",
            "general:extend_border_grab_area"
        ))
        layout.add(self.create_switch_row(
            "Hover Icon on Border",
            "Show resize cursor when hovering borders",
            "general:hover_icon_on_border"
        ))


class DecorationPage(SettingsPage):
    """Decoration settings page"""
    
    def __init__(self):
        super().__init__("Decoration", "preferences-desktop-theme-symbolic")
        
        # Rounding
        rounding = self.create_group("Rounding", "Window corner rounding")
        rounding.add(self.create_spin_row(
            "Rounding",
            "Radius of rounded window corners",
            "decoration:rounding", 0, 20, 1, 0
        ))
        
        # Opacity
        opacity = self.create_group("Opacity", "Window transparency")
        opacity.add(self.create_spin_row(
            "Active Opacity",
            "Opacity of active windows (0.0 - 1.0)",
            "decoration:active_opacity", 0.0, 1.0, 0.05, 2
        ))
        opacity.add(self.create_spin_row(
            "Inactive Opacity",
            "Opacity of inactive windows (0.0 - 1.0)",
            "decoration:inactive_opacity", 0.0, 1.0, 0.05, 2
        ))
        opacity.add(self.create_spin_row(
            "Fullscreen Opacity",
            "Opacity of fullscreen windows (0.0 - 1.0)",
            "decoration:fullscreen_opacity", 0.0, 1.0, 0.05, 2
        ))
        
        # Blur
        blur = self.create_group("Blur", "Background blur effects")
        blur.add(self.create_switch_row(
            "Enable Blur",
            "Enable background blur for transparent windows",
            "decoration:blur:enabled"
        ))
        blur.add(self.create_spin_row(
            "Blur Size",
            "Blur radius",
            "decoration:blur:size", 0, 20, 1, 0
        ))
        blur.add(self.create_spin_row(
            "Blur Passes",
            "Number of blur passes (more = better quality, slower)",
            "decoration:blur:passes", 1, 10, 1, 0
        ))
        
        # Dim
        dim = self.create_group("Dimming", "Inactive window dimming")
        dim.add(self.create_switch_row(
            "Dim Inactive",
            "Dim inactive windows",
            "decoration:dim_inactive"
        ))
        dim.add(self.create_spin_row(
            "Dim Strength",
            "Strength of dimming effect (0.0 - 1.0)",
            "decoration:dim_strength", 0.0, 1.0, 0.05, 2
        ))


class AnimationsPage(SettingsPage):
    """Animations settings page"""
    
    def __init__(self):
        super().__init__("Animations", "preferences-desktop-animation-symbolic")
        
        # Main animation settings
        anim = self.create_group("Animation Settings", "Global animation configuration")
        anim.add(self.create_switch_row(
            "Enable Animations",
            "Turn animations on or off globally",
            "animations:enabled"
        ))
        
        # Note about bezier curves and specific animations
        info = Adw.ActionRow()
        info.set_title("Advanced Animation Settings")
        info.set_subtitle("For detailed animation configuration (bezier curves, per-animation settings), edit the config file manually")
        anim.add(info)
        
        # Button to edit animations config
        open_btn = Gtk.Button(label="Edit Animations Config")
        open_btn.connect('clicked', lambda _: subprocess.Popen(['xdg-open', str(Path.home() / ".config/hypr/hyprland/general.conf")]))
        open_btn.set_valign(Gtk.Align.CENTER)
        info.add_suffix(open_btn)
        info.set_activatable_widget(open_btn)


class InputPage(SettingsPage):
    """Input settings page"""
    
    def __init__(self):
        super().__init__("Input", "input-mouse-symbolic")
        
        # Keyboard settings
        kb = self.create_group("Keyboard", "Keyboard configuration")
        kb.add(self.create_combo_row(
            "Keyboard Layout",
            "Primary keyboard layout",
            "input:kb_layout",
            ["us", "uk", "de", "fr", "es", "it", "ru", "jp", "cn"]
        ))
        kb.add(self.create_spin_row(
            "Repeat Rate",
            "Key repeat rate (keys per second)",
            "input:repeat_rate", 10, 100, 5, 0
        ))
        kb.add(self.create_spin_row(
            "Repeat Delay",
            "Delay before key repeat starts (ms)",
            "input:repeat_delay", 200, 1000, 50, 0
        ))
        kb.add(self.create_switch_row(
            "Numlock by Default",
            "Enable numlock on startup",
            "input:numlock_by_default"
        ))
        
        # Mouse settings
        mouse = self.create_group("Mouse", "Mouse and pointer settings")
        mouse.add(self.create_spin_row(
            "Mouse Sensitivity",
            "Mouse pointer sensitivity (-1.0 to 1.0)",
            "input:sensitivity", -1.0, 1.0, 0.1, 1
        ))
        mouse.add(self.create_spin_row(
            "Acceleration Profile",
            "Mouse acceleration curve (-1 = flat, 0 = none, 1 = adaptive)",
            "input:accel_profile", -1, 1, 1, 0
        ))
        mouse.add(self.create_switch_row(
            "Force No Acceleration",
            "Disable mouse acceleration completely",
            "input:force_no_accel"
        ))
        mouse.add(self.create_switch_row(
            "Left Handed Mode",
            "Swap left and right mouse buttons",
            "input:left_handed"
        ))
        mouse.add(self.create_spin_row(
            "Scroll Factor",
            "Scroll speed multiplier",
            "input:scroll_factor", 0.1, 5.0, 0.1, 1
        ))
        
        # Touchpad settings
        touchpad = self.create_group("Touchpad", "Touchpad configuration")
        touchpad.add(self.create_switch_row(
            "Natural Scroll",
            "Reverse scrolling direction (natural scrolling)",
            "input:natural_scroll"
        ))
        touchpad.add(self.create_switch_row(
            "Tap to Click",
            "Enable tap to click on touchpad",
            "input:touchpad:tap-to-click"
        ))
        touchpad.add(self.create_switch_row(
            "Drag Lock",
            "Enable drag lock for touchpad",
            "input:touchpad:drag_lock"
        ))
        touchpad.add(self.create_switch_row(
            "Disable While Typing",
            "Disable touchpad while typing",
            "input:touchpad:disable_while_typing"
        ))
        touchpad.add(self.create_switch_row(
            "Middle Button Emulation",
            "Emulate middle button with two-finger click",
            "input:touchpad:middle_button_emulation"
        ))
        
        # Focus settings
        focus = self.create_group("Focus", "Window focus behavior")
        focus.add(self.create_combo_row(
            "Follow Mouse",
            "How focus follows mouse pointer",
            "input:follow_mouse",
            ["0", "1", "2", "3"]
        ))
        # Add description for follow_mouse values
        info = Adw.ActionRow()
        info.set_title("Follow Mouse Values")
        info.set_subtitle("0 = disabled, 1 = always, 2 = loose (won't refocus on same window), 3 = tight")
        focus.add(info)
        
        focus.add(self.create_switch_row(
            "Float Switch Override Focus",
            "Override focus when switching between tiled and floating",
            "input:float_switch_override_focus"
        ))


class GesturesPage(SettingsPage):
    """Gestures settings page"""
    
    def __init__(self):
        super().__init__("Gestures", "input-touchpad-symbolic")
        
        # Workspace swipe
        swipe = self.create_group("Workspace Swipe", "Touchpad workspace switching")
        swipe.add(self.create_switch_row(
            "Enable Workspace Swipe",
            "Swipe with fingers to switch workspaces",
            "gestures:workspace_swipe"
        ))
        swipe.add(self.create_spin_row(
            "Swipe Fingers",
            "Number of fingers for workspace swipe",
            "gestures:workspace_swipe_fingers", 2, 5, 1, 0
        ))
        swipe.add(self.create_spin_row(
            "Swipe Distance",
            "Distance required to switch workspace (pixels)",
            "gestures:workspace_swipe_distance", 100, 1000, 50, 0
        ))
        swipe.add(self.create_switch_row(
            "Swipe Invert",
            "Invert swipe direction",
            "gestures:workspace_swipe_invert"
        ))


class MiscPage(SettingsPage):
    """Miscellaneous settings page"""
    
    def __init__(self):
        super().__init__("Misc", "preferences-other-symbolic")
        
        # General misc settings
        misc = self.create_group("General", "Miscellaneous settings")
        misc.add(self.create_switch_row(
            "Disable Hyprland Logo",
            "Hide Hyprland logo background",
            "misc:disable_hyprland_logo"
        ))
        misc.add(self.create_switch_row(
            "Disable Splash Rendering",
            "Disable splash text rendering",
            "misc:disable_splash_rendering"
        ))
        misc.add(self.create_switch_row(
            "Force Default Wallpaper",
            "Force use of default wallpaper",
            "misc:force_default_wallpaper"
        ))
        misc.add(self.create_switch_row(
            "VFR (Variable Frame Rate)",
            "Enable variable refresh rate",
            "misc:vfr"
        ))
        misc.add(self.create_switch_row(
            "VRR (Variable Refresh Rate)",
            "Enable variable refresh rate for monitors",
            "misc:vrr"
        ))
        
        # Performance
        perf = self.create_group("Performance", "Performance and rendering settings")
        perf.add(self.create_switch_row(
            "VFR (Variable Frame Rate)",
            "Enable variable refresh rate",
            "misc:vfr"
        ))
        perf.add(self.create_switch_row(
            "VRR (Variable Refresh Rate)",
            "Enable variable refresh rate for monitors",
            "misc:vrr"
        ))
        
        # Mouse
        mouse_misc = self.create_group("Mouse Behavior", "Additional mouse settings")
        mouse_misc.add(self.create_switch_row(
            "Mouse Move Enables DPMS",
            "Wake displays when moving mouse",
            "misc:mouse_move_enables_dpms"
        ))
        mouse_misc.add(self.create_switch_row(
            "Key Press Enables DPMS",
            "Wake displays when pressing keys",
            "misc:key_press_enables_dpms"
        ))
        mouse_misc.add(self.create_switch_row(
            "Always Follow on DND",
            "Window follows mouse during drag and drop",
            "misc:always_follow_on_dnd"
        ))
        
        # Focus
        focus_misc = self.create_group("Focus Behavior", "Window focus settings")
        focus_misc.add(self.create_switch_row(
            "Layers Hover on Touch",
            "Layers gain focus on touch",
            "misc:layers_hog_keyboard_focus"
        ))
        focus_misc.add(self.create_switch_row(
            "Animate Manual Resizes",
            "Animate windows when manually resizing",
            "misc:animate_manual_resizes"
        ))
        focus_misc.add(self.create_switch_row(
            "Animate Mouse Windowdragging",
            "Animate windows when dragging with mouse",
            "misc:animate_mouse_windowdragging"
        ))
        
        # Rendering
        render = self.create_group("Rendering", "Rendering backend settings")
        render.add(self.create_switch_row(
            "Disable Autoreload",
            "Disable automatic config reload",
            "misc:disable_autoreload"
        ))
        render.add(self.create_switch_row(
            "Enable Swallow",
            "Enable window swallowing",
            "misc:enable_swallow"
        ))
        render.add(self.create_combo_row(
            "Swallow Regex",
            "Window class regex for swallowing",
            "misc:swallow_regex",
            ["", "^(kitty)$", "^(Alacritty)$", "^(foot)$"]
        ))


class DwinLayoutPage(SettingsPage):
    """Dwindle layout settings"""
    
    def __init__(self):
        super().__init__("Dwindle Layout", "view-paged-symbolic")
        
        dwindle = self.create_group("Dwindle Layout", "Configuration for dwindle layout")
        dwindle.add(self.create_switch_row(
            "Pseudotile",
            "Enable pseudotiling",
            "dwindle:pseudotile"
        ))
        dwindle.add(self.create_switch_row(
            "Force Split",
            "Force split direction",
            "dwindle:force_split"
        ))
        dwindle.add(self.create_switch_row(
            "Preserve Split",
            "Preserve split direction when closing windows",
            "dwindle:preserve_split"
        ))
        dwindle.add(self.create_switch_row(
            "Smart Split",
            "Automatically choose split direction",
            "dwindle:smart_split"
        ))
        dwindle.add(self.create_switch_row(
            "Smart Resizing",
            "Smarter window resizing",
            "dwindle:smart_resizing"
        ))
        dwindle.add(self.create_switch_row(
            "Permanent Direction Override",
            "Permanently override split direction",
            "dwindle:permanent_direction_override"
        ))
        dwindle.add(self.create_spin_row(
            "Split Width Multiplier",
            "Multiplier for split width",
            "dwindle:split_width_multiplier", 0.5, 2.0, 0.1, 1
        ))
        dwindle.add(self.create_switch_row(
            "Use Active for Splits",
            "Use active window for determining split",
            "dwindle:use_active_for_splits"
        ))


class MasterLayoutPage(SettingsPage):
    """Master layout settings"""
    
    def __init__(self):
        super().__init__("Master Layout", "view-list-symbolic")
        
        master = self.create_group("Master Layout", "Configuration for master layout")
        master.add(self.create_switch_row(
            "Allow Small Split",
            "Allow splitting into small windows",
            "master:allow_small_split"
        ))
        master.add(self.create_combo_row(
            "New Status",
            "Position for new windows",
            "master:new_status",
            ["slave", "master", "inherit"]
        ))
        master.add(self.create_switch_row(
            "New On Top",
            "Place new windows at top of stack",
            "master:new_on_top"
        ))
        master.add(self.create_combo_row(
            "Orientation",
            "Master area orientation",
            "master:orientation",
            ["left", "right", "top", "bottom", "center"]
        ))
        master.add(self.create_switch_row(
            "Inherit Fullscreen",
            "Inherit fullscreen status",
            "master:inherit_fullscreen"
        ))
        master.add(self.create_switch_row(
            "Smart Resizing",
            "Enable smart resizing",
            "master:smart_resizing"
        ))
        master.add(self.create_switch_row(
            "Drop at Cursor",
            "Drop windows at cursor position",
            "master:drop_at_cursor"
        ))


class KeybindsPage(SettingsPage):
    """Keybinds configuration with easy-to-use interface"""
    
    # Common keybinds for users to choose from
    COMMON_ACTIONS = [
        ("exec, kitty", "Launch Terminal (kitty)"),
        ("exec, firefox", "Launch Firefox Browser"),
        ("exec, nautilus", "Launch File Manager"),
        ("killactive,", "Close Active Window"),
        ("exec, hyprlock", "Lock Screen"),
        ("togglefloating,", "Toggle Floating Mode"),
        ("fullscreen,", "Toggle Fullscreen"),
        ("workspace, 1", "Go to Workspace 1"),
        ("workspace, 2", "Go to Workspace 2"),
        ("workspace, 3", "Go to Workspace 3"),
        ("workspace, 4", "Go to Workspace 4"),
        ("movetoworkspace, 1", "Move Window to Workspace 1"),
        ("movefocus, l", "Move Focus Left"),
        ("movefocus, r", "Move Focus Right"),
        ("movefocus, u", "Move Focus Up"),
        ("movefocus, d", "Move Focus Down"),
        ("exec, playerctl play-pause", "Media: Play/Pause"),
        ("exec, playerctl next", "Media: Next Track"),
        ("exec, playerctl previous", "Media: Previous Track"),
        ("exec, pactl set-sink-volume @DEFAULT_SINK@ +5%", "Volume Up"),
        ("exec, pactl set-sink-volume @DEFAULT_SINK@ -5%", "Volume Down"),
        ("exec, pactl set-sink-mute @DEFAULT_SINK@ toggle", "Mute Toggle"),
    ]
    
    # User-friendly key names
    KEY_LABELS = {
        "XF86AudioNext": "Media Next",
        "XF86AudioPrev": "Media Previous",
        "XF86AudioPlay": "Media Play/Pause",
        "XF86AudioStop": "Media Stop",
        "XF86AudioRaiseVolume": "Volume Up",
        "XF86AudioLowerVolume": "Volume Down",
        "XF86AudioMute": "Mute",
        "XF86MonBrightnessUp": "Brightness Up",
        "XF86MonBrightnessDown": "Brightness Down",
        "Print": "Print Screen",
        "Super_L": "Super/Windows Key",
        "Return": "Enter",
        "space": "Spacebar",
    }
    
    def __init__(self):
        super().__init__("Keybinds", "input-keyboard-symbolic")
        self.hypr_dir = Path.home() / ".config" / "hypr"
        self.keybinds_file = self.find_config_file("keybinds.conf")
        
        # Search bar
        search_bar = Gtk.SearchEntry()
        search_bar.set_placeholder_text("Search keybinds...")
        search_bar.connect('search-changed', self.on_search)
        self.append(search_bar)
        
        # Info
        info = self.create_group("Keyboard Shortcuts", "Click a keybind to edit or delete it")
        
        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_margin_top(6)
        toolbar.set_margin_bottom(6)
        
        add_btn = Gtk.Button(label="Add Keybind")
        add_btn.set_icon_name("list-add-symbolic")
        add_btn.add_css_class("suggested-action")
        add_btn.connect('clicked', self.add_keybind)
        toolbar.append(add_btn)
        
        reload_btn = Gtk.Button(label="Reload")
        reload_btn.set_icon_name("view-refresh-symbolic")
        reload_btn.connect('clicked', lambda _: self.load_keybinds())
        toolbar.append(reload_btn)
        
        info.set_header_suffix(toolbar)
        
        # List of keybinds
        self.keybinds_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.keybinds_list.set_margin_end(12)  # Add padding to avoid scrollbar overlap
        info.add(self.keybinds_list)
        
        self.all_keybinds = []  # Store for search
        self.load_keybinds()
    
    def find_config_file(self, filename):
        paths = [
            self.hypr_dir / "hyprland" / filename,
            self.hypr_dir / "custom" / filename,
        ]
        for path in paths:
            if path.exists():
                return path
        return paths[0]
    
    def on_search(self, entry):
        search_text = entry.get_text().lower()
        for row, bind_data in self.all_keybinds:
            visible = search_text in bind_data.lower()
            row.set_visible(visible)
    
    def get_friendly_key_name(self, key):
        """Convert technical key name to friendly name"""
        return self.KEY_LABELS.get(key, key)
    
    def load_keybinds(self):
        while child := self.keybinds_list.get_first_child():
            self.keybinds_list.remove(child)
        
        self.all_keybinds = []
        
        if not self.keybinds_file.exists():
            label = Gtk.Label(label="No keybinds file found. Click 'Add Keybind' to create one!")
            self.keybinds_list.append(label)
            return
        
        with open(self.keybinds_file, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            if stripped.startswith('bind'):
                self.add_keybind_row(line, i)
    
    def add_keybind_row(self, bind_line, line_num):
        row = Adw.ExpanderRow()
        
        parts = bind_line.strip().split('=', 1)
        if len(parts) < 2:
            return
        
        bind_type = parts[0].strip()
        bind_rest = parts[1].strip()
        
        # Parse keybind
        bind_parts = []
        in_quotes = False
        current = ""
        for char in bind_rest:
            if char == '"':
                in_quotes = not in_quotes
                current += char
            elif char == ',' and not in_quotes:
                bind_parts.append(current.strip())
                current = ""
            else:
                current += char
        if current:
            bind_parts.append(current.strip())
        
        if len(bind_parts) >= 3:
            mods = bind_parts[0]
            key = bind_parts[1]
            action = ', '.join(bind_parts[2:])
            
            # Friendly display
            friendly_key = self.get_friendly_key_name(key)
            title = f"{mods} + {friendly_key}" if mods else friendly_key
            
            import html
            row.set_title(title)
            row.set_subtitle(html.escape(action[:100]))
            
            # Action details in expanded view
            action_row = Adw.ActionRow()
            action_row.set_title("Action")
            action_row.set_subtitle(html.escape(action))
            row.add_row(action_row)
            
            type_row = Adw.ActionRow()
            type_row.set_title("Bind Type")
            type_row.set_subtitle(bind_type)
            row.add_row(type_row)
            
            # Buttons
            btn_box = Gtk.Box(spacing=6)
            
            edit_btn = Gtk.Button(label="Edit")
            edit_btn.set_icon_name("document-edit-symbolic")
            edit_btn.connect('clicked', lambda b, ln=line_num, bl=bind_line: self.edit_keybind(ln, bl))
            btn_box.append(edit_btn)
            
            del_btn = Gtk.Button(label="Delete")
            del_btn.set_icon_name("user-trash-symbolic")
            del_btn.add_css_class("destructive-action")
            del_btn.connect('clicked', lambda b, ln=line_num: self.delete_keybind(ln))
            btn_box.append(del_btn)
            
            row.add_action(btn_box)
            
            self.keybinds_list.append(row)
            self.all_keybinds.append((row, f"{title} {action}"))
    
    def add_keybind(self, button):
        dialog = Adw.Window()
        dialog.set_title("Add Keybind")
        dialog.set_default_size(500, 600)
        dialog.set_transient_for(self.get_root())
        dialog.set_modal(True)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        dialog.set_content(box)
        
        # Header
        header = Adw.HeaderBar()
        box.append(header)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content.set_margin_start(18)
        content.set_margin_end(18)
        content.set_margin_top(18)
        content.set_margin_bottom(18)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_child(content)
        box.append(scroll)
        
        # Step 1: Choose action
        content.append(Gtk.Label(label="<b>1. Choose Action</b>", use_markup=True, xalign=0))
        
        action_combo = Gtk.ComboBoxText()
        for action_val, action_desc in self.COMMON_ACTIONS:
            action_combo.append(action_val, action_desc)
        action_combo.append("custom", "Custom Command...")
        action_combo.set_active(0)
        content.append(action_combo)
        
        # Custom action entry (hidden by default)
        custom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        custom_entry = Gtk.Entry()
        custom_entry.set_placeholder_text("e.g., exec, firefox")
        custom_box.append(Gtk.Label(label="Custom Action:", xalign=0))
        custom_box.append(custom_entry)
        custom_box.set_visible(False)
        content.append(custom_box)
        
        def on_action_changed(combo):
            custom_box.set_visible(combo.get_active_id() == "custom")
        action_combo.connect('changed', on_action_changed)
        
        content.append(Gtk.Label(label="<b>2. Press the Key You Want to Use</b>", use_markup=True, xalign=0))
        
        # Key display area (shows what was pressed)
        key_display_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        # Create a frame to capture key events
        key_frame = Gtk.Frame()
        key_frame.set_size_request(-1, 80)
        
        key_label = Gtk.Label(label="Click here and press any key...")
        key_label.set_margin_start(12)
        key_label.set_margin_end(12)
        key_label.set_margin_top(12)
        key_label.set_margin_bottom(12)
        key_label.set_wrap(True)
        key_frame.set_child(key_label)
        
        detected_key = {"key": "", "mods": []}
        
        def on_key_press(controller, keyval, keycode, state):
            """Capture key press"""
            # Get key name
            keyname = Gdk.keyval_name(keyval)
            
            # Ignore modifier keys by themselves
            if keyname in ["Control_L", "Control_R", "Alt_L", "Alt_R", 
                          "Shift_L", "Shift_R", "Super_L", "Super_R",
                          "Meta_L", "Meta_R"]:
                return True
            
            # Detect modifiers from event
            mods = []
            if state & Gdk.ModifierType.CONTROL_MASK:
                mods.append("Ctrl")
            if state & Gdk.ModifierType.ALT_MASK:
                mods.append("Alt")
            if state & Gdk.ModifierType.SHIFT_MASK:
                mods.append("Shift")
            if state & Gdk.ModifierType.SUPER_MASK:
                mods.append("Super")
            
            detected_key["key"] = keyname
            detected_key["mods"] = mods
            
            # Update UI
            if mods:
                display_text = " + ".join(mods) + " + " + (self.KEY_LABELS.get(keyname, keyname))
            else:
                display_text = self.KEY_LABELS.get(keyname, keyname)
            
            key_label.set_markup(f"<big><b>✓ Recorded: {display_text}</b></big>")
            
            return True
        
        # Set up key event controller on the dialog itself
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", on_key_press)
        dialog.add_controller(key_controller)
        
        # Make the frame focusable
        key_frame.set_focusable(True)
        
        # Add click handler to focus
        click_controller = Gtk.GestureClick()
        def on_click(gesture, n_press, x, y):
            key_frame.grab_focus()
            key_label.set_text("Press any key now...")
        click_controller.connect("pressed", on_click)
        key_frame.add_controller(click_controller)
        
        key_display_box.append(key_frame)
        
        # Helper text
        helper = Gtk.Label(
            label="Click the box above and press any key combination.\nModifiers will be detected automatically!",
            wrap=True,
            xalign=0
        )
        helper.add_css_class("dim-label")
        key_display_box.append(helper)
        
        content.append(key_display_box)
        
        # Or choose from media keys
        content.append(Gtk.Label(label="Or choose a media/special key:", xalign=0))
        media_combo = Gtk.ComboBoxText()
        media_combo.append("", "Choose a special key...")
        media_combo.append("XF86AudioNext", "🎵 Media Next")
        media_combo.append("XF86AudioPrev", "🎵 Media Previous")
        media_combo.append("XF86AudioPlay", "🎵 Play/Pause")
        media_combo.append("XF86AudioRaiseVolume", "🔊 Volume Up")
        media_combo.append("XF86AudioLowerVolume", "🔉 Volume Down")
        media_combo.append("XF86AudioMute", "🔇 Mute")
        media_combo.append("XF86MonBrightnessUp", "☀️ Brightness Up")
        media_combo.append("XF86MonBrightnessDown", "🌙 Brightness Down")
        media_combo.append("Print", "📸 Screenshot/Print Screen")
        media_combo.set_active(0)
        content.append(media_combo)
        
        def on_media_selected(combo):
            if combo.get_active_id():
                detected_key["key"] = combo.get_active_id()
                detected_key["mods"] = []
                display = self.KEY_LABELS.get(combo.get_active_id(), combo.get_active_id())
                key_label.set_markup(f"<big><b>✓ Selected: {display}</b></big>")
        
        media_combo.connect('changed', on_media_selected)
        
        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.END)
        btn_box.set_margin_top(12)
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect('clicked', lambda b: dialog.close())
        btn_box.append(cancel_btn)
        
        add_btn = Gtk.Button(label="Add Keybind")
        add_btn.add_css_class("suggested-action")
        btn_box.append(add_btn)
        
        content.append(btn_box)
        
        def on_add(btn):
            # Get key from recording
            key = detected_key.get("key", "")
            if not key:
                return
            
            # Build modifier string from detected mods
            mods = detected_key.get("mods", [])
            mod_str = " ".join(mods) if mods else ""
            
            # Get action
            if action_combo.get_active_id() == "custom":
                action = custom_entry.get_text().strip()
            else:
                action = action_combo.get_active_id()
            
            if not action:
                return
            
            # Build bind line
            if mod_str:
                bind_line = f"bind = {mod_str}, {key}, {action}\n"
            else:
                bind_line = f"bind = , {key}, {action}\n"
            
            self.save_keybind(bind_line)
            self.load_keybinds()
            dialog.close()
        
        add_btn.connect('clicked', on_add)
        dialog.present()
    
    def edit_keybind(self, line_num, old_bind_line):
        """Edit existing keybind"""
        # For now, just delete and add new
        # TODO: Pre-fill the add dialog with existing values
        self.delete_keybind(line_num)
        self.add_keybind(None)
    
    def delete_keybind(self, line_num):
        if not self.keybinds_file.exists():
            return
        
        with open(self.keybinds_file, 'r') as f:
            lines = f.readlines()
        
        bind_count = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                if line.strip().startswith('bind'):
                    if bind_count == line_num:
                        lines[i] = ''
                        break
                    bind_count += 1
        
        with open(self.keybinds_file, 'w') as f:
            f.writelines(lines)
        
        self.load_keybinds()
        subprocess.run(['hyprctl', 'reload'], capture_output=True)
    
    def save_keybind(self, bind_line):
        self.keybinds_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.keybinds_file, 'a') as f:
            f.write(bind_line)
        subprocess.run(['hyprctl', 'reload'], capture_output=True)


class RulesPage(SettingsPage):
    """Window rules with easy-to-use interface"""
    
    # Common window rules
    RULE_TYPES = [
        ("float", "Make window float"),
        ("tile", "Make window tiled"),
        ("fullscreen", "Make window fullscreen"),
        ("maximize", "Maximize window"),
        ("center", "Center window on screen"),
        ("opacity 0.9", "Set 90% opacity"),
        ("opacity 0.8", "Set 80% opacity"),
        ("noblur", "Disable blur"),
        ("noshadow", "Disable shadow"),
        ("noborder", "Remove window border"),
        ("workspace 1", "Move to workspace 1"),
        ("workspace 2", "Move to workspace 2"),
        ("workspace 3", "Move to workspace 3"),
        ("pin", "Pin window (show on all workspaces)"),
    ]
    
    # Common applications
    COMMON_APPS = [
        ("kitty", "Kitty Terminal"),
        ("firefox", "Firefox Browser"),
        ("chromium", "Chromium Browser"),
        ("nautilus", "File Manager (Nautilus)"),
        ("org.gnome.Nautilus", "File Manager (GNOME)"),
        ("thunar", "File Manager (Thunar)"),
        ("discord", "Discord"),
        ("steam", "Steam"),
        ("pavucontrol", "Volume Control"),
        ("nm-connection-editor", "Network Manager"),
    ]
    
    def __init__(self):
        super().__init__("Rules", "preferences-system-windows-symbolic")
        self.hypr_dir = Path.home() / ".config" / "hypr"
        self.rules_file = self.find_config_file("rules.conf")
        
        # Search bar
        search_bar = Gtk.SearchEntry()
        search_bar.set_placeholder_text("Search rules...")
        search_bar.connect('search-changed', self.on_search)
        self.append(search_bar)
        
        info = self.create_group("Window Rules", "Control how specific windows behave")
        
        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_margin_top(6)
        toolbar.set_margin_bottom(6)
        
        add_btn = Gtk.Button(label="Add Rule")
        add_btn.set_icon_name("list-add-symbolic")
        add_btn.add_css_class("suggested-action")
        add_btn.connect('clicked', self.add_rule)
        toolbar.append(add_btn)
        
        reload_btn = Gtk.Button(label="Reload")
        reload_btn.set_icon_name("view-refresh-symbolic")
        reload_btn.connect('clicked', lambda _: self.load_rules())
        toolbar.append(reload_btn)
        
        info.set_header_suffix(toolbar)
        
        # List of rules
        self.rules_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.rules_list.set_margin_end(12)  # Add padding to avoid scrollbar overlap
        info.add(self.rules_list)
        
        self.all_rules = []
        self.load_rules()
    
    def find_config_file(self, filename):
        paths = [
            self.hypr_dir / "hyprland" / filename,
            self.hypr_dir / "custom" / filename,
        ]
        for path in paths:
            if path.exists():
                return path
        return paths[0]
    
    def on_search(self, entry):
        search_text = entry.get_text().lower()
        for row, rule_data in self.all_rules:
            visible = search_text in rule_data.lower()
            row.set_visible(visible)
    
    def load_rules(self):
        while child := self.rules_list.get_first_child():
            self.rules_list.remove(child)
        
        self.all_rules = []
        
        if not self.rules_file.exists():
            label = Gtk.Label(label="No rules file found. Click 'Add Rule' to create one!")
            self.rules_list.append(label)
            return
        
        with open(self.rules_file, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            if stripped.startswith('windowrule'):
                self.add_rule_row(line, i)
    
    def add_rule_row(self, rule_line, line_num):
        row = Adw.ExpanderRow()
        
        parts = rule_line.strip().split('=', 1)
        if len(parts) < 2:
            return
        
        rule_type = parts[0].strip()
        rule_rest = parts[1].strip()
        
        # Parse rule
        rule_parts = rule_rest.split(',', 1)
        if len(rule_parts) >= 2:
            rule_action = rule_parts[0].strip()
            rule_match = rule_parts[1].strip()
            
            import html
            row.set_title(f"Rule: {html.escape(rule_action)}")
            row.set_subtitle(f"Matches: {html.escape(rule_match)}")
            
            # Details in expanded view
            action_row = Adw.ActionRow()
            action_row.set_title("Action")
            action_row.set_subtitle(html.escape(rule_action))
            row.add_row(action_row)
            
            match_row = Adw.ActionRow()
            match_row.set_title("Match Pattern")
            match_row.set_subtitle(html.escape(rule_match))
            row.add_row(match_row)
            
            type_row = Adw.ActionRow()
            type_row.set_title("Rule Type")
            type_row.set_subtitle(rule_type)
            row.add_row(type_row)
            
            # Buttons
            btn_box = Gtk.Box(spacing=6)
            
            del_btn = Gtk.Button(label="Delete")
            del_btn.set_icon_name("user-trash-symbolic")
            del_btn.add_css_class("destructive-action")
            del_btn.connect('clicked', lambda b, ln=line_num: self.delete_rule(ln))
            btn_box.append(del_btn)
            
            row.add_action(btn_box)
            
            self.rules_list.append(row)
            self.all_rules.append((row, f"{rule_action} {rule_match}"))
    
    def add_rule(self, button):
        dialog = Adw.Window()
        dialog.set_title("Add Window Rule")
        dialog.set_default_size(500, 650)
        dialog.set_transient_for(self.get_root())
        dialog.set_modal(True)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        dialog.set_content(box)
        
        # Header
        header = Adw.HeaderBar()
        box.append(header)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content.set_margin_start(18)
        content.set_margin_end(18)
        content.set_margin_top(18)
        content.set_margin_bottom(18)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_child(content)
        box.append(scroll)
        
        # Step 1: Choose what to do
        content.append(Gtk.Label(label="<b>1. Choose what the rule should do</b>", use_markup=True, xalign=0))
        
        rule_combo = Gtk.ComboBoxText()
        for rule_val, rule_desc in self.RULE_TYPES:
            rule_combo.append(rule_val, rule_desc)
        rule_combo.append("custom", "Custom rule...")
        rule_combo.set_active(0)
        content.append(rule_combo)
        
        # Custom rule entry
        custom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        custom_entry = Gtk.Entry()
        custom_entry.set_placeholder_text("e.g., size 800 600")
        custom_box.append(Gtk.Label(label="Custom Rule:", xalign=0))
        custom_box.append(custom_entry)
        custom_box.set_visible(False)
        content.append(custom_box)
        
        def on_rule_changed(combo):
            custom_box.set_visible(combo.get_active_id() == "custom")
        rule_combo.connect('changed', on_rule_changed)
        
        # Step 2: Choose how to match windows
        content.append(Gtk.Label(label="<b>2. Choose which windows to apply this to</b>", use_markup=True, xalign=0))
        
        match_type_combo = Gtk.ComboBoxText()
        match_type_combo.append("class", "Application class (recommended)")
        match_type_combo.append("title", "Window title")
        match_type_combo.append("initialClass", "Initial application class")
        match_type_combo.append("initialTitle", "Initial window title")
        match_type_combo.set_active(0)
        content.append(match_type_combo)
        
        # Common apps dropdown
        content.append(Gtk.Label(label="Choose a common application:", xalign=0))
        app_combo = Gtk.ComboBoxText()
        app_combo.append("", "Or type manually below...")
        for app_class, app_name in self.COMMON_APPS:
            app_combo.append(app_class, app_name)
        app_combo.set_active(0)
        content.append(app_combo)
        
        # Manual entry
        content.append(Gtk.Label(label="Or enter application class/title:", xalign=0))
        match_entry = Gtk.Entry()
        match_entry.set_placeholder_text("e.g., firefox, kitty, discord")
        content.append(match_entry)
        
        def on_app_selected(combo):
            if combo.get_active_id():
                match_entry.set_text(combo.get_active_id())
        app_combo.connect('changed', on_app_selected)
        
        # Help text
        help_label = Gtk.Label(
            label="Tip: Right-click a window title bar and select 'Window Info' to see its class name",
            wrap=True,
            xalign=0
        )
        help_label.add_css_class("dim-label")
        content.append(help_label)
        
        # Regex option
        regex_check = Gtk.CheckButton(label="Use exact match (recommended for beginners)")
        regex_check.set_active(True)
        content.append(regex_check)
        
        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.END)
        btn_box.set_margin_top(12)
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect('clicked', lambda b: dialog.close())
        btn_box.append(cancel_btn)
        
        add_btn = Gtk.Button(label="Add Rule")
        add_btn.add_css_class("suggested-action")
        btn_box.append(add_btn)
        
        content.append(btn_box)
        
        def on_add(btn):
            # Get rule action
            if rule_combo.get_active_id() == "custom":
                rule_action = custom_entry.get_text().strip()
            else:
                rule_action = rule_combo.get_active_id()
            
            # Get match
            match_value = match_entry.get_text().strip()
            if not match_value or not rule_action:
                return
            
            # Format match
            match_type = match_type_combo.get_active_id()
            if regex_check.get_active():
                # Exact match
                match_pattern = f"{match_type}:^({match_value})$"
            else:
                # Partial match
                match_pattern = f"{match_type}:{match_value}"
            
            # Build rule
            rule_line = f"windowrulev2 = {rule_action}, {match_pattern}\n"
            
            self.save_rule(rule_line)
            self.load_rules()
            dialog.close()
        
        add_btn.connect('clicked', on_add)
        dialog.present()
    
    def delete_rule(self, line_num):
        if not self.rules_file.exists():
            return
        
        with open(self.rules_file, 'r') as f:
            lines = f.readlines()
        
        rule_count = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                if line.strip().startswith('windowrule'):
                    if rule_count == line_num:
                        lines[i] = ''
                        break
                    rule_count += 1
        
        with open(self.rules_file, 'w') as f:
            f.writelines(lines)
        
        self.load_rules()
        subprocess.run(['hyprctl', 'reload'], capture_output=True)
    
    def save_rule(self, rule_line):
        self.rules_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.rules_file, 'a') as f:
            f.write(rule_line)
        subprocess.run(['hyprctl', 'reload'], capture_output=True)


class AutostartPage(SettingsPage):
    """Autostart programs with list view"""
    
    # Common programs to autostart
    COMMON_PROGRAMS = [
        ("waybar", "Status Bar (Waybar)"),
        ("hyprpaper", "Wallpaper Manager (Hyprpaper)"),
        ("dunst", "Notification Daemon (Dunst)"),
        ("mako", "Notification Daemon (Mako)"),
        ("nm-applet", "Network Manager Applet"),
        ("blueman-applet", "Bluetooth Manager"),
        ("wl-paste --watch cliphist store", "Clipboard Manager"),
        ("polkit-gnome-authentication-agent-1", "Authentication Agent"),
        ("gnome-keyring-daemon --start --components=secrets", "Keyring Manager"),
        ("hypridle", "Idle Manager (Hypridle)"),
        ("udiskie", "USB Auto-mounter"),
        ("easyeffects --gapplication-service", "Audio Effects"),
    ]
    
    def __init__(self):
        super().__init__("Autostart", "system-run-symbolic")
        self.hypr_dir = Path.home() / ".config" / "hypr"
        self.execs_file = self.find_config_file("execs.conf")
        
        # Search bar
        search_bar = Gtk.SearchEntry()
        search_bar.set_placeholder_text("Search autostart programs...")
        search_bar.connect('search-changed', self.on_search)
        self.append(search_bar)
        
        info = self.create_group("Autostart Programs", "Programs that launch when Hyprland starts")
        
        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_margin_top(6)
        toolbar.set_margin_bottom(6)
        
        add_btn = Gtk.Button(label="Add Program")
        add_btn.set_icon_name("list-add-symbolic")
        add_btn.add_css_class("suggested-action")
        add_btn.connect('clicked', self.add_program)
        toolbar.append(add_btn)
        
        reload_btn = Gtk.Button(label="Reload")
        reload_btn.set_icon_name("view-refresh-symbolic")
        reload_btn.connect('clicked', lambda _: self.load_programs())
        toolbar.append(reload_btn)
        
        info.set_header_suffix(toolbar)
        
        # List of programs
        self.programs_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.programs_list.set_margin_end(12)  # Add padding to avoid scrollbar overlap
        info.add(self.programs_list)
        
        self.all_programs = []
        self.load_programs()
    
    def find_config_file(self, filename):
        paths = [
            self.hypr_dir / "hyprland" / filename,
            self.hypr_dir / "custom" / filename,
        ]
        for path in paths:
            if path.exists():
                return path
        return paths[0]
    
    def on_search(self, entry):
        search_text = entry.get_text().lower()
        for row, prog_data in self.all_programs:
            visible = search_text in prog_data.lower()
            row.set_visible(visible)
    
    def load_programs(self):
        while child := self.programs_list.get_first_child():
            self.programs_list.remove(child)
        
        self.all_programs = []
        
        if not self.execs_file.exists():
            label = Gtk.Label(label="No execs file found. Click 'Add Program' to create one!")
            self.programs_list.append(label)
            return
        
        with open(self.execs_file, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            if stripped.startswith('exec'):
                self.add_program_row(line, i)
    
    def add_program_row(self, exec_line, line_num):
        row = Adw.ExpanderRow()
        
        parts = exec_line.strip().split('=', 1)
        if len(parts) < 2:
            return
        
        exec_type = parts[0].strip()
        command = parts[1].strip()
        
        import html
        row.set_title(html.escape(command[:80]))
        row.set_subtitle(f"Type: {exec_type}")
        
        # Details in expanded view
        cmd_row = Adw.ActionRow()
        cmd_row.set_title("Command")
        cmd_row.set_subtitle(html.escape(command))
        row.add_row(cmd_row)
        
        type_row = Adw.ActionRow()
        type_row.set_title("Exec Type")
        type_row.set_subtitle("Runs once at startup" if "once" in exec_type else "Runs every time")
        row.add_row(type_row)
        
        # Buttons
        btn_box = Gtk.Box(spacing=6)
        
        del_btn = Gtk.Button(label="Delete")
        del_btn.set_icon_name("user-trash-symbolic")
        del_btn.add_css_class("destructive-action")
        del_btn.connect('clicked', lambda b, ln=line_num: self.delete_program(ln))
        btn_box.append(del_btn)
        
        row.add_action(btn_box)
        
        self.programs_list.append(row)
        self.all_programs.append((row, f"{exec_type} {command}"))
    
    def add_program(self, button):
        dialog = Adw.Window()
        dialog.set_title("Add Autostart Program")
        dialog.set_default_size(500, 500)
        dialog.set_transient_for(self.get_root())
        dialog.set_modal(True)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        dialog.set_content(box)
        
        # Header
        header = Adw.HeaderBar()
        box.append(header)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content.set_margin_start(18)
        content.set_margin_end(18)
        content.set_margin_top(18)
        content.set_margin_bottom(18)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_child(content)
        box.append(scroll)
        
        # Step 1: Choose program
        content.append(Gtk.Label(label="<b>1. Choose a Program to Auto-start</b>", use_markup=True, xalign=0))
        
        prog_combo = Gtk.ComboBoxText()
        for cmd, desc in self.COMMON_PROGRAMS:
            prog_combo.append(cmd, desc)
        prog_combo.append("custom", "Custom command...")
        prog_combo.set_active(0)
        content.append(prog_combo)
        
        # Custom command entry
        custom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        custom_entry = Gtk.Entry()
        custom_entry.set_placeholder_text("e.g., firefox")
        custom_box.append(Gtk.Label(label="Custom Command:", xalign=0))
        custom_box.append(custom_entry)
        custom_box.set_visible(False)
        content.append(custom_box)
        
        def on_prog_changed(combo):
            custom_box.set_visible(combo.get_active_id() == "custom")
        prog_combo.connect('changed', on_prog_changed)
        
        # Step 2: Choose when to run
        content.append(Gtk.Label(label="<b>2. When Should It Run?</b>", use_markup=True, xalign=0))
        
        type_combo = Gtk.ComboBoxText()
        type_combo.append("exec-once", "Run once at startup (recommended for most programs)")
        type_combo.append("exec", "Run every time (for scripts that need to run repeatedly)")
        type_combo.set_active(0)
        content.append(type_combo)
        
        # Help text
        help_label = Gtk.Label(
            label="Tip: Use 'exec-once' for programs like status bars, wallpaper managers, etc.\nUse 'exec' only for scripts that need to run continuously.",
            wrap=True,
            xalign=0
        )
        help_label.add_css_class("dim-label")
        content.append(help_label)
        
        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.END)
        btn_box.set_margin_top(12)
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect('clicked', lambda b: dialog.close())
        btn_box.append(cancel_btn)
        
        add_btn = Gtk.Button(label="Add Program")
        add_btn.add_css_class("suggested-action")
        btn_box.append(add_btn)
        
        content.append(btn_box)
        
        def on_add(btn):
            exec_type = type_combo.get_active_id()
            
            if prog_combo.get_active_id() == "custom":
                command = custom_entry.get_text().strip()
            else:
                command = prog_combo.get_active_id()
            
            if command:
                self.save_program(f"{exec_type} = {command}\n")
                self.load_programs()
                dialog.close()
        
        add_btn.connect('clicked', on_add)
        dialog.present()
    
    def delete_program(self, line_num):
        if not self.execs_file.exists():
            return
        
        with open(self.execs_file, 'r') as f:
            lines = f.readlines()
        
        exec_count = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                if line.strip().startswith('exec'):
                    if exec_count == line_num:
                        lines[i] = ''
                        break
                    exec_count += 1
        
        with open(self.execs_file, 'w') as f:
            f.writelines(lines)
        
        self.load_programs()
    
    def save_program(self, exec_line):
        self.execs_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.execs_file, 'a') as f:
            f.write(exec_line)


class EnvironmentPage(SettingsPage):
    """Environment variables with list view"""
    
    # Common environment variables with descriptions
    COMMON_ENV_VARS = [
        ("GDK_BACKEND", ["wayland", "x11", "wayland,x11"], "GTK rendering backend - use wayland for native Wayland apps"),
        ("QT_QPA_PLATFORM", ["wayland", "xcb", "wayland;xcb"], "Qt platform - controls how Qt apps render"),
        ("SDL_VIDEODRIVER", ["wayland", "x11"], "SDL video backend - for games and SDL apps"),
        ("XCURSOR_THEME", ["Adwaita", "breeze_cursors", "Vanilla-DMZ"], "Mouse cursor theme name"),
        ("XCURSOR_SIZE", ["24", "32", "48"], "Mouse cursor size in pixels"),
        ("MOZ_ENABLE_WAYLAND", ["1"], "Enable Wayland for Firefox"),
        ("QT_QPA_PLATFORMTHEME", ["qt5ct", "gtk2", "gnome"], "Qt theme integration"),
    ]
    
    def __init__(self):
        super().__init__("Environment", "applications-system-symbolic")
        self.hypr_dir = Path.home() / ".config" / "hypr"
        self.env_file = self.find_config_file("env.conf")
        
        # Search bar
        search_bar = Gtk.SearchEntry()
        search_bar.set_placeholder_text("Search environment variables...")
        search_bar.connect('search-changed', self.on_search)
        self.append(search_bar)
        
        info = self.create_group("Environment Variables", "System environment configuration (requires Hyprland restart)")
        
        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_margin_top(6)
        toolbar.set_margin_bottom(6)
        
        add_btn = Gtk.Button(label="Add Variable")
        add_btn.set_icon_name("list-add-symbolic")
        add_btn.add_css_class("suggested-action")
        add_btn.connect('clicked', self.add_env_var)
        toolbar.append(add_btn)
        
        reload_btn = Gtk.Button(label="Reload")
        reload_btn.set_icon_name("view-refresh-symbolic")
        reload_btn.connect('clicked', lambda _: self.load_env_vars())
        toolbar.append(reload_btn)
        
        info.set_header_suffix(toolbar)
        
        # List of env vars
        self.env_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.env_list.set_margin_end(12)  # Add padding to avoid scrollbar overlap
        info.add(self.env_list)
        
        self.all_env_vars = []
        self.load_env_vars()
    
    def find_config_file(self, filename):
        paths = [
            self.hypr_dir / "hyprland" / filename,
            self.hypr_dir / "custom" / filename,
        ]
        for path in paths:
            if path.exists():
                return path
        return paths[0]
    
    def on_search(self, entry):
        search_text = entry.get_text().lower()
        for row, env_data in self.all_env_vars:
            visible = search_text in env_data.lower()
            row.set_visible(visible)
    
    def load_env_vars(self):
        while child := self.env_list.get_first_child():
            self.env_list.remove(child)
        
        self.all_env_vars = []
        
        if not self.env_file.exists():
            label = Gtk.Label(label="No env file found. Click 'Add Variable' to create one!")
            self.env_list.append(label)
            return
        
        with open(self.env_file, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            if stripped.startswith('env'):
                self.add_env_row(line, i)
    
    def add_env_row(self, env_line, line_num):
        row = Adw.ExpanderRow()
        
        parts = env_line.strip().split('=', 1)
        if len(parts) < 2:
            return
        
        env_rest = parts[1].strip()
        var_parts = env_rest.split(',', 1)
        
        if len(var_parts) >= 2:
            var_name = var_parts[0].strip()
            var_value = var_parts[1].strip()
            
            import html
            row.set_title(var_name)
            row.set_subtitle(html.escape(var_value[:80]))
            
            # Details in expanded view
            value_row = Adw.ActionRow()
            value_row.set_title("Value")
            value_row.set_subtitle(html.escape(var_value))
            row.add_row(value_row)
            
            # Add description if it's a known variable
            for env_name, values, desc in self.COMMON_ENV_VARS:
                if env_name == var_name:
                    desc_row = Adw.ActionRow()
                    desc_row.set_title("Description")
                    desc_row.set_subtitle(desc)
                    row.add_row(desc_row)
                    break
            
            # Buttons
            btn_box = Gtk.Box(spacing=6)
            
            del_btn = Gtk.Button(label="Delete")
            del_btn.set_icon_name("user-trash-symbolic")
            del_btn.add_css_class("destructive-action")
            del_btn.connect('clicked', lambda b, ln=line_num: self.delete_env_var(ln))
            btn_box.append(del_btn)
            
            row.add_action(btn_box)
            
            self.env_list.append(row)
            self.all_env_vars.append((row, f"{var_name} {var_value}"))
    
    def add_env_var(self, button):
        dialog = Adw.Window()
        dialog.set_title("Add Environment Variable")
        dialog.set_default_size(500, 550)
        dialog.set_transient_for(self.get_root())
        dialog.set_modal(True)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        dialog.set_content(box)
        
        # Header
        header = Adw.HeaderBar()
        box.append(header)
        
        # Content
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        content.set_margin_start(18)
        content.set_margin_end(18)
        content.set_margin_top(18)
        content.set_margin_bottom(18)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_child(content)
        box.append(scroll)
        
        # Step 1: Choose variable
        content.append(Gtk.Label(label="<b>1. Choose Environment Variable</b>", use_markup=True, xalign=0))
        
        var_combo = Gtk.ComboBoxText()
        for var_name, values, desc in self.COMMON_ENV_VARS:
            var_combo.append(var_name, f"{var_name} - {desc[:50]}...")
        var_combo.append("custom", "Custom variable...")
        var_combo.set_active(0)
        content.append(var_combo)
        
        # Custom name entry
        custom_name_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        custom_name_entry = Gtk.Entry()
        custom_name_entry.set_placeholder_text("e.g., MY_CUSTOM_VAR")
        custom_name_box.append(Gtk.Label(label="Variable Name:", xalign=0))
        custom_name_box.append(custom_name_entry)
        custom_name_box.set_visible(False)
        content.append(custom_name_box)
        
        # Step 2: Choose/enter value
        content.append(Gtk.Label(label="<b>2. Set Value</b>", use_markup=True, xalign=0))
        
        # Value combo (for common vars)
        value_combo = Gtk.ComboBoxText()
        content.append(value_combo)
        
        # Manual value entry
        content.append(Gtk.Label(label="Or enter custom value:", xalign=0))
        value_entry = Gtk.Entry()
        value_entry.set_placeholder_text("Enter value here")
        content.append(value_entry)
        
        # Description label
        desc_label = Gtk.Label(wrap=True, xalign=0)
        desc_label.add_css_class("dim-label")
        content.append(desc_label)
        
        def update_value_options(combo):
            var_id = combo.get_active_id()
            custom_name_box.set_visible(var_id == "custom")
            
            # Clear value combo
            value_combo.remove_all()
            
            if var_id != "custom":
                # Find matching common var
                for var_name, values, desc in self.COMMON_ENV_VARS:
                    if var_name == var_id:
                        for val in values:
                            value_combo.append_text(val)
                        value_combo.set_active(0)
                        desc_label.set_text(desc)
                        break
            else:
                desc_label.set_text("Enter a custom environment variable name and value")
        
        var_combo.connect('changed', update_value_options)
        update_value_options(var_combo)
        
        def on_value_selected(combo):
            if combo.get_active_text():
                value_entry.set_text(combo.get_active_text())
        value_combo.connect('changed', on_value_selected)
        
        # Help text
        help_label = Gtk.Label(
            label="Note: Environment variable changes require restarting Hyprland to take effect",
            wrap=True,
            xalign=0
        )
        help_label.add_css_class("warning")
        content.append(help_label)
        
        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.END)
        btn_box.set_margin_top(12)
        
        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect('clicked', lambda b: dialog.close())
        btn_box.append(cancel_btn)
        
        add_btn = Gtk.Button(label="Add Variable")
        add_btn.add_css_class("suggested-action")
        btn_box.append(add_btn)
        
        content.append(btn_box)
        
        def on_add(btn):
            # Get variable name
            if var_combo.get_active_id() == "custom":
                var_name = custom_name_entry.get_text().strip()
            else:
                var_name = var_combo.get_active_id()
            
            # Get value
            var_value = value_entry.get_text().strip()
            
            if var_name and var_value:
                self.save_env_var(f"env = {var_name},{var_value}\n")
                self.load_env_vars()
                dialog.close()
        
        add_btn.connect('clicked', on_add)
        dialog.present()
    
    def delete_env_var(self, line_num):
        if not self.env_file.exists():
            return
        
        with open(self.env_file, 'r') as f:
            lines = f.readlines()
        
        env_count = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                if line.strip().startswith('env'):
                    if env_count == line_num:
                        lines[i] = ''
                        break
                    env_count += 1
        
        with open(self.env_file, 'w') as f:
            f.writelines(lines)
        
        self.load_env_vars()
    
    def save_env_var(self, env_line):
        self.env_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.env_file, 'a') as f:
            f.write(env_line)


class WorkspacesPage(SettingsPage):
    """Workspace rules with text editor"""
    
    def __init__(self):
        super().__init__("Workspaces", "view-grid-symbolic")
        self.hypr_dir = Path.home() / ".config" / "hypr"
        self.ws_file = self.hypr_dir / "workspaces.conf"
        
        info = self.create_group("Workspace Rules", "Configure workspace behavior")
        
        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        toolbar.set_margin_top(6)
        toolbar.set_margin_bottom(6)
        
        save_btn = Gtk.Button(label="Save")
        save_btn.set_icon_name("document-save-symbolic")
        save_btn.connect('clicked', self.save_workspaces)
        toolbar.append(save_btn)
        
        reload_btn = Gtk.Button(label="Reload")
        reload_btn.set_icon_name("view-refresh-symbolic")
        reload_btn.connect('clicked', lambda _: self.load_workspaces())
        toolbar.append(reload_btn)
        
        info.set_header_suffix(toolbar)
        
        # Text editor
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_min_content_height(400)
        
        self.textview = Gtk.TextView()
        self.textview.set_monospace(True)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview.set_top_margin(12)
        self.textview.set_bottom_margin(12)
        self.textview.set_left_margin(12)
        self.textview.set_right_margin(12)
        
        scroll.set_child(self.textview)
        self.append(scroll)
        
        self.load_workspaces()
    
    def load_workspaces(self):
        if not self.ws_file.exists():
            self.textview.get_buffer().set_text("# Workspace rules\n# Example:\n# workspace = 1, monitor:DP-1\n")
            return
        
        with open(self.ws_file, 'r') as f:
            content = f.read()
        self.textview.get_buffer().set_text(content)
    
    def save_workspaces(self, button):
        buffer = self.textview.get_buffer()
        start, end = buffer.get_bounds()
        text = buffer.get_text(start, end, False)
        
        self.ws_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ws_file, 'w') as f:
            f.write(text)
        
        subprocess.run(['hyprctl', 'reload'], capture_output=True)


class HyprSettingsWindow(Adw.ApplicationWindow):
    """Main settings window"""
    
    def __init__(self, app):
        super().__init__(application=app, title="Hyprland Settings")
        self.set_default_size(1100, 750)
        
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)
        
        # Header bar
        header = Adw.HeaderBar()
        main_box.append(header)
        
        # Reload all settings button
        reload_btn = Gtk.Button(label="Refresh")
        reload_btn.set_icon_name("view-refresh-symbolic")
        reload_btn.set_tooltip_text("Reload all settings from Hyprland")
        reload_btn.connect('clicked', self.refresh_all)
        header.pack_start(reload_btn)
        
        # Open config folder button
        folder_btn = Gtk.Button()
        folder_btn.set_icon_name("folder-open-symbolic")
        folder_btn.set_tooltip_text("Open config folder")
        folder_btn.connect('clicked', self.open_config_folder)
        header.pack_end(folder_btn)
        
        # Create view switcher stack
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        
        # Add all pages
        self.pages = [
            GeneralPage(),
            DecorationPage(),
            AnimationsPage(),
            InputPage(),
            GesturesPage(),
            DwinLayoutPage(),
            MasterLayoutPage(),
            MiscPage(),
            WorkspacesPage(),
            EnvironmentPage(),
            AutostartPage(),
            RulesPage(),
            KeybindsPage(),
        ]
        
        for page in self.pages:
            scroll = Gtk.ScrolledWindow()
            scroll.set_vexpand(True)
            scroll.set_child(page)
            
            self.stack.add_titled(scroll, page.title, page.title)
            self.stack.get_page(scroll).set_icon_name(page.icon_name)
        
        # View switcher for sidebar
        sidebar = Gtk.StackSidebar()
        sidebar.set_stack(self.stack)
        sidebar.set_vexpand(True)
        sidebar.set_size_request(180, -1)
        
        # Paned layout
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_start_child(sidebar)
        paned.set_end_child(self.stack)
        paned.set_position(200)
        paned.set_vexpand(True)
        paned.set_shrink_start_child(False)
        paned.set_resize_start_child(False)
        
        main_box.append(paned)
        
        # Status bar
        self.status_bar = Gtk.Label(label="Ready • Changes apply instantly")
        self.status_bar.set_margin_top(6)
        self.status_bar.set_margin_bottom(6)
        self.status_bar.add_css_class("dim-label")
        main_box.append(self.status_bar)
    
    def refresh_all(self, button):
        """Refresh all settings by recreating pages"""
        self.status_bar.set_text("Refreshing settings...")
        # TODO: Implement refresh by reading current values
        GLib.timeout_add_seconds(1, lambda: self.status_bar.set_text("Ready • Changes apply instantly"))
    
    def open_config_folder(self, button):
        """Open config folder in file manager"""
        hypr_dir = Path.home() / ".config" / "hypr"
        subprocess.Popen(['xdg-open', str(hypr_dir)])


class HyprSettingsApp(Adw.Application):
    """Settings application"""
    
    def __init__(self):
        super().__init__(application_id='com.github.hyprsettings')
        
    def do_activate(self):
        win = HyprSettingsWindow(self)
        win.present()


if __name__ == '__main__':
    import sys
    app = HyprSettingsApp()
    sys.exit(app.run(None))
