# HyprDisplays - Automatic Monitor Configuration

## Installation

```bash
./install.sh
```

This installs everything you need, including the background daemon.

## First Time Setup

1. Open "Hyprland Display Manager" from your app menu
2. Configure your laptop-only setup, click "Apply & Save"
3. Connect work monitor, configure it, click "Apply & Save"
4. Connect home monitor, configure it, click "Apply & Save"

## Done!

From now on, when you plug/unplug monitors, the correct configuration 
automatically applies within 3 seconds. No manual steps needed.

The background daemon recognizes your Dell work monitor vs Samsung home 
monitor even though both use HDMI-A-1.

## Uninstall

```bash
./uninstall.sh
```

Removes everything (optionally keeps your saved profiles).

## Files Created

- `hyprdisplays-daemon.py` - Background monitoring service
- `INSTALL_README.txt` - Detailed installation guide
- Updated `install.sh` - Now includes daemon installation
- Updated `uninstall.sh` - Now includes daemon removal
