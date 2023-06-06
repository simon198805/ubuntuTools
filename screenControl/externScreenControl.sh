#!/bin/bash

# parameters
export DISPLAY=:1

EXTSCR="HDMI-1-0"
EXTSETUP="--auto --above"
BUILDINSCR="eDP-1"
# in 0.1 sec
IDLE_THRESHOLD=6000
# don't set the following value to under 10
CP_IDLE=10  
CP_WAKE=300

# used temp variable
IN_IDLE=false
#sec
CHECK_PERIOD=$CP_WAKE

while true; do
    IDLE_TIME=$(( $(xprintidle) / 100 ))

    echo IDLE_TIME $IDLE_TIME
    if [[ $IDLE_TIME -gt $IDLE_THRESHOLD  && "$IN_IDLE" != true ]]; then
            # this operation could reset idle time, mouse pos may be changed
            xrandr --output $EXTSCR --off
            IN_IDLE=true
            CHECK_PERIOD=$CP_IDLE
            echo inIdle $IDLE_TIME
    fi
    
	if [[ "$IN_IDLE" == true && $IDLE_TIME -lt $CHECK_PERIOD ]]; then
	    xrandr --output $EXTSCR $EXTSETUP $BUILDINSCR
	    IN_IDLE=false
	    CHECK_PERIOD=$CP_WAKE
	    echo normal $IDLE_TIME
	fi

    sleep $((CHECK_PERIOD / 10))
done
