# Advanced

Short references for daemon, profiles, and systemd.

---

## Daemon

Background monitor watcher that auto-applies saved layouts.

Install (user scope):

```bash
./install-daemon.sh
```

Manage:

```bash
systemctl --user status hyprdisplays-daemon
systemctl --user restart hyprdisplays-daemon
systemctl --user enable --now hyprdisplays-daemon
systemctl --user disable --now hyprdisplays-daemon
journalctl --user -u hyprdisplays-daemon -f
```

Run without systemd:

```bash
./hyprdisplays-daemon.py --interval 3   # foreground
./hyprdisplays-daemon.py --interval 3 & # background
```

Uninstall:

```bash
systemctl --user disable --now hyprdisplays-daemon
rm ~/.config/systemd/user/hyprdisplays-daemon.service
systemctl --user daemon-reload
```

## Profiles

- Stored in `~/.config/hypr/hyprdisplays_profiles.json`.
- Each entry fingerprints connected monitors (port + make + model + serial) and the layout.
- New combo? Arrange in HyprDisplays and hit "Apply & Save" to add a profile.
- Reset profiles: back up the file, then delete it to start clean.

## Launch at login (GUI)

If you prefer the GUI watching:

```conf
# In hyprland.conf
exec-once = hyprdisplays
```

## CLI cheatsheet

```bash
hyprdisplays                 # GUI
hyprdisplays &               # GUI minimized
./hyprdisplays-daemon.py     # daemon in foreground
./hyprdisplays-daemon.py &   # daemon in background
hyprsettings                 # settings GUI
```

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

````

Enable and start:

```bash
systemctl --user daemon-reload
systemctl --user enable hyprdisplays-daemon
systemctl --user start hyprdisplays-daemon
````

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
