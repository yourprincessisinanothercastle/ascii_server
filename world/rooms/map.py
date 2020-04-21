import json
import logging
import random

from world.rooms.tiles import TILE_MAP

logger = logging.getLogger(__name__)


class Map:
    def __init__(self, generator=None):
        self._layers = []
        # todo: doors, connections to other rooms
        self.map = json.loads(generator().as_json())

        self.tiles = self._tiles_from_map_json()

    def _tiles_from_map_json(self):
        result = {}
        for row_idx, row in enumerate(self.map):
            for col_idx, col in enumerate(row):
                tile_type_at_index = self.map[row_idx][col_idx]
                tile_class_at_index = TILE_MAP[tile_type_at_index]
                result[row_idx][col_idx] = tile_class_at_index()
        return result

    def update_visible(self, x, y):
        '''
        needed for fov
        '''

        if y > len(self.tiles) - 1:
            return True
        if x > len(self.tiles[y]) - 1:
            return True

        self.tiles[y][x].is_visible = True
        self.tiles[y][x].seen = True

        return self.tiles[y][x].block_sight

    def _random_coords(self, x1, y1, x2, y2):
        return random.randint(x1, x2), random.randint(y1, y2)
    
    def get_player_spawn(self):
        random_spawn_area = random.choice(self.map['player_spawn_areas'])
        return self._random_coords(*random_spawn_area)

    def get_creature_spawn(self):
        random_spawn_area = random.choice(self.map['creature_spawn_areas'])
        return self._random_coords(*random_spawn_area)

    def draw(self):
        result = []
        for row in self.tiles:
            result_row = [tile.char for tile in row]
            result.append(result_row)
        return result
