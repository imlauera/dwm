#!/bin/bash

while true; do
    # Date and time
    DATE=$(date '+%a %d %b %H:%M')

    # Battery
    if [ -f /sys/class/power_supply/BAT0/capacity ]; then
        BAT=$(cat /sys/class/power_supply/BAT0/capacity)
        DATE="$DATE | BAT: ${BAT}%"
    fi

    # Volume
    VOL=$(amixer get Master 2>/dev/null | grep -o '[0-9]*%' | head -1 | tr -d '%')
    if [ -n "$VOL" ]; then
        MUTE=$(amixer get Master 2>/dev/null | grep -o '\[off\]' | head -1)
        if [ -n "$MUTE" ]; then
            DATE="$DATE | VOL: MUTE"
        else
            DATE="$DATE | VOL: ${VOL}%"
        fi
    fi

    # Memory
    MEM=$(free -m 2>/dev/null | awk '/^Mem:/ {printf "%d", $3/$2 * 100}')
    if [ -n "$MEM" ]; then
        DATE="$DATE | MEM: ${MEM}%"
    fi

    # CPU temperature
    if [ -f /sys/class/thermal/thermal_zone4/temp ]; then
        TEMP=$(cat /sys/class/thermal/thermal_zone4/temp 2>/dev/null | awk '{printf "%.1f", $1/1000}')
        if [ -n "$TEMP" ]; then
            DATE="$DATE | TEMP: ${TEMP}°C"
        fi
    fi

    # Set the status bar
    xsetroot -name "$DATE"

    sleep 1
done
