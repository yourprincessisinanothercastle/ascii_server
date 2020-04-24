from util.field_of_view import fov
from world.creatures._creature import Creature
from world.creatures.player import Player
from world.rooms.map import Map
import logging

logger = logging.getLogger(__name__)

class Room():
    def __init__(self, map_generator):
        self.map: Map = None
        self.players = []
        self.creatures = []

        self.map_generator = map_generator
        
        self.field_of_view_needs_update = True

    def reset_tiles_visible(self):
        for y_coord, row in self.map.tiles.items():
            for x_coord, tile in row.items():
                tile.is_visible = False
                tile.needs_update = True

    def update_field_of_view(self):
        if self.field_of_view_needs_update:
            self.reset_tiles_visible()
            for player in self.players:
                logger.debug('updating fov')
                fov(player.x, player.y, player.view_radius, self.map.update_visible)
            self.field_of_view_needs_update = False

    def init(self):
        self.map = Map(self.map_generator)

    def remove_player(self, player: Player):
        logger.info('removing %s from room %s' % (player, self))
        self.players.remove(player)
        player.room = None

    def remove_creature(self, creature: Creature):
        self.creatures.remove(creature)
        creature.room = None

    def spawn_player(self, player: Player):
        logger.info('adding %s to room %s' % (player, self))
        if player.room:
            player.room.remove_player(player)
        player.room = self
        self.players.append(player)
        x, y = self.map.get_player_spawn()
        player.set_coords(x, y)

    def spawn_creature(self, creature: Creature, x=None, y=None):
        if creature.room:
            creature.room.remove_creature(creature)
        creature.room = self
        self.creatures.append(creature)
        if not x and y:
            x, y = self.map.random_creature_spawn()
        creature.set_coords(x, y)
