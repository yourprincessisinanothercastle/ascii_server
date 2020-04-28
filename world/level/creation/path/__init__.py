from world.level.creation.path._path_generator import PathGenerator
from world.level.creation.path.tree_path import TreePath
from typing import NamedTuple

# Add all path generators here, so the level generator can pick them up
PATH_GENERATORS = NamedTuple("PATH_GENERATORS",
                             tree_path=TreePath
                             )
