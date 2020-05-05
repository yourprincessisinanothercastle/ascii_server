import math
import random
from typing import Type, List, Tuple, NamedTuple, Set

from world.level.creation import IGenerator, GeneratorOutput
from world.level.creation.area import AreaGenerator, AreaBudget
from world.level.creation import LevelBudget
from world.level.creation.entity import EntityBudget

import logging
logger = logging.getLogger(__name__)

EMPTY_TILE = "wall"

# helper structure for 2d operations in this generator, maybe put it in a "common" package if its useful elsewhere
Rect = NamedTuple("rect", [
    ("xy", Tuple[int, int]),
    ("w", int),
    ("h", int)
])


class PathGenerator(IGenerator):
    """ Creates a level map """
    level_budget: LevelBudget

    # noinspection PyMethodOverriding
    def generate(self, level_budget: LevelBudget) -> GeneratorOutput:
        # in the very end, area generators have all been called and we can merge all tiles to a big level
        raise NotImplementedError

    def _get_area_generators(self, area_count: int) -> List[Type[AreaGenerator]]:
        """ Compose a list of area_generators (un-instantiated) to be generated for this level """
        return random.choices(self.level_budget.area_pool,
                              self.level_budget.area_weight,
                              k=area_count)

    def _get_empty_map(self, total_area_budget_points: int, padding_factor: float = 5) -> List[List[str]]:
        """
        While ad-hoc, we base the initial map on squaring and padding the levels tile budget points
        TODO this will cause a lot of empty space - override this default function to slim down the maps

        The idea is that it's up to each path generator to translate area points into a real map, depending on what
        you want the path_generator to create.
        """
        dim = math.ceil(math.sqrt(total_area_budget_points) * padding_factor)
        empty_map = []
        for n1 in range(0, dim):
            col = []
            empty_map.append(col)
            for n2 in range(0, dim):
                col.append(EMPTY_TILE)
        return empty_map

    def _get_entity_points(self, area_points: List[int]):
        # TODO not yet sure what im balancing points against, so simply the same as area for now
        return area_points.copy()

    def _get_area_points(self) -> List[int]:
        """ Divide budget somewhat randomly between a somewhat random amount of areas :-) """
        min_size = 36
        max_size = min(round(self.level_budget.tile_points / 2), 200)
        min_areas, max_areas = 3, 20

        rest = round(self.level_budget.tile_points * 2)
        areas = []

        def get_size():
            # TODO might want a weighed distribution - should big rooms be as common as medium?
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

    def _get_rect_intersections(self, rect: Rect, other_area_rects: List[Rect]) -> List[Tuple[Set[int], Set[int]]]:
        """
        Check for overlap between rectangles (Rect)
        """
        intersections = []
        rx = range(rect.xy[0], rect.xy[0] + rect.w)
        ry = range(rect.xy[1], rect.xy[1] + rect.h)
        for other in other_area_rects:
            ox = range(other.xy[0], other.xy[0] + other.w)
            oy = range(other.xy[1], other.xy[1] + other.h)
            isx = set(rx).intersection(ox)
            isy = set(ry).intersection(oy)
            if bool(isx) and bool(isy):  # both axis need to have intersections to be a 2d overlap
                intersections.append((isx, isy))
        return intersections