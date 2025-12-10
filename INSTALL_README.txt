================================================================================
                    HYPRDISPLAYS - ONE-COMMAND INSTALL
================================================================================

INSTALLATION
============

./install.sh

That's it! This installs EVERYTHING:
  ✓ GUI application for configuring monitors
  ✓ Background daemon for automatic detection
  ✓ Desktop menu entry
  ✓ Systemd service (starts on boot)


WHAT HAPPENS
============

After running ./install.sh:

1. GUI app installed at: ~/.local/share/hyprdisplays/
2. Background daemon: Automatically running now
3. Desktop entry: Find "Hyprland Display Manager" in your app menu
4. Auto-start: Daemon starts automatically on boot


HOW TO USE
==========

Step 1: Configure Your Monitor Setups (One Time)
-------------------------------------------------

Launch from app menu: "Hyprland Display Manager"

Or run: ~/.local/share/hyprdisplays/hyprdisplays.py

Configure each setup:
  - Laptop only → arrange, click "Apply & Save", close
  - Work monitor → connect it, arrange, "Apply & Save", close
  - Home monitor → connect it, arrange, "Apply & Save", close


Step 2: Enjoy Automatic Switching
----------------------------------

The daemon is already running in the background!

When you:
  - Unplug monitor → Auto-switches to laptop config
  - Plug work monitor → Auto-loads work config  
  - Plug home monitor → Auto-loads home config

No manual steps needed!


DAEMON STATUS
=============

Check if daemon is running:
  systemctl --user status hyprdisplays-daemon

View live activity:
  journalctl --user -u hyprdisplays-daemon -f

Stop daemon:
  systemctl --user stop hyprdisplays-daemon

Start daemon:
  systemctl --user start hyprdisplays-daemon


UNINSTALLATION
==============

./uninstall.sh

This removes:
  ✓ GUI application
  ✓ Background daemon (stops and disables it)
  ✓ Desktop entry
  ✓ All application files

Optionally removes:
  ? Your saved monitor profiles (you'll be asked)


FILES & LOCATIONS
=================

After installation:
  ~/.local/share/hyprdisplays/          # Application files
    ├── hyprdisplays.py                 # GUI app
    └── hyprdisplays-daemon.py          # Background daemon
  
  ~/.config/systemd/user/
    └── hyprdisplays-daemon.service     # Auto-start service
  
  ~/.local/share/applications/
    └── hyprdisplays.desktop            # Menu entry
  
  ~/.config/hypr/
    ├── hyprdisplays_profiles.json      # Your saved configs
    └── monitors.conf                   # Current active config


KEY FEATURES
============

✓ Physical monitor identification (work HDMI vs home HDMI)
✓ Automatic background monitoring (no GUI needed)
✓ Auto-start on boot (daemon runs automatically)
✓ One-command install (./install.sh)
✓ One-command uninstall (./uninstall.sh)
✓ Saved configs persist across reboots
✓ Lightweight (minimal CPU/memory usage)


TROUBLESHOOTING
===============

Daemon not working?
  systemctl --user status hyprdisplays-daemon
  journalctl --user -u hyprdisplays-daemon -f

Config not auto-applying?
  Make sure you saved it with "Apply & Save" in the GUI

Need to reconfigure?
  Just run the GUI again and save new config


COMPLETE WORKFLOW
=================

One-time setup:
  1. Run: ./install.sh
  2. Configure each monitor setup with GUI
  3. Done!

Daily use:
  Just plug/unplug monitors - it works automatically!


EXAMPLE: LAPTOP USER
====================

Install:
  ./install.sh

Configure (one time):
  # Laptop only
  Open GUI → configure → "Apply & Save" → close
  
  # Work monitor (Dell on HDMI-A-1)
  Plug in work monitor
  Open GUI → configure → "Apply & Save" → close
  
  # Home monitor (Samsung on HDMI-A-1)
  Plug in home monitor
  Open GUI → configure → "Apply & Save" → close

Daily use:
  Morning: Laptop only (auto-configured ✓)
  At work: Plug in Dell monitor (auto-configured ✓)
  At home: Plug in Samsung monitor (auto-configured ✓)
  
  No manual steps ever again!

================================================================================
