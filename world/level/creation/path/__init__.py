from world.level.creation.path._path_generator import PathGenerator
from world.level.creation.path.tree_path import TreePath


# Add all path generators here, so the level generator can pick them up
PATH_GENERATORS = dict(
    tree_path=TreePath
)
