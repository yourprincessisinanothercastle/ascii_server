from typing import List

from world.entity import ENTITY_TYPE
from world.level.creation import LevelGenerator
from world.level.level import Level

import logging

logger = logging.getLogger(__name__)


class World:

    def __init__(self):
        self.difficulty = 1
        self.players = []
        self.levels: List[Level or None] = []  # assume level 1 is index 0, and so on...
        self.start_level: Level or None = None

        self.structure = None

        self.init_world()

    def init_world(self):
        # TODO add func to progress the world with next level (generated exits have lvl_nrs we can match)
        level = self.get_level(1)
        self.start_level = level

    def get_level(self, level_nr: int):
        if len(self.levels) >= level_nr:
            level = self.levels[level_nr - 1]
            if not level:  # we get here if we at some point jumped several levels ahead
                level = self.create_level(level_nr)
                self.levels[level_nr - 1] = level
        else:
            level = self.create_level(level_nr)
            while not len(self.levels) < level_nr:
                self.levels.append(None)  # placeholders for when we skip ahead multiple levels
            self.levels.append(level)
        return level

    def create_level(self, level_nr: int):
        level = Level(self, LevelGenerator(level_nr=level_nr, difficulty=self.difficulty))
        level.init(level_nr)
        return level

    def add_player(self, player):
        self.players.append(player)
        self.start_level.spawn_player(player)

    def remove_player(self, player):
        if player.floor:
            player.floor.remove_player(player)
        self.players.remove(player)

    def tick(self, dt):
        for player in self.players:
            player.process_action_queue(dt)

        for level in self.levels:
            level.update_field_of_view()
            for entity in level.entities:
                entity.update()
                if entity.entity_type == ENTITY_TYPE['creature']:
                    entity.process_action_queue(dt)
