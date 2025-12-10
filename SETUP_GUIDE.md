# HyprDisplays Setup Guide

## Quick Start

### Option 1: Run Directly (Testing)

```bash
cd /home/roses/random/hyprdisplays
./hyprdisplays.py
```

The application will open with a GUI showing your current monitors.

### Option 2: Install System-Wide (Recommended)

```bash
cd /home/roses/random/hyprdisplays
./install.sh
```

After installation, you can launch it from:
- Application menu: Search for "Hyprland Display Manager"
- Command line: `hyprdisplays`

## How Automatic Configuration Works

### Important: The Application Must Be Running

**The automatic monitor detection ONLY works while the application is running!**

Here's how it works:

1. **While HyprDisplays is open:**
   - It checks for monitor changes every 3 seconds
   - When you unplug/plug monitors, it detects the change
   - Automatically loads and applies the saved configuration

2. **When HyprDisplays is closed:**
   - No automatic detection happens
   - Your last saved configuration stays in `~/.config/hypr/monitors.conf`
   - Hyprland continues to use that configuration

### Two Ways to Use It

#### Method 1: Keep It Running in Background

**Best for:** Users who frequently connect/disconnect monitors

```bash
# Start HyprDisplays and minimize it
./hyprdisplays.py &

# Or after installation:
hyprdisplays &
```

Then just minimize the window - it will continue monitoring in the background and auto-apply configurations.

#### Method 2: Open When Needed

**Best for:** Users who rarely change monitor setups

1. Open HyprDisplays when you connect/disconnect monitors
2. Let it detect and apply the configuration automatically
3. Close it when done

## Setting Up Your Configurations

### First Time Setup

**Step 1: Configure Single Monitor (Laptop Only)**

```bash
# Make sure only laptop display is connected
./hyprdisplays.py
```

1. Configure your laptop display settings
2. Click "Apply & Save"
3. Close the application

**Step 2: Configure Work Monitor Setup**

```bash
# Connect your work monitor (e.g., Dell on HDMI-A-1)
./hyprdisplays.py
```

1. Arrange monitors how you want
2. Set resolution, scale, position, etc.
3. Click "Apply & Save"
4. Status will show: "Config saved for 2 monitor(s) - Will auto-load on reconnect!"
5. Close the application

**Step 3: Configure Home Monitor Setup**

```bash
# Disconnect work monitor, connect home monitor (e.g., Samsung on HDMI-A-1)
./hyprdisplays.py
```

1. Arrange monitors for home setup
2. Set resolution, scale, position, etc.
3. Click "Apply & Save"
4. Close the application

### Testing Automatic Switching

**Option A: Keep HyprDisplays Running**

```bash
./hyprdisplays.py
# Keep the window open (you can minimize it)
```

Now test:
1. Unplug external monitor → Should auto-switch to laptop-only config
2. Plug in work monitor → Should auto-load work config
3. Unplug and plug in home monitor → Should auto-load home config

Watch the status bar for messages like:
- "Auto-applied saved config for 2 monitor(s)"
- "Auto-applied saved config for 1 monitor(s)"

**Option B: Manual Application**

1. Connect/disconnect monitors
2. Open HyprDisplays
3. It detects the change and auto-applies saved config
4. Close HyprDisplays

## Running at Startup (Optional)

If you want automatic configuration on boot:

**Add to Hyprland config** (`~/.config/hypr/hyprland.conf`):

```bash
# Auto-start HyprDisplays for automatic monitor management
exec-once = hyprdisplays
```

Or if not installed system-wide:

```bash
exec-once = /home/roses/random/hyprdisplays/hyprdisplays.py
```

This will:
- Start HyprDisplays when Hyprland starts
- Monitor for display changes automatically
- Apply saved configurations as monitors connect/disconnect

## File Structure

```
~/.config/hypr/
├── hyprland.conf              # Main Hyprland config
├── monitors.conf              # Current active monitor config (auto-generated)
└── hyprdisplays_profiles.json # Your saved monitor configurations
```

## Checking Your Saved Configurations

```bash
# View your saved profiles
cat ~/.config/hypr/hyprdisplays_profiles.json | python3 -m json.tool

# Or with jq (if installed)
cat ~/.config/hypr/hyprdisplays_profiles.json | jq
```

## Troubleshooting

### Config Not Auto-Loading?

**Check 1:** Is HyprDisplays running?
```bash
ps aux | grep hyprdisplays
```

If not running, automatic detection won't work. Start it with:
```bash
./hyprdisplays.py &
```

**Check 2:** Did you save the configuration?

Look for message: "Config saved for X monitor(s) - Will auto-load on reconnect!"

**Check 3:** Are monitors recognized?

Open HyprDisplays and check the status bar:
- "Loaded X display(s) - Saved config available" = Good!
- "Loaded X display(s)" (no mention of saved config) = No saved config for this setup

### Manual Configuration Reset

```bash
# Backup current profiles
cp ~/.config/hypr/hyprdisplays_profiles.json ~/hyprdisplays_backup.json

# Delete profiles (start fresh)
rm ~/.config/hypr/hyprdisplays_profiles.json

# Reconfigure from scratch
./hyprdisplays.py
```

## Workflow Examples

### Example 1: Daily Laptop User

**Morning (at home):**
```bash
# Laptop only - HyprDisplays auto-applies laptop config
# No action needed if HyprDisplays is running
```

**At office:**
```bash
# Plug in work monitor
# HyprDisplays detects Dell monitor, auto-applies work config
# No action needed!
```

**Back home:**
```bash
# Unplug work monitor
# HyprDisplays auto-applies laptop-only config
# Plug in home monitor
# HyprDisplays detects Samsung monitor, auto-applies home config
```

### Example 2: Desktop User

**Initial setup (one time):**
```bash
./hyprdisplays.py
# Configure 3-monitor setup
# Click "Apply & Save"
```

**If a monitor disconnects temporarily:**
```bash
# HyprDisplays (if running) auto-applies 2-monitor config
# Reconnect monitor
# HyprDisplays auto-applies 3-monitor config back
```

## Command Line Options

```bash
# Run normally
./hyprdisplays.py

# Run in background
./hyprdisplays.py &

# Run and log output
./hyprdisplays.py 2>&1 | tee hyprdisplays.log
```

## Systemd Service (Advanced)

If you want HyprDisplays to run as a service:

Create `~/.config/systemd/user/hyprdisplays.service`:

```ini
[Unit]
Description=Hyprland Display Manager
After=graphical-session.target

[Service]
Type=simple
ExecStart=/home/roses/random/hyprdisplays/hyprdisplays.py
Restart=on-failure

[Install]
WantedBy=default.target
```

Enable and start:
```bash
systemctl --user enable hyprdisplays
systemctl --user start hyprdisplays
```

## Summary

**Key Points:**

1. **Automatic detection requires HyprDisplays to be running**
2. **Set up each monitor configuration once** (laptop-only, work setup, home setup)
3. **Keep HyprDisplays running** for automatic switching (optional but recommended)
4. **Configurations are saved** in `~/.config/hypr/hyprdisplays_profiles.json`
5. **Each physical monitor is recognized** individually (work vs home monitor)

**Recommended Workflow:**

1. Install: `./install.sh`
2. Configure each setup once with "Apply & Save"
3. Add to Hyprland startup: `exec-once = hyprdisplays`
4. Forget about it - it just works!
