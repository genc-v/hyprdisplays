# Getting Started

HyprDisplays and HyprSettings are two GTK4 helpers for Hyprland.

- HyprDisplays: drag monitors, save layouts, auto-apply when displays change.
- HyprSettings: quick edits for gaps, borders, input, autostart, rules, keybinds, workspaces.

---

## Install

Fedora example:

```bash
sudo dnf install python3-gobject gtk4 libadwaita
./scripts/install.sh            # HyprDisplays
./scripts/install_settings.sh   # HyprSettings
```

Other distros: install GTK4 + libadwaita packages, then run the same scripts.

## Run

App menu entries are installed. Or use:

```bash
hyprdisplays
hyprsettings
```

## Basics

- Displays: drag to arrange, set scale/rotation, press "Apply & Save". A 15s confirm keeps you safe.
- Profiles: each monitor combo is remembered and auto-applied; stored in `~/.config/hypr/hyprdisplays_profiles.json`.
- Settings: sidebar for common options; raw editors for rules/keybinds/workspaces; changes call `hyprctl reload`.

## More docs

- Config file map and paths: `CONFIGURATION.md`
- Daemon, systemd, CLI: `ADVANCED.md`
