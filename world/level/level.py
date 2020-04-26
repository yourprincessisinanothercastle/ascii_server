from typing import List, NamedTuple
from world.creatures import Creature, Blob, Player
from world.level.map import Map

import logging
logger = logging.getLogger(__name__)

LevelBudget = NamedTuple("level_budget", [
    ("monster_pool", List[Creature]),  # possible subset of monsters to draw from
    ("entity_points", int),
    ("tile_points", int)
])


class Level:
    map: Map

    def __init__(self, map_generator):
        self.players = []
        self.creatures = []

        self.map_generator = map_generator
        
        self.field_of_view_needs_update = True

    def _reset_tiles_visible(self):
        """
        part of update_field_of_view
        resets all tiles to not visible
        
        :return: 
        """
        for y_coord, row in self.map.tiles.items():
            for x_coord, tile in row.items():
                tile.is_visible = False
                tile.needs_update = True

    def update_field_of_view(self):
        """
        update all tiles to current is_visible status

        :return: 
        """
        if self.field_of_view_needs_update:
            self._reset_tiles_visible()
            for player in self.players:
                logger.debug('updating fov')
                player.update_fov()
            self.field_of_view_needs_update = False

    def init(self):
        self.map = Map(self.map_generator)
        
        # todo: base on data from generator
        self.spawn_creature(Blob())

    def remove_player(self, player: Player):
        logger.info('removing %s from area %s' % (player, self))
        self.players.remove(player)
        player.room = None

    def remove_creature(self, creature: Creature):
        self.creatures.remove(creature)
        creature.room = None

    def spawn_player(self, player: Player):
        logger.info('adding %s to area %s' % (player, self))
        if player.room:
            player.room.remove_player(player)
        player.room = self
        self.players.append(player)
        x, y = self.map.get_player_spawn()
        player.set_coords(x, y)

    def spawn_creature(self, creature: Creature, x=None, y=None):
        if not x or y:
            x, y = self.map.get_creature_spawn()
        logger.info('spawning %s at (%s, %s)' % (creature, x, y))

        if creature.room:
            creature.room.remove_creature(creature)

        creature.room = self
        self.creatures.append(creature)

        creature.set_coords(x, y)
