from typing import List
from world.level.creation.area import SquareRoom
from world.level.level import Level

import logging
logger = logging.getLogger(__name__)


class World:
    def __init__(self):
        self.players = []
        self.rooms: List[Level] = []
        self.start_room: Level = None

        self.structure = None

        self.init_world()

    def init_world(self):
        self.start_room = Level(SquareRoom)  # TODO fix to use the level_generator
        self.start_room.init()
        self.rooms.append(self.start_room)

    def add_player(self, player):
        self.players.append(player)
        self.start_room.spawn_player(player)
        
    def remove_player(self, player):
        if player.room:
            player.room.remove_player(player)
        self.players.remove(player)

    def tick(self, dt):
        for player in self.players:
            player.process_action_queue(dt)

        for room in self.rooms:
            room.update_field_of_view()
            for creature in room.creatures:
                creature.process_action_queue(dt)
