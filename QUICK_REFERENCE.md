# Quick Reference: Configuration Memory

## At a Glance

✓ **Automatic**: Saves configs when you click "Apply & Save"
✓ **Smart**: Detects monitor changes every 3 seconds  
✓ **Seamless**: Auto-applies saved configs when monitors reconnect
✓ **Multi-Profile**: Different configs for different monitor setups

## Common Tasks

### Save a Configuration

1. Arrange monitors how you want
2. Click "Apply & Save"
3. Done! Config is saved for this monitor setup

### Load a Configuration

**Nothing to do!** It happens automatically when you connect monitors.

### Check Status

Look at the bottom status bar:

- "Saved config available" = You have a saved config
- "Auto-applied" = Config was just loaded automatically

## File Locations

```bash
~/.config/hypr/hyprdisplays_profiles.json  # Your saved profiles
~/.config/hypr/monitors.conf                # Active configuration
```

## View Your Profiles

```bash
# Pretty print your profiles
cat ~/.config/hypr/hyprdisplays_profiles.json | python3 -m json.tool

# Or if you have jq installed
cat ~/.config/hypr/hyprdisplays_profiles.json | jq
```

## Backup Profiles

```bash
# Backup
cp ~/.config/hypr/hyprdisplays_profiles.json ~/hyprdisplays_backup.json

# Restore
cp ~/hyprdisplays_backup.json ~/.config/hypr/hyprdisplays_profiles.json
```

## Understanding Fingerprints

Each monitor setup gets a unique fingerprint:

| Setup                 | Fingerprint          | Example          |
| --------------------- | -------------------- | ---------------- |
| Single laptop display | `eDP-1`              | Laptop built-in  |
| Laptop + 1 external   | `DP-1,eDP-1`         | Laptop + monitor |
| Desktop 2 monitors    | `DP-1,HDMI-A-1`      | Two monitors     |
| Desktop 3 monitors    | `DP-1,DP-2,HDMI-A-1` | Three monitors   |

## Troubleshooting

**Config not auto-loading?**
→ Make sure you saved it with "Apply & Save"

**Different monitor on same port?**
→ Reconfigure and save, it will update the profile

**Want to delete a profile?**
→ Edit `~/.config/hypr/hyprdisplays_profiles.json` and remove the entry

**Reset everything?**
→ Delete `~/.config/hypr/hyprdisplays_profiles.json` and start fresh

## Tips

💡 Configure once per monitor setup  
💡 Profiles are permanent until you change them  
💡 You can have unlimited different profiles  
💡 Each monitor combination gets its own profile  
💡 History keeps track of changes for 50 entries

## Support

- Full docs: `CONFIGURATION_MEMORY.md`
- Quick guide: `AUTO_CONFIG_GUIDE.md`
- Technical: `IMPLEMENTATION_SUMMARY.md`
- Main readme: `README.md`
