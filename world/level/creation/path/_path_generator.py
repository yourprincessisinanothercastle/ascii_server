from world.level.creation import IGenerator, GeneratorOutput
from world.level.creation.area import SquareRoom
from world.level.creation import LevelBudget


class PathGenerator(IGenerator):
    """ Creates a level map """

    # noinspection PyMethodOverriding
    def generate(self, level_budget: LevelBudget) -> GeneratorOutput:
        # in the very end, area generators have all been called and we can merge all tiles to a big level
        return SquareRoom().generate({}, {})

    def _walk_path(self):
        """
        We generate a base path for the whole level, using "pathers" to arrange the layout
        """
        pass