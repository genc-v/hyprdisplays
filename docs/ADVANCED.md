# Advanced Usage

## The Daemon

The daemon runs in the background to detect monitor changes and automatically apply your saved profiles.

### Management

The installer sets up a user systemd service.

```bash
# Check status
systemctl --user status hyprdisplays-daemon

# Enable and start
systemctl --user enable --now hyprdisplays-daemon

# View logs
journalctl --user -u hyprdisplays-daemon -f
```

### Manual Run

If you don't use systemd:

```bash
# Run in background
nohup ~/.local/share/hyprdisplays/hyprdisplays-daemon.py &
```

## Profiles Deep Dive

Profiles are stored in `~/.config/hypr/hyprdisplays_profiles.json`.
A profile is matched based on a "fingerprint" of all connected monitors (Manufacturer, Model, Serial).

If you connect a new set of monitors, HyprDisplays will treat it as a new profile. Configure it once in the GUI, save it, and it will be remembered.
