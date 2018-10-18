#!/bin/sh
mkdir replays
mkdir train_data_intel

./halite --replay-directory replays/ -vvv --width 32 --height 32 "python3 MyBot.py --not-headless" "python3 MyBot.py --not-headless"
