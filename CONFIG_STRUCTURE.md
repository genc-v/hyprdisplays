# Hyprland Configuration Structure

This document shows how HyprSettings integrates with your Hyprland configuration.

## Your Current Config Structure

```
~/.config/hypr/
├── custom/
│   ├── env.conf          ← Environment variables
│   ├── execs.conf        ← Autostart programs
│   ├── general.conf      ← General settings, borders, gaps
│   ├── keybinds.conf     ← Keyboard shortcuts
│   ├── rules.conf        ← Window rules
│   └── scripts/
├── hyprland/
│   ├── colors.conf       ← (Not edited by HyprSettings)
│   ├── env.conf          ← Alternative env location
│   ├── execs.conf        ← Alternative execs location
│   ├── general.conf      ← Alternative general location
│   ├── keybinds.conf     ← Alternative keybinds location
│   ├── rules.conf        ← Alternative rules location
│   └── scripts/
├── hyprland.conf         ← Main config (sources other files)
├── monitors.conf         ← Display config (managed by HyprDisplays)
└── workspaces.conf       ← Workspace rules
```

## How HyprSettings Works

HyprSettings automatically detects which directory structure you use:

1. **Checks `hyprland/` directory first** for config files
2. **Falls back to `custom/` directory** if not found in hyprland/
3. **Edits files in-place** - preserves your comments and formatting
4. **Auto-reloads** configuration after changes via `hyprctl reload`

## Supported Config Files

| File              | Category             | What It Controls                  |
| ----------------- | -------------------- | --------------------------------- |
| `general.conf`    | General & Animations | Borders, gaps, animations, layout |
| `env.conf`        | Environment          | Environment variables             |
| `execs.conf`      | Autostart            | Programs to run on startup        |
| `keybinds.conf`   | Keybinds             | Keyboard shortcuts                |
| `rules.conf`      | Rules                | Window rules and behavior         |
| `workspaces.conf` | Workspaces           | Workspace configuration           |

## Config File Format

HyprSettings can parse and edit Hyprland config format:

```conf
# General settings
general {
    border_size = 2
    gaps_in = 5
    gaps_out = 10
    pseudotile = false
}

# Animations
animations {
    enabled = true
    speed = 1.0
}

# Input settings
input {
    kb_layout = us
    sensitivity = 0.0
    natural_scroll = true
    tap-to-click = true
}
```

## Manual Editing

You can still manually edit your config files! HyprSettings:

- ✅ Preserves comments
- ✅ Maintains formatting
- ✅ Works alongside manual edits
- ✅ Doesn't overwrite unmanaged sections

Use the **"Open Config Folder"** button in HyprSettings to edit files in your favorite text editor.

## Best Practices

1. **Backup first**: `cp -r ~/.config/hypr ~/.config/hypr.backup`
2. **Use HyprSettings for common settings**: Borders, gaps, animations, etc.
3. **Use text editor for advanced configs**: Complex keybinds, custom rules
4. **Test changes**: Click "Reload Config" to test without restarting Hyprland
5. **Check syntax**: If reload fails, check Hyprland logs with `hyprctl logs`

## Integration with HyprDisplays

- **HyprDisplays** manages `monitors.conf`
- **HyprSettings** manages general configuration files
- Both work together seamlessly
- No conflicts - they edit different files

## Troubleshooting

### Changes not applying?

Click the **"Reload Config"** button or run:

```bash
hyprctl reload
```

### Config file not found?

Make sure your config files exist in either:

- `~/.config/hypr/hyprland/`
- `~/.config/hypr/custom/`

### Want to see what changed?

Use git to track your config:

```bash
cd ~/.config/hypr
git init
git add .
git commit -m "Before HyprSettings changes"
```

Then you can see changes with `git diff`.
