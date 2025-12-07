#!/bin/bash

# Install script for Hyprland Settings

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing Hyprland Settings..."

# Create local applications and icons directories if they don't exist
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons/hicolor/512x512/apps
mkdir -p ~/.local/share/icons/hicolor/scalable/apps

# Copy icon
if [ -f "$SCRIPT_DIR/settings.png" ]; then
    cp "$SCRIPT_DIR/settings.png" ~/.local/share/icons/hicolor/512x512/apps/hyprsettings.png
    echo "✓ Icon installed"
fi

# Copy desktop file
cp "$SCRIPT_DIR/hyprsettings.desktop" ~/.local/share/applications/
echo "✓ Desktop entry installed"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications
    echo "✓ Desktop database updated"
fi

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache ~/.local/share/icons/hicolor -f
    echo "✓ Icon cache updated"
fi

# Make sure script is executable
chmod +x "$SCRIPT_DIR/hyprsettings.py"
echo "✓ Script made executable"

echo ""
echo "Installation complete! You can now:"
echo "  - Launch from application menu: 'Hyprland Settings'"
echo "  - Run from terminal: $SCRIPT_DIR/hyprsettings.py"
echo ""
