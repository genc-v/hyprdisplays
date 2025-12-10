#!/bin/bash

# Hyprland GUI Tools Launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "╔════════════════════════════════════════╗"
echo "║     Hyprland GUI Tools                 ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Choose an application to launch:"
echo ""
echo "  1) HyprDisplays - Display Manager"
echo "  2) HyprSettings - Settings Manager"
echo "  3) Install both applications"
echo "  4) Exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo "Launching HyprDisplays..."
        "$PROJECT_ROOT/src/hyprdisplays.py"
        ;;
    2)
        echo "Launching HyprSettings..."
        "$PROJECT_ROOT/src/hyprsettings.py"
        ;;
    3)
        echo "Installing both applications..."
        "$SCRIPT_DIR/install.sh"
        "$SCRIPT_DIR/install_settings.sh"
        echo ""
        echo "Installation complete!"
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run again."
        exit 1
        ;;
esac
