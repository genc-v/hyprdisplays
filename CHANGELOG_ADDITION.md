# Changelog Entry - Configuration Memory Feature

## New Feature: Automatic Monitor Configuration Memory

### What's New

HyprDisplays now automatically remembers your display configurations and applies them when you connect/disconnect monitors.

### Features

- **Automatic Profile Management**: Saves configurations based on connected monitors
- **Smart Detection**: Checks every 3 seconds for monitor changes
- **Auto-Apply**: Automatically loads and applies saved configurations
- **Configuration History**: Maintains log of recent configuration changes
- **Multiple Profiles**: Supports unlimited monitor combinations

### How to Use

1. Configure your displays as desired
2. Click "Apply & Save"
3. Your configuration is automatically saved for this monitor setup
4. Next time you connect the same monitors, your configuration is automatically applied

### Technical Details

- Profiles stored in `~/.config/hypr/hyprdisplays_profiles.json`
- Each profile identified by unique fingerprint based on connected monitor names
- Maintains history of up to 50 configuration changes
- Automatic monitoring every 3 seconds for monitor changes

### Files Added

- `CONFIGURATION_MEMORY.md` - Technical documentation
- `AUTO_CONFIG_GUIDE.md` - User quick start guide
- `IMPLEMENTATION_SUMMARY.md` - Development summary

### Files Modified

- `hyprdisplays.py` - Added ConfigurationManager and auto-detection
- `README.md` - Updated with new feature documentation

### Benefits

- No more manual reconfiguration when switching between monitor setups
- Seamless transitions between laptop-only and docked configurations
- Perfect for users who frequently connect/disconnect external displays
- Maintains separate configurations for different monitor combinations

### Examples

**Laptop User:**
- Laptop only → saved configuration A
- Laptop + external monitor → saved configuration B
- Automatically switches between A and B when connecting/disconnecting

**Desktop User:**
- 1 monitor → configuration A
- 2 monitors → configuration B  
- 3 monitors → configuration C
- Automatically uses correct configuration based on what's connected

**Docking Station User:**
- Undocked → laptop configuration
- Docked → multi-monitor configuration
- Automatically applies correct setup when docking/undocking

### Version

This feature was added on 2025-12-10.
