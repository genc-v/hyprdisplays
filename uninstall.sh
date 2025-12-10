#!/bin/bash
# Uninstall script for HyprDisplays

INSTALL_DIR="$HOME/.local/share/hyprdisplays"
DESKTOP_FILE="$HOME/.local/share/applications/hyprdisplays.desktop"
ICON_FILE="$HOME/.local/share/icons/hicolor/512x512/apps/hyprdisplays.png"
ICON_FILE_ALT="$HOME/.local/share/icons/hicolor/256x256/apps/hyprdisplays.png"
SYSTEMD_SERVICE="$HOME/.config/systemd/user/hyprdisplays-daemon.service"
PROFILES_FILE="$HOME/.config/hypr/hyprdisplays_profiles.json"

echo "Uninstalling HyprDisplays..."

# Stop and disable the daemon
if systemctl --user is-active --quiet hyprdisplays-daemon.service; then
    echo "  → Stopping background daemon..."
    systemctl --user stop hyprdisplays-daemon.service
fi

if systemctl --user is-enabled --quiet hyprdisplays-daemon.service 2>/dev/null; then
    echo "  → Disabling background daemon..."
    systemctl --user disable hyprdisplays-daemon.service
fi

# Remove systemd service file
if [ -f "$SYSTEMD_SERVICE" ]; then
    rm "$SYSTEMD_SERVICE"
    systemctl --user daemon-reload
    echo "  ✓ Removed systemd service"
fi

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "  ✓ Removed application files"
fi

# Remove desktop file
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo "  ✓ Removed desktop entry"
fi

# Remove icon (check both possible locations)
if [ -f "$ICON_FILE" ]; then
    rm "$ICON_FILE"
    echo "  ✓ Removed icon"
elif [ -f "$ICON_FILE_ALT" ]; then
    rm "$ICON_FILE_ALT"
    echo "  ✓ Removed icon"
fi

# Ask about saved profiles
if [ -f "$PROFILES_FILE" ]; then
    echo ""
    read -p "Remove saved monitor profiles? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm "$PROFILES_FILE"
        echo "  ✓ Removed saved profiles"
    else
        echo "  → Kept saved profiles at $PROFILES_FILE"
    fi
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null
fi

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null
fi

echo ""
echo "✓ Uninstallation complete!"
echo ""
echo "What was removed:"
echo "  ✓ HyprDisplays GUI application"
echo "  ✓ Background daemon (stopped and disabled)"
echo "  ✓ Desktop entry"
echo "  ✓ Application files"

if [ -f "$PROFILES_FILE" ]; then
    echo ""
    echo "Your saved monitor profiles are still at:"
    echo "  $PROFILES_FILE"
fi
