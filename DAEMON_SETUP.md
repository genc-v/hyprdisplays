# HyprDisplays Background Daemon Setup

## What This Is

A lightweight background service that monitors for monitor changes and automatically applies your saved configurations. **No GUI required!**

## Quick Setup

### 1. Configure Your Monitor Setups (One Time)

First, use the GUI to save your configurations:

```bash
cd /home/roses/random/hyprdisplays

# Configure laptop only
./hyprdisplays.py
# → Set up laptop display, click "Apply & Save", close

# Configure work monitor
# (Connect work monitor)
./hyprdisplays.py
# → Arrange monitors, click "Apply & Save", close

# Configure home monitor  
# (Connect home monitor instead)
./hyprdisplays.py
# → Arrange monitors, click "Apply & Save", close
```

### 2. Install Background Daemon

```bash
./install-daemon.sh
```

That's it! The daemon is now running in the background.

### 3. Test It

- Unplug your monitor → Config switches automatically (within 3 seconds)
- Plug in work monitor → Work config applied automatically
- Plug in home monitor → Home config applied automatically

## How It Works

The daemon:
- Runs invisibly in the background (no GUI)
- Checks for monitor changes every 3 seconds
- Reads your saved profiles from `~/.config/hypr/hyprdisplays_profiles.json`
- Automatically applies the matching configuration via `hyprctl`
- Uses physical monitor details (make/model/serial) to identify monitors
- Differentiates between work HDMI-A-1 and home HDMI-A-1

## Managing the Daemon

### View Live Logs
```bash
journalctl --user -u hyprdisplays-daemon -f
```

### Check Status
```bash
systemctl --user status hyprdisplays-daemon
```

### Stop Daemon
```bash
systemctl --user stop hyprdisplays-daemon
```

### Start Daemon
```bash
systemctl --user start hyprdisplays-daemon
```

### Restart Daemon
```bash
systemctl --user restart hyprdisplays-daemon
```

### Disable Daemon (Don't Run at Startup)
```bash
systemctl --user disable hyprdisplays-daemon
```

### Enable Daemon (Run at Startup)
```bash
systemctl --user enable hyprdisplays-daemon
```

## Example Log Output

```
[12:30:15] HyprDisplays Daemon started
  Check interval: 3 seconds
  Profiles: /home/roses/.config/hypr/hyprdisplays_profiles.json
[12:30:15] Monitoring for display changes...
  Press Ctrl+C to stop

[12:30:15] Monitor setup changed!
  Detected monitors: eDP-1
  No saved configuration for this setup
  Use HyprDisplays GUI to configure and save

[12:30:45] Monitor setup changed!
  Detected monitors: HDMI-A-1, eDP-1
  Found saved configuration
  Fingerprint: HDMI-A-1|Dell|U2415|ABC123;;eDP-1|AU Optronics|0xD1ED|...
  Saved at: 2025-12-10T12:00:00
  Applying saved configuration...
  ✓ Configuration applied successfully
```

## Running Manually (Without Systemd)

If you don't want to use systemd:

```bash
# Run in foreground (see output)
./hyprdisplays-daemon.py

# Run in background
./hyprdisplays-daemon.py &

# Run with custom check interval (5 seconds)
./hyprdisplays-daemon.py --interval 5
```

## Adding Configurations Later

Want to add a new monitor setup?

1. Connect the new monitor combination
2. Run GUI: `./hyprdisplays.py`
3. Configure and click "Apply & Save"
4. Close GUI

The daemon will automatically use this new configuration when detected!

## Uninstall Daemon

```bash
systemctl --user stop hyprdisplays-daemon
systemctl --user disable hyprdisplays-daemon
rm ~/.config/systemd/user/hyprdisplays-daemon.service
systemctl --user daemon-reload
```

## Troubleshooting

### Daemon Not Detecting Changes

Check if it's running:
```bash
systemctl --user status hyprdisplays-daemon
```

View recent logs:
```bash
journalctl --user -u hyprdisplays-daemon -n 50
```

### Configuration Not Applying

1. Make sure you saved the config with the GUI first
2. Check that the daemon recognized the monitors:
   ```bash
   journalctl --user -u hyprdisplays-daemon -f
   ```
3. Look for "Found saved configuration" in the logs

### Daemon Crashes

Restart it:
```bash
systemctl --user restart hyprdisplays-daemon
```

Check error logs:
```bash
journalctl --user -u hyprdisplays-daemon -n 100
```

## Performance

- **CPU Usage**: Minimal (sleeps between checks)
- **Memory**: ~15-20 MB
- **Check Interval**: 3 seconds (customizable)
- **Battery Impact**: Negligible

## Comparison

### With Daemon (Background Service)
✓ Runs automatically on startup
✓ No GUI needed after initial setup
✓ Invisible background operation
✓ Works even when you're not logged in to a desktop session
✓ Lightweight and efficient

### Without Daemon (GUI Only)
✗ Must keep GUI window open
✗ Have to manually launch it
✗ Takes more resources (GUI overhead)
✓ Can see visual feedback immediately

## Recommendation

**Use the daemon for automatic background monitoring, use the GUI when you need to add/modify configurations.**

Perfect workflow:
1. Install daemon: `./install-daemon.sh`
2. Configure setups as needed with GUI: `./hyprdisplays.py`
3. Forget about it - daemon handles everything automatically!
