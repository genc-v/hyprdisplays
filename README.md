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
- **Auto-remember configurations** - Remembers your settings for different monitor setups
- **Automatic switching** - Detects when monitors are connected/disconnected and applies the correct configuration
- **Configuration history** - Keeps track of your display configurations

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

### Configuration Memory

HyprDisplays now automatically remembers your configuration for different monitor setups:

- **Automatic Detection**: When you connect or disconnect monitors, HyprDisplays detects the change
- **Physical Monitor ID**: Uses monitor make, model, and serial to uniquely identify each monitor
- **Same Port, Different Monitors**: HDMI-A-1 at work vs. HDMI-A-1 at home are recognized as different setups
- **Smart Profiles**: Your configuration is saved based on which physical monitors are connected
- **Auto-Apply**: When you reconnect a monitor setup you've used before, your saved configuration is automatically applied
- **Configuration History**: Keeps a history of up to 50 recent configurations

**How it works:**

1. Configure your displays as you like them
2. Click "Apply & Save" to save the configuration
3. HyprDisplays identifies your monitors by their physical details (make/model/serial)
4. Next time you connect the same physical monitors, your configuration is automatically restored
5. Different monitor combinations (even on the same ports) get their own saved configurations

**Example scenarios:**

- **Laptop only**: Configure single display settings, saved automatically
- **Laptop + work monitor (Dell on HDMI-A-1)**: Configure and save → remembers this specific monitor
- **Laptop + home monitor (Samsung on HDMI-A-1)**: Configure and save → remembers this different monitor
- **Desktop with 3 monitors**: Configure triple monitor setup, saved independently

**Key feature**: Even if you use the same port (like HDMI-A-1) for different monitors at work and home, HyprDisplays recognizes which physical monitor is connected and applies the correct configuration!

Your configurations are stored in `~/.config/hypr/hyprdisplays_profiles.json`

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
