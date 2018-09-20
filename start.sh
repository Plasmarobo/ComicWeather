#!/bin/bash

# Startup Script for RPI with a touchscreen

export SDL_FBDEV =       "/dev/fb1"
export SDL_VIDEODRIVER = "fbcon"
export LOCK_FILE =        "/tmp/comicweather.lock"
export WORK_DIR =         "/home/pi/ComicWeather"
export CONFIG_FILE =      "config.txt"

if ! mkdir $LOCK_FILE; then
  printf "ComicWeather: Could not create $LOCK_FILE" >&2
  exit 1
fi

trap 'rm -rf $LOCK_FILE' EXIT

cd $WORK_DIR
python3 comicweather.py $CONFIG_FILE
