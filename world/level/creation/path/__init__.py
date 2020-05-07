from world.level.creation.path._path_generator import PathGenerator
from world.level.creation.path.two_paths import TwoPaths

# Add all path generators here, so the level generator can pick them up
PATH_GENERATORS = dict(
    no_corridor_tree_path=TwoPaths
)
