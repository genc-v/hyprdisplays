# Hyprland GUI Tools

Modern GUI applications for managing your Hyprland setup. Configure displays, settings, and more with an easy-to-use interface.

**📖 [Full Documentation](docs/README.md) | [Advanced Features](docs/ADVANCED.md) | [Configuration Guide](docs/CONFIGURATION.md)**

---

## What's Included

### 🖥️ HyprDisplays - Display Manager
Visual display configuration tool for Hyprland with automatic monitor detection and configuration memory.

### ⚙️ HyprSettings - Settings Manager  
Complete settings application for managing all Hyprland configurations through a modern GTK4 interface.

---

## Quick Start

### 1. Install Dependencies

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

### 2. Install Applications

**Install Both (Recommended)**
```bash
./scripts/install.sh
./scripts/install_settings.sh
```

**Or Install Individually**
```bash
./scripts/install.sh              # Display Manager only
./scripts/install_settings.sh     # Settings Manager only
```

### 3. Launch

From application menu:
- **"Hyprland Display Manager"**
- **"Hyprland Settings"**

Or from terminal:
```bash
hyprdisplays    # Display manager
hyprsettings    # Settings manager
```

---

## Features

### HyprDisplays
- Visual canvas for monitor positioning
- Auto-detection of physical monitors
- Configuration memory for different setups
- Safe apply with 15-second confirmation
- Background daemon for automatic switching

### HyprSettings
- Modern GTK4/libadwaita interface
- General settings (borders, gaps, animations)
- Input configuration (mouse, keyboard, touchpad)
- Workspace rules and environment variables
- Autostart programs and window rules
- Keyboard shortcuts editor
- Live reload with `hyprctl`

---

## Documentation

📖 **[Full Documentation](docs/README.md)** - Complete setup guide with detailed usage instructions

📖 **[Advanced Features](docs/ADVANCED.md)** - Background daemon, systemd integration, and power-user features

📖 **[Configuration Guide](docs/CONFIGURATION.md)** - Config file structure and integration details

---

## Project Structure

```
hyprdisplays/
├── docs/          # Documentation
├── src/           # Python source code
├── desktop/       # Desktop entry files
├── scripts/       # Installation scripts
└── assets/        # Images and resources
```

---

## Requirements

- Hyprland window manager
- Python 3
- GTK4
- libadwaita  
- `hyprctl` (included with Hyprland)

**Tested on:** Fedora Linux with Hyprland

---

## License

MIT License - Feel free to use and modify!

---

**Made for the Hyprland community** 🎉
