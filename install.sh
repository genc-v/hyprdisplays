#!/bin/bash
# Install script for HyprDisplays

INSTALL_DIR="$HOME/.local/share/hyprdisplays"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/512x512/apps"
SYSTEMD_DIR="$HOME/.config/systemd/user"

echo "Installing HyprDisplays..."

# Create installation directory
mkdir -p "$INSTALL_DIR"
mkdir -p "$DESKTOP_DIR"
mkdir -p "$ICON_DIR"
mkdir -p "$SYSTEMD_DIR"

# Copy application files
echo "  → Installing GUI application..."
cp hyprdisplays.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/hyprdisplays.py"

# Copy daemon
echo "  → Installing background daemon..."
cp hyprdisplays-daemon.py "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/hyprdisplays-daemon.py"

# Copy icon
cp logo.png "$ICON_DIR/hyprdisplays.png"

# Update desktop file with correct path
sed "s|/home/roses/random/hyprdisplays|$INSTALL_DIR|g" hyprdisplays.desktop > "$DESKTOP_DIR/hyprdisplays.desktop"
chmod +x "$DESKTOP_DIR/hyprdisplays.desktop"

# Install systemd service for background daemon
echo "  → Installing systemd service..."
cat > "$SYSTEMD_DIR/hyprdisplays-daemon.service" << EOF
[Unit]
Description=HyprDisplays Monitor Detection Daemon
After=graphical-session.target

[Service]
Type=simple
ExecStart=$INSTALL_DIR/hyprdisplays-daemon.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

# Reload systemd
systemctl --user daemon-reload

# Enable and start the daemon
echo "  → Enabling background daemon..."
systemctl --user enable hyprdisplays-daemon.service
systemctl --user start hyprdisplays-daemon.service

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR"
fi

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor"
fi

echo ""
echo "✓ Installation complete!"
echo ""
echo "What was installed:"
echo "  ✓ HyprDisplays GUI application"
echo "  ✓ Background daemon (running now)"
echo "  ✓ Desktop entry (in application menu)"
echo ""
echo "The background daemon is now monitoring for display changes."
echo "Configure your monitor setups with: $INSTALL_DIR/hyprdisplays.py"
echo "Or launch from your application menu: 'Hyprland Display Manager'"
echo ""
echo "Daemon status:"
systemctl --user status hyprdisplays-daemon.service --no-pager | head -3
echo ""
echo "View daemon logs: journalctl --user -u hyprdisplays-daemon -f"
