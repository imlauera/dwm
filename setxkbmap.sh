



SWITCH=$(setxkbmap -query | grep layout | awk '{print $2}')
[ $SWITCH == 'es' ] && setxkbmap ru
[ $SWITCH == 'ru' ] && setxkbmap es
