#!/bin/bash
# Install script for HyprDisplays

INSTALL_DIR="$HOME/.local/share/hyprdisplays"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "Installing HyprDisplays..."

# Create installation directory
mkdir -p "$INSTALL_DIR"
mkdir -p "$DESKTOP_DIR"

# Copy application files
cp hyprdisplays.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/hyprdisplays.py"

# Update desktop file with correct path
sed "s|/home/roses/random/hyprdisplays|$INSTALL_DIR|g" hyprdisplays.desktop > "$DESKTOP_DIR/hyprdisplays.desktop"
chmod +x "$DESKTOP_DIR/hyprdisplays.desktop"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR"
fi

echo "✓ Installation complete!"
echo "You can now launch HyprDisplays from your application menu or run:"
echo "  $INSTALL_DIR/hyprdisplays.py"
