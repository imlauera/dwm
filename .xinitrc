# Status bar
/home/esotericwarfare/dwm/statusbar.sh &

# Screensaver
xfce4-screensaver &

# Set redshift and keyboard repeat rate
redshift -O3500
xset r rate 300 50

# Start dwm
while true; do
    # Log errors to a file
    dwm 2> ~/.dwm.log
done

