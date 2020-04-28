from world.level.creation import LevelBudget, GeneratorOutput
from world.level.creation.area import SquareRoom
from world.level.creation.path._path_generator import PathGenerator

import logging
logger = logging.getLogger(__name__)


class TreePath(PathGenerator):
    def generate(self, level_budget: LevelBudget) -> GeneratorOutput:
        # TODO path path path
        return SquareRoom().generate({}, {})
