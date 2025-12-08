# 🚀 Quick Start Guide

Get started with Hyprland GUI Tools in 2 minutes!

## Step 1: Install Dependencies

```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

## Step 2: Install Applications

Choose one:

### Option A: Install Both (Recommended)

```bash
./launcher.sh
# Then select option 3
```

### Option B: Install Individually

```bash
# Display manager only
./install.sh

# Settings manager only
./install_settings.sh
```

## Step 3: Launch

From your application menu:

- **"Hyprland Display Manager"** - Configure monitors
- **"Hyprland Settings"** - Configure Hyprland settings

Or from terminal:

```bash
./hyprdisplays.py   # Display manager
./hyprsettings.py   # Settings manager
```

## What Each App Does

### 🖥️ HyprDisplays (Display Manager)

Use this to:

- ✅ Configure monitor resolution and refresh rate
- ✅ Position monitors (drag and drop in visual canvas)
- ✅ Set scaling and rotation
- ✅ Set primary monitor
- ✅ Enable/disable displays

**Saves to:** `~/.config/hypr/monitors.conf`

### ⚙️ HyprSettings (Settings Manager)

Use this to:

- ✅ Configure borders and gaps
- ✅ Adjust animations
- ✅ Set up input devices (mouse, keyboard, touchpad)
- ✅ Edit environment variables
- ✅ Manage autostart programs
- ✅ Configure window rules
- ✅ Edit keyboard shortcuts
- ✅ Set up workspaces

**Edits:** Various config files in `~/.config/hypr/`

## Quick Tips

💡 **First time?** Start with HyprSettings → General to adjust borders and gaps  
💡 **Multiple monitors?** Use HyprDisplays to arrange them visually  
💡 **Want custom keybinds?** HyprSettings → Keybinds has a full editor  
💡 **Changes not working?** Click "Reload Config" button in either app  
💡 **Backup your configs** before making major changes:

```bash
cp -r ~/.config/hypr ~/.config/hypr.backup
```

## Common Tasks

### Add a Keybind

1. Open HyprSettings
2. Go to "Keybinds" section
3. Edit the text to add your bind:
   ```
   bind = SUPER, T, exec, kitty
   ```
4. Changes auto-save and reload

### Adjust Window Gaps

1. Open HyprSettings
2. Go to "General" section
3. Use the spin buttons for "Inner Gaps" and "Outer Gaps"
4. Changes apply immediately

### Configure Dual Monitors

1. Open HyprDisplays
2. Drag the monitor rectangles to position them
3. Adjust resolution/scale for each
4. Click "Apply & Save"

### Add Autostart Program

1. Open HyprSettings
2. Go to "Autostart" section
3. Add line like:
   ```
   exec-once = waybar
   ```

## Need Help?

- 📖 Read [SETTINGS_README.md](SETTINGS_README.md) for detailed HyprSettings info
- 📖 Read [CONFIG_STRUCTURE.md](CONFIG_STRUCTURE.md) to understand config layout
- 📖 Check [README.md](README.md) for complete documentation
- 🐛 Found a bug? Open an issue on GitHub

## Uninstall

To remove:

```bash
./uninstall.sh
rm ~/.local/share/applications/hyprsettings.desktop
```

---

**Enjoy your Hyprland setup! 🎉**
