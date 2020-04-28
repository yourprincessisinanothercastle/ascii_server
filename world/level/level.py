
from world.entity import Entity
from world.creatures import Player
from world.level.map import Map

import logging
logger = logging.getLogger(__name__)


class Level:
    map: Map

    def __init__(self, map_generator):
        self.players = []
        self.creatures = []
        self.entities = []

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
        for entity in self.map.entities:
            # todo: base on data from generator
            self.spawn_entity(entity)

    def remove_entity(self, entity: Entity):
        logger.info('removing entity %s from level: %s' % (entity, self))
        self.entities.remove(entity)
        entity.floor = None

    def spawn_entity(self, entity: Entity):
        logger.info('adding entity %s to level: %s' % (entity, self))
        # this will only attach an entity to current game-level, coordinates should already be generated within it
        # TODO add func to spawn entity at player spawn areas if they somehow move between levels - IF we allow this
        if entity.floor:
            entity.floor.remove_entity(entity)
        entity.floor = self
        self.entities.append(entity)

    def spawn_player(self, player: Player):
        logger.info('adding player %s to level %s' % (player, self))
        if player.floor:
            player.floor.remove_entity(player)
        player.floor = self
        self.players.append(player)
        x, y = self.map.get_player_spawn()
        player.set_coords(x, y)
