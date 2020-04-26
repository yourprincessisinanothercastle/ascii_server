import json
from typing import List, NamedTuple
from abc import ABC, abstractmethod
from world.entity import Entity

import logging
logger = logging.getLogger(__name__)

# structure used for tile-based generators (level & area generators)
GeneratorOutput = NamedTuple("area_generator_result", [
    ("entities", List[Entity]),
    ("tiles", List[List[str]])
])


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
            wall='#',
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
