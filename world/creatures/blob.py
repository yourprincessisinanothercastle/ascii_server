import logging

from util.coord_helpers import distance
from util.field_of_view import fov
from world.creatures._creature import Creature
from world.creatures.player import Player

logger = logging.getLogger(__name__)


class Blob(Creature):
    type = 'blob'

    ACTION_TIME = dict(
        move=2.,
        hit=.20
    )

    def __init__(self):
        super().__init__(0, 0)
        self.direction = Creature.DIRECTIONS['left']

        self.view_radius = 10
        self.update_sent = False
        self.color = 200

        self._visible_tile_coords = []  # temporary list to check if players are visible

    def _visit(self, x, y):
        '''
        called for every visible tile
        needs to return true if tile blocks sight
        '''

        self._visible_tile_coords.append((x, y))
        if y > len(self.room.map.tiles) - 1 or y < 0:
            return True
        if x > len(self.room.map.tiles[y]) - 1 or x < 0:
            return True
        return self.room.map.tiles[y][x].block_sight

    def get_closest_player(self):
        closest_player = None
        closest_player_distance = None

        # update visible tile coords
        self._visible_tile_coords = []
        fov(self.x, self.y, self.view_radius, self._visit)

        # get players on visible tiles
        for player in self.room.players:
            if (player.x, player.y) in self._visible_tile_coords:
                distance_player = distance(self.x, self.y, player.x, player.y)
                if not closest_player_distance or \
                        closest_player_distance > distance_player:
                    closest_player = player
                    closest_player_distance = distance_player
        return closest_player

    def update(self):
        logger.info('updating blob')
        closest_player: Player = self.get_closest_player()
        if closest_player:
            if closest_player.x < self.x:
                dx = -1
            elif closest_player.x > self.x:
                dx = 1
            else:
                dx = 0
            if closest_player.y < self.y:
                dy = -1
            elif closest_player.y > self.y:
                dy = 1
            else:
                dy = 0
            self.add_action(self.move, dx, dy, flush=True)
