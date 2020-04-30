from typing import List, Tuple, NamedTuple, Type
from world.entity import Entity
from world.level.creation import IGenerator, GeneratorOutput
from world.level.creation.entity import EntityBudget, EntityGenerator

import logging
logger = logging.getLogger(__name__)

AreaBudget = NamedTuple("area_budget", [
    ("doorways", List[Tuple[int, int]]),  # coordinate tuples for connecting areas
    ("tile_points", int)  # like for level_budget, tile_points do NOT equal actual tiles generated
])


class AreaGenerator(IGenerator):
    """
    An "area" is a themed generated place on a level with a specific shape and content.
    It could be a square room with only blob monsters or a large open area with diverse enemies.
    """
    area_budget: AreaBudget
    entity_budget: EntityBudget

    _tiles: List[List[str]]
    _entities: List[Entity]
    _player_spawn_areas: List[Tuple[Tuple[int, int], Tuple[int, int]]]

    # noinspection PyMethodOverriding
    def generate(self, area_budget: AreaBudget = AreaBudget(tile_points=0,
                                                            doorways=[]),
                 entity_budget: EntityBudget = EntityBudget(monster_pool=[],
                                                            entity_points=0,
                                                            has_exit=False),
                 player_spawn_area_count: int = 1) -> GeneratorOutput:
        """ Starts generating an area subset of a level """
        self.area_budget = area_budget
        self.entity_budget = entity_budget

        self._tiles = self._generate_tiles()
        self._entities = self._generate_entities()
        self._player_spawn_areas = self._generate_player_spawn_areas(player_spawn_area_count)

        return GeneratorOutput(self._entities, self._tiles, self._player_spawn_areas)

    def _generate_player_spawn_areas(self, player_spawn_area_count: int) -> ((int, int), (int, int)):
        # TODO implement real generation based on tiles
        def get_valid_location():
            return (1, 1), (2, 2)

        return [get_valid_location() for i in range(player_spawn_area_count)]

    # this method mostly exists on its own for easy overriding (for handmade rooms, etc)
    def _generate_entities(self) -> List[Entity]:
        return EntityGenerator().generate(self.entity_budget, self._tiles)

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

