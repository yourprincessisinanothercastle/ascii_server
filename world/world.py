from typing import List
from world.level.creation import LevelGenerator
from world.level.level import Level

import logging
logger = logging.getLogger(__name__)


class World:

    def __init__(self):
        self.difficulty = 1
        self.players = []
        self.levels: List[Level] = []
        self.start_level: Level = None

        self.structure = None

        self.init_world()

    def init_world(self):
        # TODO add func to progress the world with next level (generated lvl exits gets and incremented lvl_nr maybe)
        level_generator = LevelGenerator(len(self.levels) + 1, self.difficulty)
        self.start_level = Level(level_generator)
        self.start_level.init()
        self.levels.append(self.start_level)

    def add_player(self, player):
        self.players.append(player)
        self.start_level.spawn_player(player)
        
    def remove_player(self, player):
        if player.floor:
            player.floor.remove_entity(player)
        self.players.remove(player)

    def tick(self, dt):
        for player in self.players:
            player.process_action_queue(dt)

        for level in self.levels:
            level.update_field_of_view()
            for creature in level.creatures:
                creature.process_action_queue(dt)
