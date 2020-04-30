import math
from typing import Type, List, Tuple, NamedTuple, Set
from world.level.creation import LevelBudget, GeneratorOutput
from world.level.creation.area import SquareRoom, AreaBudget, AreaGenerator

from world.level.creation.entity import EntityBudget
from world.level.creation.path import PathGenerator

import logging
logger = logging.getLogger(__name__)


Rect = NamedTuple("rect", [
    ("xy", Tuple[int, int]),
    ("w", int),
    ("h", int)
])

class NoCorridorTreePath(PathGenerator):
    """
    This generator creates square rooms packed without corridors.
    """
    def generate(self, level_budget: LevelBudget) -> GeneratorOutput:
        self.level_budget = level_budget
        return self._build_path()

    # TODO remove test function
    def fake_gen(self, tp=160):
        l = LevelBudget(monster_pool=[], entity_points=200, tile_points=tp, area_pool=[SquareRoom], area_weight=[1])
        print(self._get_rect_intersections(Rect((10, 20), 10, 10), [Rect((19, 20), 10, 10)]))
        return self.generate(l)

    def _get_rect_intersections(self, rect: Rect, other_area_rects: List[Rect]) -> List[Tuple[Set[int], Set[int]]]:
        """
        Check for overlap between rectangles (Rect)
        If either Tuple[0] or Tuple[1] are empty, that means there was no overlap
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

    def _get_area_monster_pool(self):
        return self.level_budget.monster_pool

    def _build_path(self):
        area_points_list = self._get_area_points()
        entity_points_list = self._get_entity_points(area_points_list)
        level_map = self._get_empty_map(sum(area_points_list))
        area_generators: List[Type[AreaGenerator]] = self._get_area_generators(len(area_points_list))

        print("MAP DIMS", len(level_map), len(level_map[0]))
        print("AREA TYPES", area_generators)

        start_at = self._get_first_room_topleft(area_points=area_points_list[0],
                                                width=len(level_map),
                                                height=len(level_map[0]))
        area_map_blocks = []
        for i, area_points in enumerate(area_points_list):
            rooms_left = len(area_points_list) - i
            player_spawn_area_count = (1 if i == 0 else 0)
            has_exit = (i == len(area_points_list) - 1)

            # TODO generate doors for current room

            # TODO how to decide where doorways are?

            entity_budget = EntityBudget(entity_points=entity_points_list[i],
                                         monster_pool=self._get_area_monster_pool(),
                                         has_exit=has_exit)

            area_budget = AreaBudget(tile_points=area_points,
                                     doorways=0)

            area_output = area_generators[i]().generate(entity_budget=entity_budget,
                                                        area_budget=area_budget,
                                                        player_spawn_area_count=player_spawn_area_count)



