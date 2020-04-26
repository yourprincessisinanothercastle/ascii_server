from typing import TYPE_CHECKING, List
from world.entity import Entity
from world.level.creation import IGenerator, GeneratorOutput
from world.level.creation.area.entity import EntityBudget, EntityGenerator

import logging
logger = logging.getLogger(__name__)


class AreaGenerator(IGenerator):
    """
    An "area" is a themed generated place on a level with a specific shape and content.
    It could be a square room with only blob monsters or a large open area with diverse enemies.
    """
    # noinspection PyMethodOverriding
    def generate(self, entity_budget: EntityBudget,
                 player_spawn_count: int = 0, has_exit: bool = False) -> GeneratorOutput:
        """ Starts generating an area subset of a level """
        self._tiles = self._generate_tiles()
        self._entities = self._generate_entities(entity_budget, self._tiles, player_spawn_count, has_exit)
        return GeneratorOutput([], [])

    # this method only exists on its own for easy overriding (for handmade rooms, etc)
    def _generate_entities(self, entity_budget: EntityBudget,
                           tiles: List[List[str]],
                           player_spawn_count: int,
                           has_exit: bool) -> List[Entity]:
        return EntityGenerator().generate(entity_budget, tiles, player_spawn_count, has_exit)

    # implement in subclass
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

