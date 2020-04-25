import json
import logging
import random

from world.level.tile import TILE_MAP, Tile

logger = logging.getLogger(__name__)


class Map:
    def __init__(self, generator_class=None):
        # todo: doors, connections to other level
        generator = generator_class()
        self._map = generator.get_map()
        self.tiles = self._tiles_from_map_json()

    def get_tile(self, row, col) -> Tile:
        return self.tiles[row][col]

    def _tiles_from_map_json(self):
        result = {}

        tiles = self._map['tiles']
        for row_idx, row in enumerate(tiles):
            result[row_idx] = {}
            for col_idx, col in enumerate(row):
                tile_type_at_index = tiles[row_idx][col_idx]
                tile_class_at_index = TILE_MAP[tile_type_at_index]
                result[row_idx][col_idx] = tile_class_at_index()

        return result

    def serialize_init_state(self):
        """
        init map for new joined clients

        get all seen tiles
        :return: 
        """
        result = []
        for y_coord, row in self.tiles.items():
            for x_coord, tile in row.items():
                if tile.seen:
                    serialized_tile = [(x_coord, y_coord), tile.name, tile.serialize_attributes()]
                    result.append(serialized_tile)
        return result

    def serialize_update_state(self):
        """
        update map for clients

        get all seen tiles with 'needs_update'
        :return: 
        """

        result = []
        for y_coord, row in self.tiles.items():
            for x_coord, tile in row.items():
                if tile.seen and tile.needs_update:
                    serialized_tile = [(x_coord, y_coord), tile.name, tile.serialize_attributes()]
                    result.append(serialized_tile)
        return result

    def set_tile_update_sent(self):
        for y_coord, row in self.tiles.items():
            for x_coord, tile in row.items():
                tile.needs_update = False

    def update_visible(self, x, y):
        '''
        needed for fov
        '''

        if y > len(self.tiles) - 1 or y < 0:
            return True

        if x > len(self.tiles[y]) - 1 or x < 0:
            return True

        self.tiles[y][x].is_visible = True
        self.tiles[y][x].seen = True
        self.tiles[y][x].needs_update = True

        return self.tiles[y][x].block_sight

    def _random_coords(self, x1_y1, x2_y2):
        x1, y1 = x1_y1
        x2, y2 = x2_y2
        return random.randint(x1, x2), random.randint(y1, y2)

    def get_player_spawn(self):
        random_spawn_area = random.choice(self._map['player_spawn_areas'])
        print(random_spawn_area)
        return self._random_coords(*random_spawn_area)

    def get_creature_spawn(self):
        random_spawn_area = random.choice(self._map['creature_spawn_areas'])
        return self._random_coords(*random_spawn_area)

    def draw(self):
        result = []
        for row in self.tiles:
            result_row = [tile.char for tile in row]
            result.append(result_row)
        return result
