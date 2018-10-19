import time
import uuid
import numpy as np
import cv2
import math
import logging

from hlt.positionals import Position
from hlt.entity import Shipyard

from QNetwork import Network


class Brain:

    def __init__(self, game, headless=True):
        if headless:
            logging.info("Running in headless mode")

        self.actions = [
            'self.build_ship',
            'self.move_south',
            'self.move_west',
            'self.move_north',
            'self.move_east',
            'self.collect'
        ]

        self.network = Network(headless, len(self.actions))
        self.observer = Observer(game, headless)

        self.reward_map = {

        }

        self.network.draw()

    def choose(self, game):
        self.observer.new_observation()
        self.observer.draw(game)

        # You extract player metadata and the updated map metadata here for convenience.
        me = game.me
        game_map = game.game_map

        state = self.observer.show()


        for ship in me.get_ships():
            a = self.network.select_action(np.array([
                    ship.position.x,
                    ship.position.y
                ]), 
                state, 
                self.actions
            )
            logging.debug(self.actions[a])



class Observer:

    SHIPYARD_COLOR = (0,128,0)
    ENEMY_SHIPYARD_COLOR = (0,0,128)
    SHIP_COLOR = (0,255,0)
    ENEMY_SHIP_COLOR = (0,0,255)
    HARLITE_BASE = (255,0,0)

    def __init__(self, game, headless=True):
        self.id = uuid.uuid4()
        self.headless = headless
        self.map_ration = 8
        self.map_width = 0
        self.map_height = 0
        self.storage = "train_data_intel"
        self.observations = []
        self.map = []
        self.time = str(int(time.time()))
        self.init_map(game.game_map)


    def init_map(self, game_map):
        logging.debug("Setting up map: {}x{}".format(game_map.width, game_map.height))
        self.map_width = game_map.width
        self.map_height = game_map.height


    @staticmethod
    def locateLargest(matrix):
        largest_num = 0
        row = None
        col = None

        for row_idx, row in enumerate(matrix):
            for col_idx, num in enumerate(row):
                if num.halite_amount > largest_num or largest_num is None:
                    largest_num = num.halite_amount
                    row = row_idx
                    col = col_idx

        return largest_num, row, col

    def draw(self, game):
        self.biggest_field, _, _ = self.locateLargest(game.game_map._cells)

        for x in range(0, self.map_width):
            map_x = x
            for y in range(0, self.map_height):
                map_y = y
                self._draw_rectangle(map_x, map_y, (0, 0, 0))

                cell = game.game_map[Position(x, y)]
                self._draw_halite(game, cell, map_x, map_y)

                self._draw_ship(game, cell, map_x, map_y)

                if cell.has_structure:
                    structure = cell.structure
                    self._draw_shipyard(game, structure, map_x, map_y)

    def _draw_halite(self, game, cell, map_x, map_y):
        halite_amount = cell.halite_amount
        halite_percentage = halite_amount / self.biggest_field
        color_value = 255 * halite_percentage
        self._draw_rectangle(map_x, map_y, (color_value, 0, 0))

    def _draw_ship(self, game, cell, map_x, map_y):
        if cell.has_ship:
            if game.me.has_ship(cell.ship.id):
                self._draw_rectangle(map_x, map_y, self.SHIP_COLOR)
            else:
                self._draw_rectangle(map_x, map_y, self.ENEMY_SHIP_COLOR)

    def _draw_shipyard(self, game, structure, map_x, map_y):
        if isinstance(structure, Shipyard):
            if structure.is_owner(game.me):
                self._draw_rectangle(map_x, map_y, self.SHIPYARD_COLOR)
            else:
                self._draw_rectangle(map_x, map_y, self.ENEMY_SHIPYARD_COLOR)

    def _draw_rectangle(self, map_x, map_y, color):
        cv2.rectangle(self.map, (map_x, map_y), (map_x + self.map_ration, map_y + self.map_ration), color, -1)

    def new_observation(self):
        self.map = np.zeros(
            (
                self.map_width,
                self.map_height,
                3
            ),
            np.uint8
        )

    def show(self):
        if not self.headless:
            resized = cv2.resize(self.map, dsize=None, fx=10, fy=10)
            cv2.imshow("Intel - Harlite - {}".format(self.id), resized)
            cv2.waitKey(1)

        return self.map
