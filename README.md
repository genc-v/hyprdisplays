# HyprDisplays

A simple GUI application for managing Hyprland display configurations.

## Features

- Visual display configuration for Hyprland
- Adjust resolution, refresh rate, position, scale, and rotation
- Live preview and apply changes
- Save configuration to `~/.config/hypr/hyprland.conf`

## Requirements

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

## Installation

Quick install to your system:

```bash
./install.sh
```

Then launch from your application menu or run `~/.local/share/hyprdisplays/hyprdisplays.py`

## Usage

Run directly without installing:

```bash
./hyprdisplays.py
```

## Controls

- **Refresh**: Reload current display configuration from Hyprland
- **Apply**: Apply changes immediately (temporary, lost on Hyprland restart)
- **Save to Config**: Save configuration to `hyprland.conf` and apply

Each monitor shows:

- **Mode**: Resolution and refresh rate selection
- **X/Y**: Position coordinates
- **Scale**: Display scaling factor
- **Rotation**: Display rotation (0°, 90°, 180°, 270°)
- **Enabled**: Toggle to enable/disable the display

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

