import random
from typing import List, Tuple
from world.entity import Entity
from world.interactables import LevelExit
from world.level.creation._invalid_output import InvalidOutputException
from world.level.tile import TILE_MAP, Tile
from world.level.creation import GeneratorOutput, LevelGenerator

import logging
logger = logging.getLogger(__name__)

TILE_SIZE = 3


class Map:
    def __init__(self, level_generator: LevelGenerator = None):
        # todo: connections between levels
        self._level_generator: LevelGenerator = level_generator
        self._map: GeneratorOutput = self._level_generator.generate()
        self.entities: List[Entity] = self._map.entities
        self.tiles: dict = self._tiles_from_map_json()

    def get_tile(self, row, col) -> Tile or None:
        """ allows for out of bounds lookup, to enable sweeping checks """
        try:
            return self.tiles[row][col]
        except IndexError:
            return None

    def _tiles_from_map_json(self) -> dict:
        result = {}

        for map_row_idx, row in enumerate(self._map.tiles):
            for x in range(TILE_SIZE):
                # scale up in height
                tile_row_idx = map_row_idx * TILE_SIZE + x
                result[tile_row_idx] = {}

                for map_col_idx, col in enumerate(row):
                    # scale up in width
                    for y in range(TILE_SIZE):
                        tile_col_idx = map_col_idx * TILE_SIZE + y
                        tile_type_at_index = self._map.tiles[map_row_idx][map_col_idx]
                        tile_class_at_index = TILE_MAP[tile_type_at_index]

                        result[tile_row_idx][tile_col_idx] = tile_class_at_index()
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

    def random_coords(self, x1_y1, x2_y2):
        # TODO not in use right now (originally for player spawn location) but maybe this is useful later...
        x1, y1 = x1_y1
        x2, y2 = x2_y2
        return random.randint(x1 * TILE_SIZE, x2 * TILE_SIZE), random.randint(y1 * TILE_SIZE, y2 * TILE_SIZE)

    def get_player_spawn(self, coming_from_level_nr: int = None):
        """
        The idea is that we match exits by their level_number, to move up and down levels freely
        If no level is supplied, we pick the lowest level_nr exit
        """
        entrance = None
        for entity in self._map.entities:
            if isinstance(entity, LevelExit):
                if coming_from_level_nr:
                    if entity.level_number == coming_from_level_nr:
                        entrance = entity
                else:
                    if not entrance or entrance.level_number > entity.level_number:
                        entrance = entity

        if not entrance:
            raise InvalidOutputException("No exit matched as entrance, cannot choose spawn area")
        else:
            viable_tiles = list(filter(lambda a: bool(a),  self.get_adjacent(entrance.x, entrance.y)))
            spawn_area = random.choice(viable_tiles)[1]
            return spawn_area

    def get_adjacent(self, x: int, y: int) -> List[Tuple[str or None, Tuple[int, int]]]:
        """ Collect all 8 tiles around target, inkl coords for each"""
        # TODO make it dynamic so we can radiate outwards from center, asked by radius
        return [
            (self.get_tile(y - 1, x - 1), (y - 1, x - 1)),
            (self.get_tile(y, x - 1), (y, x - 1)),
            (self.get_tile(y + 1, x - 1), (y + 1, x - 1)),
            (self.get_tile(y - 1, x), (y - 1, x)),
            (self.get_tile(y + 1, x), (y + 1, x)),
            (self.get_tile(y - 1, x + 1), (y - 1, x + 1)),
            (self.get_tile(y, x + 1), (y, x + 1)),
            (self.get_tile(y + 1, x + 1), (y + 1, x + 1))
        ]

    def draw(self):
        # TODO is this function redundant now that a generator can draw the current map?
        result = []
        for row in self.tiles:
            result_row = [tile.char for tile in row]
            result.append(result_row)
        return result
