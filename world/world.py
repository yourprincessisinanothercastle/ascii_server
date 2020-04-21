import logging
from typing import List

from util.field_of_view import fov
from world.rooms.map_generators import DummyGenerator
from world.rooms.room import Room

logger = logging.getLogger(__name__)


class World:
    def __init__(self):
        self.players = []
        self.rooms: List[Room] = []
        self.start_room: Room = None

        self.structure = None

        self.init_world()

    def init_world(self):
        self.start_room = Room(DummyGenerator)
        self.start_room.init()
        self.rooms.append(self.start_room)

    def add_player(self, player):
        self.players.append(player)
        return player

    def tick(self, dt):
        for player in self.players:
            player.process_action_queue(dt)    
            if player.fov_needs_update:
                logger.debug('updating fov')
                for idx_row, row in enumerate(player.room.map.tiles):
                    for idx_column, column in enumerate(player.room.map.tiles[idx_row]):
                        player.room.map.tiles[idx_row][idx_column].is_visible = False
                fov(player.x, player.y, player.view_radius, player.room.map.update_visible)
                player.fov_needs_update = False
        
        for room in self.rooms:
            for creature in room.creatures:
                creature.process_action_queue(dt)

