from typing import List, Tuple, NamedTuple, Type
from world.entity import Entity
from world.level.creation import IGenerator, GeneratorOutput
from world.level.creation.entity import EntityBudget, EntityGenerator

import logging
logger = logging.getLogger(__name__)

AreaBudget = NamedTuple("area_budget", [
    ("doorways", List[Tuple[int, int]]),  # coordinate offset tuples left open (pos = from start, neg = from end)
    ("tile_points", int)  # like for level_budget, tile_points do NOT equal actual tiles generated
])


class AreaGenerator(IGenerator):
    """
    An "area" is a themed generated place on a level with a specific shape and content.
    It could be a square room with only blob monsters or a large open area with diverse enemies.
    """
    area_budget: AreaBudget
    entity_budget: EntityBudget

    # noinspection PyMethodOverriding
    def generate(self, area_budget: AreaBudget = AreaBudget(tile_points=0,
                                                            doorways=[]),
                 entity_budget: EntityBudget = EntityBudget(monster_pool=[],
                                                            entity_points=0,
                                                            level_connect_number=-1)) -> GeneratorOutput:
        """ Starts generating an area subset of a level """
        self.area_budget = area_budget
        self.entity_budget = entity_budget

        self._tiles = self._generate_tiles()
        self._entities = self._generate_entities()

        return GeneratorOutput(self._entities, self._tiles)

    # this method mostly exists on its own for easy overriding (for handmade rooms, etc)
    def _generate_entities(self) -> List[Entity]:
        return EntityGenerator().generate(self.entity_budget, self._tiles).entities

    # implement in subclass - this is a test output
    def _generate_tiles(self) -> List[List[str]]:
        W = 'wall'
        F = 'floor'

        return [
            [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
            [W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
            [W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
            [W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
            [W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
            [W, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, F, W],
            [W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
            [W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W, W, F, F, F, F, F, F, W],
            [W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W],
        ]

