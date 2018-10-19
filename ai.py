import math
import logging

from QNetwork import Network
from Observer import Observer

import hlt.commands as commands


class Brain:

    def __init__(self, game, headless=True):
        if headless:
            logging.info("Running in headless mode")

        self.actions = [
            self.build_ship,
            self.move_south,
            self.move_west,
            self.move_north,
            self.move_east,
            self.stay_still
        ]

        self.network = Network(headless, len(self.actions))
        self.observer = Observer(game, headless)

        self.reward_map = {
            self.build_ship: [0, -10],
            self.move_south: [0, -10],
            self.move_west: [0, -10],
            self.move_north: [0, -10],
            self.move_east: [0, -10],
            self.stay_still: [1, -10]
        }

        self.network.draw()

        self.observer.new_observation()
        self.observer.draw(game)
        self.state = self.observer.show()
        self.command_queue = []


    def choose(self, game):

        # You extract player metadata and the updated map metadata here for convenience.
        me = game.me
        game_map = game.game_map

        # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
        #   end of the turn.
        self.command_queue = []
        try:
            self.act_on(me.shipyard)
            
            for ship in me.get_ships():
                self.act_on(ship)


        except Exception as e:
            logging.error(e)
            pass

        game.end_turn(self.command_queue)

        game.update_frame()
        self.observer.new_observation()
        self.observer.draw(game)

        self.state = self.observer.show()



    def act_on(self, entity):
        a = self.network.select_action([
                entity.position.x,
                entity.position.y,
                entity.harlite_amount,
            ], 
            self.state, 
            self.actions
        )
        self.command_queue.append(self.call(a, entity))

    def call(self, a, entity):
        logging.info("=============== ACTION {:03} ================".format(a))
        logging.debug(entity)
        execute_action = self.actions[a]
        logging.debug(execute_action)
        return execute_action(entity)

    def build_ship(self, entity):
        logging.info("build_ship ({}({}))@[{} {}]".format(entity.id, type(entity), entity.position.x, entity.position.y))
        logging.debug(entity)
        return entity.spawn()

    def move_south(self, entity):
        logging.info("move_south ({}({}))@[{} {}]".format(entity.id, type(entity), entity.position.x, entity.position.y))
        logging.debug(entity)
        return entity.move(commands.SOUTH)

    def move_west(self, entity):
        logging.info("move_west ({})({})@[{} {}]".format(entity.id, type(entity), entity.position.x, entity.position.y))
        logging.debug(entity)
        return entity.move(commands.WEST)

    def move_north(self, entity):
        logging.info("move_north ({}({}))@[{} {}]".format(entity.id, type(entity), entity.position.x, entity.position.y))
        logging.debug(entity)
        return entity.move(commands.NORTH)

    def move_east(self, entity):
        logging.info("move_east ({})({})@[{} {}]".format(entity.id, type(entity), entity.position.x, entity.position.y))
        logging.debug(entity)
        return entity.move(commands.EAST)

    def stay_still(self, entity):
        logging.info("stay_still ({}({}))@[{} {}]".format(entity.id, type(entity), entity.position.x, entity.position.y))
        logging.debug(entity)
        return entity.stay_still()

    def make_dropof(self, entity):
        logging.info("make_dropof ({({})})@[{} {}]".format(entity.id, type(entity), entity.position.x, entity.position.y))
        logging.debug(entity)
        return entity.make_dropoff()



