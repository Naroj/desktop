#!/bin/bash

function lopik() {
    xrandr --output HDMI-1 --auto
    xrandr --output eDP-1 --auto
    xrandr --output HDMI-1 --right-of eDP-1
    xrandr --output HDMI-1 --primary
}

lopik
