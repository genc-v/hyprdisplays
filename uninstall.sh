#!/bin/bash
# Uninstall script for HyprDisplays

INSTALL_DIR="$HOME/.local/share/hyprdisplays"
DESKTOP_FILE="$HOME/.local/share/applications/hyprdisplays.desktop"
ICON_FILE="$HOME/.local/share/icons/hicolor/256x256/apps/hyprdisplays.png"
CONFIG_DIR="$HOME/.config/hyprdisplays"

echo "Uninstalling HyprDisplays..."

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "✓ Removed application files"
fi

# Remove desktop file
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo "✓ Removed desktop entry"
fi

# Remove icon
if [ -f "$ICON_FILE" ]; then
    rm "$ICON_FILE"
    echo "✓ Removed icon"
fi

# Ask about config
if [ -d "$CONFIG_DIR" ]; then
    read -p "Remove saved profiles and settings? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$CONFIG_DIR"
        echo "✓ Removed configuration files"
    else
        echo "→ Kept configuration files at $CONFIG_DIR"
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
