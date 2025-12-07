# Feature Overview

## 🖥️ HyprDisplays - Visual Display Manager

```
┌─────────────────────────────────────────────────────────────┐
│ Hyprland Display Manager                        [−][□][×]   │
├─────────────────────────────────────────────────────────────┤
│ [Refresh] [Identify]                    [Apply & Save] │
├──────────────────────────┬──────────────────────────────────┤
│                          │ ┌──────────────────────────────┐ │
│   ┌─────────┐            │ │ DP-1 - Monitor 1             │ │
│   │    1    │ DP-1       │ │ [Primary]                    │ │
│   │         │ 1920x1080  │ ├──────────────────────────────┤ │
│   └─────────┘            │ │ Mode: 1920x1080@144Hz ▼      │ │
│                          │ │ Scale: 1.00 ⊕⊖               │ │
│   ┌─────────┐            │ │ Rotation: 0° (Normal) ▼      │ │
│   │    2    │ HDMI-1     │ │ [✓] Enabled                  │ │
│   │         │ 2560x1440  │ └──────────────────────────────┘ │
│   └─────────┘            │                                  │
│                          │ ┌──────────────────────────────┐ │
│  [Zoom: 100%] [Reset]    │ │ HDMI-1 - Monitor 2           │ │
│                          │ │ [ ] Primary                  │ │
│  Drag to position        │ ├──────────────────────────────┤ │
│  Scroll to zoom          │ │ Mode: 2560x1440@60Hz ▼       │ │
│                          │ │ Scale: 1.25 ⊕⊖               │ │
│                          │ │ Rotation: 0° (Normal) ▼      │ │
│                          │ │ [✓] Enabled                  │ │
│                          │ └──────────────────────────────┘ │
└──────────────────────────┴──────────────────────────────────┘
│ Configuration changed (not applied)                         │
└─────────────────────────────────────────────────────────────┘
```

### Key Features
- **Visual Canvas**: See your monitor layout and drag to reposition
- **Live Preview**: Changes update in real-time on the canvas
- **Smart Snapping**: Monitors auto-snap to valid positions
- **Zoom Control**: Scroll to zoom in/out for better precision
- **Primary Monitor**: Set which monitor is primary with one click
- **Display Identification**: Show numbers on each screen to identify them
- **Safe Apply**: 15-second confirmation dialog prevents broken configs

---

## ⚙️ HyprSettings - Comprehensive Settings Manager

```
┌─────────────────────────────────────────────────────────────────┐
│ Hyprland Settings                                   [−][□][×]   │
├─────────────────────────────────────────────────────────────────┤
│                                 [Open Config] [Reload] │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                   │
│ ☰ General    │  Appearance                                      │
│              │  Configure visual settings                       │
│ 󰴺 Animations  │  ┌───────────────────────────────────────────┐  │
│              │  │ Border Size                        [2]⊕⊖   │  │
│ 󰌌 Input       │  │ Width of window borders                  │  │
│              │  └───────────────────────────────────────────┘  │
│  Workspaces │  ┌───────────────────────────────────────────┐  │
│              │  │ Inner Gaps                         [5]⊕⊖   │  │
│  Environment│  │ Gap size between windows                 │  │
│              │  └───────────────────────────────────────────┘  │
│  Autostart  │  ┌───────────────────────────────────────────┐  │
│              │  │ Outer Gaps                        [10]⊕⊖  │  │
│  Rules      │  │ Gap size from screen edges               │  │
│              │  └───────────────────────────────────────────┘  │
│  Keybinds   │                                                   │
│              │  Layout                                           │
│              │  Window layout settings                          │
│              │  ┌───────────────────────────────────────────┐  │
│              │  │ Pseudo Tiling                  [OFF][ON] │  │
│              │  │ Enable pseudo-tiling for floating        │  │
│              │  └───────────────────────────────────────────┘  │
│              │                                                   │
└──────────────┴──────────────────────────────────────────────────┘
│ Ready                                                            │
└──────────────────────────────────────────────────────────────────┘
```

### Available Settings Pages

#### 1. General
- Border Size (0-20px)
- Inner Gaps (0-50px)
- Outer Gaps (0-100px)
- Pseudo Tiling (on/off)
- Layout options

#### 2. Animations
- Enable/Disable animations
- Animation speed multiplier (0.5-5.0x)
- Per-animation settings

#### 3. Input
- Mouse sensitivity (-1.0 to 1.0)
- Natural scroll (on/off)
- Tap to click (on/off)
- Keyboard layout
- Keyboard variant

#### 4. Workspaces
- Full text editor for workspace rules
- Configure workspace behavior
- Multi-monitor workspace setup

#### 5. Environment
- Edit environment variables
- Set PATH, themes, etc.
- Configure XDG directories

#### 6. Autostart
- Programs to run on Hyprland start
- exec-once commands
- Full text editor

#### 7. Rules
- Window rules configuration
- Window-specific behavior
- Floating, fullscreen, workspace rules

#### 8. Keybinds
- Keyboard shortcut configuration
- Full text editor for complex binds
- All Hyprland keybind types

### Smart Features
- **Auto-detection**: Finds configs in both `hyprland/` and `custom/` dirs
- **Live Reload**: Changes apply instantly via `hyprctl reload`
- **Preserve Comments**: Keeps your config comments and formatting
- **Safe Editing**: Works alongside manual edits
- **Quick Access**: "Open Config Folder" button for advanced editing

---

## File Management

Both tools are designed to work together:

| Tool | Manages | Location |
|------|---------|----------|
| HyprDisplays | Monitor configuration | `~/.config/hypr/monitors.conf` |
| HyprSettings | General settings | `~/.config/hypr/hyprland/*.conf` |
| HyprSettings | Custom settings | `~/.config/hypr/custom/*.conf` |
| HyprSettings | Workspaces | `~/.config/hypr/workspaces.conf` |

**No conflicts** - Each tool manages separate configuration files!

---

## Benefits Over Manual Editing

### HyprDisplays Benefits
✅ Visual positioning instead of calculating coordinates  
✅ See all monitors at once  
✅ Drag-and-drop repositioning  
✅ Auto-snapping prevents gaps  
✅ Safe testing with revert dialog  

### HyprSettings Benefits  
✅ No syntax errors - GUI prevents mistakes  
✅ Instant validation of values  
✅ Descriptions for every setting  
✅ Live preview of changes  
✅ Easy access to all settings in one place  
✅ Text editors for complex configs when needed  

### Still Want Manual Editing?
Both tools let you:
- Click "Open Config Folder" to edit in your text editor
- Edit files manually - the tools won't break your configs
- Use version control (git) to track changes
- Mix GUI and manual editing as you prefer

---

## Installation Comparison

| Method | HyprDisplays | HyprSettings | Both |
|--------|--------------|--------------|------|
| `./launcher.sh` | ✓ Can launch | ✓ Can launch | ✓ Can install |
| `./install.sh` | ✓ Installs | - | - |
| `./install_settings.sh` | - | ✓ Installs | - |
| Manual | `./hyprdisplays.py` | `./hyprsettings.py` | - |

Choose what works best for your workflow!
