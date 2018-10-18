import time
import uuid
import numpy as np
import cv2
import math
# from keras import Sequential, Dense, InputLayer
from keras.models import Sequential
from keras.layers import Dense, InputLayer

from hlt.positionals import Position
from hlt.entity import Shipyard



class Brain:

    SHIPYARD_COLOR = (0,128,0)
    ENEMY_SHIPYARD_COLOR = (0,0,128)
    SHIP_COLOR = (0,255,0)
    ENEMY_SHIP_COLOR = (0,0,255)
    HARLITE_BASE = (255,0,0)

    def __init__(self, game, headless=True):
        self.network = QNetwork()
        self.observer = Observer(game, headless)


        self.actions = []
        self.reward_map = {

        }

    def choose(self, game):
        self.observer.new_observation()
        self.observer.draw(game)

        state = self.observer.show()




class QNetwork:
    def __init__(self, state):
        self.model = Sequential()
        self.model.add(InputLayer(batch_input_shape=(1, 5)))
        self.model.add(Dense(10, activation='sigmoid'))
        self.model.add(Dense(2, activation='linear'))
        self.model.compile(loss='mse', optimizer='adam', metrics=['mae'])

        self.s = state
        self.y = 0
        self.eps = 0.5
        self.decay_factor = 0.999

    def predict(self, r, new_s, actions):
        self.eps *= self.decay_factor

        a = self.select_action(actions)
        self.learn(r, a, new_s)

        self.s = new_s

    def select_action(self, actions):

        if np.random.random() < self.eps:
            a = np.random.randint(0, 2)
        else:
            a = np.argmax(self._predict(self.s))

        return a

    def learn(self, r, a, new_s):
        target = r + self.y * np.max(self._predict(new_s))
        target_vec = self._predict(self.s)[0]
        target_vec[a] = target

        self.model.fit(np.identity(5)[s:s + 1], target_vec.reshape(-1, 2), epochs=1, verbose=0)

    def _predict(self, s):
        return self.model.predict(np.identity(5)[s:s + 1])

class Observer:
    def __init__(self, game, headless=True):
        self.id = uuid.uuid4()
        self.headless = headless
        self.map_ration = 8
        self.view_size = self.map_ration * 15
        self.init_map(game)
        self.storage = "train_data_intel"
        self.observations = []
        self.map = []
        self.time = str(int(time.time()))
        self.map_width = 0
        self.map_height = 0
        self.map_ratio_to_view = 0


    def init_map(self, game):
        self.map_width = game.game_map.width
        self.map_height = game.game_map.height
        self.map_ratio_to_view = math.ceil(self.view_size / game.game_map.width)


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
            map_x = x * self.map_ratio_to_view
            for y in range(0, self.map_height):
                map_y = y * self.map_ratio_to_view
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
        cv2.rectangle(self.map, (map_x, map_y), (map_x + self.map_ration * self.map_ratio_to_view, map_y + self.map_ration * self.map_ratio_to_view), color, -1)

    def new_observation(self):
        if len(self.map):
            self.observations.append([[], self.map])

        if len(self.observations) % 10 == 0:
            self.store()

        self.map = np.zeros(
            (
                self.view_size,
                self.view_size,
                3
            ),
            np.uint8
        )

    def store(self):
        storeTo = "{}/{}-{}.npy".format(
            self.storage,
            self.time,
            self.id
        )
        np.save(storeTo, np.array(self.observations))

    def show(self):
        if not self.headless:
            resized = cv2.resize(self.map, dsize=None, fx=2, fy=2)
            cv2.imshow("Intel - Harlite - {}".format(self.id), resized)
            cv2.waitKey(1)

        return self.map
