# Advanced Features

This guide covers advanced features and use cases for power users.

**[← Back to Main README](README.md)**

---

## Table of Contents

- [Background Daemon](#background-daemon)
- [Physical Monitor Identification](#physical-monitor-identification)
- [Configuration Profiles](#configuration-profiles)
- [Running at Startup](#running-at-startup)
- [Command Line Options](#command-line-options)
- [Systemd Integration](#systemd-integration)

---

## Background Daemon

Run automatic monitor detection without the GUI using the background daemon.

### What It Does

The daemon:

- Runs invisibly in the background (no GUI window)
- Checks for monitor changes every 3 seconds
- Automatically applies saved configurations when monitors connect/disconnect
- Uses physical monitor details to identify monitors
- Minimal resource usage (~15-20 MB RAM)

### Quick Setup

**Step 1: Configure Your Setups (One Time)**

Use the GUI to save your different monitor configurations:

```bash
# Configure laptop only
hyprdisplays
# → Set up display, click "Apply & Save", close

# Configure work monitor
# (Connect work monitor first)
hyprdisplays
# → Arrange monitors, click "Apply & Save", close

# Configure home monitor
# (Connect home monitor instead)
hyprdisplays
# → Arrange monitors, click "Apply & Save", close
```

**Step 2: Install Daemon**

```bash
./install-daemon.sh
```

**Step 3: Done!**

The daemon now runs automatically. When you connect/disconnect monitors, configurations apply within 3 seconds.

### Managing the Daemon

**View Live Logs**

```bash
journalctl --user -u hyprdisplays-daemon -f
```

**Check Status**

```bash
systemctl --user status hyprdisplays-daemon
```

**Stop/Start/Restart**

```bash
systemctl --user stop hyprdisplays-daemon
systemctl --user start hyprdisplays-daemon
systemctl --user restart hyprdisplays-daemon
```

**Enable/Disable Auto-Start**

```bash
systemctl --user enable hyprdisplays-daemon   # Run at login
systemctl --user disable hyprdisplays-daemon  # Don't run at login
```

### Example Log Output

```
[12:30:15] HyprDisplays Daemon started
  Check interval: 3 seconds
  Profiles: /home/user/.config/hypr/hyprdisplays_profiles.json
[12:30:15] Monitoring for display changes...

[12:30:45] Monitor setup changed!
  Detected monitors: HDMI-A-1, eDP-1
  Found saved configuration
  Fingerprint: HDMI-A-1|Dell|U2415|ABC123;;eDP-1|AU Optronics|...
  Applying saved configuration...
  ✓ Configuration applied successfully
```

### Running Manually

If you don't want systemd:

```bash
# Run in foreground (see output)
./hyprdisplays-daemon.py

# Run in background
./hyprdisplays-daemon.py &

# Custom check interval (5 seconds instead of 3)
./hyprdisplays-daemon.py --interval 5
```

### Uninstall Daemon

```bash
systemctl --user stop hyprdisplays-daemon
systemctl --user disable hyprdisplays-daemon
rm ~/.config/systemd/user/hyprdisplays-daemon.service
systemctl --user daemon-reload
```

### Daemon vs GUI

**With Daemon (Recommended)**

- ✓ Automatic on startup
- ✓ No GUI needed after initial setup
- ✓ Invisible background operation
- ✓ Lightweight and efficient

**With GUI Only**

- ✗ Must keep window open for auto-detection
- ✗ Manual launch required
- ✓ Visual feedback
- ✓ On-demand configuration changes

**Best Approach:** Use daemon for automatic background operation, launch GUI when you need to add/modify configurations.

---

## Physical Monitor Identification

HyprDisplays uses physical monitor details to uniquely identify each display.

### How It Works

Each monitor is identified by a fingerprint combining:

- **Make**: Manufacturer (Dell, Samsung, LG, etc.)
- **Model**: Monitor model number
- **Serial Number**: Unique serial identifier
- **Connection Port**: HDMI-A-1, DP-1, etc.

### Example Fingerprint

```
HDMI-A-1|Dell|U2415|ABC123XYZ
```

This means:

- Port: HDMI-A-1
- Make: Dell
- Model: U2415
- Serial: ABC123XYZ

### Why This Matters

**Same Port, Different Monitors**

You can use the same physical port (like HDMI-A-1) for different monitors:

- **Work:** HDMI-A-1 with Dell U2415 → One saved configuration
- **Home:** HDMI-A-1 with Samsung C27 → Different saved configuration

When you connect each monitor, HyprDisplays recognizes which physical monitor is connected and applies the correct configuration automatically.

### Viewing Monitor Information

In HyprDisplays, click "Identify Displays" to show:

- Port name (HDMI-A-1, DP-1, etc.)
- Monitor make and model
- Resolution
- Display number

### Built-in Monitor Detection Script

```bash
./show_display_id.sh
```

This displays all connected monitors with their physical details.

### Configuration Storage

Monitor configurations are stored with their fingerprints in:

```
~/.config/hypr/hyprdisplays_profiles.json
```

Example structure:

```json
{
  "fingerprint": "HDMI-A-1|Dell|U2415|ABC123;;eDP-1|AU Optronics|...",
  "timestamp": "2025-12-10T12:00:00",
  "monitors": {
    "HDMI-A-1": {
      "enabled": true,
      "width": 1920,
      "height": 1080,
      "refresh": 60,
      "x": 1920,
      "y": 0,
      "scale": 1.0,
      "transform": 0
    }
  }
}
```

---

## Configuration Profiles

### Profile Management

HyprDisplays keeps a history of up to 50 recent configurations, automatically managing them based on:

- Monitor combinations (which monitors are connected)
- Physical monitor details (make, model, serial)
- Timestamp (when last saved)

### Viewing Your Profiles

```bash
cat ~/.config/hypr/hyprdisplays_profiles.json | python3 -m json.tool
```

Or with `jq`:

```bash
cat ~/.config/hypr/hyprdisplays_profiles.json | jq
```

### How Profiles Are Matched

When monitors connect, HyprDisplays:

1. Detects all connected monitors
2. Gets physical details for each monitor
3. Creates a fingerprint from the monitor combination
4. Searches saved profiles for matching fingerprint
5. Applies the configuration if found

### Adding New Profiles

Simply connect the new monitor combination and:

1. Open HyprDisplays
2. Configure the displays
3. Click "Apply & Save"

The new profile is automatically added and will be used for this combination going forward.

### Resetting Profiles

**Backup first:**

```bash
cp ~/.config/hypr/hyprdisplays_profiles.json ~/hyprdisplays_backup.json
```

**Delete all profiles:**

```bash
rm ~/.config/hypr/hyprdisplays_profiles.json
```

**Delete specific profile:**
Edit the JSON file and remove the entry for that fingerprint.

---

## Running at Startup

### Option 1: Daemon (Recommended)

Install the daemon to run automatically in the background:

```bash
./install-daemon.sh
```

The daemon:

- Starts automatically at login
- Runs invisibly
- Monitors for display changes
- No GUI window

### Option 2: GUI Application

Add to Hyprland config (`~/.config/hypr/hyprland.conf`):

```bash
# Auto-start HyprDisplays GUI
exec-once = hyprdisplays
```

Or if not installed system-wide:

```bash
exec-once = /path/to/hyprdisplays/hyprdisplays.py
```

The GUI:

- Shows a window at startup
- Can be minimized to continue monitoring
- Provides visual feedback
- Allows immediate configuration changes

### Option 3: Both

You can run both the daemon and GUI:

- Daemon handles automatic switching in background
- GUI available when you need to make changes

They won't conflict - both read from the same profile file.

---

## Command Line Options

### HyprDisplays

```bash
# Run normally
hyprdisplays

# Run in background (GUI minimized)
hyprdisplays &

# Run and log output
hyprdisplays 2>&1 | tee hyprdisplays.log
```

### HyprDisplays Daemon

```bash
# Run with default 3-second interval
./hyprdisplays-daemon.py

# Run with custom interval (5 seconds)
./hyprdisplays-daemon.py --interval 5

# Run in background
./hyprdisplays-daemon.py &

# Run with logging
./hyprdisplays-daemon.py 2>&1 | tee daemon.log
```

### HyprSettings

```bash
# Run normally
hyprsettings

# Open specific config file location
# (Automatically detects hyprland/ or custom/)
hyprsettings
```

---

## Systemd Integration

### Custom Daemon Service

Create `~/.config/systemd/user/hyprdisplays-daemon.service`:

```ini
[Unit]
Description=Hyprland Display Manager Daemon
After=graphical-session.target

[Service]
Type=simple
ExecStart=/path/to/hyprdisplays/hyprdisplays-daemon.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Enable and start:

```bash
systemctl --user daemon-reload
systemctl --user enable hyprdisplays-daemon
systemctl --user start hyprdisplays-daemon
```

### GUI Service (Optional)

Create `~/.config/systemd/user/hyprdisplays.service`:

```ini
[Unit]
Description=Hyprland Display Manager GUI
After=graphical-session.target

[Service]
Type=simple
ExecStart=/path/to/hyprdisplays/hyprdisplays.py
Restart=on-failure

[Install]
WantedBy=default.target
```

### Viewing Service Logs

**Real-time logs:**

```bash
journalctl --user -u hyprdisplays-daemon -f
```

**Last 50 lines:**

```bash
journalctl --user -u hyprdisplays-daemon -n 50
```

**Since boot:**

```bash
journalctl --user -u hyprdisplays-daemon -b
```

**With timestamps:**

```bash
journalctl --user -u hyprdisplays-daemon -o short-precise
```

---

## Advanced Troubleshooting

### Daemon Not Detecting Changes

**Check if running:**

```bash
systemctl --user status hyprdisplays-daemon
```

**Check logs:**

```bash
journalctl --user -u hyprdisplays-daemon -n 100
```

**Restart daemon:**

```bash
systemctl --user restart hyprdisplays-daemon
```

### Configuration Not Auto-Applying

**Verify profile exists:**

```bash
cat ~/.config/hypr/hyprdisplays_profiles.json | grep -A 20 "fingerprint"
```

**Check monitor fingerprint:**

```bash
./show_display_id.sh
```

**Test manually:**

```bash
# Stop daemon
systemctl --user stop hyprdisplays-daemon

# Run daemon in foreground to see output
./hyprdisplays-daemon.py

# Connect/disconnect monitor and watch output
```

### Multiple Monitors Not Detected

**Check Hyprland monitor detection:**

```bash
hyprctl monitors
```

**Verify monitor is actually connected:**

```bash
./show_display_id.sh
```

**Force refresh:**

```bash
hyprctl reload
```

### Performance Issues

**Check daemon resource usage:**

```bash
ps aux | grep hyprdisplays
top -p $(pgrep -f hyprdisplays)
```

**Increase check interval (reduce CPU usage):**

```bash
./hyprdisplays-daemon.py --interval 5
```

Edit systemd service to make permanent:

```ini
ExecStart=/path/to/hyprdisplays-daemon.py --interval 5
```

---

## Workflow Examples

### Example 1: Laptop User (Work + Home)

**Initial Setup:**

```bash
# Install daemon
./install-daemon.sh

# Configure laptop only
hyprdisplays
# → Configure, "Apply & Save", close

# At work: plug in work monitor
hyprdisplays
# → Configure dual setup, "Apply & Save", close

# At home: plug in home monitor
hyprdisplays
# → Configure dual setup, "Apply & Save", close
```

**Daily Use:**

- Arrive at work → Plug in monitor → Auto-configured within 3 seconds
- Go home → Plug in home monitor → Auto-configured to home setup
- On the go → Laptop only → Auto-configured to single display
- No manual intervention needed!

### Example 2: Desktop User (3 Monitors)

**Initial Setup:**

```bash
# Install daemon
./install-daemon.sh

# Configure all 3 monitors
hyprdisplays
# → Position all 3, set resolution/scale, "Apply & Save"
```

**Daily Use:**

- If one monitor disconnects temporarily → Auto-configured to 2-monitor setup
- Reconnect monitor → Auto-configured back to 3-monitor setup
- Completely automatic!

### Example 3: Presentation Setup

**Initial Setup:**

```bash
# Configure normal work setup
hyprdisplays
# → Configure, "Apply & Save"

# Connect to projector
hyprdisplays
# → Configure presentation layout, "Apply & Save"
```

**During Presentation:**

- Connect projector → Auto-switches to presentation layout
- Disconnect projector → Auto-switches back to work layout
- No fumbling with display settings during presentation!

---

**[← Back to Main README](README.md)**
