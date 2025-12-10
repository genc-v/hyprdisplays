# Quick Start: Configuration Memory

HyprDisplays now automatically remembers your monitor configurations!

## What's New?

- **Automatic saving**: Your display configuration is saved based on which monitors are connected
- **Smart switching**: When you connect/disconnect monitors, your saved configuration is automatically applied
- **No manual work**: Just configure once, and HyprDisplays remembers forever

## How to Use

### First Time Setup

1. **Configure your displays**

   - Open HyprDisplays
   - Arrange monitors, set resolution, scale, etc.
   - Click "Apply & Save"

2. **Done!**
   - HyprDisplays saved your configuration for this monitor setup
   - Next time you use the same monitors, it will automatically load

### Daily Use

**Nothing to do!** HyprDisplays automatically:

- Detects when you connect/disconnect monitors
- Loads the correct configuration
- Applies your saved settings

### Examples

**Laptop user connecting to external monitor:**

```
1. Laptop only → saved config A
2. Connect external monitor → HyprDisplays detects change
3. Configure dual setup → click "Apply & Save" → saved config B
4. Disconnect external → automatically switches back to config A
5. Reconnect external → automatically switches to config B
```

**Desktop user with varying monitors:**

```
1. One monitor → saved config for 1 monitor
2. Add second monitor → configure and save → saved config for 2 monitors
3. Add third monitor → configure and save → saved config for 3 monitors
4. Remove any monitor → automatically uses correct saved config
```

## Status Messages

Watch the status bar at the bottom:

- **"Loaded X display(s) - Saved config available"** - You have a saved config for this setup
- **"Auto-applied saved config for X monitor(s)"** - Your saved config was automatically loaded
- **"Config saved for X monitor(s) - Will auto-load on reconnect!"** - Configuration saved successfully

## File Locations

- **Profiles**: `~/.config/hypr/hyprdisplays_profiles.json`
- **Active config**: `~/.config/hypr/monitors.conf`

## Tips

- **Different setups, different configs**: Each unique combination of monitors gets its own saved configuration
- **No conflicts**: Old configurations are preserved when you save new ones
- **History tracking**: Check the profiles file to see your configuration history
- **Automatic monitoring**: HyprDisplays checks for changes every 3 seconds

## Troubleshooting

**Configuration not auto-loading?**

- Make sure you clicked "Apply & Save" after configuring
- Check that the same monitors are connected (by name)
- Look for status messages in the app

**Want to reset a configuration?**

- Just configure the displays as you want
- Click "Apply & Save" to overwrite the old configuration

**Multiple profiles getting mixed up?**

- Profiles are based on monitor names (e.g., "HDMI-A-1", "DP-1")
- If you swap which port a monitor uses, it creates a new profile

## Advanced

**View your profiles:**

```bash
cat ~/.config/hypr/hyprdisplays_profiles.json | jq
```

**Manual editing:**
You can manually edit the profiles file, but use "Apply & Save" to ensure consistency.

**Backup your profiles:**

```bash
cp ~/.config/hypr/hyprdisplays_profiles.json ~/hyprdisplays_backup.json
```
