from typing import List, Tuple, NamedTuple
from world.entity import Entity
from world.level.creation import IGenerator, GeneratorOutput
from world.level.creation.entity import EntityBudget, EntityGenerator

import logging
logger = logging.getLogger(__name__)

TileBudget = NamedTuple("entity_budget", [
    ("tile_points", int)
])


class AreaGenerator(IGenerator):
    """
    An "area" is a themed generated place on a level with a specific shape and content.
    It could be a square room with only blob monsters or a large open area with diverse enemies.
    """
    _tiles: List[List[str]]
    _entities: List[Entity]
    _player_spawn_areas: List[Tuple[Tuple[int, int], Tuple[int, int]]]

    # noinspection PyMethodOverriding
    def generate(self, tile_budget: TileBudget = TileBudget(0), entity_budget: EntityBudget = EntityBudget([], 0),
                 player_spawn_area_count: int = 1, has_exit: bool = False) -> GeneratorOutput:
        """ Starts generating an area subset of a level """

        self._tiles = self._generate_tiles(tile_budget)
        self._entities = self._generate_entities(entity_budget, self._tiles, has_exit)
        self._player_spawn_areas = self._generate_player_spawn_areas(player_spawn_area_count, self._tiles)

        return GeneratorOutput(self._entities, self._tiles, self._player_spawn_areas)

    def _generate_player_spawn_areas(self, player_spawn_area_count: int, tiles: List[List[str]]) -> ((int, int), (int, int)):
        # TODO implement real generation based on tiles
        def get_valid_location():
            return (1, 1), (2, 2)

        return [get_valid_location() for i in range(player_spawn_area_count)]

    # this method mostly exists on its own for easy overriding (for handmade rooms, etc)
    def _generate_entities(self, entity_budget: EntityBudget,
                           tiles: List[List[str]],
                           has_exit: bool) -> List[Entity]:
        return EntityGenerator().generate(entity_budget, tiles, has_exit)

    # implement in subclass
    def _generate_tiles(self, tile_budget) -> List[List[str]]:
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

