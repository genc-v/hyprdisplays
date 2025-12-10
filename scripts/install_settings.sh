#!/bin/bash

# Install script for Hyprland Settings

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

INSTALL_DIR="$HOME/.local/share/hyprdisplays"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/512x512/apps"

echo "Installing Hyprland Settings..."

# Create directories if they don't exist
mkdir -p "$INSTALL_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"

# Copy application
cp "$PROJECT_ROOT/src/hyprsettings.py" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/hyprsettings.py"
echo "✓ Application installed"

# Copy icon
if [ -f "$PROJECT_ROOT/assets/settings.png" ]; then
    cp "$PROJECT_ROOT/assets/settings.png" "$ICON_DIR/hyprsettings.png"
    echo "✓ Icon installed"
fi

# Update desktop file with correct path
sed "s|Exec=.*hyprsettings.py|Exec=$INSTALL_DIR/hyprsettings.py|g" "$PROJECT_ROOT/desktop/hyprsettings.desktop" > "$DESKTOP_DIR/hyprsettings.desktop"
chmod +x "$DESKTOP_DIR/hyprsettings.desktop"
echo "✓ Desktop entry installed"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR"
    echo "✓ Desktop database updated"
fi

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor"
    echo "✓ Icon cache updated"
fi

echo ""
echo "✓ Installation complete!"
echo ""
echo "You can now:"
echo "  - Launch from application menu: 'Hyprland Settings'"
echo "  - Run from terminal: $INSTALL_DIR/hyprsettings.py"
echo ""
