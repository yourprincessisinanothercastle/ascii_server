import math
import random
from typing import Type, List, Tuple
from world.creatures import Creature, Blob
from world.level.creation import IGenerator, GeneratorOutput, LevelBudget
from world.level.creation.area import SquareRoom, AreaGenerator
from world.level.creation.path import PathGenerator, PATH_GENERATORS

import logging
logger = logging.getLogger(__name__)

# base value to relate between entity and tile budgets - to avoid tweaks to out-scale one from the other
# control this value to scale game up or down, like a master volume =)
GLOBAL_VALUE_INDEX = 100


class LevelGenerator(IGenerator):
    """
    Macro scale generator. Draws the path and distributes budget across area generators
    to populate a level with content.
    """
    level_budget: LevelBudget
    path: PathGenerator

    # noinspection PyMethodOverriding
    def generate(self, level_nr: int = 1, difficulty: int = 1) -> GeneratorOutput:
        self._set_budget(level_nr, difficulty)
        self._set_path(level_nr)

        return self.path.generate(self.level_budget)

    def _set_path(self, level_nr: int):
        # TODO make choosing a generator a random choice "depending on ..."
        self.path = PATH_GENERATORS["tree_path"]()

    def _set_budget(self, level_nr: int, difficulty: int):
        """ takes the total budget and splits it up for the level sub-generators (area, path, entity) """
        tile_points = self.tile_point_formula(level_nr)
        area_pool = self.assemble_area_pool(level_nr)
        entity_points = self.entity_point_formula(level_nr, difficulty, tile_points)
        monster_pool = self.assemble_monster_pool(level_nr, difficulty)

        self.level_budget = LevelBudget(
            tile_points=tile_points,
            area_pool=area_pool,
            entity_points=entity_points,
            monster_pool=monster_pool
        )

    def assemble_monster_pool(self, level_nr: int, difficulty: int) -> List[Type[Creature]]:
        # TODO pick monsters from many, categorize them by "first level seen" somehow connected to difficulty
        return [Blob]

    def entity_point_formula(self, level_nr: int, difficulty: int, tile_points: int) -> int:
        base_points = GLOBAL_VALUE_INDEX
        level_flat = level_nr * 2
        return math.ceil((base_points + tile_points + level_flat) * (0.8 + difficulty * 0.1 * 2))

    def assemble_area_pool(self, level_nr: int) -> List[Type[AreaGenerator]]:
        # TODO devise some form of picking hierarchy for areas tied to levels?
        return [SquareRoom]

    def tile_point_formula(self, level_nr: int, random_offset: Tuple[float, float] = (0.9, 1.1)) -> int:
        """
        This basically gets us a rising flattening curve, closing in on plateau quickly.
        Eventually the scaling will mostly come from incrementing by current level, before reaching the hard cap
        """
        soft_bound = GLOBAL_VALUE_INDEX * 4  # sets the tone of increase early on, slowing down significantly after a few levels
        hard_cap = GLOBAL_VALUE_INDEX * 6
        progression = soft_bound - (soft_bound / (level_nr + 1) * 1.2) + level_nr  # flat progression
        progression *= random.uniform(*random_offset)  # should result in +/- areas generated compared to static formula
        return math.ceil(progression) if progression < hard_cap else hard_cap
