#!/bin/bash
# Display identifier overlay using wlroots layer shell
# Arguments: $1=display_number $2=monitor_name $3=description $4=monitor_output_name

DISPLAY_NUM="$1"
MONITOR_NAME="$2"
DESCRIPTION="$3"
OUTPUT="$4"

# Create a temporary overlay window with wlroots using wl-present or similar
# We'll use grim/slurp approach or a simple GTK overlay window

# For now, use a simple approach with zenity or yad if available
if command -v yad &> /dev/null; then
    DISPLAY=:0 yad --text="<span size='xx-large'>Display $DISPLAY_NUM</span>\n\n<b>$MONITOR_NAME</b>\n$DESCRIPTION" \
        --no-buttons --undecorated --center --timeout=3 \
        --width=400 --height=200 \
        --text-align=center &
elif command -v zenity &> /dev/null; then
    DISPLAY=:0 zenity --info --text="Display $DISPLAY_NUM\n\n$MONITOR_NAME\n$DESCRIPTION" --timeout=3 --width=400 --height=200 &
else
    # Fallback to notify-send
    notify-send -t 3000 "Display $DISPLAY_NUM" "$MONITOR_NAME\n$DESCRIPTION"
fi
