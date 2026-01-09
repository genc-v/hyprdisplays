# Hyprland GUI Tools

Two small GTK4 apps for Hyprland:

- `HyprDisplays`: drag-and-drop display layout, remembers monitor setups, optional daemon for auto-apply.
- `HyprSettings`: edit Hyprland options with a simple sidebar and live reload.

Docs live in `docs/`: [Getting Started](docs/README.md), [Configuration](docs/CONFIGURATION.md), [Advanced](docs/ADVANCED.md).

---

## Install (Fedora example)

```bash
sudo dnf install python3-gobject gtk4 libadwaita
./installer.py
```

For other distros, install GTK4 + libadwaita packages, then run the installer.

## Run

Application menu entries: "Hyprland Display Manager" and "Hyprland Settings".

Terminal:

```bash
hyprdisplays
hyprsettings
```

## What you get

- Visual monitor layout with safe apply timeout and config profiles per monitor combo.
- Settings editor for gaps, borders, input, autostart, rules, keybinds, workspaces.
- Config files stay readable; your comments remain.

## Quick links

- Usage and setup: `docs/README.md`
- Config file map: `docs/CONFIGURATION.md`
- Daemon, systemd, CLI: `docs/ADVANCED.md`
