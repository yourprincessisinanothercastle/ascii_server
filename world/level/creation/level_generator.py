from typing import List, NamedTuple
from world.creatures import Creature
from world.level.creation import IGenerator, GeneratorOutput
from world.level.creation.area import SquareRoom

import logging
logger = logging.getLogger(__name__)

LevelBudget = NamedTuple("level_budget", [
    ("monster_pool", List[Creature]),  # possible subset of monsters to draw from for a level
    ("entity_points", int),
    ("tile_points", int)
])


class LevelGenerator(IGenerator):
    """
    Macro scale generator. Draws the path and distributes budget across area generators
    to populate a level with content.
    """
    # noinspection PyMethodOverriding
    def generate(self, level_nr: int = 1, difficulty: int = 1):

        ''' TODO delete old return once refactored outside this class
        return dict(
            tiles=self.tiles,
            entities=self.entities,
            player_spawn_areas=self._player_spawn_areas,
            monster_spawn_areas=self._monster_spawn_areas,
            items=[],
        )
        '''

        # TODO in the very end, area generators have all been called and we can merge all tiles to a big level
        # return GeneratorOutput(self._entities, self._tiles, self._player_spawn_areas)
        return SquareRoom().generate({}, {})

    def walk_path(self):
        pass

    def allocate_budget(self):
        """ takes the total budget and splits it up over the level area generators """
        pass