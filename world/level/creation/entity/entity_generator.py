from typing import List, NamedTuple
from world.level.creation import IGenerator
from world.creatures import Bestiary, Creature

import logging
logger = logging.getLogger(__name__)

EntityBudget = NamedTuple("entity_budget", [
    ("monster_pool", List[Creature]),  # possible subset (less than level subset) of monsters to draw from
    ("entity_points", int),
    ("has_exit", bool)
])


class EntityGenerator(IGenerator):
    """
    With a budget, generates a collection of entities for distribution within an area (only what, not where)
    """
    # noinspection PyMethodOverriding
    def generate(self,
                 entity_budget: EntityBudget,
                 tiles: List[List[str]]) -> List[Creature]:

        # TODO implement real generation
        i = 2
        return [
            creature(x=3, y=2) for creature in Bestiary.get_creature_pool()
        ]

    def draw(self):
        # Could output entities in a more readable fashion than as_json if we want, at some point
        raise NotImplementedError
