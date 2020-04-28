import math, random
from typing import Type, List, Tuple, NamedTuple
from world.creatures import Creature, Blob
from world.level.creation import IGenerator, GeneratorOutput
from world.level.creation.area import SquareRoom

import logging
logger = logging.getLogger(__name__)

LevelBudget = NamedTuple("level_budget", [
    ("monster_pool", List[Type[Creature]]),  # possible subset of monsters to draw from for a level
    ("entity_points", int),
    ("tile_points", int)
])


class LevelGenerator(IGenerator):
    """
    Macro scale generator. Draws the path and distributes budget across area generators
    to populate a level with content.
    """
    # base currency value to relate between entity and tile budgets - to avoid tweaks to out-scale one from the other
    # control this value to scale game up or down, like a master volume =)
    GLOBAL_VALUE_INDEX = 100
    level_budget: LevelBudget

    # noinspection PyMethodOverriding
    def generate(self, level_nr: int = 1, difficulty: int = 1) -> GeneratorOutput:
        self._set_budget(level_nr, difficulty)

        # TODO in the very end, area generators have all been called and we can merge all tiles to a big level
        # return GeneratorOutput(self._entities, self._tiles, self._player_spawn_areas)
        return SquareRoom().generate({}, {})

    def _walk_path(self):
        pass

    def _merge_area(self):
        pass

    def _set_budget(self, level_nr: int, difficulty: int):
        """ takes the total budget and splits it up over the level area generators """
        tile_points = self.tile_point_formula(level_nr)
        entity_points = self.entity_point_formula(level_nr, difficulty, tile_points)
        monster_pool = self.assemble_monster_pool(level_nr, difficulty)

        self.level_budget = LevelBudget(
            tile_points=tile_points,
            entity_points=entity_points,
            monster_pool=monster_pool
        )

    def assemble_monster_pool(self, level_nr: int, difficulty: int):
        # TODO pick monsters from many, categorize them by "first level seen" somehow connected to difficulty
        return [Blob]

    def entity_point_formula(self, level_nr: int, difficulty: int, tile_points: int) -> int:
        base_points = self.GLOBAL_VALUE_INDEX
        level_flat = level_nr * 2
        return math.ceil((base_points + tile_points + level_flat) * (0.8 + difficulty * 0.1 * 2))

    def tile_point_formula(self, level_nr: int, random_offset: Tuple[float, float] = (0.9, 1.1)) -> int:
        """
        This basically gets us a rising flattening curve, closing in on plateau quickly.
        Eventually the scaling will mostly come from incrementing by current level, before reaching the hard cap
        """
        soft_bound = self.GLOBAL_VALUE_INDEX * 4  # sets the tone of increase early on, slowing down significantly after a few levels
        hard_cap = self.GLOBAL_VALUE_INDEX * 6
        progression = soft_bound - (soft_bound / (level_nr + 1) * 1.2) + level_nr  # flat progression
        progression *= random.uniform(random_offset)  # should result in +/- areas generated compared to static formula
        return math.ceil(progression) if progression < hard_cap else hard_cap