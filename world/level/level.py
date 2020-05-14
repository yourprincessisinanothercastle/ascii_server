from typing import TYPE_CHECKING
from world.entity import Entity
from world.creatures import Player
from world.level.map import Map

if TYPE_CHECKING:
    from world.world import World

import logging
logger = logging.getLogger(__name__)


class Level:
    world: 'World'
    map: Map
    level_number: int

    def __init__(self, world: 'World', level_generator):
        self.world = world
        self.players = []
        self.entities = []

        self.level_generator = level_generator
        
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

    def init(self, level_nr: int):
        self.level_number = level_nr
        self.map = Map(self.level_generator)
        for entity in self.map.entities:
            logger.info('adding %s at %s, %s' % (entity, entity.x, entity.y))
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

    def spawn_player(self, player: Player, coming_from_level_nr: int = None):
        logger.info('adding player %s to level %s' % (player, self))
        if player.floor:
            player.floor.remove_entity(player)
        player.floor = self
        self.players.append(player)
        x, y = self.map.get_player_spawn(coming_from_level_nr)
        player.set_coords(x, y)
    
    def remove_player(self, player: Entity):
        logger.info('removing player %s from level: %s' % (player, self))
        self.players.remove(player)
        player.floor = None

    def exit_entity(self, entity: Entity, to_level_nr: int, from_level_nr: int):
        level = self.world.get_level(to_level_nr)
        if isinstance(entity, Player):
            self.remove_player(entity)
            level.spawn_player(entity, from_level_nr)
        else:
            self.remove_entity(entity)
            level.spawn_entity(entity, from_level_nr)
