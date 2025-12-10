# Hyprland GUI Tools

Modern GUI applications for managing your Hyprland setup. Configure displays, settings, and more with an easy-to-use interface.

**📖 [Advanced Features](ADVANCED.md) | 📖 [Configuration Guide](CONFIGURATION.md)**

---

## What's Included

### 🖥️ HyprDisplays - Display Manager

Visual display configuration tool for Hyprland with automatic monitor detection and configuration memory.

### ⚙️ HyprSettings - Settings Manager

Complete settings application for managing all Hyprland configurations through a modern GTK4 interface.

---

## Quick Setup

### Step 1: Install Dependencies

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

### Step 2: Install Applications

Choose one option:

**Option A: Install Both (Recommended)**

```bash
./scripts/install.sh
./scripts/install_settings.sh
```

**Option B: Install Display Manager Only**

```bash
./scripts/install.sh
```

**Option C: Install Settings Manager Only**

```bash
./scripts/install_settings.sh
```

### Step 3: Launch

From your application menu:

- **"Hyprland Display Manager"** - Configure monitors
- **"Hyprland Settings"** - Configure Hyprland settings

Or from terminal:

```bash
hyprdisplays    # Display manager
hyprsettings    # Settings manager
```

---

## HyprDisplays - Display Manager

### Features

- **Visual Canvas**: Drag monitors to position them visually
- **Live Configuration**: Adjust resolution, refresh rate, scale, and rotation
- **Configuration Memory**: Automatically remembers settings for different monitor setups
- **Auto-Detection**: Recognizes physical monitors and auto-applies saved configurations
- **Safe Apply**: 15-second confirmation dialog prevents broken configurations
- **Identify Displays**: Show display numbers on each screen

### Basic Usage

1. **Launch HyprDisplays**

   ```bash
   hyprdisplays
   ```

2. **Configure Your Displays**

   - Drag monitors on canvas to position them
   - Adjust resolution, scale, and rotation for each monitor
   - Set one monitor as primary
   - Enable/disable displays as needed

3. **Save Configuration**
   - Click **"Apply & Save"**
   - Confirm the changes work (15-second dialog)
   - Configuration is saved to `~/.config/hypr/monitors.conf`

### Configuration Memory

HyprDisplays automatically remembers your settings for different monitor combinations:

- **Laptop only** gets its own saved configuration
- **Laptop + work monitor** gets its own saved configuration
- **Laptop + home monitor** gets its own saved configuration (even if using same port!)
- **Desktop with 3 monitors** gets its own saved configuration

**How it works:**

1. Configure your displays and click "Apply & Save"
2. HyprDisplays identifies monitors by physical details (make, model, serial)
3. Next time you connect the same physical monitors, configuration auto-applies
4. Different monitors on the same port (HDMI-A-1 at work vs home) are recognized separately

**Configurations stored in:** `~/.config/hypr/hyprdisplays_profiles.json`

### Controls

- **Refresh**: Reload current display configuration
- **Apply & Save**: Apply changes and save to monitors.conf
- **Identify Displays**: Show display numbers on screens
- **Drag monitors**: Reposition in visual canvas
- **Scroll**: Zoom in/out on canvas

---

## HyprSettings - Settings Manager

### Features

- **Modern Interface**: GTK4/libadwaita design matching Fedora
- **Live Reload**: Changes apply instantly with `hyprctl reload`
- **Multiple Categories**: General, Animations, Input, Workspaces, Environment, Autostart, Rules, Keybinds
- **Smart Detection**: Automatically finds configs in `hyprland/` and `custom/` directories
- **Safe Editing**: Preserves comments and formatting

### Settings Categories

#### General

- Border size, gaps, layout options
- Configure window appearance

#### Animations

- Enable/disable animations
- Animation speed control

#### Input

- Mouse sensitivity and scrolling
- Keyboard layout and variant
- Touchpad settings

#### Workspaces

- Full text editor for workspace rules
- Multi-monitor workspace configuration

#### Environment

- Edit environment variables
- Configure XDG directories

#### Autostart

- Programs to run on startup
- exec-once commands

#### Rules

- Window-specific behavior
- Floating, fullscreen, workspace rules

#### Keybinds

- Keyboard shortcut configuration
- Full text editor for complex binds

### Basic Usage

1. **Launch HyprSettings**

   ```bash
   hyprsettings
   ```

2. **Navigate Settings**

   - Use sidebar to switch between categories
   - Adjust settings with spinners, switches, or text editors
   - Changes auto-save

3. **Reload Configuration**
   - Click **"Reload Config"** button
   - Or changes apply automatically via `hyprctl reload`

### Configuration Files Managed

| File              | Category             | Location                                |
| ----------------- | -------------------- | --------------------------------------- |
| `general.conf`    | General & Animations | `~/.config/hypr/hyprland/` or `custom/` |
| `env.conf`        | Environment          | `~/.config/hypr/hyprland/` or `custom/` |
| `execs.conf`      | Autostart            | `~/.config/hypr/hyprland/` or `custom/` |
| `keybinds.conf`   | Keybinds             | `~/.config/hypr/hyprland/` or `custom/` |
| `rules.conf`      | Rules                | `~/.config/hypr/hyprland/` or `custom/` |
| `workspaces.conf` | Workspaces           | `~/.config/hypr/`                       |
| `monitors.conf`   | Displays             | Managed by HyprDisplays                 |

---

## Common Tasks

### Configure Dual Monitors

1. Open HyprDisplays
2. Drag monitor rectangles to position them
3. Adjust resolution and scale for each
4. Click "Apply & Save"
5. Configuration automatically saves for this monitor combination

### Adjust Window Gaps

1. Open HyprSettings
2. Go to "General" section
3. Use spin buttons for "Inner Gaps" and "Outer Gaps"
4. Changes apply immediately

### Add Keyboard Shortcut

1. Open HyprSettings
2. Go to "Keybinds" section
3. Edit the text to add your bind:
   ```
   bind = SUPER, T, exec, kitty
   ```
4. Changes auto-save and reload

### Add Autostart Program

1. Open HyprSettings
2. Go to "Autostart" section
3. Add line like:
   ```
   exec-once = waybar
   ```

---

## Tips & Best Practices

**Backup Your Configs**

```bash
cp -r ~/.config/hypr ~/.config/hypr.backup
```

**Open Config Folder**  
Both apps have an "Open Config Folder" button to edit files manually in your preferred text editor.

**Safe Testing**  
When applying display changes, you have 15 seconds to confirm they work. If you don't respond, the previous configuration is automatically restored.

**Live Preview**  
HyprSettings shows changes in real-time. Test different settings quickly to find what works best.

**Manual Editing**  
You can mix GUI and manual config editing. Both tools preserve your comments and formatting.

---

## Advanced Features

For power users, check out the [Advanced Features Guide](ADVANCED.md) which covers:

- **Background Daemon**: Automatic monitor detection without GUI
- **Physical Monitor Identification**: How monitors are uniquely identified
- **Configuration Profiles**: Managing multiple saved configurations
- **Systemd Integration**: Running as a background service
- **Command Line Options**: Advanced usage and debugging

---

## Configuration Details

For detailed information about config structure and files, see the [Configuration Guide](CONFIGURATION.md) which covers:

- Hyprland config file structure
- How HyprSettings integrates with your configs
- Manual editing alongside GUI tools
- Troubleshooting configuration issues
- Best practices for config management

---

## Troubleshooting

### Apps Won't Start

Make sure dependencies are installed:

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

### Changes Not Applying

Click the "Reload Config" button or run:

```bash
hyprctl reload
```

### Display Configuration Reverts

This is the safety feature! If you don't confirm changes within 15 seconds, the previous configuration is automatically restored. Click "Keep Changes" in the confirmation dialog.

### Config File Not Found

HyprSettings looks for configs in:

1. `~/.config/hypr/hyprland/`
2. `~/.config/hypr/custom/`

Make sure your config files exist in one of these locations.

### Monitor Not Auto-Detecting

Configuration memory requires the monitor to be physically connected when you save. Make sure you:

1. Connected the monitor
2. Configured displays
3. Clicked "Apply & Save"
4. Saw the message "Config saved for X monitor(s) - Will auto-load on reconnect!"

---

## Uninstall

To remove the applications:

```bash
./scripts/uninstall.sh
rm ~/.local/share/applications/hyprsettings.desktop
```

To also remove saved configurations:

```bash
rm ~/.config/hypr/monitors.conf
rm ~/.config/hypr/hyprdisplays_profiles.json
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
