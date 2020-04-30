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
    difficulty: int
    level_nr: int
    level_budget: LevelBudget
    path: PathGenerator

    def __init__(self, level_nr: int = 1, difficulty: int = 1):
        super().__init__()
        self.level_nr = level_nr
        self.difficulty = difficulty

    def generate(self) -> GeneratorOutput:
        self._set_budget(self.level_nr, self.difficulty)
        self._set_path(self.level_nr)

        path_output = self.path.generate(self.level_budget)
        # setting these vars so that its easy to draw/as_json directly from LevelGenerator
        self._tiles = path_output.tiles
        self._entities = path_output.entities
        self._player_spawn_areas = path_output.player_spawn_areas

        # final generated result
        return path_output

    def _set_path(self, level_nr: int):
        # TODO make choosing a generator a random choice "depending on ..."
        self.path = PATH_GENERATORS["no_corridor_tree_path"]()

    def _set_budget(self, level_nr: int, difficulty: int):
        """ takes the total budget and splits it up for the level sub-generators (area, path, entity) """
        tile_points = self.tile_point_formula(level_nr)
        area_pool, area_weight = self.assemble_area_pool(level_nr)
        entity_points = self.entity_point_formula(level_nr, difficulty, tile_points)
        monster_pool = self.assemble_monster_pool(level_nr, difficulty)

        self.level_budget = LevelBudget(
            tile_points=tile_points,
            area_pool=area_pool,
            area_weight=area_weight,
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

    def assemble_area_pool(self, level_nr: int) -> Tuple[List[Type[AreaGenerator]], List[int]]:
        # TODO devise some form of picking hierarchy for areas tied to levels?
        return [SquareRoom], [1]

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
