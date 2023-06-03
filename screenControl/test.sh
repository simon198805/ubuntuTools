while true; do
    IDLE_TIME=$(( $(xprintidle) / 1000 ));
    if [[ $IDLE_TIME -gt $IDLE_THRESHOLD ]]; then
       /home/tach/prog/personalScript/ubuntuTools/screenControl/externScreenControl.sh;
       echo 123
    fi
     sleep 1;
done