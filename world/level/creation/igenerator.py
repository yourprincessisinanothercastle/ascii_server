import json
from typing import List, NamedTuple, Tuple
from abc import ABC, abstractmethod
from world.entity import Entity

import logging
logger = logging.getLogger(__name__)

# structure used for all generators - not all fields are populated by each generator
GeneratorOutput = NamedTuple("generator_output", [
    ("entities", List[Entity]),
    ("tiles", List[List[str]])
])


class IGenerator(ABC):
    """
    common functionality shared between generators
    """
    def __init__(self):
        self._tiles: List[List[str]] = []
        self._entities: List[Entity] = []

    def draw(self, debug=False):
        """ preview output (debug allows non-tile names, trimmed to last char) """
        chars = dict(
            none='-',
            wall='W',
            floor='.'
        )
        for row_idx, row in enumerate(self._tiles):
            drawn_row = []
            for tile in row:
                if not debug or tile in chars:
                    drawn_row.append(chars[tile])
                elif debug:
                    drawn_row.append(str(tile)[-1])
            print(''.join(drawn_row))

    def as_json(self):
        return json.dumps(GeneratorOutput(entities=self._entities,
                                          tiles=self._tiles))

    def get_tile(self, x: int, y: int) -> str or None:
        """ Use in iterative checks to avoid index-errors """
        try:
            return self._tiles[x][y]
        except IndexError:
            return None

    def get_adjacent(self, x: int, y: int) -> List[Tuple[str or None, Tuple[int, int]]]:
        """ Collect all 8 tiles around target, inkl coords for each"""
        # TODO make it dynamic so we can radiate outwards from center, asked by radius
        return [
            (self.get_tile(x - 1, y - 1), (x - 1, y - 1)),
            (self.get_tile(x - 1, y), (x - 1, y)),
            (self.get_tile(x - 1, y + 1), (x - 1, y + 1)),
            (self.get_tile(x, y - 1), (x, y - 1)),
            (self.get_tile(x, y + 1), (x, y + 1)),
            (self.get_tile(x + 1, y - 1), (x + 1, y - 1)),
            (self.get_tile(x + 1, y), (x + 1, y)),
            (self.get_tile(x + 1, y + 1), (x + 1, y + 1))
        ]

    @abstractmethod
    def generate(self) -> GeneratorOutput:
        raise NotImplementedError
