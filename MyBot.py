#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

# This library allows you to generate random numbers.
import random
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--not-headless', dest='headless', action='store_const',
                    const=False, default=True,
                    help='run not headless')

parser.add_argument('--log-level', dest='log_level', action='store',
                    default=logging.INFO, help='what log level')

args = parser.parse_args()

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging
import ai


""" <<<Game Begin>>> """
game = hlt.Game(log_level=args.log_level)
brain = ai.Brain(game, args.headless)

game.ready("HelBot")
""" <<<Game Loop>>> """

while True:

    # Send your moves back to the game environment, ending this turn.
    brain.choose(game)
