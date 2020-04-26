from world.level.creation import IGenerator, GeneratorOutput

import logging
logger = logging.getLogger(__name__)


class LevelGenerator(IGenerator):
    """
    Macro scale generator. Draws the path and distributes budget across area generators
    to populate a level with content.
    """
    # noinspection PyMethodOverriding
    def generate(self, level_nr: int, difficulty: int = 1):

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
        return GeneratorOutput(self._entities, self._tiles)

    def walk_path(self):
        pass

    def allocate_budget(self):
        """ takes the total budget and splits it up over the level area generators """
        pass