#!/bin/bash

# parameters
EXTSCR="HDMI-1-0"
EXTSETUP="--auto --above"
BUILDINSCR="eDP-1"
# in sec
IDLE_THRESHOLD=600
CP_IDLE=1
CP_WAKE=60

# used temp variable
IN_IDLE=false
#sec
CHECK_PERIOD=$CP_WAKE

while true; do
    IDLE_TIME=$(( $(xprintidle) / 1000 ))

    if [[ $IDLE_TIME -gt $IDLE_THRESHOLD ]]; then
        if [ "$IN_IDLE" != true ]; then
            xrandr --output $EXTSCR --off
            IN_IDLE=true
            CHECK_PERIOD=$CP_IDLE
            echo inIdle
        fi
    else
        if [ "$IN_IDLE" = true ]; then
            xrandr --output $EXTSCR $EXTSETUP $BUILDINSCR
            IN_IDLE=false
            CHECK_PERIOD=$CP_WAKE
            echo normal
        fi
    fi

    sleep $CHECK_PERIOD
done