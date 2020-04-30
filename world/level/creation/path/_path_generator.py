import math
import random
from typing import Type, List, Tuple

from world.level.creation import IGenerator, GeneratorOutput
from world.level.creation.area import AreaGenerator, AreaBudget
from world.level.creation import LevelBudget
from world.level.creation.entity import EntityBudget

import logging
logger = logging.getLogger(__name__)

EMPTY_TILE = "-"


class PathGenerator(IGenerator):
    """ Creates a level map """
    level_budget: LevelBudget
    area_budgets: List[Type[AreaBudget]]
    entity_budgets: List[Type[EntityBudget]]

    # noinspection PyMethodOverriding
    def generate(self, level_budget: LevelBudget) -> GeneratorOutput:
        # in the very end, area generators have all been called and we can merge all tiles to a big level
        raise NotImplementedError

    def _get_area_generators(self, area_count: int) -> List[Type[AreaGenerator]]:
        return random.choices(self.level_budget.area_pool,
                              self.level_budget.area_weight,
                              k=area_count)

    def _get_empty_map(self, total_area_budget_points: int, padding_factor: float = 10) -> List[List[str]]:
        """
        While ad-hoc, we base the initial map on squaring and padding the levels tile budget points
        I do this because I want available space to iterate over in all directions as I center player spawn room
        TODO this will cause a lot of empty space - override this default function to slim down the maps
        """
        dim = math.ceil(math.sqrt(total_area_budget_points) * padding_factor)
        empty_map = []
        for n1 in range(0, dim):
            col = []
            empty_map.append(col)
            for n2 in range(0, dim):
                col.append(EMPTY_TILE)
        return empty_map

    def _get_first_room_topleft(self, area_points: int, width, height) -> Tuple[int, int]:
        offset = math.sqrt(area_points) / 2
        return width / 2 - offset, height / 2 - offset

    def _get_entity_points(self, area_points: List[int]):
        # TODO not yet sure what im balancing points against, so just simply the same as area atm
        return area_points.copy()

    def _get_area_points(self) -> List[int]:
        min_size = 36
        max_size = min(round(self.level_budget.tile_points / 2), 200)
        min_areas, max_areas = 3, 20

        rest = round(self.level_budget.tile_points * 2)
        areas = []

        def get_size():
            return random.randrange(min_size, max_size)

        while rest > 0:
            next_area = get_size()

            if next_area > rest > min_size:
                areas.append(rest)
                rest = 0
            elif rest <= min_size:
                rest = 0
            else:
                areas.append(next_area)
                rest -= next_area

        while len(areas) < min_areas:
            areas.append(get_size())

        if len(areas) > max_areas:
            areas = areas[0:max_areas]

        areas.reverse()  # there's a slightly larger chance for a small room at the end, which is nicer for player start
        print("AREAS", len(areas), areas)
        return areas
