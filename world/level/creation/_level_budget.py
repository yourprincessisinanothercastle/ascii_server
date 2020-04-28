from typing import NamedTuple, Type, List

from world.creatures import Creature
from world.level.creation.area import AreaGenerator

# needed to set this struct aside to avoid circular import issues
LevelBudget = NamedTuple("level_budget", [
    ("monster_pool", List[Type[Creature]]),  # subset of possible monsters for this level
    ("entity_points", int),
    ("area_pool", List[Type[AreaGenerator]]),  # subset of possible areas for this level
    ("tile_points", int)  # 1 point -> 1 Tile
    # TODO might expand this with more rolled properties - things like "has_secret" etc
])