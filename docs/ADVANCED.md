# Advanced Usage

## The Daemon

The daemon (`hyprdisplays-daemon.py`) runs in the background to detect monitor changes and automatically apply your saved profiles. This ensures that your preferred layout is restored immediately when you dock your laptop or connect external screens.

It performs a periodic background check of the connected monitors to detect changes in the hardware configuration.

### Management

The installer sets up a user systemd service. Make sure it is installed and running for the full "plug-and-play" experience.

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
nohup ~/.local/share/hyprdisplays/src/hyprdisplays-daemon.py &
```

## Profiles Deep Dive

Profiles are stored in `~/.config/hypr/hyprdisplays_profiles.json`.
A profile is matched based on a "fingerprint" of all connected monitors (Manufacturer, Model, Serial).

### History

The application maintains a history of up to 50 previous configurations in the JSON file. This allows for auditing or potential recovery of older setups if needed.

If you connect a new set of monitors, HyprDisplays will treat it as a new profile. Configure it once in the GUI, save it, and it will be remembered/added to history.
