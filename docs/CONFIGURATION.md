git init
git add .
git commit -m "Initial Hyprland config"
git diff # See what changed
git add .
git commit -m "Adjusted gaps and monitor layout"
git init
git add .
git commit -m "Config backup $(date +%Y-%m-%d)"
hyprctl reload
general {

# Configuration

Where files live and how the apps touch them.

---

## Paths at a glance

```
~/.config/hypr/
├── hyprland.conf          # main file, usually sources the rest
├── monitors.conf          # written by HyprDisplays
├── hyprdisplays_profiles.json  # display profiles
├── hyprland/              # preferred folder for HyprSettings
│   ├── general.conf
│   ├── env.conf
│   ├── execs.conf
│   ├── keybinds.conf
│   ├── rules.conf
│   └── workspaces.conf
└── custom/                # fallback folder if hyprland/ is missing
```

HyprSettings looks in `hyprland/` first, then `custom/`. It creates missing files when you save.

## How the apps write

- HyprDisplays rewrites `monitors.conf` and stores profiles in `hyprdisplays_profiles.json`.
- HyprSettings edits only the values you change; comments stay. When you save, it runs `hyprctl reload`.

## Minimal sourcing block

Add something like this in `hyprland.conf` if it is not there yet:

```conf
source = ~/.config/hypr/monitors.conf
source = ~/.config/hypr/hyprland/general.conf
source = ~/.config/hypr/hyprland/env.conf
source = ~/.config/hypr/hyprland/execs.conf
source = ~/.config/hypr/hyprland/keybinds.conf
source = ~/.config/hypr/hyprland/rules.conf
source = ~/.config/hypr/workspaces.conf
```

## Quick tips

- Keep manual changes; both apps preserve comments and spacing.
- If a file is missing, open the app and toggle a value; it will create the file.
- Stuck reload? Run `hyprctl reload` and check `hyprctl logs` for errors.
- Back up configs with `cp -r ~/.config/hypr ~/.config/hypr.backup` before big edits.

# Or check systemd journal

journalctl --user -u hyprland -n 50

````

### 6. Validate Syntax

Before making major changes:

```bash
# Test current config
hyprctl reload

# If successful, make changes
# If errors, fix them first
````

---

## Troubleshooting

### Changes Not Applying

**Solution 1: Reload Config**

```bash
hyprctl reload
```

Or click "Reload Config" button in HyprSettings.

**Solution 2: Check Syntax**

```bash
hyprctl reload
# Look for error messages
```

**Solution 3: Check File Locations**

Make sure files exist in correct locations:

```bash
ls -la ~/.config/hypr/hyprland/
ls -la ~/.config/hypr/custom/
ls -la ~/.config/hypr/monitors.conf
```

### HyprSettings Can't Find Config Files

**Create the directories:**

```bash
mkdir -p ~/.config/hypr/hyprland
mkdir -p ~/.config/hypr/custom
```

**Or let HyprSettings create them:**

1. Open HyprSettings
2. Navigate to any category
3. Make a change
4. File is automatically created

### Monitor Config Not Persisting

**Check monitors.conf is sourced:**

In `~/.config/hypr/hyprland.conf`:

```bash
source = ~/.config/hypr/monitors.conf
```

**Verify monitors.conf exists:**

```bash
cat ~/.config/hypr/monitors.conf
```

### Profiles Not Auto-Loading

**Check profile file exists:**

```bash
cat ~/.config/hypr/hyprdisplays_profiles.json
```

**Verify you saved the configuration:**

1. Open HyprDisplays
2. Check status bar for "Saved config available" message
3. If not, configure and click "Apply & Save"

**Check daemon is running (if using):**

```bash
systemctl --user status hyprdisplays-daemon
```

### Conflicts Between Tools

**HyprDisplays and HyprSettings don't conflict!**

- HyprDisplays: Manages `monitors.conf` only
- HyprSettings: Manages other config files

**If you think there's a conflict:**

1. Check which file has the issue:

   ```bash
   cat ~/.config/hypr/monitors.conf
   cat ~/.config/hypr/hyprland/general.conf
   ```

2. Verify correct tool is editing correct file:
   - Display settings → Use HyprDisplays
   - Everything else → Use HyprSettings or manual editing

### Manual Edits Overwritten

**HyprDisplays:**

- **Always** overwrites `monitors.conf` when you click "Apply & Save"
- This is intentional - use HyprDisplays for all monitor config
- Don't manually edit `monitors.conf` if using HyprDisplays

**HyprSettings:**

- Preserves comments and formatting
- Only updates specific values
- Should not overwrite other settings
- If it does, please report as a bug

### Config Syntax Errors

**Check with hyprctl:**

```bash
hyprctl reload
```

**Common errors:**

```conf
# Wrong: Missing equals sign
general {
    border_size 2
}

# Right:
general {
    border_size = 2
}

# Wrong: Missing comma in color
col.active_border = rgba(33ccffee

# Right:
col.active_border = rgba(33ccffee)
```

**Fix in text editor:**

```bash
$EDITOR ~/.config/hypr/hyprland/general.conf
```

Then reload:

```bash
hyprctl reload
```

---

## Configuration Examples

### Minimal Setup

```bash
# ~/.config/hypr/hyprland.conf
source = ~/.config/hypr/monitors.conf
source = ~/.config/hypr/hyprland/general.conf
```

```conf
# ~/.config/hypr/hyprland/general.conf
general {
    border_size = 2
    gaps_in = 5
    gaps_out = 10
}

input {
    kb_layout = us
    sensitivity = 0.0
}
```

### Complete Setup

```bash
# ~/.config/hypr/hyprland.conf
# Monitor configuration (HyprDisplays)
source = ~/.config/hypr/monitors.conf

# General settings (HyprSettings)
source = ~/.config/hypr/hyprland/general.conf

# Environment variables (HyprSettings)
source = ~/.config/hypr/hyprland/env.conf

# Keybinds (Manual + HyprSettings)
source = ~/.config/hypr/hyprland/keybinds.conf

# Window rules (Manual + HyprSettings)
source = ~/.config/hypr/hyprland/rules.conf

# Autostart programs (HyprSettings)
source = ~/.config/hypr/hyprland/execs.conf

# Workspace configuration (HyprSettings)
source = ~/.config/hypr/workspaces.conf

# Colors (Manual only)
source = ~/.config/hypr/hyprland/colors.conf
```

This gives you:

- Clean separation of concerns
- Easy editing with GUI tools
- Flexibility for manual advanced config
- Version control friendly structure

---

**[← Back to Main README](README.md)**
