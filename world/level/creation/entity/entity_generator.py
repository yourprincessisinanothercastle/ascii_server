from typing import List, NamedTuple
from world.level.creation import IGenerator
from world.creatures import Bestiary, Creature

import logging
logger = logging.getLogger(__name__)

EntityBudget = NamedTuple("entity_budget", [
    ("monster_pool", List[Creature]),  # possible subset (less than level subset) of monsters to draw from
    ("entity_points", int)
])


class EntityGenerator(IGenerator):
    """
    With a budget, generates a collection of entities for distribution within an area (only what, not where)
    """
    # noinspection PyMethodOverriding
    def generate(self,
                 entity_budget: EntityBudget,
                 tiles: List[List[str]],
                 player_spawn_area_count: int = 1,
                 has_exit: bool = False) -> List[Creature]:

        # TODO implement real generation
        i = 2
        return [
            creature(x=++i, y=i) for creature in Bestiary.get_creature_pool()
        ]
