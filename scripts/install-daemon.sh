#!/bin/bash

# HyprDisplays Daemon Installer

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INSTALL_DIR="$HOME/.local/share/hyprdisplays"

echo "Installing HyprDisplays Daemon..."

# Create directories
mkdir -p ~/.config/systemd/user
mkdir -p "$INSTALL_DIR"

# Copy daemon if not already installed
if [ ! -f "$INSTALL_DIR/hyprdisplays-daemon.py" ]; then
    cp "$PROJECT_ROOT/src/hyprdisplays-daemon.py" "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/hyprdisplays-daemon.py"
    echo "✓ Daemon installed"
fi

# Create systemd service file
cat > ~/.config/systemd/user/hyprdisplays-daemon.service << EOF
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

echo "✓ Service file created"

# Reload systemd
systemctl --user daemon-reload

echo "✓ Systemd reloaded"

# Enable the service
systemctl --user enable hyprdisplays-daemon.service

echo "✓ Service enabled"

# Start the service
systemctl --user start hyprdisplays-daemon.service

echo "✓ Service started"

# Check status
echo ""
echo "Service Status:"
systemctl --user status hyprdisplays-daemon.service --no-pager

echo ""
echo "Installation complete!"
echo ""
echo "Useful commands:"
echo "  View logs:    journalctl --user -u hyprdisplays-daemon -f"
echo "  Stop daemon:  systemctl --user stop hyprdisplays-daemon"
echo "  Start daemon: systemctl --user start hyprdisplays-daemon"
echo "  Restart:      systemctl --user restart hyprdisplays-daemon"
echo "  Status:       systemctl --user status hyprdisplays-daemon"
echo "  Disable:      systemctl --user disable hyprdisplays-daemon"
echo ""
echo "The daemon will now run in the background and automatically"
echo "apply monitor configurations when you connect/disconnect displays."
