# Hyprland GUI Tools

Modern GUI applications for managing your Hyprland setup on Fedora Linux.

**📖 [Quick Start Guide](QUICKSTART.md) | 📖 [Detailed Settings Guide](SETTINGS_README.md) | 📖 [Config Structure](CONFIG_STRUCTURE.md)**

---

## 🖥️ HyprDisplays - Display Manager

Visual display configuration tool for Hyprland monitors.

### Features

- Visual display configuration for Hyprland
- Adjust resolution, refresh rate, position, scale, and rotation
- Live preview and apply changes
- Save configuration to `~/.config/hypr/monitors.conf`

## ⚙️ HyprSettings - Settings Manager

Complete settings application for all Hyprland configurations.

### Features

- Modern GTK4/libadwaita interface
- Edit general settings (borders, gaps, layout)
- Configure animations
- Input settings (mouse, keyboard, touchpad)
- Workspace configuration
- Environment variables
- Autostart programs
- Window rules
- Keyboard shortcuts
- Live reload with `hyprctl`

## Requirements

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

## Installation

### Install Display Manager
```bash
./install.sh
```

### Install Settings Manager
```bash
./install_settings.sh
```

Both will be available in your application menu.

## Usage

### HyprDisplays (Display Manager)
Run directly:
```bash
./hyprdisplays.py
```

Or from application menu: "Hyprland Display Manager"

### HyprSettings (Settings Manager)
Run directly:
```bash
./hyprsettings.py
```

Or from application menu: "Hyprland Settings"

## HyprDisplays Controls

- **Refresh**: Reload current display configuration from Hyprland
- **Apply & Save**: Apply changes and save to monitors.conf
- **Identify Displays**: Show display numbers on each screen
- **Drag monitors** in the visual canvas to reposition
- **Scroll** to zoom in/out on the canvas

Each monitor shows:

- **Mode**: Resolution and refresh rate selection
- **Scale**: Display scaling factor
- **Rotation**: Display rotation (0°, 90°, 180°, 270°)
- **Enabled**: Toggle to enable/disable the display
- **Primary**: Set as primary monitor

## HyprSettings Features

Navigate through settings categories:

### General
- Border size, gaps, layout options

### Animations  
- Enable/disable, speed control

### Input
- Mouse sensitivity, natural scroll, tap-to-click
- Keyboard layout and variant

### Workspaces
- Edit workspace configuration directly

### Environment
- Edit environment variables

### Autostart
- Configure programs to launch on startup

### Rules
- Window-specific rules and behavior

### Keybinds
- Keyboard shortcuts configuration

## Confirmation Dialog

When you apply display configuration changes (either via "Apply" or "Save to Config"), a confirmation dialog will appear asking you to verify that the new settings work correctly.

**Key Features:**

- **15-second timeout**: You have 15 seconds to confirm the changes
- **Automatic revert**: If you don't respond or click "Revert", the previous configuration will be automatically restored
- **Safe testing**: This prevents you from getting stuck with a broken display configuration that you can't see
- **Config file protection**: If you used "Save to Config", the config file will also be reverted if you reject the changes

**How it works:**

1. Click "Apply" or "Save to Config"
2. The new configuration is applied immediately
3. A dialog appears asking "Keep Display Configuration?"
4. You have 15 seconds to click "Keep Changes" or "Revert"
5. If you don't respond in time, it automatically reverts to the previous configuration

This is especially useful when:

- Testing new refresh rates or resolutions
- Adjusting monitor positions
- Changing scaling that might make text unreadable
- Any change that could potentially make your display unusable
