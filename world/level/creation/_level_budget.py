from typing import NamedTuple, Type, List

from world.creatures.bestiary import Appearance
from world.level.creation.area import AreaGenerator

# Note: I set this struct aside to avoid circular import issues
LevelBudget = NamedTuple("level_budget", [
    ("level_number", int),
    ("monster_pool", List[Appearance]),  # subset of possible monsters for this level
    ("entity_points", int),
    ("area_pool", List[Type[AreaGenerator]]),  # subset of possible areas for this level
    ("area_weight", List[int]),  # should match indices with area_pool to allocate which areas should occur more often
    ("tile_points", int)
    # 1 point should NOT mean 1 tile - its a scale to calculate progression increases from
    # Ex: a "narrow map" may produce fewer tiles, while an open-area map produces more, from the same overall points
    # TODO might expand this with more rolled properties - things like "has_secret" etc
])