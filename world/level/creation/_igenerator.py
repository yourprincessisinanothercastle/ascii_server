import json
from typing import List, NamedTuple, Tuple
from abc import ABC, abstractmethod
from world.entity import Entity

import logging
logger = logging.getLogger(__name__)


# structure used for tile-based generators (level & area generators)
GeneratorOutput = NamedTuple("area_generator_result", [
    ("entities", List[Entity]),
    ("tiles", List[List[str]]),
    ("player_spawn_areas", List[Tuple[int, int]])
])

tile_abbreviation_definitions = {
    "W": "wall",
    ".": "floor",
    "_": None
}

class IGenerator(ABC):
    """
    common functionality shared between tile-based generators
    """
    def __init__(self):
        self._tiles: List[List[str]] = []
        self._entities: List[Entity] = []

    def draw(self):
        """ preview output """
        chars = dict(
            wall='W',
            floor='.'
        )
        for row_idx, row in enumerate(self._tiles):
            drawn_row = [chars[tile] for tile in row]
            print(''.join(drawn_row))

    def as_json(self):
        return json.dumps(GeneratorOutput(entities=self._entities, tiles=self._tiles))

    @abstractmethod
    def generate(self) -> GeneratorOutput:
        raise NotImplementedError
