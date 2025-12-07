#!/bin/bash
# Install script for HyprDisplays

INSTALL_DIR="$HOME/.local/share/hyprdisplays"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/512x512/apps"

echo "Installing HyprDisplays..."

# Create installation directory
mkdir -p "$INSTALL_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"

# Copy application files
cp hyprdisplays.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/hyprdisplays.py"

# Copy icon
cp logo.png "$ICON_DIR/hyprdisplays.png"

# Update desktop file with correct path
sed "s|/home/roses/random/hyprdisplays|$INSTALL_DIR|g" hyprdisplays.desktop > "$DESKTOP_DIR/hyprdisplays.desktop"
chmod +x "$DESKTOP_DIR/hyprdisplays.desktop"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR"
fi

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor"
fi

echo "✓ Installation complete!"
echo "You can now launch HyprDisplays from your application menu or run:"
echo "  $INSTALL_DIR/hyprdisplays.py"
