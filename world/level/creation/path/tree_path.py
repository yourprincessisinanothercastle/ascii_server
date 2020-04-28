from world.level.creation import GeneratorOutput, LevelBudget
from world.level.creation.path._path_generator import PathGenerator

import logging
logger = logging.getLogger(__name__)


class TreePath(PathGenerator):
    def generate(self, level_budget: LevelBudget) -> GeneratorOutput:
        pass
