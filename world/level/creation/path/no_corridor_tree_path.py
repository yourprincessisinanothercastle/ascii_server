from typing import Type, List, Tuple
from world.level.creation import LevelBudget, GeneratorOutput
from world.level.creation.area import SquareRoom, AreaBudget, AreaGenerator

from world.level.creation.entity import EntityBudget
from world.level.creation.path import PathGenerator

import logging
logger = logging.getLogger(__name__)


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
        return self.generate(l)

    def _get_buildable_sub_block(self, other_area_blocks) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        pass

    def _get_area_monster_pool(self):
        return self.level_budget.monster_pool

    def _build_path(self):
        area_points_list = self._get_area_points()
        entity_points_list = self._get_entity_points(area_points_list)
        level_map = self._get_empty_map(sum(area_points_list))
        area_generators: List[Type[AreaGenerator]] = self._get_area_generators(len(area_points_list))

        print("MAP DIMS", len(level_map), len(level_map[0]))
        print("AREA TYPES", area_generators)

        area_map_blocks = []
        for i, area_points in enumerate(area_points_list):
            player_spawn_area_count = (1 if i == 0 else 0)
            has_exit = (i == len(area_points_list) - 1)


            # TODO how to decide where doorways are?

            entity_budget = EntityBudget(entity_points=entity_points_list[i],
                                         monster_pool=self._get_area_monster_pool(),
                                         has_exit=has_exit)

            area_budget = AreaBudget(tile_points=area_points,
                                     doorways=0)

            area_output = area_generators[i]().generate(entity_budget=entity_budget,
                                                        area_budget=area_budget,
                                                        player_spawn_area_count=player_spawn_area_count)



