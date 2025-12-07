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
