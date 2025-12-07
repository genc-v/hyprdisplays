# Hyprland Settings

A modern, beautiful GUI settings application for Hyprland window manager on Fedora Linux.

![Settings App](https://img.shields.io/badge/Hyprland-Settings-5e81ac?style=for-the-badge&logo=wayland)

## Features

✨ **Clean Modern Interface** - Built with GTK4 and libadwaita for a native Fedora look  
⚙️ **Comprehensive Settings** - Edit all your Hyprland configurations without touching files  
🎨 **Multiple Categories**:

- **General** - Borders, gaps, layout settings
- **Animations** - Control animation speed and behavior
- **Input** - Mouse, keyboard, touchpad configuration
- **Workspaces** - Workspace rules and behavior
- **Environment** - Environment variables
- **Autostart** - Programs to launch on startup
- **Rules** - Window rules and behavior
- **Keybinds** - Keyboard shortcuts

🔄 **Live Reload** - Changes apply instantly with `hyprctl reload`  
📁 **Easy Access** - Open config folder directly from the app

## Screenshots

The app features:

- Sidebar navigation for easy category switching
- Clean preference rows with descriptions
- Text editors for advanced configurations
- Instant config reload

## Installation

### Quick Install

```bash
./install_settings.sh
```

This will:

- Install the desktop entry to `~/.local/share/applications/`
- Make the script executable
- Update desktop database

### Manual Installation

1. Make the script executable:

```bash
chmod +x hyprsettings.py
```

2. Run directly:

```bash
./hyprsettings.py
```

3. Or copy to a system path:

```bash
sudo cp hyprsettings.py /usr/local/bin/hyprsettings
sudo chmod +x /usr/local/bin/hyprsettings
```

## Usage

### Launch from Application Menu

After installation, search for "Hyprland Settings" in your application launcher.

### Launch from Terminal

```bash
./hyprsettings.py
```

### Configure Your Settings

The app automatically detects your Hyprland config structure at `~/.config/hypr/`:

```
.config/hypr/
├── custom/
│   ├── env.conf
│   ├── execs.conf
│   ├── general.conf
│   ├── keybinds.conf
│   └── rules.conf
├── hyprland/
│   ├── colors.conf
│   ├── env.conf
│   ├── execs.conf
│   ├── general.conf
│   ├── keybinds.conf
│   └── rules.conf
└── workspaces.conf
```

The app will automatically look in both `hyprland/` and `custom/` directories for your config files.

## Configuration Files Managed

| File              | Description                                   |
| ----------------- | --------------------------------------------- |
| `general.conf`    | General appearance, borders, gaps, animations |
| `env.conf`        | Environment variables                         |
| `execs.conf`      | Autostart programs                            |
| `keybinds.conf`   | Keyboard shortcuts                            |
| `rules.conf`      | Window rules                                  |
| `workspaces.conf` | Workspace configuration                       |

## Requirements

- Fedora Linux (or any distro with GTK4/libadwaita)
- Hyprland window manager
- Python 3
- GTK4
- libadwaita
- `hyprctl` (comes with Hyprland)

### Install Dependencies (Fedora)

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

## Features in Detail

### General Settings

- **Border Size** - Adjust window border width
- **Gaps** - Configure gaps between windows and screen edges
- **Layout Options** - Pseudo-tiling and other layout features

### Animations

- **Enable/Disable** - Turn animations on or off
- **Speed Control** - Adjust animation speed multiplier

### Input Settings

- **Mouse Sensitivity** - Fine-tune pointer speed
- **Natural Scroll** - Toggle reverse scrolling
- **Tap to Click** - Enable touchpad tapping
- **Keyboard Layout** - Configure keyboard layout and variant

### Advanced Editors

For complex configurations (keybinds, rules, workspaces), the app provides full-featured text editors with:

- Syntax highlighting
- Monospace font
- Auto-save on changes
- Immediate reload

## Tips

💡 **Instant Apply** - Most settings apply immediately via `hyprctl reload`  
💡 **Backup First** - Consider backing up your configs before making changes  
💡 **Open Config Folder** - Use the folder button to edit files in your favorite editor  
💡 **Reload Button** - Use the reload button to apply manual config changes

## Troubleshooting

### App won't start

Make sure you have all dependencies installed:

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

### Changes not applying

Click the "Reload Config" button or run:

```bash
hyprctl reload
```

### Config file not found

The app looks in:

1. `~/.config/hypr/hyprland/[file].conf`
2. `~/.config/hypr/custom/[file].conf`

Make sure your config files exist in one of these locations.

## Contributing

Found a bug or have a feature request? Feel free to open an issue!

## License

MIT License - Feel free to use and modify!

## Related Projects

- **HyprDisplays** - Display manager for Hyprland (included in this repo)
- **Hyprland** - Dynamic tiling Wayland compositor

---

**Made with ❤️ for the Hyprland community**
