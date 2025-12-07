#!/bin/bash

# Install script for Hyprland Settings

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing Hyprland Settings..."

# Create local applications directory if it doesn't exist
mkdir -p ~/.local/share/applications

# Copy desktop file
cp "$SCRIPT_DIR/hyprsettings.desktop" ~/.local/share/applications/
echo "✓ Desktop entry installed"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications
    echo "✓ Desktop database updated"
fi

# Make sure script is executable
chmod +x "$SCRIPT_DIR/hyprsettings.py"
echo "✓ Script made executable"

echo ""
echo "Installation complete! You can now:"
echo "  - Launch from application menu: 'Hyprland Settings'"
echo "  - Run from terminal: $SCRIPT_DIR/hyprsettings.py"
echo ""
