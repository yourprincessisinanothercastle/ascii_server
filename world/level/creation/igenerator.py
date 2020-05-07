import json
from typing import List, Tuple, NamedTuple
from abc import ABC, abstractmethod
from world.entity import Entity

import logging
logger = logging.getLogger(__name__)

# structure used for all generators - not all fields are populated by each generator
GeneratorOutput = NamedTuple("generator_output", [
    ("entities", List[Entity]),
    ("tiles", List[List[str]]),
    ("player_spawn_areas", List[Tuple[int, int]])
])


class IGenerator(ABC):
    """
    common functionality shared between generators
    """
    def __init__(self):
        self._tiles: List[List[str]] = []
        self._entities: List[Entity] = []
        self._player_spawn_areas: List[Tuple[int, int]] = []

    def draw(self, debug=False):
        """ preview output (debug allows non-tile names, trimmed to last char) """
        chars = dict(
            wall='-',
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
                                          tiles=self._tiles,
                                          player_spawn_areas=self._player_spawn_areas))

    @abstractmethod
    def generate(self) -> GeneratorOutput:
        raise NotImplementedError
