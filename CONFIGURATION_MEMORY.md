# Configuration Memory Feature

HyprDisplays now includes intelligent configuration memory that automatically saves and restores your display settings based on which monitors are connected.

## How It Works

### Automatic Profile Management

HyprDisplays creates a unique "fingerprint" for each monitor setup based on the connected monitors. When you save your configuration, it's stored with this fingerprint, allowing the system to:

1. **Detect monitor changes** - Checks every 3 seconds if monitors have been connected or disconnected
2. **Load saved configurations** - When monitors are detected, loads the matching saved configuration
3. **Auto-apply settings** - Automatically applies the saved configuration without user intervention
4. **Maintain history** - Keeps track of up to 50 recent configuration changes

### Configuration Storage

Your configurations are stored in:

```
~/.config/hypr/hyprdisplays_profiles.json
```

This file contains:

- **profiles**: Saved configurations for each monitor setup
- **history**: Log of recent configuration changes with timestamps

### Profile Format

Each profile includes:

- Monitor names (fingerprint)
- Resolution and refresh rate for each monitor
- Position (x, y coordinates)
- Scale factor
- Rotation/transformation
- Enabled/disabled state
- Primary monitor designation
- Timestamp of when it was saved

## Usage Examples

### Scenario 1: Laptop User

**Single Monitor (Built-in display)**

- Configure your laptop display settings
- Click "Apply & Save"
- Configuration is saved for "laptop only" setup

**Laptop + External Monitor**

- Connect external monitor
- HyprDisplays detects the change
- If no saved config exists, uses current settings
- Configure your dual monitor setup
- Click "Apply & Save"
- Configuration is saved for "laptop + external" setup

**Future Reconnections**

- Disconnect external monitor → automatically switches to "laptop only" config
- Reconnect external monitor → automatically switches to "laptop + external" config

### Scenario 2: Desktop User with Multiple Monitors

**One Monitor Connected**

- Configure single monitor
- Save configuration

**Two Monitors Connected**

- Connect second monitor
- Configure dual setup
- Save configuration

**Three Monitors Connected**

- Connect third monitor
- Configure triple setup
- Save configuration

**Automatic Switching**

- Each time you change your monitor setup, HyprDisplays automatically loads the correct configuration
- No manual intervention needed

### Scenario 3: Docking Station User

**Undocked (Laptop Only)**

- Configure laptop display
- Save configuration

**Docked (Laptop + Multiple Monitors)**

- Connect to docking station
- HyprDisplays detects all monitors
- Configure multi-monitor setup
- Save configuration

**Daily Workflow**

- Dock laptop → automatically applies docked configuration
- Undock laptop → automatically applies laptop-only configuration

## Technical Details

### Monitor Fingerprinting

A fingerprint is created by:

1. Collecting detailed information for each monitor (name, make, model, serial number)
2. Creating a unique identifier for each physical monitor
3. Sorting identifiers alphabetically (to ensure consistency)
4. Joining them together

This approach allows the system to differentiate between:
- Same connector (e.g., HDMI-A-1) with different physical monitors
- Work monitor vs. home monitor on the same laptop
- Multiple monitor setups with the same number of displays but different brands/models

Example fingerprints:

- Single laptop: `eDP-1|AU Optronics|0xD1ED|`
- Laptop + work monitor: `HDMI-A-1|Dell|U2415|ABC123;;eDP-1|AU Optronics|0xD1ED|`
- Laptop + home monitor: `HDMI-A-1|Samsung|C27F390|XYZ789;;eDP-1|AU Optronics|0xD1ED|`

**Key benefit**: You can have HDMI-A-1 at work with one configuration and HDMI-A-1 at home with a completely different configuration - HyprDisplays will know which is which!

### Auto-Detection

The application checks for monitor changes every 3 seconds by:

1. Querying Hyprland for connected monitors
2. Creating a fingerprint from the current setup
3. Comparing with the previous fingerprint
4. If different, attempting to load and apply saved configuration

### Configuration Application

When a saved configuration is found:

1. Configuration is applied via `hyprctl keyword monitor` commands
2. UI is refreshed to show the applied settings
3. Status bar indicates the auto-applied configuration

## Benefits

1. **No manual reconfiguration** - Set it once, use it everywhere
2. **Seamless transitions** - Smooth switching between different monitor setups
3. **Persistent settings** - Your preferences are remembered indefinitely
4. **Multiple profiles** - Support for unlimited monitor combinations
5. **History tracking** - See when configurations were saved
6. **Automatic recovery** - If monitors disconnect and reconnect, settings are restored

## Files Created

- `~/.config/hypr/hyprdisplays_profiles.json` - Profile and history database
- `~/.config/hypr/monitors.conf` - Current active monitor configuration (sourced by Hyprland)

## Notes

- Profiles are identified by monitor physical details (make, model, serial) not just connector names
- **Same connector, different monitors**: HDMI-A-1 at work vs. HDMI-A-1 at home are treated as different setups
- If a monitor doesn't provide make/model/serial info, the system falls back to using the connector name
- The 3-second check interval is designed to balance responsiveness with system resource usage
- All profile operations are logged to console for debugging
